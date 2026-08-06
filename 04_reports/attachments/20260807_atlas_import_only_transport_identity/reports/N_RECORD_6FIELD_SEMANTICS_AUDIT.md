# SDB ASCII `n`-record payload audit

## Observed records

Pre-resave source STR first matching record:

```text
n 0 77 13 0 0 0 0
```

ATLAS-mode transport-mapped STR first matching record:

```text
n 0 77 13 0 0 0 0 0 0
```

The line token count changes from 8 to 10, or from four to six numeric payload
values after the leading record/index fields.  The preceding invariance audit
already established that the donor and acceptor scalars used there remained
unchanged.  It did not establish the semantics of all six output payload
positions.

## Verdict

```text
N_RECORD_6FIELD_SEMANTICS = NOT_DEMONSTRATED
```

Reason: the installed Victory Mesh manual documents SDB only as a proprietary
interchange container and provides no six-field record schema.  The import-only
runtime ended before ATLAS read the STR, so it adds no runtime interpretation.

