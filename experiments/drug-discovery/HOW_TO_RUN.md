# How to Run: Drug Discovery Optimization

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

### Standard run (10 iterations)

Paste this prompt:

```
Read experiments/drug-discovery/program.md and execute the optimization loop. Start from the baseline molecules, optimize for QED and novelty. Log everything to results.tsv.
```

### Extended run (20 iterations, divergent exploration)

Paste this prompt instead:

```
Read experiments/drug-discovery/program.md and execute the optimization loop. Override exit conditions: run 20 experiments instead of 10. Start from the current best molecule in molecule.py and keep pushing for higher QED and more novel structures. Try radically different scaffolds — not just pyrrolidine variants. Explore oxazines, morpholines, piperazines, indoles, benzimidazoles. Log everything.
```

## Expected Runtime

- ~30 minutes for 10 iterations
- ~60 minutes for 20 iterations

## Expected Output

| File | Description |
|------|-------------|
| `results.tsv` | Tab-separated log: iteration, SMILES, QED score, novelty metrics, accept/reject |
| `renders/*.png` | 2D structure images of the best molecules discovered |

## Verify Results

```bash
# Check the results log
cat experiments/drug-discovery/results.tsv

# List rendered molecule images
ls experiments/drug-discovery/renders/

# Find the best QED score
sort -t$'\t' -k3 -nr experiments/drug-discovery/results.tsv | head -5
```

## Notes

- QED (Quantitative Estimate of Drug-likeness) ranges from 0 to 1. Higher is better.
- The divergent prompt pushes exploration beyond local optima by trying entirely different molecular scaffolds.
- All generated molecules are validated for chemical feasibility via RDKit.
