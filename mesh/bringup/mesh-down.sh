#!/usr/bin/env bash
# Leave the mesh and give the Wi-Fi interface back to NetworkManager.
# Usage: sudo mesh-down.sh
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

need_root "$@"
load_conf

if ip link show bat0 >/dev/null 2>&1; then
  batctl meshif bat0 interface del "$IFACE" 2>/dev/null || true
  ip link del bat0 || die "cannot remove bat0"
  log "bat0 removed"
fi
if ip link show "$IFACE" >/dev/null 2>&1; then
  iw dev "$IFACE" ibss leave 2>/dev/null || true
  ip addr flush dev "$IFACE"
  ip link set "$IFACE" down
  iw dev "$IFACE" set type managed || die "cannot set $IFACE back to managed mode"
  ip link set "$IFACE" mtu 1500 up
  iw dev "$IFACE" info | grep -q 'type managed' || die "$IFACE is not in managed mode"
  log "$IFACE is in managed mode"
fi
if command -v nmcli >/dev/null; then
  nmcli dev set "$IFACE" managed yes >/dev/null 2>&1 || log "WARNING: could not hand $IFACE back to NetworkManager"
fi
log "mesh down"
