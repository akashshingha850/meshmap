# Forward-feed photogrammetry (P3)

[← Main doc](../README.md) · **Owner:** *TBD*

What map quality can the swarm deliver live, per Mbit/s sent over the mesh, and how much does refinement after landing add? This pipeline captures and geotags images onboard, schedules what to send at which quality given the available goodput, builds a quick-look map on the ground, refines it after landing, and scores both on ground control points.

| Gives to others | Takes from others |
| --- | --- |
| [Image record](../integration/interfaces/image-record.md) → mesh, integration | [Live goodput](../integration/interfaces/goodput.md) and [link-capacity model](../integration/interfaces/link-model.md) from mesh |
| [Coverage holes](../integration/interfaces/coverage-holes.md) → planning | [Mission plan](../integration/interfaces/mission-plan.md) from planning |
| | [Run metadata](../integration/interfaces/run-metadata.md) |

## Status

- **Now:** *(owner updates this weekly)*
- **Next:**
- **Blocked on:**

Full task list: [technical todo](docs/technical.md#technical-todo).

## Contents

| Path | Contents |
| --- | --- |
| [docs/academic.md](docs/academic.md) | State of the art, gaps, research questions and hypotheses, three-arm evaluation, contributions (C1, C2, C4, C6) |
| [docs/technical.md](docs/technical.md) | Data flow, camera rig options, geotagging, scheduler and quality ladder, ground processing, field setup |

Planned code folders, added as work starts:

```
capture/      # onboard capture node: libcamera, GNSS/PPS timestamps, pose prior
scheduler/    # keyframe score, quality ladder, reachback
ground/       # ingest, quick-look map, coverage-hole detection, refinement
eval/         # GCP / check-point RMSE, completeness
tests/
```
