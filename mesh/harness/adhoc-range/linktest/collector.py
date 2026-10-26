"""Poll `iw station dump` and `iw survey dump` once per second.

Parsing (pure functions) is separate from polling (Collector) so the parsers can
be unit tested against saved `iw` output.
"""

from __future__ import annotations

import logging
import re
import threading
import time
from dataclasses import asdict, dataclass, fields
from typing import Optional

from .common import run

log = logging.getLogger(__name__)

_STATION_HEADER = re.compile(r"^Station\s+([0-9a-fA-F:]{17})")
_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")
_MCS = re.compile(r"MCS\s+(\d+)")
_RATE = re.compile(r"([\d.]+)\s*MBit/s")
_EXPECTED_TP = re.compile(r"([\d.]+)\s*Mbps", re.IGNORECASE)


@dataclass
class StationInfo:
    """One peer from `iw station dump`; None means the driver did not report it."""

    mac: str
    inactive_ms: Optional[float] = None
    signal_dbm: Optional[float] = None
    signal_avg_dbm: Optional[float] = None
    tx_bitrate_mbps: Optional[float] = None
    rx_bitrate_mbps: Optional[float] = None
    tx_mcs: Optional[int] = None
    rx_mcs: Optional[int] = None
    tx_packets: Optional[int] = None
    tx_retries: Optional[int] = None
    tx_failed: Optional[int] = None
    expected_tp_mbps: Optional[float] = None


@dataclass
class SurveyEntry:
    """One channel from `iw survey dump`."""

    frequency_mhz: int
    in_use: bool = False
    noise_dbm: Optional[float] = None


@dataclass
class Sample:
    """One per-second row of the raw CSV. All link fields are empty if no peer was seen."""

    ts: float
    phase: str = ""
    signal_dbm: Optional[float] = None
    signal_avg_dbm: Optional[float] = None
    noise_dbm: Optional[float] = None
    snr_db: Optional[float] = None
    tx_bitrate_mbps: Optional[float] = None
    rx_bitrate_mbps: Optional[float] = None
    tx_mcs: Optional[int] = None
    rx_mcs: Optional[int] = None
    tx_packets: Optional[int] = None
    tx_retries: Optional[int] = None
    tx_failed: Optional[int] = None
    expected_tp_mbps: Optional[float] = None


SAMPLE_FIELDS = [f.name for f in fields(Sample)]


def _first_number(value: str) -> Optional[float]:
    match = _NUMBER.search(value)
    return float(match.group()) if match else None


def _parse_bitrate(value: str) -> tuple[Optional[float], Optional[int]]:
    rate = _RATE.search(value)
    mcs = _MCS.search(value)
    return (float(rate.group(1)) if rate else None, int(mcs.group(1)) if mcs else None)


def parse_station_dump(text: str) -> list[StationInfo]:
    """Parse `iw dev <if> station dump` into one StationInfo per peer."""
    stations: list[StationInfo] = []
    current: Optional[StationInfo] = None
    for line in text.splitlines():
        header = _STATION_HEADER.match(line)
        if header:
            current = StationInfo(mac=header.group(1).lower())
            stations.append(current)
            continue
        if current is None:
            continue
        key, sep, value = line.strip().partition(":")
        if not sep:
            continue
        key, value = key.strip(), value.strip()
        if key == "inactive time":
            current.inactive_ms = _first_number(value)
        elif key == "signal":
            current.signal_dbm = _first_number(value)
        elif key == "signal avg":
            current.signal_avg_dbm = _first_number(value)
        elif key == "tx bitrate":
            current.tx_bitrate_mbps, current.tx_mcs = _parse_bitrate(value)
        elif key == "rx bitrate":
            current.rx_bitrate_mbps, current.rx_mcs = _parse_bitrate(value)
        elif key in ("tx packets", "tx retries", "tx failed"):
            number = _first_number(value)
            attr = key.replace(" ", "_")
            setattr(current, attr, int(number) if number is not None else None)
        elif key == "expected throughput":
            match = _EXPECTED_TP.search(value)
            current.expected_tp_mbps = float(match.group(1)) if match else None
    return stations


def parse_survey_dump(text: str) -> list[SurveyEntry]:
    """Parse `iw dev <if> survey dump`. The noise field is optional per channel."""
    entries: list[SurveyEntry] = []
    current: Optional[SurveyEntry] = None
    for line in text.splitlines():
        key, sep, value = line.strip().partition(":")
        if not sep:
            continue
        key, value = key.strip(), value.strip()
        if key == "frequency":
            freq = _first_number(value)
            if freq is None:
                continue
            current = SurveyEntry(frequency_mhz=int(freq), in_use="[in use]" in value)
            entries.append(current)
        elif key == "noise" and current is not None:
            current.noise_dbm = _first_number(value)
    return entries


def noise_in_use(entries: list[SurveyEntry]) -> Optional[float]:
    """Noise floor of the channel in use, or None if the driver does not report one."""
    for entry in entries:
        if entry.in_use:
            return entry.noise_dbm
    return None


def pick_station(stations: list[StationInfo]) -> Optional[StationInfo]:
    """Choose the peer heard most recently (two-node test; stale IBSS peers are ignored)."""
    if not stations:
        return None
    return min(stations, key=lambda s: s.inactive_ms if s.inactive_ms is not None else float("inf"))


def build_sample(
    ts: float, phase: str, station: Optional[StationInfo], noise_dbm: Optional[float]
) -> Sample:
    """Combine one station and the noise floor; SNR stays empty if either is missing."""
    sample = Sample(ts=ts, phase=phase)
    if station is None:
        return sample
    for name in SAMPLE_FIELDS:
        if name not in ("ts", "phase", "noise_dbm", "snr_db"):
            setattr(sample, name, getattr(station, name))
    sample.noise_dbm = noise_dbm
    if station.signal_dbm is not None and noise_dbm is not None:
        sample.snr_db = station.signal_dbm - noise_dbm
    return sample


class Collector:
    """Background thread that polls `iw` every `interval_s` and keeps the samples."""

    def __init__(self, interface: str, interval_s: float = 1.0) -> None:
        self.interface = interface
        self.interval_s = interval_s
        self.phase = ""
        self.samples: list[Sample] = []
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._warned_survey = False

    def poll_once(self) -> Sample:
        """Run both `iw` commands once and return the resulting sample."""
        ts = time.time()
        rc, out, err = run(["iw", "dev", self.interface, "station", "dump"], timeout=5)
        stations = parse_station_dump(out) if rc == 0 else []
        if rc != 0:
            log.warning("station dump failed: %s", err.strip() or f"exit {rc}")
        rc, out, err = run(["iw", "dev", self.interface, "survey", "dump"], timeout=5)
        noise = noise_in_use(parse_survey_dump(out)) if rc == 0 else None
        if noise is None and not self._warned_survey:
            self._warned_survey = True
            log.warning("no noise floor from survey dump (driver may not report it); SNR will be empty")
        return build_sample(ts, self.phase, pick_station(stations), noise)

    def _loop(self) -> None:
        next_tick = time.monotonic()
        while not self._stop.is_set():
            self.samples.append(self.poll_once())
            next_tick += self.interval_s
            self._stop.wait(max(0.0, next_tick - time.monotonic()))

    def start(self) -> None:
        """Start polling in the background."""
        self.samples = []
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="collector", daemon=True)
        self._thread.start()

    def stop(self) -> list[Sample]:
        """Stop polling and return all samples."""
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=10)
        return self.samples


def sample_to_row(sample: Sample) -> dict[str, object]:
    """Dict for csv.DictWriter, with None as an empty cell."""
    return {k: ("" if v is None else v) for k, v in asdict(sample).items()}
