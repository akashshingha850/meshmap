# Mesh networking (P1)

[← Main doc](../docs/README.md) · **Owner:** *TBD*

How much imagery and telemetry can a flying multi-hop BATMAN-adv mesh carry, and how fast does it recover when links break? This pipeline tunes the mesh and the ROS 2 transport, measures them on the bench, on the ground and in flight, and turns the results into a link-capacity model the other pipelines use.

| Gives to others | Takes from others |
| --- | --- |
| [Link-capacity model](../integration/interfaces/link-model.md) → planning, photogrammetry | [Image record](../integration/interfaces/image-record.md) (for per-image latency) |
| [Live goodput](../integration/interfaces/goodput.md) → photogrammetry | [Run metadata](../integration/interfaces/run-metadata.md) |

## Status

- **Now:** *(owner updates this weekly)*
- **Next:**
- **Blocked on:**

Full task list: [technical todo](docs/technical.md#technical-todo).

## Contents

| Path | Contents |
| --- | --- |
| [docs/academic.md](docs/academic.md) | State of the art, gaps, research questions and hypotheses, evaluation design, contributions (C3, C5), venues |
| [docs/technical.md](docs/technical.md) | Network architecture, hardware, BATMAN-adv bring-up and tuning, ROS 2 transports, time sync, measurement harness, test procedure |

Planned code folders, added as work starts:

```
bringup/      # mesh-up.sh, systemd units, Ansible role for all nodes
transport/    # zenoh-bridge config + QoS, CycloneDDS XML, Discovery Server launch
timesync/     # gpsd + PPS + chrony configs
harness/      # probe, route logger, station dump, tcpdump rotation
model/        # builds link_model.json from harness logs
tests/
```
