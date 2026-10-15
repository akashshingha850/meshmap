# Link-capacity model

[← Interfaces](README.md)

| Version | Producer | Consumers | Form |
| --- | --- | --- | --- |
| 0.1 (draft) | mesh | planning, photogrammetry | `link_model.json` |

Measured goodput as a function of hops, distance and altitude, built from the mesh measurement harness after each test campaign. Planning turns it into a goodput cost raster and uses it to drive `tc netem` in SITL. Photogrammetry uses it as the prior bandwidth budget before live goodput is available.

## Format

```json
{
  "version": "0.1",
  "measured": "2026-12-10",
  "underlay": "ibss", "routing": "batman-adv-iv", "transport": "zenoh",
  "entries": [
    {"hops": 1, "distance_m": 50, "alt_agl_m": 30,
     "goodput_mbps_p50": 8.2, "goodput_mbps_p10": 5.1,
     "latency_ms_p50": 12, "loss": 0.01}
  ]
}
```

- One file per (underlay, routing, transport) setting.
- `p10` is there so planners can be conservative; consumers state in their docs which percentile they use.
- Stored with the campaign data under `runs/`; the latest accepted model is copied to `mesh/model/link_model.json` so others can use it without the data drive.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-10-16 | First draft |
