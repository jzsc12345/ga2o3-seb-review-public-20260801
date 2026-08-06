# BV→SEB OFAT A1_REV2 one-time runtime stop handoff

> Status: `A1_REV2_EXECUTED_ONCE / DEVEDIT_SEGFAULT / STR_NOT_CREATED / STOPPED`
>
> Input commit: `bbe2b5f22a7c9245d35e80831a8bc056d84d4fd6`
>
> Scope: `A1_REV2_ONLY`; A2 and all electrical/transient stages remain denied.

## 1. Result first

The approved packet was uploaded byte-for-byte unchanged and executed exactly once through
the established `DeckBuild + tmux` route. DevEdit built an intermediate mesh, entered the
inherited refinement sequence, and then terminated with exit code 11. The VM kernel log
records a `devedit.exe` segmentation fault. The final STR was not written.

Therefore the unchanged track-mesh contract cannot be measured on A1_REV2. The correct
adjudication is:

```text
A1_REV2_MESH_CONTRACT = FAIL
FAILURE_MODE = DEVEDIT_SEGFAULT_BEFORE_FINAL_STR
A2_AUTHORIZATION = DENIED
SECOND_EXECUTION = NOT_PERFORMED
```

## 2. Fixed input and execution identity

- Fixed packet: [OFAT_A1_REV2_devedit_track_mesh_packet.in](attachments/20260806_bv_to_seb_ofat/a1_rev2_mesh_repair_20260807/packets/OFAT_A1_REV2_devedit_track_mesh_packet.in)
- Remote host: `tcad` through SSH alias `silvaco`
- Remote workdir: `/root/DECKBUILD/preflight/OFAT_bbe2b5f_A1_REV2_20260807`
- Command: `/root/bin/vdoe_tmux.sh start-deck /root/DECKBUILD/preflight/OFAT_bbe2b5f_A1_REV2_20260807 OFAT_A1_REV2_devedit_track_mesh_packet.in`
- DeckBuild: `5.2.40.R`
- DevEdit: `2.8.26.R`
- Execution count: `1`
- Exit code: `11`
- Input readback: byte-for-byte identical, 9,263 bytes; no hash calculated

## 3. Failure evidence

The initial MeshBuild printed 2,332 points, 4,557 triangles, and 0 obtuse triangles. These are
intermediate values only. The crash occurred later during this inherited card:

```silvaco
refine mode=x x1=4.18 y1=-0.1377 x2=13.89 y2=0.5819
```

The transcript records `simExited with exitcode11`; the kernel records a `devedit.exe`
segmentation fault. No explicit parse error appeared, but parser/structure completion was not
reached. No final STR, structure image, mesh image, or measured REV2 ROI table exists.

## 4. A1 versus A1_REV2

| Metric | Original A1 | A1_REV2 | Adjudication |
|---|---:|---:|---|
| final STR | YES | NO | REV2 FAIL |
| max Δx | 0.3125 µm | `NOT_AVAILABLE` | not comparable |
| max Δy | 0.0250 µm | `NOT_AVAILABLE` | not comparable |
| full-y continuity | PASS | `NOT_EVALUABLE` | not comparable |
| final nodes | 5,045 | `NOT_AVAILABLE` | not comparable |
| final triangles | 9,802 | `NOT_AVAILABLE` | not comparable |
| final obtuse | 0 | `NOT_AVAILABLE` | not comparable |

The contract remains max Δx ≤0.016 µm, max Δy ≤0.016 µm, and full-y continuity PASS. REV2
fails because there is no final STR to test, not because a measured REV2 spacing exceeded the
limit.

## 5. Evidence index

Runtime evidence is under
[`attachments/20260806_bv_to_seb_ofat/a1_rev2_runtime_20260807/`](attachments/20260806_bv_to_seb_ofat/a1_rev2_runtime_20260807/):

- [complete typescript](attachments/20260806_bv_to_seb_ofat/a1_rev2_runtime_20260807/typescript.txt)
- [runner exit](attachments/20260806_bv_to_seb_ofat/a1_rev2_runtime_20260807/EXIT.txt)
- [runtime report](attachments/20260806_bv_to_seb_ofat/a1_rev2_runtime_20260807/A1_REV2_RUNTIME_REPORT.md)
- [warning/fatal register](attachments/20260806_bv_to_seb_ofat/a1_rev2_runtime_20260807/A1_REV2_WARNING_FATAL_REGISTER.md)
- [remote failure evidence](attachments/20260806_bv_to_seb_ofat/a1_rev2_runtime_20260807/A1_REV2_REMOTE_STATE_AND_FAILURE_EVIDENCE.txt)
- [ROI contract table](attachments/20260806_bv_to_seb_ofat/a1_rev2_runtime_20260807/A1_REV2_MESH_ROI_METRICS.csv)
- [A1 versus REV2 table](attachments/20260806_bv_to_seb_ofat/a1_rev2_runtime_20260807/A1_VS_A1_REV2_METRICS.csv)
- [artifact index](attachments/20260806_bv_to_seb_ofat/a1_rev2_runtime_20260807/ARTIFACT_INDEX.md)

`deckbuild_log.txt` is preserved as the actual zero-byte runner artifact. There is no STR or
image attachment because none was generated; no substitute was fabricated.

## 6. Authorization boundary and final state

```text
A2_EXECUTED = NO
ATLAS_EXECUTED = NO
STATIC_BIAS_EXECUTED = NO
SEU_TRANSIENT_EXECUTED = NO
PAIRED_TRANSIENT_EXECUTED = NO
AUTO_FIX_PERFORMED = NO
```

No packet or parameter was modified after failure. No rerun was launched. Post-run, the exact
tmux session and all relevant SILVACO processes were absent.

## 7. Open gates

1. A1_REV2 must not be promoted to a valid mesh parent.
2. A2 remains denied.
3. The earlier ordering hypothesis remains unconfirmed by a final STR.
4. Any third repair packet or execution requires a new plan, web review, and explicit user
   authorization.

## 8. Recommendation

`STOP_FOR_WEB_REVIEW / DO_NOT_AUTHORIZE_A2 / REVIEW_DEVEDIT_SEGFAULT_BEFORE_ANY_NEW_PACKET`.
