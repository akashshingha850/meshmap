# Integration

[← Main doc](../docs/README.md) · **Owner:** all three. Changes here need review from every pipeline they affect.

Everything that ties the three pipelines into one project: the contracts between them, the decisions that affect more than one of them, the shared system and field campaigns, and the joint evaluation that the papers are built on.

| | Contents |
| --- | --- |
| [interfaces/](interfaces/README.md) | One file per data hand-off between pipelines, with format, producer, consumers and version |
| [decisions/](decisions/README.md) | Dated decision records for choices that affect more than one pipeline |
| [docs/academic.md](docs/academic.md) | Positioning against neighbouring fields, contributions C1–C7, venues, joint evaluation, novelty check |
| [docs/technical.md](docs/technical.md) | System architecture, bill of materials, run and data layout, timeline, risks |

## Thesis

The Pi camera rig and the mesh are the testbed. The research contribution is a forward-feed architecture that adapts to the available bandwidth and to the mesh, plus a joint evaluation that reports network metrics and GCP accuracy from the same flights. No paper in the review does both on a multi-hop mesh.

All three pipelines share one flight dataset, so one campaign can support three papers: networking, accuracy and methods.
