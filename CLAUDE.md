# CLAUDE.md

## Project

MeshMap: mesh-fed forward-feed photogrammetry with a UAV swarm (BATMAN-adv mesh, path planning, swarm photogrammetry). See [docs/README.md](docs/README.md).

## Team and repo layout

- Three people, one pipeline each. Code folders: `mesh/` (P1), `planning/` (P2), `photogrammetry/` (P3); shared: `common/`, `analysis/`. Owners in [README.md](README.md); rules in [CONTRIBUTING.md](CONTRIBUTING.md).
- Contracts between pipelines live in `docs/04-cross-pipeline/interfaces.md`. Changing one means bumping its version and updating producer and consumers together.
- `runs/` holds flight data and is git-ignored.

## Docs layout

- All project documentation lives in `docs/`, one subfolder per pipeline (`01-mesh-networking/`, `02-path-planning/`, `03-forward-feed-photogrammetry/`, `04-cross-pipeline/`).
- Each subfolder has `README.md` (index), `academic.md` (state of the art, gaps, RQs, evaluation, contributions, venues) and `technical.md` (architecture, hardware, software, configs, procedures, technical todo). Keep both academic and technical content up to date when changing a pipeline.
- Cite sources inline with links; mark anything not verified as *verify* / unverified.

## Git

- Do not add Claude (or any AI) as a co-author. No `Co-Authored-By: Claude ...` trailer in commit messages and no "Generated with Claude Code" line in PR descriptions.
- Keep project files in this repo and push changes to GitHub (`origin`, branch `main`) when work is done.
