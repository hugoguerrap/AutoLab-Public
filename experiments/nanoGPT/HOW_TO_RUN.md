# How to Run: nanoGPT Optimization

## Prerequisites

1. **Python 3.10+**
2. **PyTorch with CUDA support:**
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
   ```
3. **NVIDIA GPU** with CUDA 12.4 compatible drivers
4. **Claude Code** installed and authenticated

## Run the Experiment

Launch Claude Code with permissions bypass for unattended execution:

```bash
claude --dangerously-skip-permissions
```

Then paste this prompt:

```
Read experiments/nanoGPT/program.md and execute the optimization loop. Baseline val_loss is 1.6867. Your goal is to minimize it by modifying only train.py. Run experiments, measure, keep what works, revert what doesn't. Do not stop until you hit the exit conditions.
```

## Expected Runtime

~1 hour for 10 experiments (varies by GPU).

## Expected Output

| File | Description |
|------|-------------|
| `results.tsv` | Tab-separated log of every experiment: iteration, change description, val_loss, accept/reject |
| Git commits | One commit per accepted experiment, so you can `git log` to see the progression |

## Verify Results

```bash
# Check the results log
cat experiments/nanoGPT/results.tsv

# See the progression of accepted changes
git log --oneline experiments/nanoGPT/

# Compare final val_loss against baseline (1.6867)
tail -1 experiments/nanoGPT/results.tsv
```

## Notes

- Each experiment modifies `train.py`, trains, measures val_loss, and either keeps or reverts the change.
- The loop exits when it hits the iteration limit or when improvements plateau.
- GPU memory errors will cause the experiment to be reverted automatically.
