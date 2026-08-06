# A1_REV2 DevEdit syntax provenance

> Evidence level: local manual plus an executed project case. No new execution was performed.

## 1. DevEdit 2.8.26.R manual

Local source: `D:\knowledge\pdf25\devedit_users1.pdf`.

- Printed/PDF page 89, §4.4 `CONSTRAINT.MESH`: the statement sets triangle limits during mesh and refine operations; `constr.mesh` is the preferred abbreviation; rectangular constraints use `x1`, `y1`, `x2`, `y2`; `MAXIMUM.HEIGHT` and `MAXIMUM.WIDTH` are supported.
- Printed/PDF page 104, §4.12 `MESH`: `MESH` creates a new mesh using parameters set previously. The documented order includes refining on mesh constraints as step 6. The manual example is `mesh mode=mesh.build`.

This establishes the ordering rule used by A1_REV2: the rectangle constraint must be declared before the MeshBuild that is expected to apply it.

## 2. Executed project case

Deck:
`D:\SILVACO_LOCAL\decks\PREFLIGHT_RUN227_TANPG_mesh_tube_x6p5_full_depth_fproi.in`

Relevant sequence:

```silvaco
constr.mesh x1=$ion_roi_l y1=$y_surf x2=$ion_roi_r y2=$y_uid_b \
  max.height=$ion_dy_upper max.width=$ion_dx
constr.mesh x1=$ion_roi_l y1=$y_uid_b x2=$ion_roi_r y2=$y_sub_b \
  max.height=$ion_dy_sub max.width=$ion_dx
mesh mode=MeshBuild
structure outfile="PREFLIGHT_RUN227_TANPG_mesh_tube_x6p5_full_depth_fproi.str"
```

Runtime report:
`D:\SILVACO_LOCAL\docs\reports\RUN227_MESH_REPAIR_DEVEDIT_REPORT_20260804.md`

Runtime spacing table:
`D:\SILVACO_LOCAL\outputs\runs\RUN227_tanpg-mesh-tube-x6p5-full-depth-fproi\csv\mesh_local_spacing.csv`

Observed in that executed case:

- track-tube maximum Δx: `0.015625 µm` for a pre-MeshBuild width constraint;
- full-depth tube existed;
- its y contract was intentionally looser and therefore is not reused numerically here.

A1_REV2 reuses only the proven statement form and ordering. It retains the current, stricter `max.height=0.016` requirement.

## 3. A1 failure evidence

`A1_MESH_ROI_METRICS.csv` from commit `43591ade734d4568a927f71bcc3ed8b46b875bc6` records:

```text
max Δx = 0.3125 um
max Δy = 0.0250 um
full-y continuity = PASS
```

The original A1 packet placed its new rectangle constraint after MeshBuild. It created one xion centerline but did not produce two-dimensional radial resolution.

## 4. Historical-record handling

The readable Fable5/Claude conversation export was searched by mesh/track/`constr.mesh` terms. No stronger syntax-level statement was found there. The executable project case and the installed manual therefore remain the direct evidence; no missing chat statement is inferred.
