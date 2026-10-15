# common/ — Shared code and schemas

**Owner:** shared — changes need approval from every pipeline they affect ([CONTRIBUTING](../CONTRIBUTING.md#changing-an-interface)).

Code and definitions more than one pipeline depends on. The human-readable contracts are in [interfaces.md](../docs/04-cross-pipeline/interfaces.md); this folder holds their machine-readable form.

## Planned layout

```
common/
├── schemas/      # JSON Schema: link_model (I1), plan (I3), image record (I4), run.yaml (I6)
├── msgs/         # ROS 2 message package: Goodput (I2), ImageMeta (I4), CoverageHoles (I5)
└── runlog/       # helpers to create run folders, read run.yaml, write GNSS-stamped logs
```

Keep this folder small. If only one pipeline uses something, it belongs in that pipeline's folder.
