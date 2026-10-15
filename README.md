# MeshMap

***M**ulti-hop **E**dge **S**warm for **H**ybrid **M**apping **A**nd **P**hotogrammetry*

**Live photogrammetric mapping from a UAV swarm whose only link is a multi-hop BATMAN-adv mesh.**

📖 **Start here: [docs/](docs/README.md)** for the overview, research questions and links to every doc.

## Who owns what

| Folder | Pipeline | Owner |
| --- | --- | --- |
| [mesh/](mesh/README.md) | Mesh networking (P1) | *TBD* |
| [planning/](planning/README.md) | Path planning (P2) | *TBD* |
| [photogrammetry/](photogrammetry/README.md) | Forward-feed photogrammetry (P3) | *TBD* |
| [integration/](integration/README.md) | Interfaces, decisions, joint evaluation | all three |

## Repository layout

```
meshmap/
├── docs/                   main doc (overview + links to every inner doc), skills
├── mesh/                   ┐
├── planning/               │ one per owner, same shape:
├── photogrammetry/         ┘   README.md  status, inputs/outputs
│                               docs/      academic.md, technical.md
│                               <code>/    added as work starts
├── integration/            shared: interfaces/, decisions/, docs/
├── CONTRIBUTING.md         how we work together
└── runs/                   flight and test data (git-ignored)
```

Why this shape: [decision record](integration/decisions/2026-10-16-split-repo-by-owner.md). How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).
