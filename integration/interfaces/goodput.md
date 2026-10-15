# Live goodput

[← Interfaces](README.md)

| Version | Producer | Consumers | Form |
| --- | --- | --- | --- |
| 0.1 (draft) | mesh | photogrammetry | ROS 2 topic |

Per-UAV estimate of the current goodput to the ground, so the photogrammetry scheduler can choose a quality rung.

## Format

- Topic: `/<uav>/meshmap/goodput`, 1 Hz, local to the UAV (does not cross the mesh).
- Fields: `stamp`, `goodput_mbps` (EWMA), `hops_to_ground`, `rtt_ms`.
- If the topic is missing for more than 5 s, the scheduler falls back to its own measured send rate and logs that it did.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-10-16 | First draft |
