# Latest web-side independent review verdict — BV→SEB conversion package

> Source: user-pasted web-side independent review
>
> Date received: 2026-08-06
>
> Role: governing review input for this handoff; it does not itself authorize execution

## Verdict

```text
REVIEW_VERDICT: REVISE
CONTROLLED_LINEAGE_MASTER: original bv.in
ZIP_DECK: CANDIDATE_PARENT / NOT_RUNTIME_VALIDATED
DEVEDIT_RUNTIME_READINESS: NOT READY
DIRECT_MESH_EQUIVALENCE_FEASIBILITY: CONDITIONAL
BENCHMARK_EXCEPTION_REQUIRED: YES
NEXT_AUTHORIZATION: REVISE_BEFORE_COMPARISON
```

The original `bv.in` is the only master for structure, regions, doping, mobility and impact lineage. The ZIP candidate
cannot be promoted to a controlled execution parent before runtime gates close. The patch provenance gate is closed:
the patch applies to the original uploaded this round and produces the candidate in the ZIP.

## Conversion-fidelity decision

`CONVERSION_FIDELITY: PARTIAL PASS`.

Preserved items include geometry, 12 region boundaries, thick Nickel source/drain/gate, electrode names and IDs, active
impurities, mobility, impact coefficients and active interface charge. The original gate is one continuous thick Nickel
`gate`; there is no separate `gate_fp`. Neither deck activates traps, so only trap comments—not an active trap model—are
preserved.

Static state and physics were not fully preserved: the candidate adds `auger`, `lat.temp` and `max.temp=50000`, changes
the 200→300 V step from 15 V to 10 V, and removes the original gate-state `outf/load` flow.

## Runtime blockers

1. Five `refine mode=x` windows do not prove track resolution in both x and y.
2. `vfinal=300` is a target, not evidence of an accepted 300 V state.
3. `thermcontact` to `elec.num` binding is not runtime-verified.
4. `MATERIAL region=10 mun=50` targets the thick Nickel source region and requires parser/runtime adjudication.
5. The NiO `tcon.const tc.const=2.27` interpretation is unverified.
6. The C source is nonzero at `t=0`, and its statement precedes the static ramp; a true source-off baseline is unproved.
7. Five accepted pre-strike baseline points are absent.
8. Legacy `Acceptors=2e6` and impact `2.5e6/3.96e7/betan=1.37` conflict with production preflight.
9. Added `auger` has no explicit parameters and may activate parent-material defaults.
10. `max.temp=50000` and the ramp-step change are solver changes beyond a pure BV→SEB increment.
11. Explicit accepted 20 µs and 50 µs points and matching STRs are absent.
12. Interactive `tonyplot` must be outside the benchmark execution and wall-time path.

## Current-only criterion revision

The four current-only outcomes can distinguish late decay, persistent late current, insufficient time and numerical
termination, but the below-noise-floor loophole must be closed:

```text
If baseline-subtracted drain and source currents fall below their declared floors at two consecutive late accepted points,
a resolvable peak existed earlier, KCL passes, and no recovery occurs from 50 to 100 µs,
SET_LIKE_CURRENT_RESPONSE may be declared without computing a log-slope below the floor.
```

Configuration/equivalence failure has priority as `OFAT_INVALID`; solver failure on an otherwise legitimate arm is
`NUMERICAL_TERMINATION`. The charge-integration segmentation must use one consistent four-segment definition.

## Direct-mesh boundary

Mechanical transcription is only conditionally feasible. It must preserve thick Nickel source/drain/stepped gate, actual
contact lengths, single gate `elec.id=3`, oxide topology, Al₂O₃/NiO/Ga₂O₃ interfaces and thermal-contact area/binding.
Creating `gate_fp`, substituting zero-thickness line electrodes, or changing region/contact topology makes the comparison
`OFAT_INVALID / CONTROLLED_COMPARISON_NOT_FEASIBLE`.

## Mandatory revisions

1. Mark the original-to-ZIP patch provenance gate PASS and remove the obsolete “original file not provided” gap.
2. Restore or explicitly justify the static sequence; both arms must be identical.
3. Remove `auger`, or justify it with explicit parameters rather than parent defaults.
4. Remove or separately justify `max.temp=50000`.
5. Generate at least five accepted baseline points with the particle source truly off or strictly zero.
6. Close the x/y mesh gate with measured Δx/Δy, center spacing and full-y track continuity.
7. Close accepted-300 V, thermcontact binding, region-10 material and NiO thermal runtime gates.
8. Align accepted times, STR times and fields, explicitly including 20 µs and 50 µs.
9. Add the below-floor recovered-SET branch and unify four-segment charge integration.
10. Preserve thick Nickel and a single gate electrode in the direct ATLAS twin.
11. Obtain a written benchmark-only exception before retaining legacy substrate/impact values through preflight.
12. Remove `tonyplot` from the benchmark execution path and time generation, ATLAS and plotting separately.

## Authorization boundary

This review does not authorize SSH, simulation, deck modification, new RUNs, parameter adjustment, branch/worktree
creation or any paired transient launch.
