# ATLAS 5.40.0.R material/METHOD evidence index

Status: `PRE-RUN / READ-ONLY EVIDENCE`

## Current-version primary sources

| Evidence | Exact location | What it establishes |
|---|---|---|
| ATLAS user manual | `/atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/docs/atlas_users1.pdf`, B.2.4 pp.1714–1715 | An imported unknown material falls back to an insulator. |
| ATLAS user manual | same PDF, B.2.5 p.1715 | A user material requires a user group and a known default; `USER.GROUP=SEMICONDUCTOR` and `USER.DEFAULT=<known material>` are the documented mechanism. |
| ATLAS user manual | same PDF, B.14 pp.1762–1763 | User material properties are overridden with `MATERIAL`, `MOBILITY`, `MODELS`, and `IMPACT`; the minimum semiconductor parameter set and thermal overrides are described. |
| ATLAS user manual | same PDF, §8.2.2 pp.600–601 | `TCON.CONST` selects constant thermal conductivity and `TC.CONST` supplies its value. |
| ATLAS user manual | same PDF, METHOD pp.1417–1427 | `ITLIMIT`, `MAXTRAPS`, `CLIMIT`, and numeric `WEAK` are current METHOD fields; `MAXTRAPS` is documented in the range 1–10. |
| Current parser dictionary | `/atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/common/atlas.key`, METHOD block around lines 643–709 and 818–831 | Canonical tokens `ITLIMIT`, `MAXTRAPS`, `CLIMIT`, `WEAK`, `TRAP`, and `NEWTON` exist. `CARR.LIMIT` and `DAMPING.FACTOR` do not exist. |
| Current parser dictionary | same file, MATERIAL block around lines 1948 and 2925–2926 | `REGION`, `USER.DEFAULT`, and `USER.GROUP` are legal MATERIAL fields. |

## Installed examples and project runtime corroboration

| Evidence | Exact location | Scope |
|---|---|---|
| Official DeckBuild example | `/atctools/Synopsys/Silvaco2024/examples/deckbuild/5.2.40.R/Technology/Power_and_RF/Other/Other_Power_ex08/Other_Power_ex08.in`, lines 45–55 | Shows a user-defined Ga2O3 material and a region-specific MATERIAL override. It is syntax evidence, not this device's physics source. |
| Official Victory Mesh flow example | `/atctools/Synopsys/Silvaco2024/examples/deckbuild/5.2.40.R/Technology/Display/LED_and_OLED/LED_OLED_ex12/LED_OLED_ex12.in`, lines 93–192 | Shows a Victory Mesh STR followed by user material declarations. It is flow evidence; it uses Victory Device, not an independent ATLAS proof. |
| Project accepted ATLAS run | `outputs/runs/RUN228_tanpg-atlas-binding-parser/logs/typescript.txt`, lines 182–185 and 230–233 | Region-level `USER.GROUP/USER.DEFAULT` declarations produced runtime NiO regions typed `semicond.`. |
| Project accepted ATLAS run | `outputs/runs/RUN233_tanpg-tannio-nsub-parser-solveinit/logs/typescript.txt`, lines 172–174 and 227–230 | Independent solve-init lineage corroborates region-scoped NiO material binding and the regional material table. |
| Failed predecessor | `outputs/runs/VICTORYMESH_SEB_ATLAS_STATIC300_PREFLIGHT_20260807/logs/typescript.txt`, lines 9041–9105 | Fixes the real failure signature: 13 regions/3 electrodes, code 304 fallback, ignored material-name NiO card, GA2O3_BETA group/default warnings, and invalid METHOD tokens. |

## Evidence boundary

The sources support a single runtime hypothesis: bind runtime regions 9 and 10 by `MATERIAL region=... user.group=semiconductor user.default=GaN`. They do not prove success on material code 304 before execution. The one authorized `solve init` is the falsification test; failure must stop without a retry.
