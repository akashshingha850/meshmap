# Contributing

Three people, three pipelines, one repo. These rules keep us out of each other's way.

## Ownership

| Area | Owner | Who must review |
| --- | --- | --- |
| `mesh/`, `docs/01-mesh-networking/` | P1 owner | P1 owner (others optional) |
| `planning/`, `docs/02-path-planning/` | P2 owner | P2 owner (others optional) |
| `photogrammetry/`, `docs/03-forward-feed-photogrammetry/` | P3 owner | P3 owner (others optional) |
| `common/`, `docs/04-cross-pipeline/`, `analysis/` | shared | every pipeline the change affects |
| `README.md`, `CONTRIBUTING.md`, `.github/` | shared | at least one other person |

Owners are listed in the [README](README.md#pipelines-and-owners) and enforced through [.github/CODEOWNERS](.github/CODEOWNERS).

## Branches and pull requests

- `main` is always in a working state. Don't push broken code to it.
- Branch names start with the pipeline: `p1/zenoh-qos`, `p2/ortools-mtsp`, `p3/quality-ladder`, `common/run-schema`, `docs/...`.
- Open a pull request for any code change and any change to shared areas. Small typo or wording fixes in your own docs folder can go straight to `main`.
- Keep PRs small and focused on one pipeline where possible. If a change spans pipelines, say so in the PR description and tag both owners.

## Changing an interface

The contracts between pipelines live in [docs/04-cross-pipeline/interfaces.md](docs/04-cross-pipeline/interfaces.md) and, once they exist, as schemas in [common/](common/).

1. Open an issue or PR describing the change and why.
2. Bump the interface version in `interfaces.md`.
3. Get approval from the producer **and** every consumer of that interface.
4. Update the producer and consumers in the same PR, or keep the old version working until they are updated.

## Docs

- When you change how your pipeline works, update both `academic.md` and `technical.md` in your docs folder if they are affected.
- Tick items in the "Technical todo" list of your `technical.md` as they are done.
- Cite sources inline with links. Mark anything not yet verified as *verify*.

## Data

- Flight and test data go under `runs/<date>/<run-id>/` (layout in [cross-pipeline technical](docs/04-cross-pipeline/technical.md#run-and-data-layout)). `runs/` is git-ignored; store it on the shared drive.
- Every run has a `run.yaml` with its factor settings. All timestamps are UTC from GNSS-disciplined clocks.
- Never commit full-resolution images, ULogs or pcaps. Small sample files for tests go in `<pipeline>/tests/data/`.

## Commits

- Present-tense summary, optionally prefixed with the area: `p1: add station-dump logger`, `common: add run.yaml schema`.
- Don't add AI tools as co-authors.
