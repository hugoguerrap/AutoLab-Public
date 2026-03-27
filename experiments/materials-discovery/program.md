# Materials Discovery — Optimization Program

## Objective

Discover novel materials with useful properties by modifying `material.py`.
The evaluation function in `prepare.py` is FROZEN — do not modify it.

## The Loop

For each experiment:

1. **Read** current material.py and results.tsv
2. **Hypothesize** — propose a new material composition, lattice, or structure type
3. **Edit** material.py with the new material (add to MATERIALS list or replace)
4. **Run**: `python prepare.py evaluate` — get the composite score and properties
5. **Run**: `python prepare.py novelty` — check if it exists in Materials Project
6. **Record** results in results.tsv (append a new row)
7. **Decide**:
   - If composite_score > best AND passes all checks → keep (commit)
   - If novel AND composite_score > 0.5 → keep (even if not best score)
   - Otherwise → revert material.py to previous state
8. **Repeat** from step 1

## What to Try

### Phase 1: Explore known structures (experiments 1-3)
- Evaluate baseline BaTiO3
- Try classic solar cell materials (perovskites with Pb, Sn, Ge)
- Try thermoelectric candidates (heavy elements: Bi, Te, Sb, Se)

### Phase 2: Creative combinations (experiments 4-7)
- Mix cations: (Ba,Sr)TiO3, (Cs,Rb)PbI3
- Try unusual B-site elements: V, Cr, Mo, W, Ru
- Non-oxide perovskites: oxynitrides, oxysulfides, oxyhalides
- Explore spinel and fluorite structures

### Phase 3: Novel territory (experiments 8-10)
- Quaternary compositions (4 elements)
- Unusual element combinations no one has tried
- Optimize for MULTIPLE applications simultaneously
- Focus on materials NOT in Materials Project

## Scoring Priority

1. **Novel + high score** = best outcome (unknown material with good properties)
2. **Novel + decent score** = still valuable (undiscovered material)
3. **Known + high score** = validates the model works
4. **Known + low score** = not useful, revert

## Constraints

- Only modify `material.py`
- Do NOT modify `prepare.py`
- Each experiment should test ONE hypothesis
- Record ALL results (including failures) in results.tsv
- Aim for at least 5 novel materials discovered

## Results Format (results.tsv)

```
experiment	formula	composite_score	band_gap_eV	density	formation_energy	checks	applications	novel	description
```

## Exit Conditions

Stop when ANY of these is true:
- 10 experiments completed
- 5 consecutive experiments with no improvement in best composite score
- Found 5+ novel materials with composite > 0.5
