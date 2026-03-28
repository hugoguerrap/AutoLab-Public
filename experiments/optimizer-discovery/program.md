# Optimizer Discovery — Optimization Loop

## Goal
Discover a **novel optimization algorithm** that outperforms Adam and AdamW on neural network training. The optimizer must be a general-purpose update rule — not a hack specific to MNIST.

## Rules
1. **ONLY modify `optimizer.py`** — `prepare.py` is frozen
2. **Log ALL results** to `results.tsv` — even failures
3. **One hypothesis per iteration** — atomic, measurable, revertible
4. **Git commit** every improvement

## Evaluation Commands

```bash
# Evaluate your custom optimizer
python experiments/optimizer-discovery/prepare.py evaluate

# Run all baselines (SGD, Adam, AdamW, etc.)
python experiments/optimizer-discovery/prepare.py baseline

# Download MNIST data
python experiments/optimizer-discovery/prepare.py setup
```

## The Loop

### 1. READ
Read `optimizer.py` to understand the current update rule and strategy notes.

### 2. HYPOTHESIZE
Form ONE hypothesis about the update rule:
- "Adding exponential moving average of gradients (momentum) will improve convergence"
- "Tracking gradient variance per-parameter will enable adaptive learning rates"
- "Combining sign-based updates with magnitude tracking will balance speed and stability"

### 3. MODIFY
Edit `optimizer.py` — change the update rule in the `step()` method.
You can also adjust `LEARNING_RATE`.

### 4. EVALUATE
```bash
python experiments/optimizer-discovery/prepare.py evaluate
```
This trains a fresh MLP on MNIST for 10 epochs and outputs the composite score.

### 5. DECIDE
- **Better?** Update `optimizer.py`, commit to git.
- **Worse?** Revert `optimizer.py`, log the failure.

### 6. LOG
Append ALL results to `results.tsv`:
```
experiment	composite_score	val_acc	val_loss	convergence_epoch	stability	accuracy_score	loss_score	convergence_score	stability_score	lr	description
```

### 7. REPEAT

## Exit Conditions
- **Max experiments:** 15 iterations
- **Plateau:** 5 consecutive iterations with no improvement > 0.005
- **Target reached:** composite_score >= 0.95
- **Beats Adam by 5%+:** composite_score > Adam_baseline * 1.05

## Strategy Phases

### Phase 1: Understand the Landscape (exp 1-3)
- Run baseline to get SGD, Adam, AdamW scores
- Implement basic momentum SGD → understand the gap
- Try a simple adaptive method (RMSprop-like)
- Learn what sub-scores drive the composite

### Phase 2: Novel Combinations (exp 4-8)
- Combine momentum + adaptive LR in new ways
- Try gradient centralization + momentum
- Try sign-based updates with variance tracking
- Experiment with novel bias correction
- Try decoupled weight decay + novel momentum

### Phase 3: Creative Breakthroughs (exp 9-12)
- Invent completely new update rules
- Try hypergradient (learning the learning rate)
- Try curvature estimation from gradient history
- Try dual-rate updates (fast component + slow component)
- Gradient compression/quantization

### Phase 4: Fine-tuning (exp 13-15)
- Tune hyperparameters of best algorithm
- Try different learning rates
- Optimize the beta/momentum constants
- Push for ceiling score

## Scoring Breakdown
| Component | Weight | What it measures |
|-----------|--------|-----------------|
| Accuracy Score | 35% | Final val accuracy (0.90→0, 0.985→1) |
| Loss Score | 25% | Final val loss (0.35→0, 0.04→1) |
| Convergence Score | 25% | Speed to 95% accuracy (epoch 3 ideal) |
| Stability Score | 15% | Low variance in final epochs |

## Tips
- Adam's key insight: per-parameter adaptive LR from gradient moments
- Momentum's key insight: gradient history smooths noisy updates
- Weight decay is separate from L2 regularization (AdamW insight)
- Gradient centralization (subtract mean) often helps
- Learning rate warmup prevents early instability
- Don't overcomplicate: the best optimizers have simple update rules
- Test with the default LR=0.001 first, then tune
- The model is small (MLP) — techniques that help large models may not help here
- Convergence speed (25%) is as important as final accuracy
