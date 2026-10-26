"""Tests for the maths: link budget, path loss fit, usable range, step summary."""

import math

import numpy as np
import pandas as pd
import pytest

from linktest.analysis import estimate_range, fit_path_loss
from linktest.collector import Sample
from linktest.linkbudget import fspl_db, max_range_m, path_loss_db, rx_power_dbm
from linktest.runner import summarize


def test_fspl_at_1m_2412mhz():
    assert fspl_db(1, 2412) == pytest.approx(40.1, abs=0.1)


def test_range_inverts_path_loss():
    kwargs = dict(freq_mhz=2412, tx_power_dbm=15, tx_gain_dbi=2, rx_gain_dbi=2)
    d = max_range_m(-82, n=3.0, **kwargs)
    assert rx_power_dbm(d, n=3.0, **kwargs) == pytest.approx(-82, abs=1e-6)
    assert path_loss_db(d, 2412, 3.0) == pytest.approx(15 + 2 + 2 + 82)


def test_fit_recovers_exponent():
    d = np.array([1, 5, 10, 20, 50, 100], dtype=float)
    rssi = -40 - 10 * 2.7 * np.log10(d)
    fit = fit_path_loss(d, rssi)
    assert fit.n == pytest.approx(2.7) and fit.a_dbm == pytest.approx(-40) and fit.r2 == pytest.approx(1)


def test_fit_needs_three_distances():
    assert fit_path_loss([1, 10], [-40, -60]) is None
    assert fit_path_loss([1, 10, 10], [-40, -60, -61]) is None


def _df(rows):
    return pd.DataFrame(rows, columns=["distance_m", "tcp_mbps", "udp_loss_pct", "ping_loss_pct"])


def test_range_stops_at_throughput_drop():
    df = _df([(1, 20, 0, 0), (10, 18, 1, 0), (20, 6, 2, 0), (30, 1, 50, 50)])
    est = estimate_range(df, 0.5, 10)
    assert est.range_m == 10 and est.first_fail_m == 20


def test_range_stops_at_loss():
    df = _df([(1, 20, 0, 0), (10, 19, 15, 0), (20, 18, 0, 0)])
    est = estimate_range(df, 0.5, 10)
    assert est.range_m == 1 and est.first_fail_m == 10


def test_range_no_failure():
    est = estimate_range(_df([(1, 20, 0, 0), (10, 19, 1, 1)]), 0.5, 10)
    assert est.range_m == 10 and est.first_fail_m is None


def test_summarize_handles_missing_noise_and_failed_tests():
    samples = [
        Sample(ts=0, signal_dbm=-60, tx_mcs=5, tx_packets=100, tx_retries=0),
        Sample(ts=1, signal_dbm=-64, tx_mcs=3, tx_packets=200, tx_retries=10),
        Sample(ts=2),  # peer not seen
    ]
    row = summarize(30, samples, None, None, None, ["tcp failed: x"])
    assert row["rssi_dbm"] == -62 and row["n_samples"] == 3
    assert row["link_up_pct"] == pytest.approx(200 / 3)
    assert math.isnan(row["snr_db"]) and math.isnan(row["noise_dbm"])
    assert row["tx_retries"] == 10 and row["tx_retry_pct"] == pytest.approx(10.0)
    assert row["tcp_mbps"] == 0.0 and math.isnan(row["udp_loss_pct"])
    assert row["notes"] == "tcp failed: x"
