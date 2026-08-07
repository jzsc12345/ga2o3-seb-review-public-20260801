# Victory Mesh conformal-minimal one-shot audit (2026-08-07)

## 0. Scope and stop boundary

Final status: `ONE_SHOT_EXECUTED / FINAL_STR_NOT_CREATED / EXECUTION_COUNT=1`.

This audit covers one structure-preserving path only:

`Stage 2 DevEdit structure -> raw STR from the same deck -> Victory Mesh conformal-minimal -> Atlas-mode STR`

It does not authorize or execute Atlas, Victory Device, `solve`, bias, SET, SEB, or a second Victory Mesh run.

## 1. Frozen files

- lineage source: `decks/PREFLIGHT_VICTORYMESH_SEB_STAGE2_conformal_x10p25.in`
- one-shot candidate: `decks/PREFLIGHT_VICTORYMESH_SEB_ONESHOT_conformal_minimal_interfaces_x10p25.in`
- read-only analyzer: `scripts/analyze_victorymesh_contract.py`
- Stage 1 STR: `E:/silvaco2425/bulk/str/VICTORYMESH_SEB_20260807/VM_SEB_STAGE1_conformal_baseline.str`
- Stage 2 STR: `E:/silvaco2425/bulk/str/VICTORYMESH_SEB_20260807/VM_SEB_STAGE2_conformal_track_x10p25.str`

The final candidate STR path was reserved as:

`E:/silvaco2425/bulk/str/VICTORYMESH_CONFORMAL_CONTRACT_20260807/VM_SEB_ONESHOT_CANDIDATE_conformal_minimal.str`

It was **not created**.  The only generated candidate-side STR is the
pre-remesh DevEdit raw structure; it is retained as failure-boundary evidence
and is not presented as the requested final Victory Mesh candidate.

## 2. Official syntax evidence

| Decision | Evidence | Result |
|---|---|---|
| Minimal conformal route | local `victorymesh_users1.txt`, §10.1.3, lines 6364–6384 | `REMESH CONFORMAL SIMPLEX.MINIMAL` is the supported 2-D minimal conformal route. |
| AABB size meaning | same section, lines 6373–6380 | conformal size is the axis-aligned bounding box; size accepts per-axis x/y values. |
| No `MAX.DISTANCE` | same section, lines 6380–6384 | approximation-distance refinement is not supported for minimal conformal. |
| Region size | manual §11.57 and UMOS §10.11.2 | `REFINE ... MAX.SIZE="x,y"` is documented. |
| Interface size | manual §10.7 and UMOS example around lines 7166–7170 | `MAX.INTERFACE.SIZE="x,y"` with `INTERFACE.REGIONS` and `OTHER.INTERFACE.REGIONS` is documented. |
| Local shape | manual §10.8, §4.3 and `GaN_Power_ex08.in` lines 68–94 | named `CUBOID` plus `SHAPE`/`MAX.SHAPE.SIZE` is the closest official GaN lateral-device template. |
| Unnamed region selector | manual §11.75 and `GaN_Power_Ex11.in` lines 70–77 | `TAG POINT=... VALUE=...`, selected as `USER:<VALUE>`. |

Official-example selection: `GaN_Power_ex08.in` is the primary local-shape/conformal-minimal template; `Silicon_Power_ex07.in` supplies the official interface-refinement form. `GaN_Power_Ex11.in` is used only for `TAG POINT`. No device parameters or mesh numbers were copied from these examples.

## 3. Frozen lineage and selector checks

### 3.1 Stage 2 lines 1–215

The only differences in lines 1–215 are allowed non-physics changes:

- lines 9–11: candidate identification comments;
- line 215: unique raw STR output name.

All region, polygon, material, impurity, electrode, DevEdit meshing, and structural commands remain mechanically unchanged.

### 3.2 Strict-interior tags

| Tag | Point (µm) | Source-region proof | Expected selection |
|---|---:|---|---|
| `REGION5` | `(0.25, 0.075)` | strict interior of source region 5 polygon `x=0..1, y=0..0.15`; channel excludes that interior | exactly region 5 |
| `SOURCE_METAL` | `(0.25, -0.10)` | strict interior of region 10 Nickel | exactly source |
| `DRAIN_METAL` | `(14.75, -0.10)` | strict interior of region 11 Nickel | exactly drain |
| `GATE_METAL` | `(3.00, -0.16)` | strict interior of the stepped region 12 Nickel top bar | exactly gate |

Runtime INFO verification remains a pre-run gate: zero or multiple matches blocks execution.

## 4. Frozen source adjacency matrix

Finite-length adjacency was independently checked from the source geometry and the existing Stage 2 STR topology. A common corner alone was excluded.

| Pair | Expected | Finite shared length in Stage 2 (µm) | Candidate interface rule |
|---|---:|---:|---:|
| ga2o3 / sio2 | NOT_PRESENT | 0 | no |
| ga2o3 / al2o3 | PRESENT | 14.0 | yes |
| ga2o3 / nio | NOT_PRESENT | 0 | no |
| nio / al2o3 | PRESENT | 2.0 | yes |
| sio2 / nickel | PRESENT | 2.9 total | yes, split by terminal |
| al2o3 / nickel | PRESENT | 0.04 | yes |
| sio2 / al2o3 | PRESENT | 12.0 | yes |
| sio2 / nio | PRESENT | 0.20 | yes |
| nio / nickel | PRESENT | 2.0 | yes |
| ga2o3 / nickel | PRESENT | 1.0 | yes, source/drain split |

## 5. Predeclared measurement implementation

For each triangle intersecting a closed ROI:

- `dx = max(vertex x) - min(vertex x)`;
- `dy = max(vertex y) - min(vertex y)`;
- P95 = `numpy.percentile(values, 95, method="linear")`.

The same script and definitions are used for Stage 1, Stage 2, and the candidate. Full-y continuity merges the intersections of `x=10.25` with ga2o3 triangles and requires continuous coverage of `y=0..0.60`.

Frozen clean-drift windows for the two otherwise unspecified horizontal semantic boundaries are:

- substrate/uid: `x=6.50..7.50, y=0.375..0.425`;
- uid/channel: `x=6.50..7.50, y=0.175..0.225`.

## 6. Stage 1/2 measured baselines frozen before execution

| Metric | Stage 1 | Stage 2 | Candidate gate/policy |
|---|---:|---:|---|
| nodes | 38,359 | 56,454 | efficiency target only |
| elements | 75,458 | 111,350 | efficiency target only |
| track DX max (µm) | 0.0366047 | 0.0150000 | <= 0.016 |
| track DY max (µm) | 0.0400000 | 0.0166667 | <= 0.016 |
| full-y continuity | PASS | PASS | PASS |
| gate drain-edge DX max (µm) | measured in CSV | 0.0200000 | <= 0.010 |
| gate drain-edge DY max (µm) | measured in CSV | 0.00906164 | <= 0.010 |
| channel/region5 DX max (µm) | measured in CSV | 0.0200000 | <= 0.025 |
| channel/N_D DX max (µm) | measured in CSV | 0.0506551 | <= 0.025 |
| substrate/uid normal DY max (µm) | measured in CSV | **0.0153846154** | candidate <= this value |
| uid/channel normal DY max (µm) | measured in CSV | **0.0166666667** | candidate <= this value |
| Al2O3 min intervals | measured in CSV | 4 | >=4; DY max <=0.005 |
| NiO P- min intervals | measured in CSV | 10 | >=5; DY max <=0.010 |
| NiO P+ min intervals | measured in CSV | 10 | >=5; DY max <=0.010 |

Stage 2 evidence is under `outputs/preflight/VICTORYMESH_CONFORMAL_CONTRACT_20260807/stage2/`.

## 7. Frozen anisotropic mesh policy

The candidate contains zero Victory Mesh `LINE` commands. Geometry boundaries remain in the conformal source; local resolution is carried by region, interface, and named-shape refinements.

Tangential targets were derived from Stage 2 adjacent-triangle AABBs before candidate execution:

| Interface/orientation | Candidate `(x,y)` max size (µm) | Stage 2 non-critical-axis anchor |
|---|---:|---:|
| ga2o3/al2o3 horizontal | `(0.050,0.005)` | tangential DX 0.050655 |
| nio/al2o3 horizontal | `(0.020,0.005)` | tangential DX 0.020000 |
| sio2/al2o3 horizontal | `(0.050,0.005)` | tangential DX 0.050655 |
| al2o3/nickel vertical | `(0.005,0.005)` | short 0.020-µm interface; stricter Al2O3 gate |
| sio2/nio vertical | `(0.010,0.020)` | tangential DY 0.005 already bounded by NiO region policy |
| nio/nickel horizontal | `(0.020,0.010)` | tangential DX 0.020000 |
| sio2/source or drain vertical | `(0.010,0.025)` | tangential DY 0.005; normal contract dominates |
| sio2/gate mixed | `(0.010,0.010)` | mixed orientation and high-field participation |
| ga2o3/source or drain horizontal | `(0.050,0.025)` | Stage 2 tangential DX up to 0.0983; local contact policy tightened |

Local shapes are frozen as:

- strike: `x=10.10..10.40, y=0..0.60`, max size `(0.015,0.015)`;
- gate edge: `x=5.95..6.05, y=-0.20..-0.12`, max size `(0.010,0.010)`.

## 8. Static safety scan

Current local scan:

- active `go devedit`: 1;
- active `go victorymesh`: 1;
- active `go atlas` / `go victorydevice`: 0;
- active `solve`, `singleeventupset`, `tfinal`, bias ramp: 0;
- `REMESH`: one, `CONFORMAL SIMPLEX.MINIMAL`;
- `MAX.DISTANCE`: 0;
- Victory Mesh `LINE`: 0;
- output names are unique and do not overwrite Stage 1/2;
- project deck-ban scanner: PASS.

## 9. Pre-run gate table

| Gate | Status before remote execution | Evidence |
|---|---|---|
| `PRE_RUN_LINEAGE_DIFF` | PASS | §3.1; exact line comparison |
| `SELECTOR_VALIDATION` | PASS, runtime INFO confirmation required | §3.2; manual §11.75 |
| `REGION5_TAG_SELECTION` | PASS, runtime INFO confirmation required | strict interior geometry proof |
| `ADJACENCY_CHECK` | PASS | §4 and Stage 2 shared-edge audit |
| `SYNTAX_CHECK` | PASS | §2 manual and official examples |
| `OUTPUT_PATH_CHECK` | PASS | unique candidate names and non-RUN preflight path |
| `FORBIDDEN_COMMAND_SCAN` | PASS | §8 |
| `MEASUREMENT_WINDOWS_FROZEN` | PASS | §§5–7 |
| `STAGE2_BASELINE_GATES_RECORDED` | PASS | §6 |

## 10. Post-run result

### 10.1 Execution identity

| Item | Actual value |
|---|---|
| host / SSH route | established alias `silvaco` -> host `tcad` |
| remote directory | `/root/DECKBUILD/preflight/VM_ONESHOT_CONFORMAL_MINIMAL_20260807` |
| runner | `/root/bin/vdoe_tmux.sh start-deck` |
| tmux session | `deck_PREFLIGHT_VICTORYMESH_SEB_ONESHOT_conformal_minimal_interfaces_x10p25` |
| exact launch | `/root/bin/vdoe_tmux.sh start-deck /root/DECKBUILD/preflight/VM_ONESHOT_CONFORMAL_MINIMAL_20260807 PREFLIGHT_VICTORYMESH_SEB_ONESHOT_conformal_minimal_interfaces_x10p25.in` |
| DeckBuild | `5.2.40.R` |
| DevEdit | `2.8.26.R` |
| Victory Mesh | `1.12.0.R`, four CPUs |
| start | `2026-08-07 14:05:01 CST` |
| stop evidence | `2026-08-07 14:35:54 CST`, controller elapsed about 30 min 52.5 s |
| Victory phase | about 1,825 s from the Victory banner to signal handling; no final output |
| exit | signal 2, simulator exit code `130` |
| authorized Victory executions | **1 of 1** |

The uploaded input and the returned executed input are byte-equal by direct
comparison without hashing.  The final remote check found no residual tmux
session and no Atlas, Victory Mesh, DeckBuild, or DevEdit process.

### 10.2 What completed and where it stopped

1. DevEdit completed and wrote
   `VM_SEB_ONESHOT_CANDIDATE_devedit_raw.str` (617,727 bytes); it was
   archived under `E:/silvaco2425/bulk/str/VICTORYMESH_CONFORMAL_CONTRACT_20260807/`.
2. All four strict-interior `TAG POINT` selectors returned one intended
   material: region 5 -> `ga2o3`; source/drain/gate -> `nickel`.
3. `INFO` reported the source structure, dopants and three electrodes.
4. `REMESH CONFORMAL SIMPLEX.MINIMAL` completed.
5. All twelve region `MAX.SIZE` refinements completed and returned to the
   Victory prompt.
6. The first same-material semantic-boundary command,
   `substrate/uid MAX.INTERFACE.SIZE="0.10,0.015"`, printed 100% progress but
   did not return to the prompt.
7. The transcript stopped growing while resident memory reached about
   7.2 GiB and swap reached about 6.3 GiB.  A five-second process sample
   showed about 4,740 major faults/s and about 20.8 MiB/s reads: this was swap
   thrash rather than productive mesh output.
8. After the frozen 30-minute no-progress boundary, the exact tmux job was
   interrupted.  No parameter was changed, no fallback was used, and no
   second execution occurred.

This localizes the failure boundary to the first whole-interface,
same-material semantic refinement.  It does **not** prove a parser failure,
SSH/runner failure, source-structure failure, or a general failure of
`CONFORMAL SIMPLEX.MINIMAL`.  The exact internal Victory Mesh defect or
complexity mechanism remains unproven.

## 11. Pre-remesh structure evidence

The raw STR is valid evidence that the mechanically preserved Stage 2
structure reached Victory Mesh; it is not post-remesh acceptance evidence.

| Raw-structure item | Measured |
|---|---:|
| points | 5,045 |
| triangles | 9,802 |
| computed obtuse triangles | 0 |
| source region declarations / unique semantic names | 12 / 12 |
| raw runtime region records | 12 |
| oxide connected components (triangle topology) | 2 |
| electrodes | 3: `source`, `drain`, `gate` |
| track ROI DX max | 0.3125 µm (pre-remesh diagnostic only) |
| track ROI DY max | 0.0250 µm (pre-remesh diagnostic only) |
| full-y semiconductor continuity | PASS |

The analyzer was corrected during post-review so that connected components
are counted from triangle edge connectivity, not from serialized runtime
record count.  It was then re-run on Stage 1, Stage 2 and the raw candidate;
all three report two oxide components.  This correction changes no mesh and
does not invoke a simulator.

`POST_RUN_STR_PRESERVATION` is `NOT_EVALUABLE`: the final remeshed STR does
not exist.  Geometry, material, doping and electrode preservation are proven
only up to the pre-remesh raw STR boundary.

## 12. Stage 1 / Stage 2 / one-shot comparison

The same triangle-AABB analyzer was used for the two completed baselines.
Candidate values are not substituted with raw-STR or requested-refinement
values.

| Metric | Stage 1 | Stage 2 | One-shot candidate |
|---|---:|---:|---:|
| remesh | `CONFORMAL` | `CONFORMAL` | `CONFORMAL SIMPLEX.MINIMAL` |
| final nodes | 38,359 | 56,454 | `NOT_AVAILABLE` |
| final elements | 75,458 | 111,350 | `NOT_AVAILABLE` |
| final STR bytes | 7,379,545 | 11,127,049 | `NOT_AVAILABLE` |
| Victory `LINE x` / `LINE y` | 10 / 11 | 13 / 11 | 0 / 0 |
| track DX max (µm) | 0.0366047 | 0.0150000 | `NOT_EVALUABLE` |
| track DY max (µm) | 0.0400000 | 0.0166667 | `NOT_EVALUABLE` |
| full-y continuity | PASS | PASS | `NOT_EVALUABLE` |
| Al2O3 intervals / DY max | 4 / 0.0050 | 4 / 0.0050 | `NOT_EVALUABLE` |
| NiO P- intervals / DY max | 10 / 0.0050 | 10 / 0.0050 | `NOT_EVALUABLE` |
| NiO P+ intervals / DY max | 10 / 0.0050 | 10 / 0.0050 | `NOT_EVALUABLE` |
| material-interface coverage | measured; several frozen gates fail | same | `NOT_EVALUABLE` |
| semantic-boundary coverage | measured; `channel/N_D` fails | same except denser horizontal boundaries | `NOT_EVALUABLE` |
| gate-edge DX / DY max (µm) | 0.0201741 / 0.00906164 | 0.0200000 / 0.00906164 | `NOT_EVALUABLE` |
| successful Victory time | 13.10 s | 14.71 s | >1,825 s, terminated, no final STR |

### MESH_SIZE_COST_PROXY

Relative to Stage 1, Stage 2 has 1.472x nodes, 1.476x elements and 1.508x
STR size.  These are mesh-size proxies only.  The one-shot candidate has no
final mesh, so no node, element or STR-size ratio exists.  Its >1,825-second
failed Victory phase is reported as a generation failure, not as an estimate
of Atlas/SEB runtime or memory.

## 13. Frozen acceptance table

| GATE | FROZEN_THRESHOLD | MEASURED_RESULT | STATUS | EVIDENCE |
|---|---|---|---|---|
| lineage | Stage 2 lines 1-215 unchanged except allowed labels/paths | mechanical comparison passed; raw structure generated | PASS | candidate deck; §3 |
| selector validation | each strict-interior tag selects exactly one intended region | four tags each returned one intended material | PASS | `typescript` INFO block |
| source semantic topology before remesh | 12 semantic regions; oxide components=2; 3 electrodes | 12 / 2 / 3 | PASS — PRE-REMESH | raw STR analyzer |
| syntax / forbidden commands | official conformal-minimal syntax; no Atlas/solve/transient | commands parsed through first interface rule; forbidden count zero | PASS | candidate deck; `typescript` |
| execution count | at most 1 | 1 | PASS | remote workdir and controller evidence |
| final candidate STR | one Atlas-mode Victory Mesh STR must exist | not created | **FAIL** | remote directory listing |
| post-remesh structure preservation | semantic geometry/components/material/doping/electrodes unchanged | no final STR | NOT_EVALUABLE | required output absent |
| track DX max | <=0.016 µm | no final STR | NOT_EVALUABLE | required output absent |
| track DY max | <=0.016 µm | no final STR | NOT_EVALUABLE | required output absent |
| full-y continuity | PASS | no final STR | NOT_EVALUABLE | required output absent |
| Al2O3 | >=4 intervals; normal max <=0.005 µm | no final STR | NOT_EVALUABLE | required output absent |
| NiO P- | >=5 intervals; normal max <=0.010 µm | no final STR | NOT_EVALUABLE | required output absent |
| NiO P+ | >=5 intervals; normal max <=0.010 µm | no final STR | NOT_EVALUABLE | required output absent |
| gate drain-side ROI | DX and DY max <=0.010 µm | no final STR | NOT_EVALUABLE | required output absent |
| channel/region5 | DX max <=0.025 µm | no final STR | NOT_EVALUABLE | required output absent |
| channel/N_D | DX max <=0.025 µm | no final STR | NOT_EVALUABLE | required output absent |
| substrate/uid | candidate normal max <=0.0153846154 µm | no final STR | NOT_EVALUABLE | required output absent |
| uid/channel | candidate normal max <=0.0166666667 µm | no final STR | NOT_EVALUABLE | required output absent |
| present material interfaces | frozen normal gates in §12 of authorization | no final STR | NOT_EVALUABLE | required output absent |
| no device simulation | no Atlas/Victory Device/solve/bias/transient | none executed | PASS | deck scan; transcript; final process check |
| no fallback/retune | zero fallback and no second mesh execution | none | PASS | controller history and unchanged candidate |

## 14. Bug review and first-principles simplification

### 14.1 Candidate-deck review

- No geometry, material, doping, electrode, contact or physical-model line was
  changed in the preserved structure body.
- No illegal device-simulation command exists.
- Selector tokens and all region `MAX.SIZE` commands are runtime accepted.
- The failing semantic-interface command is syntactically accepted but is not
  operationally viable on this structure under the observed resource limit.
- Because the failure occurred before every material-interface and local-shape
  rule, those later rules are **not runtime validated**.

### 14.2 Proposed next-round diff only — not implemented

The same physical intent can be expressed with fewer global interface
operations:

1. delete the four whole-interface same-material
   `MAX.INTERFACE.SIZE` rules;
2. replace them with four named local CUBOID shapes at the already frozen
   semantic-boundary measurement windows;
3. preserve the strict region tags and coarse region `MAX.SIZE` policies;
4. retain only physically present material-interface rules, but review each
   long interface for a local-shape replacement where only a high-field or
   contact segment carries a numerical gate;
5. place the strike and gate-edge local shapes before optional broad material
   interface refinements so the critical contract is explicit and auditable.

This proposal stays within `CONFORMAL SIMPLEX.MINIMAL`; it does not switch to
Delaunay and does not restore fine global `LINE y` planes.  It needs a new
review and a separately authorized run.  No such edit or second run was made.

## 15. Evidence and scope closure

Primary deliverables:

1. candidate deck:
   `decks/PREFLIGHT_VICTORYMESH_SEB_ONESHOT_conformal_minimal_interfaces_x10p25.in`;
2. final candidate STR: **not generated because the unique execution failed**;
   retained pre-remesh evidence is
   `E:/silvaco2425/bulk/str/VICTORYMESH_CONFORMAL_CONTRACT_20260807/VM_SEB_ONESHOT_CANDIDATE_devedit_raw.str`;
3. this audit report.

Supporting evidence:

- complete `typescript.log` and exit record under
  `outputs/preflight/VICTORYMESH_CONFORMAL_CONTRACT_20260807/candidate/`;
- `execution_resource_samples.csv`;
- `warning_failure_register.csv`;
- `stage1_stage2_candidate_comparison.csv`;
- Stage 1, Stage 2 and candidate-raw analyzer CSV/JSON outputs;
- analyzer source: `scripts/analyze_victorymesh_contract.py`.

No structure/mesh PNG for the final candidate exists because there is no final
candidate STR.  No screenshot or raw-STR picture is relabeled as a final mesh.

Unauthorized actions remained zero: Atlas, Victory Device, solve, bias, SET,
SEB, transient, transport remap, automatic retune, second Victory execution,
branch, worktree, commit and push.

Final local verification:

- candidate deck-ban scan: PASS;
- executed-input direct byte comparison against the local candidate: PASS
  (no hash used);
- analyzer `py_compile`: PASS;
- Stage 1 / Stage 2 / candidate-raw analyzer rerun: PASS;
- analyzer has no SSH or simulator invocation path;
- layout checker still reports 207 pre-existing repository violations, but
  reports zero violation whose path belongs to this task after moving the raw
  STR to the required `E:/silvaco2425/bulk/str/` archive and using permitted
  text/log extensions for lightweight evidence.

EXECUTION_COUNT: 1

MESH_ONLY_VERDICT: FAIL
