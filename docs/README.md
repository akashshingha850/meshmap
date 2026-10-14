# MeshMap docs — Mesh-Fed Swarm Photogrammetry

Project outline, as of 2026-10-15.

MeshMap tests how good a photogrammetric map a UAV swarm can deliver live when its only link is a multi-hop BATMAN-adv mesh carrying 0.3–10 Mbit/s. The work is split into three pipelines. They share one testbed and one set of flights. Each UAV carries three Raspberry Pi cameras (one nadir, two oblique). It streams image topics and MAVROS telemetry over the mesh to a local ground server with no internet.

## Structure

Each pipeline folder has a `README.md` index, an `academic.md` (state of the art, gaps, research questions, evaluation, contributions) and a `technical.md` (architecture, hardware, software, configuration, procedures).

```
docs/
├── README.md                          # this file: overview + research questions
├── 01-mesh-networking/                # P1
├── 02-path-planning/                  # P2
├── 03-forward-feed-photogrammetry/    # P3
└── 04-cross-pipeline/                 # joint evaluation, venues, architecture, timeline, risks
```

| Pipeline | Question it answers | Primary output | Academic | Technical |
| --- | --- | --- | --- | --- |
| [P1 Mesh networking (BATMAN-adv)](01-mesh-networking/README.md) | How much imagery and telemetry can a flying multi-hop mesh carry, and how fast does it recover? | Link-capacity model + tuned mesh and ROS 2 transport | [academic](01-mesh-networking/academic.md) | [technical](01-mesh-networking/technical.md) |
| [P2 Path planning for photogrammetry](02-path-planning/README.md) | Where should each UAV fly and shoot so the map is complete and the mesh stays connected? | Multi-UAV planner that handles both coverage and connectivity | [academic](02-path-planning/academic.md) | [technical](02-path-planning/technical.md) |
| [P3 Forward-feed swarm photogrammetry](03-forward-feed-photogrammetry/README.md) | What map quality is reachable live, per Mbit/s, and how much does refinement add? | Quick-look map + refined model, scored on GCPs | [academic](03-forward-feed-photogrammetry/academic.md) | [technical](03-forward-feed-photogrammetry/technical.md) |
| [Cross-pipeline](04-cross-pipeline/README.md) | How do the pipelines combine into papers and a schedule? | Joint evaluation, venues, timeline | [academic](04-cross-pipeline/academic.md) | [technical](04-cross-pipeline/technical.md) |

How the pipelines feed each other:

- **P1 → P2:** the link-capacity model becomes the planner's goodput cost.
- **P1 → P3:** the measured goodput sets the scheduler's bandwidth budget.
- **P2 → P3:** the planned paths determine the image set.
- **P3 → P2:** coverage holes in the quick-look map trigger online re-planning.

## Thesis

The Pi camera rig and the mesh are the testbed. The research contribution is a forward-feed architecture that adapts to available bandwidth and to the mesh. It also includes a joint evaluation that reports network metrics and GCP accuracy from the same flights. No paper in the review does both on a multi-hop mesh.

## Research questions

1. **RQ1 (P1):** How do tuned BATMAN-adv and the ROS 2 transports behave in flight over 1–3+ hops with real image payloads? Tuning covers IV vs V, the OGM interval and the hop penalty. Transports are Zenoh vs tuned DDS.
2. **RQ2 (P2):** Can a single planner optimise photogrammetric coverage, oblique view geometry and mesh goodput together? Compared with a lawnmower baseline, it should cut flight time and relay outages without losing accuracy.
3. **RQ3 (P3):** How does map accuracy trade off against delivered bytes? Accuracy is RMSE on held-out RTK check points. The comparison is a quick-look-then-refine scheme against send-all and offline baselines.
4. **RQ4 (cross-cutting):** How much accuracy is lost per millisecond of capture-timestamp error and per hop of mesh latency?
