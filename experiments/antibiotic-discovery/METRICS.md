# Antibiotic Discovery — Frozen Metrics

**Do not modify after creation.**

## Primary Metric
- **composite_score** — weighted combination of antibacterial property score + gram-negative permeability + structural novelty + drug-likeness + synthesizability
- Range: 0.0 to 1.0
- Target: > 0.80

## How It's Calculated
Defined in `prepare.py:evaluate()`:

### Sub-metrics (weights):
- **Antibacterial drug profile (25%)** — MW, LogP, HBD, HBA tuned for antibiotic property space (not general drugs)
- **Gram-negative permeability (20%)** — Hergenrother's eNTRy rules: primary amine, low globularity, rigidity
- **Structural novelty vs known classes (15%)** — Tanimoto distance from beta-lactams, fluoroquinolones, tetracyclines, macrolides, aminoglycosides
- **QED-like drug score (15%)** — General drug-likeness (oral bioavailability, PAINS clean)
- **Synthesizability (10%)** — SA Score < 4.0
- **Predicted membrane disruption (5%)** — Amphiphilic moment estimate (cLogP variance across fragments)

### Bonuses:
- +5% if gram-neg score > 0.6 AND novelty score > 0.7 (novel gram-negative active)
- +3% if contains nitrogen heterocycle AND primary amine (dual mechanism potential)

## Baselines
| Molecule | Class | Composite | Notes |
|----------|-------|-----------|-------|
| Ciprofloxacin | Fluoroquinolone | ~0.55 | Known class, resistance common |
| Halicin | Novel (MIT 2020) | ~0.65 | Benchmark novel antibiotic |
| Trimethoprim | Diaminopyrimidine | ~0.50 | Old class |

## What Counts as a Win
A molecule that scores composite > 0.80, is structurally dissimilar to ALL known antibiotic classes (novelty > 0.7), AND is not found in PubChem = a genuinely novel antibiotic candidate worth laboratory synthesis and testing against MRSA/gram-negative pathogens.

## Success Criteria
| Metric | Target |
|--------|--------|
| Best composite_score | > 0.80 |
| Molecules evaluated | >= 100 |
| Novel molecules (not in PubChem) | >= 10 |
| Structurally novel (Tanimoto < 0.3 to all known classes) | >= 5 |
| Gram-negative score > 0.6 | >= 3 candidates |
