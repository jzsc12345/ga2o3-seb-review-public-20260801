# Victory Mesh SEB structure/track mesh result

> Status: `STAGE1_PASS / STAGE2_MESH_CONTRACT_HARD_FAIL / STOPPED`
>
> Route: `DevEdit structure -> Victory Mesh Conformal -> SAVE MODE=ATLAS`

## Result summary

| Gate | Stage 1 baseline | Stage 2 track | Contract |
|---|---:|---:|---|
| points | 38,359 | 56,454 | report only |
| triangles | 75,458 | 111,350 | report only |
| obtuse | 0 | 0 | PASS |
| semantic regions | 12 | 12 | PASS |
| runtime region records | 13 | 13 | explained by the two disconnected SiO2 components of semantic region 4 |
| electrodes | 3 | 3 | PASS |
| thick stepped gate | preserved | preserved | PASS |
| max Δx in ROI | 0.0366047116 µm | 0.0150000000 µm | Stage 2 PASS (`<=0.016`) |
| max Δy in ROI | 0.0400000000 µm | 0.0166666667 µm | **Stage 2 FAIL** (`>0.016`) |
| full-y continuity | PASS | PASS | PASS |

ROI is fixed at `x=10.10–10.40 µm`, `y=0.00–0.60 µm`, with `xion=10.25 µm`.

## Stage 1

Stage 1 completed naturally in Victory Mesh 1.12.0.R and wrote an Atlas-compatible STR. The final
STR preserves all 12 semantic regions, doping fields, source/drain/single stepped-gate electrodes,
thick Nickel shapes and material/interface geometry. Stage 1 therefore passes the baseline gate.

## Stage 2

Stage 2 completed mechanically and wrote an Atlas-compatible STR. The x-direction contract and
full-y continuity pass. The y-direction contract fails at the channel interval approximately
`y=0.1833333–0.2000000 µm`, where the measured separation is `0.0166666667 µm`.

Because the contract is unchanged at `max Δy <= 0.016 µm`, the correct result is:

```text
STAGE2_RESULT = HARD_FAIL
FAILURE_MODE = TRACK_MAX_DY_EXCEEDS_CONTRACT
SECOND_STAGE2_EXECUTION = NO
AUTO_FALLBACK_USED = NO
ATLAS_EXECUTED = NO
```

No spacing was adjusted after the result, no alternate mesher was tried, and the run was not
repeated.

## Structure and impurity preservation

The two final region tables show identical areas, bounding boxes, material codes and impurity
ranges for Stage 1 and Stage 2; triangle counts alone change. Key records include:

- substrate Ga2O3: acceptor `2e6 cm^-3`;
- UID Ga2O3: donor `1.5e15 cm^-3`;
- channel Ga2O3: donor `1e17 cm^-3`;
- source/drain n+: donor `5e19 cm^-3`;
- NiO P-: acceptor `1.3e18 cm^-3`;
- NiO P+: acceptor `3e19 cm^-3`;
- source/drain/gate: Nickel, electrode ids 1/2/3;
- gate bbox `x=1.5–6.0 µm`, `y=-0.20–-0.12 µm`, area `0.235 µm²`.

## Execution identity

Stage 1:

```text
/root/bin/vdoe_tmux.sh start-deck \
  /root/DECKBUILD/preflight/VICTORYMESH_SEB_STAGE1_CONFORMAL_20260807 \
  PREFLIGHT_VICTORYMESH_SEB_STAGE1_conformal_baseline.in
```

Stage 2:

```text
/root/bin/vdoe_tmux.sh start-deck \
  /root/DECKBUILD/preflight/VICTORYMESH_SEB_STAGE2_CONFORMAL_X10P25_20260807 \
  PREFLIGHT_VICTORYMESH_SEB_STAGE2_conformal_x10p25.in
```

Versions: DeckBuild `5.2.40.R`, DevEdit `2.8.26.R`, Victory Mesh `1.12.0.R`.

## Boundaries

```text
ATLAS_EXECUTED = NO
STATIC_BIAS_EXECUTED = NO
SEU_TRANSIENT_EXECUTED = NO
PAIRED_TRANSIENT_EXECUTED = NO
AUTO_FALLBACK_USED = NO
```
