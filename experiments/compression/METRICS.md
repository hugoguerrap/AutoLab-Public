# Compression — Frozen Metrics

**Do not modify this file after creation.**

## Success Criteria

| Metric | Target | How to Measure |
|--------|--------|----------------|
| All datasets lossless | 100% | `all_lossless` in results |
| Beat gzip ratio | avg_ratio < 0.35 | `avg_ratio` in results |
| Composite score | > 0.62 (gzip baseline) | `composite` in results |
| Experiments completed | >= 8 | Count rows in results.tsv |

## Composite Score (frozen in prepare.py)

```
composite = 0.50 * ratio_score + 0.20 * speed_score + 0.30 * lossless_score
```

- ratio_score: 1.0 - avg_ratio (lower ratio = better)
- speed_score: min(speed_mbps / 100, 1.0)
- lossless_score: 1.0 if all lossless, 0.0 if any lossy
