# Artificial Life (Lenia) — Optimization Program

## Objective

Discover rules for a continuous cellular automaton that produce emergent life-like behavior.
Modify `rules.py` to find parameter combinations that maximize the composite score.
The simulation engine in `prepare.py` is FROZEN — do not modify it.

## The Loop

For each experiment:

1. **Read** current rules.py and results.tsv
2. **Hypothesize** — propose new parameter values based on what worked/failed
3. **Edit** rules.py with new parameters in CURRENT_RULES
4. **Run**: `python prepare.py evaluate` — get metrics
5. **If composite_score > 0.4**: `python prepare.py render experiment renders/experiment_N.gif` — save a GIF
6. **Record** results in results.tsv (append a new row)
7. **Decide**:
   - If composite_score > best previous → keep (commit)
   - If new behavior type discovered (movement, oscillation) → keep even if score is lower
   - Otherwise → revert rules.py
8. **Repeat** from step 1

## What to Optimize

The composite score is:
```
25% survival + 20% complexity + 20% movement + 15% stability + 10% structure + 10% oscillation
```

The DREAM outcome: a set of rules where a "creature" emerges that:
- Survives indefinitely (survival > 0.8)
- Moves across the grid (movement > 0.5)
- Has organized structure (complexity > 0.5)
- Is stable but not static (stability > 0.5, oscillation > 0.3)

## Exploration Strategy

### Phase 1: Understand the landscape (experiments 1-3)
- Evaluate the Orbium baseline
- Try wider sigma (less strict rules)
- Try multi-shell kernel (multiple beta peaks)

### Phase 2: Search for movement (experiments 4-6)
- Asymmetric initial conditions
- Ring kernel type
- Different init_type (ring, multi_blob)

### Phase 3: Search for complexity (experiments 7-10)
- 3+ beta peaks for richer interactions
- Fine-tune mu/sigma around best values
- Try large radius (15-18) for long-range interactions
- Combine best features from previous experiments

## Key Insight

Small changes in mu and sigma can cause PHASE TRANSITIONS:
- mu too low → everything dies
- mu just right → life emerges
- mu too high → everything explodes

The sweet spot is narrow. Use binary search around promising values.

## Results Format (results.tsv)

```
experiment	name	composite	survival	complexity	movement	stability	structure	oscillation	mu	sigma	radius	description
```

## Exit Conditions

Stop when ANY of these is true:
- 10 experiments completed
- composite_score > 0.7 achieved
- 5 consecutive experiments with no improvement
