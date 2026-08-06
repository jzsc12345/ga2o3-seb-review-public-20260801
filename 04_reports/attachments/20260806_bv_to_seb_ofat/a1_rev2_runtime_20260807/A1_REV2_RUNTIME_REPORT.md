# OFAT Arm A A1_REV2 DevEdit mesh-repair runtime report

> Evidence date: 2026-08-07 (Asia/Singapore)
>
> Input commit: `bbe2b5f22a7c9245d35e80831a8bc056d84d4fd6`
>
> Scope: `A1_REV2_ONLY / ONE_EXECUTION_ONLY / DEVEDIT_STRUCTURE_MESH`
>
> Result: `DEVEDIT_SEGFAULT / STR_NOT_CREATED / MESH_CONTRACT_FAIL / STOPPED`

## 1. Result first

The single authorized A1_REV2 execution was launched once and ended with DevEdit exit code
11. The VM kernel log records a `devedit.exe` segmentation fault. The crash occurred during
an inherited post-MeshBuild `refine mode=x` card, before the packet reached its final
`structure outf=...` statement. No STR was generated.

Consequently, A1_REV2 did not produce evidence with which to measure the unchanged two-axis
mesh contract. All final-STR-dependent quantities are `NOT_EVALUABLE`; none are copied from
the original A1 or inferred from the intermediate mesh statistics.

```text
A1_REV2_EXECUTION_COUNT = 1
A1_REV2_PARSER = INCOMPLETE_DUE_DEVEDIT_SEGFAULT
A1_REV2_STR_CREATED = NO
A1_REV2_MESH_CONTRACT = FAIL
A2_AUTHORIZATION = DENIED
AUTO_FIX_PERFORMED = NO
```

## 2. Execution identity

- Packet: `04_reports/attachments/20260806_bv_to_seb_ofat/a1_rev2_mesh_repair_20260807/packets/OFAT_A1_REV2_devedit_track_mesh_packet.in`
- Remote host: `tcad` through SSH alias `silvaco`
- Remote workdir: `/root/DECKBUILD/preflight/OFAT_bbe2b5f_A1_REV2_20260807`
- Command: `/root/bin/vdoe_tmux.sh start-deck /root/DECKBUILD/preflight/OFAT_bbe2b5f_A1_REV2_20260807 OFAT_A1_REV2_devedit_track_mesh_packet.in`
- DeckBuild: `5.2.40.R`
- DevEdit: `2.8.26.R`
- Packet readback: byte-for-byte identical, 9,263 bytes; no hash was calculated
- Approximate runtime interval from remote file timestamps: `01:17:04–01:17:24 +08:00`
- DevEdit elapsed line: `18.05 s`
- Exit code: `11`

## 3. Runtime sequence and failure point

DevEdit accepted all 12 region statements and reached the relocated two-axis constraint:

```silvaco
constr.mesh x1=10.10 y1=0.0 x2=10.40 y2=0.6 \
  max.width=0.016 max.height=0.016
Mesh Mode=MeshBuild
```

The initial MeshBuild completed and printed an intermediate mesh of 2,332 points, 4,557
triangles, and 0 obtuse triangles. Those figures are **not** final STR metrics: the packet
then entered its inherited sequence of local `refine` cards. It crashed while executing:

```silvaco
refine mode=x x1=4.18 y1=-0.1377 x2=13.89 y2=0.5819
```

The transcript stopped after `Creating list... done.` and during `Refining...`. The kernel
log records the corresponding `devedit.exe` segmentation fault. No explicit `Parse Error`,
`Parse complete`, or literal `fatal` message preceded the crash.

## 4. Warning and failure accounting

- Four `Material WARNING` transcript lines were retained: two after region 3 and two after
  region 6. They did not stop execution.
- The runner recorded `simExited with exitcode11` and `simulator exits with code 11`.
- `deckbuild_log.txt` is zero bytes; the full PTY evidence is in `typescript.txt`.
- The expected output `OFAT_A_bv_devedit_mesh_x10p25.str` is absent.

## 5. Contract adjudication

| Item | Original A1 | A1_REV2 actual | REV2 result |
|---|---:|---:|---|
| final STR | created | not created | FAIL |
| nodes | 5,045 | `NOT_AVAILABLE` | `NOT_EVALUABLE` |
| triangles | 9,802 | `NOT_AVAILABLE` | `NOT_EVALUABLE` |
| obtuse | 0 | `NOT_AVAILABLE` | `NOT_EVALUABLE` |
| region count | 12 | `NOT_EVALUABLE` | `NOT_EVALUABLE` |
| electrode count | 3 | `NOT_EVALUABLE` | `NOT_EVALUABLE` |
| stepped-gate topology | PASS | `NOT_EVALUABLE` | `NOT_EVALUABLE` |
| max Δx in track ROI | 0.3125 µm | `NOT_AVAILABLE` | FAIL: no STR |
| max Δy in track ROI | 0.0250 µm | `NOT_AVAILABLE` | FAIL: no STR |
| full-y continuity | PASS | `NOT_EVALUABLE` | FAIL: no STR |

The mesh contract remains unchanged: actual max Δx and Δy must both be no greater than
0.016 µm and full-y continuity must pass. A1_REV2 fails the runtime gate because it did not
produce the STR required to make those measurements. This is distinct from a measured
spacing failure.

## 6. Missing artifacts are not fabricated

No final STR means that the following requested artifacts do not exist:

- actual structure image;
- actual mesh image;
- final nodes/triangles/obtuse statistics;
- final region/electrode table;
- actual ROI Δx/Δy table;
- actual full-y continuity result.

The repository contains explicit `NOT_AVAILABLE` rows instead of placeholders or values
copied from A1. The complete transcript and the crash evidence are preserved.

## 7. Scope compliance and stop state

After the crash there was no exact tmux session and no `deckbuild`, `dbascii.exe`,
`devedit.exe`, or `atlas` process. The authorized execution count is exhausted.

```text
A2_EXECUTED = NO
ATLAS_EXECUTED = NO
STATIC_BIAS_EXECUTED = NO
SEU_TRANSIENT_EXECUTED = NO
PAIRED_TRANSIENT_EXECUTED = NO
AUTO_FIX_PERFORMED = NO
```

## 8. Open gates and recommendation

1. A1_REV2 mesh contract is failed because the required final STR was not created.
2. The previous hypothesis that relocating the constraint alone closes the A1 spacing gap
   remains runtime-unconfirmed.
3. The interaction between the denser initial MeshBuild and the inherited later refinement
   sequence is now a concrete repair candidate, not an authorized change.
4. A2 remains denied.

Recommendation:
`STOP_FOR_WEB_REVIEW / DO_NOT_AUTHORIZE_A2 / THIRD_REPAIR_REQUIRES_NEW_PLAN_AND_AUTHORIZATION`.
