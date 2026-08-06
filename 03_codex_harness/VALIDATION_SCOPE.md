# Validation scope

Run from repository root:

```text
python 03_codex_harness/tools/validate_export.py --mode public
```

The validator checks current-tree file extensions and names, maximum size, high-confidence secret
shapes, absolute local paths, message/session identifiers, Markdown links, present lock-target
hashes, and the public manifest's coverage, sizes, and SHA-256 values.

It does not validate semiconductor physics, material truth, numerical convergence, the Wang 2026
fit, execution authorization, or user identity. `USER_SEAL=SEALED` is published as a byte-identical
lock/review result whose compact authorization evidence remains in the private repository.
