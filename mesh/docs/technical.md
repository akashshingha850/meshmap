# P1 Mesh networking — Technical

[← Main doc](../../docs/README.md) · [P1 overview](../README.md) · [Academic](academic.md)

How the mesh is built, configured and measured. Commands target Raspberry Pi OS (Bookworm) and ROS 2 Jazzy. Any value marked *verify* has not been tested on our hardware yet.

## Network architecture

```mermaid
flowchart LR
    subgraph UAV1[UAV 1]
        FC1[Pixracer / PX4] -- TELEM2 serial --> M1[MAVROS]
        CAM1[SIYI A8 mini] -- eth0, own subnet --> CAP1[capture node]
        M1 & CAP1 --> ZB1[zenoh bridge]
        ZB1 --> BAT1[bat0]
    end
    subgraph UAV2[UAV 2 / relay]
        BAT2[bat0]
    end
    subgraph GND[Ground server]
        BATG[bat0] --> ZBG[zenoh bridge] --> GS[ROS 2 ground stack]
    end
    BAT1 <-. 802.11 ad-hoc / mesh point .-> BAT2
    BAT2 <-. .-> BATG
    BAT1 <-. direct when in range .-> BATG
```

- **Layer 2:** BATMAN-adv makes every node look like it sits on one Ethernet segment (`bat0`). IP addressing is static per node: `10.10.0.<node-id>/24`.
- **Camera link:** the A8 mini sits on the Pi's `eth0` in its own subnet (`192.168.144.0/24`). Never add `eth0` to `bat0` and never forward between the two: the camera's RTSP stream would flood the mesh. Images cross the mesh only through the P3 scheduler.
- **Flight controller:** the Pixracer's PX4 build (`px4_fmu-v4`) has the uXRCE-DDS client disabled (`CONFIG_MODULES_UXRCE_DDS_CLIENT=n` in [default.px4board](https://github.com/PX4/PX4-Autopilot/blob/main/boards/px4/fmu-v4/default.px4board)), so MAVROS is the only ROS 2 path from the FC. That makes MAVROS-vs-uXRCE-DDS comparisons out of scope on this airframe.
- **ROS 2:** DDS stays on each host (`ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`). Only allow-listed topics cross the mesh through zenoh-bridge-ros2dds, as the zenoh-plugin-ros2dds README advises.
- **Time:** every UAV disciplines its clock from GNSS + PPS. The ground server syncs from a GNSS receiver or from a UAV over chrony.

## Hardware

| Item | Choice | Notes |
| --- | --- | --- |
| Companion computer | Raspberry Pi 5 (8 GB) | One per UAV; ground server is a laptop/mini-PC. Onboard Ethernet is used by the A8 mini |
| Flight controller | mRo Pixracer (FMUv4), PX4 | MAVROS on TELEM2. Turn off the onboard ESP8266 Wi-Fi bridge in flight: it is a second 2.4 GHz radio and a second MAVLink path (*verify* how on our board revision) |
| Radio, option A | Pi onboard Wi-Fi (brcmfmac) | Baseline only; ~60 m range in the UCI study; *verify* IBSS support; no 802.11s |
| Radio, option B | USB adapter with mt76 / ath9k_htc driver (e.g. ALFA AWUS036ACM, mt7612u) | Supports IBSS + mesh point; external antenna |
| Radio, option C | mini-PCIe ath9k/ath10k via M.2/PCIe HAT | Research-grade range (Hayat 2015 used Atheros cards); heavier |
| Antennas | Dual-band dipoles, vertical, below the airframe | Record placement and orientation per flight |
| GNSS | u-blox M8/M9/F9P with PPS pin | PPS → GPIO 18 |

## Mesh bring-up (BATMAN-adv over IBSS)

Use the scripts in [bringup/](../bringup/README.md) (`check-node.sh`, `install.sh`, `mesh-up.sh`); the commands below show what they do. Deployed settings are SSID `mesh-net`, 5180 MHz (indoor-only in Finland), `10.10.0.<node-id>/24`, where the node id is the number at the end of the hostname.

```bash
# one-time
sudo apt install batctl iw gpsd chrony iperf3
echo batman-adv | sudo tee /etc/modules-load.d/batman-adv.conf

# per boot (mesh-up.sh)
IF=wlan1; MESH=meshmap; FREQ=5180; BSSID=02:ca:fe:ca:fe:01
sudo modprobe batman-adv
sudo batctl routing_algo BATMAN_IV          # or BATMAN_V; must be set before bat0 exists
sudo ip link set $IF down
sudo iw dev $IF set type ibss
sudo ip link set $IF mtu 1532               # batman-adv adds a 32 B header
sudo ip link set $IF up
sudo iw dev $IF ibss join $MESH $FREQ HT20 fixed-freq $BSSID
sudo batctl meshif bat0 interface add $IF   # older batctl: batctl if add $IF
sudo ip link set bat0 up
sudo ip addr add 10.10.0.${NODE_ID}/24 dev bat0
```

### Underlay variant: 802.11s mesh point with forwarding off

```bash
sudo iw dev $IF interface add mesh0 type mp
sudo ip link set mesh0 mtu 1532 && sudo ip link set mesh0 up
sudo iw dev mesh0 mesh join $MESH freq $FREQ HT20
sudo iw dev mesh0 set mesh_param mesh_fwding 0   # let batman-adv do routing, not HWMP
sudo batctl meshif bat0 interface add mesh0
```

### Tuning levers

| Parameter | Command | Default | Sweep |
| --- | --- | --- | --- |
| OGM interval (IV, V) | `batctl orig_interval <ms>` | 1000 ms | 1000, 500, 250, 100 |
| Hop penalty | `batctl hop_penalty <0-255>` | 30 (*verify*) | 15, 30, 60 |
| ELP interval (V) | `batctl hardif <if> elp_interval <ms>` | 500 ms (*verify*) | 500, 200, 100 |
| Throughput override (V) | `batctl hardif <if> throughput_override <Mbit>` | auto | auto only |
| Multicast optimisation | `batctl multicast_forceflood 0/1` | on | on/off (for RQ1.4) |

Before campaign A, check every default against open-mesh.org and `batctl -h` for the installed version.

### Babel baseline

`babeld` on top of the same IBSS/mesh interfaces, but with no `bat0`. IP routing happens on `wlan1` directly.

## ROS 2 transport configurations

| Config | Setup |
| --- | --- |
| rmw_zenoh | `RMW_IMPLEMENTATION=rmw_zenoh_cpp`; one `rmw_zenohd` router per host, peers connected over `bat0` |
| zenoh-bridge-ros2dds | Local DDS on each host + bridge with `allow` list (below) |
| Tuned CycloneDDS | `CYCLONEDDS_URI` with `MaxMessageSize` ≈ 1400 B, unicast peer list, multicast off |
| Fast DDS Discovery Server | `ROS_DISCOVERY_SERVER=10.10.0.1:11811` on the ground server |

```json5
// zenoh-bridge-ros2dds config (UAV side), allow-list only what crosses the mesh
{
  plugins: { ros2dds: {
    namespace: "/uav1",
    allow: {
      publishers: ["/mavros/global_position/global", "/mavros/local_position/pose",
                   "/mavros/state", "/meshmap/image_meta", "/meshmap/image_jpeg", "/meshmap/thumb"],
      subscribers: ["/meshmap/request"],
    },
  }},
  mode: "peer",
  connect: { endpoints: ["tcp/10.10.0.1:7447"] },
}
```

QoS: telemetry uses best-effort with depth 1, which matches PX4's publishers. Image metadata uses reliable with depth 10. Image payloads use reliable with depth 1 (the latest image wins).

## Time sync (GNSS + PPS → chrony)

```ini
# /boot/firmware/config.txt
dtoverlay=pps-gpio,gpiopin=18
```

```ini
# /etc/chrony/chrony.conf
refclock SHM 0 refid NMEA offset 0.2 delay 0.2 noselect
refclock PPS /dev/pps0 refid PPS lock NMEA prefer
allow 10.10.0.0/24
```

Log `chronyc tracking` once a second on every node. The offset between nodes is a measured outcome (RQ1 / RQ4), not an assumption.

## Measurement harness

| Measurement | Tool | Output |
| --- | --- | --- |
| Link goodput | `iperf3 -c <peer> -t 30 [-u -b <rate>]`; `batctl throughputmeter <mac>` | CSV per run |
| Route state | `batctl originators` / `batctl neighbors` every 200 ms | Route-change log with timestamps |
| Convergence time | Link break (node moves out of range) → first packet on new route, from a 50 Hz UDP probe | Seconds |
| Per-image latency | Capture GNSS time vs ground receive time (from `image_meta`) | Per-image CSV |
| Discovery bytes | `tcpdump -i bat0` on every hop, filtered on RTPS/Zenoh ports | Bytes per hop |
| Radio | `iw dev <if> station dump` (RSSI, tx bitrate, retries) at 1 Hz | CSV |

The two-node range and signal-quality test (step 2 of the procedure below) is implemented in [harness/adhoc-range](../harness/adhoc-range/README.md); it runs on the live mesh (bat0, `10.10.0.0/24`), so bring the mesh up first.

Log everything with GNSS-disciplined timestamps under `runs/<date>/<run-id>/<node>/`.

## Ground test procedure (before flights)

1. Bench: 3 nodes on a table with attenuators or reduced tx power (`iw dev <if> set txpower fixed 500`), to check that multi-hop forwarding works.
2. Line walk: one fixed node, one walked away in 10 m steps; iperf3 at each step for 30 s (as in Cai et al.).
3. Relay geometry: A–relay–B in a line, to force 2 hops; repeat for 3 hops.
4. Mobility: carry nodes on foot and in a vehicle; break links on purpose to measure convergence.
5. Repeat steps 2–4 for each tuning-lever setting and each transport.

## Technical todo

- [ ] Choose and buy radios (option B first); confirm IBSS + mesh point with `iw list`
- [x] Write `mesh-up.sh` / systemd unit (`bringup/`, checked on pi1 only, `mesh-up` not re-run since). [ ] Ansible role for all nodes
- [ ] gpsd + PPS + chrony on every node; log offsets
- [ ] zenoh-bridge config + QoS profiles; tuned CycloneDDS XML; Discovery Server launch
- [ ] Measurement harness scripts (probe, route logger, station dump, tcpdump rotation)
- [ ] Run `harness/adhoc-range` on two Pis (onboard brcmfmac first): confirm IBSS, HT and noise-floor behaviour, record the path loss exponent
- [ ] Bench and walk tests; first link-capacity table
- [ ] Flight campaign A runbook and checklist
- [ ] Export link-capacity model (goodput vs hops, distance, altitude) as a JSON/CSV file for P2 and P3
