# Fertilizer Design — Optimization Program

## Objective

Discover novel nitrogen-carrying molecules that are **better than urea** for agricultural use:
- Slower nutrient release (less waste, less pollution)
- Biodegradable (EU 2026 compliant)
- High nitrogen content (>20% N by mass)
- Affordable to synthesize
- Not found in PubChem (genuinely novel)

## The Loop

For each experiment:

1. **Read** `molecule.py` — current candidates and best score
2. **Hypothesize** — propose a modification to improve composite_score
3. **Modify** `molecule.py` — change SMILES strings, add new candidates
4. **Evaluate** — run `python prepare.py evaluate <SMILES>` for each candidate
5. **Record** — append results to `results.tsv`
6. **Judge:**
   - If composite_score > previous best → `git commit` with description
   - If worse or equal → `git checkout molecule.py` to revert
7. **Check novelty** of best molecules: `python prepare.py novelty <SMILES>`
8. **Render** top molecules: `python prepare.py render <SMILES> renders/exp_N_name.png`
9. **Repeat** from step 1

## Rules

- **NEVER** modify `prepare.py` — it's the frozen truth
- **ONLY** modify `molecule.py`
- All molecules must be valid SMILES (RDKit must parse them)
- Each experiment evaluates 3-8 candidates per round
- Commit message format: `exp: [description] — composite [score], N% [pct]`
- Log ALL evaluated molecules to results.tsv, including failures

## What to Optimize For

The composite score weights (defined in prepare.py):
- Nutrient content: 20% (must carry nitrogen)
- **Slow-release: 25%** (the KEY differentiator vs urea)
- Solubility: 10% (moderate — not too fast, not too slow)
- Biodegradability: 15% (EU compliance)
- Environmental safety: 10% (less runoff)
- Cost: 10% (affordable atoms)
- Synthesizability: 10% (can be made in a lab)

Bonuses:
- +5% for slow-release > 0.6 AND N% > 20 (the holy grail)
- +3% for biodegradable > 0.7 AND slow-release > 0.5 (EU compliant slow-release)

## Strategy Suggestions

1. **Start with urea derivatives** — they're the most studied, good baseline
2. **Try oligomers** — biuret, triuret, longer chains
3. **Try cyclic structures** — triazines, pyrimidines, barbiturates
4. **Add hydrophobic groups** — slow water penetration, slower release
5. **Try guanidine** — very high N%, natural slow-release
6. **Combine N + P** — dual-nutrient molecules
7. **Cross-link with formaldehyde** — methylene urea (known slow-release)
8. **Try amino acid conjugates** — natural, biodegradable, slow-release

## Baselines (for reference)

Run `python prepare.py baseline` to see:
- Urea: 46.6% N, fast release, composite ~0.55
- Biuret: 40.8% N, slightly slower, composite ~0.60
- IBDU: slow-release commercial product

Your goal: **beat all baselines on composite score while discovering novel molecules.**

## Exit Conditions

Stop when ANY of these is true:
- 15 experiments completed in this session
- 5 consecutive experiments with no improvement in composite_score
- Best composite_score > 0.85 with a novel molecule
- Unrecoverable error (RDKit crash, disk full, etc.)

When done, update molecule.py BEST_SMILES with the champion and summarize findings.

## results.tsv Format

```
experiment\tsmiles\tname\tcomposite\tn_pct\tslow_release\tbiodeg\tnovel\tdescription
```
