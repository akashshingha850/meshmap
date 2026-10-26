#!/usr/bin/env bash
# Run the iperf3 server on Pi 2, bound to its bat0 address. Stop with Ctrl-C.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

need_cmd iperf3 iperf3
IP="$(cfg ips.pi2)"; PORT="$(cfg iperf.port)"
ip -4 addr show | grep -q "inet $IP/" || die "$IP is not configured here; is the mesh up? ('sudo mesh/bringup/mesh-up.sh')"
log "iperf3 server on $IP:$PORT"
exec iperf3 -s -B "$IP" -p "$PORT"
