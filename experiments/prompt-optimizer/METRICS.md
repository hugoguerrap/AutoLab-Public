# Prompt Optimizer — Frozen Metrics

**Do not modify after creation.**

## Primary Metric
- **pass@1** — percentage of HumanEval problems solved correctly on first attempt
- Range: 0.0 to 1.0
- Target: > 0.85 (beat default Haiku by 15%+)

## How It's Calculated
Defined in `prepare.py:evaluate_prompt()`:
1. Load 164 HumanEval problems
2. For each problem: send function signature + system prompt to Haiku
3. Extract generated code, combine with function signature
4. Execute with test cases from HumanEval
5. pass@1 = problems_passed / total_problems

## Secondary Metrics
- **avg_tokens** — average tokens per problem (efficiency)
- **estimated_cost** — USD cost per full evaluation
- **error_breakdown** — syntax errors, runtime errors, timeouts, wrong answers

## Baselines
| Configuration | Expected pass@1 | Notes |
|--------------|----------------|-------|
| No system prompt | ~55-65% | Raw Haiku capability |
| Basic prompt (current) | ~65-75% | Simple instructions |
| Optimized prompt (target) | >85% | After 30 iterations |

## What Counts as a Win
Any prompt that achieves pass@1 > baseline AND uses fewer or equal tokens.
The dream: pass@1 > 85% with a prompt under 200 tokens.

## Cost Budget
- Per evaluation: ~$0.10-0.20 (164 problems × ~700 tokens × Haiku pricing)
- Total experiment: ~$3-6 (30 evaluations)
