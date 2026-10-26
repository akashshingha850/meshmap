#!/usr/bin/env bash
# Put the Wi-Fi interface into IBSS mode, join the test network and set the IP.
# Usage: sudo scripts/setup_adhoc.sh <1|2>      (FORCE=1 to skip the lock-out check)
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

NODE="${1:-}"
[[ "$NODE" == "1" || "$NODE" == "2" ]] || die "usage: sudo $0 <1|2>"
need_root "$@"
need_cmd iw iw
need_cmd ip iproute2

IF="$(cfg interface)"; SSID="$(cfg ssid)"; BSSID="$(cfg bssid)"; FREQ="$(cfg frequency_mhz)"
HT="$(cfg ht_mode)"; IP="$(cfg "ips.pi$NODE")"; PREFIX="$(cfg prefix_len)"; TXP="$(cfg tx_power_dbm)"
STATE=/run/linktest-stopped-services
SERVICES=(NetworkManager wpa_supplicant dhcpcd)

# 1. interface exists and supports IBSS
ip link show "$IF" >/dev/null 2>&1 || die "interface $IF not found (see 'iw dev')"
PHY="phy$(iw dev "$IF" info | awk '/wiphy/ {print $2}')"
iw phy "$PHY" info | grep -q '\* IBSS' || die "$IF ($PHY) does not list IBSS support in 'iw phy $PHY info'"
log "interface $IF on $PHY supports IBSS"

# 2. do not cut off our own session
if [[ "${FORCE:-0}" != "1" ]]; then
  [[ -z "$(ip route show default dev "$IF")" ]] || die "$IF carries the default route; you would lose network access. Use another interface for SSH, or FORCE=1"
  if [[ -n "${SSH_CONNECTION:-}" ]]; then
    ssh_local_ip="$(awk '{print $3}' <<<"$SSH_CONNECTION")"
    ip -4 addr show dev "$IF" | grep -q "inet $ssh_local_ip/" && die "this SSH session runs over $IF; connect over eth0/USB instead, or FORCE=1"
  fi
fi

# 3. stop network managers (this affects ALL interfaces, not only $IF)
: > "$STATE"
for svc in "${SERVICES[@]}"; do
  if systemctl is-active --quiet "$svc" 2>/dev/null; then
    log "stopping $svc"
    systemctl stop "$svc" || die "could not stop $svc"
    echo "$svc" >> "$STATE"
    systemctl is-active --quiet "$svc" && die "$svc is still running"
  fi
done
pkill -x wpa_supplicant 2>/dev/null || true   # leftover per-interface instances
command -v rfkill >/dev/null && rfkill unblock wlan || true

# 4. switch to IBSS (the interface must be down to change type)
ip link set "$IF" down || die "cannot bring $IF down"
ip addr flush dev "$IF"
iw dev "$IF" set type ibss || die "cannot set $IF to IBSS"
ip link set "$IF" up || die "cannot bring $IF up (rfkill? 'rfkill list')"
iw dev "$IF" info | grep -q 'type IBSS' || die "$IF is not in IBSS mode after 'set type ibss'"
log "$IF is in IBSS mode"

# 5. TX power (optional); read-back is advisory because some drivers round or ignore it
if [[ -n "$TXP" ]]; then
  iw dev "$IF" set txpower fixed "$((TXP * 100))" || log "WARNING: driver rejected txpower $TXP dBm"
  log "txpower now: $(iw dev "$IF" info | awk '/txpower/ {print $2, $3}') (requested $TXP dBm; the regulatory limit still applies)"
fi

# 6. join
JOIN=(iw dev "$IF" ibss join "$SSID" "$FREQ")
[[ -n "$HT" ]] && JOIN+=("$HT")
JOIN+=(fixed-freq)
[[ -n "$BSSID" ]] && JOIN+=("$BSSID")
log "${JOIN[*]}"
"${JOIN[@]}" || die "ibss join failed. If the HT mode is the problem, set ht_mode: NOHT in config.yaml"
joined=0
for _ in $(seq 1 10); do
  if iw dev "$IF" link | grep -qE "Joined IBSS|SSID: $SSID"; then joined=1; break; fi
  sleep 1
done
[[ $joined -eq 1 ]] || die "did not join IBSS '$SSID' within 10 s ('iw dev $IF link': $(iw dev "$IF" link | head -1))"
log "joined '$SSID' at $FREQ MHz"

# 7. address
ip addr add "$IP/$PREFIX" dev "$IF" || die "cannot assign $IP/$PREFIX"
ip -4 addr show dev "$IF" | grep -q "inet $IP/" || die "$IP is not on $IF"
log "ready: $IF = $IP/$PREFIX (node $NODE). Next: scripts/start_server.sh on Pi 2, or 'make run' on Pi 1"
