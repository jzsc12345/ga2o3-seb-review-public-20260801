# A1_REV2 mesh-only change proof

> Status: `DERIVED_MESH_REPAIR_PACKET / NOT_RUNTIME_VALIDATED`
> Scope: static text comparison only; no DevEdit, DeckBuild, ATLAS, SSH, or VM action.

## Source and candidate

- Original A1: `stage_packets_20260807/packets/OFAT_A1_devedit_structure_mesh_packet.in`
- Repair candidate: `packets/OFAT_A1_REV2_devedit_track_mesh_packet.in`
- Fixed A1 evidence commit: `43591ade734d4568a927f71bcc3ed8b46b875bc6`

The original A1 file remains unchanged. A1_REV2 is a new derived packet.

## Only executable change

The following logical DevEdit statement is byte-for-byte unchanged:

```silvaco
constr.mesh x1=10.10 y1=0.0 x2=10.40 y2=0.6 \
  max.width=0.016 max.height=0.016
```

Its location changes from **after** the existing `Mesh Mode=MeshBuild` and inherited `refine` sequence to immediately **before** that same existing MeshBuild statement.

No second `MeshBuild` is added. No mesh value, coordinate, geometry, region, electrode, impurity, material, mobility, impact, thermal, solver, output, or structure filename is changed.

## Comment-only changes

The header gains the required labels and one sentence describing the mesh-only repair. One adjacent comment states why the constraint must precede MeshBuild. Comments have no executable effect.

## Complete proof surface

The complete unified diff is `diffs/OFAT_A1_to_A1_REV2_complete.diff`. It contains exactly three hunks:

1. required comment labels;
2. insertion of the unchanged track constraint before MeshBuild;
3. deletion of the same constraint from its ineffective late position.

All original 12 region statements, thick Nickel polygons, three electrode declarations, inherited mesh statements, and the final `structure outf=OFAT_A_bv_devedit_mesh_x10p25.str` remain present.

## Contract

```text
TARGET_ROI = x=10.10..10.40 um, y=0.00..0.60 um
MAX_DX = 0.016 um
MAX_DY = 0.016 um
FULL_Y_CONTINUITY = REQUIRED
CONTRACT_CHANGED = NO
```

These are acceptance requirements, not claimed runtime results.
