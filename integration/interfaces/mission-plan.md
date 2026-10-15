# Mission plan

[← Interfaces](README.md)

| Version | Producer | Consumers | Form |
| --- | --- | --- | --- |
| 0.1 (draft) | planning | photogrammetry, flight ops | PX4 mission + `plan.json` |

## Format

- **PX4 mission** per UAV: pushed through MAVROS `/mavros/mission/push`, or as a QGroundControl `.plan` for manual upload. Includes `DO_SET_CAM_TRIGG_DIST`.
- **`plan.json`** per UAV, with what photogrammetry and evaluation need:

```json
{
  "version": "0.1",
  "uav": "uav1",
  "planner": "joint", "planner_version": "0.3.0",
  "alt_agl_m": 60, "trigger_dist_m": 12.5,
  "overlap_front": 0.8, "overlap_side": 0.7,
  "capture_points": [[25.4663, 65.0593], "..."],
  "footprints": {"type": "FeatureCollection", "features": []}
}
```

Mission rules (altitude layers, turn-arounds outside the area of interest, distance triggering) are in [planning mission conventions](../../planning/docs/technical.md#mission-conventions).

## Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-10-16 | First draft |
