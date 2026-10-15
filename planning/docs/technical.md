# P2 Path planning for photogrammetry — Technical

[← Main doc](../../docs/README.md) · [P2 overview](../README.md) · [Academic](academic.md)

How missions are computed, simulated and flown.

## Planner architecture

```mermaid
flowchart LR
    AOI[AOI polygon + no-fly zones] --> VP[viewpoint generator]
    RIG[rig geometry + camera model] --> VP
    LCM[P1 link-capacity model] --> COST[goodput cost map]
    VP --> ALLOC[multi-UAV split: partition / mTSP]
    COST --> ALLOC
    ALLOC --> PATH[per-UAV path + trigger points]
    PATH --> MIS[MAVROS mission push]
    QL[P3 quick-look coverage] -. holes .-> REPLAN[online re-plan] --> MIS
```

## Camera and footprint math

For a nadir camera at height *h* above ground, with pixel pitch *p*, focal length *f* and image size *W* × *H* px:

```latex
\mathrm{GSD} = \frac{p \, h}{f}, \qquad
\text{footprint} = \mathrm{GSD}\cdot W \times \mathrm{GSD}\cdot H
```

```latex
\text{line spacing} = \mathrm{GSD}\cdot W\,(1 - o_{\text{side}}), \qquad
\text{trigger distance} = \mathrm{GSD}\cdot H\,(1 - o_{\text{fwd}})
```

The examples below assume Pi Camera Module 3 (IMX708: 1.4 µm pixels, 4608 × 2592 px, f = 4.74 mm), with the long side across track and 70% side / 80% forward overlap.

| Height | GSD | Footprint | Line spacing | Trigger distance | Interval at 8 m/s |
| --- | --- | --- | --- | --- | --- |
| 50 m | 1.48 cm | 68 × 38 m | 20.4 m | 7.7 m | ~1.0 s |
| 80 m | 2.36 cm | 109 × 61 m | 32.7 m | 12.3 m | ~1.5 s |
| 120 m | 3.54 cm | 163 × 92 m | 49.0 m | 18.4 m | ~2.3 s |

These are calculated values. Check them against calibrated intrinsics once the rig is built.

**Oblique cameras** tilted θ from nadir (vertical FOV φ) cover the ground from *h*·tan(θ − φ/2) to *h*·tan(θ + φ/2) out from the nadir point. GSD at the image centre is roughly GSD<sub>nadir</sub> / cos θ across the tilt direction and GSD<sub>nadir</sub> / cos²θ along it. At θ = 30°, that is about 1.15× and 1.33× the nadir GSD.

**Rig layout options (decide before building):**

| Option | Obliques point | Pro | Con |
| --- | --- | --- | --- |
| A | Left + right (cross-track) | Wider swath, fewer lines | Only 2 view directions per pass; double-grid needed for 4 |
| B | Forward + back (along-track) | Strong along-track parallax | Same swath as nadir |

## Software stack

| Component | Tool |
| --- | --- |
| Geometry | Python, Shapely, pyproj (UTM) |
| Area split + routing | Polygon partition (equal-area strips) + Google OR-Tools VRP/mTSP |
| Goodput cost | Grid raster built from the P1 link-capacity model (hops, distance, altitude) |
| Quality score | Smith-style heuristics on a coarse DEM (Copernicus DEM or the first quick-look map) |
| Mission upload | MAVROS `/mavros/mission/push` (waypoints + `DO_SET_CAM_TRIGG_DIST`), or MAVSDK |
| Simulation | PX4 SITL + Gazebo (Harmonic), multi-vehicle launch |
| Network emulation | `tc netem` between SITL containers, driven by the link-capacity model; Mininet-WiFi as an option (*verify* batman-adv support) |

```bash
# example: emulate a 2-hop link at 4 Mbit/s, 40 ms, 2% loss between containers
tc qdisc add dev veth-uav1 root netem rate 4mbit delay 40ms 10ms loss 2%
```

## Mission conventions

- Altitude AGL, constant per mission, with terrain following off in phase 1.
- PX4 triggers the cameras by distance (`TRIG_MODE` distance-based). The `camera_capture` feedback events are logged for geotag checks (P3).
- Turn-around legs extend beyond the AOI so no image is taken mid-turn. Piras et al. 2017 saw 2.3 m offsets at turns.
- Each UAV flies its own altitude layer (≥ 5 m apart) for basic separation.

## Technical todo

- [ ] Camera model module (intrinsics → GSD, footprint, oblique footprint)
- [ ] Lawnmower and double-grid generators → MAVROS missions; check in QGroundControl
- [ ] Multi-vehicle PX4 SITL + Gazebo launch; tc-netem link emulation driven by the P1 model
- [ ] Goodput cost raster and OR-Tools mTSP with the cost term
- [ ] Coverage checker (simulated footprints → % AOI at the target overlap)
- [ ] Online re-plan service: subscribe to P3 coverage holes, push mission updates
- [ ] Flight campaign B runbook (same AOI, all planners, same day)
