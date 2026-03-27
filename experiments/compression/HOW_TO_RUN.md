# How to Run: Compression Optimization

## Prerequisites

1. **Python 3.10+**
2. **No additional packages** -- uses Python stdlib only
3. **Claude Code** installed and authenticated

## Run the Experiment

Launch Claude Code with permissions bypass for unattended execution:

```bash
claude --dangerously-skip-permissions
```

Then paste this prompt:

```
Read experiments/compression/program.md and execute the optimization loop. Start with the baseline compressor and try to beat gzip's compression ratio. Implement increasingly sophisticated algorithms — LZ77, Huffman coding, deflate-style. Measure ratio, speed, and correctness. Do not stop until you hit the exit conditions.
```

## Expected Runtime

~45 minutes for 10 experiments.

## Expected Output

| File | Description |
|------|-------------|
| `results.tsv` | Tab-separated log: iteration, algorithm description, compression ratio, speed (MB/s), correctness (pass/fail), accept/reject |
| `data/` | Directory containing test files used for benchmarking |

## Verify Results

```bash
# Check the results log
cat experiments/compression/results.tsv

# Find the best compression ratio achieved
sort -t$'\t' -k3 -n experiments/compression/results.tsv | head -5

# Verify correctness -- all experiments should show "pass"
grep -c "fail" experiments/compression/results.tsv
```

## Notes

- The baseline is a naive compressor. The goal is to approach or beat gzip's ratio (~3:1 on text).
- Each experiment implements or improves a compression algorithm, then measures ratio and throughput.
- Correctness is mandatory -- compress then decompress must produce identical output.
- No external libraries are used; everything is pure Python stdlib.
