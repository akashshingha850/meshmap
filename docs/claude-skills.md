# Claude skills

[← Main doc](README.md)

Claude Code skills that make Claude useful on this repo: the repeatable jobs worth writing down once, where each skill lives, and who owns it. Nothing here is built yet; this is the plan.

## How skills work (short version)

From the [Claude Code skills docs](https://code.claude.com/docs/en/skills):

- A skill is a folder with a `SKILL.md`: YAML frontmatter plus Markdown instructions, with optional supporting files (`reference.md`, `scripts/…`).
- Claude only sees each skill's `description` until the skill is needed, then loads the body; supporting files load only when referenced. So skills cost almost nothing until used, unlike `CLAUDE.md`, which is always loaded.
- Run one with `/skill-name`, or let Claude pick it from the description.
- Useful frontmatter: `description` (what it does and **when** to use it; key use case first, the listing truncates at 1,536 chars), `disable-model-invocation: true` (only a person can trigger it; use for anything with side effects), `argument-hint` / `$ARGUMENTS`, `allowed-tools`, `paths` (only auto-activate for matching files).
- Keep `SKILL.md` under ~500 lines; move detail into supporting files.

**Where they live matters for us.** Project skills in `.claude/skills/` are committed and shared. Skills in a subfolder's own `.claude/skills/` (e.g. `mesh/.claude/skills/`) load for sessions started in that folder, or the first time Claude reads a file there. That matches our owner-based layout: shared skills at the root, pipeline skills inside each pipeline folder, owned by that pipeline's owner.

## Layout

```
.claude/skills/                  shared, owned by all three
├── interface-change/
├── decision-record/
├── docs-check/                  + scripts/check_links.py
├── status-update/
├── lit-review/
└── new-run/
mesh/.claude/skills/             mesh owner
├── bench-test/
└── link-model/
planning/.claude/skills/         planning owner
├── mission-check/
└── sitl-run/
photogrammetry/.claude/skills/   photogrammetry owner
├── image-record-check/
└── accuracy-report/
```

## Shared skills

| Skill | What it does | Trigger | Why |
| --- | --- | --- | --- |
| `interface-change` | Edits a file in `integration/interfaces/`, bumps `MAJOR.MINOR` correctly, adds a change-log line, lists the producer and consumers to tag, and finds code in each pipeline that uses the changed fields | `/interface-change <file> <what>`; manual only | Interfaces are the only place we depend on each other; this enforces the [change rules](../integration/interfaces/README.md#how-it-works) every time |
| `decision-record` | Creates `integration/decisions/YYYY-MM-DD-title.md` from the template, fills context and options from the conversation, adds it to the index | `/decision-record <title>`, or when a cross-pipeline choice is made | Keeps decisions written down without extra effort |
| `docs-check` | Runs a link and anchor checker over all Markdown, checks that every doc is linked from the [main doc](README.md), that changed pipelines updated `academic.md` / `technical.md`, and that unverified claims are marked *verify* | Before a commit or PR; Claude may run it itself | Docs are most of the repo right now; broken links and stale docs creep in fast |
| `status-update` | Reads recent commits and the todo list in one pipeline folder and drafts its **Status** block (now / next / blocked on); with `all`, drafts a weekly summary of the three | `/status-update <folder or all>`; manual only | Makes the weekly sync cheap |
| `lit-review` | Finds and summarises papers for a topic, checks them against existing citations, and proposes additions to the right `academic.md` with inline links and *verify* marks; supports the novelty check | `/lit-review <topic> [pipeline]` | Research questions and novelty claims depend on staying current |
| `new-run` | Creates `runs/<date>/<run-id>/` with a `run.yaml` from the [run metadata](../integration/interfaces/run-metadata.md) contract and the per-node folders; validates an existing `run.yaml` | `/new-run <date> <run-id>`; manual only | Every run must have the same layout and complete factor settings, or joint analysis breaks |

## Pipeline skills

| Folder | Skill | What it does |
| --- | --- | --- |
| mesh | `bench-test` | Walks through the [ground test procedure](../mesh/docs/technical.md#ground-test-procedure-before-flights) step by step, generates the harness commands for the current tuning setting, and records results under `runs/` |
| mesh | `link-model` | Parses iperf3 / `batctl` / station-dump logs and builds `link_model.json` in the [link-model](../integration/interfaces/link-model.md) format |
| planning | `mission-check` | Validates a `plan.json` against the [mission plan](../integration/interfaces/mission-plan.md) contract and recomputes GSD, footprint, overlap and trigger distance from the camera model |
| planning | `sitl-run` | Starts a multi-vehicle PX4 SITL with `tc netem` links built from the current link model, and collects the logs |
| photogrammetry | `image-record-check` | Validates `images.jsonl` against the [image record](../integration/interfaces/image-record.md) contract: timestamps on the GNSS clock, pose present, no gaps in ids |
| photogrammetry | `accuracy-report` | Computes horizontal and vertical RMSE on check points and writes the metrics CSV, following [ASPRS Edition 2](https://asprs.org/?p=27154) rules (RMSE only, ≥30 check points for a product assessment) |

Each owner writes and maintains their pipeline's skills. Add more as you find yourself giving Claude the same instructions twice.

## Existing skills worth using

Already available skills that cover parts of the work, so we don't rewrite them:

| Skill | Source | Use here |
| --- | --- | --- |
| `skill-creator` | [anthropics/skills](https://github.com/anthropics/skills) | Writing and testing the skills above |
| `pdf`, `docx`, `pptx` | [anthropics/skills](https://github.com/anthropics/skills) (`document-skills` plugin) | Reading papers, conference templates, slides for sync meetings |
| `engineering:architecture` | engineering plugin (*verify* which marketplace each of us installs it from) | Thinking through a design choice before writing the decision record |
| `engineering:testing-strategy` | engineering plugin | Test plans for the harness, planner and pipeline code |
| `data:statistical-analysis`, `data:create-viz` | data plugin (*verify*) | Network and accuracy statistics, paper figures |
| `code-review`, `simplify` | built into Claude Code | Reviewing PRs, especially interface changes |

Install the Anthropic examples in Claude Code with `/plugin marketplace add anthropics/skills`, then `/plugin install document-skills@anthropic-agent-skills` or `example-skills@anthropic-agent-skills` ([repo README](https://github.com/anthropics/skills)). Only install community skills after reading them; they run with your permissions.

## Rules for our skills

1. **One job per skill**, with a `description` that starts with what it does and says when to use it ("Use when …").
2. **`disable-model-invocation: true`** for anything that creates runs, changes interfaces or touches hardware. Claude can suggest them; a person starts them.
3. **No git side effects.** Skills edit files only; people commit and push (see [CLAUDE.md](../CLAUDE.md)).
4. **Point to docs, don't copy them.** A skill links to the interface file or `technical.md` section it relies on, so there is one source of truth.
5. **Scripts over prose** for checks that must be exact (link checks, schema validation, RMSE): put them in the skill's `scripts/` and have the skill run them.
6. **Ownership follows the folder:** shared skills need review like other shared files; pipeline skills are reviewed by their owner. Add `/.claude/` to the shared section of [CODEOWNERS](../.github/CODEOWNERS) when you fill it in.
7. **Test before relying on it:** check that it triggers from a normal request and produces the right files.

## Suggested order

1. `docs-check` (useful today: docs are most of the repo).
2. `interface-change` and `decision-record` (protect the shared parts).
3. `status-update` (before the first weekly sync).
4. `new-run`, then the pipeline skills as each pipeline starts producing data.
