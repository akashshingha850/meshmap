# Cross-pipeline — Interfaces

[← Cross-pipeline index](README.md) · [Technical](technical.md)

The contracts between P1, P2 and P3. Each pipeline can change anything inside its own folder freely, but a change to anything on this page follows the [interface change process](../../CONTRIBUTING.md#changing-an-interface).

**Status: draft v0.1** — field names and topics are proposals until the first bench integration. Machine-readable schemas will live in [`common/schemas/`](../../common/).

## Overview

| ID | Interface | Producer | Consumers | Form | When |
| --- | --- | --- | --- | --- | --- |
| I1 | Link-capacity model | P1 | P2, P3 | `link_model.json` file | Offline, after each test campaign |
| I2 | Live goodput estimate | P1 | P3 | ROS 2 topic | In flight |
| I3 | Mission plan | P2 | flight ops, P3 | PX4 mission + `plan.json` | Before flight, and on re-plan |
| I4 | Image record | P3 | ground, evaluation, P1 latency stats | `images.jsonl` + `image_meta` topic | Per capture |
| I5 | Coverage holes | P3 (ground) | P2 re-planner | ROS 2 topic (GeoJSON) | In flight |
| I6 | Run metadata | all | all, `analysis/` | `run.yaml` | Per run |

## Shared conventions

- **Time:** UTC, from GNSS/PPS-disciplined clocks (chrony). ISO 8601 with microseconds in files; `builtin_interfaces/Time` in ROS messages.
- **Coordinates:** WGS84 lat/lon + `alt_amsl` in files; UTM (zone of the test site) for planning maths. Angles in degrees.
- **Units:** SI; bit rates in Mbit/s; sizes in bytes.
- **Vehicle names:** `uav1`, `uav2`, …; ground nodes `gnd`, `relay1`, …
- **ROS namespaces:** `/<node>/...`, e.g. `/uav1/meshmap/image_meta`. Only allow-listed topics cross the mesh (see [P1 transport](../01-mesh-networking/technical.md#ros-2-transport-configurations)).

## I1 — Link-capacity model (P1 → P2, P3)

Measured goodput as a function of hops, distance and altitude. P2 turns it into a cost raster and drives `tc netem` in SITL; P3 uses it as the prior bandwidth budget.

```json
{
  "version": "0.1",
  "measured": "2026-12-10",
  "underlay": "ibss", "routing": "batman-adv-iv", "transport": "zenoh",
  "entries": [
    {"hops": 1, "distance_m": 50, "alt_agl_m": 30,
     "goodput_mbps_p50": 8.2, "goodput_mbps_p10": 5.1,
     "latency_ms_p50": 12, "loss": 0.01}
  ]
}
```

## I2 — Live goodput estimate (P1 → P3)

Per-UAV estimate of current goodput to the ground, so the P3 scheduler can pick a quality rung.

- Topic: `/<uav>/meshmap/goodput` — fields: `stamp`, `goodput_mbps` (EWMA), `hops_to_ground`, `rtt_ms`.
- Rate: 1 Hz. Local to the UAV; does not cross the mesh.
- Fallback if absent: P3 estimates goodput from its own send rate.

## I3 — Mission plan (P2 → flight ops, P3)

- Per UAV: a PX4 mission (MAVROS `/mavros/mission/push`, or QGC `.plan` for manual upload) with `DO_SET_CAM_TRIGG_DIST`.
- Alongside it, `plan.json` with what P3 and evaluation need: `uav`, `alt_agl_m`, `trigger_dist_m`, planned capture points, planned footprints (GeoJSON), target overlaps, planner name and version.
- Conventions in [P2 mission conventions](../02-path-planning/technical.md#mission-conventions).

## I4 — Image record (P3 → all)

One record per capture, written to `runs/.../<uav>/images.jsonl` and sent (without the `sent` list) on `/<uav>/meshmap/image_meta`. Schema and example: [P3 image record](../03-forward-feed-photogrammetry/technical.md#image-record-one-per-capture). P1 uses `t_capture_gnss` vs ground receive time for per-image latency.

## I5 — Coverage holes (P3 ground → P2)

- Topic: `/gnd/meshmap/coverage_holes` — GeoJSON `FeatureCollection` of polygons where the quick-look map lacks coverage or tie points, each with `reason` (`no_images`, `low_overlap`, `weak_tiepoints`) and `priority`.
- Published after each quick-look update. P2's re-plan service subscribes and pushes mission updates (I3).

## I6 — Run metadata (all)

`run.yaml` at the root of each run folder. Every pipeline reads its own factors from it and must not assume defaults for missing keys.

```yaml
run_id: r03
date: 2027-05-20
site: <test site>
uavs: [uav1, uav2, uav3]
p1: {underlay: ibss, routing: batman-adv-iv, ogm_interval_ms: 1000, hop_penalty: 30, transport: zenoh}
p2: {planner: joint-v1, alt_agl_m: 60, overlap_front: 0.8, overlap_side: 0.7}
p3: {arm: quicklook-refine, rig: C, rungs: [thumb, quick]}
conditions: {wind_ms: 4, temp_c: 12, notes: ""}
```

## Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-10-16 | First draft of I1–I6 |
