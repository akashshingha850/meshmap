"""Run iperf3 (TCP, UDP) and ping against the peer and parse the results.

The parse_* functions are pure so they can be tested against saved output.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Optional

from .common import LinkTestError, run

log = logging.getLogger(__name__)


class TrafficError(LinkTestError):
    """A traffic test failed; at long range this is data, not a crash."""


@dataclass
class TcpResult:
    throughput_mbps: float
    retransmits: Optional[int]


@dataclass
class UdpResult:
    throughput_mbps: float
    jitter_ms: float
    lost_packets: int
    packets: int
    loss_pct: float


@dataclass
class PingResult:
    sent: int
    received: int
    loss_pct: float
    rtt_min_ms: Optional[float]
    rtt_avg_ms: Optional[float]
    rtt_max_ms: Optional[float]


def _iperf_end(text: str) -> dict:
    """Return the 'end' object of an iperf3 --json result, or raise TrafficError."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise TrafficError(f"iperf3 output is not JSON: {text[:200]!r}") from exc
    if "error" in data:
        raise TrafficError(f"iperf3: {data['error']}")
    if "end" not in data:
        raise TrafficError("iperf3 JSON has no 'end' section")
    return data["end"]


def parse_iperf3_tcp(text: str) -> TcpResult:
    """Parse iperf3 TCP JSON; goodput is what the receiver got."""
    end = _iperf_end(text)
    received = end.get("sum_received") or end.get("sum_sent")
    if not received:
        raise TrafficError("iperf3 TCP JSON has no sum_received/sum_sent")
    sent = end.get("sum_sent") or {}
    return TcpResult(received["bits_per_second"] / 1e6, sent.get("retransmits"))


def parse_iperf3_udp(text: str) -> UdpResult:
    """Parse iperf3 UDP JSON (jitter and loss are measured by the server)."""
    end = _iperf_end(text)
    total = end.get("sum") or end.get("sum_received")
    if not total or "lost_percent" not in total:
        raise TrafficError("iperf3 UDP JSON has no sum with lost_percent")
    return UdpResult(
        throughput_mbps=total["bits_per_second"] / 1e6,
        jitter_ms=total["jitter_ms"],
        lost_packets=int(total["lost_packets"]),
        packets=int(total["packets"]),
        loss_pct=float(total["lost_percent"]),
    )


_PING_LOSS = re.compile(r"(\d+) packets transmitted, (\d+) (?:packets )?received.*?([\d.]+)% packet loss")
_PING_RTT = re.compile(r"= ([\d.]+)/([\d.]+)/([\d.]+)/[\d.]+ ms")


def parse_ping(text: str) -> PingResult:
    """Parse the summary of iputils ping. RTT fields are None if nothing came back."""
    loss = _PING_LOSS.search(text)
    if not loss:
        raise TrafficError(f"cannot parse ping output: {text[-200:]!r}")
    rtt = _PING_RTT.search(text)
    return PingResult(
        sent=int(loss.group(1)),
        received=int(loss.group(2)),
        loss_pct=float(loss.group(3)),
        rtt_min_ms=float(rtt.group(1)) if rtt else None,
        rtt_avg_ms=float(rtt.group(2)) if rtt else None,
        rtt_max_ms=float(rtt.group(3)) if rtt else None,
    )


def _iperf(cmd: list[str], duration_s: float) -> str:
    rc, out, err = run(cmd, timeout=duration_s + 20)
    if not out.strip():
        raise TrafficError(f"iperf3 produced no output (exit {rc}): {err.strip()}")
    return out


def run_tcp(peer: str, port: int, duration_s: float) -> TcpResult:
    """iperf3 TCP test against `peer`; needs scripts/start_server.sh on the peer."""
    cmd = ["iperf3", "-c", peer, "-p", str(port), "-t", str(int(duration_s)), "-J"]
    return parse_iperf3_tcp(_iperf(cmd, duration_s))


def run_udp(peer: str, port: int, duration_s: float, bitrate: str) -> UdpResult:
    """iperf3 UDP test at a fixed offered load."""
    cmd = ["iperf3", "-c", peer, "-p", str(port), "-t", str(int(duration_s)), "-u", "-b", bitrate, "-J"]
    return parse_iperf3_udp(_iperf(cmd, duration_s))


def run_ping(peer: str, duration_s: float, interval_s: float) -> PingResult:
    """Ping for about `duration_s` seconds."""
    count = max(1, int(duration_s / interval_s))
    cmd = ["ping", "-c", str(count), "-i", str(interval_s), "-W", "1", "-q", peer]
    rc, out, err = run(cmd, timeout=duration_s + 20)
    if not out.strip():
        raise TrafficError(f"ping produced no output (exit {rc}): {err.strip()}")
    return parse_ping(out)


def check_peer(peer: str) -> None:
    """Raise LinkTestError if the peer does not answer a ping."""
    rc, _, _ = run(["ping", "-c", "2", "-W", "2", "-q", peer], timeout=15)
    if rc != 0:
        raise LinkTestError(
            f"peer {peer} is unreachable. Check that the mesh is up on both Pis "
            f"(mesh/bringup/mesh-up.sh, 'batctl n') and the Pis are within range."
        )
