# Drug Discovery Metrics (FROZEN)

**Do not modify this file.**

## Primary Metric
- **composite_score** — weighted combination of QED + Lipinski + PAINS + Veber + SA
- Range: 0.0 to 1.0
- Target: > 0.85

## How It's Calculated
Defined in `prepare.py:evaluate_molecule()`:
- Base: QED score (0-1)
- +0.05 if Lipinski pass
- +0.05 if PAINS clean
- +0.03 if Veber pass
- +0.02 if SA score < 4
- Capped at 1.0

## Baseline
- Aspirin: composite_score ~0.68
- The optimizer must improve from here

## Novelty
- Checked via PubChem REST API
- A molecule not found in PubChem is considered novel
- Novel + composite_score > 0.85 = genuine drug candidate discovery
