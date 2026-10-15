# Path planning (P2)

[← Main doc](../docs/README.md) · **Owner:** *TBD*

Where should each UAV fly and take pictures so the map is complete and the mesh stays connected? This pipeline builds a multi-UAV planner that combines photogrammetric coverage, oblique view geometry and measured mesh goodput, tests it in SITL with emulated links, and re-plans online when the quick-look map shows holes.

| Gives to others | Takes from others |
| --- | --- |
| [Mission plan](../integration/interfaces/mission-plan.md) → photogrammetry, flight ops | [Link-capacity model](../integration/interfaces/link-model.md) from mesh |
| | [Coverage holes](../integration/interfaces/coverage-holes.md) from photogrammetry |
| | [Run metadata](../integration/interfaces/run-metadata.md) |

## Status

- **Now:** *(owner updates this weekly)*
- **Next:**
- **Blocked on:**

Full task list: [technical todo](docs/technical.md#technical-todo).

## Contents

| Path | Contents |
| --- | --- |
| [docs/academic.md](docs/academic.md) | State of the art, gaps, research questions and hypotheses, formal problem, evaluation design, contribution C7 |
| [docs/technical.md](docs/technical.md) | Planner architecture, GSD/footprint maths, rig layout options, software stack, SITL + network emulation, mission conventions |

Planned code folders, added as work starts:

```
camera/       # intrinsics → GSD, footprint, oblique footprint
planners/     # lawnmower, double-grid, joint coverage + goodput (OR-Tools mTSP)
replan/       # online re-plan service: coverage holes in, mission plans out
sim/          # multi-vehicle PX4 SITL + Gazebo, tc-netem driven by the link model
tests/
```
