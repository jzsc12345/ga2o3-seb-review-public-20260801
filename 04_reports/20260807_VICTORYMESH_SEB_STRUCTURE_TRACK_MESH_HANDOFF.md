# Victory Mesh SEB structure/track mesh — fixed review handoff

> Final status: `STAGE1_PASS / STAGE2_MESH_CONTRACT_HARD_FAIL / STOPPED`
>
> Mesher: `Victory Mesh Conformal`
>
> Scope: structure and mesh only; no ATLAS, static bias or particle transient.

## 1. Decision first

The task's Stage 1 gate passed. `str.txt` was generated through DevEdit, loaded by Victory Mesh,
remeshed with `REMESH CONFORMAL`, and saved with `MODE=ATLAS`. The generated baseline STR retains
12 semantic regions, three electrodes, one continuous thick Nickel stepped gate, original impurity
fields and material/interface geometry.

Stage 2 completed mechanically but **fails the unchanged two-dimensional track-mesh contract**:

```text
actual max Δx = 0.0150000000 µm  <= 0.016 µm  PASS
actual max Δy = 0.0166666667 µm  >  0.016 µm  FAIL
full-y continuity = PASS
```

Therefore no parameter was adjusted, no fallback was selected, no rerun was made, and ATLAS was not
entered. A normal simulator exit is not being misreported as contract success.

## 2. User correction and frozen route

The user corrected the earlier recollection: there is no need to find an R-prefixed mesher; the
intended route is **Conformal**. The only executed route was:

```text
DevEdit structure
  -> Victory Mesh LOAD
  -> LINE X / LINE Y device grid
  -> REMESH CONFORMAL
  -> SAVE MODE=ATLAS
```

No Delaunay, R-tree, regular, custom or automatic fallback was executed.

## 3. Inputs and derived decks

Original attachments, copied without modification for review:

- [formal task](attachments/20260807_victorymesh_seb_structure_track/source/CODEX_TASK_VICTORYMESH_SEB.md)
- [unique structure master `str.txt`](attachments/20260807_victorymesh_seb_structure_track/source/str.txt)
- [workflow reference `changban3(1).in`](attachments/20260807_victorymesh_seb_structure_track/source/changban3%281%29.in)

Derived decks:

- [Stage 1 baseline deck](attachments/20260807_victorymesh_seb_structure_track/decks/PREFLIGHT_VICTORYMESH_SEB_STAGE1_conformal_baseline.in)
- [Stage 2 track deck](attachments/20260807_victorymesh_seb_structure_track/decks/PREFLIGHT_VICTORYMESH_SEB_STAGE2_conformal_x10p25.in)
- [source-to-Stage-1 complete diff](attachments/20260807_victorymesh_seb_structure_track/diffs/str_to_stage1_complete.diff)
- [Stage-1-to-Stage-2 complete diff](attachments/20260807_victorymesh_seb_structure_track/diffs/stage1_to_stage2_complete.diff)

The original `str.txt` and `changban3(1).in` were not edited.

## 4. Manual, examples and exact command family

The exact mesh statements were:

```silvaco
line x location=<geometry or track plane> spacing=<requested spacing>
line y location=<geometry/interface plane> spacing=<requested spacing>
remesh conformal
save out=<final.str> mode=atlas
```

Evidence is recorded in
[MANUAL_AND_EXAMPLE_EVIDENCE.md](attachments/20260807_victorymesh_seb_structure_track/MANUAL_AND_EXAMPLE_EVIDENCE.md).
The local manual establishes `LINE`, `REMESH CONFORMAL` and `SAVE MODE=ATLAS`; three local installed
examples establish the executable lineage. `changban3(1).in` was not used as a source of device or
mesh values.

## 5. Runtime environment and commands

- SSH alias: `silvaco`
- VM host: `tcad`
- runner: `/root/bin/vdoe_tmux.sh start-deck`
- DeckBuild: `5.2.40.R`
- DevEdit: `2.8.26.R`
- Victory Mesh: `1.12.0.R`

Stage 1 remote directory:
`/root/DECKBUILD/preflight/VICTORYMESH_SEB_STAGE1_CONFORMAL_20260807`

Stage 2 remote directory:
`/root/DECKBUILD/preflight/VICTORYMESH_SEB_STAGE2_CONFORMAL_X10P25_20260807`

Both logs show `remesh conformal`, `save ... mode=atlas`, `quit`, and Victory Mesh natural finish.
Full transcripts are linked in §9.

## 6. Stage 1 result

| Item | Actual result | Gate |
|---|---:|---|
| points | 38,359 | report |
| triangles | 75,458 | report |
| obtuse | 0 | PASS |
| semantic regions | 12 | PASS |
| runtime region records | 13 | explained: semantic SiO2 region 4 has two disconnected components |
| electrodes | 3 | PASS |
| thick stepped gate | preserved | PASS |
| ATLAS-compatible STR | created | PASS |

Bulk paths:

- raw DevEdit STR: `E:\silvaco2425\bulk\str\VICTORYMESH_SEB_20260807\VM_SEB_STAGE1_devedit_raw.str`
- final STR: `E:\silvaco2425\bulk\str\VICTORYMESH_SEB_20260807\VM_SEB_STAGE1_conformal_baseline.str`

## 7. Stage 2 result and hard stop

Fixed ROI: `x=10.10–10.40 µm`, `y=0.00–0.60 µm`; `xion=10.25 µm`, `r=0.05 µm`.

| Item | Actual result | Gate |
|---|---:|---|
| points | 56,454 | report |
| triangles | 111,350 | report |
| obtuse | 0 | PASS |
| semantic regions | 12 | PASS |
| electrodes | 3 | PASS |
| thick stepped gate | preserved | PASS |
| max Δx | 0.0150000000 µm | PASS |
| max Δy | **0.0166666667 µm** | **FAIL** |
| full-y continuity | PASS; merged interval `[0.0, 0.6]` | PASS |

The worst y interval lies in the channel near `y=0.1833333–0.2000000 µm`. The input requested
`spacing=0.015`, but the acceptance criterion is based on the generated STR, not the requested
spacing. The measured `0.0166667 µm` therefore controls the verdict.

Bulk paths:

- raw DevEdit STR: `E:\silvaco2425\bulk\str\VICTORYMESH_SEB_20260807\VM_SEB_STAGE2_devedit_raw.str`
- final STR: `E:\silvaco2425\bulk\str\VICTORYMESH_SEB_20260807\VM_SEB_STAGE2_conformal_track_x10p25.str`

## 8. Preservation audit

Stage 1 and Stage 2 final STR tables have the same region areas, bounding boxes, material codes,
impurity ranges and electrode ids. Only mesh triangle counts change. In particular:

- source, drain and gate remain Nickel electrodes 1, 2 and 3;
- there is no independent `gate_fp`;
- the stepped gate remains one continuous thick region with area `0.235 µm²`;
- all original Ga2O3 and NiO donor/acceptor fields remain represented;
- the semantic region count is 12; Victory Mesh serializes the disconnected oxide components as
  two runtime region records, producing 13 runtime records without adding a semantic device region.

Detailed tables:

- [Stage 1 regions](attachments/20260807_victorymesh_seb_structure_track/stage1/csv/VM_SEB_STAGE1_regions.csv)
- [Stage 2 regions](attachments/20260807_victorymesh_seb_structure_track/stage2/csv/VM_SEB_STAGE2_regions.csv)

## 9. Evidence index

Main evidence:

- [full result](attachments/20260807_victorymesh_seb_structure_track/RESULT.md)
- [artifact index](attachments/20260807_victorymesh_seb_structure_track/ARTIFACT_INDEX.md)
- [warning/fatal register](attachments/20260807_victorymesh_seb_structure_track/WARNING_FATAL_REGISTER.md)
- [read-only STR analyzer](attachments/20260807_victorymesh_seb_structure_track/scripts/analyze_victorymesh_seb_str.py)

Stage 1:

- [complete transcript](attachments/20260807_victorymesh_seb_structure_track/stage1/logs/typescript.log)
- [actual structure](attachments/20260807_victorymesh_seb_structure_track/stage1/figs/VM_SEB_STAGE1_A14_actual_structure.png)
- [actual mesh](attachments/20260807_victorymesh_seb_structure_track/stage1/figs/VM_SEB_STAGE1_A14_actual_mesh.png)
- [summary JSON](attachments/20260807_victorymesh_seb_structure_track/stage1/csv/VM_SEB_STAGE1_summary.json)
- [ROI triangle data](attachments/20260807_victorymesh_seb_structure_track/stage1/csv/VM_SEB_STAGE1_roi_triangles.csv)

Stage 2:

- [complete transcript](attachments/20260807_victorymesh_seb_structure_track/stage2/logs/typescript.log)
- [actual structure](attachments/20260807_victorymesh_seb_structure_track/stage2/figs/VM_SEB_STAGE2_A14_actual_structure.png)
- [actual mesh](attachments/20260807_victorymesh_seb_structure_track/stage2/figs/VM_SEB_STAGE2_A14_actual_mesh.png)
- [summary JSON](attachments/20260807_victorymesh_seb_structure_track/stage2/csv/VM_SEB_STAGE2_summary.json)
- [ROI triangle data](attachments/20260807_victorymesh_seb_structure_track/stage2/csv/VM_SEB_STAGE2_roi_triangles.csv)

Large STRs remain in the bulk paths recorded above; they were not duplicated into GitHub. All
reported mesh metrics derive from those actual STRs.

## 10. Authorization boundary and final state

```text
VICTORYMESH_STRUCTURE_MESH_ONLY
ATLAS_EXECUTED = NO
STATIC_BIAS_EXECUTED = NO
SEU_TRANSIENT_EXECUTED = NO
PAIRED_TRANSIENT_EXECUTED = NO
AUTO_FALLBACK_USED = NO
STAGE2_RERUN = NO
```

## 11. Open gate and recommendation

Only the Stage 2 y-spacing contract remains failed. A future action, if separately reviewed and
authorized, should be a new Conformal mesh-only candidate with a conservative requested y spacing
below `0.015 µm`, followed by one fresh real-STR measurement. This handoff does **not** authorize or
implement that candidate.

Recommendation:

`STOP_FOR_WEB_REVIEW / REVISE_STAGE2_Y_DEVICE_GRID_BEFORE_ANY_ATLAS_OR_SEB`.
