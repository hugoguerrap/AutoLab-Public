"""
Surfactant Design — Editable Candidate File
============================================

THIS IS THE ONLY FILE YOU MODIFY during the optimization loop.

BEST_SMILES: The current champion molecule.
CANDIDATES:  Top candidates for further exploration.
STRATEGY_NOTES: What you've learned so far.

Champion: Lauroyl Glucose Ester = 0.9381
"""

# ── Current Champion ───────────────────────────────────────────
# Lauroyl Glucose Ester — ester-linked sugar surfactant
BEST_SMILES = "CCCCCCCCCCCC(=O)OC1C(O)C(O)C(CO)OC1CO"

# ── Top Candidates ─────────────────────────────────────────────
CANDIDATES = [
    {
        "name": "Lauroyl_Glucose_Ester",
        "smiles": "CCCCCCCCCCCC(=O)OC1C(O)C(O)C(CO)OC1CO",
        "score": 0.9381,
        "notes": "Ester linkage + sugar head = HLB 14.94, biodeg 0.74",
    },
    {
        "name": "Lauroyl_Glucoside_Ester",
        "smiles": "CCCCCCCCCCCC(=O)OC1C(O)C(O)C(O)C(CO)O1",
        "score": 0.9374,
        "notes": "Sugar ester variant, HLB 15.58, biodeg 0.74",
    },
    {
        "name": "Glycerol_Monolaurate",
        "smiles": "CCCCCCCCCCCC(=O)OCC(O)CO",
        "score": 0.9313,
        "notes": "Simple ester + glycerol, high SA, biodeg 0.72",
    },
    {
        "name": "Lauroyl_Glycinate",
        "smiles": "CCCCCCCCCCCC(=O)NCC(=O)[O-].[Na+]",
        "score": 0.9012,
        "notes": "Amino acid surfactant, great SA + amphiphilicity",
    },
    {
        "name": "Lauryl_Glucoside",
        "smiles": "CCCCCCCCCCCCOC1OC(CO)C(O)C(O)C1O",
        "score": 0.8923,
        "notes": "Original baseline — ether link, lower biodeg",
    },
]

# ── Strategy Notes ─────────────────────────────────────────────
STRATEGY_NOTES = """
Experiment 1 — Baseline survey of 10 surfactant scaffolds.

KEY FINDING: Ester linkages are the #1 lever.
- Ether-linked glucoside: biodeg 0.66
- Ester-linked glucose: biodeg 0.74 (+0.08!)
- Ester also counts as hydrolyzable bond → green bonus

Scaffold ranking:
1. Sugar esters (glucose ester): 0.9381 — perfect HLB + good biodeg
2. Glycerol esters: 0.9313 — simple, high SA, ester boost
3. Amino acid (glycinate): 0.9012 — great SA but lower amphiphilicity
4. Sugar ethers (glucosides): 0.8923 — good but ether < ester for biodeg
5. Rhamnolipid-inspired: 0.8811 — complex, lower SA

Bottlenecks to optimize:
- Biodegradability: best is 0.74, needs more hydrolyzable bonds + OH groups
- SA score: sugar esters only 0.60, simplify structure
- HLB: already near-optimal for sugar esters

Next: Try adding MORE ester/hydroxyl groups to sugar ester scaffold.
Try glycerol + sugar hybrid heads. Try ester-amide dual linkages.
"""
