# DevEdit raw STR versus Victory Mesh ATLAS-mode STR material audit

> Scope: read-only ASCII SDB comparison. No DevEdit, Victory Mesh, ATLAS, remesh, resave, or solve was executed.

## 1. Compared objects

| Stage | Object | Tool header / mesh |
|---|---|---|
| A | `str.txt` structure source | DevEdit command source; 12 semantic regions |
| B | `VM_SEB_STAGE2_devedit_raw.str` | DevEdit 2.8.26.R; 5,045 points; 9,802 triangles |
| C | `VM_SEB_STAGE2_conformal_track_x10p25.str` | Victory Mesh 1.12.0.R; 56,454 points; 111,350 triangles |

## 2. Region/material lineage

| Semantic material | A: DevEdit token | B: raw DevEdit SDB | Victory LOAD evidence | C: `SAVE MODE=ATLAS` SDB | ATLAS 5.40 import |
|---|---|---|---|---|---|
| Ga₂O₃ | `UD1(Ga2O3)` in semantic regions 1/2/3/5/6 | code 50; `G 50 Ga2O3`; `Q 50 ... Ga2O3` | runtime log still prints `ga2o3` for those regions | code 50; `G 50 ga2o3`; `Q 50 ... ga2o3` | runtime records 1/2/3/6/7 become Silicon |
| NiO | `UD2(NiO)` in semantic regions 8/9 | code 51; `G 51 NiO`; `Q 51 ... NiO` | runtime log still prints `nio` | code 304; `Q 304 ... 0`; current SMDB maps code 304 to NiO | 2,228 `Unknown material #304`; records 9/10 become SiO₂/insulator |
| SiO₂ | `SiO2` | code 1 | retained | code 1; disconnected component split is mechanical | SiO₂/insulator, correct |
| Al₂O₃ | `Al2O3` | code 229 | retained | code 229 | Al₂O₃/insulator, correct |
| Nickel | `Nickel` with source/drain/gate | code 77 plus electrode metadata | retained | code 77; three electrodes retained | Nickel/metal, correct |

The oxide split produces 13 runtime records from 12 semantic regions; it is not a material-identity failure. The source, drain, and single stepped gate remain three electrodes.

## 3. Doping and electrode metadata

The Victory Mesh runtime log and conformal STR analysis retain the semantic doping set:

- substrate acceptor `2e6`;
- UID donor `1.5e15`;
- channel donor `1e17`;
- source/drain n+ donors `5e19`;
- NiO p− acceptor `1.3e18` and p+ acceptor `3e19`.

Source, drain, and gate electrode names/numbers survive C and ATLAS import. Thus the observed Ga₂O₃/NiO failure is not explained by lost electrode or impurity metadata.

## 4. First-loss interpretation

- **Victory LOAD is not the first loss:** its runtime material listing still contains `ga2o3` and `nio`.
- **Victory SAVE does not yet show a demonstrated classification loss:** Ga₂O₃ retains code/label 50/`ga2o3`; NiO changes from local user code 51 to current SMDB canonical code 304. The text label `0` is degraded metadata, but code 304 remains a canonical NiO identifier in SMDB.
- **The first observed wrong material class is ATLAS import:** Ga₂O₃ becomes Silicon and NiO/code 304 becomes SiO₂/insulator.

This does not mean post-import repair is viable. It has already failed. The practical repair boundary is immediately before `SAVE MODE=ATLAS`, using only ATLAS-recognized transport-parent identities while preserving the frozen mesh.

## 5. User-specified UD-label hypothesis

The exact requested DevEdit forms are:

```text
UD1(BetaGa2O3)
UD2(NiOx)
```

These are **user-slot labels**, not direct claims that `BetaGa2O3` or `NiOx` is an ATLAS built-in material. DevEdit may accept arbitrary text inside the UD wrapper, so the dictionary result alone does not prove a DevEdit syntax error. It does prove that the two inner strings have no installed canonical SMDB/ATLAS identity to which downstream tools are obligated to map them.

The unexecuted mechanical source hypothesis would be exactly:

```diff
-mat="UD1(Ga2O3)"
+mat="UD1(BetaGa2O3)"
-mat="UD2(NiO)"
+mat="UD2(NiOx)"
```

It remains a label-only hypothesis: UD1/UD2 would still export through user-material slots, and no official source shows that these alternative labels change the ATLAS import classification. Testing it would require regenerating the downstream structure and is therefore not selected as the frozen-mesh repair candidate in this task.

### Installed-name check

| Candidate string | Current SMDB result | ATLAS 5.40 built-in table | Decision |
|---|---|---|---|
| `BetaGa2O3` | no exact entry | absent | reject as unsupported spelling |
| `Beta-Ga2O3` | official SMDB name, code 259 | absent | valid SMDB name, but not ATLAS-import proof |
| `NiOx` | no exact entry | absent | reject as unsupported spelling |
| `NiO` | official SMDB name, code 304 | absent; code 304 actually failed import | valid SMDB name, but not ATLAS-import proof |

Therefore the exact UD forms are recorded for a possible separately reviewed OFAT test, but they are not promoted as the evidence-backed fix in this handoff.
