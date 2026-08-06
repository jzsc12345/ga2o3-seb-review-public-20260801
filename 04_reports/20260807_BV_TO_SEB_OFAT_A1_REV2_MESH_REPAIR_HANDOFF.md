# BV→SEB OFAT A1_REV2 mesh-repair handoff

> Status: `PREPARED_NOT_RUNTIME_VALIDATED`
> Packet: `DERIVED_MESH_REPAIR_PACKET / A1_REV2_ONLY`
> Source runtime evidence commit: `43591ade734d4568a927f71bcc3ed8b46b875bc6`

## 1. Result first

A1 structure and terminal topology remain accepted. The track-mesh contract failed because the new rectangle constraint was declared after the only `MeshBuild`; it therefore did not participate in mesh construction. A1_REV2 moves the unchanged two-axis constraint immediately before the existing MeshBuild. No other executable value is changed.

```text
ORIGINAL_A1_UNCHANGED = YES
A1_REV2_STATUS = NOT_RUNTIME_VALIDATED
CONTRACT_CHANGED = NO
EXECUTION_PERFORMED = NO
A2_AUTHORIZATION = DENIED
```

## 2. Evidence for the root cause

| Evidence | Finding |
|---|---|
| A1 actual STR metrics | max Δx `0.3125 µm`, max Δy `0.0250 µm`, continuity PASS |
| A1 packet order | `Mesh Mode=MeshBuild` precedes the new track `constr.mesh` |
| DevEdit manual p.89 | rectangle `constr.mesh` supports x/y bounds and max width/height |
| DevEdit manual p.104 | `MESH` uses previously set parameters and applies mesh constraints during mesh construction |
| executed RUN227 | rectangle constraints placed before MeshBuild; measured max Δx `0.015625 µm` |

The evidence supports an ordering failure, not a failure of the `max.width/max.height` syntax.

## 3. Repair packet

Packet:
[OFAT_A1_REV2_devedit_track_mesh_packet.in](attachments/20260806_bv_to_seb_ofat/a1_rev2_mesh_repair_20260807/packets/OFAT_A1_REV2_devedit_track_mesh_packet.in)

Complete diff:
[OFAT_A1_to_A1_REV2_complete.diff](attachments/20260806_bv_to_seb_ofat/a1_rev2_mesh_repair_20260807/diffs/OFAT_A1_to_A1_REV2_complete.diff)

The same statement is relocated:

```silvaco
constr.mesh x1=10.10 y1=0.0 x2=10.40 y2=0.6 \
  max.width=0.016 max.height=0.016
Mesh Mode=MeshBuild
```

## 4. Contract and expected layout

```text
ROI = x=10.10..10.40 um, y=0.00..0.60 um
actual max Δx <= 0.016 um
actual max Δy <= 0.016 um
full-y continuity = PASS
```

Expected minimum interval counts are 19 across x and 38 through y. This is an expectation only; runtime acceptance still requires the same STR-based measurement used for A1.

## 5. Scope proof

[Mesh-only change proof](attachments/20260806_bv_to_seb_ofat/a1_rev2_mesh_repair_20260807/A1_REV2_MESH_ONLY_CHANGE_PROOF.md)

[DevEdit syntax provenance](attachments/20260806_bv_to_seb_ofat/a1_rev2_mesh_repair_20260807/A1_REV2_DEVEDIT_SYNTAX_PROVENANCE.md)

[Expected layout and risks](attachments/20260806_bv_to_seb_ofat/a1_rev2_mesh_repair_20260807/A1_REV2_EXPECTED_LAYOUT_AND_RISK.md)

[Forbidden-command scan](attachments/20260806_bv_to_seb_ofat/a1_rev2_mesh_repair_20260807/A1_REV2_FORBIDDEN_COMMAND_SCAN.md)

## 6. Required labels and execution boundary

```text
DERIVED_MESH_REPAIR_PACKET
NOT_RUNTIME_VALIDATED
A1_REV2_ONLY
NO A2
NO ATLAS
NO STATIC_BIAS
NO SEU TRANSIENT
NO AUTOMATIC_EXPANSION_OF_AUTHORIZATION
```

This handoff does not authorize SSH, upload, DeckBuild, DevEdit, ATLAS, A1 rerun, A2/A3/B1/B2, 300 V static, or transient execution.

## 7. Open gates

1. Web-side review of the packet and full diff.
2. Separate one-time A1_REV2-only execution authorization, if approved.
3. Generated STR verification using the unchanged max Δx/max Δy/full-y contract.
4. A2 remains denied until A1_REV2 runtime evidence passes and receives a new review.

## 8. Recommended next action

`REVIEW_A1_REV2_PACKET_THEN_AUTHORIZE_ONE_TIME_DEVEDIT_ONLY_IF_ACCEPTED`.

No automatic execution follows this document or its publication.
