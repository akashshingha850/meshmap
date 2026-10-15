# Split the repo by owner, with a shared integration folder

- **Date:** 2026-10-16
- **Status:** proposed
- **Decided by:** *all three, to confirm*
- **Affects:** mesh, planning, photogrammetry, integration

## Context

Three people each own one pipeline, and the pipelines meet only at a few data hand-offs. The first layout put all docs in a numbered `docs/` tree and planned separate top-level `common/` and `analysis/` folders. With that layout, one person's work is spread over several places, and every change risks touching folders someone else is editing.

## Options considered

1. **Split by file type** (`docs/`, `src/`, `analysis/` at the top): familiar, but ownership cuts across every folder and reviews always involve everyone.
2. **Separate repo per pipeline:** clean ownership, but joint evaluation, shared conventions and cross-links get harder, and three repos must be kept in sync.
3. **One repo, split by owner:** each pipeline folder holds its own docs and code; one shared `integration/` folder holds the contracts, decisions and joint docs. Similar to Spotify's "docs like code" layout, where docs sit next to the code their owners maintain ([Spotify Engineering](https://engineering.atspotify.com/2019/10/solving-documentation-for-monoliths-and-monorepos)).

## Decision

Option 3. Top-level folders `mesh/`, `planning/`, `photogrammetry/` and `integration/`, without number prefixes. No separate `analysis/` folders. Integration holds the [interfaces](../interfaces/README.md) (one file per contract, producer-owned, consumer-approved), these decision records and the joint docs. The root README is the one main doc and links to every inner doc.

## Consequences

- Most PRs touch one folder and need only that owner's review; CODEOWNERS can enforce it.
- Cross-pipeline work is visible in one place, `integration/`.
- Shared code (ROS messages, schemas) lives next to its interface file instead of in a general `common/` folder. If real shared libraries appear later, revisit this.
