#!/usr/bin/env bash
# Sourced by the other scripts: config loading, logging and helpers.

log() { echo "[$(date +%H:%M:%S)] $*" >&2; }
die() { log "ERROR: $*"; exit 1; }
need_root() { [[ $EUID -eq 0 ]] || die "run as root: sudo $0 $*"; }
need_cmd() { command -v "$1" >/dev/null 2>&1 || die "'$1' not found; sudo apt install $2"; }

# load_conf: MESH_CONF, else /etc/meshmap/mesh.conf, else mesh.conf next to the scripts
load_conf() {
  local here conf
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  for conf in "${MESH_CONF:-}" /etc/meshmap/mesh.conf "$here/mesh.conf"; do
    if [[ -n "$conf" && -r "$conf" ]]; then
      # shellcheck disable=SC1090
      source "$conf"; CONF_USED="$conf"; return
    fi
  done
  die "no mesh.conf found (looked in MESH_CONF, /etc/meshmap, $here)"
}

# resolve_node_id [arg]: argument, else NODE_ID from the conf, else trailing digits of the hostname
resolve_node_id() {
  local id="${1:-${NODE_ID:-}}"
  [[ -n "$id" ]] || id="$(hostname | grep -oE '[0-9]+$' || true)"
  [[ "$id" =~ ^[0-9]+$ ]] && (( id >= 1 && id <= 254 )) \
    || die "need a node id 1-254: pass it as an argument, set NODE_ID, or end the hostname with a number (got '$(hostname)')"
  echo "$id"
}
