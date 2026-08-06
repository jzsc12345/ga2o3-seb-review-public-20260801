# First material-identity loss decision

## Verdict

| Material | First observed wrong interpretation | Evidence-backed first-loss stage |
|---|---|---|
| Ga₂O₃ | ATLAS prints semantic Ga₂O₃ runtime records as Silicon | `ATLAS_IMPORT_INTERPRETATION` |
| NiO | ATLAS emits `Unknown material #304` and prints semantic NiO records as SiO₂/insulator | `ATLAS_IMPORT_INTERPRETATION` |

## Why earlier stages are not selected

1. **DEVEDIT_EXPORT:** raw STR contains explicit `Ga2O3` and `NiO` labels/codes, semantic regions, doping, and electrodes.
2. **VICTORY_LOAD:** Victory Mesh logs still list the correct semantic materials `ga2o3` and `nio`.
3. **VICTORY_SAVE_MODE_ATLAS:** Ga₂O₃ remains code/label 50/`ga2o3`; NiO becomes current SMDB canonical code 304. The NiO textual Q-label becomes `0`, which is a metadata degradation, but current SMDB still identifies code 304 as NiO. No wrong semiconductor/insulator class is observed until ATLAS reads the file.
4. **ATLAS_IMPORT_INTERPRETATION:** this is the first stage with direct wrong class/name evidence.

## Repair-layer decision

`RECOMMENDED_FIX_LAYER = C. VICTORY_SAVE_MODE_ATLAS_MAPPING_FIX`

This is not a claim that `SAVE MODE=ATLAS` itself caused the first observable loss. It identifies the last documented, non-destructive layer where the frozen mesh can be assigned importer-recognized transport parents before ATLAS interprets it.

## Mesh/resave decision

- `REMESH_REQUIRED = NO`
- `RESAVE_REQUIRED = YES`

The existing conformal mesh stays frozen:

- nodes: 56,454;
- triangles: 111,350;
- obtuse: 0;
- track max Δx: 0.015 µm;
- track max Δy: 0.0166667 µm;
- full-y continuity: PASS.

No mesh command appears in the candidate.

## Candidate and stop boundary

The sole candidate is `VICTORYMESH_ATLAS_PARENT_MAPPING_RESAVE_CANDIDATE.in`. It proposes a Victory-side parent remap and Atlas-mode resave only. It is `NONEXECUTED_PLAN_ONLY / NOT_RUNTIME_VALIDATED`.

The requested exact forms `UD1(BetaGa2O3)` and `UD2(NiOx)` are recorded as an unvalidated DevEdit-label hypothesis. Their inner strings have no installed official dictionary entry; the wrappers do not by themselves establish downstream ATLAS identity. The installed official names `Beta-Ga2O3` and `NiO` are also absent from ATLAS Table B-1, and code 304 already fails the tested ATLAS import. For that reason the label-only hypothesis does not replace the frozen-mesh resave candidate.

Open gates after this audit:

1. Web review of the mapping concept and selectors;
2. separate authorization for one Victory Mesh resave-only test, if approved;
3. separate one-shot ATLAS zero-bias import/solve-init gate after a successful resave;
4. proof that explicit Ga₂O₃/NiO physical cards bind without inheriting unapproved parent defaults;
5. independent OUTPUT contact `-999` repair;
6. 300 V and all transients remain denied.
