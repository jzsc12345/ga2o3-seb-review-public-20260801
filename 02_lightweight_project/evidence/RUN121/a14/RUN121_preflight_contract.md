# RUN121 preflight and execution contract

Status: `CONTRACT_PASS / STATIC_GATE_PASS / COMPLETED_TO_500NS`.

## Machine-checked preflight

```text
RUN121_CONTRACT Z_IMPACT_FIVE_REGIONS=PASS count=5 regions=['3', '4', '5', '6', '7']
RUN121_CONTRACT NO_Y_IMPACT_VALUES=PASS old_A_hits=0 old_B_hits=0
RUN121_CONTRACT NO_LT_TAU_MIX=PASS lt_tau_hits=0
RUN121_CONTRACT TIME_STEPS_TO_500NS=PASS count=22 last=solve tstop=500e-9 dt=1e-8 previous
RUN121_CONTRACT NO_POST_500NS_SOLVE=PASS count=0
RUN121_CONTRACT NORMALIZED_RUN096_IDENTITY=PASS parent=173 candidate=173 first_mismatch=NONE
RUN121_CONTRACT ENGINE_AND_BIAS=PASS go_devedit=1 go_atlas=1 target_vds_1000=True
RUN121_CONTRACT PARENT_SHA256=786EA68542AA235621A2A2AD13DC81CB86666FD875577F00FF1FBFA5143D7CB5
RUN121_CONTRACT CANDIDATE_SHA256=0DB0ABE8E5BA83DE340DA376679A7486FA1C6C8184658F1DCDD629B01BDCBFBF
RUN121_CONTRACT OVERALL=PASS
```

The normalized identity check removes only the run label, output basenames, the RUN096 tail after
500 ns, and the five paired impact statements. All remaining 173 normalized lines are identical.

## Authorized physical delta

Regions 3–7 changed together from the RUN096 Y/[010] electron/hole Selberherr group
`A=2.16e6 cm^-1`, `B=1.77e7 V/cm` to the reviewed Z/[001] group
`A=7.06e5 cm^-1`, `B=2.10e7 V/cm`. This paired group is one registered physical variable.

Structure, mesh, LT.TAU, UID, substrate, mobility, thermal model, ion source, solver, compliance,
and the time schedule through 500 ns remained frozen. No second physical variable or solve beyond
500 ns was added, and license configuration was not changed.

## Review hashes

| Artifact | SHA-256 |
|---|---|
| Frozen RUN096 parent deck | `786EA68542AA235621A2A2AD13DC81CB86666FD875577F00FF1FBFA5143D7CB5` |
| RUN121 candidate deck | `0DB0ABE8E5BA83DE340DA376679A7486FA1C6C8184658F1DCDD629B01BDCBFBF` |
| Full deck diff | `A5A8AAEB60ED727C2A03C12C8DDA933463D32EC0C9764D1692CFF3B90AE063B2` |
| Structure PNG | `9116F8398F8B63D2046704CC1B357AA333CD9DE08D006CCD7F225F02AB511B76` |
| Track/mesh PNG | `B38FDA192E4CBBE99F1ABAD9379A3221C6EE8F31A764374F23F56FA85D0F42C0` |

The two A14 images are byte-identical to the frozen RUN096 images because geometry and mesh did
not change. The full review materials are the [parent deck](../decks/RUN096_Wang2026_nofp_Lgd9_x11_hfo2hc_SEB_1000V_Et0p8_long.in.txt),
[candidate deck](../decks/RUN121_Wang2026_nofp_Lgd9_x11_zimpact_SEB_1000V_short500ns.in.txt),
[full diff](RUN096_RUN121_full_deck_diff.md), [structure image](RUN121_preflight_structure_RUN096_identical.png),
and [track/mesh image](RUN121_preflight_track_mesh_RUN096_identical.png).

## Execution closure

The 1000 V static gate passed with 219 accepted points and maximum absolute current
`2.184003738e-15 A/um`. Deposited charge was `2.4355067009 pC/um`, within `+0.516%` of target.
The single launch ended naturally at the accepted 500 ns endpoint with ATLAS `Error(s)=0` and no
fatal marker. Adaptive-step rejections and temperature-limit trial states are disclosed in the
[result report](../RUN121_RESULT.md); they are not represented as accepted trajectory points.

This contract and its sanitized timeline are not raw authorization or runtime transcripts. They do
not authorize another run or broaden the completed result beyond the stated Z/[001] impact-only,
1000 V, 500 ns boundary.
