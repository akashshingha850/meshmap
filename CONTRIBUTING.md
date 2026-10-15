# Contributing

Three people, three pipelines, one repo. The structure is built so that most of the time you only touch your own folder, and the few places where we depend on each other are explicit.

## Ownership

| Area | Owner | Review needed from |
| --- | --- | --- |
| `mesh/` | mesh owner | mesh owner |
| `planning/` | planning owner | planning owner |
| `photogrammetry/` | photogrammetry owner | photogrammetry owner |
| `integration/interfaces/<file>.md` | that interface's producer | producer **and** every consumer listed in the file |
| `integration/decisions/`, `integration/docs/` | all three | every pipeline the change affects |
| `README.md`, `CONTRIBUTING.md`, `.github/` | all three | at least one other person |

Owners are listed in the [README](README.md#who-owns-what). Once GitHub usernames are filled in, [.github/CODEOWNERS](.github/CODEOWNERS) requests the right reviewers automatically.

## Branches and pull requests

- `main` should always be in a working state.
- Name branches after the folder: `mesh/zenoh-qos`, `planning/ortools-mtsp`, `photogrammetry/quality-ladder`, `integration/run-metadata-v0.2`.
- Use a pull request for code and for anything in `integration/`. Text-only edits inside your own folder can go straight to `main`.
- Keep PRs to one folder where possible. If a change spans pipelines, split it, or tag every affected owner.

## Interfaces

The contracts live in [integration/interfaces/](integration/interfaces/README.md), one file per hand-off. The producer maintains the file; consumers must approve changes. Bump the version, add a change-log line, and keep the old version working until every consumer has switched. Details are in the interfaces README.

## Decisions

When a choice affects another pipeline or had real alternatives, write a short [decision record](integration/decisions/README.md) (`YYYY-MM-DD-title.md` from the template). Accepted records are never rewritten; a new record supersedes an old one.

## Status and sync

- Each owner keeps the **Status** block (now / next / blocked on) at the top of their pipeline README current, at least before the weekly sync.
- "Blocked on" is how we ask each other for things. If you're blocked on another pipeline, link the interface or issue.
- Use GitHub issues for tasks that involve more than one person; label them with the pipeline name.

## Docs

- Research content goes in your `docs/academic.md`, engineering content in `docs/technical.md`. Update both when your pipeline changes.
- Tick items in the "Technical todo" list of your `technical.md` as they are done.
- Cite sources inline with links. Mark anything not yet verified as *verify*.

## Data

- Flight and test data go under `runs/<date>/<run-id>/` (layout in [integration technical notes](integration/docs/technical.md#run-and-data-layout)). `runs/` is git-ignored; store it on the shared drive.
- Every run has a [`run.yaml`](integration/interfaces/run-metadata.md). All timestamps are UTC from GNSS-disciplined clocks.
- Never commit full-resolution images, ULogs or pcaps. Small sample files for tests go in `<pipeline>/tests/data/`.

## Commits

- Present-tense summary, prefixed with the folder: `mesh: add station-dump logger`, `integration: bump image record to 0.2`.
- Don't add AI tools as co-authors.
