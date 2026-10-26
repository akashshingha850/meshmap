#!/usr/bin/env bash
# Read-only readiness check: can this unit run the batman-adv mesh? Works without root.
# Usage: scripts/check-node.sh        (exit 1 if any check FAILs)
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"
load_conf

PASS=0; WARN=0; FAIL=0
ok()   { echo "  PASS  $*"; PASS=$((PASS+1)); }
warn() { echo "  WARN  $*"; WARN=$((WARN+1)); }
bad()  { echo "  FAIL  $*"; FAIL=$((FAIL+1)); }

echo "Node $(hostname), config $CONF_USED"

echo "System"
echo "  info  $(. /etc/os-release; echo "$PRETTY_NAME"), kernel $(uname -r), $(cat /proc/device-tree/model 2>/dev/null | tr -d '\0')"

echo "Software"
if modinfo batman-adv >/dev/null 2>&1; then
  ok "batman-adv kernel module available (version $(modinfo -F version batman-adv))"
else
  bad "batman-adv kernel module not available for kernel $(uname -r)"
fi
if command -v batctl >/dev/null; then ok "batctl installed ($(batctl -v 2>&1 | head -1))"; else bad "batctl missing: sudo apt install batctl"; fi
if command -v iw >/dev/null; then ok "iw installed ($(iw --version))"; else bad "iw missing: sudo apt install iw"; fi
if grep -rqs '^batman-adv' /etc/modules-load.d/; then ok "batman-adv loads at boot"; else warn "batman-adv not in /etc/modules-load.d (mesh-up loads it anyway; install.sh adds it)"; fi

echo "Radio ($IFACE)"
if [[ ! -d "/sys/class/net/$IFACE" ]]; then
  bad "interface $IFACE not found (see 'iw dev')"
else
  driver="$(basename "$(readlink -f "/sys/class/net/$IFACE/device/driver" 2>/dev/null)")"
  phy="phy$(iw dev "$IFACE" info 2>/dev/null | awk '/wiphy/ {print $2}')"
  ok "interface present, driver $driver, $phy"
  if iw phy "$phy" info 2>/dev/null | grep -q '\* IBSS'; then ok "supports IBSS (needed)"; else bad "no IBSS support"; fi
  if iw phy "$phy" info 2>/dev/null | grep -q '\* mesh point'; then ok "supports 802.11s mesh point (optional)"; else warn "no mesh point mode (only the IBSS underlay is possible)"; fi
  case "$driver" in
    brcmfmac*) warn "brcmfmac (Pi onboard): IBSS works but no HT/MCS, reported txpower and regdom are not reliable; use a USB adapter (mt76, ath9k_htc) for range" ;;
    mt76*|mt7*|ath9k*|ath10k*) ok "driver $driver is a good fit for IBSS/mesh" ;;
    *) warn "driver $driver is untested here; verify IBSS join and rates" ;;
  esac
  rule="$(iw reg get | awk -v f="$FREQ_MHZ" '/^[ \t]*\(/ && match($0,/\([0-9]+ - [0-9]+/) { split(substr($0,RSTART+1,RLENGTH-1),a," - "); if (f+0>=a[1]+0 && f+0<=a[2]+0) { print; exit } }')"
  country="$(iw reg get | awk '/^country/ {sub(/:$/,"",$2); print $2; exit}')"
  if [[ -z "$rule" ]]; then
    bad "$FREQ_MHZ MHz is not allowed by the regulatory domain (${country:-unset}); pick another frequency or fix 'iw reg set'"
  else
    ok "$FREQ_MHZ MHz allowed in ${country:-?}: ${rule//$'\t'/ }"
    [[ "$rule" == *NO-OUTDOOR* ]] && warn "$FREQ_MHZ MHz is indoor-only: fine on the bench, not for flights"
    [[ "$rule" == *DFS* ]] && warn "$FREQ_MHZ MHz needs DFS; IBSS cannot run on DFS channels"
  fi
  [[ "$country" == "00" || -z "$country" ]] && warn "regulatory domain is unset: sudo iw reg set <CC> (and raspi-config)"
  if [[ "$(iw dev "$IFACE" info | awk '/type/ {print $2}')" != "managed" ]]; then
    echo "  info  $IFACE is currently in $(iw dev "$IFACE" info | awk '/type/ {print $2}') mode"
  fi
fi

echo "Access and conflicts"
mgmt="$(ip route show default | awk -v i="$IFACE" '$5!=i {print $5; exit}')"
if [[ -n "$mgmt" ]]; then ok "default route is on $mgmt, so taking $IFACE will not cut your session"; else warn "no default route outside $IFACE: you need Ethernet/USB to log in once $IFACE joins the mesh"; fi
if [[ -n "$(ip route show default dev "$IFACE" 2>/dev/null)" ]]; then bad "$IFACE carries the default route; mesh-up would refuse (FORCE=1 overrides)"; fi
if command -v nmcli >/dev/null; then
  st="$(nmcli -t -f DEVICE,STATE dev | awk -F: -v i="$IFACE" '$1==i {print $2}')"
  case "$st" in
    unmanaged|"") ok "NetworkManager does not manage $IFACE" ;;
    *) warn "NetworkManager manages $IFACE ($st); mesh-up sets it to unmanaged (mesh-down restores it)" ;;
  esac
fi
if [[ $EUID -ne 0 ]] && ! sudo -n true 2>/dev/null; then warn "sudo needs a password (fine, but unattended installs need root)"; fi

echo "Current mesh state"
if ip link show bat0 >/dev/null 2>&1; then
  echo "  info  bat0 is up: $(ip -br addr show bat0 | awk '{print $1,$2,$3}'), mtu $(cat /sys/class/net/bat0/mtu), slaves: $(ls /sys/class/net/bat0 | sed -n 's/^lower_//p' | tr '\n' ' ')"
else
  echo "  info  bat0 does not exist"
fi
echo "  info  mesh.service: $(systemctl is-enabled mesh.service 2>/dev/null || echo not installed) / $(systemctl is-active mesh.service 2>/dev/null || true)"

echo
echo "Result: $PASS pass, $WARN warn, $FAIL fail"
[[ $FAIL -eq 0 ]]
