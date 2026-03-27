"""
Prompt Optimizer — Evaluation Engine (FROZEN)
==============================================
DO NOT MODIFY THIS FILE. This is the frozen evaluation function.
Claude modifies prompts.py; this file evaluates the results.

Runs a given system prompt against HumanEval problems using Haiku,
executes the generated code, and measures pass@1.

Requires: ANTHROPIC_API_KEY environment variable set.
"""

import sys
import json
import os
import time
import subprocess
import tempfile
import re
import signal
from datetime import datetime

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package required. Install with: pip install anthropic")
    sys.exit(1)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL = "claude-haiku-4-5-20251001"  # Cheapest model — the whole point
MAX_TOKENS = 2048
TEMPERATURE = 0.0
TIMEOUT_PER_PROBLEM = 10  # seconds to execute generated code
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "humaneval.jsonl")


# ============================================================
# LOAD HUMANEVAL
# ============================================================

def load_problems(path=DATA_FILE, limit=None):
    """Load HumanEval problems from JSONL file."""
    problems = []
    with open(path) as f:
        for line in f:
            problems.append(json.loads(line))
    if limit:
        problems = problems[:limit]
    return problems


# ============================================================
# CODE GENERATION
# ============================================================

def generate_completion(client, system_prompt, problem, few_shots=None):
    """Generate code completion using Haiku with the given system prompt."""
    messages = []

    # Add few-shot examples if provided
    if few_shots:
        for shot in few_shots:
            messages.append({"role": "user", "content": shot["user"]})
            messages.append({"role": "assistant", "content": shot["assistant"]})

    # The actual problem
    user_content = f"Complete the following Python function. Return ONLY the function body (the code that goes after the function signature). Do not include the function signature, imports, or any explanation.\n\n{problem['prompt']}"
    messages.append({"role": "user", "content": user_content})

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text, response.usage.input_tokens + response.usage.output_tokens
    except Exception as e:
        return f"# ERROR: {e}", 0


def extract_code(completion, problem):
    """Extract the function body from the completion and combine with the prompt."""
    # Try to extract code from markdown blocks
    code_match = re.search(r'```(?:python)?\s*\n(.*?)```', completion, re.DOTALL)
    if code_match:
        code_body = code_match.group(1).strip()
    else:
        code_body = completion.strip()

    # Remove the function signature if the model included it
    lines = code_body.split('\n')
    cleaned_lines = []
    skip_sig = True
    for line in lines:
        if skip_sig and (line.strip().startswith('def ') or line.strip().startswith('from ') or line.strip().startswith('import ')):
            # Check if this is the same function signature
            if problem['entry_point'] in line:
                skip_sig = False
                continue
            elif line.strip().startswith(('from ', 'import ')):
                # Keep imports that aren't in the prompt
                if line.strip() not in problem['prompt']:
                    cleaned_lines.append(line)
                continue
        else:
            skip_sig = False
        if not skip_sig:
            cleaned_lines.append(line)

    if cleaned_lines:
        code_body = '\n'.join(cleaned_lines)

    # Normalize indentation to exactly 4 spaces for function body
    # Haiku often returns: first line 0-indent, rest 4-indent. We need all at 4.
    lines = code_body.split('\n')
    # Find the most common indentation among non-empty lines (excluding 0)
    indent_counts = {}
    for line in lines:
        if line.strip():
            indent = len(line) - len(line.lstrip())
            indent_counts[indent] = indent_counts.get(indent, 0) + 1

    # The base indent of the code body (most common, or min non-zero)
    non_zero_indents = {k: v for k, v in indent_counts.items() if k > 0}
    if non_zero_indents:
        base_indent = min(non_zero_indents.keys())
    else:
        base_indent = 0

    # Re-indent: remove base_indent, add 4 spaces
    normalized = []
    for line in lines:
        if line.strip():
            current_indent = len(line) - len(line.lstrip())
            relative_indent = max(0, current_indent - base_indent)
            normalized.append('    ' + ' ' * relative_indent + line.lstrip())
        else:
            normalized.append('')
    code_body = '\n'.join(normalized)

    # Combine with the original prompt (which has the function signature)
    full_code = problem['prompt'] + code_body

    return full_code


# ============================================================
# CODE EXECUTION
# ============================================================

def execute_and_test(code, problem, timeout=TIMEOUT_PER_PROBLEM):
    """Execute the generated code and run the test cases."""
    # Build the test program
    test_code = code + "\n\n" + problem['test'] + f"\n\ncheck({problem['entry_point']})"

    # Write to temp file and execute
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_code)
        temp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        passed = result.returncode == 0
        error = result.stderr[:500] if result.stderr else ""
        return passed, error
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, str(e)[:500]
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass


# ============================================================
# EVALUATION
# ============================================================

def evaluate_prompt(system_prompt, few_shots=None, limit=None, verbose=False):
    """
    Evaluate a system prompt against HumanEval.
    Returns: dict with pass_rate, total_tokens, cost, per-problem results.
    """
    client = anthropic.Anthropic()
    problems = load_problems(limit=limit)

    results = []
    passed = 0
    total_tokens = 0
    errors = {"syntax": 0, "runtime": 0, "timeout": 0, "wrong": 0}

    for i, problem in enumerate(problems):
        task_id = problem['task_id']

        # Generate
        completion, tokens = generate_completion(client, system_prompt, problem, few_shots)
        total_tokens += tokens

        # Extract and test
        full_code = extract_code(completion, problem)
        success, error = execute_and_test(full_code, problem)

        if success:
            passed += 1
            status = "PASS"
        else:
            status = "FAIL"
            if "SyntaxError" in error:
                errors["syntax"] += 1
            elif "TIMEOUT" in error:
                errors["timeout"] += 1
            elif error:
                errors["runtime"] += 1
            else:
                errors["wrong"] += 1

        results.append({
            "task_id": task_id,
            "entry_point": problem['entry_point'],
            "passed": success,
            "error": error[:200] if error else "",
            "tokens": tokens,
        })

        if verbose:
            marker = "PASS" if success else "FAIL"
            err_msg = f" -- {error[:60]}" if error and not success else ""
            print(f"  [{i+1:3d}/{len(problems)}] {marker:4s} {task_id:20s} ({tokens} tokens){err_msg}")

        # Rate limit: ~50 req/min for Haiku
        if (i + 1) % 50 == 0:
            time.sleep(2)

    pass_rate = passed / len(problems) if problems else 0
    # Haiku pricing: $0.80/M input + $4/M output (estimate ~70% input, 30% output)
    estimated_cost = total_tokens * 0.0000018  # rough average

    return {
        "pass_rate": round(pass_rate, 4),
        "passed": passed,
        "total": len(problems),
        "total_tokens": total_tokens,
        "avg_tokens": round(total_tokens / len(problems)) if problems else 0,
        "estimated_cost_usd": round(estimated_cost, 4),
        "errors": errors,
        "results": results,
    }


# ============================================================
# CLI INTERFACE
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python prepare.py evaluate [--limit N] [--verbose]    Run full evaluation")
        print("  python prepare.py quick                                Quick test (10 problems)")
        print("  python prepare.py baseline                             Show baseline with no system prompt")
        print("  python prepare.py sample N                             Show N sample problems")
        print("  python prepare.py cost                                 Estimate cost for full run")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "evaluate":
        # Import the current prompt from prompts.py
        sys.path.insert(0, os.path.dirname(__file__))
        from prompts import SYSTEM_PROMPT, FEW_SHOTS

        limit = None
        verbose = False
        for i, arg in enumerate(sys.argv[2:]):
            if arg == "--limit" and i + 3 < len(sys.argv):
                limit = int(sys.argv[i + 3])
            if arg == "--verbose":
                verbose = True

        print(f"=== PROMPT OPTIMIZER EVALUATION ===")
        print(f"Model: {MODEL}")
        print(f"Problems: {limit or 164}")
        print(f"System prompt: {len(SYSTEM_PROMPT)} chars")
        print(f"Few-shots: {len(FEW_SHOTS)}")
        print()

        result = evaluate_prompt(SYSTEM_PROMPT, FEW_SHOTS, limit=limit, verbose=verbose)

        print(f"\n=== RESULTS ===")
        print(f"  pass@1:      {result['pass_rate']:.1%} ({result['passed']}/{result['total']})")
        print(f"  tokens:      {result['total_tokens']:,} total, {result['avg_tokens']} avg/problem")
        print(f"  cost:        ${result['estimated_cost_usd']:.4f}")
        print(f"  errors:      syntax={result['errors']['syntax']}, runtime={result['errors']['runtime']}, timeout={result['errors']['timeout']}, wrong={result['errors']['wrong']}")

        # Save detailed results
        outfile = os.path.join(os.path.dirname(__file__), "last_eval.json")
        with open(outfile, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n  Details saved to: {outfile}")

    elif cmd == "quick":
        sys.path.insert(0, os.path.dirname(__file__))
        from prompts import SYSTEM_PROMPT, FEW_SHOTS

        print("=== QUICK TEST (10 problems) ===")
        result = evaluate_prompt(SYSTEM_PROMPT, FEW_SHOTS, limit=10, verbose=True)
        print(f"\nQuick pass@1: {result['pass_rate']:.1%} ({result['passed']}/10)")
        print(f"Cost: ${result['estimated_cost_usd']:.4f}")

    elif cmd == "baseline":
        print("=== BASELINE (empty system prompt, 10 problems) ===")
        result = evaluate_prompt("", few_shots=None, limit=10, verbose=True)
        print(f"\nBaseline pass@1: {result['pass_rate']:.1%} ({result['passed']}/10)")

    elif cmd == "sample" and len(sys.argv) >= 3:
        n = int(sys.argv[2])
        problems = load_problems(limit=n)
        for p in problems:
            print(f"\n{'='*60}")
            print(f"Task: {p['task_id']} — {p['entry_point']}")
            print(f"Prompt:\n{p['prompt'][:300]}...")

    elif cmd == "cost":
        print(f"=== COST ESTIMATE ===")
        print(f"Model: {MODEL}")
        print(f"Problems: 164")
        print(f"Est. tokens/problem: ~500 (prompt) + ~200 (completion) = ~700")
        print(f"Total tokens: ~115,000")
        print(f"Cost per eval: ~$0.10-0.20")
        print(f"30 iterations: ~$3-6 total")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
