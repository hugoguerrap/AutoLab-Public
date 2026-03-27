# Antibiotic Discovery — Optimization Program

## Objective

Discover novel molecules with predicted antibacterial activity against **gram-negative bacteria** (E. coli, Klebsiella, Pseudomonas, Acinetobacter) — the WHO's "critical priority" pathogens.

The key challenge: gram-negative bacteria have a double membrane that blocks most drugs. Only molecules with the right size, charge, and shape can penetrate. AND the molecule must be structurally different from all known antibiotic classes to bypass existing resistance mechanisms.

## The Karpathy Loop

This experiment follows the [Karpathy Loop](https://github.com/karpathy/autoresearch) pattern: **hypothesis → experiment → measure → accept/reject → repeat.** You are an autonomous molecular optimizer. You can ONLY modify `molecule.py`. The evaluator `prepare.py` is frozen — you cannot change what "good" means. Every iteration you propose candidates, measure them against the frozen metric, keep improvements, discard regressions, and accumulate strategy knowledge. The loop runs until you hit the exit conditions.

For each experiment:

1. **Read** `molecule.py` — current candidates, best score, strategy notes
2. **Hypothesize** — propose a molecular modification based on what you've learned
3. **Modify** `molecule.py` — change SMILES strings, add new candidates
4. **Evaluate** — run `python prepare.py evaluate <SMILES>` for each candidate (5-15 per round)
5. **Record** — append ALL results to `results.tsv` (even failures teach us)
6. **Judge:**
   - If composite_score > previous best → update BEST_SMILES, commit
   - If worse → revert molecule.py, log the failure
7. **Check novelty** of promising molecules (composite > 0.70): `python prepare.py novelty <SMILES>`
8. **Render** best molecules: `python prepare.py render <SMILES> renders/exp_N_name.png`
9. **Update STRATEGY_NOTES** with what you learned this round
10. **Repeat** from step 1

## Rules

- **NEVER** modify `prepare.py` — it's the frozen truth
- **ONLY** modify `molecule.py`
- All molecules must be valid SMILES (RDKit must parse them)
- Each experiment evaluates 5-15 candidates
- Log ALL evaluated molecules to results.tsv, including failures
- Commit format: `exp N: [description] — composite [score]`

## Scoring Breakdown (defined in prepare.py)

| Component | Weight | What it measures |
|-----------|--------|-----------------|
| Antibacterial profile | 25% | MW, LogP, N-count, TPSA, rings tuned for antibiotic space |
| Gram-negative permeability | 20% | eNTRy rules: primary amine, rigidity, amphiphilicity, size |
| Structural novelty | 15% | Tanimoto distance (top-3 avg) from 45 known antibiotics across all major classes |
| Drug-likeness | 15% | QED + relaxed Lipinski + PAINS + Veber |
| Synthesizability | 10% | SA Score (can it be made in a lab?) |
| Membrane disruption | 5% | Amphiphilic moment, cationic character |
| **Bonuses** | +5%, +3% | Novel gram-neg active; N-heterocycle + primary amine |

## Strategy Phases

### Phase 1: Baseline & Exploration (Experiments 1-5)
- Run baselines: `python prepare.py baseline`
- Evaluate Halicin and known antibiotics to understand scoring
- Try 3-4 different scaffold families (thiazoles, oxadiazoles, pyrimidines, quinolines)
- Goal: understand which structural features drive each sub-score

### Phase 2: Optimize Best Scaffold (Experiments 6-15)
- Pick the best-scoring scaffold family from Phase 1
- Systematic modifications: add/remove amine, change ring size, add substituents
- Focus on maximizing gram_neg_score (hardest sub-metric)
- Track: what modification → what effect on each sub-score

### Phase 3: Combine Insights (Experiments 16-25)
- Merge best features from different scaffolds
- Try hybrid structures (e.g., best gram-neg features + best novelty scaffold)
- Fragment merging: take amine from one, heterocycle from another
- This is where breakthroughs happen (drug-discovery found its champion here)

### Phase 4: Push the Frontier (Experiments 26-30)
- Focus on the highest-scoring molecule
- Fine-tune: isomers, stereochemistry, bioisosteric replacements
- Verify novelty of all top candidates
- Render top 5 molecules

## Molecular Design Tips for Antibiotics

**What makes a good antibiotic (different from general drugs):**
- Primary amine (NH2) — critical for gram-negative porin entry
- Nitrogen heterocycles — most antibiotics have them (pyridine, pyrimidine, thiazole, imidazole)
- MW 250-600 (wider range than general drugs)
- LogP -1 to 3 (more polar than general drugs)
- Rigid structures (fewer rotatable bonds = better porin penetration)
- Multiple nitrogen atoms (≥3 is common in antibiotics)
- Cationic character at physiological pH (protonated amines bind anionic bacterial membrane)

**Known mechanisms to exploit:**
- DNA gyrase inhibition (quinolones target this — but design DIFFERENT scaffolds)
- Cell wall synthesis disruption (β-lactams — but design non-β-lactam alternatives)
- Ribosome binding (aminoglycosides, tetracyclines — but different scaffolds)
- Membrane disruption (polymyxins — cationic amphiphiles)
- Metal chelation (starve bacteria of iron/zinc)
- Metabolic pathway inhibition (sulfonamides target folate synthesis)

**What kills the score:**
- No nitrogen → low antibacterial profile
- No amine → low gram-negative score
- Too similar to known class → low novelty score
- LogP > 4 → can't reach bacterial cytoplasm
- MW > 600 → can't enter porins
- PAINS hit → drug-likeness drops

## results.tsv Format

```
experiment	smiles	name	composite	antibacterial	gram_neg	novelty	druglike	novel	description
```

## Exit Conditions

Stop when ANY of these is true:
- **30 experiments completed** in this session
- **8 consecutive experiments with no improvement** in composite_score
- **Best composite_score > 0.90** with a novel molecule (exceptional candidate)
- Unrecoverable error

When stopping:
1. Update molecule.py with CHAMPION and full strategy notes
2. Check novelty of ALL top 10 molecules
3. Render top 5 to renders/
4. Write a summary of key discoveries and what worked/didn't work
