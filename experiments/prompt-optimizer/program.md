# Prompt Optimizer — Maximize Haiku's Code Generation Performance

## The Karpathy Loop for Prompt Engineering

You are optimizing a system prompt to maximize **claude-haiku-4-5-20251001**'s performance on HumanEval (164 Python coding problems). The metric is **pass@1** — the percentage of problems where the generated code passes all test cases on the first attempt.

This follows the Karpathy Loop: **hypothesis → test → measure → accept/reject → repeat.**

You can ONLY modify `prompts.py`. The evaluator `prepare.py` is frozen.

## Why This Matters

If you can make Haiku ($0.25/M tokens) perform at Opus-level ($15/M tokens) on code generation just by optimizing the prompt, that's a **60x cost reduction** for any developer using LLMs for coding. That's a real, publishable, immediately useful result.

## The Loop

Each iteration:

1. **Read** `prompts.py` — see current SYSTEM_PROMPT, FEW_SHOTS, BEST_PASS_RATE, and STRATEGY_NOTES
2. **Analyze** — what was the last change? Did it help? Why or why not?
3. **Hypothesize** — what single change might improve pass@1?
   - Modify the system prompt wording
   - Add/remove/reorder few-shot examples
   - Change output format instructions
   - Add/remove constraints
   - Try chain-of-thought vs direct completion
4. **Edit** `prompts.py` — make ONE change (atomic, testable)
5. **Evaluate** — run the prompt against HumanEval:
   - Quick test (10 problems): `python prepare.py quick` (~$0.01, 30 seconds)
   - Full test (164 problems): `python prepare.py evaluate --verbose` (~$0.15, 5-10 minutes)
   - Use `quick` for rapid iteration, `evaluate` for definitive measurements
6. **Decide:**
   - pass@1 improved → **keep**, update BEST_PASS_RATE in prompts.py
   - pass@1 same or worse → **revert** prompts.py, log what was tried
7. **Update STRATEGY_NOTES** with what you learned
8. **Log to results.tsv** — every iteration, even failures
9. **Repeat** from step 1

## Evaluation Commands

```bash
# Quick test — 10 problems, ~30 seconds, ~$0.01
python prepare.py quick

# Full evaluation — 164 problems, ~5-10 minutes, ~$0.15
python prepare.py evaluate --verbose

# Full evaluation with limit
python prepare.py evaluate --limit 50 --verbose

# Baseline — no system prompt
python prepare.py baseline

# Cost estimate
python prepare.py cost

# See sample problems
python prepare.py sample 5
```

## Rules

- **NEVER** modify `prepare.py` — it's the frozen truth
- **ONLY** modify `prompts.py`
- Make **ONE change per iteration** — so you know what caused the improvement
- Use `quick` (10 problems) for rapid testing, `evaluate` for final measurements
- **Always** update BEST_PASS_RATE when you beat the previous best
- **Always** log to results.tsv, even failed iterations
- After 3 full evals without improvement → try a radically different approach

## Strategy Guide

### What tends to work for code generation prompts:
- **Concise instructions** — Haiku gets confused by long prompts
- **Format enforcement** — "return ONLY the function body, no explanation"
- **Edge case reminders** — "handle empty inputs, None, negative numbers"
- **Type awareness** — "pay attention to type hints in the signature"
- **Test awareness** — "the code will be tested with assert statements"
- **Few-shots** — 1-3 examples of correct completions help anchor format

### What tends to hurt:
- **Over-explaining** — too many rules confuse small models
- **Chain-of-thought for simple problems** — wastes tokens, sometimes introduces errors
- **Conflicting instructions** — "be thorough" + "be concise"
- **Too many few-shots** — fills context window, less room for the actual problem

### Things to try:
1. No system prompt at all (baseline)
2. One-line prompt ("Complete the Python function correctly.")
3. Detailed prompt with rules
4. Few-shot examples (easy, medium, hard)
5. CoT instruction ("Think through the solution step by step, then write the code")
6. Negative examples ("Do NOT do X, Y, Z")
7. Role-playing ("You are a senior Python engineer at Google")
8. Test-first hint ("Before writing code, think about what test cases this function needs to handle")
9. Pattern-based ("Look for mathematical patterns, list patterns, string patterns")
10. Combinations of the above

## results.tsv Format

```
iteration	pass_rate	passed	total	avg_tokens	cost_usd	prompt_length	few_shots	change_description
```

## Exit Conditions

Stop when ANY of these is true:
- **30 iterations completed**
- **pass@1 > 0.90** (exceptional — likely near ceiling for Haiku)
- **5 consecutive full evaluations without improvement** (plateau)

When stopping:
1. Update prompts.py with the CHAMPION prompt and full strategy notes
2. Run one final `python prepare.py evaluate --verbose` to confirm
3. Compare champion vs baseline vs default
4. Document: what worked, what didn't, what surprised you
