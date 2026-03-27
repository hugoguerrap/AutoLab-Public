# molecule.py — EDITABLE: current candidate nootropic molecules
# ─────────────────────────────────────────────────────────────────────────────
# Claude modifies ONLY this file during the optimization loop.
# NEVER modify prepare.py.
#
# Optimization target:
#   composite = 0.25*QED + 0.30*BBB + 0.25*CNS_MPO + 0.20*cogn_pharm ≥ 0.80
#
# KEY LEVERS (in order of weight):
#   BBB (30%) — keep TPSA < 60, logP 1-3, MW < 350, HBD ≤ 2
#   QED (25%) — balance MW, rotatable bonds, rings
#   CNS_MPO (25%) — MW ≤ 360, TPSA ≤ 90, HBD ≤ 3, logP ≤ 4
#   Pharm (20%) — add pyrrolidone, indole, piperidine, xanthine motif

# Champion so far — update after each improvement
BEST_SMILES    = "O=C1CCCN1C(c1cc2ccccc2[nH]1)C1CCN(C)CC1"  # direct-linker N-Me-pip triple — exp_10
BEST_COMPOSITE = 0.9864

# What we're testing this round
HYPOTHESIS = """
OPTIMIZATION COMPLETE — EXIT CONDITION MET: composite ≥ 0.85 with novel molecule.

Champion: O=C1CCCN1C(c1cc2ccccc2[nH]1)C1CCN(C)CC1
  Composite: 0.9864 (target was 0.85)
  QED=0.9454, BBB=1.0, CNS_MPO=1.0, cogn_pharm=1.0
  MW=311.4, logP=3.17, TPSA=39.3, HBD=1, HBA=2
  PAINS: CLEAN, NOVEL (PubChem CID=0 = not found)

Architecture: 2-(1H-indol-2-yl)-1-(1-methylpiperidin-4-yl)pyrrolidin-2-one
  Triple pharmacophore: pyrrolidone + indole + N-methylpiperidine
  All three SMARTS matched simultaneously for pharm=1.0
  N-methylation of piperidine: HBD 2→1, unlocked MPO=1.0
  Direct linker (no CH2 spacer): fewer rotatable bonds → QED boost

12 experiments, 55 molecules evaluated, composite went:
  0.717 (Piracetam) → 0.8623 → 0.9441 → 0.9571 → 0.9844 → 0.9864

Key breakthroughs:
  Exp 3: Dual pharmacophore (indole+pyrrolidone) — pharm 0.55→0.80
  Exp 8: Triple pharmacophore discovery — pharm=1.0
  Exp 9: N-methyl piperidine — MPO 0.917→1.0
  Exp 10: Direct linker — QED 0.937→0.945
"""

# ─── CHAMPION MOLECULE ────────────────────────────────────────────────────────
CANDIDATES = [
    ("CHAMPION", "O=C1CCCN1C(c1cc2ccccc2[nH]1)C1CCN(C)CC1"),
]

# ─── STRATEGY NOTES FOR THE LOOP ─────────────────────────────────────────────
#
# PHASE 1 — Racetam derivatives (exp 1-4)
#   Goal: beat Piracetam (composite ~0.62) quickly
#   Moves:
#     • N-phenyl piracetam: replace NH2 on acetamide with NHPh → lower MW, keep QED
#     • N,N-dimethyl piracetam: NC(=O) → CN(C)C=O → drops HBD, ↑ BBB
#     • 4-fluorophenyl aniracetam: swap benzoyl ring for 4-F-phenyl → ↑ metabolic stability
#     • Methylated pyrrolidone: N-methyl on the ring → slightly ↓ TPSA
#
# PHASE 2 — Xanthine / methylxanthine hybrids (exp 5-8)
#   Goal: leverage cogn_pharm bonus from xanthine core
#   Moves:
#     • Theophylline (remove 3-methyl from caffeine): Cn1cnc2c1c(=O)[nH]c(=O)n2
#     • 3-methylxanthine: O=C1NC(=O)c2nc(C)nc2N1 — lower MW than caffeine
#     • Xanthine-pyrrolidone hybrid: fuse xanthine fragment with 2-pyrrolidone linker
#     • 8-substituted theophylline: add small groups at C8 position
#
# PHASE 3 — Novel scaffolds (exp 9-12)
#   Goal: composite > 0.80, novel molecule (not in PubChem)
#   Moves:
#     • Indole-2-carboxyl pyrrolidone: indole + lactam → high cogn_pharm, CNS-friendly
#     • Benzimidazole-acetamide: low TPSA, known CNS scaffold
#     • Imidazo[1,2-a]pyridine-2-carboxamide: fused bicyclic, low MW
#     • Piperidine-xanthine conjugate: pilocarpine-like but CNS-optimized
#
# PHASE 4 — Fine-tune champion (exp 13-15)
#   Goal: composite ≥ 0.85, PAINS CLEAN, not in PubChem
#   Moves:
#     • Fluorine substitution on aryl rings → ↑ metabolic stability, ↓ logP slightly
#     • N-methylation of HBDs → ↓ TPSA → ↑ BBB
#     • Ring contraction (6→5): often ↓ MW + ↓ TPSA
#     • Bioisosteric swap: CONH2 → CN(CH3)2 → ↓ HBD, ↑ BBB
