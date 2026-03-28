"""
Surfactant Design — Editable Candidate File
============================================

THIS IS THE ONLY FILE YOU MODIFY during the optimization loop.

Champion: Lauroyl Bis-Glycerol Ester = 0.9600
"""

# ── Current Champion ───────────────────────────────────────────
# Lauroyl Bis-Glycerol Ester — branched tetrol head + ester link
BEST_SMILES = "CCCCCCCCCCCC(=O)OC(C(O)CO)C(O)CO"

# ── Top Candidates ─────────────────────────────────────────────
CANDIDATES = [
    {
        "name": "Lauroyl_Bis_Glycerol",
        "smiles": "CCCCCCCCCCCC(=O)OC(C(O)CO)C(O)CO",
        "score": 0.9600,
        "notes": "Branched tetrol head, HLB 15.42, biodeg 0.76, SA 0.825",
    },
    {
        "name": "Lauroyl_Erythritol",
        "smiles": "CCCCCCCCCCCC(=O)OCC(O)C(O)CO",
        "score": 0.9558,
        "notes": "Linear tetrol, perfect HLB 13.61, biodeg 0.74",
    },
    {
        "name": "Lauroyl_Threitol_Branched",
        "smiles": "CCCCCCCCCCCC(=O)OC(CO)C(O)CO",
        "score": 0.9558,
        "notes": "Branched triol, perfect HLB 13.61",
    },
    {
        "name": "Lauroyl_Pentitol",
        "smiles": "CCCCCCCCCCCC(=O)OCC(O)C(O)C(O)CO",
        "score": 0.9550,
        "notes": "5-OH chain, highest biodeg 0.76",
    },
    {
        "name": "Lauroyl_Glucose_Ester",
        "smiles": "CCCCCCCCCCCC(=O)OC1C(O)C(O)C(CO)OC1CO",
        "score": 0.9381,
        "notes": "Sugar ring head, perfect HLB but lower SA",
    },
]

# ── Strategy Notes ─────────────────────────────────────────────
STRATEGY_NOTES = """
Exp 1: Baseline survey — sugar esters best class (0.9381)
Exp 2: Hydroxyl optimization — branched polyol heads dominate

KEY INSIGHTS:
- Ester linkage: mandatory (+0.08 biodeg vs ether)
- Optimal OH count: 4 (3=ok, 5+=LogP too low)
- Branched polyol > linear chain for SA score
- Bis-glycerol head: 0.9600 (biodeg 0.76, SA 0.825)
- Erythritol head: 0.9558 (perfect HLB 13.61)
- Sugar rings hurt SA score (0.60 vs 0.825)

Bottlenecks remaining:
- Biodegradability: 0.76 (needs more hydrolyzable bonds?)
- CMC score: 0.906 (could improve with longer tail?)
- HLB: 15.42 (slightly above 15, could tune with tail length)

Next: Try C10/C14 tail on bis-glycerol. Try adding ester-amide dual
linkage for extra biodeg. Try adding a second ester in the head.
"""
