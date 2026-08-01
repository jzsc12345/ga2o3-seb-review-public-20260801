# RUN122 parent-slot parser closure — sanitized summary

Verdict: `PASS_LTTAU_PARENT_CLOSURE / PARSER_ONLY / NO PHYSICS CONCLUSION`.

RUN122 was a parser-only check using the frozen RUN096 mesh. It executed model printing and
initialization only; it did not perform a voltage ramp, lattice-temperature solve, particle
transient, or result-file production.

ATLAS accepted explicit `LT.TAUN=LT.TAUP=0` in regions 3–7 while retaining
`TAUN0=TAUP0=1.2e-8 s`. Apart from the two LT slots, the compared RUN120/RUN122 model summaries
matched. The regional values are in
[the parent-slot matrix](RUN122_regional_parent_slot_matrix.csv).

This proves parser binding only. It does not establish that real β-Ga₂O₃ lifetime is temperature
independent and does not predict a corrected thermal transient. The printed Richardson constants
were classified as inactive for the then-current contact configuration. Carrying the zero values
into a 500 ns experiment would be a new physics change requiring separate authorization. RUN121
also remained a separate, unapproved OFAT arm.

Source summary SHA-256:
`1CF24AD3FBAAA1CE93DB0AC01B3F41036DA3D9E6CA57CB8B4A705BAE1F70B58A`.
