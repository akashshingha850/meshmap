"""Interactive runner: one row per distance step in summary.csv, raw samples per step."""

from __future__ import annotations

import argparse
import csv
import logging
import math
import shutil
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Sequence

import pandas as pd

from . import config as cfgmod
from . import traffic
from .collector import SAMPLE_FIELDS, Collector, Sample, sample_to_row
from .common import LinkTestError, require_tools, setup_logging

log = logging.getLogger(__name__)

NAN = float("nan")


def _mean(values: Sequence[float]) -> float:
    return statistics.fmean(values) if values else NAN


def _delta(values: Sequence[Optional[int]]) -> float:
    """Growth of a cumulative counter over the step; NaN if unknown or the counter reset."""
    seen = [v for v in values if v is not None]
    if len(seen) < 2 or seen[-1] < seen[0]:
        return NAN
    return float(seen[-1] - seen[0])


def summarize(
    distance_m: float,
    samples: Sequence[Sample],
    tcp: Optional[traffic.TcpResult],
    udp: Optional[traffic.UdpResult],
    ping: Optional[traffic.PingResult],
    notes: Sequence[str] = (),
) -> dict[str, Any]:
    """Collapse one step into a summary.csv row. A failed iperf3 test counts as 0 Mbit/s."""

    def col(name: str) -> list[float]:
        return [getattr(s, name) for s in samples if getattr(s, name) is not None]

    rssi = col("signal_dbm")
    retries = _delta([s.tx_retries for s in samples])
    packets = _delta([s.tx_packets for s in samples])
    mcs = col("tx_mcs")
    return {
        "distance_m": distance_m,
        "n_samples": len(samples),
        "link_up_pct": 100.0 * len(rssi) / len(samples) if samples else NAN,
        "rssi_dbm": _mean(rssi),
        "rssi_std_db": statistics.pstdev(rssi) if len(rssi) > 1 else NAN,
        "rssi_min_dbm": min(rssi) if rssi else NAN,
        "signal_avg_dbm": _mean(col("signal_avg_dbm")),
        "noise_dbm": _mean(col("noise_dbm")),
        "snr_db": _mean(col("snr_db")),
        "tx_bitrate_mbps": _mean(col("tx_bitrate_mbps")),
        "rx_bitrate_mbps": _mean(col("rx_bitrate_mbps")),
        "tx_mcs": statistics.median(mcs) if mcs else NAN,
        "tx_retries": retries,
        "tx_retry_pct": 100.0 * retries / packets if packets and not math.isnan(retries) else NAN,
        "tx_failed": _delta([s.tx_failed for s in samples]),
        "expected_tp_mbps": _mean(col("expected_tp_mbps")),
        "tcp_mbps": tcp.throughput_mbps if tcp else 0.0,
        "tcp_retransmits": tcp.retransmits if tcp and tcp.retransmits is not None else NAN,
        "udp_mbps": udp.throughput_mbps if udp else 0.0,
        "udp_loss_pct": udp.loss_pct if udp else NAN,
        "udp_jitter_ms": udp.jitter_ms if udp else NAN,
        "ping_loss_pct": ping.loss_pct if ping else NAN,
        "rtt_min_ms": ping.rtt_min_ms if ping and ping.rtt_min_ms is not None else NAN,
        "rtt_avg_ms": ping.rtt_avg_ms if ping and ping.rtt_avg_ms is not None else NAN,
        "rtt_max_ms": ping.rtt_max_ms if ping and ping.rtt_max_ms is not None else NAN,
        "notes": "; ".join(notes),
    }


def write_raw(path: Path, samples: Sequence[Sample]) -> None:
    """Write the per-second samples of one step."""
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=SAMPLE_FIELDS)
        writer.writeheader()
        writer.writerows(sample_to_row(s) for s in samples)


def update_summary(path: Path, row: dict[str, Any]) -> None:
    """Add the row, replacing any earlier row for the same distance."""
    new = pd.DataFrame([row])
    if path.exists():
        old = pd.read_csv(path)
        old = old[old["distance_m"] != row["distance_m"]]
        new = pd.concat([old, new], ignore_index=True)
    new.sort_values("distance_m").to_csv(path, index=False)


def settle(seconds: float) -> None:
    """Wait, logging progress every 10 s."""
    log.info("settling for %.0f s", seconds)
    end = time.monotonic() + seconds
    while (left := end - time.monotonic()) > 0:
        time.sleep(min(10.0, left))
        if left > 10:
            log.info("  %.0f s left", end - time.monotonic())


def measure_step(cfg: dict[str, Any], distance_m: float) -> tuple[dict[str, Any], list[Sample]]:
    """Run the collector alongside ping, TCP and UDP and return (summary row, raw samples)."""
    test, peer, port = cfg["test"], cfg["ips"]["pi2"], cfg["iperf"]["port"]
    collector = Collector(cfg["interface"], peer_mac=cfg.get("peer_mac"))
    notes: list[str] = []
    results: dict[str, Any] = {"ping": None, "tcp": None, "udp": None}
    collector.start()
    try:
        for phase, fn in (
            ("ping", lambda: traffic.run_ping(peer, test["duration_s"], test["ping_interval_s"])),
            ("tcp", lambda: traffic.run_tcp(peer, port, test["duration_s"])),
            ("udp", lambda: traffic.run_udp(peer, port, test["duration_s"], cfg["iperf"]["udp_bitrate"])),
        ):
            collector.phase = phase
            log.info("%s for %s s", phase, test["duration_s"])
            try:
                results[phase] = fn()
            except traffic.TrafficError as exc:
                log.warning("%s failed: %s", phase, exc)
                notes.append(f"{phase} failed: {exc}")
    finally:
        samples = collector.stop()
    row = summarize(distance_m, samples, results["tcp"], results["udp"], results["ping"], notes)
    return row, samples


def _run_dir(cfg: dict[str, Any], run_id: Optional[str], resume: bool) -> Path:
    base = Path(cfg["output_dir"])
    if resume:
        if run_id is None:
            runs = sorted(p for p in base.iterdir() if p.is_dir()) if base.exists() else []
            if not runs:
                raise LinkTestError(f"nothing to resume in {base}")
            run_id = runs[-1].name
        path = base / run_id
        if not path.is_dir():
            raise LinkTestError(f"cannot resume: {path} does not exist")
        return path
    run_id = run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
    path = base / run_id
    if path.exists():
        raise LinkTestError(f"{path} already exists; use --resume to continue it")
    return path


def format_distance(distance_m: float) -> str:
    return f"{distance_m:g}"


def run_steps(cfg: dict[str, Any], run_dir: Path, distances: list[float], check_peer: bool) -> None:
    """Prompt, settle, measure and save each distance in turn."""
    summary_path = run_dir / "summary.csv"
    for i, distance in enumerate(distances):
        input(f"\nMove Pi 2 to {format_distance(distance)} m and press Enter ")
        if i == 0 and check_peer:
            traffic.check_peer(cfg["ips"]["pi2"])
        settle(cfg["test"]["settle_s"])
        row, samples = measure_step(cfg, distance)
        write_raw(run_dir / f"raw_{format_distance(distance)}m.csv", samples)
        update_summary(summary_path, row)
        log.info("%s m: RSSI %.1f dBm, TCP %.1f Mbit/s, UDP loss %.1f%%, ping loss %.1f%%",
                 format_distance(distance), row["rssi_dbm"], row["tcp_mbps"], row["udp_loss_pct"], row["ping_loss_pct"])


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Interactive range test; run on Pi 1 with Pi 2 serving iperf3.")
    parser.add_argument("--config", default=str(cfgmod.DEFAULT_CONFIG))
    parser.add_argument("--run-id", help="name of the run directory (default: timestamp)")
    parser.add_argument("--resume", action="store_true",
                        help="continue an existing run (latest, or --run-id), skipping finished distances")
    parser.add_argument("--distance", type=float, help="measure only this distance (replaces its row)")
    parser.add_argument("--no-peer-check", action="store_true",
                        help="skip the reachability check (e.g. resuming at a distance beyond range)")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    setup_logging(args.verbose)
    try:
        cfg = cfgmod.load_config(args.config)
        require_tools(["iw", "iperf3", "ping"])
        run_dir = _run_dir(cfg, args.run_id, args.resume)
        if args.distance is not None:
            distances = [args.distance]
        else:
            distances = [float(d) for d in cfg["test"]["distances_m"]]
            if args.resume and (run_dir / "summary.csv").exists():
                done = set(pd.read_csv(run_dir / "summary.csv")["distance_m"])
                distances = [d for d in distances if d not in done]
                if not distances:
                    log.info("all distances already measured in %s", run_dir)
                    return 0
        run_dir.mkdir(parents=True, exist_ok=True)
        if not (run_dir / "config.yaml").exists():
            shutil.copy(args.config, run_dir / "config.yaml")
        log.info("run directory: %s", run_dir)
        log.info("distances: %s", ", ".join(format_distance(d) for d in distances))
        run_steps(cfg, run_dir, distances, check_peer=not args.no_peer_check)
    except LinkTestError as exc:
        log.error("%s", exc)
        return 1
    except (KeyboardInterrupt, EOFError):
        log.warning("interrupted; finished steps are saved. Continue with --resume")
        return 130
    log.info("done. Analyse with: make analyze RUN=%s", run_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
