# Pipeline 3 — Forward-feed photogrammetry with a swarm

Goal: a quick-look map on the ground server within minutes of covering the area, refined to decimetre accuracy after landing. Every image's path from capture to map is logged. Streaming every image at full resolution, continuously, is not feasible. A 5–10 MB still takes 5–10 s on a sustained 8 Mbps relay, while missions capture every 1–3 s. Three cameras triple the load. These figures are the review's own estimate.

## Research study (state of the art)

| Topic | Key finding | Source |
| --- | --- | --- |
| Progressive multi-UAV imagery | JPEG2000 sent in resolution layers, with priority for images covering new ground; 5.9 s to the low-res layer, 101 s to full, <13 cm mosaic deviation | [Wischounig-Strucl & Rinner 2015](https://pervasive.uni-klu.ac.at/BR/pubs/2015/Wischounig_MVA2015.pdf) |
| Real-time mapping (OpenREALM) | 5 MP subsampled to ~1.2 MP over ROS/Wi-Fi; MAVROS GNSS/heading; 0.53 m APE vs Metashape | [Kern et al. 2020](https://arxiv.org/pdf/2009.10492) |
| Edge SLAM to ground (AIT) | ORB-SLAM3 on Orin NX, ~2 Hz keyframes over LTE, ~0.9 s/frame on ground; 4.82 m XY without GCPs | [Haubenstock et al. 2025](https://isprs-archives.copernicus.org/articles/XLVIII-2-W11-2025/111/2025/isprs-archives-XLVIII-2-W11-2025-111-2025.pdf) |
| Multi-UAV keyframe mosaicking | ~10x lower bandwidth, ~100x fewer frames than video; no GCP accuracy | [Wu et al. 2026](https://www.mdpi.com/2673-4052/7/2/43) |
| Onboard filtering | EarlyDiscard: 7.0–10.7 Mbps cut to 0.03–0.43 Mbps; ground can request dropped frames later ("reachback") | [Wang et al., CMU](https://elijah.cs.cmu.edu/DOCS/drone2018-CAMERA-READY.pdf) |
| Compression vs SfM | Mild JPEG within ~1 cm of RAW; heavy compression up to ~15 cm, can break dense matching | [Alfio et al. 2020](https://www.mdpi.com/2313-433X/6/5/30) |
| Pi camera accuracy | ~1 cm at 12 m with RTK; up to 2.3 m GNSS-image offset at turns | [Piras et al. 2017](https://iris.polito.it/retrieve/handle/11583/2679327/535545) |
| Timing | Geotag error ≈ velocity × offset; GNSS-triggered capture <1 ms | [Sakr 2016](https://isprs-archives.copernicus.org/articles/XLI-B1/1017/2016/isprs-archives-XLI-B1-1017-2016.pdf), [Gueguen 2025](https://isprs-archives.copernicus.org/articles/XLVIII-G-2025/535/2025/) |
| Real-time accuracy bar | ~1 m absolute without GCPs | [Kern et al. 2021](https://isprs-archives.copernicus.org/articles/XLIII-B1-2021/165/2021/) |

**Gaps P3 targets:**

- No system reports bandwidth and GCP accuracy together on a multi-hop mesh (C1).
- No image scheduler since 2015 adapts to the link while accounting for SfM needs (C2).
- No peer-reviewed multi-Pi oblique rig has quantified accuracy or a sync-error study (C4).
- No study tests H.264/H.265 frames as SfM input.

## Scope

**In scope**

- Onboard (per UAV): capture from 3 Pi cameras stamped with GNSS/PPS time; full-res originals stored; keyframe and thumbnail selection; JPEG quality and scale chosen from measured link capacity; telemetry prioritised
- Ground server: incremental SfM and ortho quick-look (OpenREALM or COLMAP/OpenMVG incremental) using MAVROS pose priors; global refinement (Metashape/ODM) after landing
- Rig: calibration, fixed rig constraints in bundle adjustment, inter-camera sync spread measured
- Three arms on identical flights: offline (land then process), send-all, proposed adaptive
- Optional C6: Jetson companion for onboard keyframe selection, energy as share of flight energy

**Out of scope**

- Learned reconstruction (NeRF/3DGS) as the primary product; may appear only as a side comparison
- Video-codec streaming as the mapping input (tested once as a compression arm only)

## Todo

- [ ] Survey RTK GCPs and held-out check points at the test site before the first flight
- [ ] Build 3-camera rig; calibrate intrinsics and rig extrinsics; measure sync spread
- [ ] Implement capture node: GNSS-time stamps, onboard storage, ROS 2 image + metadata topics
- [ ] Implement scheduler: keyframe score (novelty + overlap), image quality and scale set from measured link capacity, priority queue
- [ ] Stand up ground pipeline: quick-look incremental map + post-flight refinement
- [ ] Compression study: RMSE vs JPEG quality and downscale, plus one H.264 arm
- [ ] Timing study: inject capture offsets, measure RMSE change
- [ ] Flight campaign C: three arms × 1/2/3 hops; log time-to-first-map, bytes/km², RMSE, completeness
- [ ] Plot the trade-off curve: RMSE vs delivered Mbit
