# BATMAN-adv node setup

[← Mesh (P1)](../README.md) · [Main doc](../../docs/README.md) · [Technical notes](../docs/technical.md#mesh-bring-up-batman-adv-over-ibss)

Scripts to turn a Raspberry Pi into a mesh node: batman-adv on top of an IBSS (ad-hoc) Wi-Fi interface. Every unit uses the same scripts and the same [mesh.conf](mesh.conf); only the node id differs.

| File | Purpose |
| --- | --- |
| [check-node.sh](check-node.sh) | Read-only readiness check (no root): kernel module, batctl, IBSS support, driver, regulatory domain, access path, current state |
| [mesh-up.sh](mesh-up.sh) | Join the mesh and set the address; safe to re-run |
| [mesh-down.sh](mesh-down.sh) | Leave the mesh, return Wi-Fi to NetworkManager |
| [install.sh](install.sh) | Install the scripts, config, module autoload and `mesh.service` on a unit; enables the mesh at boot |
| [mesh.conf](mesh.conf) | Settings shared by all nodes |
| [mesh.service](mesh.service) | systemd unit that starts the mesh at boot (enabled by `install.sh`) |

## Address scheme

Node id = the trailing number of the hostname, so `raspberrypi1` gets `10.10.0.1/24` on `bat0`, `raspberrypi2` gets `10.10.0.2`, and so on. Pass an id (`sudo mesh-up 5`) or set `NODE_ID` in the conf when the hostname has no number. `bat0` also gets the MAC `02:ba:7a:00:00:<id>`. **Give every unit a unique hostname ending in its number** (`sudo hostnamectl set-hostname raspberrypi3`).

## Set up a new unit

1. Flash Raspberry Pi OS (Bookworm or newer), set the hostname with its number, and make sure you can log in **over Ethernet or USB**: the Wi-Fi interface is taken over by the mesh.
2. Get this repo on the unit and run the check: `mesh/bringup/check-node.sh`. Fix every FAIL; read every WARN.
3. Set the regulatory domain if the check says it is unset: `sudo iw reg set FI` (use your country).
4. `sudo mesh/bringup/install.sh` (enables the mesh at every boot; add `--no-enable` to skip that).
5. `sudo mesh-up` (or `sudo systemctl start mesh`).
6. Verify (below). To leave the mesh: `sudo mesh-down`.

To change a setting for the whole fleet, edit `/etc/meshmap/mesh.conf` (or the repo copy before installing) identically on every unit, then `sudo mesh-up` again. `install.sh` never overwrites an existing `/etc/meshmap/mesh.conf`, and it backs up any older script it replaces as `*.bak`.

## Quick start: two units from scratch

On each unit (`raspberrypi1`, `raspberrypi2`), logged in over Ethernet/USB:

```bash
git clone <repo-url> meshmap && cd meshmap/mesh/bringup   # or copy the folder
./check-node.sh                      # expect 0 FAIL
sudo iw reg set FI                   # your country; also raspi-config → Localisation → WLAN country
sudo ./install.sh                    # also enables the mesh at every boot (--no-enable to skip)
sudo mesh-up                         # raspberrypi1 → 10.10.0.1, raspberrypi2 → 10.10.0.2
```

Then, from unit 1: `ping -c 4 10.10.0.2` and `sudo batctl meshif bat0 neighbors`. Start the second unit within a few metres first; move them apart only after the ping works.

## Disconnect and reconnect test

Run on one unit while pinging it from the other (`ping 10.10.0.1`):

```bash
sudo mesh-down        # pings stop; wlan0 is back in managed mode
sudo mesh-up          # pings resume within roughly 10-30 s
sudo batctl meshif bat0 neighbors   # the other node is listed again
```

The mesh has recovered if the ping resumes without touching the other unit. If it does not, the two units disagree on SSID, BSSID, frequency, routing algorithm or MTU (see troubleshooting).

## Verify

```bash
sudo batctl meshif bat0 interface        # wlan0: active
sudo batctl meshif bat0 neighbors        # direct neighbours with last-seen time
sudo batctl meshif bat0 originators      # all nodes and the next hop (multi-hop: next hop != destination)
ping -c 4 10.10.0.2                      # from node 1
sudo batctl meshif bat0 ping 02:ba:7a:00:00:02   # layer-2 ping, below IP
sudo batctl meshif bat0 throughputmeter 02:ba:7a:00:00:02
iperf3 -s   /   iperf3 -c 10.10.0.1      # TCP goodput over bat0
```

## Configuration notes

- **Starts at boot.** `install.sh` enables `mesh.service`, so every boot takes the Wi-Fi interface for the mesh and sets it to unmanaged in NetworkManager. Keep Ethernet or USB access to the unit. If the interface carries the default route, `mesh-up` refuses and the unit logs it (`journalctl -u mesh`). Turn it off with `sudo systemctl disable mesh`.

- **Frequency.** The deployed units use 5180 MHz (channel 36). In Finland 5150–5250 MHz is indoor-only (`iw reg get`: `NO-OUTDOOR`), so this is for the bench. For flights use 2.4 GHz (`FREQ_MHZ=2412`) or 5745 MHz and above, within the power limit shown by `iw reg get`. IBSS cannot use DFS channels (5250–5350, 5470–5725 MHz). `check-node.sh` warns about both.
- **MTU.** batman-adv adds a 32-byte header. The Wi-Fi interface stays at 1500 (brcmfmac cannot go higher) and `bat0` is set to 1400 so packets are not fragmented. Mesh-wide, every node must use the same `BAT_MTU`.
- **Routing algorithm.** `BATMAN_IV` by default. It is fixed when `bat0` is created, so changing it means `mesh-down` then `mesh-up`, and all nodes must match.
- **Distributed ARP table** is off, as in the deployed units.
- **Fixed BSSID** (`02:ca:fe:ca:fe:01`). Units set up with the older hand-made `mesh-up` joined with a random BSSID, so they form a different cell from units using this one. Move all units to these scripts together.
- **NetworkManager.** Only the mesh interface is set to unmanaged; other links (Ethernet, USB tether) stay up.
- The [adhoc-range](../harness/adhoc-range/README.md) test runs on the mesh this script brings up; it does not touch the radio.

## Known limitations

- **Pi onboard Wi-Fi (brcmfmac)** supports IBSS but not 802.11s mesh point, has no reliable HT in IBSS (legacy rates, up to 54 Mbit/s), and reports `txpower` and regulatory limits unreliably (it showed 31 dBm on channel 36 while the domain allows 23 dBm) (*verify* on each firmware). It is a baseline radio; a USB adapter (mt76, ath9k_htc) is the planned range radio ([hardware](../docs/technical.md#hardware)).
- The `batctl` and kernel module versions should match closely (Pi OS Trixie: batctl 2025.0 with batman-adv 2025.4 works). Mixing nodes on very different versions is untested.
- A node that is the only one in the cell shows no neighbours; that is normal.
- IBSS cells can partition; the fixed BSSID and fixed frequency reduce this but do not remove it.
- No GNSS time sync, ROS 2 transport or tuning here yet; see the [technical todo](../docs/technical.md#technical-todo).

## Troubleshooting

| Symptom | Likely cause and fix |
| --- | --- |
| `ibss join failed` | Frequency not allowed by the regulatory domain (check-node shows it); try `HT_MODE=NOHT`; `dmesg \| tail`. |
| Nodes do not see each other | Different `SSID`, `BSSID`, `FREQ_MHZ` or old-style units with a random BSSID; check `iw dev wlan0 link` on both. |
| `neighbors` empty but `link` shows the cell | Different `ROUTING_ALGO` or batman-adv versions on the nodes. |
| Ping works but large transfers stall | MTU mismatch; set the same `BAT_MTU` everywhere. |
| Lost SSH after `mesh-up` | You were logged in over Wi-Fi. Use Ethernet/USB; the script refuses this unless `FORCE=1`. |
| `cannot set routing algorithm` | Not root, or `batctl` too old; `sudo apt install batctl`. |
| Hostname error | The hostname must end in a number, or pass the id: `sudo mesh-up 3`. |
