# A1_REV2 forbidden-command scan

> Scope: active statements only; comments are excluded. Static scan only.

| Check | Count/result |
|---|---:|
| active `go devedit` | 1 |
| active `structure` | 1 |
| active `quit` | 1 |
| active `go atlas` | 0 |
| active `solve` | 0 |
| active `singleeventupset` | 0 |
| active `tfinal` | 0 |
| active `system` / `ssh` / `shell` | 0 |
| local track `constr.mesh` logical statement | 1 |
| local track `max.width` | 0.016 µm |
| local track `max.height` | 0.016 µm |

Static diff review:

```text
GEOMETRY_CHANGE = NO
REGION_CHANGE = NO
ELECTRODE_CHANGE = NO
DOPING_CHANGE = NO
MATERIAL_CHANGE = NO
MOBILITY_CHANGE = NO
IMPACT_CHANGE = NO
THERMAL_CHANGE = NO
SOLVER_CHANGE = NO
OTHER_ROI_CHANGE = NO
TRACK_CONSTRAINT_VALUE_CHANGE = NO
TRACK_CONSTRAINT_ORDER_CHANGE = YES
```

Packet labels retained:

```text
DERIVED_MESH_REPAIR_PACKET
NOT_RUNTIME_VALIDATED
A1_REV2_ONLY
NO A2
NO ATLAS
NO STATIC_BIAS
NO SEU TRANSIENT
NO AUTOMATIC_EXPANSION_OF_AUTHORIZATION
```

No execution authorization is embedded in the packet.
