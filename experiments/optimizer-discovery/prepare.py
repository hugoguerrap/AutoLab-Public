#!/usr/bin/env python3
"""
FROZEN EVALUATOR — DO NOT MODIFY
Optimizer Discovery: Novel Optimization Algorithms for Neural Networks

Trains a small MLP on MNIST with a candidate optimizer and measures:
- Final validation accuracy
- Final validation loss
- Convergence speed (epochs to reach 95% accuracy)
- Training stability (loss variance in final epochs)

Usage:
    python prepare.py evaluate              # Evaluate optimizer from optimizer.py
    python prepare.py baseline              # Run all baseline optimizers
    python prepare.py setup                 # Download MNIST data
"""

import sys
import os
import json
import time
import math
import importlib.util

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

# ── Configuration ──────────────────────────────────────────────
SEED = 42
EPOCHS = 10
BATCH_SIZE = 128
LR = 0.001  # default learning rate for all optimizers
HIDDEN_1 = 256
HIDDEN_2 = 128
INPUT_DIM = 784  # 28x28
OUTPUT_DIM = 10
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Scoring thresholds (calibrated for MNIST + small MLP + 10 epochs)
ACC_FLOOR = 0.90    # below this, score = 0
ACC_CEILING = 0.985  # above this, score = 1
LOSS_FLOOR = 0.35   # above this, score = 0
LOSS_CEILING = 0.04  # below this, score = 1
CONVERGENCE_TARGET = 3  # ideal: reach 95% acc by epoch 3


# ── Data Setup ─────────────────────────────────────────────────

def download_mnist():
    """Download MNIST using torchvision or generate synthetic data."""
    os.makedirs(DATA_DIR, exist_ok=True)
    train_path = os.path.join(DATA_DIR, "train_data.pt")
    test_path = os.path.join(DATA_DIR, "test_data.pt")

    if os.path.exists(train_path) and os.path.exists(test_path):
        return

    try:
        from torchvision import datasets, transforms
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
        train_ds = datasets.MNIST(DATA_DIR, train=True, download=True, transform=transform)
        test_ds = datasets.MNIST(DATA_DIR, train=False, download=True, transform=transform)

        # Convert to tensors
        train_x = torch.stack([train_ds[i][0].view(-1) for i in range(len(train_ds))])
        train_y = torch.tensor([train_ds[i][1] for i in range(len(train_ds))])
        test_x = torch.stack([test_ds[i][0].view(-1) for i in range(len(test_ds))])
        test_y = torch.tensor([test_ds[i][1] for i in range(len(test_ds))])

        torch.save((train_x, train_y), train_path)
        torch.save((test_x, test_y), test_path)
        print(f"MNIST downloaded: {len(train_x)} train, {len(test_x)} test")

    except Exception as e:
        print(f"MNIST download failed ({e}), generating synthetic data...")
        torch.manual_seed(SEED)
        train_x = torch.randn(10000, INPUT_DIM)
        train_y = torch.randint(0, OUTPUT_DIM, (10000,))
        test_x = torch.randn(2000, INPUT_DIM)
        test_y = torch.randint(0, OUTPUT_DIM, (2000,))
        torch.save((train_x, train_y), train_path)
        torch.save((test_x, test_y), test_path)
        print("Synthetic data generated (MNIST unavailable)")


def load_data():
    """Load MNIST data tensors."""
    train_path = os.path.join(DATA_DIR, "train_data.pt")
    test_path = os.path.join(DATA_DIR, "test_data.pt")

    if not os.path.exists(train_path):
        download_mnist()

    train_x, train_y = torch.load(train_path, weights_only=True)
    test_x, test_y = torch.load(test_path, weights_only=True)
    return train_x, train_y, test_x, test_y


# ── Model ──────────────────────────────────────────────────────

class MLP(nn.Module):
    """Fixed MLP architecture. Same for all optimizers."""
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(INPUT_DIM, HIDDEN_1)
        self.fc2 = nn.Linear(HIDDEN_1, HIDDEN_2)
        self.fc3 = nn.Linear(HIDDEN_2, OUTPUT_DIM)
        self.dropout = nn.Dropout(0.1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x


def init_model(seed=SEED):
    """Create a fresh model with fixed initialization."""
    torch.manual_seed(seed)
    model = MLP()
    return model


# ── Training Engine ────────────────────────────────────────────

def train_and_evaluate(optimizer_fn, lr=LR, seed=SEED, verbose=True):
    """
    Train an MLP with the given optimizer and return metrics.

    optimizer_fn: callable(params, lr) -> optimizer instance
    Returns dict with all metrics.
    """
    torch.manual_seed(seed)

    # Load data
    train_x, train_y, test_x, test_y = load_data()
    train_loader = DataLoader(
        TensorDataset(train_x, train_y),
        batch_size=BATCH_SIZE, shuffle=True,
        generator=torch.Generator().manual_seed(seed)
    )
    test_loader = DataLoader(
        TensorDataset(test_x, test_y),
        batch_size=BATCH_SIZE * 2, shuffle=False
    )

    # Init model
    model = init_model(seed)
    criterion = nn.CrossEntropyLoss()

    # Create optimizer
    try:
        optimizer = optimizer_fn(model.parameters(), lr=lr)
    except Exception as e:
        return {"error": f"Optimizer creation failed: {e}", "composite_score": 0.0}

    # Training loop
    epoch_metrics = []
    convergence_epoch = EPOCHS  # default: never converged
    start_time = time.time()

    for epoch in range(EPOCHS):
        model.train()
        train_loss_sum = 0.0
        train_correct = 0
        train_total = 0

        for batch_x, batch_y in train_loader:
            try:
                optimizer.zero_grad()
                output = model(batch_x)
                loss = criterion(output, batch_y)
                loss.backward()
                optimizer.step()

                train_loss_sum += loss.item() * batch_x.size(0)
                train_correct += (output.argmax(1) == batch_y).sum().item()
                train_total += batch_x.size(0)
            except Exception as e:
                return {"error": f"Training step failed at epoch {epoch}: {e}", "composite_score": 0.0}

        # Validation
        model.eval()
        val_loss_sum = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for batch_x, batch_y in test_loader:
                output = model(batch_x)
                loss = criterion(output, batch_y)
                val_loss_sum += loss.item() * batch_x.size(0)
                val_correct += (output.argmax(1) == batch_y).sum().item()
                val_total += batch_x.size(0)

        train_loss = train_loss_sum / train_total
        train_acc = train_correct / train_total
        val_loss = val_loss_sum / val_total
        val_acc = val_correct / val_total

        epoch_metrics.append({
            "epoch": epoch + 1,
            "train_loss": round(train_loss, 6),
            "train_acc": round(train_acc, 4),
            "val_loss": round(val_loss, 6),
            "val_acc": round(val_acc, 4),
        })

        if verbose:
            print(f"  Epoch {epoch+1:2d}: train_loss={train_loss:.4f} train_acc={train_acc:.4f} "
                  f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}")

        # Track convergence (first epoch >= 95% val accuracy)
        if val_acc >= 0.95 and convergence_epoch == EPOCHS:
            convergence_epoch = epoch + 1

    elapsed = time.time() - start_time
    final = epoch_metrics[-1]

    # Stability: std of val_loss in last 3 epochs
    last_losses = [m["val_loss"] for m in epoch_metrics[-3:]]
    stability = float(torch.tensor(last_losses).std().item()) if len(last_losses) > 1 else 0.0

    return {
        "val_loss": final["val_loss"],
        "val_acc": final["val_acc"],
        "train_loss": final["train_loss"],
        "train_acc": final["train_acc"],
        "convergence_epoch": convergence_epoch,
        "stability": round(stability, 6),
        "elapsed_seconds": round(elapsed, 1),
        "epoch_metrics": epoch_metrics,
    }


# ── Scoring ────────────────────────────────────────────────────

def compute_score(metrics):
    """
    Compute composite score from training metrics.

    composite = 0.35 * accuracy_score
              + 0.25 * loss_score
              + 0.25 * convergence_score
              + 0.15 * stability_score
    """
    if "error" in metrics:
        return 0.0, {"error": metrics["error"]}

    val_acc = metrics["val_acc"]
    val_loss = metrics["val_loss"]
    conv_epoch = metrics["convergence_epoch"]
    stability = metrics["stability"]

    # Accuracy score: linear scale from floor to ceiling
    if val_acc >= ACC_CEILING:
        acc_score = 1.0
    elif val_acc <= ACC_FLOOR:
        acc_score = 0.0
    else:
        acc_score = (val_acc - ACC_FLOOR) / (ACC_CEILING - ACC_FLOOR)

    # Loss score: lower is better
    if val_loss <= LOSS_CEILING:
        loss_score = 1.0
    elif val_loss >= LOSS_FLOOR:
        loss_score = 0.0
    else:
        loss_score = (LOSS_FLOOR - val_loss) / (LOSS_FLOOR - LOSS_CEILING)

    # Convergence score: faster is better
    if conv_epoch <= CONVERGENCE_TARGET:
        conv_score = 1.0
    elif conv_epoch >= EPOCHS:
        conv_score = 0.1  # never reached 95%
    else:
        conv_score = 1.0 - 0.9 * (conv_epoch - CONVERGENCE_TARGET) / (EPOCHS - CONVERGENCE_TARGET)

    # Stability score: lower variance is better
    if stability <= 0.001:
        stab_score = 1.0
    elif stability >= 0.05:
        stab_score = 0.0
    else:
        stab_score = 1.0 - (stability - 0.001) / (0.05 - 0.001)

    # Composite
    composite = (
        0.35 * acc_score
        + 0.25 * loss_score
        + 0.25 * conv_score
        + 0.15 * stab_score
    )

    sub_scores = {
        "accuracy_score": round(acc_score, 4),
        "loss_score": round(loss_score, 4),
        "convergence_score": round(conv_score, 4),
        "stability_score": round(stab_score, 4),
    }

    return round(composite, 4), sub_scores


# ── Baselines ──────────────────────────────────────────────────

def get_baselines():
    """Return baseline optimizer factories."""
    return {
        "SGD": lambda params, lr: torch.optim.SGD(params, lr=lr),
        "SGD_Momentum": lambda params, lr: torch.optim.SGD(params, lr=lr, momentum=0.9),
        "SGD_Nesterov": lambda params, lr: torch.optim.SGD(params, lr=lr, momentum=0.9, nesterov=True),
        "Adam": lambda params, lr: torch.optim.Adam(params, lr=lr),
        "AdamW": lambda params, lr: torch.optim.AdamW(params, lr=lr, weight_decay=0.01),
        "RMSprop": lambda params, lr: torch.optim.RMSprop(params, lr=lr),
    }


def run_baseline():
    """Evaluate all baseline optimizers."""
    print("\n" + "=" * 70)
    print("  OPTIMIZER DISCOVERY — BASELINE EVALUATION")
    print("=" * 70)
    print(f"  Model: MLP({INPUT_DIM}→{HIDDEN_1}→{HIDDEN_2}→{OUTPUT_DIM})")
    print(f"  Dataset: MNIST, {EPOCHS} epochs, batch_size={BATCH_SIZE}, lr={LR}")
    print("=" * 70)

    download_mnist()
    results = []

    for name, opt_fn in get_baselines().items():
        print(f"\n--- {name} ---")
        metrics = train_and_evaluate(opt_fn, lr=LR)
        composite, sub = compute_score(metrics)
        metrics["composite_score"] = composite
        metrics["sub_scores"] = sub
        metrics["name"] = name
        results.append(metrics)

    # Summary table
    results.sort(key=lambda x: x["composite_score"], reverse=True)
    print(f"\n{'='*70}")
    print(f"{'Optimizer':<20} {'Composite':>9} {'ValAcc':>7} {'ValLoss':>8} {'ConvEp':>7} {'Stab':>7}")
    print("-" * 70)
    for r in results:
        print(
            f"{r['name']:<20} {r['composite_score']:>9.4f} "
            f"{r['val_acc']:>7.4f} {r['val_loss']:>8.4f} "
            f"{r['convergence_epoch']:>7d} {r['stability']:>7.4f}"
        )
    print(f"\nBest baseline: {results[0]['name']} = {results[0]['composite_score']:.4f}")
    print(f"Target: Beat Adam/AdamW with a novel update rule")
    return results


# ── Custom Optimizer Evaluation ────────────────────────────────

def load_custom_optimizer():
    """Load the CustomOptimizer from optimizer.py."""
    opt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "optimizer.py")
    if not os.path.exists(opt_path):
        print(f"ERROR: {opt_path} not found")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("custom_optimizer", opt_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    if not hasattr(mod, "CustomOptimizer"):
        print("ERROR: optimizer.py must define a CustomOptimizer class")
        sys.exit(1)

    return mod.CustomOptimizer, getattr(mod, "LEARNING_RATE", LR)


def run_evaluate():
    """Evaluate the custom optimizer from optimizer.py."""
    print("\n" + "=" * 70)
    print("  EVALUATING CUSTOM OPTIMIZER")
    print("=" * 70)

    download_mnist()
    CustomOptimizer, lr = load_custom_optimizer()

    print(f"  Optimizer: {CustomOptimizer.__name__}")
    print(f"  Learning rate: {lr}")
    print()

    opt_fn = lambda params, lr=lr: CustomOptimizer(params, lr=lr)
    metrics = train_and_evaluate(opt_fn, lr=lr)

    if "error" in metrics:
        print(f"\nERROR: {metrics['error']}")
        print(json.dumps({"composite_score": 0.0, "error": metrics["error"]}, indent=2))
        return metrics

    composite, sub = compute_score(metrics)
    metrics["composite_score"] = composite
    metrics["sub_scores"] = sub

    print(f"\n{'='*60}")
    print(f"  Composite Score:    {composite:.4f}")
    print(f"  ─────────────────────────────────")
    print(f"  Val Accuracy:       {metrics['val_acc']:.4f}  (score: {sub['accuracy_score']:.4f})")
    print(f"  Val Loss:           {metrics['val_loss']:.4f}  (score: {sub['loss_score']:.4f})")
    print(f"  Convergence Epoch:  {metrics['convergence_epoch']}       (score: {sub['convergence_score']:.4f})")
    print(f"  Stability (std):    {metrics['stability']:.6f}  (score: {sub['stability_score']:.4f})")
    print(f"  Elapsed:            {metrics['elapsed_seconds']}s")
    print(f"{'='*60}")

    print(json.dumps({
        "composite_score": composite,
        "val_acc": metrics["val_acc"],
        "val_loss": metrics["val_loss"],
        "convergence_epoch": metrics["convergence_epoch"],
        "stability": metrics["stability"],
        "sub_scores": sub,
    }, indent=2))

    return metrics


# ── CLI ────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python prepare.py [evaluate|baseline|setup]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "setup":
        download_mnist()
        print("Data setup complete.")

    elif cmd == "baseline":
        run_baseline()

    elif cmd == "evaluate":
        run_evaluate()

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: evaluate, baseline, setup")
        sys.exit(1)


if __name__ == "__main__":
    main()
