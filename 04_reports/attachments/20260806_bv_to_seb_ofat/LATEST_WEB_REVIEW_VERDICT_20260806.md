# Latest web-side formal re-review — OFAT documentation alignment

> Source: user-pasted formal web-side re-review
>
> Date received: 2026-08-06
>
> Authority: governs the documentation revision only; it does not authorize execution

## Formal verdict

```text
REVIEW_VERDICT: REVISE
DOCUMENT_REVISION_COMPLETENESS: REVISE
CANDIDATE_NORMALIZATION_CONTRACT: PASS
SOURCE_OFF_AND_RUNTIME_GATES: PASS
DIRECT_MESH_EQUIVALENCE: CONDITIONAL_NOT_DEMONSTRATED
CURRENT_ONLY_CRITERION: REVISE
BENCHMARK_ONLY_EXCEPTION: USER_DECISION_REQUIRED
NEXT_AUTHORIZATION_SCOPE: PASS
ATTACHMENT_COMPLETENESS: PASS
```

Stable identities remain unchanged:

```text
CONTROLLED_LINEAGE_MASTER: original bv.in
ZIP_DECK: CANDIDATE_PARENT / NOT_RUNTIME_VALIDATED
CONTROLLED_EXECUTION_PARENT: NONE
```

## Six documentation revisions required by this re-review

1. Mark item 14 in plan §13.3 directly and unconditionally as `CLOSED`.
2. Restrict every primary status in §13.3 to `CLOSED`, `NEXT-STAGE TODO` or `OPEN`; details may follow only as qualifiers.
3. Assign the recovered-to-floor SET classification to `NEXT-STAGE TODO — POSTPROCESS/ANALYSIS`, never to the deck.
4. Assign four-segment signed-charge integration to `NEXT-STAGE TODO — POSTPROCESS`, never to the deck.
5. Replace the stale section references in handoff §6 with references to sections that exist in the current plan.
6. State explicitly that the deck owns only the output contract, while unified postprocess/analysis owns floor, KCL,
   trend fitting, signed-charge integration, decision order and final current-only labels.

These are documentation corrections only. They do not close any parser, mesh, accepted-300 V, thermal-binding or
transient execution gate.

The original `bv.in` is the only structure/physics lineage master. `RUN238` is excluded. The historical direct-mesh
`seb_2` may supply runtime and late-window references only; it must not supply material, doping, impact, thermal or solver
parameters. The patch applies to the uploaded original `bv.in` and produces the ZIP candidate, so the
original—patch—candidate provenance gate is closed and must not reappear as an open gap.

## Conversion fidelity

Direct comparison confirms that the conversion preserves:

- every original geometry and region boundary;
- the actual thick Nickel source, drain and stepped-gate polygons;
- `source/drain/gate` and `elec.id=1/2/3`;
- original doping type, concentration and region;
- active interface charge `qf=-9e12`;
- Ga₂O₃ mobility;
- SELB `an1/an2=2.5e6`, `bn1/bn2=3.96e7`, `betan=1.37`;
- trap lines in their original commented/inactive state.

No active trap exists in either deck. The valid statement is “no trap was added or enabled,” not “an enabled trap model
was preserved.” The original has one continuous thick Nickel `gate`; it has no separate `gate_fp` electrode.

The static physics/solver body is not preserved verbatim because the candidate adds `auger`, `lat.temp` and
`max.temp=50000`, changes the 200→300 V step from 15 V to 10 V, removes the gate-state `outf/load` flow, and replaces
the output/file flow. `auger`, `max.temp=50000` and the static-ramp changes therefore require removal or an independently
reviewed justification.

## Runtime gates that remain open

1. Five `refine mode=x` windows prove only lateral-refinement intent; they do not prove x/y track resolution.
2. `vfinal=300` is an input target, not an accepted 300 V state.
3. `thermcontact` to `elec.num` binding is not runtime-verified.
4. `MATERIAL region=10 mun=50` points to the Nickel source region and requires parser/runtime adjudication.
5. NiO `tcon.const tc.const=2.27` runtime interpretation is unverified.
6. The C source time factor is `exp(-4)≈0.0183` at `t=0`, not zero.
7. Five accepted source-off baseline points are absent.
8. Legacy `Acceptors=2e6` and SELB `2.5e6/3.96e7/betan=1.37` conflict with production preflight.
9. The static stage is not explicitly proven to have the particle source disabled.
10. Accepted/STR judging points at 20 µs and 50 µs are not explicitly implemented.
11. Interactive `tonyplot` must not be inside the non-interactive performance benchmark path.
12. Added `auger` may activate unfrozen parent-material defaults.

All parser, mesh, static-state and runtime work above remains a future task. This review does not authorize performing it.

## Direct-mesh feasibility

`CONDITIONAL_NOT_DEMONSTRATED` means mechanical transcription appears geometrically possible but is not yet proven to
preserve all of the following simultaneously:

- thick Nickel source/drain/gate regions;
- actual source/drain contact lengths;
- the single continuous stepped-gate equipotential;
- multi-polygon oxide topology;
- NiO/Al₂O₃/Ga₂O₃ interfaces;
- thermal-contact position, area and electrode binding.

The twin must not create `gate_fp`. If direct ATLAS requires zero-thickness line electrodes, different contact lengths,
different region topology or different thermal boundaries, the comparison is `OFAT_INVALID`.

## Current-only criterion

The declared minimum endpoint for this pairwise comparison is 100 µs, not a universally sufficient SEB time. If the
response remains undecidable at 100 µs, the only valid result is `INSUFFICIENT_TIME_WINDOW`.

The recovery loophole is closed by the following branch:

```text
If ΔId and ΔIs fall below their own floors at at least two consecutive late accepted points,
a resolvable peak existed earlier, KCL-consistent decay persisted before reaching the floors,
and no secondary recovery occurs from 50 to 100 µs,
classify SET_LIKE_CURRENT_RESPONSE without requiring a log-slope below the floors.
```

Decision priority is fixed:

```text
configuration/equivalence failure → OFAT_INVALID
solver failure on a legitimate configuration → NUMERICAL_TERMINATION
normal arrival at 100 µs with unresolved trend → INSUFFICIENT_TIME_WINDOW
complete decay or persistence gate → corresponding current-only classification
```

Raw three-terminal current pairing, Revision 4 formal spatial Phase 2 and thermal-runaway SEB remain separate. Terminal
pairing proves only sign/pairing/KCL. Formal spatial Phase 2 still needs three `Jn` connectivity frames in one hold interval
and cross-section flux closure. Thermal runaway still needs independent late current–impact–temperature positive feedback.

## Benchmark-only exception

A separate written user approval is required before both arms may retain, solely for numerical route comparison:

- substrate `Acceptors=2e6`;
- SELB `2.5e6 / 3.96e7 / betan=1.37`.

The exception must be labeled `LEGACY_BENCHMARK_ONLY / NOT_PRODUCTION_QUALIFIED_SEB`. It cannot qualify the parameters
for production, bypass preflight silently, or import historical `seb_2` physics.

## Previously confirmed technical gates remain in force

- Freeze one static-state sequence shared by A/B: gate initialization, 15 V ramp step, save/load and solver.
- Remove Auger or justify it with explicit parameters and separate approval.
- Remove `max.temp=50000` or review it as a shared solver change.
- Require at least five accepted baseline points with source truly off/zero.
- Freeze maximum Δx/Δy and verify center spacing and full-y continuity from generated STR.
- Close accepted-300 V, thermcontact, region-10 and NiO thermal runtime gates.
- Align deck/plan accepted and STR times at 10/20/50/100 µs.
- Preserve thick Nickel, actual contact lengths and one stepped-gate electrode in any future direct twin.
- Obtain the written benchmark-only exception; do not bypass production preflight.
- Move `tonyplot` out of execution and time structure build, static bias and transient separately.
- Implement recovered-to-floor classification and four-segment signed-charge integration only in unified
  postprocess/analysis.

## Next authorization boundary

This re-review authorizes documentation revision and scoped publication only. It does not authorize SSH, simulation, deck
or C-source edits, direct-twin preparation, new RUNs, parameter changes, branch/worktree creation or any remote operation.

After documentation revision, a future authorization may be requested for this limited sequence only:

```text
local candidate-deck preparation
+ parser-only check
+ DevEdit/direct-mesh structure and mesh-generation inspection
+ 300 V static-state equivalence preflight
```

That future preflight must not automatically enter a particle transient.

```text
NO SEU TRANSIENT
NO PAIRED TRANSIENT
NO AUTOMATIC EXPANSION OF AUTHORIZATION
```
