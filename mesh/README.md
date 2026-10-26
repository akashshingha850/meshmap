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
| [bringup/](bringup/README.md) | BATMAN-adv node setup: readiness check, `mesh-up`/`mesh-down`, installer, systemd unit, shared `mesh.conf` |
| [harness/adhoc-range/](harness/adhoc-range/README.md) | Two-Pi ad-hoc link range test: iw/iperf3/ping collector, path loss fit, usable range, link budget |
| [docs/technical.md](docs/technical.md) | Network architecture, hardware, BATMAN-adv bring-up and tuning, ROS 2 transports, time sync, measurement harness, test procedure |

Planned code folders, added as work starts:

```
bringup/      # done: scripts, systemd unit; Ansible role to come
transport/    # zenoh-bridge config + QoS, CycloneDDS XML, Discovery Server launch
timesync/     # gpsd + PPS + chrony configs
harness/      # adhoc-range/ (done, untested on hardware); probe, route logger, tcpdump rotation to come
model/        # builds link_model.json from harness logs
tests/        # shared tests; adhoc-range keeps its own in harness/adhoc-range/tests
```
