# Integration — Academic

[← Main doc](../../docs/README.md) · [Integration overview](../README.md) · [Technical](technical.md)

All three pipelines share one flight dataset. Every flight logs network, timing and photogrammetric data together. One campaign can therefore support three papers: networking (C3, C5), accuracy (C1, C4) and methods (C2, C7).

## Positioning

No reviewed paper combines low-cost UAV gimbal-camera capture, image + MAVROS traffic over a multi-hop BATMAN-adv mesh, and live photogrammetry on a ground server with no internet. Five neighbouring fields each cover part of this, and none covers all of it:

| Strand | Closest prior work | What it leaves out |
| --- | --- | --- |
| Mesh routing tested in flight | Guillen-Perez 2021; Yanmaz 2014; Hayat 2015 | 2 UAVs, 1–2 hops, no images, no photogrammetry, no ROS |
| ROS 2 over wireless/mesh | Chovet 2025; Zhang et al. (TIERS); Lee 2025 | Ground rovers, ≤ 64 KB synthetic payloads, 802.11s not BATMAN-adv |
| Real-time UAV mapping | OpenREALM 2020; AIT 2021–2025; Wischounig-Strucl 2012/2015 | Single-hop links; link behaviour not studied together with accuracy |
| Low-cost / oblique photogrammetry | Nesbit 2019; Bannakulpiphat 2024; Piras 2017 | No trigger-latency or geotag study for SDK-triggered gimbal cameras; no real-time use |
| Robot meshes proven in the field | DARPA SubT MARBLE 2022; CHORD (JPL) 2021 | Ground robots, ROS 1, imagery for situational awareness rather than mapping |
| Planning for coverage + connectivity | Smith 2018; Zhang 2023; Samshad & Rajawat 2024 | Quality and connectivity are never planned together; range, not goodput |

**Regional angle:** Oulu and VTT drone-connectivity work is cellular (5GTN, 5G!Drones, a drone-mounted 5G base station). No Oulu/VTT publication on Wi-Fi mesh drones was found, so this project complements that work.

## Contributions and venues

| # | Contribution | Pipeline | Novelty confidence | First target |
| --- | --- | --- | --- | --- |
| C1 | Joint network + GCP-accuracy evaluation on 1–3 hop BATMAN-adv | P1 + P3 | High | ICUAS 2027, then MDPI Drones |
| C2 | Image scheduling that adapts to the mesh link and to SfM needs | P3 | High | DroNet 2027 |
| C3 | ROS 2 transport benchmark over flying BATMAN-adv | P1 | High, but most exposed to unseen IEEE work | ICUAS / JIRS / Ad Hoc Networks |
| C4 | Low-cost gimbal-camera capture (A8 mini + Pi 5), trigger-latency and geotag-error study | P3 | Medium (less novel than the old 3-camera rig; check overlap) | ISPRS GSW / UAV-g 2027 |
| C5 | Tuned BATMAN-adv in flight, convergence time, 3+ hops | P1 | Medium | IEEE VTC / GLOBECOM workshops |
| C6 | Onboard keyframe pre-filtering on the Pi 5 | P3 | Medium | DroneSys 2027 |
| C7 | Photogrammetric path planning for a mesh swarm that accounts for link goodput | P2 | Medium (searched only lightly) | ICUAS / IROS 2027 |

C1 + C2 together make the strongest paper. For ICUAS, use only uasconferences.com, because look-alike listings are predatory.

| Venue | Fit | Status |
| --- | --- | --- |
| ICUAS 2027 | C1–C3 | Deadline ~Feb 2027 (unverified) |
| DroNet 2027 @ MobiSys | C2, C6 | ~Mar–Apr 2027 (pattern only) |
| IROS 2027 | C7, robotics framing | ~1 Mar 2027 (unverified) |
| ISPRS GSW 2027 / UAV-g | C1, C4 | Early 2027 (unverified) |
| DroneSys 2027 @ SEC | C6 | ~late Jun 2027 (inferred) |
| MDPI Drones | Journal version | Rolling; IF 5.2, CiteScore 10.0, ~21–22 days to first decision ([MDPI](https://www.mdpi.com/journal/drones)) |
| IEEE IoT J / Ad Hoc Networks / JIRS | Journal version | Rolling |

## Joint evaluation

| Layer | Metrics | Pass/fail target |
| --- | --- | --- |
| Network (P1) | Per-hop and end-to-end goodput, per-image latency (p50/p95), PDR, convergence time, discovery bytes per hop | Telemetry PDR ≥ 99%; convergence measured in seconds |
| Planning (P2) | Flight time, energy, outage seconds, image count, completeness | Completeness equal to or better than lawnmower, with fewer outage seconds |
| System (P3) | Time-to-first-map, time-to-complete-map, bytes/km², CPU/GPU load and power | First usable overview within minutes of coverage (inferred target) |
| Photogrammetry (P3) | Horizontal/vertical RMSE on held-out check points, reprojection error, completeness, GSD | ≤ 10 cm GSD; ~1 m live without GCPs; decimetre after refinement |
| Timing (all) | Trigger-to-exposure latency and jitter, camera-to-autopilot offset, RMSE under injected offsets | velocity × jitter < GSD for refined; < 1 m for live |

Headline figure: RMSE (m) vs delivered Mbit, one curve per arm and hop count.

## Novelty check (before any submission)

- [ ] Search Google Scholar and IEEE Xplore for these combinations:
    - "BATMAN-adv" + "ROS 2"
    - "rmw_zenoh UAV"
    - mesh + "real-time photogrammetry" / orthomosaic
    - "FANET image offloading SfM"
    - "SIYI A8 mini" photogrammetry / gimbal camera trigger latency
    - connectivity-aware + reconstruction path planning
- [ ] Forward citations of Guillen-Perez 2021, Chovet 2025, OpenREALM 2020, Samshad & Rajawat 2024
- [ ] Read arXiv 2606.27028 for overlap with C3/C5
- [ ] Check ICRA/IROS/ICUAS/VTC/GLOBECOM 2024–2026 proceedings, which are behind the Xplore paywall

## Verification status

- **Checked (Oct 2026):** the sources linked in each pipeline's academic.md. P1/P3 sources come from the supplied literature review. P2 sources were looked up for this outline.
- **Unverified:**
    - CMU EarlyDiscard venue (SEC 2018?)
    - BATMAN-adv default and tuning values
    - all venue dates except MDPI Drones
    - Hardouin et al. IROS 2020 and the Zhou et al. 2020 survey (leads, not read)
- **Partly accessible:** the numeric tables in Guillen-Perez 2021; Map2DFusion/TerrainFusion/RTSfM numbers; Cotta et al. MAVROS vs uXRCE-DDS.
