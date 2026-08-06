# ATLAS import-only manual evidence

## Sources inspected

- `atlas_users1_5p40_layout.txt`, derived from the installed ATLAS 5.40 user
  manual.
- `victorymesh_users1_1p12_layout.txt`, derived from the installed Victory
  Mesh 1.12 user manual.

## Findings

1. ATLAS manual lines 1634–1638 state that `MESH INFILE=<filename>` loads the
   mesh, geometry, electrode positions, and doping of an existing structure.
2. ATLAS manual lines 3872–3875 and 65347–65348 state that `MODELS PRINT` is the
   documented route for echoing material parameters, constants, and mobility
   models.
3. `MODELS` was expressly prohibited by the import-only authorization, so no
   unsupported solve-free full material-table command was added.
4. Victory Mesh manual Appendix C.2, lines 15647–15653, says SDB is a
   proprietary Silvaco interchange format that stores mesh, physical data,
   electrodes, materials, and other quantities.  It does not define the ASCII
   `n`-record payload layout.
5. No installed manual or dedicated format reference found in the scoped
   search defines the six numeric payload fields of the resaved `n` record.

## Consequence

```text
N_RECORD_6FIELD_SEMANTICS = NOT_DEMONSTRATED
FULL_RUNTIME_MATERIAL_TABLE_WITHOUT_MODELS_PRINT = NOT_DEMONSTRATED
```

No field semantics or material defaults are inferred from undocumented column
positions.

