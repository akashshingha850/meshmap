# analysis/ — Joint evaluation and figures

**Owner:** shared.

Scripts and notebooks that read `runs/` and produce the paper figures and tables, especially the joint network + accuracy results (RQ4). Evaluation design: [cross-pipeline academic](../docs/04-cross-pipeline/academic.md).

Conventions:

- One script or notebook per figure/table, named after it (`fig_rmse_vs_bytes.py`).
- Read data only through `common/runlog`; never hard-code run paths.
- Clear notebook outputs before committing.
