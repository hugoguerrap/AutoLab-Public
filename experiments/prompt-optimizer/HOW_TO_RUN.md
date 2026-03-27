# How to Run: Prompt Optimizer

## Prerequisites

1. **Python 3.10+**
2. **Anthropic API key** set as environment variable:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   ```
3. **Anthropic Python SDK:**
   ```bash
   pip install anthropic
   ```
4. **Claude Code** installed and authenticated

## Run the Experiment

Launch Claude Code with permissions bypass for unattended execution:

```bash
claude --dangerously-skip-permissions
```

### Standard run (10 experiments)

Paste this prompt:

```
Read experiments/prompt-optimizer/program.md and execute the optimization loop. Maximize Haiku pass@1 on HumanEval. Use quick test (10 problems, ~$0.01) for rapid iteration, full eval (164 problems, ~$0.15) for definitive measurements. Try: edge case instructions, few-shot examples, output format constraints, chain-of-thought vs direct. 10 experiments. Log everything to results.tsv.
```

### Extended run (20 experiments, aggressive exploration)

```
Read experiments/prompt-optimizer/program.md and execute the optimization loop. Override exit conditions: run 20 experiments. Start from the current best prompt, then try radically different approaches: multi-step reasoning, code review self-check, type-hint emphasis, algorithmic thinking frameworks, negative examples ("don't do X"). Use quick test for screening, full eval for promising candidates. Log everything.
```

## Expected Runtime

- ~30 minutes for 10 experiments (mostly API call time)
- ~60 minutes for 20 experiments
- Cost: ~$0.15 per full eval, ~$0.01 per quick test

## Expected Output

| File | Description |
|------|-------------|
| `results.tsv` | Tab-separated log: experiment, pass_rate, avg_tokens, prompt_summary, accept/reject |
| `prompts.py` | Updated with best system prompt, few-shots, and strategy notes |

## Verify Results

```bash
# Check the results log
cat experiments/prompt-optimizer/results.tsv

# Run a quick test with current best prompt
python experiments/prompt-optimizer/prepare.py quick

# Run full evaluation
python experiments/prompt-optimizer/prepare.py evaluate --verbose
```

## Notes

- pass@1 is the metric: percentage of 164 HumanEval problems solved correctly on first attempt.
- Current baseline: 80.5% (132/164) with a one-sentence system prompt.
- Quick test (10 problems) is good for screening; full eval (164 problems) for definitive comparison.
- The goal: make Haiku ($0.25/M) perform at near-Opus ($15/M) level — a 60x cost reduction.
