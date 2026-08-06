# Victory Mesh → ATLAS material-mapping manual audit

> Local official sources: Victory Mesh 1.12.0.R User's Manual and installed examples. This is syntax evidence only; no command was executed.

## 1. Official Victory Mesh mechanism

Victory Mesh User's Manual §7.5 documents:

```text
MATERIAL REGIONS=<region selector> VALUE=<material name>
```

It states that `MATERIAL` changes the selected regions to a new material. Section 7.10.1 includes official examples such as:

```text
MATERIAL REGIONS="USER:CONTACT_A" VALUE="SILVER"
```

The region selector system also accepts material attributes, and the `INFO` command documents selectors such as `MATERIAL:SILICON`.

## 2. What `SAVE MODE=ATLAS` does—and does not do

Victory Mesh User's Manual §11.62 documents:

```text
SAVE IN="VM_FINAL" MODE="ATLAS"
```

The manual says Atlas mode sets format flags automatically for Atlas structure compatibility. It does **not** document a material-name mapping parameter on `SAVE`.

Therefore the only documented Victory-side material mapping mechanism found locally is:

1. load the already-frozen conformal STR;
2. use `MATERIAL` to assign ATLAS-recognized parent identities to selected regions;
3. save a new SDB with `MODE=ATLAS`.

This is a resave operation, not a remesh.

## 3. Candidate-name audit

Current installed SMDB 2.16.0.R contains:

```text
/material/ga2o3-beta/sdb/materialcode = 259
/material/ga2o3-beta/sdb/sdbname = Beta-Ga2O3
/material/nio/sdb/materialcode = 304
/material/nio/sdb/sdbname = NiO
```

Exact strings `BetaGa2O3` and `NiOx` were not found. They can still be written as custom text inside DevEdit `UD1(...)`/`UD2(...)`; that does not make them canonical cross-tool material identities. More importantly, ATLAS 5.40 Table B-1 does not contain even the official SMDB names `Beta-Ga2O3` or `NiO`.

Thus the candidate must not map to `BetaGa2O3`, `Beta-Ga2O3`, `NiOx`, or `NiO` as though those names were already recognized by the ATLAS importer. The exact user hypothesis `UD1(BetaGa2O3)`/`UD2(NiOx)` is retained as an unvalidated DevEdit-label OFAT alternative, not as official mapping evidence.

## 4. Official example boundary

Local `Other_Power_ex08.in` uses a `user.material=Ga2O3`/`user.default=GaN` pattern in a Victory Device lineage. It is not evidence that an imported Victory Mesh ATLAS-mode STR can preserve a custom user material through ATLAS 5.40.

No local official example was found that demonstrates custom `Beta-Ga2O3`/`NiO` SDB identities surviving Victory Mesh `SAVE MODE=ATLAS` and then importing into ATLAS 5.40 with correct semiconductor groups.

## 5. Nonexecuted repair candidate rationale

ATLAS Table B-1 explicitly lists `GaN` and `ZnO` as built-in binary compound semiconductors. The sole candidate therefore proposes:

- Ga₂O₃ transport identity → `GaN` parent;
- NiO transport identity → `ZnO` parent;
- preserve all geometry, mesh, doping, electrodes, and topology;
- resave once in Atlas mode;
- later, only after separate review/authorization, reapply the fully explicit Ga₂O₃/NiO physical parameter cards in ATLAS.

This is an import-identity transport hypothesis, not evidence that GaN or ZnO physical defaults are acceptable for the final SEB model. If the selector or import identity fails in a future separately authorized zero-bias test, execution must stop; no automatic fallback is permitted.
