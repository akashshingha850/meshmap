# UAV hardware: SIYI A8 mini, Raspberry Pi 5, Pixracer with PX4 + MAVROS

- **Date:** 2026-10-16
- **Status:** proposed
- **Decided by:** Akash Shingha; *other owners to confirm*
- **Affects:** mesh, planning, photogrammetry, integration

## Context

The first outline assumed three Raspberry Pi cameras per UAV (one nadir, two oblique), a Pi 5 companion and a Pixhawk-class PX4 flight controller. A Pi 5 has only two CSI ports, so that rig needed extra boards and a synchronisation scheme (rig options A–D). The payload has now been chosen: one SIYI A8 mini gimbal camera, a Raspberry Pi 5 and a Pixracer running PX4, with MAVROS on the Pi. A Jetson was considered for the companion and dropped.

## Options considered

1. **Three Pi cameras on a Pi 5 (previous plan):** fixed nadir + oblique geometry and sensor timestamps from libcamera. But it needs extra boards or a multi-camera HAT, an inter-camera sync study, and a custom rig and mounts.
2. **SIYI A8 mini on a Pi 5 (chosen):** one 95 g, 3-axis stabilised camera with Ethernet control (SIYI SDK over UDP), RTSP video and HTTP media download. Obliques come from gimbal pitch, not fixed cameras. Captures are software-triggered and the camera exposes no sensor timestamp, so capture time has to be measured rather than read.
3. **SIYI A8 mini on a Jetson:** more onboard compute for keyframe selection, but JetPack's Ubuntu/ROS 2 versions and the L4T kernel (batman-adv module) differ from the Pi setup that P1 already documents. Dropped.

## Decision

Option 2. Each UAV carries a Pixracer (PX4, `px4_fmu-v4`), a Raspberry Pi 5 running MAVROS over TELEM2, and a SIYI A8 mini on the Pi's Ethernet port. PX4 owns the trigger distance and sends `CAMERA_TRIGGER` to the Pi; the Pi's capture node fires the A8 mini through the SIYI SDK, controls the gimbal, logs its attitude and fetches the stills. PX4 does not drive the gimbal.

## Consequences

- **Photogrammetry:** rig options A–D and the inter-camera sync study go away. In their place is a trigger-to-exposure latency study, because the A8 mini gives no sensor timestamp ([P3 technical](../../photogrammetry/docs/technical.md#capture-and-geotagging)). Contribution C4 and RQ3.3 are reframed around one gimbal camera.
- **Planning:** the camera model changes to the A8 mini (wide 81° HFOV *verify*). Obliques are planned as gimbal pitch per pass or per trigger, not as a fixed rig ([P2 technical](../../planning/docs/technical.md#camera-and-footprint-math)). RQ2.2 is reframed.
- **Mesh:** the Pi's Ethernet port is now used by the camera, and the A8 mini's RTSP video must stay off the mesh. The Pixracer build has the uXRCE-DDS client disabled, so MAVROS is the only ROS path from the FC.
- **Integration:** BOM, architecture, run layout and risks updated. The [image record](../interfaces/image-record.md) goes to v0.2 (gimbal attitude, trigger sequence, timestamp source). The [run metadata](../interfaces/run-metadata.md) goes to v0.2 (`rig` replaced by camera and gimbal fields).
- **Open, to confirm with the team:** whether one A8 mini per UAV is enough for the oblique research questions, or whether to keep a fixed oblique camera as well.
