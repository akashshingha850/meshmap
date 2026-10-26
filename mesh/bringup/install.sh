#!/usr/bin/env bash
# Install the mesh scripts on this unit and enable the mesh at every boot. Does not start it now.
# Usage: sudo ./install.sh [--no-enable]
#   --no-enable   install only; do not start the mesh at boot (the mesh takes the Wi-Fi interface at every boot)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/_lib.sh"
need_root "$@"

if ! command -v batctl >/dev/null || ! command -v iw >/dev/null; then
  log "installing batctl and iw"
  apt-get install -y batctl iw || die "apt install failed (no internet? install batctl and iw by hand)"
fi
modinfo batman-adv >/dev/null 2>&1 || die "this kernel ($(uname -r)) has no batman-adv module"

echo batman-adv > /etc/modules-load.d/batman-adv.conf
install -d /etc/meshmap
if [[ -e /etc/meshmap/mesh.conf ]]; then
  log "keeping existing /etc/meshmap/mesh.conf (compare with $HERE/mesh.conf)"
else
  install -m 644 "$HERE/mesh.conf" /etc/meshmap/mesh.conf
fi
for f in _lib.sh check-node.sh mesh-up.sh mesh-down.sh; do
  dest="/usr/local/sbin/${f%.sh}"; [[ "$f" == _lib.sh ]] && dest=/usr/local/sbin/_lib.sh
  if [[ -e "$dest" ]] && ! cmp -s "$HERE/$f" "$dest"; then cp "$dest" "$dest.bak"; log "backed up old $dest to $dest.bak"; fi
  install -m 755 "$HERE/$f" "$dest"
done
install -m 644 "$HERE/mesh.service" /etc/systemd/system/mesh.service
systemctl daemon-reload
if [[ "${1:-}" == "--no-enable" ]]; then
  log "not enabled at boot; enable later with: sudo systemctl enable mesh"
else
  systemctl enable mesh.service || die "cannot enable mesh.service"
  log "mesh.service enabled: the mesh starts at every boot"
fi
log "installed. Check with: check-node   Start with: sudo mesh-up [node-id]"
