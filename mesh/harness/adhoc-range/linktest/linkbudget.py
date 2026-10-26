"""Theoretical link budget: predicted range per MCS and comparison with a measured run."""

from __future__ import annotations

import argparse
import logging
import math
import sys
from pathlib import Path
from typing import Any, Optional

from . import config as cfgmod
from .common import LinkTestError, setup_logging

log = logging.getLogger(__name__)


def fspl_db(distance_m: float, freq_mhz: float) -> float:
    """Free-space path loss: 20log10(d_km) + 20log10(f_MHz) + 32.44."""
    return 20 * math.log10(distance_m / 1000.0) + 20 * math.log10(freq_mhz) + 32.44


def path_loss_db(distance_m: float, freq_mhz: float, n: float, d0_m: float = 1.0) -> float:
    """Log-distance model anchored at free-space loss at d0: PL(d0) + 10 n log10(d/d0)."""
    return fspl_db(d0_m, freq_mhz) + 10 * n * math.log10(distance_m / d0_m)


def eirp_dbm(tx_power_dbm: float, tx_gain_dbi: float, cable_loss_db: float) -> float:
    """Radiated power."""
    return tx_power_dbm + tx_gain_dbi - cable_loss_db


def rx_power_dbm(
    distance_m: float, freq_mhz: float, n: float, tx_power_dbm: float,
    tx_gain_dbi: float, rx_gain_dbi: float, cable_loss_db: float = 0.0,
) -> float:
    """Predicted received power at `distance_m`."""
    return eirp_dbm(tx_power_dbm, tx_gain_dbi, cable_loss_db) + rx_gain_dbi - path_loss_db(distance_m, freq_mhz, n)


def max_range_m(
    sensitivity_dbm: float, freq_mhz: float, n: float, tx_power_dbm: float,
    tx_gain_dbi: float, rx_gain_dbi: float, cable_loss_db: float = 0.0,
    fade_margin_db: float = 0.0, d0_m: float = 1.0,
) -> float:
    """Distance where predicted RSSI equals sensitivity + fade margin."""
    allowed_loss = (
        eirp_dbm(tx_power_dbm, tx_gain_dbi, cable_loss_db) + rx_gain_dbi - sensitivity_dbm - fade_margin_db
    )
    return d0_m * 10 ** ((allowed_loss - fspl_db(d0_m, freq_mhz)) / (10 * n))


def budget_params(cfg: dict[str, Any], tx_power_dbm: Optional[float] = None) -> dict[str, float]:
    """Radio parameters shared by predictions and plots, taken from the config."""
    tx = tx_power_dbm if tx_power_dbm is not None else cfg.get("tx_power_dbm")
    if tx is None:
        raise LinkTestError("tx_power_dbm is null in the config; set it (or pass --tx-power) for a link budget")
    lb = cfg["linkbudget"]
    return {
        "freq_mhz": float(cfg["frequency_mhz"]),
        "tx_power_dbm": float(tx),
        "tx_gain_dbi": float(lb.get("tx_antenna_gain_dbi", 0.0)),
        "rx_gain_dbi": float(lb.get("rx_antenna_gain_dbi", 0.0)),
        "cable_loss_db": float(lb.get("cable_loss_db", 0.0)),
    }


def predict_ranges(cfg: dict[str, Any], n: float, tx_power_dbm: Optional[float] = None) -> dict[str, float]:
    """Predicted range in metres for every MCS in the sensitivity table."""
    params = budget_params(cfg, tx_power_dbm)
    margin = float(cfg["linkbudget"].get("fade_margin_db", 0.0))
    return {
        mcs: max_range_m(sens, n=n, fade_margin_db=margin, **params)
        for mcs, sens in cfg["linkbudget"]["sensitivity_dbm"].items()
    }


def compare_with_run(cfg: dict[str, Any], run_dir: Path) -> None:
    """Log model-vs-measurement: RSSI error at the configured n and free space, and the range."""
    from .analysis import estimate_range, fit_path_loss, load_summary  # local: avoids a plotting import for plain predictions

    df = load_summary(run_dir)
    params = budget_params(cfg)
    n_cfg = float(cfg["linkbudget"]["path_loss_exponent"])
    data = df.dropna(subset=["rssi_dbm"])
    if data.empty:
        log.warning("no RSSI in the run; nothing to compare")
        return
    for label, n in (("free space (n=2)", 2.0), (f"configured (n={n_cfg:g})", n_cfg)):
        pred = [rx_power_dbm(d, n=n, **params) for d in data["distance_m"]]
        err = data["rssi_dbm"].to_numpy() - pred
        log.info("model %-22s mean error (measured - predicted) %+.1f dB, RMS %.1f dB",
                 label, err.mean(), math.sqrt((err ** 2).mean()))
    fit = fit_path_loss(data["distance_m"], data["rssi_dbm"])
    if fit is not None:
        log.info("measured n = %.2f (R^2 %.2f); predicted ranges with measured n:", fit.n, fit.r2)
        for mcs, rng in predict_ranges(cfg, fit.n).items():
            log.info("  %-5s %7.0f m", mcs, rng)
    usable = estimate_range(df, cfg["analysis"]["throughput_fraction"], cfg["analysis"]["loss_threshold_pct"])
    log.info("measured usable range: %s", usable.describe())


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Theoretical link budget and comparison with measurements.")
    parser.add_argument("--config", default=str(cfgmod.DEFAULT_CONFIG))
    parser.add_argument("--n", type=float, help="path loss exponent (default: from config)")
    parser.add_argument("--tx-power", type=float, help="TX power in dBm (default: from config)")
    parser.add_argument("--run", type=Path, help="run directory to compare against")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    setup_logging(args.verbose)
    try:
        cfg = cfgmod.load_config(args.config)
        n = args.n if args.n is not None else float(cfg["linkbudget"]["path_loss_exponent"])
        params = budget_params(cfg, args.tx_power)
        eirp = eirp_dbm(params["tx_power_dbm"], params["tx_gain_dbi"], params["cable_loss_db"])
        limit = cfg["linkbudget"].get("regulatory_eirp_limit_dbm")
        log.info("%.0f MHz, TX %.1f dBm, EIRP %.1f dBm, n=%.2f, FSPL at 1 m %.1f dB",
                 params["freq_mhz"], params["tx_power_dbm"], eirp, n, fspl_db(1, params["freq_mhz"]))
        if limit is not None and eirp > limit:
            log.warning("EIRP %.1f dBm exceeds the configured regulatory limit of %s dBm", eirp, limit)
        log.info("predicted range (fade margin %.0f dB):", cfg["linkbudget"].get("fade_margin_db", 0))
        for mcs, rng in predict_ranges(cfg, n, args.tx_power).items():
            log.info("  %-5s sensitivity %5.0f dBm  ->  %7.0f m", mcs, cfg["linkbudget"]["sensitivity_dbm"][mcs], rng)
        if args.run:
            compare_with_run(cfg, args.run)
    except LinkTestError as exc:
        log.error("%s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
