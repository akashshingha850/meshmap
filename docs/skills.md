# Skills

[← Main doc](README.md)

The skills this project needs, who needs them and how deeply, and where to learn them. Everyone needs the shared foundation. Each owner then goes deep in their own pipeline, and knows enough of the neighbouring pipelines to work with their [interfaces](../integration/interfaces/README.md).

Resources are official docs where possible. Versions match the project's target stack: Raspberry Pi OS (Bookworm), ROS 2 Jazzy, PX4. Anything not yet checked against our hardware or current regulation is marked *verify*.

## Skills matrix

**●●●** deep (you build and own it) · **●●** working (you can use, debug and review it) · **●** awareness (you know what it does and where it fits)

| Skill | mesh | planning | photogrammetry |
| --- | :-: | :-: | :-: |
| Linux, shell and Raspberry Pi admin | ●●● | ●● | ●●● |
| Git and GitHub collaboration | ●● | ●● | ●● |
| Python | ●● | ●●● | ●●● |
| ROS 2 (nodes, topics, QoS, launch, bags) | ●●● | ●● | ●●● |
| PX4, MAVLink and MAVROS | ●● | ●●● | ●● |
| UAV field operations and regulation | ●● | ●● | ●● |
| GNSS, PPS and time sync (chrony) | ●●● | ● | ●● |
| Wireless networking (802.11, IBSS, 802.11s) | ●●● | ● | ● |
| Mesh routing (BATMAN-adv, Babel) | ●●● | ●● | ● |
| ROS 2 middleware (Zenoh, DDS) | ●●● | ● | ●● |
| Network measurement (iperf3, tcpdump) and emulation (tc netem) | ●●● | ●● | ● |
| Fleet configuration (Ansible, systemd) | ●●● | ● | ●● |
| Geometry and geodesy (UTM, pyproj, Shapely) | ● | ●●● | ●● |
| Combinatorial optimisation (VRP/mTSP, OR-Tools) | | ●●● | |
| Simulation (PX4 SITL, Gazebo, multi-vehicle) | ● | ●●● | ● |
| Camera models and photogrammetric flight design (GSD, overlap) | | ●●● | ●●● |
| Embedded cameras (libcamera, Picamera2) | | | ●●● |
| Structure from Motion and bundle adjustment (COLMAP, ODM, Metashape) | | ● | ●●● |
| Accuracy assessment (GCPs, check points, RMSE) | | ●● | ●●● |
| GIS tools (QGIS, GeoJSON, raster tiles) | | ●● | ●● |
| Experimental design and statistics | ●● | ●● | ●● |
| Academic writing and literature review | ●● | ●● | ●● |

Use the matrix to spot gaps: where only one person has ●●● or ●●, that person is a single point of failure, so plan a short knowledge-transfer session before flight campaigns. Each owner can mark their current level next to the target in their pipeline README if useful.

## Shared foundation (everyone)

| Skill | Why we need it | Start with |
| --- | --- | --- |
| Linux shell, Git, Python | Every node is a Pi; all code and docs live in one repo | [Software Carpentry lessons](https://software-carpentry.org/lessons/): Unix shell, Git, Python, designed for researchers |
| GitHub collaboration | Pull requests, code review, CODEOWNERS, issues | [CONTRIBUTING.md](../CONTRIBUTING.md); GitHub docs on [pull requests](https://docs.github.com/en/pull-requests) and [code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners) |
| ROS 2 basics | All onboard data moves as ROS 2 topics | [ROS 2 Jazzy tutorials](https://docs.ros.org/en/jazzy/Tutorials.html), "Beginner: CLI tools" and "Beginner: Client libraries" in order; they build on each other |
| PX4 + ROS 2 | Missions, telemetry, camera triggers | [PX4 user guide](https://docs.px4.io/main/en/) and its [ROS 2 section](https://docs.px4.io/main/en/ros2/) |
| Drone regulation and field safety | No flights without it | EU rules: [EASA rules & standards](https://www.easa.europa.eu/en/domains/drones-air-mobility/rules-standards) (Reg. 2019/947 and 2019/945; open, specific and certified categories). Finland: [Traficom open category](https://traficom.fi/en/operations-open-category), [where and when you can fly](https://static.traficom.fi/en/unmanned-aviation/where-and-what-conditions-you-can-fly-drone), and restricted zones on [droneinfo.fi](https://droneinfo.fi/en). Every pilot needs at least the A1/A3 online certificate; A2 requires A1/A3 plus self-practical training ([Traficom](https://traficom.fi/en/additional-theoretical-knowledge-examination-subcategory-a2)). Multi-UAV flights with a >2 kg custom airframe likely fall in the **specific** category and need an operational authorisation (*verify* with Traficom early) |
| Time and coordinates | Every interface uses GNSS-UTC time and WGS84/UTM ([conventions](../integration/interfaces/README.md#shared-conventions)) | [pyproj docs](https://pyproj4.github.io/pyproj/stable/); the [time sync section](../mesh/docs/technical.md#time-sync-gnss--pps--chrony) of the mesh notes |
| Experimental design | One shared flight dataset must answer RQ1–RQ4 with controlled factors | [integration academic notes](../integration/docs/academic.md); factor settings in [run metadata](../integration/interfaces/run-metadata.md) |

## Mesh networking

| Skill | Why we need it | Start with |
| --- | --- | --- |
| 802.11 interface modes, `iw` | Bring up IBSS and 802.11s mesh point on USB radios; check driver support | [mac80211 virtual interfaces (iw)](https://wireless.docs.kernel.org/en/latest/en/users/documentation/iw/vif.html): IBSS join, mesh point creation |
| BATMAN-adv and `batctl` | The mesh under test; tuning levers (OGM interval, hop penalty, ELP) | [batman-adv getting started](https://www.open-mesh.org/doc/batman-adv/gettingstarted.html); [kernel docs](https://docs.kernel.org/networking/batman-adv.html); `man batctl`. Support: #batadv on hackint, mailing list |
| Babel (baseline) | Comparison routing protocol | [babeld](https://www.irif.fr/~jch/software/babel/) docs and man page |
| ROS 2 middleware | Zenoh vs tuned DDS is a research question | [rmw_zenoh README](https://github.com/ros2/rmw_zenoh) (router/session configs, `ZENOH_CONFIG_OVERRIDE`); [zenoh-plugin-ros2dds](https://github.com/eclipse-zenoh/zenoh-plugin-ros2dds) (bridge, allow-lists). Note: the bridge and rmw_zenoh are separate and do not talk to each other ([ROS Discourse](https://discourse.openrobotics.org/t/rmw-rmw-bridge-is-it-possible-has-anyone-done-it/49564)) |
| GNSS + PPS + chrony | Clock offset between nodes is a measured outcome (RQ4) | [chrony docs](https://chrony-project.org/documentation.html); worked Pi example on the [openSUSE HCL page](https://en.opensuse.org/HCL:Raspberry_Pi3_GPS). Test with `ppstest /dev/pps0` before chrony; tune the NMEA offset for your receiver, don't copy it |
| Measurement and capture | Goodput, route changes, discovery overhead | `man iperf3`, `man tcpdump`; [Wireshark user guide](https://www.wireshark.org/docs/wsug_html_chunked/) for RTPS/Zenoh dissection |
| Network emulation | Feed realistic links to planning's SITL | [tc-netem(8)](https://man7.org/linux/man-pages/man8/tc-netem.8.html): delay, loss, rate; note timer-granularity limits and that TCP tests need netem on the receiver's ingress |
| Ansible + systemd | Identical config on every node, repeatable bring-up | [Ansible docs](https://docs.ansible.com/) (inventory, playbooks, roles); `man systemd.service` |

## Path planning

| Skill | Why we need it | Start with |
| --- | --- | --- |
| Photogrammetric flight design | GSD, footprint, overlap, trigger distance, oblique geometry | The [camera and footprint maths](../planning/docs/technical.md#camera-and-footprint-math) in the planning notes, and the literature in [planning academic](../planning/docs/academic.md) |
| Computational geometry | Area split, footprints, coverage checks | [Shapely manual](https://shapely.readthedocs.io/); [pyproj](https://pyproj4.github.io/pyproj/stable/) for UTM |
| Vehicle routing / mTSP | Multi-UAV routing with a goodput cost term | [OR-Tools VRP guide](https://developers.google.com/optimization/routing/vrp) (minimise the longest route), then [capacitated VRP](https://developers.google.com/optimization/routing/cvrp) for adding dimensions |
| PX4 missions and MAVROS/MAVSDK | Upload missions with distance-based camera triggers | [PX4 missions](https://docs.px4.io/main/en/flying/missions.html); [MAVSDK](https://mavsdk.mavlink.io/); [MAVLink mission protocol](https://mavlink.io/en/services/mission.html) |
| Multi-vehicle SITL | Test the planner with several UAVs and emulated links | [PX4 multi-vehicle simulation with ROS 2](https://docs.px4.io/main/en/ros2/multi_vehicle): one uXRCE-DDS agent, per-instance namespaces `px4_N`; [Gazebo docs](https://gazebosim.org/docs) |
| Online re-planning | React to coverage holes in flight | ROS 2 services/actions ([Jazzy tutorials](https://docs.ros.org/en/jazzy/Tutorials.html)); the [coverage holes](../integration/interfaces/coverage-holes.md) and [mission plan](../integration/interfaces/mission-plan.md) contracts |
| GIS | Draw and check areas of interest, view plans | [QGIS user manual](https://docs.qgis.org/latest/en/docs/user_manual/); GeoJSON ([RFC 7946](https://datatracker.ietf.org/doc/html/rfc7946)) |

## Forward-feed photogrammetry

| Skill | Why we need it | Start with |
| --- | --- | --- |
| Pi cameras and libcamera | Fixed focus/exposure capture, `SensorTimestamp` for geotags | [Picamera2 library guide (PDF)](https://pip-assets.raspberrypi.com/categories/1044-raspberry-pi-ai-camera/documents/RP-008156-DS-3-picamera2-manual.pdf), metadata section; [Raspberry Pi camera docs](https://www.raspberrypi.com/documentation/computers/camera_software.html) |
| Geotagging and pose priors | Timing error is likely the dominant error source (RQ4) | The [capture and geotagging](../photogrammetry/docs/technical.md#capture-and-geotagging) notes; [image record](../integration/interfaces/image-record.md) contract |
| Structure from Motion | Quick-look and refinement pipelines | [COLMAP tutorial](https://colmap.readthedocs.io/en/stable/tutorial.html): features → matching → incremental SfM → MVS |
| OpenDroneMap / Metashape | Refined products with GCPs; reference pipeline | [ODM docs](https://docs.opendronemap.org/), especially [ground control points](https://docs.opendronemap.org/gcp/) (≥5 GCPs, 8–10 for larger areas, spread across the area); Agisoft Metashape user manual |
| Accuracy assessment | RMSE on independent check points is the main accuracy metric | [ASPRS Positional Accuracy Standards, Edition 2, Version 2 (2024)](https://asprs.org/?p=27154), which includes a UAS addendum (RMSE only; no 95% confidence level; minimum 30 check points for product assessment; survey error included). Summary: [LIDAR Magazine](https://lidarmag.com/2023/10/06/the-asprs-positional-accuracy-standards-edition-2/) |
| RTK GNSS surveying | Measure GCPs and check points | Receiver manual (u-blox F9P or the survey rover we use); a field session with someone experienced (*verify* who in the lab) |
| Bandwidth-aware scheduling | Quality ladder, keyframe score, reachback | ROS 2 QoS ([Jazzy QoS concepts](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html)); [live goodput](../integration/interfaces/goodput.md) contract |
| Map viewing | Quick-look display for the ground team | [Leaflet](https://leafletjs.com/) or [OpenLayers](https://openlayers.org/); [Foxglove](https://docs.foxglove.dev/) for ROS data |
| Point-cloud comparison | Cloud-to-cloud checks against reference | [CloudCompare documentation](https://www.cloudcompare.org/doc/) |

## Suggested first month

1. **Week 1, everyone:** Software Carpentry shell + Git refresher; ROS 2 Jazzy beginner tutorials; read the [main doc](README.md) and all [interfaces](../integration/interfaces/README.md).
2. **Week 1–2, everyone:** start the drone pilot certificates (A1/A3, then A2) so they are ready before spring flights.
3. **Week 2–4, mesh:** three Pis on a bench with BATMAN-adv over IBSS; chrony + PPS on one node; first iperf3 numbers.
4. **Week 2–4, planning:** camera/footprint module in Python; single-vehicle PX4 SITL mission; OR-Tools VRP example adapted to strips.
5. **Week 2–4, photogrammetry:** Picamera2 capture with fixed settings and `SensorTimestamp`; process a public drone dataset in COLMAP and ODM with GCPs.
6. **End of month, all three:** one-hour session each, teaching the other two your pipeline at ●● level (see matrix).
