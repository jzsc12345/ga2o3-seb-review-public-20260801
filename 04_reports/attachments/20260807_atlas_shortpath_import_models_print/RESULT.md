# ATLAS short-path import + MODELS PRINT result

> Scope: one ATLAS import and `MODELS PRINT`; zero solve.
>
> Status: `ATLAS_IMPORT_TRANSPORT_IDENTITY=PASS`.
>
> Physics status: `NOT_VALIDATED / NOT_STATIC_READY / NOT_SEB_READY`.

## Result

The frozen 12,735,490-byte STR was copied to `/root/DECKBUILD/preflight/AI70/t.str`.
Remote `cmp -s` returned identical before launch.  The four-active-line deck ran
once and ATLAS read the short-path file as a Victory Mesh MASTER file.

| Gate | Actual result |
|---|---|
| Short-path open | PASS |
| Nodes / triangles / obtuse | 56,454 / 111,350 / 0 |
| Runtime region records | 13 |
| Frozen semantic regions | 12 |
| Ga2O3 lineage | runtime 1/2/3/6/7 = GaN / semiconductor |
| NiO lineage | runtime 9/10 = ZnO / semiconductor |
| Unknown material 124 / 209 | 0 / 0 |
| GaN/ZnO `Using insulator` | absent |
| Electrodes | source=1, drain=2, gate=3; count=3 |
| MODELS PRINT | completed |
| Solve / bias / transient | none |

The preceding long-path failure and the successful import of a byte-identical
short-path copy strongly support path truncation as the causal mechanism.  No
specific maximum path length is inferred.

## Scientific boundary

GaN and ZnO are only transport identities.  `MODELS PRINT` exposes parent
defaults, including GaN `mu_n=400`, `mu_p=8`, and ZnO built-in mobilities whose
numeric values were not printed.  These and all other printed defaults are
`TRANSPORT_PARENT_DEFAULT / NOT_ACCEPTED_FOR_GA2O3_OR_NIO`.

No runtime doping table is emitted without solve.  The resaved six-field `n`
record remains `PARTIALLY_DEMONSTRATED_ONLY`: the first donor/acceptor scalars
were previously shown invariant, while the remaining four fields are not
documented by the installed manuals or this import.

## Execution note

The simulator transcript contains `ATLAS version 5.40.0.R finished`, zero
simulator warning/error/fatal lines, and no solve command.  The runner-created
`EXIT.txt` is empty, so it is archived as an unusable runner marker rather than
misreported as an exit-code value.  A single monitoring SSH probe failed and
then succeeded; it did not launch or modify any remote task.

## Stop state

```text
MATERIAL_OVERRIDE_EXECUTED=NO
SOLVE_EXECUTED=NO
SOLVE_INIT_EXECUTED=NO
300V_EXECUTED=NO
SEU_EXECUTED=NO
VICTORYMESH_EXECUTED=NO
DEVEDIT_EXECUTED=NO
REMESH_EXECUTED=NO
SECOND_LAUNCH=NO
AUTO_FALLBACK=NO
```
