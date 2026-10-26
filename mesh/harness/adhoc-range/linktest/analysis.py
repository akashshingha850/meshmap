"""Plots, path-loss fit and usable-range estimate from a run's summary.csv."""

from __future__ import annotations

import argparse
import logging
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from . import config as cfgmod
from .common import LinkTestError, setup_logging
from .linkbudget import budget_params, rx_power_dbm

log = logging.getLogger(__name__)


@dataclass
class PathLossFit:
    """RSSI = a_dbm - 10 * n * log10(d)."""

    a_dbm: float
    n: float
    r2: float
    n_points: int

    def rssi(self, distance_m):
        return self.a_dbm - 10 * self.n * np.log10(distance_m)


@dataclass
class RangeEstimate:
    """Usable range: last distance before the first failing step."""

    range_m: Optional[float]      # None if even the nearest step fails
    first_fail_m: Optional[float]  # None if no step fails
    reason: str

    def describe(self) -> str:
        if self.first_fail_m is None:
            return f"at least {self.range_m:g} m (no step failed; test further out)"
        if self.range_m is None:
            return f"below the nearest step ({self.first_fail_m:g} m): {self.reason}"
        return f"{self.range_m:g} m (first failure at {self.first_fail_m:g} m: {self.reason})"


def load_summary(run_dir: Path) -> pd.DataFrame:
    """Read <run_dir>/summary.csv sorted by distance."""
    path = Path(run_dir) / "summary.csv"
    if not path.exists():
        raise LinkTestError(f"{path} not found; run the runner first")
    df = pd.read_csv(path).sort_values("distance_m").reset_index(drop=True)
    if df.empty:
        raise LinkTestError(f"{path} has no rows")
    return df


def fit_path_loss(distances_m, rssi_dbm) -> Optional[PathLossFit]:
    """Least-squares fit of RSSI against 10*log10(d). Needs >= 3 distinct distances."""
    d = np.asarray(distances_m, dtype=float)
    r = np.asarray(rssi_dbm, dtype=float)
    ok = np.isfinite(d) & np.isfinite(r) & (d > 0)
    d, r = d[ok], r[ok]
    if len(np.unique(d)) < 3:
        return None
    x = 10 * np.log10(d)
    slope, intercept = np.polyfit(x, r, 1)
    resid = r - (slope * x + intercept)
    ss_tot = float(((r - r.mean()) ** 2).sum())
    r2 = 1.0 - float((resid ** 2).sum()) / ss_tot if ss_tot > 0 else float("nan")
    return PathLossFit(a_dbm=float(intercept), n=float(-slope), r2=r2, n_points=int(len(d)))


def estimate_range(df: pd.DataFrame, throughput_fraction: float, loss_threshold_pct: float) -> RangeEstimate:
    """Scan distances in order; a step fails if TCP goodput < fraction*baseline or loss > threshold.

    Baseline is TCP goodput at the nearest distance. Loss is the larger of UDP and ping loss.
    """
    df = df.sort_values("distance_m")
    baseline = df["tcp_mbps"].iloc[0]
    passed: Optional[float] = None
    for _, row in df.iterrows():
        reasons = []
        tcp = row["tcp_mbps"]
        if pd.notna(baseline) and baseline > 0 and (pd.isna(tcp) or tcp < throughput_fraction * baseline):
            reasons.append(f"TCP {0 if pd.isna(tcp) else tcp:.1f} Mbit/s < {throughput_fraction:g} x baseline {baseline:.1f}")
        loss = max((v for v in (row.get("udp_loss_pct"), row.get("ping_loss_pct")) if pd.notna(v)), default=math.nan)
        if pd.notna(loss) and loss > loss_threshold_pct:
            reasons.append(f"loss {loss:.0f}% > {loss_threshold_pct:g}%")
        if reasons:
            return RangeEstimate(passed, float(row["distance_m"]), "; ".join(reasons))
        passed = float(row["distance_m"])
    return RangeEstimate(passed, None, "")


_MEASURED = "#2f6fb3"
_REFERENCE = "#8a8f98"
_FIT = "#c2571a"


def _plot_metric(df, column, ylabel, title, out_path, *, logx=True, extra=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 4), dpi=130)
    data = df.dropna(subset=[column])
    ax.plot(data["distance_m"], data[column], "o-", color=_MEASURED, lw=2, ms=6, mec="white", mew=1.5, label="measured")
    if extra:
        extra(ax)
    if logx:
        ax.set_xscale("log")
    ax.set_xlabel("distance (m)")
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontsize=11)
    ax.grid(True, color="#e3e5e8", lw=0.8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    if extra or column == "rssi_dbm":
        ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_all(df: pd.DataFrame, fit: Optional[PathLossFit], cfg: Optional[dict], out_dir: Path) -> list[Path]:
    """Write the five plots; returns their paths. Empty metrics (e.g. no noise floor) are skipped."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    dmin, dmax = df["distance_m"].min(), df["distance_m"].max()
    grid = np.geomspace(max(dmin, 0.5), dmax, 100)

    def rssi_extra(ax):
        if fit is not None:
            ax.plot(grid, fit.rssi(grid), "--", color=_FIT, lw=1.5, label=f"fit, n = {fit.n:.2f}")
        if cfg is not None:
            try:
                params = budget_params(cfg)
            except LinkTestError:
                return
            ax.plot(grid, [rx_power_dbm(d, n=2.0, **params) for d in grid], ":", color=_REFERENCE, lw=1.5,
                    label="free space (n = 2)")

    specs = [
        ("rssi_dbm", "RSSI (dBm)", "RSSI vs distance", "rssi_vs_distance.png", rssi_extra),
        ("snr_db", "SNR (dB)", "SNR vs distance", "snr_vs_distance.png", None),
        ("tcp_mbps", "TCP goodput (Mbit/s)", "Throughput vs distance", "throughput_vs_distance.png", None),
        ("udp_loss_pct", "UDP packet loss (%)", "Packet loss vs distance", "loss_vs_distance.png", None),
        ("tx_mcs", "TX MCS (median)", "MCS vs distance", "mcs_vs_distance.png", None),
    ]
    for column, ylabel, title, name, extra in specs:
        if df[column].notna().sum() == 0:
            log.warning("no data for %s; skipping %s", column, name)
            continue
        path = out_dir / name
        _plot_metric(df, column, ylabel, title, path, extra=extra)
        written.append(path)
    return written


def analyze(run_dir: Path) -> None:
    """Fit, estimate the range and write plots for one run."""
    df = load_summary(run_dir)
    snapshot = Path(run_dir) / "config.yaml"
    cfg = cfgmod.load_config(snapshot) if snapshot.exists() else cfgmod.load_config()
    if not snapshot.exists():
        log.warning("no config snapshot in the run; using the current config.yaml for the free-space overlay")
    fit = fit_path_loss(df["distance_m"], df["rssi_dbm"])
    if fit is None:
        log.warning("need RSSI at >= 3 distinct distances for the path loss fit")
    else:
        log.info("path loss fit: RSSI = %.1f - 10 x %.2f x log10(d), R^2 = %.2f (%d points)",
                 fit.a_dbm, fit.n, fit.r2, fit.n_points)
    est = estimate_range(df, cfg["analysis"]["throughput_fraction"], cfg["analysis"]["loss_threshold_pct"])
    log.info("usable range: %s", est.describe())
    for path in plot_all(df, fit, cfg, Path(run_dir) / "plots"):
        log.info("wrote %s", path)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Analyse one run: plots, path loss exponent, usable range.")
    parser.add_argument("--run", type=Path, required=True, help="run directory containing summary.csv")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    setup_logging(args.verbose)
    try:
        analyze(args.run)
    except LinkTestError as exc:
        log.error("%s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
