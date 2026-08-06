# BV→SEB OFAT A1 one-time runtime handoff

> This is the unique handoff for the one-time A1 execution authorized after packet commit `cdfd5327579cd6045844918d5456990f3cce532c`.
>
> Primary status: `A1_STRUCTURE_PASS / A1_MESH_CONTRACT_FAIL / STOPPED_BEFORE_A2`.

## 1. Result first

A1 ran exactly once on `tcad` and generated a real DevEdit STR. Parser completion and structure topology passed: 12 regions, three terminals, and one continuous stepped gate. The actual two-axis track mesh failed the fixed contract:

- actual max Δx in the track ROI: `0.3125 µm` (required ≤`0.016 µm`);
- actual max Δy: `0.0250 µm` (required ≤`0.016 µm`);
- full y=0–0.60 µm path continuity: PASS.

The presence of one continuous vertical xion node line does not compensate for the missing radial x resolution. No edit, fix, rerun, or A2 action was taken.

## 2. Fixed identity and environment

| Field | Value |
|---|---|
| packet commit | `cdfd5327579cd6045844918d5456990f3cce532c` |
| source candidate commit | `994d83bc444e7a17695f003b65f0d90da25c8023` |
| packet | `04_reports/attachments/20260806_bv_to_seb_ofat/stage_packets_20260807/packets/OFAT_A1_devedit_structure_mesh_packet.in` |
| remote host | `tcad` via `silvaco` |
| remote workdir | `/root/DECKBUILD/preflight/OFAT_cdfd532_A1_20260807` |
| DeckBuild | `5.2.40.R` |
| DevEdit | `2.8.26.R` |
| command | `/root/bin/vdoe_tmux.sh start-deck /root/DECKBUILD/preflight/OFAT_cdfd532_A1_20260807 OFAT_A1_devedit_structure_mesh_packet.in` |

The uploaded packet was read back and verified byte-identical before execution. It was not edited remotely.

## 3. Gate results

| Gate | Result | Evidence |
|---|---|---|
| input active-token scan | PASS | 1 DevEdit, 1 structure, 0 Atlas/solve/SEU/tfinal/system |
| parser | PASS WITH MATERIAL WARNINGS | parse errors 0; eight material warning records retained |
| STR creation | PASS | 617,727-byte actual STR |
| region topology | PASS | 12 actual regions |
| terminal topology | PASS | source=1, drain=2, single stepped gate=3 |
| mesh quality | PASS for obtuse only | 5,045 points / 9,802 triangles / 0 obtuse |
| track max Δx | **FAIL** | 0.3125 µm > 0.016 µm |
| track max Δy | **FAIL** | 0.0250 µm > 0.016 µm |
| full-y continuity | PASS | connected y=0–0.60 µm center path |

## 4. Scope confirmation

```text
A1_EXECUTIONS = 1
A2_EXECUTED = NO
A3_EXECUTED = NO
B1_EXECUTED = NO
B2_EXECUTED = NO
ATLAS_EXECUTED = NO
STATIC_300V_EXECUTED = NO
SEU_TRANSIENT_EXECUTED = NO
PAIRED_TRANSIENT_EXECUTED = NO
AUTO_FIX_PERFORMED = NO
NEW_RUN_CREATED = NO
```

The remote session ended naturally and no SILVACO process or tmux session remained. The standard runner did not record a numeric DevEdit child exit code because its `EXIT.txt` extractor is ATLAS-specific. This limitation is explicit; the handoff does not fabricate an exit code.

## 5. Evidence index

All runtime attachments are in [`a1_runtime_20260807/`](attachments/20260806_bv_to_seb_ofat/a1_runtime_20260807/):

- [technical report](attachments/20260806_bv_to_seb_ofat/a1_runtime_20260807/A1_RUNTIME_REPORT.md)
- [complete typescript](attachments/20260806_bv_to_seb_ofat/a1_runtime_20260807/typescript.txt)
- [actual STR](attachments/20260806_bv_to_seb_ofat/a1_runtime_20260807/OFAT_A_bv_devedit_mesh_x10p25.str)
- [region/electrode table](attachments/20260806_bv_to_seb_ofat/a1_runtime_20260807/A1_REGION_ELECTRODE_TABLE.csv)
- [mesh ROI metrics](attachments/20260806_bv_to_seb_ofat/a1_runtime_20260807/A1_MESH_ROI_METRICS.csv)
- [warning/fatal register](attachments/20260806_bv_to_seb_ofat/a1_runtime_20260807/A1_WARNING_FATAL_REGISTER.md)
- [artifact index](attachments/20260806_bv_to_seb_ofat/a1_runtime_20260807/A1_ARTIFACT_INDEX.md)
- [actual structure image](attachments/20260806_bv_to_seb_ofat/a1_runtime_20260807/figs/OFAT_A1_cdfd532_A14_actual_structure.png)
- [actual mesh image](attachments/20260806_bv_to_seb_ofat/a1_runtime_20260807/figs/OFAT_A1_cdfd532_A14_actual_mesh.png)

## 6. Open gates and next recommendation

Open gates:

1. A1 track mesh contract is failed and needs web-side adjudication.
2. A2 remains unauthorized pending A1 result and a new web review.
3. A3 and B2 remain unauthorized.
4. B1 still requires separate authorization; B1B remains not established.
5. No ATLAS parser/material/thermcontact/static-equivalence fact has been established.

`NEXT_RECOMMENDATION = STOP_FOR_WEB_REVIEW / DO_NOT_AUTHORIZE_A2_ON_THIS_STR`.

This handoff is evidence and a stop report. It does not authorize packet repair or any next-stage execution.
