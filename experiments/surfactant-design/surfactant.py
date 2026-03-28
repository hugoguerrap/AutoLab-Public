"""
Surfactant Design — Editable Candidate File
============================================

Champion: Undecenoyl Tris(hydroxymethyl)methane Ester = 0.9723
"""

# ── Current Champion ───────────────────────────────────────────
# Undecenoyl ester of tris(hydroxymethyl)methanol
# C11:1 unsaturated tail + neopentyl triol head
BEST_SMILES = "CCCCCCCCCC=CC(=O)OCC(O)(CO)CO"

# ── Top Candidates ─────────────────────────────────────────────
CANDIDATES = [
    {
        "name": "Undecenoyl_TrisHM",
        "smiles": "CCCCCCCCCC=CC(=O)OCC(O)(CO)CO",
        "score": 0.9723,
        "notes": "C12 unsaturated + triol head, LogP 1.94, aquatic 0.779",
    },
    {
        "name": "Undecenoyl_Pentaerythritol",
        "smiles": "CCCCCCCCCC=CC(=O)OC(CO)(CO)CO",
        "score": 0.9723,
        "notes": "Same score, pentaerythritol isomer",
    },
    {
        "name": "Lauroyl_TrisHM",
        "smiles": "CCCCCCCCCCCC(=O)OCC(O)(CO)CO",
        "score": 0.9698,
        "notes": "Saturated version, LogP 2.17",
    },
    {
        "name": "Lauroyl_Pentaerythritol_4OH",
        "smiles": "CCCCCCCCCCCC(=O)OC(CO)(CO)C(O)CO",
        "score": 0.9690,
        "notes": "4-OH variant, biodeg 0.78",
    },
    {
        "name": "Lauroyl_Bis_Glycerol",
        "smiles": "CCCCCCCCCCCC(=O)OC(C(O)CO)C(O)CO",
        "score": 0.9600,
        "notes": "Branched tetrol, previous champion",
    },
]

# ── Strategy Notes ─────────────────────────────────────────────
STRATEGY_NOTES = """
Exp 1: Baseline survey — sugar esters best class (0.9381)
Exp 2: Hydroxyl optimization — branched tetrol (0.9600)
Exp 3: Tail length + dual ester — no improvement
Exp 4: Quaternary C triol head (0.9698)
Exp 5: Fine-tuning — no improvement over 0.9698
Exp 6: UNSATURATED TAIL BREAKTHROUGH (0.9723)

KEY: Double bond in C12 tail lowers LogP (2.17→1.94), boosting aquatic
safety (0.763→0.779) while maintaining all other maxed scores.

Score decomposition (0.9723):
  amphi=1.0, HLB=1.0(13.68), CMC=0.906, biodeg=0.76, aquatic=0.779, SA=0.975
  Bonuses: green(+0.03) + sweet_spot(+0.02) + amphi(+0.02) = +0.07

Remaining bottlenecks:
- CMC 0.906 — locked at C12 chain length
- Biodeg 0.76 — needs hydrolyzable bonds but adds complexity
- Aquatic 0.779 — could improve with lower LogP but risks LogP penalty

Double bond position doesn't matter (all C12:1 isomers = same score).
Ether-interrupted chain kills amphiphilicity (chain length < 8).

At theoretical ceiling for this scaffold class.
"""
