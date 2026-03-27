# How to Run: Antibiotic Discovery

## Prerequisites

1. **Python 3.10+**
2. **RDKit:**
   ```bash
   pip install rdkit
   ```
3. **Claude Code** installed and authenticated

## Run the Experiment

Launch Claude Code with permissions bypass for unattended execution:

```bash
claude --dangerously-skip-permissions
```

### Standard run (30 experiments)

Paste this prompt:

```
Read experiments/antibiotic-discovery/program.md and execute the optimization loop. Start by running python prepare.py baseline to understand the scoring. Run 30 experiments with 5-15 candidates each. Focus on primary amines for gram-negative penetration, nitrogen heterocycles, rigid structures, and scaffolds that are TRULY novel vs all 45 known antibiotic classes. Log everything to results.tsv. Exit after 30 experiments or 8 consecutive without improvement.
```

### Fresh start (reset and re-discover)

```
Read experiments/antibiotic-discovery/program.md and execute the optimization loop. Ignore the current best in molecule.py — start fresh from baselines. Run python prepare.py baseline first. Explore completely new scaffold families: thiazoles, oxadiazoles, pyrimidines, quinolines, benzimidazoles. 30 experiments, 5-15 candidates each.
```

## Expected Runtime

- ~60 minutes for 30 experiments

## Expected Output

| File | Description |
|------|-------------|
| `results.tsv` | Tab-separated log: experiment, SMILES, name, composite, antibacterial, gram_neg, novelty, druglike, novel, description |
| `renders/*.png` | 2D structure images of the best molecules |
| `molecule.py` | Updated with champion SMILES and strategy notes |

## Verify Results

```bash
# Check the results log
cat experiments/antibiotic-discovery/results.tsv

# Find the best composite scores
sort -t$'\t' -k4 -nr experiments/antibiotic-discovery/results.tsv | head -10

# Check novelty of the champion
python experiments/antibiotic-discovery/prepare.py novelty "Nc1[nH]c(CC2CCN(c3cnc(/C=C)cn3)CC2)cn1"
```

## Notes

- Composite score combines: antibacterial (25%), gram-neg permeability (20%), novelty (15%), drug-likeness (15%), synthesizability (10%), membrane disruption (5%), plus bonuses.
- Novelty is measured via Tanimoto distance from 45 known antibiotic classes.
- Primary amines are critical for gram-negative outer membrane penetration (Hergenrother's eNTRy rules).
