# VictoryMesh Stage-2 STR → ATLAS material mapping + solve-init result

## Verdict

`MATERIAL_MAPPING_HARD_FAIL / SOLVE_INIT_NUMERIC_PASS_PHYSICS_INADMISSIBLE`

The one authorized launch completed naturally and wrote an equilibrium STR, but the runtime material table proves that the imported custom-material lineage is not closed:

- runtime regions 1/2/3/6/7 print as `Silicon`, not Ga₂O₃;
- runtime regions 9/10 print as `SiO2 / insulator`, not NiO semiconductor;
- material code 304 produced 2,228 `Unknown material #304 / Using insulator` warning pairs;
- `MATERIAL region=9/10 user.default=GaN user.group=semiconductor` targeted the code-304 fallback regions but ATLAS refused to change their existing SiO₂ default/group;
- the numeric NiO values were therefore applied to an insulator fallback and do not establish NiO semiconductor physics.

No retry, fallback, bias ramp, 300 V solve, remesh, Victory Mesh execution, or transient was performed.

## Frozen input and execution

- Deck: `decks/PREFLIGHT_VICTORYMESH_SEB_STAGE2_ATLAS_MATERIAL_INIT_REV1.in`
- Frozen STR: `/root/DECKBUILD/preflight/VICTORYMESH_SEB_STAGE2_CONFORMAL_X10P25_20260807/VM_SEB_STAGE2_conformal_track_x10p25.str`
- Remote host: `tcad` via SSH alias `silvaco`
- Remote workdir: `/root/DECKBUILD/preflight/VICTORYMESH_SEB_ATLAS_MATERIAL_INIT_REV1_20260807`
- Runner: `/root/bin/vdoe_tmux.sh start-deck`
- Session: `deck_PREFLIGHT_VICTORYMESH_SEB_STAGE2_ATLAS_MATERIAL_INIT_REV1`
- ATLAS: `5.40.0.R`
- Elapsed time printed by ATLAS: `39.17 s`
- Launch count: exactly one

## Runtime facts

| Gate | Result | Evidence |
|---|---|---|
| STR import | PASS mechanically | 56,454 nodes, 111,350 triangles, 13 runtime regions, 3 electrodes |
| Regions 4/5 oxide | PASS | both print `SiO2 / insulator` |
| Regions 9/10 NiO | FAIL | both print `SiO2 / insulator` |
| Ga₂O₃ imported regions | FAIL | 1/2/3/6/7 print `Silicon`; the table retains Silicon permittivity 11.8 and Silicon mobility ancestry |
| NiO reclassification cards | FAIL | two default-parent warnings, two group warnings, and four corresponding `Ignoring...` messages |
| METHOD | PASS parser gate | `newton trap maxtraps=10 climit=1e-4 weak=1 itlimit=50`; no METHOD error |
| solve init | PASS numerically | direct zero-bias solution completed; no `Cannot trap` |
| equilibrium STR | CREATED | 42,540,868-byte remote file; archived in `E:\silvaco2425\bulk\str` |
| physical admissibility | FAIL | solve used wrong Ga₂O₃/NiO runtime material identities |

## Region-number audit

VictoryMesh runtime records 9/10 are the two semantic NiO regions whose material code 304 fell back to SiO₂. The numeric selectors therefore reached those records, but ATLAS does not allow the post-import `MATERIAL` cards to change their established material group/default parent. This is a material-import/reclassification failure, not evidence that the 9/10 record identities were swapped.

The original `MATERIAL region=10 mun=50` was correctly removed: original `bv.in` semantic region 10 was the thick Nickel source, whereas VictoryMesh runtime record 10 is the p+ NiO/code-304 fallback record. Retargeting that stale card would have silently changed its meaning.

## Additional warning

The `OUTPUT` statement emitted `Contact number given (-999) is out of range.` This did not stop `solve init`, but it remains a separate output-contract gate. It must not be silently fixed in this stopped run.

## Stop state

The authorized falsification test is complete. The next action must be a new, separately reviewed mapping design that establishes custom material identities at the mesh/STR export boundary or uses a documented import-time material-name mapping. It must be parser/solve-init only before any bias is considered.
