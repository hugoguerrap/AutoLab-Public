# How to Run: Artificial Life Optimization

## Prerequisites

1. **Python 3.10+**
2. **numpy and Pillow:**
   ```bash
   pip install numpy Pillow
   ```
3. **Claude Code** installed and authenticated

## Run the Experiment

Launch Claude Code with permissions bypass for unattended execution:

```bash
claude --dangerously-skip-permissions
```

Then paste this prompt:

```
Read experiments/artificial-life/program.md and execute the optimization loop. Start with the Orbium baseline parameters, then evolve rules that produce emergent life-like behavior — survival, movement, complexity, oscillation. Save GIFs of interesting results. Do not stop until you hit the exit conditions.
```

## Expected Runtime

~20 minutes for 10 experiments.

## Expected Output

| File | Description |
|------|-------------|
| `results.tsv` | Tab-separated log: iteration, rule parameters, fitness metrics (survival, complexity, movement), accept/reject |
| `renders/*.gif` | Animated GIFs of the most interesting emergent behaviors |

## Verify Results

```bash
# Check the results log
cat experiments/artificial-life/results.tsv

# List generated GIFs
ls experiments/artificial-life/renders/

# Find experiments with longest survival
sort -t$'\t' -k3 -nr experiments/artificial-life/results.tsv | head -5
```

## Notes

- Orbium is a well-known Lenia species (continuous cellular automaton) that exhibits glider-like behavior.
- The optimizer mutates kernel parameters and growth functions to discover novel life-like patterns.
- GIFs are saved for experiments that show interesting emergent properties (movement, oscillation, self-replication).
- No GPU required -- all simulations run on CPU with numpy.
