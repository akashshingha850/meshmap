# Run metadata

[← Interfaces](README.md)

| Version | Producer | Consumers | Form |
| --- | --- | --- | --- |
| 0.2 (draft) | all (each pipeline owns its own block) | all | `run.yaml` |

`run.yaml` sits at the root of every run folder (`runs/<date>/<run-id>/`). Each pipeline owns its own block and can add keys to it with a minor version bump. Top-level keys are shared. Code must not assume defaults for missing keys.

## Format

```yaml
version: "0.2"
run_id: r03
date: 2027-05-20
site: <test site>
uavs: [uav1, uav2, uav3]
hardware:       {fc: pixracer-fmuv4, px4: v1.17.0, companion: rpi5-8gb, camera: siyi-a8-mini, camera_fw: "<x.y.z>"}
mesh:           {underlay: ibss, routing: batman-adv-iv, ogm_interval_ms: 1000, hop_penalty: 30, transport: zenoh}
planning:       {planner: joint, alt_agl_m: 60, overlap_front: 0.8, overlap_side: 0.7}
photogrammetry: {arm: quicklook-refine, oblique: none, gimbal_pitch_deg: -90, latency_cal: 2027-05-18, rungs: [thumb, quick]}
conditions:     {wind_ms: 4, temp_c: 12, notes: ""}
```

## Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-10-16 | First draft; blocks named after pipeline folders |
| 0.2 | 2026-10-16 | Added shared `hardware` block; `photogrammetry.rig` replaced by `oblique` (`none`, `passes`, `sweep`), `gimbal_pitch_deg` and `latency_cal` (date of the latency calibration used) |
