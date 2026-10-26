# Mesh link range test

[← Mesh (P1)](../../README.md) · [Main doc](../../../docs/README.md)

Measures range and signal quality of the running BATMAN-adv mesh link between two Raspberry Pis (the folder keeps its original name, `adhoc-range`): RSSI, SNR, MCS, retries, TCP/UDP throughput, loss and RTT against distance. It also fits a path loss exponent, estimates the usable range and compares both with a theoretical link budget. It is step 2 of the [ground test procedure](../../docs/technical.md#ground-test-procedure-before-flights) and runs *on the mesh*: traffic goes over bat0, and link quality comes from `iw station dump` on the underlying IBSS interface. The harness does not configure the radio; bring the mesh up with [mesh-up.sh](../../bringup/README.md) first.

**Status:** written and unit-tested against hand-written sample output; **not yet run on two Pis** (reworked from a standalone IBSS test to run on the mesh, also untested). Treat every *verify* below as untested.

```
adhoc-range/
├── config.yaml          # single source of truth for scripts and Python
├── requirements.txt  Makefile
├── scripts/
│   └── start_server.sh        # iperf3 -s on Pi 2
├── linktest/
│   ├── collector.py     # iw station/survey dump, 1 Hz
│   ├── traffic.py       # iperf3 TCP/UDP + ping
│   ├── runner.py        # interactive distance steps
│   ├── analysis.py      # plots, path loss fit, usable range
│   ├── linkbudget.py    # theoretical range, comparison
│   └── config.py  common.py
└── tests/               # pytest + data/ (saved iw, iperf3, ping output)
```

## Setup

Assumed hardware: two Raspberry Pi 5 with onboard Wi-Fi (brcmfmac) in the mesh from [mesh/bringup](../../bringup/README.md): `mesh-net`, ch 36 (5180 MHz), `10.10.0.1` (Pi 1, fixed) and `10.10.0.2` (Pi 2, moved). Change addresses or the frequency in [config.yaml](config.yaml); the frequency must match `FREQ_MHZ` in `mesh.conf` (used only by the link budget).

1. **Install on both Pis:** `sudo apt install iw iperf3 iputils-ping python3-venv`, then `make setup` (creates `.venv`).
2. **Mesh up on both Pis:** `sudo mesh/bringup/mesh-up.sh`. Check from Pi 1: `batctl n` lists Pi 2 and `ping 10.10.0.2` answers. Nothing is torn down or reconfigured by this harness, so SSH over the mesh keeps working.
3. **Pi 2:** `scripts/start_server.sh` (leave it running).
6. **Physical layout:** line of sight, both antennas at the same height (about 1.5 m) and orientation, Pi 2 on a power bank, nothing else on the mesh channel if you can avoid it. Keep the same layout for the whole run, otherwise the distance trend is polluted by antenna changes.

## Run a test

On Pi 1:

```bash
make run                      # all distances in config.yaml
make run ARGS="--distance 30" # re-measure one distance (replaces its row)
make run ARGS="--resume"      # continue the latest run, skipping finished distances
make analyze RUN=../../../runs/linktest/<run_id>
make test
```

For each distance the runner prompts `Move Pi 2 to X m and press Enter`, waits `settle_s` (30 s), then runs the collector for the whole step while ping, TCP and UDP run one after another, each for `duration_s`. A step therefore takes about `settle_s + 3 × duration_s`. Output goes to `<output_dir>/<run_id>/` (default `runs/linktest/`, git-ignored): `summary.csv` (one row per distance), `raw_<distance>m.csv` (per-second samples with a `phase` column), `config.yaml` (snapshot) and, after analysis, `plots/`. `--resume` and `--run-id` pick the run; `--no-peer-check` skips the start-up ping (needed when resuming at a distance beyond range). Ctrl-C keeps finished steps.

Stop the iperf3 server on Pi 2 with Ctrl-C. The mesh stays up.

Analysis writes RSSI, SNR, throughput, loss and MCS plots, fits `RSSI = A - 10·n·log10(d)` (needs ≥ 3 distances), overlays free space (n = 2) on the RSSI plot, and reports the usable range: the last distance before the first step where TCP goodput is below `throughput_fraction` × the nearest step's goodput, or UDP/ping loss exceeds `loss_threshold_pct`. `linkbudget.py` prints the predicted range per MCS and, with `--run`, the model error and the range with the measured exponent.

## Interpreting the metrics

Rules of thumb for 2.4 GHz Wi-Fi, not standards (5 GHz loses about 6 dB more over the same distance). RSSI is what Pi 1 measures on frames from Pi 2, so it is one direction only.

| Metric | Reading |
| --- | --- |
| RSSI (`signal`) | > −55 dBm excellent · −55 to −67 good · −67 to −75 usable, rate drops · −75 to −85 marginal · < −85 expect drops. Std dev above ~5 dB means multipath or movement. Compare with the free-space line: a large gap at 1–5 m means antenna misalignment, not distance. |
| SNR | RSSI − noise floor. > 25 dB supports high MCS, 10–25 low/mid MCS, < 10 barely works. Empty when the driver reports no noise. |
| Path loss exponent n | ~2 free space, 2.7–3.5 near the ground or with obstacles, > 4 heavy obstruction. A 1 m point sits in the near field and can skew the fit; drop it if the plot shows it. |
| MCS / bitrate | Falls as SNR falls. A rate stuck low at good RSSI points to interference. No MCS (legacy rates) means the link runs without HT (see limitations). |
| `tx_retry_pct` | Retries per transmitted packet over the step: < 5 % healthy, 5–20 % degrading, > 20 % poor. Rises before throughput falls, so it is the early warning. `tx_failed` counts packets dropped after the retry limit. |
| TCP goodput | The usable capacity. Expect well below the PHY rate (about half or less). A cliff is the range edge. |
| UDP loss / jitter | Loss at a fixed offered load (`udp_bitrate`); only meaningful if that load is below capacity at short range. Check `udp_mbps` at 1 m first. |
| Ping loss / RTT | Loss measures link reliability for small packets; rising RTT max with retries shows retransmission. |
| `link_up_pct` | Share of seconds in which Pi 2 appeared in the station dump. Below 100 % means the link dropped during the step. |
| `notes` | Failed traffic tests. A failed iperf3 test is recorded as 0 Mbit/s, which can also mean the server is not running; read the note. |

## Known limitations

- **brcmfmac (Pi onboard Wi-Fi) and IBSS.** The driver lists IBSS, but it is a FullMAC driver with limited ad-hoc behaviour: HT (802.11n) in IBSS is not reliable (*verify*), so expect legacy rates up to 54 Mbit/s and no MCS column. `station dump` may report fewer fields (no expected throughput, no averaged signal) and peers may take several seconds to appear (*verify*). 802.11s is not available. A USB adapter with mt76/ath9k_htc is the planned alternative ([hardware options](../../docs/technical.md#hardware)).
- **Empty `station dump`.** Observed on the Pi 5 (brcmfmac) in the mesh: `iw station dump` lists nothing, but `iw station get <mac>` returns signal, tx bitrate and packet counters (no retries, MCS or expected throughput). Set `peer_mac` in `config.yaml` (Pi 2's wlan0 MAC) and the collector uses `station get`. Those missing fields stay empty in the CSVs.
- **Noise floor may not be reported.** `iw survey dump` on brcmfmac often has no `noise` line (*verify*). The collector logs a warning once and leaves `noise_dbm` and `snr_db` empty; the SNR plot is skipped. Use RSSI against the thresholds instead, or assume a floor of about −95 dBm for a rough SNR.
- **Regulatory limits.** The country domain caps TX power and allowed channels. In Finland `iw reg get` shows 20 dBm EIRP on 2.4 GHz, 5150–5250 MHz indoor only, and DFS on 5250–5350 and 5470–5725 MHz. `linkbudget` warns when TX power + antenna gain exceeds `regulatory_eirp_limit_dbm`. Check your country's rules. brcmfmac manages its own regulatory domain in firmware, so `iw reg set` may not change what the chip allows (*verify*). `txpower` may be rounded, capped or ignored; the script reads it back but only warns.
- **Measures the mesh, not the bare radio.** Throughput and RTT include batman-adv encapsulation (32 B header, `BAT_MTU` 1400) and routing. RSSI, MCS and retries are still per-radio-link values from the station dump. Between Pis that are two hops apart through a third node, the iperf3 numbers are end-to-end while RSSI is for the strongest-heard neighbour, so keep the test to a direct link (`batctl n`, `batctl o`).
- **Mesh traffic shares the channel.** OGM broadcasts and any other traffic on bat0 run during the test; keep other flows off.
- Single-link, single-direction RSSI; one run per distance; no mobility. Multipath at ground level makes RSSI at a point vary by several dB, so measure more than one run before trusting n.
- iperf3 is stopped by the runner's timeout only; if the server was restarted mid-run, rerun that distance with `--distance`.

## Troubleshooting

| Symptom | Likely cause and fix |
| --- | --- |
| `missing required tool(s)` | `sudo apt install iw iperf3 iputils-ping` |
| `config key '...' is missing` / pyyaml import error | Run through `make` (uses `.venv`), or `sudo apt install python3-yaml` |
| `peer ... is unreachable` | Mesh not up on both Pis (`batctl n`), addresses in `config.yaml` differ from `mesh.conf`, or too far apart at the first step. |
| iperf3 `Connection refused` in `notes` | `scripts/start_server.sh` not running on Pi 2, or bound to a different IP. |
| `station dump` is empty | No traffic yet (IBSS peers appear after frames are exchanged), or the mesh link is down, or the peer left. The step is recorded with `link_up_pct` below 100. |
| UDP loss high even at 1 m | `udp_bitrate` exceeds capacity; lower it. |
| No SNR plot | The driver reports no noise floor, see above. |
