# Image record

[← Interfaces](README.md)

| Version | Producer | Consumers | Form |
| --- | --- | --- | --- |
| 0.1 (draft) | photogrammetry | mesh, integration | `images.jsonl` + `/<uav>/meshmap/image_meta` |

One record per capture. The full record is written to `runs/<date>/<run>/<uav>/images.jsonl`. The same record without the `sent` list is published on `/<uav>/meshmap/image_meta`. Mesh uses `t_capture_gnss` against the ground receive time to measure per-image latency.

## Format

```json
{
  "id": "uav1-cam0-000123",
  "uav": "uav1", "cam": 0,
  "t_capture_gnss": "2027-05-20T10:31:12.481203Z",
  "lat": 65.0593, "lon": 25.4663, "alt_amsl": 92.4,
  "roll": 0.8, "pitch": -1.2, "yaw": 87.5,
  "pos_std_m": 1.5,
  "keyframe_score": 0.73,
  "sent": [{"rung": "thumb", "bytes": 48211, "t_send": "...", "t_recv": "...", "hops": 2}],
  "file_fullres": "runs/2027-05-20/r03/uav1/cam0/000123.jpg"
}
```

- `t_capture_gnss` is the libcamera sensor timestamp on the GNSS-disciplined clock, never the file-write or ground-receive time.
- Pose fields are interpolated from MAVROS to `t_capture_gnss` (see [photogrammetry geotagging](../../photogrammetry/docs/technical.md#capture-and-geotagging)).

## Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-10-16 | Moved here from the photogrammetry technical notes |
