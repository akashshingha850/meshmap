#!/usr/bin/env bash
# Join the batman-adv mesh over IBSS and give bat0 its address.
# Usage: sudo mesh-up.sh [node-id]     (FORCE=1 skips the lock-out check)
# Safe to run again: an existing bat0 is torn down first.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

need_root "$@"
load_conf
need_cmd batctl batctl
need_cmd iw iw
need_cmd ip iproute2

ID="$(resolve_node_id "${1:-}")"
IP="$SUBNET.$ID"
MAC="$(printf '02:ba:7a:00:00:%02x' "$ID")"
log "node $ID: $IP/$PREFIX_LEN on $IFACE, '$SSID' at $FREQ_MHZ MHz (config $CONF_USED)"

# 1. preconditions
ip link show "$IFACE" >/dev/null 2>&1 || die "interface $IFACE not found (see 'iw dev')"
PHY="phy$(iw dev "$IFACE" info | awk '/wiphy/ {print $2}')"
iw phy "$PHY" info | grep -q '\* IBSS' || die "$IFACE ($PHY) does not support IBSS"
if [[ "${FORCE:-0}" != "1" ]]; then
  [[ -z "$(ip route show default dev "$IFACE")" ]] || die "$IFACE carries the default route; log in over Ethernet/USB, or FORCE=1"
  if [[ -n "${SSH_CONNECTION:-}" ]]; then
    local_ip="$(awk '{print $3}' <<<"$SSH_CONNECTION")"
    ip -4 addr show dev "$IFACE" | grep -q "inet $local_ip/" && die "this SSH session runs over $IFACE; use Ethernet/USB, or FORCE=1"
  fi
fi

# 2. clean slate, then the kernel module and routing algorithm (algorithm is fixed when bat0 is created)
if ip link show bat0 >/dev/null 2>&1; then
  log "bat0 exists; removing it first"
  batctl meshif bat0 interface del "$IFACE" 2>/dev/null || true
  ip link del bat0 || die "cannot remove bat0"
fi
modprobe batman-adv || die "cannot load batman-adv (kernel $(uname -r))"
batctl routing_algo "$ROUTING_ALGO" || die "cannot set routing algorithm $ROUTING_ALGO"

# 3. take the interface from NetworkManager (only this interface; other links stay up)
if command -v nmcli >/dev/null; then
  nmcli dev disconnect "$IFACE" >/dev/null 2>&1 || true
  nmcli dev set "$IFACE" managed no >/dev/null 2>&1 || true
  sleep 1
fi
command -v rfkill >/dev/null && rfkill unblock wlan || true

# 4. IBSS
ip link set "$IFACE" down || die "cannot bring $IFACE down"
iw dev "$IFACE" set type ibss || die "cannot set $IFACE to IBSS"
ip link set "$IFACE" mtu "$WLAN_MTU" up || die "cannot bring $IFACE up with mtu $WLAN_MTU (rfkill? 'rfkill list')"
if [[ -n "$TX_POWER_DBM" ]]; then
  iw dev "$IFACE" set txpower fixed "$((TX_POWER_DBM * 100))" || log "WARNING: driver rejected txpower $TX_POWER_DBM dBm"
fi
JOIN=(iw dev "$IFACE" ibss join "$SSID" "$FREQ_MHZ")
[[ -n "$HT_MODE" ]] && JOIN+=("$HT_MODE")
JOIN+=(fixed-freq)
[[ -n "$BSSID" ]] && JOIN+=("$BSSID")
log "${JOIN[*]}"
"${JOIN[@]}" || die "ibss join failed (regulatory domain? try HT_MODE=NOHT or another FREQ_MHZ; 'dmesg | tail')"
for _ in $(seq 1 10); do
  iw dev "$IFACE" link | grep -qE "Joined IBSS|SSID: $SSID" && break
  sleep 1
done
iw dev "$IFACE" link | grep -qE "Joined IBSS|SSID: $SSID" || die "did not join '$SSID' within 10 s"

# 5. batman-adv
batctl meshif bat0 interface add "$IFACE" || die "cannot add $IFACE to bat0"
batctl meshif bat0 interface | grep -q "$IFACE: active" || die "$IFACE is not active in bat0 ('batctl meshif bat0 interface')"
batctl meshif bat0 distributed_arp_table "$DISTRIBUTED_ARP_TABLE" || log "WARNING: could not set distributed_arp_table"
ip link set bat0 down
ip link set bat0 address "$MAC"
ip link set bat0 mtu "$BAT_MTU" up || die "cannot bring bat0 up"
ip addr flush dev bat0
ip addr add "$IP/$PREFIX_LEN" dev bat0 || die "cannot assign $IP/$PREFIX_LEN"
ip -4 addr show dev bat0 | grep -q "inet $IP/" || die "$IP is not on bat0"

log "mesh up: $IP on '$SSID' ch $FREQ_MHZ ($ROUTING_ALGO)"
sleep 3
log "neighbors: $(batctl meshif bat0 neighbors 2>&1 | tail -n +2 | grep -c . || true) (none is normal for the first node)"
