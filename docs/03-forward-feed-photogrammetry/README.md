# P3 — Forward-feed swarm photogrammetry

[← Docs index](../README.md)

Pipeline 3 asks how good a map can be produced live, per Mbit/s sent over the mesh, and how much refinement after landing adds. Its main output is a quick-look map plus a refined model, both scored on ground control points. It uses P1's bandwidth budget and the images captured on P2's planned paths.

| File | Contents |
| --- | --- |
| [academic.md](academic.md) | State of the art, gaps, research questions and hypotheses, three-arm evaluation, contributions (C1, C2, C4, C6) |
| [technical.md](technical.md) | Data flow, camera rig options, geotagging, image record schema, scheduler and quality ladder, ground processing, field setup |
