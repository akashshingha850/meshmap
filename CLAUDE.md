# CLAUDE.md

## Project

MeshMap (Multi-hop Edge Swarm for Hybrid Mapping And Photogrammetry): mesh-fed forward-feed photogrammetry with a UAV swarm (BATMAN-adv mesh, path planning, swarm photogrammetry). [docs/README.md](docs/README.md) is the main doc: it links to every inner doc, so add new docs to its documentation map. Keep the root README.md minimal (title, owners, layout).

## Repo layout

- Split by owner, no numbered folders. Three people, one pipeline each: `mesh/` (P1), `planning/` (P2), `photogrammetry/` (P3). Shared work in `integration/`. Rules in [CONTRIBUTING.md](CONTRIBUTING.md).
- Every pipeline folder has the same shape: `README.md` (status, inputs/outputs, contents), `docs/academic.md` (state of the art, gaps, RQs, evaluation, contributions, venues), `docs/technical.md` (architecture, hardware, software, configs, procedures, technical todo), and code folders as work starts. No `analysis/` folders. Keep academic and technical docs up to date when changing a pipeline.
- `integration/interfaces/` has one file per hand-off between pipelines. Changing one means bumping its version, adding a change-log line, and updating producer and consumers together.
- `integration/decisions/` holds dated decision records (`YYYY-MM-DD-title.md`, from `template.md`); add one for choices that affect more than one pipeline.
- `runs/` holds flight data and is git-ignored.
- Cite sources inline with links; mark anything not verified as *verify* / unverified.

## Git

- Do not commit or push. The user reviews, commits and pushes manually.
- Do not add Claude (or any AI) as a co-author anywhere.
