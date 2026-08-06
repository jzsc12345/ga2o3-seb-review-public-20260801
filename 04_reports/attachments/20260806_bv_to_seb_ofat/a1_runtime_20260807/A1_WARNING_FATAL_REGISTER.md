# A1 warning and fatal register

## Runtime summary

- Fatal records: 0
- Parse error summary: 0
- Parse warning summary: 0
- Material warning records in the full transcript: 8
- ATLAS errors: not applicable; ATLAS was not executed

## Material warnings retained from `typescript.txt`

| Transcript lines | Context | Message |
|---|---|---|
| 105, 107 | region 2, user material 50 | `Material WARNING: Using material by number (50). Extraneous text ignore ...` |
| 117, 119 | region 3, user material 50 | same warning |
| 143, 145 | region 6, user material 50 | same warning |
| 161, 163 | region 8, user material 51 | `Material WARNING: Using material by number (51). Extraneous text ignore ...` |

The final DevEdit `Parse complete` block reports `Warning(s)=0` despite these eight earlier messages. Both facts are preserved; the earlier warnings are not reclassified as fatal and are not silently discarded.
