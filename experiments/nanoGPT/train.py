"""
nanoGPT training script — THE file that Claude Code optimizes.

This is the ONLY file the agent can modify during the Karpathy Loop.
Everything here is fair game: architecture, hyperparameters, optimizer,
scheduler, training loop, etc.

Usage:
    python train.py                  # Train for TRAIN_MINUTES
    python train.py --benchmark      # Output metrics for the loop
"""
import argparse
import math
import os
import sys
import time

import torch
import torch.nn as nn
import torch.nn.functional as F

# Add parent to path for prepare.py imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prepare import load_data, get_batch, estimate_loss, generate_sample

# ============================================================
# HYPERPARAMETERS — Claude can tune these
# ============================================================
BATCH_SIZE = 64
BLOCK_SIZE = 256       # context window
N_EMBD = 384           # embedding dimension
N_HEAD = 6             # attention heads
N_LAYER = 6            # transformer blocks
DROPOUT = 0.2
LEARNING_RATE = 1e-3
WEIGHT_DECAY = 2e-1
BETA1 = 0.9
BETA2 = 0.95
GRAD_CLIP = 1.0
WARMUP_ITERS = 100
TRAIN_MINUTES = 5      # wall-clock training budget (frozen by convention)

# ============================================================
# MODEL — Claude can modify architecture
# ============================================================

class CausalSelfAttention(nn.Module):
    def __init__(self, n_embd, n_head, block_size, dropout):
        super().__init__()
        assert n_embd % n_head == 0
        self.n_head = n_head
        self.n_embd = n_embd
        self.head_dim = n_embd // n_head
        self.c_attn = nn.Linear(n_embd, 3 * n_embd, bias=False)
        self.c_proj = nn.Linear(n_embd, n_embd, bias=False)
        self.attn_dropout = nn.Dropout(dropout)
        self.resid_dropout = nn.Dropout(dropout)

    def forward(self, x):
        B, T, C = x.size()
        q, k, v = self.c_attn(x).split(self.n_embd, dim=2)
        q = q.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        # Use PyTorch's scaled_dot_product_attention (Flash Attention when available)
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True, dropout_p=self.attn_dropout.p if self.training else 0.0)
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        y = self.resid_dropout(self.c_proj(y))
        return y


class MLP(nn.Module):
    def __init__(self, n_embd, dropout):
        super().__init__()
        self.c_fc = nn.Linear(n_embd, 4 * n_embd, bias=False)
        self.gelu = nn.GELU()
        self.c_proj = nn.Linear(4 * n_embd, n_embd, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        x = self.c_fc(x)
        x = self.gelu(x)
        x = self.c_proj(x)
        x = self.dropout(x)
        return x


class Block(nn.Module):
    def __init__(self, n_embd, n_head, block_size, dropout):
        super().__init__()
        self.ln_1 = nn.LayerNorm(n_embd)
        self.attn = CausalSelfAttention(n_embd, n_head, block_size, dropout)
        self.ln_2 = nn.LayerNorm(n_embd)
        self.mlp = MLP(n_embd, dropout)

    def forward(self, x):
        x = x + self.attn(self.ln_1(x))
        x = x + self.mlp(self.ln_2(x))
        return x


class GPT(nn.Module):
    def __init__(self, vocab_size, block_size, n_embd, n_head, n_layer, dropout):
        super().__init__()
        self.block_size = block_size
        self.tok_emb = nn.Embedding(vocab_size, n_embd)
        self.pos_emb = nn.Embedding(block_size, n_embd)
        self.drop = nn.Dropout(dropout)
        self.blocks = nn.ModuleList([
            Block(n_embd, n_head, block_size, dropout) for _ in range(n_layer)
        ])
        self.ln_f = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size, bias=False)

        # Weight tying
        self.tok_emb.weight = self.lm_head.weight

        # Init weights
        self.apply(self._init_weights)
        # Scale residual projections
        for pn, p in self.named_parameters():
            if pn.endswith("c_proj.weight"):
                torch.nn.init.normal_(p, mean=0.0, std=0.02 / math.sqrt(2 * n_layer))

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx, targets=None):
        B, T = idx.size()
        assert T <= self.block_size, f"Sequence length {T} > block_size {self.block_size}"
        pos = torch.arange(0, T, dtype=torch.long, device=idx.device)
        tok_emb = self.tok_emb(idx)
        pos_emb = self.pos_emb(pos)
        x = self.drop(tok_emb + pos_emb)
        for block in self.blocks:
            x = block(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)

        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss

    def count_params(self):
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# ============================================================
# TRAINING LOOP
# ============================================================

def train():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # Load data
    train_data, val_data, vocab_size = load_data()
    print(f"Vocab: {vocab_size}, Train tokens: {len(train_data):,}, Val tokens: {len(val_data):,}")

    # Create model
    model = GPT(vocab_size, BLOCK_SIZE, N_EMBD, N_HEAD, N_LAYER, DROPOUT).to(device)
    n_params = model.count_params()
    print(f"Model params: {n_params:,} ({n_params/1e6:.1f}M)")

    # Optimizer
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        betas=(BETA1, BETA2),
        weight_decay=WEIGHT_DECAY,
    )

    # Training
    model.train()
    t_start = time.time()
    deadline = t_start + TRAIN_MINUTES * 60
    step = 0
    best_val_loss = float("inf")

    # Mixed precision training
    use_amp = device == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)
    amp_dtype = torch.float16

    # torch.compile requires Triton (Linux only). Skip on Windows.
    if hasattr(torch, "compile") and sys.platform != "win32":
        try:
            model = torch.compile(model)
            print("torch.compile enabled")
        except Exception:
            pass

    print(f"Training for {TRAIN_MINUTES} minutes... (AMP: {use_amp})")
    print("-" * 60)

    # Estimate total steps for cosine schedule (based on ~2200 steps in 5 min)
    MAX_ITERS = 2500
    MIN_LR = LEARNING_RATE * 0.1  # decay to 10% of peak

    while time.time() < deadline:
        # Learning rate schedule: warmup + cosine decay to MIN_LR
        if step < WARMUP_ITERS:
            lr = LEARNING_RATE * (step + 1) / WARMUP_ITERS
        else:
            decay_ratio = min((step - WARMUP_ITERS) / (MAX_ITERS - WARMUP_ITERS), 1.0)
            coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
            lr = MIN_LR + coeff * (LEARNING_RATE - MIN_LR)
        for pg in optimizer.param_groups:
            pg["lr"] = lr

        # Get batch and forward
        xb, yb = get_batch("train", train_data, val_data, BATCH_SIZE, BLOCK_SIZE, device)
        with torch.amp.autocast("cuda", enabled=use_amp, dtype=amp_dtype):
            _, loss = model(xb, yb)

        # Backward with scaler
        optimizer.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        if GRAD_CLIP > 0:
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
        scaler.step(optimizer)
        scaler.update()

        # Log every 100 steps
        if step % 100 == 0:
            elapsed = time.time() - t_start
            print(f"step {step:5d} | loss {loss.item():.4f} | lr {lr:.2e} | {elapsed:.0f}s")

        # Evaluate every 500 steps
        if step > 0 and step % 500 == 0:
            losses = estimate_loss(model, train_data, val_data, BATCH_SIZE, BLOCK_SIZE, device)
            print(f"  eval | train_loss {losses['train']:.4f} | val_loss {losses['val']:.4f}")
            if losses["val"] < best_val_loss:
                best_val_loss = losses["val"]

        step += 1

    # Final evaluation
    elapsed = time.time() - t_start
    losses = estimate_loss(model, train_data, val_data, BATCH_SIZE, BLOCK_SIZE, device)
    if losses["val"] < best_val_loss:
        best_val_loss = losses["val"]

    # Peak VRAM
    peak_vram_mb = torch.cuda.max_memory_allocated(device) / 1024**2 if device == "cuda" else 0

    # Generate sample
    meta_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "meta.pkl")
    sample = generate_sample(model, meta_path, device, max_tokens=200)

    # Print results (these lines are parsed by the loop)
    print("=" * 60)
    print(f"val_loss:{best_val_loss:.6f}")
    print(f"train_loss:{losses['train']:.6f}")
    print(f"peak_vram_mb:{peak_vram_mb:.0f}")
    print(f"total_steps:{step}")
    print(f"elapsed_seconds:{elapsed:.0f}")
    print(f"params_millions:{n_params/1e6:.1f}")
    print("=" * 60)
    print(f"SAMPLE:\n{sample}")


def benchmark():
    """Quick benchmark mode — just output metrics."""
    train()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", action="store_true", help="Output metrics for the loop")
    args = parser.parse_args()
    train()
