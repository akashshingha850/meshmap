# planning/ — P2 Path planning

**Owner:** *TBD* · **Docs:** [academic](../docs/02-path-planning/academic.md) · [technical](../docs/02-path-planning/technical.md)

Camera/footprint model, multi-UAV coverage + connectivity planner, SITL and network emulation.

**Produces:** I3 mission plans ([interfaces](../docs/04-cross-pipeline/interfaces.md)).
**Consumes:** I1 link-capacity model, I5 coverage holes, I6 `run.yaml`.

## Planned layout

```
planning/
├── camera/       # intrinsics → GSD, footprint, oblique footprint
├── planners/     # lawnmower, double-grid, joint coverage + goodput (OR-Tools mTSP)
├── replan/       # online re-plan service (I5 in, I3 out)
├── sim/          # multi-vehicle PX4 SITL + Gazebo launch, tc-netem driven by I1
└── tests/
```

Todo list: [P2 technical todo](../docs/02-path-planning/technical.md#technical-todo).
