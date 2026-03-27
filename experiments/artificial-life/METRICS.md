# Artificial Life — Frozen Metrics

**Do not modify this file after creation.**

## Success Criteria

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Experiments completed | >= 8 | Count rows in results.tsv |
| Best composite score | > 0.5 | Max composite in results.tsv |
| Moving creature found | >= 1 | movement_score > 0.3 |
| Oscillating pattern | >= 1 | oscillation_score > 0.3 |
| GIFs rendered | >= 5 | Count files in renders/ |

## Composite Score (frozen in prepare.py)

```
composite = 0.25 * survival + 0.20 * complexity + 0.20 * movement + 0.15 * stability + 0.10 * structure + 0.10 * oscillation
```
