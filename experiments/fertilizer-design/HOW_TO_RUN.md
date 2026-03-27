# How to Run: Fertilizer Design Optimization

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

Then paste this prompt:

```
Read experiments/fertilizer-design/program.md and execute the optimization loop. Start from urea baseline, discover novel slow-release nitrogen carriers with high N-content and biodegradability. Compare against commercial IBDU. Log everything.
```

## Expected Runtime

~30 minutes for 15 experiments.

## Expected Output

| File | Description |
|------|-------------|
| `results.tsv` | Tab-separated log: iteration, SMILES, N-content (%), biodegradability score, slow-release estimate, accept/reject |
| `renders/*.png` | 2D structure images of the best fertilizer molecules |

## Verify Results

```bash
# Check the results log
cat experiments/fertilizer-design/results.tsv

# List rendered molecule images
ls experiments/fertilizer-design/renders/

# Find highest nitrogen content molecules
sort -t$'\t' -k3 -nr experiments/fertilizer-design/results.tsv | head -5
```

## Notes

- Urea (46% N) is the baseline. IBDU (isobutylidene diurea, ~32% N) is the commercial slow-release benchmark.
- The optimizer balances nitrogen content, biodegradability, and slow-release properties.
- All molecules are validated for chemical feasibility via RDKit.
- Higher N-content is better, but must be balanced with practical slow-release and environmental safety.
