# RUN120 parser-only material/model closure — sanitized summary

Verdict: `PASS_PARSER_AND_CORE_REGIONAL_CLOSURE / STOP_FULL_PARENT_ISOLATION / NO PHYSICS CONCLUSION`.

RUN120 was a parser-only check using a frozen mesh. It executed model printing and initialization;
it did not perform a voltage ramp, particle transient, or self-heating solve.

Across regions 3–7, the printed core band, density-of-states, incomplete-ionization, baseline SRH,
Auger, mobility, impact, and model-flag values matched the deck targets. The regional values are in
[the material/model matrix](RUN120_regional_material_model_matrix.csv).

The check also found an active parent-material inheritance: `LT.TAUN=LT.TAUP=1.42` was present in
all five regions even though the production deck had not explicitly set those slots. Because the
production transient uses lattice temperature, this blocked a claim of complete parent-material
isolation. BGN values were printed but the BGN model flag was inactive. The Richardson constants
remained unresolved for the then-current contact boundary. Thermal constants were parser echoes in
this run and were not evidence of a thermal runtime solve.

RUN121 remained unapproved and unrun. Source summary SHA-256:
`25FF65989AFC81D2E66D699B65F600FD973D9336C70C7B43D06B9DEA4337D09F`.
