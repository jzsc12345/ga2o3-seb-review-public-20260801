# BV → SEB conversion notes

## Deliverables

| File | Purpose |
|---|---|
| `bv_SEB_x10p25_300V.in` | The original `bv.in` structure and physics, converted from a BV sweep into a 300 V SEB transient deck |
| `mySEU_bv.c` | The supplied user-defined SEU source adapted to the present 15 µm device |
| `bv_to_SEB.patch` | Unified diff against the uploaded `bv.in` |

## Fixed choices

| Item | Value | Basis |
|---|---:|---|
| Strike position | `xion = 10.25 µm` | Midpoint between the gate edge at `x=6.0 µm` and drain-side metal edge at `x=14.5 µm` |
| Strike track | `y=0.0…0.6 µm` | Restricts generation to the present Ga₂O₃ semiconductor stack |
| Static drain bias | `300 V` | Matches the requested/current 300 V-class case rather than copying the old template’s 700 V |
| Gate bias | `0 V` | Preserved off-state setup from `bv.in` |
| LET, radius, pulse | `0.36`, `r=0.05 µm`, `T0=4 ps`, `Tc=2 ps` | Preserved exactly from the supplied `mySEU(1).c` template |
| Final transient time | `100 µs` | Gives a late-current window without copying the template’s 100 s tail |

## Main changes

1. Added one `xion` control and five nested vertical DevEdit refinement boxes around the particle track.
2. Enabled `auger` and `lat.temp`, then added source and drain thermal contacts.
3. Added `singleeventupset F.SEU=mySEU_bv.c`.
4. Removed the BV sweep from 300 V to 2100 V and the undefined loop/harness tail.
5. Replaced undefined `$Doping` and `${name}` output paths with standalone filenames.
6. Added staged transient saves from 4 ps through 100 µs.
7. Moved SEB output-field selection before transient saves.

## Static review result

`PASS` for internal consistency:

- `xion` in the deck equals `x0` in the C source;
- the strike position lies inside the gate–drain drift region;
- all five mesh windows are nested and inside the 0–15 µm work area;
- the C track bounds match the 0–0.6 µm semiconductor stack;
- transient target times are strictly increasing;
- output filenames are unique;
- no `$Doping`, `${name}`, `go internal`, or unmatched `l.end` remains.

## Not validated here

Silvaco/DeckBuild was not available in this session, so the following remain execution gates:

1. DevEdit must successfully resolve the arithmetic `set` variables in the `refine` statements.
2. The generated mesh must be inspected to confirm adequate node density across the `r=0.05 µm` track.
3. ATLAS must accept the mapped thermal-contact geometry.
4. The pre-existing lines `MATERIAL region=10 mun=50` and the NiO thermal-property syntax were preserved, not corrected.
5. The supplied temporal pulse is nonzero at `t=0`; it was preserved rather than silently changed.

Do not interpret this conversion as proof of numerical convergence or physical SEB.
