# /experiment — Create a New Karpathy Loop Experiment

Create a ready-to-run optimization experiment in `experiments/`.

## Usage

```
/experiment <name> <description>
```

Examples:
```
/experiment protein-folding "Optimize protein sequences for stability using ESMFold"
/experiment trading-strategy "Evolve trading strategies on crypto backtest data"
/experiment hash-function "Create a faster hash function than xxhash"
/experiment sorting-algo "Discover sorting algorithms for near-sorted data"
```

## What It Does

1. **Asks** for the domain details:
   - What file does the agent optimize? (the editable file)
   - What metric defines success? (the frozen metric)
   - What baselines exist? (what to compare against)
   - What dependencies are needed? (pip packages)

2. **Creates** the full experiment structure:
   ```
   experiments/<name>/
   ├── prepare.py        # FROZEN evaluation + benchmarking
   ├── <editable>.py     # The file Claude optimizes
   ├── program.md        # Instructions for the optimization loop
   ├── results.tsv       # Header row ready for data
   ├── METRICS.md        # Frozen success criteria
   └── data/             # Test data directory (if needed)
   ```

3. **Validates** the experiment runs:
   - Runs `python prepare.py baseline` to verify baselines work
   - Runs `python prepare.py evaluate` to verify the editable file works
   - Confirms lossless/correctness checks pass

4. **Commits** the experiment to git

5. **Outputs** the exact command to run the experiment

## Architecture Rules

Every experiment follows the Karpathy pattern:

- **ONE editable file** — the only file Claude modifies during the loop
- **ONE frozen evaluator** (prepare.py) — Claude NEVER modifies this
- **ONE frozen metrics file** (METRICS.md) — success criteria locked at creation
- **program.md** — instructions for the loop (exit conditions, strategy suggestions)
- **results.tsv** — append-only experiment log

## Template Structure

### prepare.py must have:
- `evaluate` command — runs the editable file and measures metrics
- `baseline` command — shows reference scores to beat
- `setup` command (optional) — downloads/creates test data
- A `composite_score` that combines all metrics into one number
- Verification that results are correct (lossless, valid, etc.)

### The editable file must have:
- A clear baseline implementation (even if bad)
- Comments explaining what Claude can modify
- Strategy suggestions for optimization

### program.md must have:
- The optimization loop steps (read → hypothesize → edit → run → decide)
- Exit conditions (max experiments, plateau detection, target score)
- Phase-based strategy (explore → combine → optimize)
- Results format for results.tsv

### METRICS.md must have:
- Success criteria table with targets
- The composite score formula
- What each sub-metric measures

## Existing Experiments as Reference

| Experiment | Editable File | Metric | Domain |
|-----------|--------------|--------|--------|
| nanoGPT | train.py | val_loss | ML training |
| drug-discovery | molecule.py | QED + novelty | Chemistry |
| materials-discovery | material.py | composite (band gap + stability) | Materials science |
| artificial-life | rules.py | composite (survival + complexity) | Cellular automata |
| compression | compressor.py | ratio + speed + lossless | Data compression |

## After Creation

The skill outputs the exact command to start the experiment:

```
Experiment created! To run it:

cd autolab
claude --dangerously-skip-permissions

> Read experiments/<name>/program.md and execute the optimization loop. <context>
```
