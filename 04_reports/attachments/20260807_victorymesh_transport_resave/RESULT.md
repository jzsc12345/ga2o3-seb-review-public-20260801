# Victory Mesh ATLAS transport-identity resave — runtime result

> Scope: `IMPORT_TRANSPORT_STR_ONLY`
>
> Status: `NOT_PHYSICS_VALIDATED / NOT_STATIC_READY / NOT_SEB_READY`

## Result

One and only one Victory Mesh process loaded the frozen conformal STR, passed
the pre-map selector gate, applied the two approved material-identity changes,
passed the post-map material/electrode gate, saved one ATLAS-mode STR, and quit.
No DevEdit, remesh, ATLAS, solve, bias, 300 V, SEU, SET, or SEB operation ran.

| Item | Actual result |
|---|---|
| Source | `VM_SEB_STAGE2_conformal_track_x10p25.str` |
| Output | `VM_SEB_STAGE2_conformal_track_x10p25_atlas_transport_mapped.str` |
| Pre-map Ga2O3 selector | 5 records: regions 1/2/3/6/7, 62,100 triangles |
| Pre-map NiO selector | 2 records: regions 9/10, 4,000 triangles |
| Ga2O3 lineage output | GaN, code 124, 5 records |
| NiO lineage output | ZnO, code 209, 2 records |
| Mesh | 56,454 nodes; 111,350 triangles; 0 obtuse |
| Track ROI | max dx 0.015 um; max dy 0.0166666667 um; full-y PASS |
| Geometry/interfaces | unchanged; coordinates and triangle topology identical |
| Donor/acceptor doping | unchanged by node and semantic region |
| Electrodes | source/drain/gate only; stepped gate retained; no `gate_fp` |

## Important open fact

Victory Mesh's post-map `INFO` reports ZnO as `semiconductor`, but reports all
five mapped GaN records with `conduction: unknown`.  This is recorded without
being classified as a resave failure.  The actual saved STR contains GaN code
124 / label `GaN` on exactly the five lineage regions and ZnO code 209 / label
`ZnO` on exactly the two lineage regions.  Whether ATLAS imports both identities
as semiconductors remains `NOT_YET_TESTED`; ATLAS was not run.

The ATLAS-mode save expands the ASCII `n` payload from four to six values per
record.  The first two donor/acceptor scalars remain exactly identical; the
derived payload layout is recorded as changed and is not misreported as a
physical doping change.

## Execution note

An initial tmux shell command failed before creating a controller transcript or
starting any Victory process.  The corrected guarded launcher then created the
sole `VICTORY_EXECUTION_STARTED.flag` and ran exactly one Victory process.  The
scientific execution count is one; no second Victory launch or fallback exists.

## Next gate

Before any 300 V or SEB work: separately authorize an ATLAS import-only / minimum
`solve init` gate, then perform `PARENT_DEFAULT_LEAKAGE_AUDIT` covering every
active band, mobility, recombination, incomplete-ionization, thermal, impact,
and temperature-dependent slot.  GaN/ZnO are only
`ATLAS_IMPORT_TRANSPORT_IDENTITIES`.
