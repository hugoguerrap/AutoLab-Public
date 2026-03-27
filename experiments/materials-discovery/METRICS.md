# Materials Discovery — Frozen Metrics

**Do not modify this file after creation.**

## Success Criteria

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Experiments completed | >= 8 | Count rows in results.tsv |
| Novel materials found | >= 3 | Count "novel" entries in results.tsv |
| Best composite score | > 0.6 | Max composite_score in results.tsv |
| Solar candidate found | >= 1 | Material with band_gap 1.1-1.7 eV + checks pass |
| All checks pass | >= 50% of materials | checks column in results.tsv |

## Scoring Function (frozen in prepare.py)

```
composite = 0.4 * stability + 0.3 * band_gap_usefulness + 0.2 * applications + 0.1 * novelty_bonus
```

- stability: checks_passed / total_checks (density, charge, thermodynamics, lattice, elements)
- band_gap_usefulness: Gaussian peaks at 1.4 eV (solar), 2.5 eV (LED), 0.5 eV (thermoelectric)
- applications: count / 3 (capped at 1.0)
- novelty_bonus: 0.1 for ternary+ compositions
