# ATLAS STATIC INPUT REV1 audit

Status: `PREPARED / NOT_RUNTIME_VALIDATED / ONE_SOLVE_INIT_AUTHORIZED`

## 1. Frozen input and scope

- Frozen STR: `/root/DECKBUILD/preflight/VICTORYMESH_SEB_STAGE2_CONFORMAL_X10P25_20260807/VM_SEB_STAGE2_conformal_track_x10p25.str`
- Candidate: `decks/PREFLIGHT_VICTORYMESH_SEB_STAGE2_ATLAS_MATERIAL_INIT_REV1.in`
- Maximum execution: STR import → material/physics declarations → `solve init` → one equilibrium STR → quit.
- Prohibited: Victory Mesh, DevEdit, remesh, any electrical bias, 300 V, particle source, transient, retry, repair, or fallback.

## 2. Frozen 13-runtime / 12-semantic mapping

The two disconnected polygons of the single semantic SiO2 `oxide` region became runtime records 4 and 5. Therefore 13 runtime records do **not** imply an unknown background region. The exact map is in `csv/semantic_runtime_region_map.csv`.

Key anchors:

- runtime 9/10 = p-/p+ NiO, material code 304;
- runtime 11/12/13 = source/drain/gate Nickel, electrode IDs 1/2/3;
- runtime 4/5 jointly represent the original semantic oxide region.

## 3. Material code 304 and NiO repair hypothesis

The predecessor imported code 304 as an insulator, then ignored `material material=NiO ...` because no usable NiO material name existed in ATLAS. REV1 instead binds the already identified runtime records directly:

```silvaco
MATERIAL region=9  user.group=semiconductor user.default=GaN ...
MATERIAL region=10 user.group=semiconductor user.default=GaN ...
```

Both cards retain the original active NiO values: `affinity=2.0`, `eg300=3.92`, `permittivity=11.9`, `TCON.CONST`, and `TC.CONST=2.27`. The different p-/p+ acceptor concentrations remain embedded in the frozen STR. No commented NiO parameter is activated.

This is supported by the current parser dictionary, manual B.2.5, and accepted project region-scoped material runs. It remains a runtime hypothesis until the one-shot result prints runtime regions 9/10 as semiconductor and accepts `solve init`.

## 4. `MATERIAL region=10 mun=50` lineage

Original `bv.in` defines semantic region 10 as the thick Nickel source electrode (lines 91–94). Its electrical section later applies `MATERIAL region=10 mun=50` (line 214). Thus the old statement did **not** target Ga2O3; it targeted a metal region and is already stale or ineffectual in its source lineage.

Victory Mesh inserted a second oxide runtime record, shifting later IDs so runtime 10 is p+ NiO. Mechanical retention would incorrectly impose `mun=50` on p+ NiO. There is no evidence for a different intended semiconductor target, so REV1 removes the card rather than guessing a replacement region.

## 5. Region-number-sensitive statement audit

The complete disposition is in `csv/region_number_sensitive_audit.csv`.

- DevEdit `region.id=` impurity and `constr.mesh region=` statements are already embodied in the frozen STR and are not copied into REV1.
- The only active inherited numeric ATLAS material selector was the stale region-10 mobility card; it is removed.
- `elec.num=1/2` refers to preserved electrode IDs, not runtime region IDs.
- Ga2O3 mobility/impact and Al2O3 material cards use material names, not numeric region IDs.
- Interface and probes are coordinate-scoped.
- Historical `region=9/10` trap/defect lines are comments and remain inactive.

## 6. GA2O3_BETA handling

The predecessor proved code 50 is already recognized as `GA2O3_BETA`. REV1 therefore removes only `user.default=GaN` and `user.group=semiconductor` from the Ga2O3 card. It retains every active explicit override from `bv.in`:

| Slot | Before | REV1 |
|---|---:|---:|
| affinity | 4.0 | 4.0 |
| Eg300 | 4.8 eV | 4.8 eV |
| Nc300 / Nv300 | 3.72e18 / 3.72e18 cm^-3 | unchanged |
| permittivity | 10 | unchanged |
| mun / mup | 300 / 50 cm2/Vs | unchanged |
| thermal model/value | TCON.CONST / 0.27 W cm^-1 K^-1 | unchanged |
| mobility card | original Ga2O3 card | unchanged |
| impact card | original legacy SELB card | unchanged |

The inherited legacy impact values are retained only because this is the explicitly frozen benchmark lineage; the deck is labeled `NOT_PRODUCTION_QUALIFIED_SEB`.

## 7. METHOD legality

Current `atlas.key` and manual evidence establish:

| Token | Current status | REV1 decision |
|---|---|---|
| `newton` | legal logical | keep |
| `trap` | legal logical | keep |
| `maxtraps` | legal integer, documented 1–10 | canonical spelling, use 10 |
| `climit` | legal real | keep `1e-4` |
| `weak` | legal real | keep `1` |
| `itlimit` | legal integer | keep `50` |
| `carr.limit` | absent from current METHOD dictionary; predecessor parser rejected it | remove, no substitute |
| `damping.factor` | absent from current METHOD dictionary; predecessor parser rejected it | remove, no substitute |

Final card:

```silvaco
METHOD newton trap maxtraps=10 climit=1e-4 weak=1 itlimit=50
```

## 8. First-principles review before launch

1. The structure file is read-only and no mesher is invoked.
2. NiO binding changes only the runtime material classification/parameters of known p-/p+ regions; geometry and doping stay in the STR.
3. No numeric region selector is retained without a semantic mapping.
4. The candidate contains exactly one `solve`, and it is `solve init`.
5. There is no bias token, transient token, particle source, or second execution path.
6. Failure is terminal for this task; no fallback syntax is prepared.

## 9. Runtime hard gates

PASS requires: parser zero fatal; runtime 9/10 semiconductor; NiO cards not ignored; no illegal GA2O3_BETA group/default change; 3 preserved electrodes; accepted `solve init`; equilibrium STR; no `Cannot trap`. The initial code-304 import warning is tolerated only if the later regional table and solve prove the two records were reclassified as semiconductor.

## 10. Evidence references

See `MANUAL_EXAMPLE_EVIDENCE_INDEX.md`, the two CSV audits, and the exact predecessor-to-REV1 diff. No runtime PASS is claimed before the single authorized launch.
