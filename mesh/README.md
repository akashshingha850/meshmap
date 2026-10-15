# mesh/ — P1 Mesh networking

**Owner:** *TBD* · **Docs:** [academic](../docs/01-mesh-networking/academic.md) · [technical](../docs/01-mesh-networking/technical.md)

BATMAN-adv mesh bring-up, ROS 2 transport configuration and the measurement harness.

**Produces:** I1 link-capacity model, I2 live goodput topic ([interfaces](../docs/04-cross-pipeline/interfaces.md)).
**Consumes:** I4 image records (for per-image latency), I6 `run.yaml`.

## Planned layout

```
mesh/
├── bringup/      # mesh-up.sh, systemd units, Ansible role for all nodes
├── transport/    # zenoh-bridge config + QoS, CycloneDDS XML, Discovery Server launch
├── timesync/     # gpsd + PPS + chrony configs
├── harness/      # probe, route logger, station dump, tcpdump rotation
├── model/        # scripts that build link_model.json from harness logs
└── tests/
```

Todo list: [P1 technical todo](../docs/01-mesh-networking/technical.md#technical-todo).
