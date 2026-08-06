# Victory Mesh Stage-2 STR → ATLAS source-off static preflight stop handoff

> Unique handoff date: 2026-08-07
>
> Status: `ATLAS_STATIC_PREFLIGHT_PARSER_FAILED_STOPPED`
>
> Input mesh status: `PHYSICAL_TRACK_MESH_PASS / STRICT_0P016_BOOKKEEPING_GATE_NOT_MET`
>
> Execution count: one authorized launch

## 1. What was authorized

Only the frozen Victory Mesh Stage-2 STR could be loaded into ATLAS for a
source-off VGS=0, VDS=300 V static preflight. Remeshing, parameter changes,
automatic repair, a second launch, and all SEU/SET/SEB transients were forbidden.

The mesh was therefore frozen at:

```text
/root/DECKBUILD/preflight/VICTORYMESH_SEB_STAGE2_CONFORMAL_X10P25_20260807/
VM_SEB_STAGE2_conformal_track_x10p25.str
```

The preceding Victory Mesh evidence remains available from the fixed prior
handoff:

<https://github.com/jzsc12345/ga2o3-seb-review-public-20260801/blob/60b9bb49530b157afebfa298b645ef5be5e0e374/04_reports/20260807_VICTORYMESH_SEB_STRUCTURE_TRACK_MESH_HANDOFF.md>

## 2. Actual execution

Environment:

- SSH alias: `silvaco`
- Host: `tcad`
- DeckBuild: `5.2.40.R`
- ATLAS: `5.40.0.R`
- Remote working directory:
  `/root/DECKBUILD/preflight/VICTORYMESH_SEB_STAGE2_ATLAS_STATIC300_20260807`
- Parser/input wall time: approximately 31 s (`02:30:49–02:31:20 +08:00`)
- Static wall time: not started

Command:

```text
/root/bin/vdoe_tmux.sh start-deck \
  /root/DECKBUILD/preflight/VICTORYMESH_SEB_STAGE2_ATLAS_STATIC300_20260807 \
  PREFLIGHT_VICTORYMESH_SEB_STAGE2_ATLAS_STATIC300_sourceoff.in
```

The uploaded deck was round-tripped and compared byte-for-byte with the local
input before launch. It was identical. The runner created tmux session:

```text
deck_PREFLIGHT_VICTORYMESH_SEB_STAGE2_ATLAS_STATIC300_sourceoff
```

## 3. Primary stop reason

ATLAS exited with code 2 before the first `solve`:

```text
ATLAS> METHOD newton trap maxtrap=30 climit=1e-4 weak=1 itlimit=50 carr.limit=1e18 damping.factor=0.8
 ** ERROR #  3 **
 * Invalid parameter specification *
 ==> carr.limit
 ** ERROR #  3 **
 * Invalid parameter specification *
 ==> damping.factor

*** simulator exits with code 2
```

Therefore:

```text
PARSER = FAIL
VGS_0_ACCEPTED = NO
VDS_300_ACCEPTED = NO
STATIC_STR = NOT_CREATED
```

No retry or correction was performed.

## 4. Independent material/import findings

Before the METHOD fatal, ATLAS reported:

```text
Warning: Unknown material #304.
Using insulator.
```

This pair occurred 2228 times. ATLAS then read:

```text
Read 56454 nodes.
Read 111350 triangles.
Read 13 regions.
Read 3 electrodes.
```

The three imported electrodes were:

| No. | Name | x range (µm) | y range (µm) |
|---:|---|---|---|
| 1 | source | 0.0–0.5 | -0.18–0.0 |
| 2 | drain | 14.5–15.0 | -0.18–0.0 |
| 3 | gate | 1.5–6.0 | -0.20–-0.12 |

The NiO statement produced:

```text
material material=NiO ... tcon.const tc.const=2.27
Statement ignored.
```

The imported Ga2O3 statement produced warnings that `GA2O3_BETA` default
material parameters and group could not be changed. `MATERIAL region=10 mun=50`
was accepted syntactically but never reached a solve, so its runtime effect is
not evaluable. The thermcontact statements were also accepted syntactically,
but no runtime binding table or solution exists.

These are material-mapping and input-deck blockers. They are separate from the
already accepted physical track-spacing decision; no remesh is recommended.

## 5. Gate table

| Required item | Result |
|---|---|
| Frozen Stage-2 STR read | `PARTIAL_PASS` |
| Parser | `FAIL` |
| Region mapping | `NOT_VALIDATED` — 13 runtime regions, semantic mapping incomplete |
| Material mapping | `FAIL` — #304 fell back to insulator |
| Electrode mapping | `PASS_IMPORT_ONLY` — exactly source/drain/gate |
| Thermcontact mapping | `NOT_EVALUATED` |
| Region 10 result | `NOT_EVALUATED` |
| NiO thermal result | `FAIL_TO_APPLY` |
| VGS=0 accepted | `NO` |
| VDS=300 V accepted | `NO` |
| Five-point baseline | `NOT_EXECUTED` |
| Static Id/Is/Ig/Tmax/potential/|E| | `NOT_AVAILABLE` |

## 6. Scope compliance

```text
VICTORYMESH_RERUN = NO
AUTO_FIX_PERFORMED = NO
SECOND_LAUNCH = NO
STATIC_BIAS_EXECUTED = NO
SEU_TRANSIENT_EXECUTED = NO
PAIRED_TRANSIENT_EXECUTED = NO
NEW_RUN_CREATED = NO
PARAMETERS_ADJUSTED = NO
```

## 7. Evidence index

- [Executed deck](attachments/20260807_victorymesh_seb_atlas_static300_preflight/PREFLIGHT_VICTORYMESH_SEB_STAGE2_ATLAS_STATIC300_sourceoff.in)
- [Complete typescript](attachments/20260807_victorymesh_seb_atlas_static300_preflight/typescript.txt)
- [Runner exit evidence](attachments/20260807_victorymesh_seb_atlas_static300_preflight/EXIT.txt)
- [Result report](attachments/20260807_victorymesh_seb_atlas_static300_preflight/RESULT.md)
- [Warning/failure register](attachments/20260807_victorymesh_seb_atlas_static300_preflight/warning_failure_register.csv)

No STR, static log, structure image, mesh image, or 300 V table is attached
because the parser/input gate stopped before any `solve` or output generation.

## 8. Open gates and next recommendation

Before another static launch can be considered, a separately reviewed candidate
must close all four items:

1. ATLAS 5.40.0.R-valid METHOD syntax while preserving the intended solver;
2. Victory Mesh material #304 mapping without remeshing or changing geometry;
3. an ATLAS-applied NiO material/thermal assignment;
4. an auditable 13-total-region to 12-semantic-region mapping.

Recommended next action: `REVISE_STATIC_INPUT_AND_MATERIAL_MAPPING_BEFORE_RETRY`.
This handoff does not authorize deck edits or a second launch.
