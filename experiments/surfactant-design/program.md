# Surfactant Design — Optimization Loop

## Goal
Design **novel, biodegradable surfactant molecules** that outperform existing detergents on a composite score combining cleaning potential (HLB, CMC), environmental safety (biodegradability, aquatic toxicity), and synthesizability.

## Rules
1. **ONLY modify `surfactant.py`** — `prepare.py` is frozen
2. **Log ALL results** to `results.tsv` — even failures
3. **One hypothesis per iteration** — atomic, measurable, revertible
4. **Git commit** every improvement

## Evaluation Commands

```bash
# Evaluate a single molecule
python experiments/surfactant-design/prepare.py evaluate "SMILES"

# Run all baselines
python experiments/surfactant-design/prepare.py baseline

# Batch evaluate surfactant.py candidates
python experiments/surfactant-design/prepare.py batch experiments/surfactant-design/surfactant.py

# Check novelty on PubChem
python experiments/surfactant-design/prepare.py novelty "SMILES"

# Compare two molecules
python experiments/surfactant-design/prepare.py compare "SMILES1" "SMILES2"

# Render structure
python experiments/surfactant-design/prepare.py render "SMILES" experiments/surfactant-design/renders/mol.png
```

## The Loop

For each experiment iteration:

### 1. READ
Read `surfactant.py` to understand the current best molecule and strategy notes.

### 2. HYPOTHESIZE
Based on the current best score and what's been tried, form ONE hypothesis:
- "Adding an ester linkage between head and tail will improve biodegradability"
- "Switching from glucose to sorbitan head will optimize HLB"
- "Extending chain from C12 to C14 will lower CMC"

### 3. GENERATE
Design 10-20 candidate SMILES based on your hypothesis. Vary systematically:
- Change tail length (C8-C18)
- Swap head groups (sugar, amino acid, sulfate, betaine, ester)
- Add/remove linker groups (amide, ester, ether)
- Try novel combinations not seen in commercial surfactants

### 4. EVALUATE
```bash
python experiments/surfactant-design/prepare.py evaluate "SMILES1" "SMILES2" ...
```

### 5. DECIDE
- **Better?** Update `BEST_SMILES` and `CANDIDATES` in `surfactant.py`. Git commit.
- **Worse?** Log the result anyway. Note what didn't work in `STRATEGY_NOTES`.

### 6. LOG
Append ALL results to `results.tsv` (tab-separated):
```
experiment	smiles	composite_score	amphiphilicity	hlb	hlb_score	cmc_score	biodegradability	aquatic_safety	sa_score	mw	logp	novel	description
```

### 7. REPEAT

## Exit Conditions
- **Max experiments:** 15 iterations
- **Plateau:** 5 consecutive iterations with no improvement > 0.005
- **Target reached:** composite_score >= 0.92 with novel molecule
- **Perfect score:** composite_score >= 0.95 (near theoretical ceiling)

## Strategy Phases

### Phase 1: Baseline Survey (exp 1-3)
- Evaluate ALL known surfactant classes
- Establish baseline scores for each class
- Identify which class has highest potential
- Map the scoring landscape

### Phase 2: Scaffold Exploration (exp 4-7)
- Take the best class and explore structural variations
- Vary tail length, head group, linker chemistry
- Try hybrid scaffolds (e.g., sugar + amino acid)
- Try biosurfactant-inspired structures (rhamnolipids, sophorolipids)

### Phase 3: Optimization (exp 8-11)
- Fine-tune the best scaffold
- Optimize specific sub-scores (HLB, CMC, biodeg)
- Try dual-function groups (e.g., ester linker = biodeg + flexibility)
- Explore gemini structures for CMC breakthrough

### Phase 4: Novelty Push (exp 12-15)
- Check PubChem novelty for all top candidates
- If top candidates are known, create novel analogs
- Combine best features from different scaffolds
- Push for ceiling score with novel structure

## Scoring Breakdown
| Component | Weight | What it measures |
|-----------|--------|-----------------|
| Amphiphilicity | 20% | Has proper head + tail structure |
| HLB Score | 20% | Proximity to detergent range (13-15) |
| CMC Score | 15% | Micelle efficiency (lower = better) |
| Biodegradability | 20% | Environmental breakdown potential |
| Aquatic Safety | 15% | Low toxicity to aquatic life |
| Synthesizability | 10% | Practical to manufacture |

**Bonuses:** green (biodeg+aquatic >= 0.7): +0.03, sweet spot (HLB+CMC high): +0.02, amphiphilic excellence: +0.02

## Tips
- Sugar-based surfactants (glucosides, sophorolipids) score well on biodeg + aquatic
- Amino acid surfactants (sarcosinates, glutamates) balance performance + safety
- Ester linkages boost biodegradability (hydrolyzable bonds)
- C12-C14 tails are the sweet spot for detergent HLB
- Avoid halogens (kill biodeg + aquatic scores)
- Avoid excessive branching (hurts biodeg)
- Gemini surfactants can have CMC 10-100x lower than monomeric analogs
- Novel ≠ complex. Simple structural changes can create novel molecules
