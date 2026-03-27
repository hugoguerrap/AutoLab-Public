# Compression Discovery — Optimization Program

## Objective

Build a lossless compression algorithm that beats gzip on the test datasets.
Modify only `compressor.py`. The evaluation in `prepare.py` is FROZEN.

## Setup (run once first)

```bash
python prepare.py setup     # Creates test datasets in data/
python prepare.py baseline   # Shows gzip/zlib scores to beat
```

## The Baselines to Beat

```
gzip (level 6):  ratio ~0.35, composite ~0.62
gzip (level 9):  ratio ~0.34, composite ~0.61 (slower)
zlib (level 6):  ratio ~0.35, composite ~0.62
```

## The Loop

For each experiment:

1. **Read** current compressor.py and results.tsv
2. **Hypothesize** — what compression technique to try or combine
3. **Edit** compressor.py with the new algorithm
4. **Run**: `python prepare.py evaluate` — get ratio, speed, lossless check
5. **Record** results in results.tsv
6. **Decide**:
   - If composite_score > best AND all_lossless = True → keep (commit)
   - If ratio improved but speed dropped → keep if composite improved
   - If NOT lossless → IMMEDIATELY revert (non-negotiable)
   - Otherwise → revert
7. **Repeat**

## CRITICAL RULE

**LOSSLESS IS NON-NEGOTIABLE.** If decompress(compress(data)) != data for ANY dataset,
the experiment is an automatic failure. Revert immediately. Do not try to "fix" a
lossy compressor — revert and try a different approach.

## Strategy

### Phase 1: Basic algorithms (experiments 1-3)
- Evaluate RLE baseline (it will be terrible for text)
- Implement LZ77 (sliding window with back-references)
- Try Huffman coding (frequency-based variable-length codes)

### Phase 2: Combinations (experiments 4-7)
- LZ77 + Huffman (this is essentially what gzip does internally)
- BWT + MTF + simple entropy coding
- Dictionary coding optimized for the data types
- Adaptive: detect data type and pick best strategy

### Phase 3: Beat gzip (experiments 8-10)
- Larger sliding windows
- Better dictionary building
- Context modeling
- Fine-tune parameters against the test datasets

## Results Format (results.tsv)

```
experiment	avg_ratio	composite	speed_mbps	lossless	vs_gzip_pct	description
```

## Exit Conditions

Stop when ANY of these is true:
- 10 experiments completed
- composite_score > gzip's composite (you beat gzip!)
- 5 consecutive experiments with no improvement
- Achieved ratio < 0.30 on all datasets
