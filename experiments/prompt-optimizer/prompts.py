"""
Prompt Optimizer — System Prompt & Configuration
==================================================
THIS IS THE FILE CLAUDE OPTIMIZES.

Contains:
- SYSTEM_PROMPT: The system prompt sent to Haiku for code generation
- FEW_SHOTS: Few-shot examples (user/assistant pairs)
- Strategy notes and optimization history

The goal: maximize pass@1 on HumanEval (164 coding problems)
by evolving the system prompt and few-shot examples.

prepare.py is the frozen evaluator — it runs Haiku with this prompt
and measures how many problems it solves.
"""

# ============================================================
# SYSTEM PROMPT — The core of what Claude optimizes
# ============================================================

SYSTEM_PROMPT = """You are a senior Python engineer who writes production-quality, bug-free code. Think about edge cases first, then return ONLY the function body code, nothing else. Match the docstring examples exactly."""

# ============================================================
# FEW-SHOT EXAMPLES — Claude can add, remove, reorder these
# ============================================================

FEW_SHOTS = []

# ============================================================
# OPTIMIZATION HISTORY
# ============================================================

BEST_PASS_RATE = 0.8049  # 132/164 — "production-quality bug-free + edge cases + docstring"
BASELINE_PASS_RATE = 0.6098  # Same — this IS the baseline

# ============================================================
# STRATEGY NOTES
# ============================================================

STRATEGY_NOTES = """
=== PROMPT OPTIMIZER — STARTING STRATEGY ===

GOAL: Maximize Haiku's pass@1 on HumanEval by optimizing the system prompt.

MODEL: claude-haiku-4-5-20251001 (~$0.10-0.20 per full eval of 164 problems)

WHAT TO OPTIMIZE:
1. System prompt wording (instructions, constraints, style)
2. Few-shot examples (which problems, how many, what format)
3. Output format instructions (code only vs explanation vs CoT)
4. Edge case handling instructions
5. Prompt length (shorter might be better — less distraction)

PHASES:
- Phase 1 (iter 1-3): Establish baseline. Run with current prompt, then minimal prompt, then no prompt.
- Phase 2 (iter 4-10): Test major strategies: CoT, few-shots, format changes.
- Phase 3 (iter 11-20): Combine best strategies, fine-tune.
- Phase 4 (iter 21-30): Micro-optimize: word choice, ordering, trim fat.

HYPOTHESES TO TEST:
- Chain-of-thought ("think step by step before coding") — may help complex problems
- Few-shots — 2-3 examples of correct completions might anchor the format
- Negative instructions ("do NOT use recursion for X") — may prevent common errors
- Type hints emphasis ("always use type hints") — may improve correctness
- Test-driven hint ("the code will be tested with assert statements") — may improve edge cases
- Shorter is better? — Haiku has limited context, less prompt = more room for thinking
- Format strictness — "return ONLY code, no explanation" vs "explain then code"

WHAT WE KNOW ABOUT HAIKU:
- Small, fast model — less capable on complex reasoning
- Benefits from clear, concise instructions
- Can get confused by long, complex prompts
- Good at pattern matching — few-shots might help a lot
- Tends to over-explain when not told to be concise
"""
