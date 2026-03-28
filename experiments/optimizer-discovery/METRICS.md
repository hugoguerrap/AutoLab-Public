# Optimizer Discovery — Frozen Metrics

## DO NOT MODIFY THIS FILE

## Primary Metric
**composite_score** (0.0 – 1.0)

Target: Beat Adam/AdamW baselines with a novel update rule.

## Composite Formula

```
composite = 0.35 * accuracy_score
          + 0.25 * loss_score
          + 0.25 * convergence_score
          + 0.15 * stability_score
```

## Sub-Metrics

| Metric | Range | Formula | Target |
|--------|-------|---------|--------|
| accuracy_score | 0–1 | (val_acc - 0.90) / (0.985 - 0.90) | >= 0.9 |
| loss_score | 0–1 | (0.35 - val_loss) / (0.35 - 0.04) | >= 0.9 |
| convergence_score | 0–1 | Based on epoch reaching 95% acc (3 = ideal) | >= 0.8 |
| stability_score | 0–1 | 1 - (loss_std / 0.05), last 3 epochs | >= 0.9 |

## Training Setup (Frozen)

| Parameter | Value |
|-----------|-------|
| Model | MLP (784 → 256 → 128 → 10) |
| Dataset | MNIST (60K train, 10K test) |
| Epochs | 10 |
| Batch Size | 128 |
| Default LR | 0.001 |
| Dropout | 0.1 |
| Loss | CrossEntropyLoss |
| Seed | 42 (reproducible) |

## Baselines

| Optimizer | Expected Composite | Expected Accuracy |
|-----------|-------------------|-------------------|
| SGD | ~0.35-0.45 | ~92-94% |
| SGD+Momentum | ~0.65-0.75 | ~96-97% |
| Adam | ~0.75-0.85 | ~97-98% |
| AdamW | ~0.75-0.85 | ~97-98% |
| RMSprop | ~0.60-0.70 | ~96-97% |

## Success Criteria

| Level | Composite Score | Meaning |
|-------|----------------|---------|
| Baseline | ~0.40 | Plain SGD level |
| Good | > 0.70 | Momentum SGD level |
| **Target** | **> Adam** | **Novel optimizer matches Adam** |
| Excellent | > Adam + 5% | Genuinely better algorithm |
| Discovery | > 0.95 | Near-perfect optimization |
