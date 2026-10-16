# Image record

[← Interfaces](README.md)

| Version | Producer | Consumers | Form |
| --- | --- | --- | --- |
| 0.2 (draft) | photogrammetry | mesh, integration | `images.jsonl` + `/<uav>/meshmap/image_meta` |

One record per capture. The full record is written to `runs/<date>/<run>/<uav>/images.jsonl`. The same record without the `sent` list is published on `/<uav>/meshmap/image_meta`. Mesh uses `t_capture_gnss` against the ground receive time to measure per-image latency.

## Format

```json
{
  "id": "uav1-cam0-000123",
  "uav": "uav1", "cam": 0,
  "trigger_seq": 123,
  "t_trigger_cmd": "2027-05-20T10:31:12.402110Z",
  "t_capture_gnss": "2027-05-20T10:31:12.481203Z",
  "t_source": "cmd+latency",
  "latency_ms": 79.1, "latency_jitter_ms": 12.0,
  "lat": 65.0593, "lon": 25.4663, "alt_amsl": 92.4,
  "roll": 0.8, "pitch": -1.2, "yaw": 87.5,
  "gimbal_pitch": -90.0, "gimbal_yaw": 0.0, "gimbal_roll": 0.0,
  "pos_std_m": 1.5,
  "keyframe_score": 0.73,
  "sent": [{"rung": "thumb", "bytes": 48211, "t_send": "...", "t_recv": "...", "hops": 2}],
  "file_fullres": "runs/2027-05-20/r03/uav1/cam0/000123.jpg"
}
```

- `cam` stays an integer so more cameras can be added later. With one SIYI A8 mini per UAV it is always `0`.
- `trigger_seq` is the PX4 `CAMERA_TRIGGER` sequence number. `t_trigger_cmd` is when the Pi sent the SDK take-picture command, on the GNSS-disciplined clock.
- `t_capture_gnss` is the estimated exposure time: `t_trigger_cmd + latency_ms`, with `t_source` = `cmd+latency`. It is never the file-write, download or ground-receive time. `latency_ms` and `latency_jitter_ms` come from the latest bench calibration ([P3 capture](../../photogrammetry/docs/technical.md#capture-and-geotagging)). If a camera with sensor timestamps is added later, use `t_source` = `sensor`.
- `roll`, `pitch`, `yaw` are the vehicle attitude from MAVROS. `gimbal_*` are the camera angles from SIYI SDK `0x0D`, in the frame the gimbal reports (*verify* earth or body). All are interpolated to `t_capture_gnss`.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-10-16 | Moved here from the photogrammetry technical notes |
| 0.2 | 2026-10-16 | SIYI A8 mini ([decision](../decisions/2026-10-16-uav-hardware-a8mini-pi5-pixracer.md)): added `trigger_seq`, `t_trigger_cmd`, `t_source`, `latency_ms`, `latency_jitter_ms`, `gimbal_*`; `t_capture_gnss` is now estimated, not a sensor timestamp |
