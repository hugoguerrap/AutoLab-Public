# Fertilizer Design — Frozen Metrics

**Do not modify after creation.**

## Success Criteria

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Composite score | > 0.75 | `python prepare.py evaluate <SMILES>` |
| Nitrogen content | > 20% N by mass | Calculated from formula |
| Slow-release score | > 0.6 | prepare.py slow_release_score |
| Biodegradability | > 0.7 | prepare.py biodegradability_score |
| Novelty | Not in PubChem | `python prepare.py novelty <SMILES>` |
| Synthesizability | SA < 4.0 (normalized > 0.67) | RDKit SA Score |
| Molecules evaluated | >= 30 | Count in results.tsv |
| Novel molecules found | >= 3 | Count "novel" in results.tsv |

## Baselines

| Molecule | N% | Composite | Slow-Release |
|---------|-----|-----------|-------------|
| Urea | 46.6% | ~0.55 | Low (dissolves instantly) |
| Biuret | 40.8% | ~0.60 | Low-Medium |
| IBDU | 32.2% | ~0.65 | High (commercial slow-release) |

## What Counts as a Win

A molecule that scores composite > 0.75 with slow_release > 0.6 and N% > 20
AND is not found in PubChem would be a novel slow-release nitrogen carrier
worth investigating in a real laboratory.
