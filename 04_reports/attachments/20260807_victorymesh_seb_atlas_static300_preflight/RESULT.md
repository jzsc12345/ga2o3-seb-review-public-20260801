# Victory Mesh Stage-2 STR → ATLAS 300 V source-off static preflight

> Status: `ATLAS_STATIC_PREFLIGHT_PARSER_FAILED_STOPPED`
>
> Date: 2026-08-07
>
> Scope: frozen Stage-2 STR, ATLAS input/parser and source-off static preflight only
>
> Result trust: runtime evidence from the single authorized launch

## Result

The one authorized launch stopped in the ATLAS input/parser gate before the
first `solve`. No static state, 300 V state, baseline, or transient was run.

Primary fatal:

```text
METHOD ... carr.limit=1e18 damping.factor=0.8
ERROR #3 Invalid parameter specification ==> carr.limit
ERROR #3 Invalid parameter specification ==> damping.factor
simulator exits with code 2
```

Independent material-import blockers were also observed before the fatal:

- `Unknown material #304. Using insulator.` occurred 2228 times while loading
  the Victory Mesh STR.
- The NiO material statement was followed by `Statement ignored.`
- The Ga2O3 statement warned that the imported `GA2O3_BETA` default material
  and material group could not be changed.

These observations do not invalidate the frozen Stage-2 track-mesh spacing.
They show that ATLAS material import and the inherited METHOD line are not yet
runtime-admissible.

## Runtime facts

| Field | Evidence |
|---|---|
| Remote host | `tcad` via SSH alias `silvaco` |
| Remote directory | `/root/DECKBUILD/preflight/VICTORYMESH_SEB_STAGE2_ATLAS_STATIC300_20260807` |
| Runner | `/root/bin/vdoe_tmux.sh start-deck` |
| tmux | `deck_PREFLIGHT_VICTORYMESH_SEB_STAGE2_ATLAS_STATIC300_sourceoff` |
| DeckBuild | `5.2.40.R` |
| ATLAS | `5.40.0.R` |
| Imported mesh | 56,454 nodes; 111,350 triangles; 0 obtuse |
| Runtime region count | 13 total; 12-semantic equivalence not proven in this failed gate |
| Runtime electrodes | 3: source, drain, gate |
| Exit | code 2 |
| Parser/input wall time | approximately 31 s (02:30:49–02:31:20 +08:00) |
| Static wall time | not started |
| `solve` reached | 0 |
| `Cannot trap` | 0; not applicable because no solve began |
| Static STR | not created |

## Gate decisions

| Gate | Decision |
|---|---|
| Frozen Victory Mesh STR read | `PARTIAL_PASS` — mesh imported, but material #304 fell back to insulator |
| Parser/input | `FAIL` |
| Region mapping | `NOT_VALIDATED` |
| Material mapping | `FAIL` |
| Electrode import | `PASS_IMPORT_ONLY` |
| Thermcontact mapping | `NOT_EVALUATED` — commands parsed, no runtime table/solve |
| `MATERIAL region=10 mun=50` | `NOT_EVALUATED` — statement accepted, effect not exercised |
| NiO thermal parameters | `FAIL_TO_APPLY` — statement ignored |
| VGS=0 | `NOT_EXECUTED` |
| VDS=300 V | `NOT_EXECUTED` |
| Five-point baseline | `NOT_EXECUTED` |

## Stop compliance

- Victory Mesh rerun: **NO**
- Deck auto-fix: **NO**
- Second launch: **NO**
- Static bias: **NO**
- SEU/SET/SEB transient: **NO**
- Paired transient: **NO**
- New RUN number: **NO**

## Next decision required

A new authorization and reviewed candidate are required before any retry. The
next review must separately close:

1. the ATLAS 5.40.0.R-valid METHOD syntax without changing the intended solver;
2. Victory Mesh material #304 → ATLAS material mapping;
3. the NiO material/thermal assignment that was ignored;
4. the meaning of the 13th imported region and 12-semantic-region equivalence.

No retry is authorized by this result.
