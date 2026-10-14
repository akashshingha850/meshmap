# P2 — Path planning for photogrammetry

[← Docs index](../README.md)

Pipeline 2 asks where each UAV should fly and take pictures, so that the map is complete and the mesh stays connected. Its main output is a multi-UAV planner that combines coverage, oblique view geometry and measured goodput. It takes the link-capacity model from P1, and its image set feeds P3.

| File | Contents |
| --- | --- |
| [academic.md](academic.md) | State of the art, gaps, research questions and hypotheses, formal problem, evaluation design, contribution C7 |
| [technical.md](technical.md) | Planner architecture, GSD/footprint math, rig layout options, software stack, SITL + network emulation, mission conventions |
