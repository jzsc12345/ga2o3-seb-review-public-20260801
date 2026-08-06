# Victory Mesh SEB material-identity lineage handoff

> Status: `READ_ONLY_AUDIT_COMPLETE / FIRST_LOSS_LOCALIZED / PLAN_ONLY_CANDIDATE_PREPARED`
> Evidence baseline: frozen public evidence commit `b14447247afba64afb1e5bc57663851ac30fa6c2`
> Scope: DevEdit raw STR → Victory Mesh load/save → ATLAS import identity only
> Trust: `LEGACY_BENCHMARK_ONLY / NOT_PRODUCTION_QUALIFIED_SEB`

## 1. Executive decision

The frozen conformal geometry and mesh remain valid. The first directly observed material-class failure for both target semiconductors is the **ATLAS import interpretation**, not the DevEdit export or Victory Mesh load:

| Material | Raw DevEdit STR | Victory LOAD / Atlas-mode STR | ATLAS 5.40 import | First loss |
|---|---|---|---|---|
| Ga₂O₃ | code 50, label `Ga2O3` | identity retained as `ga2o3`, code 50 | Silicon/semiconductor | `ATLAS_IMPORT_INTERPRETATION` |
| NiO | code 51, label `NiO` | identity retained at load; saved as canonical SMDB code 304 | `Unknown material #304` → SiO₂/insulator | `ATLAS_IMPORT_INTERPRETATION` |

Post-import material reclassification has already failed and is not proposed again.

## 2. User-requested UD-label check

The exact requested DevEdit forms are `UD1(BetaGa2O3)` and `UD2(NiOx)`. These wrappers can carry custom labels, so absence from the dictionary does not prove that DevEdit will reject the syntax. It does mean the inner strings are not canonical identities recognized across the installed tools.

The requested spelling experiment was resolved by official local dictionaries without executing it:

| String | Official local result | Use in candidate |
|---|---|---|
| `BetaGa2O3` | no exact SMDB/ATLAS entry | NO |
| `Beta-Ga2O3` | official SMDB name, code 259; absent from ATLAS Table B-1 | NO—valid SMDB identity is not ATLAS-import proof |
| `NiOx` | no exact SMDB/ATLAS entry | NO |
| `NiO` | official SMDB name, code 304; absent from ATLAS Table B-1 and already failed runtime import | NO |

The two-line label-only hypothesis is preserved verbatim in the attachment audit. It is not executed and is not promoted above the evidence-backed frozen-mesh resave candidate, because no official evidence shows that changing only the UD labels changes the downstream material codes/classes.

## 3. Material lineage

The complete machine-readable table is [MATERIAL_IDENTITY_LINEAGE.csv](attachments/20260807_victorymesh_material_identity_lineage/MATERIAL_IDENTITY_LINEAGE.csv).

Key observations:

1. semantic region geometry, doping, source/drain/gate names, and the single stepped gate survive the conformal route;
2. SiO₂, Al₂O₃, and Nickel import correctly;
3. Ga₂O₃ and NiO fail only when ATLAS assigns runtime material identities;
4. NiO's Q-label degrades to `0` at Atlas-mode save, but code 304 is still the official current SMDB NiO code; the first demonstrated wrong class remains the ATLAS import stage.

## 4. Official mechanisms found

### 4.1 Victory Mesh

Victory Mesh 1.12.0.R User's Manual §7.5 documents `MATERIAL REGIONS=... VALUE=...`. Section 11.62 documents `SAVE MODE=ATLAS`, which adjusts format flags but exposes no material-mapping parameter.

### 4.2 ATLAS

ATLAS 5.40.0.R User's Manual §B.2.4 says imported materials outside Table B-1 become insulators. Section B.2.5 documents `USER.MATERIAL/USER.GROUP/USER.DEFAULT` for user-defined materials, but the existing runtime evidence proves those post-import cards do not repair already misclassified imported records.

ATLAS Table B-1 includes `GaN` and `ZnO`; it excludes `Beta-Ga2O3` and `NiO`.

## 5. Sole nonexecuted candidate

`RECOMMENDED_FIX_LAYER = C. VICTORY_SAVE_MODE_ATLAS_MAPPING_FIX`

The sole candidate is [VICTORYMESH_ATLAS_PARENT_MAPPING_RESAVE_CANDIDATE.in](attachments/20260807_victorymesh_material_identity_lineage/VICTORYMESH_ATLAS_PARENT_MAPPING_RESAVE_CANDIDATE.in), with its [full add-file diff](attachments/20260807_victorymesh_material_identity_lineage/VICTORYMESH_ATLAS_PARENT_MAPPING_RESAVE_CANDIDATE_FULL.diff).

It proposes:

- load the existing frozen conformal STR;
- no remesh;
- map Ga₂O₃ semantic regions to ATLAS-recognized semiconductor parent `GaN`;
- map NiO semantic regions to ATLAS-recognized semiconductor parent `ZnO`;
- resave once with `MODE=ATLAS`;
- stop.

The parent names are an **import-identity transport mechanism only**. They do not authorize GaN/ZnO physical defaults, and do not validate any SEB physics. Explicit Ga₂O₃/NiO parameters would remain a separate later gate.

`REMESH_REQUIRED = NO`
`RESAVE_REQUIRED = YES`

## 6. Fixed mesh evidence

The existing conformal mesh is not reopened:

| Metric | Frozen value |
|---|---:|
| Nodes | 56,454 |
| Triangles | 111,350 |
| Obtuse | 0 |
| Track max Δx | 0.015 µm |
| Track max Δy | 0.0166667 µm |
| Full-y continuity | PASS |

## 7. Attachments

1. [MATERIAL_IDENTITY_LINEAGE.csv](attachments/20260807_victorymesh_material_identity_lineage/MATERIAL_IDENTITY_LINEAGE.csv)
2. [DEVEDIT_RAW_VS_VICTORY_STR_MATERIAL_DIFF.md](attachments/20260807_victorymesh_material_identity_lineage/DEVEDIT_RAW_VS_VICTORY_STR_MATERIAL_DIFF.md)
3. [VICTORYMESH_ATLAS_MATERIAL_MAPPING_MANUAL_AUDIT.md](attachments/20260807_victorymesh_material_identity_lineage/VICTORYMESH_ATLAS_MATERIAL_MAPPING_MANUAL_AUDIT.md)
4. [ATLAS_MASTER_MATERIAL_CODE_AUDIT.md](attachments/20260807_victorymesh_material_identity_lineage/ATLAS_MASTER_MATERIAL_CODE_AUDIT.md)
5. [FIRST_LOSS_DECISION.md](attachments/20260807_victorymesh_material_identity_lineage/FIRST_LOSS_DECISION.md)
6. [VICTORYMESH_ATLAS_PARENT_MAPPING_RESAVE_CANDIDATE.in](attachments/20260807_victorymesh_material_identity_lineage/VICTORYMESH_ATLAS_PARENT_MAPPING_RESAVE_CANDIDATE.in)
7. [VICTORYMESH_ATLAS_PARENT_MAPPING_RESAVE_CANDIDATE_FULL.diff](attachments/20260807_victorymesh_material_identity_lineage/VICTORYMESH_ATLAS_PARENT_MAPPING_RESAVE_CANDIDATE_FULL.diff)

Previous runtime evidence remains at [VictoryMesh Stage-2 → ATLAS material mapping / solve-init stop handoff](20260807_VICTORYMESH_SEB_ATLAS_MATERIAL_INIT_REV1_STOP_HANDOFF.md).

## 8. Authorization boundary

Confirmed not executed in this task:

- DevEdit;
- Victory Mesh;
- ATLAS;
- solve init;
- remesh or resave;
- 300 V;
- SEU/SET/SEB or any transient;
- automatic fallback.

The candidate is `NONEXECUTED_PLAN_ONLY / NOT_RUNTIME_VALIDATED`. It must be reviewed before any resave authorization.

## 9. Open gates and recommendation

Open gates:

1. web review of the one-candidate Victory-side parent mapping;
2. web decision on whether the lower-priority `UD1(BetaGa2O3)`/`UD2(NiOx)` label-only OFAT deserves a separate future packet;
3. whether `MATERIAL:GA2O3` and `MATERIAL:NIO` resolve correctly after loading the frozen conformal SDB;
4. separately authorized resave-only evidence, if approved;
5. separately authorized ATLAS zero-bias import table/solve-init after a successful resave;
6. proof that explicit Ga₂O₃/NiO physics binds without unapproved parent-default leakage;
7. independent OUTPUT contact `-999` warning;
8. 300 V and all transients remain denied.

`NEXT_RECOMMENDATION = WEB_REVIEW_NONEXECUTED_RESAVE_CANDIDATE`

## 10. Required result-field mirror

```text
STATUS: READ_ONLY_AUDIT_COMPLETE / FIRST_LOSS_LOCALIZED / PLAN_ONLY_CANDIDATE_PREPARED
GA2O3_FIRST_LOSS_STAGE: ATLAS_IMPORT_INTERPRETATION
NIO_FIRST_LOSS_STAGE: ATLAS_IMPORT_INTERPRETATION
RAW_DEVEDIT_GA2O3_ID: code 50 / label Ga2O3
RAW_DEVEDIT_NIO_ID: code 51 / label NiO
VICTORY_GA2O3_ID: code 50 / label ga2o3
VICTORY_NIO_ID: code 304 / current SMDB identity NiO / Q-label 0
ATLAS_GA2O3_INTERPRETATION: Silicon / semiconductor
ATLAS_NIO_INTERPRETATION: SiO2 / insulator after Unknown material #304
CODE50_MEANING: DevEdit user-material code labeled Ga2O3; no current SMDB m50 entry; not an ATLAS Ga2O3 identity
CODE304_MEANING: current SMDB NiO; rejected as unknown by tested ATLAS 5.40 SDB import
OFFICIAL_ATLAS_MAPPING_MECHANISM: USER.MATERIAL + USER.GROUP + USER.DEFAULT for Atlas-defined user materials; not a proven post-import repair here
OFFICIAL_VICTORY_MAPPING_MECHANISM: MATERIAL REGIONS=... VALUE=... before SAVE MODE=ATLAS
REMESH_REQUIRED: NO
RESAVE_REQUIRED: YES
RECOMMENDED_FIX_LAYER: C. VICTORY_SAVE_MODE_ATLAS_MAPPING_FIX
RECOMMENDED_NONEXECUTED_CANDIDATE: VICTORYMESH_ATLAS_PARENT_MAPPING_RESAVE_CANDIDATE.in
ATLAS_EXECUTED: NO
VICTORYMESH_EXECUTED: NO
DEVEDIT_EXECUTED: NO
OPEN_GATES: selector binding; resave-only proof; ATLAS zero-bias import; explicit physics binding; OUTPUT -999; 300 V; all transients
NEXT_RECOMMENDATION: WEB_REVIEW_NONEXECUTED_RESAVE_CANDIDATE
```
