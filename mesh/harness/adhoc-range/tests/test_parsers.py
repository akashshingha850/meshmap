"""Parser tests against saved `iw`, iperf3 and ping output.

The files in data/ are hand-written from the documented output formats, not captured
from hardware; replace them with real captures once measured.
"""

from pathlib import Path

import pytest

from linktest.collector import (
    build_sample, noise_in_use, parse_station_dump, parse_survey_dump, pick_station,
)
from linktest.traffic import (
    TrafficError, parse_iperf3_tcp, parse_iperf3_udp, parse_ping,
)

DATA = Path(__file__).parent / "data"


def read(name: str) -> str:
    return (DATA / name).read_text()


def test_station_dump_ht():
    [st] = parse_station_dump(read("station_dump_ht.txt"))
    assert st.mac == "02:ca:fe:00:00:02"
    assert st.signal_dbm == -52 and st.signal_avg_dbm == -53
    assert st.tx_bitrate_mbps == 65.0 and st.tx_mcs == 7
    assert st.rx_bitrate_mbps == 72.2 and st.rx_mcs == 7
    assert (st.tx_packets, st.tx_retries, st.tx_failed) == (10000, 250, 3)
    assert st.expected_tp_mbps == 40.5
    assert st.inactive_ms == 120


def test_station_dump_legacy_has_no_mcs_and_picks_freshest_peer():
    stations = parse_station_dump(read("station_dump_legacy_two_peers.txt"))
    assert len(stations) == 2
    best = pick_station(stations)
    assert best.mac == "02:ca:fe:00:00:02"
    assert best.signal_dbm == -67
    assert best.tx_bitrate_mbps == 54.0 and best.tx_mcs is None
    assert best.expected_tp_mbps is None


def test_station_dump_empty():
    assert parse_station_dump(read("station_dump_empty.txt")) == []
    assert pick_station([]) is None


def test_survey_dump_noise_of_channel_in_use():
    entries = parse_survey_dump(read("survey_dump.txt"))
    assert [e.frequency_mhz for e in entries] == [2412, 2417]
    assert noise_in_use(entries) == -95


def test_survey_dump_without_noise_gives_none():
    assert noise_in_use(parse_survey_dump(read("survey_dump_no_noise.txt"))) is None


def test_sample_snr_is_signal_minus_noise():
    [st] = parse_station_dump(read("station_dump_ht.txt"))
    sample = build_sample(1.0, "tcp", st, -95.0)
    assert sample.snr_db == 43.0
    assert sample.phase == "tcp" and sample.tx_mcs == 7


def test_sample_snr_empty_when_noise_missing():
    [st] = parse_station_dump(read("station_dump_ht.txt"))
    sample = build_sample(1.0, "", st, None)
    assert sample.signal_dbm == -52 and sample.noise_dbm is None and sample.snr_db is None


def test_sample_without_station_is_all_empty():
    sample = build_sample(1.0, "", None, -95.0)
    assert sample.signal_dbm is None and sample.snr_db is None


def test_iperf_tcp():
    res = parse_iperf3_tcp(read("iperf3_tcp.json"))
    assert res.throughput_mbps == pytest.approx(23.6)
    assert res.retransmits == 12


def test_iperf_udp():
    res = parse_iperf3_udp(read("iperf3_udp.json"))
    assert res.throughput_mbps == pytest.approx(9.8)
    assert res.jitter_ms == 1.2
    assert (res.lost_packets, res.packets) == (20, 8500)
    assert res.loss_pct == pytest.approx(0.235)


@pytest.mark.parametrize("parser", [parse_iperf3_tcp, parse_iperf3_udp])
def test_iperf_error_is_reported(parser):
    with pytest.raises(TrafficError, match="Connection refused"):
        parser(read("iperf3_error.json"))


def test_iperf_garbage():
    with pytest.raises(TrafficError):
        parse_iperf3_tcp("not json")


def test_ping_ok():
    res = parse_ping(read("ping_ok.txt"))
    assert (res.sent, res.received, res.loss_pct) == (150, 147, 2.0)
    assert (res.rtt_min_ms, res.rtt_avg_ms, res.rtt_max_ms) == (1.234, 3.456, 45.678)


@pytest.mark.parametrize("name", ["ping_total_loss.txt", "ping_unreachable.txt"])
def test_ping_total_loss_has_no_rtt(name):
    res = parse_ping(read(name))
    assert res.loss_pct == 100.0 and res.received == 0
    assert res.rtt_avg_ms is None


def test_ping_garbage():
    with pytest.raises(TrafficError):
        parse_ping("ping: unknown host")
