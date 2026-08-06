# OFAT Arm A A1 DevEdit structure/mesh runtime report

> Evidence date: 2026-08-07 (Asia/Singapore)
>
> Packet commit: `cdfd5327579cd6045844918d5456990f3cce532c`
>
> Packet path: `04_reports/attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/packets/OFAT_A1_devedit_structure_mesh_packet.in`
>
> Scope: `A1_ONLY / DEVEDIT_STRUCTURE_MESH_PACKET`
>
> Result: `A1_STRUCTURE_PASS / A1_MESH_CONTRACT_FAIL / STOPPED`

## 1. Execution identity

- Remote host: `tcad` through SSH alias `silvaco`
- OS: Red Hat Enterprise Linux Server 7.9
- Remote workdir: `/root/DECKBUILD/preflight/OFAT_cdfd532_A1_20260807`
- DeckBuild: `5.2.40.R`
- DevEdit: `2.8.26.R`
- Command: `/root/bin/vdoe_tmux.sh start-deck /root/DECKBUILD/preflight/OFAT_cdfd532_A1_20260807 OFAT_A1_devedit_structure_mesh_packet.in`
- Start: `2026-08-07T00:38:40.102318219+0800`
- STR write time: `2026-08-07 00:39:03.153953604 +0800`
- DevEdit elapsed line: `20.89 s`
- Launcher exit: `0`
- Simulator exit code: `NOT_RECORDED_BY_STANDARD_RUNNER`. `EXIT.txt` is empty because the standard runner only extracts the ATLAS phrase `simulator exits with code`; this A1 packet never enters ATLAS. Natural tmux termination, `Parse complete`, and the generated STR are the completion evidence.

The uploaded packet was read back before execution and compared byte-for-byte with the fixed local packet: 8,936 bytes on both sides and identical. No hash was used.

## 2. Scope compliance

Pre-execution active-command scan:

| Token | Count |
|---|---:|
| `go devedit` | 1 |
| `structure` | 1 |
| `go atlas` | 0 |
| `solve` | 0 |
| `singleeventupset` | 0 |
| `tfinal` | 0 |
| `system/ssh/shell` | 0 |
| `quit` | 1 |

Final remote state: no `dbascii.exe`, `deckbuild`, `devedit`, or `atlas` process and no tmux session. No A2, A3, B1, B2, ATLAS, static bias, 300 V solve, SEU, or paired transient was executed.

## 3. Parser and structure result

The DevEdit tail records `Parse complete: Error(s)=0, Warning(s)=0`, but the full transcript separately contains eight `Material WARNING` records for user materials 50/51. They are retained in the warning register and must not be hidden by the final summary count.

The generated STR is `617,727` bytes and contains:

- 5,045 coordinate records;
- 9,802 triangles;
- 0 obtuse and 0 degenerate triangles;
- 12 regions;
- three electrodes: source=1, drain=2, gate=3;
- one continuous stepped Nickel gate in region 12.

The gate's actual triangle-union area is `0.235 µm²`, with bbox `x=1.5–6.0 µm`, `y=-0.20–-0.12 µm`. This matches the intended stepped-gate polygon and does not create a separate `gate_fp` terminal.

## 4. Track mesh contract result

The packet declares a two-axis target of `max.width=max.height=0.016 µm` in `x=10.10–10.40 µm`, `y=0–0.60 µm`. The generated STR does **not** meet it.

Metric method: for actual semiconductor triangles (regions 1–3) whose centroid lies in the declared track ROI, report the largest triangle bounding span in x and y. This directly measures the cell span that resolves the source column.

| Metric | Contract | Actual | Result |
|---|---:|---:|---|
| max Δx | ≤0.016 µm | 0.3125 µm | FAIL |
| max Δy | ≤0.016 µm | 0.0250 µm | FAIL |
| full-y node/path continuity | required | PASS, y=0–0.60 µm | PASS |

Only one vertical node line exists at `xion=10.25 µm`; the nearest bracketing x levels are `9.9375` and `10.5625 µm`, each `0.3125 µm` away. The centerline has 49 nodes and a maximum y gap of `0.025 µm`. Full-y continuity therefore exists, but the two-axis radial resolution does not.

Per the authorization, this is a hard stop. No packet edit, auto-fix, rerun, or A2 execution was performed.

## 5. Other ROI measurements

The same actual-triangle centroid/bounding-span method gives:

| ROI | max Δx (µm) | max Δy (µm) |
|---|---:|---:|
| channel/oxide | 0.5000 | 0.0125 |
| stepped-gate endpoint | 0.1875 | 0.0200 |
| source junction | 0.5000 | 0.0250 |
| drain junction | 0.3125 | 0.0250 |
| NiO/Ga2O3 | 0.2500 | 0.0250 |

These values are evidence, not an instruction to modify the mesh.

## 6. Evidence and open gates

- Raw combined PTY transcript: `typescript.txt`
- Actual STR: `OFAT_A_bv_devedit_mesh_x10p25.str`
- Structure image: `figs/OFAT_A1_cdfd532_A14_actual_structure.png`
- Mesh image: `figs/OFAT_A1_cdfd532_A14_actual_mesh.png`
- Region/electrode table: `A1_REGION_ELECTRODE_TABLE.csv`
- ROI table: `A1_MESH_ROI_METRICS.csv`
- Warning register: `A1_WARNING_FATAL_REGISTER.md`

Open gates:

1. A1 track mesh contract is failed.
2. A2 requires a new web review and is not authorized.
3. A3, B1, B1B, and B2 remain closed/not established as previously adjudicated.
4. No ATLAS/material/thermal/static-state claim can be made from A1.

Recommendation: `STOP_FOR_WEB_REVIEW / DO_NOT_AUTHORIZE_A2_ON_THIS_STR`.
