#!/usr/bin/env bash
# Sourced by the other scripts: config access, logging, root check.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="${CONFIG:-$ROOT/config.yaml}"
# Under sudo the venv is not on PATH; use PYTHON=.venv/bin/python if system python lacks pyyaml.
PYTHON="${PYTHON:-python3}"

log() { echo "[$(date +%H:%M:%S)] $*" >&2; }
die() { log "ERROR: $*"; exit 1; }

# cfg <dotted.key>: print one value from config.yaml (empty for null)
cfg() { (cd "$ROOT" && "$PYTHON" -m linktest.config --config "$CONFIG" "$1") || die "cannot read '$1' from $CONFIG (is pyyaml installed? try PYTHON=.venv/bin/python)"; }

need_root() { [[ $EUID -eq 0 ]] || die "run as root: sudo $0 $*"; }
need_cmd() { command -v "$1" >/dev/null 2>&1 || die "'$1' not found; sudo apt install $2"; }
