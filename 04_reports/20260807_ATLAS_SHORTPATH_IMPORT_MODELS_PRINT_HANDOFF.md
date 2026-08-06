# ATLAS short-path import + MODELS PRINT handoff

> Accepted predecessor commit: `70dc90c58a6df77babf361a792736b5c17cdb0be`
>
> Result: `SHORT_PATH_IMPORT_MODELS_PRINT_PASS`.
>
> Scientific boundary: transport identity PASS; physics/static/SEB readiness NO.

## 1. Authorization and exact execution

One four-active-line deck was launched once through the established runner:

```text
go atlas simflags="-V 5.40.0.R -P 4"
mesh infile="/root/DECKBUILD/preflight/AI70/t.str"
models print
quit
```

Environment and command:

| Item | Actual value |
|---|---|
| SSH alias / host | `silvaco` / `tcad` |
| Remote workdir | `/root/DECKBUILD/preflight/AI70` |
| DeckBuild | `5.2.40.R` |
| ATLAS | `5.40.0.R`, `-P 4` |
| Runner | `/root/bin/vdoe_tmux.sh start-deck` |
| Execution count | 1 |
| Simulator completion | `ATLAS version 5.40.0.R finished` |

Exact launch:

```bash
/root/bin/vdoe_tmux.sh start-deck \
  /root/DECKBUILD/preflight/AI70 \
  PREFLIGHT_ATLAS_SHORTPATH_IMPORT_MODELS_PRINT.in
```

The runner's `EXIT.txt` is zero bytes, so no exit-code value is invented.  The
complete simulator transcript is the completion evidence.

## 2. Frozen STR and short-path falsification

The original STR remained untouched:

```text
/root/DECKBUILD/preflight/VICTORYMESH_SEB_ATLAS_TRANSPORT_RESAVE_D75BFD9_20260807/
VM_SEB_STAGE2_conformal_track_x10p25_atlas_transport_mapped.str
```

It was copied to `/root/DECKBUILD/preflight/AI70/t.str` and compared before
launch:

| Field | Result |
|---|---|
| ORIGINAL_SIZE | 12,735,490 bytes |
| SHORT_COPY_SIZE | 12,735,490 bytes |
| `cmp -s` | `CMP_IDENTICAL=YES` |
| Hash used | NO |

ATLAS then printed:

```text
Reading MASTER format file /root/DECKBUILD/preflight/AI70/t.str from "Victory Mesh".
Read 56454 nodes.
Read 111350 triangles.
Read 13 regions.
Read 3 electrodes.
```

Therefore:

```text
SHORT_PATH_OPEN=PASS
PATH_TRUNCATION_CAUSAL_EVIDENCE=STRONGLY_SUPPORTED
```

No precise internal maximum path length is claimed.

## 3. Runtime material identities

ATLAS `MODELS PRINT` supplied the real runtime material table:

| Runtime regions | Runtime material / type | Frozen lineage |
|---|---|---|
| 1 / 2 / 3 / 6 / 7 | GaN / semiconductor | Ga2O3; exporter code 124 |
| 4 / 5 | SiO2 / insulator | SiO2 |
| 8 | Al2O3 / insulator | Al2O3 |
| 9 / 10 | ZnO / semiconductor | NiO; exporter code 209 |
| 11 / 12 / 13 | Nickel / metal | Nickel |

The oxide split still explains 13 runtime records from 12 frozen semantic
regions.  No unknown-material line or `Using insulator` line exists for the
GaN/ZnO lineages.

```text
UNKNOWN_MATERIAL_124_COUNT=0
UNKNOWN_MATERIAL_209_COUNT=0
GAN_ZNO_USING_INSULATOR=NO
ATLAS_IMPORT_TRANSPORT_IDENTITY=PASS
```

This is only an import/transport-identity conclusion.  It does not validate
Ga2O3 or NiO physics.

## 4. Electrode topology

Both the import table and final contact table show exactly:

```text
source = electrode 1
drain  = electrode 2
gate   = electrode 3
```

There is no `gate_fp` and no fourth terminal.  The gate geometry remains one
terminal spanning `x=1.5..6.0 um`, `y=-0.20..-0.12 um`.

## 5. Parent-default leakage baseline

`MODELS PRINT` was executed only to expose defaults.  Every recorded value in
the attached table has the status:

```text
TRANSPORT_PARENT_DEFAULT
NOT_ACCEPTED_FOR_GA2O3_OR_NIO
```

Examples of why closure remains mandatory:

| Slot | GaN parent | ZnO parent |
|---|---:|---:|
| Eg | 3.44 eV | 3.37 eV |
| affinity | 4.45 eV | 4.5 eV |
| permittivity | 8.9 | 8.49 |
| Nc / Nv | 2.24e18 / 2.51e19 | 2.2e18 / 1.8e19 cm^-3 |
| electron/hole mobility | 400 / 8 cm2/Vs | built-in; numeric value not printed |
| vsatn / vsatp | 1.91e7 / 1e6 cm/s | 1e6 / 1e6 cm/s |
| taun0 / taup0 | 1.2e-8 / 1.2e-8 s | 1 / 1 s |
| lt.taun / lt.taup | 1.42 / 1.42 | 0 / 0 |

SRH, Auger, BGN, incomplete ionization, tunneling and impact flags were also
printed and are inactive.  Impact coefficients, thermal conductivity and heat
capacity were not printed; they remain `NOT_PRINTED`, not inferred.

No defaults were modified in this execution.

## 6. Doping and six-field record boundary

```text
ATLAS_DOPING_RUNTIME_TABLE=NOT_OBSERVABLE_WITHOUT_SOLVE
N_RECORD_6FIELD_SEMANTICS=PARTIALLY_DEMONSTRATED_ONLY
```

Prior offline evidence proves only that the donor/acceptor scalars remained
invariant through resave.  The four added payload fields remain undocumented.
No solve was added to expand this evidence.

## 7. Operational anomalies without scientific reclassification

- One post-launch SSH status probe returned `Permission denied`; the same
  read-only probe then succeeded and showed the sole job had ended.
- One pre-launch remote `awk` display command had a quoting error; only the
  read-only text scan was repeated, not the input or simulation.
- `EXIT.txt` is empty; the transcript cleanly reports ATLAS `finished`, with
  zero warning, error and fatal lines.

None caused a second launch, input edit, retry of ATLAS, or fallback.

## 8. Evidence index

Paths are relative to this handoff.

- [Executed four-line deck](attachments/20260807_atlas_shortpath_import_models_print/PREFLIGHT_ATLAS_SHORTPATH_IMPORT_MODELS_PRINT.in)
- [Complete transcript](attachments/20260807_atlas_shortpath_import_models_print/logs/typescript.txt)
- [Empty runner exit marker](attachments/20260807_atlas_shortpath_import_models_print/logs/EXIT.txt)
- [Empty DeckBuild side log](attachments/20260807_atlas_shortpath_import_models_print/logs/deckbuild_log.txt)
- [Result summary](attachments/20260807_atlas_shortpath_import_models_print/RESULT.md)
- [Short-copy proof](attachments/20260807_atlas_shortpath_import_models_print/reports/SHORT_PATH_COPY_PROOF.txt)
- [Exact deck diff](attachments/20260807_atlas_shortpath_import_models_print/reports/EXACT_DECK_DIFF.md)
- [Runtime region/material table](attachments/20260807_atlas_shortpath_import_models_print/reports/runtime_region_material_table.csv)
- [Electrode table](attachments/20260807_atlas_shortpath_import_models_print/reports/electrode_table.csv)
- [Unknown-material register](attachments/20260807_atlas_shortpath_import_models_print/reports/unknown_material_register.csv)
- [MODELS PRINT parent-default baseline](attachments/20260807_atlas_shortpath_import_models_print/reports/parent_default_leakage_baseline.csv)
- [`n`-record and doping note](attachments/20260807_atlas_shortpath_import_models_print/reports/N_RECORD_6FIELD_SEMANTICS_NOTE.md)
- [Warning/fatal register](attachments/20260807_atlas_shortpath_import_models_print/reports/warning_fatal_register.csv)

The 12.7 MB STR is not committed.

## 9. Stop state and recommendation

```text
PHYSICS_VALIDATED=NO
STATIC_READY=NO
SEB_READY=NO
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

Open gates are physical material closure, a separately reviewed doping-runtime
gate, and only then a separately authorized zero-bias/static gate.  Do not
advance to 300 V or SEB from transport identity alone.
