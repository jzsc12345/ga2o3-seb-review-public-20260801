# A1_REV2 warning and fatal register

> Scope: the single authorized DevEdit execution on 2026-08-07.
>
> Source: the complete `typescript.txt`, `EXIT.txt`, and the read-only kernel log line in
> `A1_REV2_REMOTE_STATE_AND_FAILURE_EVIDENCE.txt`.

## Summary

| Class | Count | Adjudication |
|---|---:|---|
| `Material WARNING` transcript lines | 4 | Preserved; execution continued past them |
| explicit `Parse Error` / `Parse complete` status | 0 | Parser completion was not reached |
| literal `fatal` token | 0 | Absence of a literal token does not override the process crash |
| exit-code-11 records | 2 | `simExited` plus runner exit record |
| kernel `devedit.exe` segfault records captured | 1 | Runtime-fatal process crash |

## Material warnings

The transcript records two warnings after region 3 and two after region 6:

```text
Material WARNING: Using material by number (50). Extraneous text ignore ...
Material WARNING: Using material by number (50). Extraneous text ignore ...
```

The non-printable suffix is retained in the raw transcript. These warnings did not trigger
an automatic stop or any packet modification.

## Fatal runtime event

The final DevEdit action was an inherited x-refinement card. The transcript then records:

```text
simExited with exitcode11
*** simulator exits with code 11
```

The VM kernel log independently records a `devedit.exe` segmentation fault for that process.
No STR was written. The correct label is:

```text
DEVEDIT_SEGFAULT
STR_NOT_CREATED
A1_REV2_MESH_CONTRACT_FAIL
```

This is not evidence of an ATLAS, static-bias, SEU, or paired-transient failure because none
of those stages was entered.
