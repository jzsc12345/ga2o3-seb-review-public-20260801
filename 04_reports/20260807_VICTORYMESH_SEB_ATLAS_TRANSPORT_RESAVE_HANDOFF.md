# Victory Mesh SEB — one-time ATLAS transport-identity resave handoff

> Input review commit: `d75bfd90bd99a8eba0dfe506a63386673749604e`
>
> Result: `VICTORY_RESAVE_ONLY_PASS / ATLAS_IMPORT_NOT_TESTED`
>
> Classification: `IMPORT_TRANSPORT_STR_ONLY / NOT_PHYSICS_VALIDATED / NOT_STATIC_READY / NOT_SEB_READY`

## 1. Authorization and execution boundary

The authorized sequence was executed once:

```text
frozen conformal STR
→ Victory Mesh load
→ pre-map INFO hard gate
→ Ga2O3 lineage: GaN import transport identity
→ NiO lineage: ZnO import transport identity
→ post-map INFO hard gate
→ one SAVE MODE=ATLAS
→ quit
→ offline STR audit
```

No DevEdit, remesh, refine, ATLAS, solve, bias, 300 V, SEU, SET, SEB,
second Victory process, or automatic fallback was executed.

Environment and execution:

| Item | Value |
|---|---|
| Remote host | `tcad`, reached with SSH alias `silvaco` |
| Remote workdir | `/root/DECKBUILD/preflight/VICTORYMESH_SEB_ATLAS_TRANSPORT_RESAVE_D75BFD9_20260807` |
| Victory Mesh | `1.12.0.R`, 4 CPUs |
| Actual process | one interactive `/atctools/Synopsys/Silvaco2024/bin/victorymesh -P 4` process under tmux |
| Source STR (remote) | workdir `/VM_SEB_STAGE2_conformal_track_x10p25.str` |
| Output STR (remote) | workdir `/VM_SEB_STAGE2_conformal_track_x10p25_atlas_transport_mapped.str` |
| Output STR (bulk) | `E:\silvaco2425\bulk\str\VICTORYMESH_SEB_20260807\VM_SEB_STAGE2_conformal_track_x10p25_atlas_transport_mapped.str` |

An initial tmux command had a shell-quoting/PATH failure before Python or
Victory Mesh started: it created no Victory transcript, no sentinel, no output
STR, and no simulator process.  The guarded launcher was then used; it creates
an exclusive execution sentinel immediately before the sole Victory process,
so a second Victory launch is mechanically blocked.  This preliminary launcher
failure is preserved in the evidence, not hidden.

## 2. Pre-map selector gate

Victory `INFO` before either `MATERIAL` command reported:

| Selector | Selected runtime regions | Count | Triangles | Gate |
|---|---|---:|---:|---|
| `MATERIAL:GA2O3` | 1, 2, 3, 6, 7 | 5 | 62,100 | PASS |
| `MATERIAL:NIO` | 9, 10 | 2 | 4,000 | PASS |

The same pre-map table showed two SiO2 records, one Al2O3 record, and three
Nickel electrodes named source, drain, and gate.

## 3. Approved material-identity changes and post-map gate

Only these commands were sent:

```silvaco
material regions="MATERIAL:GA2O3" value="GaN"
material regions="MATERIAL:NIO" value="ZnO"
```

Post-map `INFO` proved:

| Lineage | Runtime identity | Regions | Triangles | Victory conduction attribute |
|---|---|---|---:|---|
| Ga2O3 | GaN | 1, 2, 3, 6, 7 | 62,100 | `unknown` |
| NiO | ZnO | 9, 10 | 4,000 | `semiconductor` |
| SiO2 | unchanged | 4, 5 | 34,200 | `insulator` |
| Al2O3 | unchanged | 8 | 5,360 | `insulator` |
| Nickel | unchanged | 11, 12, 13 | 5,690 | `conductor` |

The GaN `conduction: unknown` result is recorded but is **not** used to fail the
Victory resave.  The saved STR dictionary/region table is the resave gate; ATLAS
classification remains `NOT_YET_TESTED`.  The output is not yet static-ready or
physics-ready.

## 4. Actual output material dictionary

The saved STR, not merely the input commands, reports:

| Output identity | Numeric code | Label | Runtime region records |
|---|---:|---|---:|
| GaN | 124 | `GaN` | 5 |
| ZnO | 209 | `ZnO` | 2 |

After resave, legacy material codes have zero runtime records:

```text
GA2O3_RUNTIME_RECORDS_AFTER_RESAVE = 0
NIO_RUNTIME_RECORDS_AFTER_RESAVE = 0
```

This proves only exporter-side transport identities, not ATLAS import success.

## 5. Offline invariance audit

Source and output ASCII STRs were parsed independently.  File size and images
were not used as substitutes for the audit.

| Gate | Result | Evidence |
|---|---|---|
| Node count | 56,454 → 56,454 | PASS |
| Triangle count | 111,350 → 111,350 | PASS |
| Obtuse triangles | 0 → 0 | PASS |
| Coordinates | identical by node ID | PASS |
| Triangle topology | identical per region, order/winding normalized | PASS |
| Region area/bbox/interfaces | identical; tolerance 1e-12 um for derived area/bbox | PASS |
| Track max dx | 0.0150000000 um → same | PASS |
| Track max dy | 0.0166666667 um → same | PASS |
| Full-y continuity | PASS → PASS | PASS |
| Donor/acceptor scalars | identical by region and node | PASS |
| Electrode map | source/drain/gate; IDs 1/2/3 | PASS |
| Thick stepped gate | retained; no `gate_fp` | PASS |
| Material-only transform | 5 Ga2O3→GaN; 2 NiO→ZnO; other materials unchanged | PASS |

The ATLAS-mode exporter changed the `n`-record payload length from four to six
values.  Donor and acceptor (the first two scalars) are unchanged; derived
payload layout is separately flagged as changed and remains an import-audit
item.

## 6. Warnings and truthful limitations

- Victory transcript warning/fatal/error hits: **0**.
- Victory reported GaN conduction as `unknown`; ZnO was `semiconductor`.
- ATLAS did not run, so `IMPORT_CLASSIFICATION_PASS` is **not established**.
- No physical Ga2O3 or NiO model was validated.
- `UD1(BetaGa2O3)` / `UD2(NiOx)` label-only path is closed:
  `LABEL_ONLY_OFAT = CLOSED_NOT_SELECTED`.

## 7. Evidence index

All paths below are relative to this handoff.

- [Executed resave deck](attachments/20260807_victorymesh_transport_resave/VICTORYMESH_ATLAS_TRANSPORT_RESAVE_EXECUTED.in)
- [Complete Victory transcript](attachments/20260807_victorymesh_transport_resave/logs/victorymesh_transcript.log)
- [Controller execution status](attachments/20260807_victorymesh_transport_resave/logs/RESAVE_STATUS.txt)
- [Pre-launch shell failure evidence](attachments/20260807_victorymesh_transport_resave/logs/PRELAUNCH_SHELL_FAILURE.txt)
- [Pre-map selector evidence](attachments/20260807_victorymesh_transport_resave/runtime_evidence/PREMAP_SELECTOR_AND_REGION_INFO.txt)
- [Post-map material/electrode evidence](attachments/20260807_victorymesh_transport_resave/runtime_evidence/POSTMAP_MATERIAL_AND_ELECTRODE_INFO.txt)
- [INFO summary](attachments/20260807_victorymesh_transport_resave/runtime_evidence/info_evidence_summary.json)
- [Warning/fatal register](attachments/20260807_victorymesh_transport_resave/runtime_evidence/warning_fatal_register.csv)
- [Invariance summary](attachments/20260807_victorymesh_transport_resave/invariance/transport_resave_invariance_summary.json)
- [Source/output material dictionaries](attachments/20260807_victorymesh_transport_resave/invariance/material_dictionary_and_region_table.csv)
- [Per-region geometry/material/doping comparison](attachments/20260807_victorymesh_transport_resave/invariance/region_geometry_material_doping_comparison.csv)
- [Offline audit script](attachments/20260807_victorymesh_transport_resave/audit_transport_resave_str.py)
- [INFO extraction script](attachments/20260807_victorymesh_transport_resave/extract_victory_info_evidence.py)
- [Hard-gate controller](attachments/20260807_victorymesh_transport_resave/logs/run_victory_resave_gate.py)
- [One-execution launcher](attachments/20260807_victorymesh_transport_resave/logs/launch_victory_resave_once.sh)

Large source/output STR files remain in bulk storage and are not committed.

## 8. Verdict and next gate

```text
VICTORY_RESAVE_ONLY = PASS
ATLAS_IMPORT_TRANSPORT_IDENTITY = NOT_YET_TESTED
IMPORT_TRANSPORT_STR_ONLY = YES
PHYSICS_VALIDATED = NO
STATIC_READY = NO
SEB_READY = NO
LABEL_ONLY_OFAT = CLOSED_NOT_SELECTED
```

The next authorized work, if any, must be a new, separately reviewed package:

```text
resaved STR
→ ATLAS import-only / minimum solve-init gate
→ runtime material/region table
→ PARENT_DEFAULT_LEAKAGE_AUDIT
→ explicit Ga2O3/NiO slot restoration
→ only then discuss 300 V
```

`PARENT_DEFAULT_LEAKAGE_AUDIT` must cover bandgap, affinity, permittivity,
Nc/Nv, electron/hole mobility, vsat, SRH lifetime, Auger, BGN, incomplete
ionization, thermal conductivity, impact ionization, temperature dependence,
and every default used by active `MODELS`.  No 300 V or SEB authorization is
carried by this handoff.
