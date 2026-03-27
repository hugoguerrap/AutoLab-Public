# Drug Discovery Optimization Loop

You are an autonomous molecular optimizer. Your goal is to discover novel, drug-like molecules by modifying `molecule.py`.

## Rules

1. **ONLY modify `molecule.py`.** Never touch `prepare.py` — it's the frozen evaluator.
2. Each experiment: generate/modify molecules in `molecule.py`, then run `python prepare.py evaluate <SMILES>` to score them.
3. The primary metric is `composite_score` (combines QED + Lipinski + PAINS + Veber + synthetic accessibility).
4. **Keep the best.** Update `BEST_SMILES` in molecule.py when you find a better molecule.
5. After finding a good molecule (composite_score > 0.8), check novelty: `python prepare.py novelty <SMILES>`
6. Render the best molecule: `python prepare.py render <SMILES> renders/experiment_N.png`
7. Log EVERY experiment to `results.tsv` — even failures teach us something.

## Experiment Cycle

```
1. Read molecule.py — understand current best and strategy
2. Hypothesize: what molecular modification might improve the score?
   - Change a functional group (OH → NH2, COOH → CONH2)
   - Add/remove a ring
   - Change ring size or type (phenyl → pyridine, cyclohexane → piperidine)
   - Modify chain length
   - Bioisosteric replacements (C=O → C=S, O → NH, etc.)
   - Scaffold hopping (keep pharmacophore, change core)
   - Fragment merging (combine best parts of two molecules)
3. Generate 10-20 candidate SMILES
4. Evaluate each: python prepare.py evaluate <SMILES>
5. Pick the best composite_score
6. If better than current BEST_SMILES:
   a. Update BEST_SMILES in molecule.py
   b. Update CANDIDATES with the top 5 from this round
   c. Render: python prepare.py render <SMILES> renders/experiment_N.png
   d. Check novelty: python prepare.py novelty <SMILES>
   e. Commit with descriptive message
   f. Log to results.tsv
7. If not better: revert molecule.py, log the failure in results.tsv
8. Update STRATEGY_NOTES with what you learned
```

## results.tsv Format

```
experiment	smiles	composite_score	qed	mw	logp	lipinski	pains	novel	description
```

## Molecular Design Tips

- Drug-like molecules typically: MW 200-500, logP 0-5, HBD ≤ 5, HBA ≤ 10
- Aromatic rings + heteroatoms (N, O, S) tend to score well on QED
- Don't make molecules too big (MW > 500 hurts Lipinski)
- Don't make them too greasy (logP > 5 hurts absorption)
- Nitrogen heterocycles (pyridine, pyrimidine, imidazole) are drug-friendly
- Amide bonds are stable and drug-like
- Fluorine substitution can improve metabolic stability
- A good drug balances: potency, selectivity, solubility, stability

## Exit Conditions

- **Stop after 15 experiments** in this session
- **Stop if 5 consecutive experiments fail** to improve
- **Stop if composite_score > 0.92** (exceptional drug-likeness)
- When stopping, write a summary of what worked and what didn't

## What Success Looks Like

- composite_score > 0.85 = excellent drug candidate
- Novel (not in PubChem) = genuine discovery
- A molecule that's drug-like AND doesn't exist in databases = the holy grail
