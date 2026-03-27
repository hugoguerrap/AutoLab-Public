"""
Compression Discovery — Evaluation & Benchmarking
====================================================
FROZEN FILE — Claude must NOT modify this.

Evaluates custom compression algorithms against standard baselines (gzip, zlib).
Tests on multiple data types to ensure the compressor generalizes.

Usage:
    python prepare.py setup              # Download/create test datasets
    python prepare.py evaluate           # Evaluate current compressor
    python prepare.py baseline           # Show gzip/zlib baselines
"""

import sys
import os
import time
import zlib
import gzip
import hashlib
import json
import math
import random
import string

# ============================================================
# TEST DATASETS — FROZEN
# ============================================================

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def setup_datasets():
    """Create standardized test datasets for compression benchmarking."""
    os.makedirs(DATA_DIR, exist_ok=True)

    datasets = {}

    # 1. English text (Shakespeare-like)
    print("Creating text dataset...")
    random.seed(42)
    words = [
        "the", "of", "and", "to", "in", "a", "is", "that", "it", "was",
        "for", "on", "are", "with", "as", "his", "they", "be", "at", "one",
        "have", "this", "from", "by", "not", "but", "what", "all", "were", "when",
        "we", "there", "can", "an", "your", "which", "their", "said", "each", "she",
        "do", "how", "will", "up", "other", "about", "out", "many", "then", "them",
        "would", "like", "so", "these", "her", "long", "make", "thing", "see", "him",
        "two", "has", "look", "more", "day", "could", "go", "come", "did", "my",
        "no", "most", "who", "over", "know", "than", "call", "first", "people", "may",
        "down", "been", "now", "find", "any", "new", "part", "take", "get", "place",
        "where", "after", "back", "only", "little", "round", "man", "year", "came", "show",
        "every", "good", "give", "our", "under", "name", "very", "through", "just", "great",
        "think", "say", "help", "low", "line", "before", "turn", "cause", "same", "mean",
        "differ", "move", "right", "here", "old", "big", "high", "such", "follow", "act",
        "why", "ask", "change", "went", "light", "kind", "off", "need", "house", "picture",
        "try", "again", "animal", "point", "mother", "world", "near", "build", "self", "earth",
    ]

    sentences = []
    for _ in range(2000):
        length = random.randint(5, 20)
        sentence = " ".join(random.choice(words) for _ in range(length))
        sentence = sentence.capitalize() + random.choice([".", "!", "?"])
        sentences.append(sentence)
    text_data = "\n".join(sentences)
    with open(os.path.join(DATA_DIR, "text.txt"), "w") as f:
        f.write(text_data)
    datasets["text"] = len(text_data.encode())

    # 2. JSON data (structured, repetitive keys)
    print("Creating JSON dataset...")
    random.seed(42)
    records = []
    cities = ["New York", "London", "Tokyo", "Paris", "Berlin", "Sydney", "Toronto", "Mumbai", "Seoul", "Dubai"]
    departments = ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations", "Research", "Support"]
    for i in range(500):
        records.append({
            "id": i,
            "name": f"User_{i:04d}",
            "email": f"user{i}@company.com",
            "age": random.randint(22, 65),
            "salary": round(random.uniform(30000, 150000), 2),
            "city": random.choice(cities),
            "department": random.choice(departments),
            "active": random.choice([True, False]),
            "score": round(random.gauss(75, 15), 1),
            "joined": f"20{random.randint(10,24)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        })
    json_data = json.dumps(records, indent=2)
    with open(os.path.join(DATA_DIR, "data.json"), "w") as f:
        f.write(json_data)
    datasets["json"] = len(json_data.encode())

    # 3. CSV data (tabular, lots of repeated patterns)
    print("Creating CSV dataset...")
    random.seed(42)
    csv_lines = ["timestamp,sensor_id,temperature,humidity,pressure,status"]
    statuses = ["OK", "WARN", "ERROR", "OK", "OK", "OK"]  # Weighted toward OK
    for i in range(5000):
        ts = f"2024-01-{(i // 200) + 1:02d}T{(i % 24):02d}:{random.randint(0,59):02d}:00"
        sensor = f"S{random.randint(1,20):03d}"
        temp = round(random.gauss(22, 3), 1)
        humidity = round(random.gauss(45, 10), 1)
        pressure = round(random.gauss(1013, 5), 1)
        status = random.choice(statuses)
        csv_lines.append(f"{ts},{sensor},{temp},{humidity},{pressure},{status}")
    csv_data = "\n".join(csv_lines)
    with open(os.path.join(DATA_DIR, "sensors.csv"), "w") as f:
        f.write(csv_data)
    datasets["csv"] = len(csv_data.encode())

    # 4. Binary-like data (bytes as hex string — simulates binary patterns)
    print("Creating binary dataset...")
    random.seed(42)
    # Structured binary: repeating patterns with noise
    patterns = [bytes([i % 256]) * random.randint(3, 20) for i in range(50)]
    binary_chunks = []
    for _ in range(200):
        binary_chunks.append(random.choice(patterns))
        binary_chunks.append(bytes(random.randint(0, 255) for _ in range(random.randint(1, 10))))
    binary_data = b"".join(binary_chunks)
    with open(os.path.join(DATA_DIR, "binary.bin"), "wb") as f:
        f.write(binary_data)
    datasets["binary"] = len(binary_data)

    # 5. Source code (Python-like, highly structured)
    print("Creating source code dataset...")
    random.seed(42)
    code_lines = []
    func_names = ["process", "validate", "transform", "compute", "analyze", "filter", "merge", "split", "convert", "extract"]
    var_names = ["data", "result", "value", "items", "count", "total", "output", "config", "params", "state"]
    for i in range(200):
        fname = random.choice(func_names)
        args = ", ".join(random.sample(var_names, random.randint(1, 3)))
        code_lines.append(f"\ndef {fname}_{i}({args}):")
        code_lines.append(f'    """Process {fname} operation."""')
        for _ in range(random.randint(3, 8)):
            var = random.choice(var_names)
            op = random.choice(["len", "str", "int", "float", "list", "dict", "set", "sum", "max", "min"])
            code_lines.append(f"    {var} = {op}({random.choice(var_names)})")
        code_lines.append(f"    return {random.choice(var_names)}")
    code_data = "\n".join(code_lines)
    with open(os.path.join(DATA_DIR, "source.py"), "w") as f:
        f.write(code_data)
    datasets["source"] = len(code_data.encode())

    print(f"\nDatasets created in {DATA_DIR}/:")
    total = 0
    for name, size in datasets.items():
        print(f"  {name}: {size:,} bytes ({size/1024:.1f} KB)")
        total += size
    print(f"  TOTAL: {total:,} bytes ({total/1024:.1f} KB)")

    return datasets


def load_datasets():
    """Load all test datasets."""
    datasets = {}

    files = {
        "text": ("text.txt", "r"),
        "json": ("data.json", "r"),
        "csv": ("sensors.csv", "r"),
        "binary": ("binary.bin", "rb"),
        "source": ("source.py", "r"),
    }

    for name, (filename, mode) in files.items():
        path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(path):
            print(f"Dataset {name} not found. Run: python prepare.py setup")
            sys.exit(1)
        with open(path, mode) as f:
            data = f.read()
        if isinstance(data, str):
            data = data.encode("utf-8")
        datasets[name] = data

    return datasets


# ============================================================
# EVALUATION — FROZEN
# ============================================================

def evaluate_compressor(compress_fn, decompress_fn, datasets):
    """
    Evaluate a compression algorithm against all datasets.

    Returns dict with per-dataset and aggregate metrics.
    """
    results = {}
    total_original = 0
    total_compressed = 0
    total_compress_time = 0
    total_decompress_time = 0
    all_lossless = True

    for name, data in datasets.items():
        original_size = len(data)

        # Compress
        try:
            start = time.perf_counter()
            compressed = compress_fn(data)
            compress_time = time.perf_counter() - start
        except Exception as e:
            results[name] = {"error": f"Compression failed: {e}", "ratio": 1.0}
            continue

        compressed_size = len(compressed)

        # Decompress
        try:
            start = time.perf_counter()
            decompressed = decompress_fn(compressed)
            decompress_time = time.perf_counter() - start
        except Exception as e:
            results[name] = {"error": f"Decompression failed: {e}", "ratio": 1.0}
            all_lossless = False
            continue

        # Verify lossless
        lossless = (decompressed == data)
        if not lossless:
            all_lossless = False

        ratio = compressed_size / original_size
        speed_mbps = (original_size / 1024 / 1024) / max(compress_time, 0.0001)

        results[name] = {
            "original_bytes": original_size,
            "compressed_bytes": compressed_size,
            "ratio": round(ratio, 4),
            "compress_time_ms": round(compress_time * 1000, 2),
            "decompress_time_ms": round(decompress_time * 1000, 2),
            "speed_mbps": round(speed_mbps, 2),
            "lossless": lossless,
        }

        total_original += original_size
        total_compressed += compressed_size
        total_compress_time += compress_time
        total_decompress_time += decompress_time

    # Aggregate
    avg_ratio = total_compressed / max(total_original, 1)
    total_speed = (total_original / 1024 / 1024) / max(total_compress_time, 0.0001)

    results["_aggregate"] = {
        "total_original": total_original,
        "total_compressed": total_compressed,
        "avg_ratio": round(avg_ratio, 4),
        "total_compress_ms": round(total_compress_time * 1000, 2),
        "total_decompress_ms": round(total_decompress_time * 1000, 2),
        "speed_mbps": round(total_speed, 2),
        "all_lossless": all_lossless,
        "datasets_tested": len(datasets),
    }

    # Composite score
    # Lower ratio = better (weight 50%)
    # Higher speed = better (weight 20%)
    # Lossless required (30% — binary: pass or fail)
    ratio_score = max(0, 1.0 - avg_ratio)  # 0 = no compression, 1 = perfect
    speed_score = min(total_speed / 100, 1.0)  # Normalized to 100 MB/s
    lossless_score = 1.0 if all_lossless else 0.0

    composite = 0.50 * ratio_score + 0.20 * speed_score + 0.30 * lossless_score
    results["_aggregate"]["composite_score"] = round(composite, 4)

    return results


def show_baselines(datasets):
    """Evaluate standard compression baselines."""
    print("=" * 80)
    print("BASELINE COMPRESSORS")
    print("=" * 80)

    # gzip (level 6 — default)
    print("\n--- gzip (level 6, default) ---")
    gzip_results = evaluate_compressor(
        lambda d: gzip.compress(d, compresslevel=6),
        gzip.decompress,
        datasets
    )
    for name, r in sorted(gzip_results.items()):
        if name.startswith("_"):
            print(f"\n  AGGREGATE: ratio={r['avg_ratio']}, speed={r['speed_mbps']} MB/s, lossless={r['all_lossless']}, composite={r['composite_score']}")
        else:
            print(f"  {name}: ratio={r.get('ratio', 'N/A')}, time={r.get('compress_time_ms', 'N/A')}ms, lossless={r.get('lossless', 'N/A')}")

    # zlib (level 6)
    print("\n--- zlib (level 6, default) ---")
    zlib_results = evaluate_compressor(
        lambda d: zlib.compress(d, level=6),
        zlib.decompress,
        datasets
    )
    for name, r in sorted(zlib_results.items()):
        if name.startswith("_"):
            print(f"\n  AGGREGATE: ratio={r['avg_ratio']}, speed={r['speed_mbps']} MB/s, lossless={r['all_lossless']}, composite={r['composite_score']}")
        else:
            print(f"  {name}: ratio={r.get('ratio', 'N/A')}, time={r.get('compress_time_ms', 'N/A')}ms, lossless={r.get('lossless', 'N/A')}")

    # gzip (level 9 — max compression)
    print("\n--- gzip (level 9, max compression) ---")
    gzip9_results = evaluate_compressor(
        lambda d: gzip.compress(d, compresslevel=9),
        gzip.decompress,
        datasets
    )
    for name, r in sorted(gzip9_results.items()):
        if name.startswith("_"):
            print(f"\n  AGGREGATE: ratio={r['avg_ratio']}, speed={r['speed_mbps']} MB/s, lossless={r['all_lossless']}, composite={r['composite_score']}")
        else:
            print(f"  {name}: ratio={r.get('ratio', 'N/A')}, time={r.get('compress_time_ms', 'N/A')}ms, lossless={r.get('lossless', 'N/A')}")

    return {
        "gzip_6": gzip_results["_aggregate"],
        "zlib_6": zlib_results["_aggregate"],
        "gzip_9": gzip9_results["_aggregate"],
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python prepare.py [setup|evaluate|baseline]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "setup":
        setup_datasets()

    elif command == "baseline":
        datasets = load_datasets()
        baselines = show_baselines(datasets)
        print("\n\nBASELINE SUMMARY (targets to beat):")
        for name, agg in baselines.items():
            print(f"  {name}: ratio={agg['avg_ratio']}, composite={agg['composite_score']}")

    elif command == "evaluate":
        datasets = load_datasets()

        # Import the custom compressor
        sys.path.insert(0, ".")
        from compressor import compress, decompress

        print("=" * 80)
        print("EVALUATING CUSTOM COMPRESSOR")
        print("=" * 80)

        results = evaluate_compressor(compress, decompress, datasets)

        for name, r in sorted(results.items()):
            if name.startswith("_"):
                print(f"\n  AGGREGATE:")
                for k, v in sorted(r.items()):
                    print(f"    {k}: {v}")
            else:
                if "error" in r:
                    print(f"\n  {name}: ERROR — {r['error']}")
                else:
                    print(f"\n  {name}:")
                    print(f"    {r['original_bytes']:,} → {r['compressed_bytes']:,} bytes (ratio: {r['ratio']})")
                    print(f"    compress: {r['compress_time_ms']}ms, decompress: {r['decompress_time_ms']}ms")
                    print(f"    speed: {r['speed_mbps']} MB/s, lossless: {r['lossless']}")

        # Compare vs gzip baseline
        print("\n\n--- vs gzip (level 6) ---")
        gzip_results = evaluate_compressor(
            lambda d: gzip.compress(d, compresslevel=6),
            gzip.decompress,
            datasets
        )
        custom_ratio = results["_aggregate"]["avg_ratio"]
        gzip_ratio = gzip_results["_aggregate"]["avg_ratio"]
        diff_pct = ((gzip_ratio - custom_ratio) / gzip_ratio) * 100

        print(f"  Custom:  ratio={custom_ratio}, composite={results['_aggregate']['composite_score']}")
        print(f"  gzip(6): ratio={gzip_ratio}, composite={gzip_results['_aggregate']['composite_score']}")
        if diff_pct > 0:
            print(f"  → Custom is {diff_pct:.1f}% BETTER than gzip")
        else:
            print(f"  → Custom is {abs(diff_pct):.1f}% WORSE than gzip")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
