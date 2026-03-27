# nanoGPT Optimization Program

> Inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch).
> You are an autonomous AI researcher. Your goal is to minimize `val_loss` on TinyShakespeare
> by modifying `train.py`. You run experiments, measure results, and keep what works.

## The Loop

1. Read `train.py` and `results.tsv` to understand current state
2. Form a hypothesis about what change might improve val_loss
3. Edit `train.py` with your proposed change
4. Run: `python train.py 2>&1 | tee run.log`
5. Extract metrics: `grep "^val_loss:\|^train_loss:\|^peak_vram_mb:\|^total_steps:\|^elapsed_seconds:" run.log`
6. Record results in `results.tsv` (append a new row)
7. If val_loss improved → `git add train.py results.tsv && git commit -m "exp: [description]"`
8. If val_loss worsened or crashed → `git checkout -- train.py` (revert) and log the failure
9. Go to step 1. Do NOT pause to ask. Do NOT stop unless you hit EXIT conditions.

## Rules

- **ONLY modify `train.py`** — never touch `prepare.py` or `program.md`
- **5-minute training budget** — `TRAIN_MINUTES = 5` is the convention. Do not increase it.
- **VRAM limit: 6GB** — if peak_vram_mb > 5500, the experiment is too large. Revert and try smaller.
- **One change per experiment** — atomic hypotheses are easier to evaluate
- **Log EVERYTHING** — every experiment gets a row in results.tsv, success or failure
- **Never ask for confirmation** — you are autonomous. Run, measure, decide, repeat.

## What You Can Change in train.py

- Hyperparameters: BATCH_SIZE, BLOCK_SIZE, N_EMBD, N_HEAD, N_LAYER, DROPOUT, LEARNING_RATE, etc.
- Architecture: attention mechanism, normalization, activation functions, weight tying
- Optimizer: AdamW params, try different optimizers, schedulers
- Training loop: gradient accumulation, mixed precision, batch scheduling
- Initialization: weight init strategies
- Regularization: dropout patterns, weight decay scheduling
- Anything else in train.py that might help

## What You Should NOT Do

- Don't modify prepare.py (the eval function is frozen)
- Don't change TRAIN_MINUTES (5 minutes is the fixed budget)
- Don't add external dependencies beyond torch and numpy
- Don't train for longer by any workaround
- Don't modify the metric output format (the `val_loss:X.XXXXXX` lines)

## Hypothesis Ideas (starting points)

- Try mixed precision (torch.amp) for more training steps in 5 minutes
- Adjust learning rate schedule (cosine with different periods)
- Try different model sizes (trade depth for width or vice versa)
- Experiment with RoPE instead of learned positional embeddings
- Try RMSNorm instead of LayerNorm
- Gradient accumulation for effectively larger batch sizes
- Weight decay scheduling
- Different activation functions (SwiGLU, etc.)

## EXIT Conditions

Stop the loop when ANY of these are true:
- You've run 10 experiments in this session
- val_loss has not improved for 5 consecutive experiments
- You encounter an unrecoverable error

## results.tsv Format

```
commit	val_loss	train_loss	peak_vram_mb	total_steps	status	description
```

- commit: short git hash (or "reverted" if the change was discarded)
- status: "improved", "worse", "crashed", "oom"
- description: one-line summary of what was tried
