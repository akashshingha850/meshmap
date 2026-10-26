#!/usr/bin/env bash
# Run the iperf3 server on Pi 2, bound to its ad-hoc address. Stop with Ctrl-C.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

need_cmd iperf3 iperf3
IP="$(cfg ips.pi2)"; PORT="$(cfg iperf.port)"
ip -4 addr show | grep -q "inet $IP/" || die "$IP is not configured here; run 'sudo scripts/setup_adhoc.sh 2' first"
log "iperf3 server on $IP:$PORT"
exec iperf3 -s -B "$IP" -p "$PORT"
