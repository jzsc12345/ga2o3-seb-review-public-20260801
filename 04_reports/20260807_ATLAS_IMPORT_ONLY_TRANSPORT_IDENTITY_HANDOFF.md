# ATLAS 5.40 import-only GaN/ZnO transport-identity handoff

> Previous Victory resave evidence commit: `a0de908593946ce20775ccf2600adf3a2b9916a4`
>
> Result: `ATLAS_IMPORT_ONLY_INPUT_OPEN_FAILED / NO_RETRY`
>
> Identity verdict: `NOT_EVALUABLE` — neither PASS nor material failure.

## 1. Authorization and exact boundary

One minimal import-only execution was authorized and performed.  The deck
contained only `go atlas`, one `mesh infile`, and `quit`.  It contained no
material/model declarations and no solve, save, bias, or transient command.

```text
NO MATERIAL / MOBILITY / MODELS / IMPACT / INTERFACE / THERMCONTACT
NO METHOD / OUTPUT / PROBE
NO SOLVE / SOLVE INIT / LOAD / SAVE / BIAS / TRANSIENT
NO VICTORY MESH / DEVEDIT / REMESH
ONE EXECUTION ONLY / NO RETRY / NO AUTO FALLBACK
```

Environment:

| Item | Actual value |
|---|---|
| SSH alias / host | `silvaco` / `tcad` |
| Remote workdir | `/root/DECKBUILD/preflight/ATLAS_IMPORT_ONLY_A0DE908_20260807` |
| DeckBuild | `5.2.40.R` |
| ATLAS | `5.40.0.R`, `-P 4` |
| Runner | `/root/bin/vdoe_tmux.sh start-deck` |
| Execution count | 1 |
| Simulator exit | 1 |

Exact launch command:

```bash
/root/bin/vdoe_tmux.sh start-deck \
  /root/DECKBUILD/preflight/ATLAS_IMPORT_ONLY_A0DE908_20260807 \
  PREFLIGHT_ATLAS_IMPORT_ONLY_GAN_ZNO_TRANSPORT_IDENTITY.in
```

## 2. Frozen input

The input STR was not rewritten or resaved in this round:

```text
/root/DECKBUILD/preflight/VICTORYMESH_SEB_ATLAS_TRANSPORT_RESAVE_D75BFD9_20260807/
VM_SEB_STAGE2_conformal_track_x10p25_atlas_transport_mapped.str
```

Immediately after the failure, remote `stat` still reported:

```text
present = YES
size = 12,735,490 bytes
mode = 644
```

Frozen prior facts remain historical input facts, not new ATLAS results:

| Item | Frozen prior result |
|---|---|
| semantic regions | 12 |
| runtime region records | 13 |
| mesh | 56,454 nodes; 111,350 triangles; 0 obtuse |
| Ga2O3 lineage exporter identity | GaN / code 124 / runtime regions 1,2,3,6,7 |
| NiO lineage exporter identity | ZnO / code 209 / runtime regions 9,10 |
| electrodes | source, drain, gate |

## 3. Manual and record-format review

The installed ATLAS manual documents `MESH INFILE` as loading mesh, geometry,
electrodes, and doping.  It documents `MODELS PRINT` as the way to print full
material parameters and mobility defaults.  Because `MODELS` was forbidden,
the deck did not add it.

The Victory Mesh manual describes SDB as proprietary and does not define the
six-field ASCII `n` payload.  The resaved record expanded from four to six
payload values, but their full semantics cannot be proven from the installed
manual or this failed import.

```text
N_RECORD_6FIELD_SEMANTICS = NOT_DEMONSTRATED
```

## 4. Runtime result

ATLAS launched successfully, reached the frozen `MESH INFILE`, and then ended:

```text
Error: Could not open MASTER file
.../VM_SEB_STAGE2_conformal_track_x10p25_atlas_transpo.

ATLAS version 5.40.0.R aborted
simExited with exitcode1
```

No region, material, electrode, doping, or unknown-material runtime table was
produced.  Therefore all transport-identity outcomes are `NOT_EVALUABLE`.

| Gate | Verdict |
|---|---|
| ATLAS executable and license start | PASS |
| `MESH INFILE` reached | PASS |
| frozen STR opened | FAIL |
| ATLAS imported region count | NOT_OBSERVABLE |
| GaN target regions | NOT_OBSERVABLE |
| ZnO target regions | NOT_OBSERVABLE |
| unknown material 124/209 counts | NOT_OBSERVABLE |
| electrode mapping | NOT_OBSERVABLE |
| doping table | NOT_OBSERVABLE |
| `IMPORT_TRANSPORT_IDENTITY` | NOT_EVALUABLE_INPUT_OPEN_FAILED |

## 5. Root-cause boundary

The full requested path is 145 characters.  The error shows only a
132-character prefix followed by a dot (133 display characters), while the
full file exists and is readable by mode.  This supports:

```text
PATH_TRUNCATION_SUSPECTED = YES
PATH_TRUNCATION_CONFIRMED = NO
```

The displayed shortening could reflect an internal filename limit or only
error-message formatting.  It is not enough to assert causality.  The failure
occurred before material parsing, so it cannot be classified as GaN/ZnO
transport failure.

Per the one-execution authorization, the path was not shortened, the STR was
not copied to a new alias, and the deck was not run again.

## 6. Parent-default leakage scope

No parent defaults were reached or printed.  A non-execution scope is retained
for the next material review: identity and band slots; affinity, permittivity,
Nc/Nv; electron/hole mobility and high-field/temperature dependence; SRH,
Auger, BGN, incomplete ionization; thermal conductivity and heat capacity;
impact model/coefficient/exponent slots; and any default activated later by
`MODELS`.

All values remain `UNVERIFIED`; this handoff does not restore physical
Ga2O3/NiO parameters and does not authorize `MODELS PRINT` or `solve init`.

## 7. Evidence index

Paths are relative to this handoff.

- [Executed import-only deck](attachments/20260807_atlas_import_only_transport_identity/PREFLIGHT_ATLAS_IMPORT_ONLY_GAN_ZNO_TRANSPORT_IDENTITY.in)
- [Complete DeckBuild/ATLAS typescript](attachments/20260807_atlas_import_only_transport_identity/logs/typescript)
- [Runner exit marker](attachments/20260807_atlas_import_only_transport_identity/logs/EXIT.txt)
- [Runtime result](attachments/20260807_atlas_import_only_transport_identity/RESULT.md)
- [Manual evidence](attachments/20260807_atlas_import_only_transport_identity/reports/ATLAS_IMPORT_ONLY_MANUAL_EVIDENCE.md)
- [`n`-record audit](attachments/20260807_atlas_import_only_transport_identity/reports/N_RECORD_6FIELD_SEMANTICS_AUDIT.md)
- [Warning/fatal register](attachments/20260807_atlas_import_only_transport_identity/reports/warning_fatal_register.csv)
- [Parent-default leakage scope](attachments/20260807_atlas_import_only_transport_identity/reports/PARENT_DEFAULT_LEAKAGE_AUDIT_SCOPE.md)

The 12.7 MB frozen STR remains in bulk storage and is not recommitted.

## 8. Stop state and next recommendation

```text
ATLAS_IMPORT_ONLY = INPUT_OPEN_FAILED
IMPORT_TRANSPORT_IDENTITY = NOT_EVALUABLE
PHYSICS_VALIDATED = NO
EQUILIBRIUM_STR_CREATED = NO
SOLVE_INIT_EXECUTED = NO
STATIC_BIAS_EXECUTED = NO
SEU_TRANSIENT_EXECUTED = NO
AUTO_FIX_PERFORMED = NO
SECOND_LAUNCH_EXECUTED = NO
```

Recommended next gate, requiring separate review and authorization:

```text
prepare a short-path import-only packet
→ prove the short-path packet is otherwise byte/statement equivalent
→ execute once only after new authorization
→ if import succeeds, inspect runtime region/material/electrode/doping evidence
```

Do not advance to `solve init`, physics restoration, 300 V, or SEB until the
import gate is genuinely closed.
