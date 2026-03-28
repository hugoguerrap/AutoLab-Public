# Surfactant Design — Frozen Metrics

## DO NOT MODIFY THIS FILE

## Primary Metric
**composite_score** (0.0 – 1.0)

Target: > 0.85 with a **novel** molecule (not in PubChem).

## Composite Formula

```
composite = (
    0.20 * amphiphilicity      # Head + tail structure
  + 0.20 * hlb_score           # HLB proximity to 13-15
  + 0.15 * cmc_score           # Micelle formation efficiency
  + 0.20 * biodegradability    # Environmental breakdown
  + 0.15 * aquatic_safety      # Low aquatic toxicity
  + 0.10 * sa_score            # Synthetic accessibility
) * validity_score

+ 0.03 bonus if biodeg >= 0.7 AND aquatic >= 0.7   (green surfactant)
+ 0.02 bonus if hlb_score >= 0.8 AND cmc >= 0.7    (sweet spot)
+ 0.02 bonus if amphiphilicity >= 0.8              (excellent amphiphile)
```

Capped at 1.0.

## Sub-Metrics

| Metric | Range | What it measures | Target |
|--------|-------|-----------------|--------|
| amphiphilicity | 0–1 | Hydrophilic head + hydrophobic tail quality | >= 0.8 |
| hlb_score | 0–1 | HLB proximity to 13-15 (detergent range) | >= 0.8 |
| cmc_score | 0–1 | Critical micelle concentration efficiency | >= 0.7 |
| biodegradability | 0–1 | OECD 301 degradation potential | >= 0.7 |
| aquatic_safety | 0–1 | Low aquatic toxicity (ECOSAR-type) | >= 0.7 |
| sa_score | 0–1 | Synthetic accessibility (1=easy) | >= 0.7 |
| validity_score | 0–1 | Structural validity gate | = 1.0 |

## Baselines

| Surfactant | Type | Expected Score |
|-----------|------|---------------|
| SDS | Anionic benchmark | ~0.55 |
| Lauryl Glucoside | Nonionic green | ~0.70 |
| CAPB | Amphoteric mild | ~0.65 |
| Sodium Lauroyl Sarcosinate | Amino acid | ~0.65 |
| LAS | Anionic workhorse | ~0.50 |

## Success Criteria

| Level | Composite Score | Meaning |
|-------|----------------|---------|
| Baseline | ~0.55-0.70 | Known commercial surfactant |
| Good | > 0.75 | Better than most known surfactants |
| **Target** | **> 0.85** | **Novel green detergent candidate** |
| Excellent | > 0.90 | Exceptional discovery |
| Ceiling | > 0.95 | Theoretical maximum |
