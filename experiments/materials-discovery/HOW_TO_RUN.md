# How to Run: Materials Discovery Optimization

## Prerequisites

1. **Python 3.10+**
2. **pymatgen:**
   ```bash
   pip install pymatgen
   ```
3. **Claude Code** installed and authenticated

## Run the Experiment

Launch Claude Code with permissions bypass for unattended execution:

```bash
claude --dangerously-skip-permissions
```

Then paste this prompt:

```
Read experiments/materials-discovery/program.md and execute the optimization loop. Start with the BaTiO3 baseline, then discover novel materials with useful properties. Focus on solar cell and thermoelectric candidates. Do not stop until you hit the exit conditions.
```

## Expected Runtime

~30 minutes for 10 experiments.

## Expected Output

| File | Description |
|------|-------------|
| `results.tsv` | Tab-separated log: iteration, composition, target property scores, accept/reject |

## Verify Results

```bash
# Check the results log
cat experiments/materials-discovery/results.tsv

# Count accepted experiments
grep -c "accept" experiments/materials-discovery/results.tsv

# See the best candidates
sort -t$'\t' -k3 -nr experiments/materials-discovery/results.tsv | head -5
```

## Notes

- The baseline is BaTiO3 (barium titanate), a well-known perovskite.
- The optimizer explores compositions targeting solar cell efficiency (band gap) and thermoelectric performance (Seebeck coefficient, thermal conductivity).
- pymatgen validates crystal structures and computes properties.
