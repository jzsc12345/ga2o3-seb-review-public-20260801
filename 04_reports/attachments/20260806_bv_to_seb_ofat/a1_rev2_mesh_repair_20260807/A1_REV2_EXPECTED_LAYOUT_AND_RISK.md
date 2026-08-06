# A1_REV2 expected layout and risk review

> Status: `NOT_RUNTIME_VALIDATED`. This document contains expectations, not generated-mesh evidence.

## Expected two-dimensional layout

The rectangular constraint spans `0.30 µm` in x and `0.60 µm` in y. If DevEdit applies the fixed maximum spans during the existing MeshBuild:

- x requires at least `ceil(0.30/0.016)=19` intervals across the full track box;
- y requires at least `ceil(0.60/0.016)=38` intervals along the full depth;
- multiple x columns should therefore resolve `xion±3r`, rather than a single centerline;
- every accepted triangle measured by the same A1 ROI method must have bounding Δx and Δy no greater than `0.016 µm`.

These counts describe a lower-bound layout expectation, not a demand for a uniform Cartesian grid. DevEdit may add more points near material and region boundaries.

## Why the repair is narrow

- The constraint remains limited to `x=10.10–10.40`, `y=0–0.60`.
- No global `base.mesh` tightening is introduced.
- No second MeshBuild is introduced after the inherited manual refinements.
- All original geometry, 12 regions, thick Nickel and electrodes remain untouched.
- The inherited `unrefine` box is far from the track ROI and is unchanged.

## Risks that remain open

1. DevEdit may place extra boundary nodes or nonuniform triangles; only a generated STR can establish actual Δx/Δy.
2. Constraint hierarchy at region interfaces may produce denser mesh, which is acceptable, but must not produce any triangle wider/taller than the contract in the registered semiconductor ROI.
3. The later inherited `refine` operations are expected only to subdivide; their interaction with the predeclared constraint is still runtime-unverified for this exact geometry.
4. Node count is not an acceptance criterion. A denser or lighter global count cannot substitute for ROI Δx/Δy and full-y continuity.
5. A1_REV2 must be run once, without edit or fallback, only after a separate user/web authorization.

## Future acceptance method

Use the same semiconductor triangle-centroid/bounding-span method used for A1, over the same ROI. Do not substitute requested spacing, centerline spacing, image appearance, or total node count for the measured contract.
