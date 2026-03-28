"""
Surfactant Design — Editable Candidate File
============================================

THIS IS THE ONLY FILE YOU MODIFY during the optimization loop.

Champion: Lauroyl Tris(hydroxymethyl)methane Ester = 0.9698
"""

# ── Current Champion ───────────────────────────────────────────
# Lauroyl ester of 2-hydroxy-1,1,1-tris(hydroxymethyl)methane
# Simple neopentyl triol head + C12 ester
BEST_SMILES = "CCCCCCCCCCCC(=O)OCC(O)(CO)CO"

# ── Top Candidates ─────────────────────────────────────────────
CANDIDATES = [
    {
        "name": "Lauroyl_TrisHM_Triol",
        "smiles": "CCCCCCCCCCCC(=O)OCC(O)(CO)CO",
        "score": 0.9698,
        "notes": "Quaternary C triol head, perfect HLB 13.61, SA 0.975!",
    },
    {
        "name": "Lauroyl_Pentaerythritol_Type_A",
        "smiles": "CCCCCCCCCCCC(=O)OC(CO)(CO)C(O)CO",
        "score": 0.9690,
        "notes": "4-OH branched, HLB 15.42, biodeg 0.78, SA 0.875",
    },
    {
        "name": "Lauroyl_Pentaerythritol_Type_B",
        "smiles": "CCCCCCCCCCCC(=O)OC(CO)(C(O)CO)CO",
        "score": 0.9690,
        "notes": "Bis-glycerol with quat C, same scores",
    },
    {
        "name": "Lauroyl_Bis_Glycerol",
        "smiles": "CCCCCCCCCCCC(=O)OC(C(O)CO)C(O)CO",
        "score": 0.9600,
        "notes": "Previous champion — branched tetrol",
    },
    {
        "name": "Lauroyl_Erythritol",
        "smiles": "CCCCCCCCCCCC(=O)OCC(O)C(O)CO",
        "score": 0.9558,
        "notes": "Linear tetrol, perfect HLB 13.61",
    },
]

# ── Strategy Notes ─────────────────────────────────────────────
STRATEGY_NOTES = """
Exp 1: Baseline survey — sugar esters best class (0.9381)
Exp 2: Hydroxyl optimization — branched tetrol head (0.9600)
Exp 3: Tail length + dual ester — no improvement
Exp 4: Polyol geometry — quaternary C triol BREAKTHROUGH (0.9698)

KEY FINDING: Quaternary carbon with CH2OH branches is the optimal head.
- Neopentyl-type geometry: C(OH)(CH2OH)(CH2OH)
- Simple + compact = SA 0.975 (massive improvement!)
- 3 OH groups = enough for biodeg 0.76 + aquatic 0.76
- Perfect HLB 13.61

Score decomposition (0.9698):
  amphi=1.0, HLB=1.0, CMC=0.906, biodeg=0.76, aquatic=0.763, SA=0.975
  Base: 0.200 + 0.200 + 0.136 + 0.152 + 0.114 + 0.098 = 0.900
  Bonuses: green(+0.03) + sweet_spot(+0.02) + amphi(+0.02) = +0.07
  Total: 0.970

Remaining bottleneck: biodeg (0.76) and aquatic (0.763).
CMC is locked at 0.906 for C12.

Next ideas:
- Try C13/C14 on the trisHM head (might improve CMC without losing HLB)
- Try adding one more OH to the trisHM without adding too much complexity
- Try ester-amide hybrid linker to boost biodeg
"""
