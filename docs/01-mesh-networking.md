# Pipeline 1 — Mesh networking with BATMAN-adv

Goal: a BATMAN-adv mesh and ROS 2 transport, both tuned and measured. Telemetry must arrive reliably, and imagery at a known, measured rate. Flight evidence for BATMAN-adv is thin. One two-UAV study ranked default BATMAN-adv below Babel and OLSR and blamed the 1 s OGM interval ([Guillen-Perez et al. 2021](https://www.mdpi.com/2076-3417/11/10/4363)).

## Research study (state of the art)

| Topic | Key finding | Source |
| --- | --- | --- |
| Flown routing comparison | Babel > OLSR > BATMAN-adv at defaults. 2 UAVs at 10 m altitude; switched to the relay at ~60–70 m (2.4 GHz); no latency measured | [Guillen-Perez 2021](https://www.mdpi.com/2076-3417/11/10/4363) |
| 802.11s two-hop aerial | HWMP kept an unreliable direct route; only 3% of packets used a steady ~8 Mbps relay beyond 275 m | [Yanmaz 2014](https://mobile.aau.at/publications/yanmaz-2014-wcnc-two-hop-aerial.pdf) |
| Mobility and rate adaptation | Throughput swings and unfair sharing with several transmitting drones; ~30 Mbps at 500 m with Atheros cards | [Hayat 2015](https://mobile.aau.at/publications/hayat-2015-pimrc-drones.pdf) |
| Pi BATMAN-adv testbed | 19.7 Mbit/s at 0 m to 575 kbit/s at 45.6 m; ~60 m usable range on Pi 3B onboard Wi-Fi | [Cai et al., UCI](https://projects.eng.uci.edu/sites/default/files/Dynamic_Mesh_Network_for_Telemetry_Propagation_and_Communications_in_Coordinated_Drone_Swarms%20%28revised%29.pdf) |
| Field robot mesh | DARPA SubT MARBLE: meshmerize reconnects in ~1 s vs ~10 s for batman-adv; ~10 Mbit/s carried | [Biggie & McGuire 2022](https://arxiv.org/pdf/2203.12832) |
| ROS 2 over 802.11s | Zenoh: 76% lower delay, 146.93% higher reachability than Fast DDS; mesh carried 270 kbit/s–1.31 Mbit/s | [Chovet 2025](https://arxiv.org/pdf/2407.03091v1) |
| ROS 2 over Wi-Fi/4G (Turku) | Zenoh wins on 1 KB (15 vs 51 ms); CycloneDDS wins on 256 KB (1574 vs 3022 ms) | [Zhang et al.](https://arxiv.org/html/2309.07496v4) |
| DDS on lossy links | 64 KB sample = ~44 fragments; at 1% PER, 330 KB delivery falls to 9%; tuning that caps messages at the MTU holds 12.9 Hz at 20% PER | [Lee 2025](https://arxiv.org/html/2508.11366v1) |
| Discovery storms | Model cuts DDS discovery completion time 25.3–39.7% on wireless | [Choi 2026](https://arxiv.org/abs/2608.02242) |
| Telemetry practice | Keep MAVROS/uXRCE-DDS local; bridge allow-listed topics only (zenoh-bridge-ros2dds) | [PX4 docs](https://raw.githubusercontent.com/PX4/PX4-Autopilot/main/docs/en/middleware/uxrce_dds.md), [zenoh-plugin-ros2dds](https://raw.githubusercontent.com/eclipse-zenoh/zenoh-plugin-ros2dds/main/README.md) |

**Gaps P1 targets:**

- No flight study reports convergence time in seconds.
- No flight comparison goes beyond 2 hops or 3 UAVs.
- No flight data exist for BATMAN-adv over 802.11s mesh-point interfaces.
- No ROS 2 benchmark has run over a flying BATMAN-adv mesh with real image payloads.
- One hypothesis is untested: BATMAN-adv flooding should repeat DDS multicast discovery traffic once per hop.

## Scope

**In scope**

- 3–5 nodes (UAVs + ground relays + ground server), 1–3+ hops, 2.4 and 5 GHz, BATMAN-adv IV vs V, Babel as the routing baseline
- Tuning levers: `orig_interval`, hop penalty, B.A.T.M.A.N. V throughput metric, ad-hoc vs 802.11s mesh-point underlay
- ROS 2 transports: rmw_zenoh, zenoh-bridge-ros2dds, tuned CycloneDDS, Fast DDS Discovery Server
- Payloads: MAVROS telemetry, JPEG stills at several qualities/scales, thumbnails
- Clock sync: GNSS/PPS on each UAV; chrony accuracy over the mesh measured
- Metrics: per-hop and end-to-end goodput, p50/p95 latency, PDR, route convergence time, discovery bytes per hop

**Out of scope**

- Cellular/5G backhaul (complementary to Oulu/VTT work, cited only)
- New routing protocol design; security and encryption beyond basic WPA3/SAE
- Antenna design (use off-the-shelf dipoles; record placement)

## Todo

- [ ] Read open-mesh.org docs for BATMAN-adv IV/V tuning parameters; record verified values
- [ ] Fetch arXiv 2606.27028 (drone-swarm RF/Wi-Fi testbed) and check overlap with C3/C5
- [ ] Choose radios: Pi onboard Wi-Fi vs USB (ALFA) vs mini-PCIe Atheros; bench-test throughput vs distance
- [ ] Build a reproducible mesh image with Ansible (batctl, alfred, chrony, gpsd + PPS)
- [ ] Ground tests: iperf3 TCP/UDP at 1/2/3 hops, with nodes carried on foot and in a vehicle
- [ ] Implement measurement harness: per-image capture-to-ground latency, PDR, route-change log from `batctl o` and `batctl n`
- [ ] Benchmark ROS 2 transports with real image topics; measure how multicast traffic multiplies per hop
- [ ] Flight campaign A: OGM interval sweep, IV vs V vs Babel, convergence time in seconds
- [ ] Derive link-capacity model (goodput vs hop count, distance, altitude) for P2 and P3
- [ ] Release mesh config + dataset
