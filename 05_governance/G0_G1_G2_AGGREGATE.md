# G0 / G1 / G2 aggregate

Only aggregate counts and original manifest hashes are public. The path-bearing manifests are not
included.

| Layer | Records | SHA-256 | Public treatment |
|---|---:|---|---|
| G0 architecture governance inventory | 6,700 | `C70AE81E72BE4E750B5BE1AB09489531ADA72D64107D80E392D12BA67FFE7AD9` | counts only |
| G1 frozen mirror inventory | 954 | `DDAF0DE251AB1A381D029A57ABC09F018CE5E9BCED6502BE5EE2ADBC27C5AE30` | counts only |
| G2 generated mirror inventory | 4,924 | `681D120DE783BC5F40AF34BABDB513F1CC46965CBDFCB0CB8005471EF4114149` | counts only |

G0 classifications:

| Classification | Count |
|---|---:|
| RUNTIME_EVIDENCE_UNVERIFIED | 4,189 |
| FROZEN_CONFIRMED | 938 |
| PROTECTED_LEGACY_UNTOUCHED | 831 |
| POST_CUTOFF_LOWER_TRUST | 653 |
| POST_CUTOFF_LOWER_TRUST_MIXED_SNAPSHOT | 54 |
| MIXED_SPLIT_REQUIRED | 15 |
| FROZEN_CONFIRMED_UNTRACKED | 11 |
| PROVENANCE_UNRESOLVED | 6 |
| USER_BASELINE_PROTECTED | 2 |
| USER_ELEVATED_EXCEPTION | 1 |

G1 contains 953 cutoff-snapshot rows and one user-elevated exception. G2 contains 4,190 runtime
evidence rows, 664 post-cutoff lower-trust rows, 54 mixed-snapshot rows, and 16 split-required rows.
