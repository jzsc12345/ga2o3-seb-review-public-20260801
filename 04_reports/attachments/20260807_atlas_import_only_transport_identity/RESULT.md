# ATLAS import-only transport-identity gate — runtime result

> Status: `INPUT_OPEN_FAILED / IMPORT_TRANSPORT_IDENTITY_NOT_EVALUABLE`
>
> Execution count: one; no retry, fallback, solve, bias, or transient.

## Result

The frozen three-line deck started ATLAS 5.40.0.R and issued only:

```text
go atlas simflags="-V 5.40.0.R -P 4"
mesh infile="<frozen transport-mapped STR>"
quit
```

ATLAS stopped while opening the input STR:

```text
Error: Could not open MASTER file ..._atlas_transpo.
ATLAS version 5.40.0.R aborted
simExited with exitcode1
```

The frozen remote STR still existed after the run, was 12,735,490 bytes, and
had mode 644.  The requested path contains 145 characters; the path shown in
the ATLAS error contains a 132-character prefix plus a final dot (133 display
characters).  This supports, but does not prove, a path-truncation hypothesis.
No input correction or second execution was authorized or performed.

## Adjudication

| Gate | Result |
|---|---|
| ATLAS process start | PASS |
| Frozen `MESH INFILE` statement reached | PASS |
| Input STR opened | FAIL |
| Region/material table | NOT_OBSERVABLE |
| Electrode table | NOT_OBSERVABLE |
| Doping table | NOT_OBSERVABLE |
| GaN code 124 import identity | NOT_EVALUABLE |
| ZnO code 209 import identity | NOT_EVALUABLE |
| Parent-default leakage | NOT_EVALUABLE |

This is not a material-identity failure and not evidence that GaN or ZnO is
accepted or rejected by ATLAS.

## Prohibited actions confirmed absent

```text
MATERIAL/MOBILITY/MODELS/IMPACT/INTERFACE/THERMCONTACT/METHOD = 0
SOLVE/SOLVE INIT/LOAD/SAVE/BIAS/TRANSIENT = 0
VICTORY MESH/DEVEDIT/REMESH = 0
SECOND LAUNCH/AUTO FALLBACK = 0
```

