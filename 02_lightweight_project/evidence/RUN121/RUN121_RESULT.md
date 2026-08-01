# RUN121 result — Wang Z/[001] impact OFAT at 1000 V through 500 ns

## Verdict

`RUN_VALID_TO_500NS / STATIC_GATE_PASS / SOURCE_GATE_PASS / NATURAL_FINISH / ERROR_COUNT_0`

RUN121 executed the authorized single-variable change: regions 3–7 use the paired electron/hole
Wang Z/[001] Selberherr group `A=7.06e5 cm^-1`, `B=2.10e7 V/cm` instead of the frozen RUN096
Y/[010] group `A=2.16e6 cm^-1`, `B=1.77e7 V/cm`. Structure, mesh, LT.TAU, UID, substrate,
mobility, thermal model, ion source, solver, compliance, and the time schedule through 500 ns were
unchanged. The candidate deck SHA-256 is
`0DB0ABE8E5BA83DE340DA376679A7486FA1C6C8184658F1DCDD629B01BDCBFBF`.

The Z/[001] group materially weakens the post-strike impact/current path under this frozen case.
This is a strong sensitivity result for the selected impact parameter group; it is not evidence
that Wang 2026 has been fitted and it does not establish that the material parameters are correct.

## Admission and completion gates

| Gate | Observed result | Verdict |
|---|---:|---|
| Static accepted points | 219 | PASS |
| Last accepted VDS | 1000.000 V | PASS |
| Static current at 1000 V | `-2.086305028e-15 A/um` | PASS |
| Maximum static absolute current | `2.184003738e-15 A/um` | PASS |
| Prestrike signed path diagnostic | `1.20686462e-13 A/cm^2` | no high-current path |
| Deposited charge | `2.4355067009 pC/um` versus `2.423015 pC/um` target (`+0.516%`) | PASS |
| Last accepted transient time | `500 ns` | PASS |
| ATLAS terminal state | natural `5.40.0.R finished`; `Error(s)=0` | PASS |
| Fatal markers | `Cannot trap=0`, `ATLAS DIED=0`, `Command Error=0` | PASS |

The production runner's `EXIT.txt` remained empty because its phrase-based extractor did not
match this transcript. No process return-code claim is made from that file. Completion is supported
instead by the natural ATLAS finish marker, zero reported errors, accepted 500 ns SSF row, final
STR snapshot, and zero remaining simulator process/session.

## Frozen-baseline comparison

Terminal values are exact accepted SSF rows. Connectivity is the same native-STR-vertex Delaunay,
signed drain-to-source widest-path diagnostic used for the frozen RUN096 baseline; it is not an
integrated terminal current.

| Time | RUN121 Id (A/um) | Id vs RUN096 | RUN121 ImpactMax (cm^-3 s^-1) | Impact vs RUN096 | RUN121 Tmax (K) | Tmax vs RUN096 | RUN121 signed path (A/cm^2) | Path vs RUN096 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 ps | `4.057886254e-4` | `-7.43%` | `3.797802882e28` | `-36.76%` | `318.1302` | `-7.859 K` | — | — |
| 50 ns | `4.082966040e-6` | `-25.13%` | `1.947008655e25` | `-93.46%` | `332.2487` | `-9.932 K` | `27.7551` | `-85.37%` |
| 100 ns | `1.689163037e-6` | `-24.97%` | `8.085619180e24` | `-93.12%` | `324.7359` | `-7.587 K` | `10.7976` | `-82.81%` |
| 500 ns | `5.375394559e-7` | `-18.22%` | `2.521804966e24` | `-91.89%` | `315.2054` | `-3.919 K` | `3.59746` | `-73.56%` |

The signed bottleneck moves from RUN096's approximately `(14.6484, 0.01875) um` to RUN121's
approximately `(11.8047, 0.01875) um` at all three late milestones. The changes follow the
pre-registered expected direction, so the `SOLVER_BRANCH_AUDIT_REQUIRED` reversal condition is
not triggered. At 100 ps, local JouleMax is `+32.35%` even while Tmax is lower; that early local
redistribution is retained as an observation and is not generalized into a late-time mechanism.

Accepted RUN121 temperatures ranged from `299.9994867 K` to `372.4318852 K`. The maximum occurred
near `0.764 ns`; it is an accepted-row peak, not a rejected Newton trial.

## Solver rejection disclosure

The transient reached 500 ns by adaptive time-step reduction, not by a warning-free path:

- 65 trials were rejected with “repeat with smaller time-step”;
- 17 rejected trials reached the configured temperature limits, including 120 K and 5000 K
  boundary values;
- 8 trials exhausted 50 Newton iterations;
- 22 `BLOCK.TRAN` advisory warnings occurred;
- the accepted SSF curve contains none of those rejected temperature-limit states.

These are non-fatal convergence-history facts, not silently discarded results. They limit the
claim to the accepted trajectory and motivate caution about extrapolating beyond 500 ns.

## Spatial and topology evidence

- [Terminal/current/temperature/impact overlay](figs/RUN096_121_zimpact_terminal_overlay.png)
- [Four-field shallow zoom](figs/RUN121_fourfield_shallow_zoom.png)
- [Four-field full depth](figs/RUN121_fourfield_full_depth.png)
- [Native-vertex signed paths](figs/RUN096_121_native_vertex_paths.png)
- [Compact result table](csv/RUN121_result_summary.csv)
- [Exact milestone table](csv/RUN096_121_zimpact_milestones.csv)
- [Execution and warning audit](csv/RUN121_execution_audit.csv)
- [Native-vertex metrics](csv/RUN096_121_native_vertex_metrics.csv)
- [Directed-path sign check](csv/RUN096_121_directed_path_signcheck.csv)
- [Spatial maxima](csv/RUN121_spatial_maxima.csv)
- [Prestrike path diagnostic](csv/RUN121_prestrike_path_diagnostic.csv)
- [Restricted-input hash inventory](csv/RUN121_restricted_provenance.csv)
- [Lightweight bundle manifest](csv/RUN121_bundle_manifest.csv)

The regular-grid VictoryExtract closure produced 16/16 heatmap CSVs. A first extractor attempt
with seven fields in one command failed in VictoryExtract's regular-expression stack before
producing a CSV; it was stopped without Atlas. Splitting the command into the proven five-field
topology extraction plus two-field electric/temperature extraction succeeded. A separate
VictoryExtract-only native-vertex pass produced 3/3 CSVs. Every transferred raw CSV matched its
remote SHA-256; raw heatmaps, STR files, logs, and terminal transcripts remain outside GitHub.

## A14 and source review

- [Structure image](a14/RUN121_preflight_structure_RUN096_identical.png)
- [Track/mesh image](a14/RUN121_preflight_track_mesh_RUN096_identical.png)
- [Full parent/candidate diff](a14/RUN096_RUN121_full_deck_diff.md)
- [Preflight contract](a14/RUN121_preflight_contract.md)
- [Frozen RUN096 parent deck](decks/RUN096_Wang2026_nofp_Lgd9_x11_hfo2hc_SEB_1000V_Et0p8_long.in.txt)
- [RUN121 candidate deck](decks/RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_short500ns.in.txt)

The two A14 images are byte-identical to the frozen RUN096 preflight images, which is expected
because geometry and mesh were not changed. The run used tmux session
`deck_RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_short500ns`; it ended naturally.

## Claim boundary

This result accepts only the completed 1000 V, Z/[001]-impact single-variable run through 500 ns.
It does not authorize or report a second variable, LT.TAU change, structure/mesh/UID/substrate/
solver change, license reconfiguration, run beyond 500 ns, history rewrite, force push, or deletion.
It does not prove a Wang 2026 fit; that requires the paper's Fig.4 current-temperature dual
trajectory and four-stage morphology to be assessed under the final parameter set.
