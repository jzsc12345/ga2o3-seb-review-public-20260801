# Victory Mesh conformal-minimal one-shot failure handoff

## 0. Review status and scope

```text
HANDOFF_STATUS = READY_FOR_WEB_READONLY_REVIEW
EXECUTION_COUNT = 1
MESH_ONLY_VERDICT = FAIL
FINAL_REMESHED_STR = NOT_CREATED
SECOND_VICTORYMESH_RUN_AUTHORIZED = NO
ATLAS_OR_DEVICE_SIMULATION_AUTHORIZED = NO
```

This is the single review entry for the completed Victory Mesh one-shot. It
publishes the executed deck, transcript, measurements, analyzer, and baseline
comparison. It does **not** authorize another mesh run, Atlas, Victory Device,
electrical bias, SET, SEB, or parameter changes.

The large binary STR is intentionally not committed to this public repository.
The only candidate-side STR produced was the pre-remesh DevEdit raw STR; its
local archive location and derived read-only measurements are recorded below.
It is not represented as the requested final Victory Mesh result.

## 1. Frozen objective

The authorized path was:

```text
Stage 2 DevEdit structure
  -> raw STR produced by the same deck
  -> REMESH CONFORMAL SIMPLEX.MINIMAL
  -> Atlas-mode remeshed STR
```

The candidate preserved the Stage 2 structure-generation body and replaced
only the Victory Mesh policy. It used zero Victory global `LINE x/y` commands,
no `MAX.DISTANCE`, no transport material remap, and no device-simulation
commands.

## 2. Result in one paragraph

DevEdit successfully generated the raw structure (5,045 nodes, 9,802
triangles, 0 computed obtuse triangles). Runtime `INFO` confirmed the intended
tags and the source structure. `REMESH CONFORMAL SIMPLEX.MINIMAL` and all 12
region `MAX.SIZE` operations completed. The first whole-interface,
same-material rule—`substrate/uid MAX.INTERFACE.SIZE="0.10,0.015"`—printed
100% but never returned to the Victory prompt. Resident memory reached about
7.2 GiB, swap about 6.3 GiB, and a process sample showed about 4,740 major
faults/s with no transcript progress. The only authorized execution was
interrupted after the frozen no-progress boundary. Exit code was 130 and no
final remeshed STR was created.

This localizes the observed failure boundary. It does not establish the exact
internal Victory Mesh defect, and it does not prove a general failure of
`CONFORMAL SIMPLEX.MINIMAL`.

## 3. Runtime identity

| Item | Observed value |
|---|---|
| SSH route / host | established alias `silvaco` / host `tcad` |
| Remote workdir | `/root/DECKBUILD/preflight/VM_ONESHOT_CONFORMAL_MINIMAL_20260807` |
| Runner | `/root/bin/vdoe_tmux.sh start-deck` |
| DeckBuild | `5.2.40.R` |
| DevEdit | `2.8.26.R` |
| Victory Mesh | `1.12.0.R`, four CPUs |
| Controller elapsed | about 30 min 52.5 s |
| Victory phase before stop | about 1,825 s |
| Exit | signal 2 / code 130 |
| Final process state | no residual tmux or SILVACO process |

The uploaded and returned input were directly byte-compared and matched. No
file hash was generated.

## 4. Evidence-level separation

| Layer | Result | Meaning |
|---|---|---|
| Structure lineage before remesh | PASS | Stage 2 structure body reached the remesher unchanged except approved labels/paths. |
| Selectors | PASS | `REGION5`, source, drain, and gate each selected one intended material. |
| Conformal-minimal route | PARTIAL | Base remesh and region-size rules completed. Later interface/shape rules were not reached. |
| Final candidate mesh | FAIL | Required final remeshed STR was not created. |
| Post-remesh preservation | NOT_EVALUABLE | No final STR exists. |
| Track/interface numerical gates | NOT_EVALUABLE | Requested values and raw-STR values cannot substitute for final mesh measurements. |
| Atlas / electrical / transient | NOT_EXECUTED | Outside authorization. |

## 5. Stage 1 / Stage 2 / candidate comparison

| Metric | Stage 1 | Stage 2 | One-shot candidate |
|---|---:|---:|---:|
| Remesh algorithm | `CONFORMAL` | `CONFORMAL` | `CONFORMAL SIMPLEX.MINIMAL` |
| Nodes | 38,359 | 56,454 | `NOT_AVAILABLE` |
| Elements | 75,458 | 111,350 | `NOT_AVAILABLE` |
| STR bytes | 7,379,545 | 11,127,049 | `NOT_AVAILABLE` |
| Victory `LINE x/y` count | 10 / 11 | 13 / 11 | 0 / 0 |
| Track max dx (um) | 0.0366047 | 0.0150000 | `NOT_EVALUABLE` |
| Track max dy (um) | 0.0400000 | 0.0166667 | `NOT_EVALUABLE` |
| Full-y continuity | PASS | PASS | `NOT_EVALUABLE` |
| Successful Victory time | 13.10 s | 14.71 s | no output after >1,825 s |

Stage 2 relative to Stage 1 has 1.472x nodes, 1.476x elements, and 1.508x
STR size. These are mesh-size proxies only. No claim about Atlas/SEB runtime
or memory follows from them.

## 6. Raw structure evidence

The pre-remesh raw STR is archived locally at:

```text
E:\silvaco2425\bulk\str\VICTORYMESH_CONFORMAL_CONTRACT_20260807\VM_SEB_ONESHOT_CANDIDATE_devedit_raw.str
```

Its read-only audit found:

| Item | Measured result |
|---|---:|
| Points / triangles / obtuse | 5,045 / 9,802 / 0 |
| Source semantic regions | 12 |
| Serialized runtime region records | 12 |
| Oxide connected components | 2 |
| Electrodes | 3: source, drain, gate |
| Full-y semiconductor continuity at x=10.25 um | PASS |

The connected-component analyzer uses triangle-edge connectivity rather than
serialized region-record count. The raw STR only establishes the preserved
input boundary; it is not final mesh acceptance evidence.

## 7. Candidate interpretation and proposed next-round change

The first-principles simplification identified one narrower candidate change,
which is **not implemented here**:

1. remove the four whole-interface same-material `MAX.INTERFACE.SIZE` rules;
2. replace them with named local CUBOID shapes at the already frozen semantic
   boundary measurement windows;
3. retain the accepted strict-region tags and coarse region `MAX.SIZE`
   policies;
4. retain only physically present material-interface rules, while reviewing
   long interfaces for local-shape replacement when only a limited segment
   has a numerical gate;
5. keep `CONFORMAL SIMPLEX.MINIMAL`, the local strike/gate-edge shapes, and
   zero fine global `LINE y` planes.

This is a review proposal, not an execution authorization. A second one-shot
would require a separately reviewed deck and explicit user authorization.

## 8. Questions for web-side review

Please adjudicate the published evidence and proposed simplification using:

```text
REVIEW_VERDICT:
FAILURE_EVIDENCE:
FAILURE_LOCALIZATION:
CONFORMAL_MINIMAL_ROUTE:
WHOLE_INTERFACE_SAME_MATERIAL_RULE:
LOCAL_SHAPE_REPLACEMENT:
MATERIAL_INTERFACE_POLICY:
ZERO_GLOBAL_LINE_POLICY:
SECOND_ONE_SHOT_JUSTIFIED:
MANDATORY_REVISIONS:
NEXT_AUTHORIZATION:
```

Please keep these distinctions:

- runtime failure is established;
- exact internal Victory root cause is not established;
- final mesh contracts are not evaluable without a final STR;
- no device-physics result exists.

## 9. Attachment index

The public evidence package is under
[`attachments/20260807_victorymesh_conformal_minimal_oneshot/`](attachments/20260807_victorymesh_conformal_minimal_oneshot/SOURCE_MANIFEST.md).

Primary files:

- [Full audit report](attachments/20260807_victorymesh_conformal_minimal_oneshot/VICTORYMESH_CONFORMAL_MINIMAL_ONESHOT_AUDIT_20260807.md)
- [Executed candidate deck](attachments/20260807_victorymesh_conformal_minimal_oneshot/PREFLIGHT_VICTORYMESH_SEB_ONESHOT_conformal_minimal_interfaces_x10p25.in)
- [Complete runtime transcript](attachments/20260807_victorymesh_conformal_minimal_oneshot/typescript.log)
- [Exit record](attachments/20260807_victorymesh_conformal_minimal_oneshot/EXIT.txt)
- [Resource samples](attachments/20260807_victorymesh_conformal_minimal_oneshot/execution_resource_samples.csv)
- [Warning/failure register](attachments/20260807_victorymesh_conformal_minimal_oneshot/warning_failure_register.csv)
- [Stage comparison](attachments/20260807_victorymesh_conformal_minimal_oneshot/stage1_stage2_candidate_comparison.csv)
- [Read-only analyzer](attachments/20260807_victorymesh_conformal_minimal_oneshot/analyze_victorymesh_contract.py)

## 10. Authorization closure

```text
ATLAS_EXECUTED = NO
VICTORY_DEVICE_EXECUTED = NO
STATIC_BIAS_EXECUTED = NO
SEU_TRANSIENT_EXECUTED = NO
PAIRED_TRANSIENT_EXECUTED = NO
AUTO_FALLBACK_USED = NO
SECOND_VICTORYMESH_EXECUTION = NO
TRANSPORT_REMAP_USED = NO
```

