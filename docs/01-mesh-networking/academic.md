# P1 Mesh networking — Academic

[← P1 index](README.md) · [Technical](technical.md)

Goal: describe how a flying BATMAN-adv mesh behaves when tuned, together with the ROS 2 transport on top of it. Telemetry must arrive reliably, and imagery must arrive at a known, measured rate. Few studies have tested BATMAN-adv in flight. One two-UAV study ranked default BATMAN-adv below Babel and OLSR and blamed the 1 s OGM interval ([Guillen-Perez et al. 2021](https://www.mdpi.com/2076-3417/11/10/4363)).

## Research study (state of the art)

| Topic | Key finding | Source |
| --- | --- | --- |
| Routing protocols compared in flight | Babel > OLSR > BATMAN-adv at defaults. 2 UAVs at 10 m altitude; switched to the relay at ~60–70 m (2.4 GHz); no latency measured | [Guillen-Perez 2021](https://www.mdpi.com/2076-3417/11/10/4363) |
| 802.11s two-hop aerial | HWMP kept an unreliable direct route; only 3% of packets used a steady ~8 Mbps relay beyond 275 m | [Yanmaz 2014](https://mobile.aau.at/publications/yanmaz-2014-wcnc-two-hop-aerial.pdf) |
| Mobility and rate adaptation | Throughput swings and unfair sharing with several transmitting drones; ~30 Mbps at 500 m with Atheros cards | [Hayat 2015](https://mobile.aau.at/publications/hayat-2015-pimrc-drones.pdf) |
| Pi BATMAN-adv testbed | 19.7 Mbit/s at 0 m to 575 kbit/s at 45.6 m; ~60 m usable range on Pi 3B onboard Wi-Fi | [Cai et al., UCI](https://projects.eng.uci.edu/sites/default/files/Dynamic_Mesh_Network_for_Telemetry_Propagation_and_Communications_in_Coordinated_Drone_Swarms%20%28revised%29.pdf) |
| Field robot mesh | DARPA SubT MARBLE: meshmerize reconnects in ~1 s vs ~10 s for batman-adv; ~10 Mbit/s carried | [Biggie & McGuire 2022](https://arxiv.org/pdf/2203.12832) |
| ROS 2 over 802.11s | Zenoh: 76% lower delay, 146.93% higher reachability than Fast DDS; mesh carried 270 kbit/s–1.31 Mbit/s | [Chovet 2025](https://arxiv.org/pdf/2407.03091v1) |
| ROS 2 over Wi-Fi/4G (Turku) | Zenoh wins on 1 KB (15 vs 51 ms); CycloneDDS wins on 256 KB (1574 vs 3022 ms) | [Zhang et al.](https://arxiv.org/html/2309.07496v4) |
| DDS on lossy links | 64 KB sample = ~44 fragments; at 1% PER, 330 KB delivery falls to 9%; tuning that caps messages at the MTU holds 12.9 Hz at 20% PER | [Lee 2025](https://arxiv.org/html/2508.11366v1) |
| Discovery storms | Model cuts DDS discovery completion time 25.3–39.7% on wireless | [Choi 2026](https://arxiv.org/abs/2608.02242) |
| Telemetry practice | Keep MAVROS/uXRCE-DDS local; bridge allow-listed topics only (zenoh-bridge-ros2dds) | [PX4 docs](https://raw.githubusercontent.com/PX4/PX4-Autopilot/main/docs/en/middleware/uxrce_dds.md), [zenoh-plugin-ros2dds](https://raw.githubusercontent.com/eclipse-zenoh/zenoh-plugin-ros2dds/main/README.md) |
| ROS 2 wireless swarms | "Significant lack of optimisation" for ROS 2 wireless comms in swarms | [Castillo-Sanchez 2024](https://doaj.org/article/b47296672fe34499845e50da753c2899) |

## Gaps

- No flight study reports route convergence time in seconds. Published results give only switching distances.
- No flight comparison goes beyond 2 hops or 3 UAVs.
- No flight data exist for BATMAN-adv over 802.11s mesh-point interfaces.
- No ROS 2 middleware benchmark has run over a flying BATMAN-adv mesh with real image payloads.
- One hypothesis is untested: BATMAN-adv floods broadcast and multicast frames, so DDS multicast discovery traffic should be repeated once per hop.

## Research questions and hypotheses

- **RQ1.1:** How long does route convergence take, in seconds, for BATMAN IV, BATMAN V and Babel as UAVs move through 1–3+ hops?
    - *H1.1:* Cutting `orig_interval` from 1000 ms to ≤ 250 ms brings BATMAN IV convergence to within 2× of Babel, at a measurable cost in overhead.
- **RQ1.2:** Does B.A.T.M.A.N. V's throughput metric pick better relays than IV's packet-loss metric on mobile aerial links?
- **RQ1.3:** Which ROS 2 transport gives the highest image goodput and telemetry PDR over the flying mesh?
    - *H1.3:* A Zenoh bridge carrying allow-listed topics beats tuned DDS on telemetry latency and discovery bytes. Tuned CycloneDDS matches or beats Zenoh on large image payloads.
- **RQ1.4:** Do discovery bytes grow linearly with hop count under multicast DDS on BATMAN-adv?

## Research scope

**In scope:** 3–5 nodes; 1–3+ hops; 2.4 and 5 GHz; BATMAN IV vs V vs Babel; ad-hoc vs 802.11s underlay; four ROS 2 transports; real telemetry and image payloads; clock-sync accuracy over the mesh.

**Out of scope:** cellular/5G backhaul (complementary to Oulu/VTT work, cited only); new routing protocol design; security beyond basic WPA3/SAE; antenna design.

## Evaluation design

| Factor | Levels |
| --- | --- |
| Routing | BATMAN IV (default), BATMAN IV (tuned), BATMAN V, Babel |
| Underlay | IBSS ad-hoc, 802.11s mesh point with forwarding off |
| Hops | 1, 2, 3 (+4 if nodes allow) |
| Band | 2.4 GHz, 5 GHz |
| Transport | rmw_zenoh, zenoh-bridge-ros2dds, tuned CycloneDDS, Fast DDS Discovery Server |
| Payload | Telemetry only; telemetry + thumbnails; telemetry + full JPEG |

**Metrics:**

- per-hop and end-to-end goodput
- p50/p95 latency
- PDR
- convergence time, measured from link break to the first packet delivered on the new route
- discovery bytes per hop
- chrony offset

Run at least 3 repetitions per cell and report medians with IQR. Use a randomised run order within each flight day.

## Expected contributions

- **C3:** ROS 2 transport benchmark over flying BATMAN-adv, with real image payloads and multicast amplification measured per hop.
- **C5:** Tuned BATMAN-adv in flight, with convergence time in seconds and 3+ hops.
- Feeds **C1** (joint evaluation) with the link-capacity model.

## Target venues

ICUAS 2027, JIRS, Ad Hoc Networks, and IEEE VTC/GLOBECOM UAV workshops. See [cross-pipeline academic](../04-cross-pipeline/academic.md).

## Academic todo

- [ ] Read open-mesh.org docs on BATMAN IV/V, OGM/ELP intervals and hop penalty; cite them in the method
- [ ] Fetch arXiv 2606.27028 (drone-swarm RF/Wi-Fi testbed) and check overlap with C3/C5
- [ ] Forward-citation search on Guillen-Perez 2021 and Chovet 2025
- [ ] Pre-register the factor design and metrics (above) before campaign A
- [ ] Write related-work section for the networking paper
