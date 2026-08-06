# VictoryMesh Stage-2 → ATLAS material mapping / solve-init stop handoff

> Status: `MATERIAL_MAPPING_HARD_FAIL / STOPPED_AFTER_ONE_AUTHORIZED_SOLVE_INIT`  
> Scope: material mapping + zero-bias `solve init` only  
> Trust boundary: `LEGACY_BENCHMARK_ONLY / NOT_PRODUCTION_QUALIFIED_SEB`

## 1. Fixed scope

The run used the already generated VictoryMesh Stage-2 STR. It did **not** run Victory Mesh, DevEdit, 300 V bias, or any transient. The single active solve was `solve init`; one equilibrium STR was saved; no retry or fallback was used.

## 2. Inputs

- Frozen STR: `/root/DECKBUILD/preflight/VICTORYMESH_SEB_STAGE2_CONFORMAL_X10P25_20260807/VM_SEB_STAGE2_conformal_track_x10p25.str`
- Candidate deck: [PREFLIGHT_VICTORYMESH_SEB_STAGE2_ATLAS_MATERIAL_INIT_REV1.in](attachments/20260807_victorymesh_atlas_material_init_rev1/PREFLIGHT_VICTORYMESH_SEB_STAGE2_ATLAS_MATERIAL_INIT_REV1.in)
- Predecessor-to-REV1 full diff: [PREDECESSOR_TO_REV1_FULL.txt](attachments/20260807_victorymesh_atlas_material_init_rev1/PREDECESSOR_TO_REV1_FULL.txt)
- Semantic/runtime mapping prepared before launch: [semantic_runtime_region_map.csv](attachments/20260807_victorymesh_atlas_material_init_rev1/semantic_runtime_region_map.csv)
- Region-sensitive statement audit: [region_number_sensitive_audit.csv](attachments/20260807_victorymesh_atlas_material_init_rev1/region_number_sensitive_audit.csv)

## 3. Environment and one execution

- SSH alias: `silvaco`
- Runtime host: `tcad`
- Workdir: `/root/DECKBUILD/preflight/VICTORYMESH_SEB_ATLAS_MATERIAL_INIT_REV1_20260807`
- Runner: `/root/bin/vdoe_tmux.sh start-deck`
- tmux: `deck_PREFLIGHT_VICTORYMESH_SEB_STAGE2_ATLAS_MATERIAL_INIT_REV1`
- ATLAS: `5.40.0.R`
- Printed elapsed time: `39.17 s`
- Launch count: `1`

The complete terminal transcript is [typescript.txt](attachments/20260807_victorymesh_atlas_material_init_rev1/typescript.txt).

## 4. Mechanical import result

| Item | Runtime result |
|---|---:|
| Nodes | 56,454 |
| Triangles | 111,350 |
| Runtime region records | 13 |
| Electrodes | 3 |
| Source/drain/gate bias at import | 0 / 0 / 0 V |
| Source/drain/gate names | preserved |

The 13 runtime records still correspond to 12 semantic regions because the oxide has two disconnected components.

## 5. Material result — hard failure

ATLAS printed this runtime material table:

| Runtime record | Semantic identity | Printed material/type | Verdict |
|---:|---|---|---|
| 1 | substrate Ga₂O₃ | Silicon / semiconductor | FAIL |
| 2 | UID Ga₂O₃ | Silicon / semiconductor | FAIL |
| 3 | channel Ga₂O₃ | Silicon / semiconductor | FAIL |
| 4 | oxide component A | SiO₂ / insulator | PASS |
| 5 | oxide component B | SiO₂ / insulator | PASS |
| 6 | source n+ Ga₂O₃ | Silicon / semiconductor | FAIL |
| 7 | n_d Ga₂O₃ | Silicon / semiconductor | FAIL |
| 8 | Al₂O₃ | Al₂O₃ / insulator | PASS |
| 9 | p− NiO, code 304 | SiO₂ / insulator | FAIL |
| 10 | p+ NiO, code 304 | SiO₂ / insulator | FAIL |
| 11 | source | Nickel / metal | PASS |
| 12 | drain | Nickel / metal | PASS |
| 13 | stepped gate | Nickel / metal | PASS |

The machine-readable table is [runtime_region_material_table.csv](attachments/20260807_victorymesh_atlas_material_init_rev1/runtime_region_material_table.csv).

### 5.1 Code 304

The imported code-304 cells emitted 2,228 `Unknown material #304` warnings and 2,228 `Using insulator` messages. Runtime records 9/10 are the semantic NiO records, but their imported material state is already SiO₂/insulator.

### 5.2 Region-scoped NiO cards

Both cards reached runtime records 9/10, but ATLAS replied for each:

- `Cannot change default material parameters for material "SiO2"`;
- `Ignoring default material parameters specification`;
- `Cannot change material group ...`;
- `Ignoring material group specification`.

The numeric values changed some fallback-insulator table fields, but the records remained SiO₂/insulator. This does **not** establish NiO semiconductor physics.

### 5.3 Ga₂O₃

The material-name card did not bind the imported Ga₂O₃ lineage to the intended explicit Ga₂O₃ parameters. Records 1/2/3/6/7 print as Silicon, retain printed permittivity 11.8, and use built-in Silicon mobility ancestry. `GA2O3_BETA_RESULT = FAIL_NOT_BOUND`.

## 6. Old `MATERIAL region=10 mun=50`

The removal was correct and is not the cause of this failure. In original `bv.in`, semantic region 10 was the thick Nickel source. After VictoryMesh import, runtime record 10 is the p+ NiO/code-304 fallback record. Blindly carrying the old numeric card forward would silently retarget a stale metal-region override onto the wrong semantic material.

## 7. Parser, METHOD and solve-init

- Parser/fatal errors: `0`
- METHOD syntax errors: `0`
- Final METHOD: `newton trap maxtraps=10 climit=1e-4 weak=1 itlimit=50`
- `Cannot trap`: `0`
- `solve init`: numerically completed
- equilibrium STR: created, 42,540,868 bytes remotely and archived at `E:\silvaco2425\bulk\str\VM_SEB_STAGE2_ATLAS_material_init_rev1_equilibrium.str`

This numerical completion is **physically inadmissible** because the core Ga₂O₃/NiO material identities were not established.

The OUTPUT card also emitted one `Contact number given (-999) is out of range` warning. It is an independent output-contract open gate and was not modified or retried.

## 8. Warning register and evidence

- [runtime_warning_register.csv](attachments/20260807_victorymesh_atlas_material_init_rev1/runtime_warning_register.csv)
- [ATLAS_STATIC_INPUT_REV1_AUDIT.md](attachments/20260807_victorymesh_atlas_material_init_rev1/ATLAS_STATIC_INPUT_REV1_AUDIT.md)
- [MANUAL_EXAMPLE_EVIDENCE_INDEX.md](attachments/20260807_victorymesh_atlas_material_init_rev1/MANUAL_EXAMPLE_EVIDENCE_INDEX.md)
- [RESULT.md](attachments/20260807_victorymesh_atlas_material_init_rev1/RESULT.md)
- [EXECUTION_SCOPE_CONFIRMATION.md](attachments/20260807_victorymesh_atlas_material_init_rev1/EXECUTION_SCOPE_CONFIRMATION.md)

## 9. Stop boundary

Confirmed not executed:

- Victory Mesh / DevEdit;
- any VDS or VGS bias;
- 300 V;
- SEU/SET/SEB;
- paired transient;
- second launch;
- auto-fix/fallback.

## 10. Open gates and recommendation

Open gates:

1. establish a documented import-time mapping for VictoryMesh custom materials so Ga₂O₃ and NiO arrive in ATLAS with correct material identities/groups;
2. prove the Ga₂O₃ explicit parameter card binds to records 1/2/3/6/7;
3. eliminate code-304 fallback without post-import reclassification;
4. resolve the OUTPUT contact `-999` warning separately.

Recommendation: prepare a **new plan-only import-boundary material mapping experiment**. The next executable test, if separately authorized, must remain one zero-bias `solve init`; do not proceed to 300 V or transient until the runtime table shows Ga₂O₃ and NiO correctly.
