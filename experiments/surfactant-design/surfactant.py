"""
Surfactant Design — Editable Candidate File
============================================

THIS IS THE ONLY FILE YOU MODIFY during the optimization loop.

BEST_SMILES: The current champion molecule.
CANDIDATES:  Top candidates for further exploration.
STRATEGY_NOTES: What you've learned so far.

Baseline: Lauryl Glucoside (nonionic green surfactant)
"""

# ── Current Champion ───────────────────────────────────────────
# Lauryl Glucoside — nonionic green surfactant baseline
BEST_SMILES = "CCCCCCCCCCCCOC1OC(CO)C(O)C(O)C1O"

# ── Top Candidates ─────────────────────────────────────────────
CANDIDATES = [
    {
        "name": "Lauryl_Glucoside",
        "smiles": "CCCCCCCCCCCCOC1OC(CO)C(O)C(O)C1O",
        "score": None,  # will be evaluated
        "notes": "Baseline — nonionic, sugar-based, biodegradable",
    },
    {
        "name": "Sodium_Lauroyl_Sarcosinate",
        "smiles": "CCCCCCCCCCCC(=O)N(C)CC(=O)[O-].[Na+]",
        "score": None,
        "notes": "Amino acid surfactant — anionic, mild, biodegradable",
    },
    {
        "name": "CAPB",
        "smiles": "CCCCCCCCCCCC(=O)NCCC[N+](C)(C)CC(=O)[O-]",
        "score": None,
        "notes": "Cocamidopropyl betaine — amphoteric, very mild",
    },
]

# ── Strategy Notes ─────────────────────────────────────────────
STRATEGY_NOTES = """
Experiment 0 — Baseline evaluation pending.

Known surfactant classes to explore:
1. Sugar-based (alkyl glucosides, sophorolipids) — green, biodegradable
2. Amino acid-based (sarcosinates, glutamates, glycinates) — mild, biodegradable
3. Ester-linked (fatty acid esters of polyols) — hydrolyzable, green
4. Betaines/amphoterics — mild, good foaming
5. Gemini surfactants (twin-tail, twin-head) — very low CMC
6. Biosurfactant-inspired (rhamnolipids, trehalolipids) — novel scaffolds

Target: composite_score > 0.85 with novel, biodegradable structure.
"""
