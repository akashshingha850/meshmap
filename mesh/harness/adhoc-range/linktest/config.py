"""Load and validate config.yaml; also a tiny CLI so shell scripts can read it.

Shell usage: ``python3 -m linktest.config ips.pi1`` prints the value (empty for null).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

from .common import LinkTestError

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config.yaml"

_REQUIRED = [
    "interface", "ssid", "frequency_mhz", "ips.pi1", "ips.pi2", "prefix_len",
    "test.distances_m", "test.settle_s", "test.duration_s", "test.ping_interval_s",
    "iperf.port", "iperf.udp_bitrate", "output_dir",
    "analysis.throughput_fraction", "analysis.loss_threshold_pct",
    "linkbudget.path_loss_exponent", "linkbudget.sensitivity_dbm",
]


def get(cfg: dict[str, Any], dotted: str) -> Any:
    """Return cfg['a']['b'] for 'a.b'; raise LinkTestError if absent."""
    node: Any = cfg
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            raise LinkTestError(f"config key '{dotted}' is missing")
        node = node[part]
    return node


def load_config(path: Path | str = DEFAULT_CONFIG) -> dict[str, Any]:
    """Read the YAML file, check required keys and resolve output_dir to an absolute path."""
    path = Path(path)
    try:
        with path.open() as fh:
            cfg = yaml.safe_load(fh)
    except FileNotFoundError as exc:
        raise LinkTestError(f"config file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise LinkTestError(f"cannot parse {path}: {exc}") from exc
    if not isinstance(cfg, dict):
        raise LinkTestError(f"{path} must contain a YAML mapping")
    for key in _REQUIRED:
        if get(cfg, key) is None:
            raise LinkTestError(f"config key '{key}' must not be null")
    if not get(cfg, "test.distances_m"):
        raise LinkTestError("config key 'test.distances_m' must list at least one distance")
    cfg["output_dir"] = str((path.resolve().parent / cfg["output_dir"]).resolve())
    return cfg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print one config value for shell scripts.")
    parser.add_argument("key", help="dotted key, e.g. ips.pi1")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    args = parser.parse_args(argv)
    try:
        value = get(load_config(args.config), args.key)
    except LinkTestError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1
    print("" if value is None else value)
    return 0


if __name__ == "__main__":
    sys.exit(main())
