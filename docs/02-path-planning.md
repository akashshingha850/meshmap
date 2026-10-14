# Pipeline 2 — Path planning for photogrammetry

Goal: a multi-UAV planner that places nadir and oblique shots for a complete, accurate reconstruction. It must also keep every UAV within the measured mesh range of a relay or the ground server. Planning for reconstruction quality and planning for connectivity have each been studied, but never together. No paper found plans for both photogrammetric quality and multi-hop mesh goodput.

## Research study (state of the art)

| Strand | Representative work | What it gives P2 | What it leaves out |
| --- | --- | --- | --- |
| View planning for reconstruction quality | [Smith et al., SIGGRAPH Asia 2018](https://download.hrz.tu-darmstadt.de/media/FB20/GCC/paper/Smith-2018-APP.pdf): continuous optimisation with heuristics for multi-view stereo (MVS) quality; ≤1 cm GSD over 30,000 m²; public benchmark | Quality heuristics (triangulation angle, distance, overlap) and a benchmark | Single UAV, offline, no comms |
| Multi-UAV model-based planning | [Zhang, Zhang & Liu, ISPRS 2023](https://isprs-archives.copernicus.org/articles/XLVIII-1-W2-2023/1923/2023/): viewpoints from a coarse model, split by mTSP | Two-stage (coarse → refined) multi-UAV pattern | Needs prior model; no link model |
| Online next-best-view (NBV) | [Sportich et al. 2025](https://arxiv.org/abs/2511.20353v1): NBV driven by TSDF uncertainty, with a user-set quality target; Hardouin et al., IROS 2020: multi-UAV NBV (lead, not read) | Adaptive re-planning from live map uncertainty | Simulation only; assumes perfect comms |
| Connectivity-aware coverage | [Samshad & Rajawat 2024](https://arxiv.org/abs/2411.02772): minimises energy and inter-UAV connectivity radius together; 99% match of predicted vs actual range on 3 UAVs | Connectivity radius as an optimisation term | Area coverage, not photogrammetric geometry; range not goodput |
| Bandwidth- and storage-aware missions | [Politecnico di Bari, IEEE Netw. Lett. 2020](https://telematics.poliba.it/wp-content/uploads/publications/2020/Drones__IEEE_Networking_Letters.pdf): upload low-res copies to relieve onboard memory | Acquire-vs-offload budgeting | Cellular link; no SfM quality |
| Oblique capture geometry | [Nesbit & Hugenholtz 2019](https://doaj.org/article/be5ee30f38c44109adff171ea06a3c98): 20–35° obliques improve accuracy ~50% in high relief | Rig tilt angles and expected gain | Not a planner |

**Gaps P2 targets:**

- Connectivity constraints are expressed as range, not as measured multi-hop goodput.
- No planner decides *where to upload*, for example by flying into high-goodput zones before sending keyframes.
- No plan uses the fixed geometry of a 3-camera rig to cut the number of flight lines.
- NBV methods are untested over a lossy link, where the ground map lags behind the drone.

## Scope

**In scope**

- Baselines: lawnmower (boustrophedon) grid at 80/70% overlap, double-grid (cross-hatch), and a plan optimised for quality in the style of Smith et al.
- Proposed: an objective for coverage and oblique geometry, plus a connectivity term built from P1's measured goodput map (hops, distance, altitude)
- Multi-UAV task split (mTSP / area partition) with optional relay UAV placement
- Online re-plan: fly back to fill holes found in the ground quick-look map (P3), and return into range to upload
- Platform: PX4 + MAVROS mission upload, simulated first in Gazebo/PX4 SITL with an emulated mesh (ns-3 or tc/netem)

**Out of scope**

- Complex 3D structures that need flights close along building facades (stay with terrain and low buildings)
- Collision avoidance beyond altitude separation; BVLOS regulatory work beyond what the test site permits

## Todo

- [ ] Fetch and read Hardouin et al. IROS 2020 and the Zhou et al. 2020 path/view-planning survey; add to related work
- [ ] Fix rig geometry (tilt angles, focal lengths) and compute footprint/GSD per camera at 40–120 m
- [ ] Implement baselines (lawnmower, double-grid) as MAVROS missions
- [ ] Build goodput map from P1 data and encode it as a planning cost
- [ ] Implement multi-UAV planner (partition + mTSP + connectivity term); test in SITL with a mesh emulated by netem
- [ ] Add online hole-filling from P3 coverage feedback
- [ ] Flight campaign B: baselines vs proposed on the same AOI; log flight time, energy, outage seconds, image count
- [ ] Report coverage completeness and RMSE per plan (shared with P3)
