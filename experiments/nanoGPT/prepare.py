"""
Data preparation and evaluation for nanoGPT experiment.
FROZEN — the agent must NEVER modify this file.

Downloads TinyShakespeare, tokenizes it, and provides:
- get_batch(): returns training/validation batches
- estimate_loss(): evaluates model on validation set
"""
import os
import urllib.request
import pickle
import numpy as np
import torch

# --- Config (frozen) ---
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DATA_URL = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
EVAL_ITERS = 50  # batches to average for loss estimation
VAL_SPLIT = 0.1  # 10% validation


def download_data():
    """Download TinyShakespeare if not present."""
    os.makedirs(DATA_DIR, exist_ok=True)
    raw_path = os.path.join(DATA_DIR, "input.txt")
    if not os.path.exists(raw_path):
        print("Downloading TinyShakespeare...")
        urllib.request.urlretrieve(DATA_URL, raw_path)
        print(f"Downloaded to {raw_path}")
    return raw_path


def prepare_data():
    """Tokenize data and save train/val splits. Returns vocab_size."""
    raw_path = download_data()

    with open(raw_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Character-level tokenizer
    chars = sorted(list(set(text)))
    vocab_size = len(chars)
    stoi = {ch: i for i, ch in enumerate(chars)}
    itos = {i: ch for i, ch in enumerate(chars)}

    # Save tokenizer
    meta = {"vocab_size": vocab_size, "itos": itos, "stoi": stoi}
    with open(os.path.join(DATA_DIR, "meta.pkl"), "wb") as f:
        pickle.dump(meta, f)

    # Encode full text
    data = np.array([stoi[ch] for ch in text], dtype=np.uint16)

    # Split
    n = int(len(data) * (1 - VAL_SPLIT))
    train_data = data[:n]
    val_data = data[n:]

    # Save as binary
    train_data.tofile(os.path.join(DATA_DIR, "train.bin"))
    val_data.tofile(os.path.join(DATA_DIR, "val.bin"))

    print(f"Vocab size: {vocab_size}")
    print(f"Train tokens: {len(train_data):,}")
    print(f"Val tokens: {len(val_data):,}")

    return vocab_size


def load_data():
    """Load prepared data. Returns (train_data, val_data, vocab_size)."""
    meta_path = os.path.join(DATA_DIR, "meta.pkl")

    if not os.path.exists(meta_path):
        prepare_data()

    with open(meta_path, "rb") as f:
        meta = pickle.load(f)

    train_data = np.memmap(os.path.join(DATA_DIR, "train.bin"), dtype=np.uint16, mode="r")
    val_data = np.memmap(os.path.join(DATA_DIR, "val.bin"), dtype=np.uint16, mode="r")

    return train_data, val_data, meta["vocab_size"]


def get_batch(split, train_data, val_data, batch_size, block_size, device):
    """Get a random batch of data."""
    data = train_data if split == "train" else val_data
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([torch.from_numpy(data[i:i+block_size].astype(np.int64)) for i in ix])
    y = torch.stack([torch.from_numpy(data[i+1:i+1+block_size].astype(np.int64)) for i in ix])
    x, y = x.to(device), y.to(device)
    return x, y


@torch.no_grad()
def estimate_loss(model, train_data, val_data, batch_size, block_size, device):
    """Estimate train and val loss. This is the FROZEN metric."""
    out = {}
    model.eval()
    for split in ["train", "val"]:
        losses = torch.zeros(EVAL_ITERS)
        for k in range(EVAL_ITERS):
            X, Y = get_batch(split, train_data, val_data, batch_size, block_size, device)
            _, loss = model(X, Y)
            losses[k] = loss.item()
        out[split] = losses.mean().item()
    model.train()
    return out


@torch.no_grad()
def generate_sample(model, meta_path, device, max_tokens=200):
    """Generate a text sample from the model."""
    with open(meta_path, "rb") as f:
        meta = pickle.load(f)
    itos = meta["itos"]

    context = torch.zeros((1, 1), dtype=torch.long, device=device)
    model.eval()
    generated = []
    for _ in range(max_tokens):
        logits, _ = model(context)
        logits = logits[:, -1, :]
        probs = torch.softmax(logits, dim=-1)
        next_id = torch.multinomial(probs, num_samples=1)
        generated.append(itos[next_id.item()])
        context = torch.cat([context, next_id], dim=1)
        # Keep only last block_size tokens
        if context.size(1) > 256:
            context = context[:, -256:]
    model.train()
    return "".join(generated)


if __name__ == "__main__":
    prepare_data()
    print("Data preparation complete.")
