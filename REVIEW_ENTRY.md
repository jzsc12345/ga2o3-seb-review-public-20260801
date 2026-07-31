# Audit entry and non-negotiable checks

Please treat simulator evidence as higher priority than later handoff prose.

## Required checks

1. Ga2O3 material/model values must be traceable to the high-confidence tables,
   atlas.key, the official manuals, examples, or a cited paper. Missing values
   must be labelled unverified rather than silently inherited from GaN.
2. The forbidden impact set `an=2.5e6`, `bn=3.96e7`, `betan=1.37` must not enter
   a production deck.
3. The substrate must not be represented as shallow p-type `2e6 cm^-3` merely to
   force high resistance. The intended semi-insulating mechanism is n-type
   background plus a Fe deep acceptor, with occupancy and transport verified.
4. DevEdit source/gate/drain/field-plate contacts must remain zero-area line
   contacts. Check endpoint nodes and `common=gate` binding without restoring
   vertical x-mesh columns.
5. A Wang Fig.4 claim requires the four physical stages under the same final
   geometry and bias: prompt e-h separation, hole accumulation/compensation,
   persistent electron path, and sustained current/thermal feedback.
6. A failed static admission gate is not a transient result. RUN119 must remain
   labelled `STATIC_GATE_FAIL / NO_VALID_TRANSIENT`.
7. Current project status is not a successful Wang2026 reproduction. RUN096 is
   the frozen 1000 V baseline; its late current decays and its peak temperature
   is far below the paper target.

## Requested reviewer output

Return findings ordered by severity, cite exact repository paths and line
numbers, separate verified evidence from inference, and propose no more than
three falsifiable next experiments.
