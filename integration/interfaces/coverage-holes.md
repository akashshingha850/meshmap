# Coverage holes

[← Interfaces](README.md)

| Version | Producer | Consumers | Form |
| --- | --- | --- | --- |
| 0.1 (draft) | photogrammetry (ground) | planning | ROS 2 topic carrying GeoJSON |

Areas where the quick-look map is missing or weak. The planning re-plan service subscribes and pushes updated [mission plans](mission-plan.md).

## Format

- Topic: `/gnd/meshmap/coverage_holes`, published after each quick-look update.
- Payload: GeoJSON `FeatureCollection` of polygons. Each feature has `reason` (`no_images`, `low_overlap`, `weak_tiepoints`), `priority` (0–1) and `quicklook_version`.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-10-16 | First draft |
