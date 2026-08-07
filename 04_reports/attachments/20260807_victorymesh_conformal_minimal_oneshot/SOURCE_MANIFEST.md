# Public attachment manifest

This directory contains text evidence for the Victory Mesh conformal-minimal
one-shot audit. No file hash was generated.

## Published primary evidence

| Public file | Local source |
|---|---|
| `VICTORYMESH_CONFORMAL_MINIMAL_ONESHOT_AUDIT_20260807.md` | `docs/reports/VICTORYMESH_CONFORMAL_MINIMAL_ONESHOT_AUDIT_20260807.md` |
| `PREFLIGHT_VICTORYMESH_SEB_ONESHOT_conformal_minimal_interfaces_x10p25.in` | `decks/PREFLIGHT_VICTORYMESH_SEB_ONESHOT_conformal_minimal_interfaces_x10p25.in` |
| `typescript.log` | `outputs/preflight/VICTORYMESH_CONFORMAL_CONTRACT_20260807/candidate/typescript.log` |
| `EXIT.txt` | `outputs/preflight/VICTORYMESH_CONFORMAL_CONTRACT_20260807/candidate/EXIT.txt` |
| `execution_resource_samples.csv` | `outputs/preflight/VICTORYMESH_CONFORMAL_CONTRACT_20260807/candidate/execution_resource_samples.csv` |
| `warning_failure_register.csv` | `outputs/preflight/VICTORYMESH_CONFORMAL_CONTRACT_20260807/candidate/warning_failure_register.csv` |
| `stage1_stage2_candidate_comparison.csv` | `outputs/preflight/VICTORYMESH_CONFORMAL_CONTRACT_20260807/candidate/stage1_stage2_candidate_comparison.csv` |
| `executed_input_returned.txt` | `outputs/preflight/VICTORYMESH_CONFORMAL_CONTRACT_20260807/candidate/executed_input_returned.txt` |
| `analyze_victorymesh_contract.py` | `scripts/analyze_victorymesh_contract.py` |

## Derived analysis groups

- `stage1/`: completed Stage 1 STR measurements.
- `stage2/`: completed Stage 2 STR measurements.
- `candidate_raw_analysis/`: pre-remesh raw candidate STR measurements.

Each group contains `summary.json`, `regions.csv`, `roi_metrics.csv`,
`thin_layers.csv`, `material_interfaces.csv`, and
`semantic_interfaces.csv` with a group-specific prefix.

## Intentionally excluded

The binary STR is not committed to the public repository. The candidate did
not produce a final remeshed STR. The existing pre-remesh raw STR remains in
the local bulk archive and is referenced only by path. No PNG is labeled as a
final candidate mesh because no final candidate mesh exists.

