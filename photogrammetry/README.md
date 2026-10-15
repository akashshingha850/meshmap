# photogrammetry/ — P3 Forward-feed photogrammetry

**Owner:** *TBD* · **Docs:** [academic](../docs/03-forward-feed-photogrammetry/academic.md) · [technical](../docs/03-forward-feed-photogrammetry/technical.md)

Onboard capture and bandwidth-aware scheduling, ground quick-look and refinement, accuracy evaluation.

**Produces:** I4 image records, I5 coverage holes ([interfaces](../docs/04-cross-pipeline/interfaces.md)).
**Consumes:** I2 live goodput, I3 mission plans, I6 `run.yaml`.

## Planned layout

```
photogrammetry/
├── capture/      # onboard capture node: libcamera, GNSS/PPS timestamps, pose prior
├── scheduler/    # keyframe score, quality ladder, reachback
├── ground/       # ingest, quick-look map, coverage-hole detection, refinement
├── eval/         # GCP / check-point RMSE, completeness
└── tests/
```

Todo list: [P3 technical todo](../docs/03-forward-feed-photogrammetry/technical.md#technical-todo).
