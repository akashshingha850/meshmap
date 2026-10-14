# P2 Path planning for photogrammetry — Academic

[← P2 index](README.md) · [Technical](technical.md)

Goal: a multi-UAV planner that places nadir and oblique shots for a complete, accurate reconstruction. It must also keep every UAV within the measured mesh range of a relay or the ground server. Planning for reconstruction quality and planning for connectivity have each been studied, but never together. No paper found plans for both photogrammetric quality and multi-hop mesh goodput.

## Research study (state of the art)

| Strand | Representative work | What it gives P2 | What it leaves out |
| --- | --- | --- | --- |
| View planning for reconstruction quality | [Smith et al., SIGGRAPH Asia 2018](https://download.hrz.tu-darmstadt.de/media/FB20/GCC/paper/Smith-2018-APP.pdf): continuous optimisation with heuristics for multi-view stereo (MVS) quality; ≤1 cm GSD over 30,000 m²; public benchmark | Quality heuristics (triangulation angle, distance, overlap) and a benchmark | Single UAV, offline, no comms |
| Multi-UAV model-based planning | [Zhang, Zhang & Liu, ISPRS 2023](https://isprs-archives.copernicus.org/articles/XLVIII-1-W2-2023/1923/2023/): viewpoints from a coarse model, split by mTSP | Two-stage (coarse → refined) multi-UAV pattern | Needs prior model; no link model |
| Online next-best-view (NBV) | [Sportich et al. 2025](https://arxiv.org/abs/2511.20353v1): NBV driven by TSDF uncertainty, with a user-set quality target; Hardouin et al., IROS 2020: multi-UAV NBV (lead, not read) | Adaptive re-planning from live map uncertainty | Simulation only; assumes perfect comms |
| Connectivity-aware coverage | [Samshad & Rajawat 2024](https://arxiv.org/abs/2411.02772): minimises energy and inter-UAV connectivity radius together; 99% match of predicted vs actual range on 3 UAVs | Connectivity radius as an optimisation term | Area coverage, not photogrammetric geometry; range not goodput |
| Bandwidth- and storage-aware missions | [Politecnico di Bari, IEEE Netw. Lett. 2020](https://telematics.poliba.it/wp-content/uploads/publications/2020/Drones__IEEE_Networking_Letters.pdf): upload low-res copies to relieve onboard memory | Acquire-vs-offload budgeting | Cellular link; no SfM quality |
| Oblique capture geometry | [Nesbit & Hugenholtz 2019](https://doaj.org/article/be5ee30f38c44109adff171ea06a3c98): 20–35° obliques improve accuracy ~50% in high relief; [Nikolakopoulos & Kyriou 2023](https://isprs-archives.copernicus.org/articles/XLVIII-1-W3-2023/131/2023/isprs-archives-XLVIII-1-W3-2023-131-2023.pdf): 1.21 vs 0.817 km² per grid | Rig tilt angles and expected gain | Not a planner |

## Gaps

- Connectivity constraints are expressed as range, not as measured multi-hop goodput.
- No planner decides *where to upload*, for example by flying into high-goodput zones before sending keyframes.
- No plan uses the fixed geometry of a 3-camera rig to cut the number of flight lines.
- NBV methods are untested over a lossy link, where the ground map lags behind the drone.

## Research questions and hypotheses

- **RQ2.1:** Does a planner with a goodput term reduce outage seconds and time-to-complete-map compared with lawnmower and double-grid baselines?
    - *H2.1:* With the same AOI and UAV count, the planner cuts outage seconds by ≥ 50% and loses no more than 5% in coverage completeness.
- **RQ2.2:** How much flight time does a fixed nadir-plus-two-oblique rig save compared with a double-grid flown with one camera, at equal RMSE?
- **RQ2.3:** Does re-planning online from the ground quick-look map (hole filling) improve completeness enough to justify the extra flight time?

## Formal problem (sketch)

Each UAV *k* follows a path *P_k* through candidate viewpoints *V*. The planner chooses paths that minimise

```latex
J = \sum_k T(P_k) \;-\; \alpha \, Q\!\left(\bigcup_k V_k\right) \;+\; \beta \sum_k \int_{P_k} \mathbb{1}\!\left[g(x) < g_{\min}\right] dt
```

- *T* is flight time.
- *Q* is a reconstruction-quality score covering coverage, triangulation angle and GSD (Smith-style heuristics).
- *g(x)* is the predicted end-to-end goodput at position *x*, taken from P1's link-capacity model.
- *g*<sub>min</sub> is the goodput needed by P3's scheduler.

Constraints: battery, altitude limits, AOI and no-fly polygons, and per-camera overlap.

## Research scope

**In scope:** terrain and low buildings; 2–4 UAVs; lawnmower, double-grid and Smith-style baselines; goodput-aware multi-UAV planner; optional relay placement; online hole filling.

**Out of scope:** complex 3D structures that need flights close along facades; collision avoidance beyond altitude separation; BVLOS regulatory work.

## Evaluation design

| Factor | Levels |
| --- | --- |
| Planner | Lawnmower, double-grid, quality-only, quality + goodput (proposed) |
| UAVs | 1, 2, 3 |
| Relay | None, fixed ground relay, relay UAV |
| Online re-plan | Off, on |

Metrics: flight time, energy (Wh), image count, outage seconds, time-to-complete-map, coverage completeness, and RMSE on check points (shared with P3). Run in SITL first (many seeds), then flight campaign B on one AOI.

## Expected contribution

- **C7:** goodput-aware photogrammetric path planning for a mesh swarm.
- Supports **C1**, because a plan that keeps the link alive makes the joint evaluation possible.

## Academic todo

- [ ] Read Hardouin et al. IROS 2020 and the Zhou et al. 2020 path/view-planning survey
- [ ] Targeted search: connectivity-aware + reconstruction planning, "data ferrying" + photogrammetry
- [ ] Fix the quality score *Q* (choose heuristics; justify from Smith 2018)
- [ ] Write the formal problem and its complexity (mTSP reduction ⇒ NP-hard)
- [ ] Related-work section for C7
