# Warning / fatal register

## Stage 1

- Fatal / parse error: `0`
- Victory Mesh final warning count: `0`
- DevEdit inherited material warnings: six lines concerning numeric user-material codes 50/51 and
  ignored extra encoded text. These warnings also occur before Victory Mesh in the unchanged source
  structure path. They did not delete the Ga2O3/NiO semantic regions or their impurity fields in the
  final STR.
- Unexpected ATLAS entry: `NO`

## Stage 2

- Fatal / parse error: `0`
- Victory Mesh final warning count: `0`
- Same inherited DevEdit material-warning class as Stage 1.
- Unexpected ATLAS entry: `NO`

## Adjudication

The warnings are disclosed, not suppressed. Region geometry, material codes, impurities, three
electrodes and thick gate were checked from each generated STR. The Stage 2 hard failure is not a
parser or material warning: it is the measured mesh-contract miss `max Δy=0.0166666667 µm`.
