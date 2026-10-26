#!/usr/bin/env bash
# Leave the IBSS, return the interface to managed mode and restart the services setup_adhoc.sh stopped.
# Usage: sudo scripts/teardown_adhoc.sh
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

need_root "$@"
need_cmd iw iw
IF="$(cfg interface)"
STATE=/run/linktest-stopped-services

ip link show "$IF" >/dev/null 2>&1 || die "interface $IF not found"
iw dev "$IF" ibss leave 2>/dev/null || log "not in an IBSS (continuing)"
ip addr flush dev "$IF"
ip link set "$IF" down
iw dev "$IF" set type managed || die "cannot set $IF back to managed mode"
ip link set "$IF" up
iw dev "$IF" info | grep -q 'type managed' || die "$IF is not in managed mode"
log "$IF is back in managed mode"

if [[ -f "$STATE" ]]; then
  while read -r svc; do
    [[ -n "$svc" ]] || continue
    log "starting $svc"
    systemctl start "$svc" || die "could not start $svc"
    systemctl is-active --quiet "$svc" || die "$svc did not start"
  done < "$STATE"
  rm -f "$STATE"
else
  log "no record of stopped services; start yours manually (e.g. sudo systemctl start NetworkManager)"
fi
log "teardown complete"
