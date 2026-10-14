# P3 Forward-feed swarm photogrammetry — Academic

[← P3 index](README.md) · [Technical](technical.md)

Goal: a quick-look map on the ground server within minutes of covering the area, refined to decimetre accuracy after landing. Every image's path from capture to map is logged. Streaming every image at full resolution, continuously, is not feasible. A 5–10 MB still takes 5–10 s on a sustained 8 Mbps relay, while missions capture every 1–3 s. Three cameras triple the load. These figures are the review's own estimate.

## Research study (state of the art)

| Topic | Key finding | Source |
| --- | --- | --- |
| Progressive multi-UAV imagery | JPEG2000 sent in resolution layers, with priority for images covering new ground; 5.9 s to the low-res layer, 101 s to full, <13 cm mosaic deviation | [Wischounig-Strucl & Rinner 2015](https://pervasive.uni-klu.ac.at/BR/pubs/2015/Wischounig_MVA2015.pdf) |
| Multi-UAV networking agenda | Off-the-shelf 802.11 "poorly suited"; delay-tolerant networking and cooperative relaying proposed as next steps | [Hellwagner & Bettstetter, TNC'17](https://tnc2017.geant.org/getfile/tnc17_paper_TNC17Multi-UAVNetworking.pdf) |
| Real-time mapping (OpenREALM) | 5 MP subsampled to ~1.2 MP over ROS/Wi-Fi; MAVROS GNSS/heading; 0.53 m APE vs Metashape | [Kern et al. 2020](https://arxiv.org/pdf/2009.10492) |
| Edge SLAM to ground (AIT) | ORB-SLAM3 on Orin NX, ~2 Hz keyframes over LTE, ~0.9 s/frame on ground; 4.82 m XY without GCPs | [Haubenstock et al. 2025](https://isprs-archives.copernicus.org/articles/XLVIII-2-W11-2025/111/2025/isprs-archives-XLVIII-2-W11-2025-111-2025.pdf) |
| Multi-UAV keyframe mosaicking | ~10x lower bandwidth, ~100x fewer frames than video; no GCP accuracy | [Wu et al. 2026](https://www.mdpi.com/2673-4052/7/2/43) |
| Onboard filtering | EarlyDiscard: 7.0–10.7 Mbps cut to 0.03–0.43 Mbps; ground can request dropped frames later ("reachback") | [Wang et al., CMU](https://elijah.cs.cmu.edu/DOCS/drone2018-CAMERA-READY.pdf) |
| Compression vs SfM | Mild JPEG within ~1 cm of RAW; heavy compression up to ~15 cm, can break dense matching | [Alfio et al. 2020](https://www.mdpi.com/2313-433X/6/5/30) |
| Oblique accuracy | 20–35° obliques improve accuracy ~50% in high relief; bundle adjustment uses oblique rays only moderately | [Nesbit & Hugenholtz 2019](https://doaj.org/article/be5ee30f38c44109adff171ea06a3c98), [Bannakulpiphat 2024](https://isprs-archives.copernicus.org/articles/XLVIII-2-W7-2024/17/2024/) |
| Pi camera accuracy | ~1 cm at 12 m with RTK; up to 2.3 m GNSS-image offset at turns | [Piras et al. 2017](https://iris.polito.it/retrieve/handle/11583/2679327/535545) |
| Timing | Geotag error ≈ velocity × offset; GNSS-triggered capture <1 ms | [Sakr 2016](https://isprs-archives.copernicus.org/articles/XLI-B1/1017/2016/isprs-archives-XLI-B1-1017-2016.pdf), [Gueguen 2025](https://isprs-archives.copernicus.org/articles/XLVIII-G-2025/535/2025/) |
| Real-time accuracy bar | ~1 m absolute without GCPs | [Kern et al. 2021](https://isprs-archives.copernicus.org/articles/XLIII-B1-2021/165/2021/) |
| End-user requirement | Copernicus EMS: ≤ 0.1 m GSD ortho, ideally 0.5 m DEM vertical, delivered within hours to days | [CEMS portfolio](https://mapping.emergency.copernicus.eu/about/rapid-mapping-portfolio/) |

## Gaps

- No system reports bandwidth and GCP accuracy together on a multi-hop mesh (C1).
- No image scheduler since 2015 adapts to the link while accounting for SfM needs (C2).
- No peer-reviewed multi-Pi oblique rig has quantified accuracy or a sync-error study (C4).
- No study tests H.264/H.265 frames as SfM input.
- Nobody has measured how inter-UAV clock offset affects multi-UAV SfM.

## Research questions and hypotheses

- **RQ3.1:** How does map accuracy trade off against delivered bytes? Accuracy is RMSE on check points, for the quick-look and the refined product.
    - *H3.1:* At ≤ 20% of the send-all byte volume, the adaptive scheme reaches ≤ 1 m live RMSE without GCPs. After refinement it matches the offline baseline within 10%.
- **RQ3.2:** Does choosing keyframes by SfM value (novelty, overlap, view angle) beat uniform subsampling at equal bytes?
- **RQ3.3:** How much RMSE do the oblique cameras add or save at equal flight time, and how sensitive is it to inter-camera sync error (ms)?
- **RQ3.4:** At what JPEG quality and downscale factor does the quick-look map start to fail (tie points, completeness)?

## Research scope

**In scope:** onboard capture stamped with GNSS time; full-res originals stored onboard; scheduler that adapts to the link; incremental ground quick-look; refinement after the flight; 3-camera rig calibration and sync study; three experimental arms; optional Jetson onboard filtering (C6).

**Out of scope:** NeRF/3DGS as the primary product (side comparison only); video codecs as the mapping input (one compression arm only).

## Evaluation design

Three arms flown on the same flights and AOI:

| Arm | What crosses the mesh | Map produced |
| --- | --- | --- |
| Offline (baseline) | Telemetry only | Full-res, GCP-constrained, after landing |
| Send-all | Every full-res image | Incremental, as images arrive |
| Adaptive (proposed) | Keyframes/thumbnails at a link-adapted quality + pose priors; reachback on request | Quick-look live → refined after landing |

| Layer | Metrics |
| --- | --- |
| System | Time-to-first-map, time-to-complete-map, bytes/km², capture-to-tile latency, CPU/GPU load, power |
| Photogrammetry | Horizontal/vertical RMSE on held-out RTK check points, reprojection error, tie points, completeness (% AOI, cloud-to-cloud vs offline), GSD |
| Timing | Camera-to-autopilot offset, inter-camera sync spread, RMSE under injected offsets |
| Compression | RMSE and completeness vs JPEG quality, downscale factor, and one H.264 arm |

Each arm runs at 1, 2 and 3 hops, with adaptation switched on and off. Report the RMSE-vs-Mbit trade-off curve as the headline figure.

## Expected contributions

- **C1:** joint network + GCP-accuracy evaluation (with P1).
- **C2:** image scheduling that adapts to the mesh link and to SfM needs.
- **C4:** low-cost 3-Pi nadir + oblique rig, with a sync-error study.
- **C6 (optional):** onboard keyframe pre-filtering on a Jetson, with energy as a share of flight energy.

## Academic todo

- [ ] Read OpenREALM and AIT pipelines in full; note their metrics and how they compute them
- [ ] Search "multi-camera Raspberry Pi UAV oblique" and "H.264 SfM accuracy" for overlap
- [ ] Define the keyframe score formally; justify it from SfM view-selection literature
- [ ] Fix GCP / check point layout (count, distribution) following ISPRS practice
- [ ] Write related-work sections for C1, C2 and C4
