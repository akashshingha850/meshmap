# Decision records

[← Integration overview](../README.md)

Short notes on design choices that affect more than one pipeline, or that we will want to explain in a paper later ("why Zenoh and not DDS?"). The format follows Michael Nygard's architecture decision records ([adr.github.io](https://adr.github.io/)): context, decision, consequences.

## Rules

- **When:** a choice affects another pipeline, changes an [interface](../interfaces/README.md), or had real alternatives. Choices inside your own pipeline can go in your own `docs/technical.md` instead.
- **File name:** `YYYY-MM-DD-short-title.md`, copied from [template.md](template.md). Dates instead of sequence numbers, so two people writing records on separate branches never collide.
- **Status:** `proposed` → `accepted` (merged after review by the affected owners), later possibly `superseded by <file>`. Never delete or rewrite an accepted record; write a new one that supersedes it.

## Index

| Date | Decision | Status |
| --- | --- | --- |
| 2026-10-16 | [Split the repo by owner, with a shared integration folder](2026-10-16-split-repo-by-owner.md) | proposed |
| 2026-10-16 | [UAV hardware: SIYI A8 mini, Raspberry Pi 5, Pixracer with PX4 + MAVROS](2026-10-16-uav-hardware-a8mini-pi5-pixracer.md) | proposed |
