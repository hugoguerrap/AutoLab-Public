"""
Drug Discovery - Molecule Generator & Optimizer
================================================
THIS IS THE FILE CLAUDE OPTIMIZES.

It defines the current best molecule and the mutation strategy.
Claude modifies the SMILES string, the mutation approach, and the
generation strategy to maximize the composite_score from prepare.py.

Current approach: gamma-lactam (pyrrolidinone) scaffold with thienyl + fluorophenyl.
"""

# --- CURRENT BEST MOLECULE ---
# Claude: modify this SMILES to improve the composite_score.
# The evaluate function in prepare.py is the frozen truth.
BEST_SMILES = "O=C(O)C1CC(c2ccsc2)C(=O)N1c1ccc(F)cc1"  # QED 0.9484, composite 1.0, NOVEL

# --- TOP 5 CANDIDATES (ALL NOVEL — CID 0 on PubChem) ---
CANDIDATES = [
    "O=C(O)C1CC(c2ccsc2)C(=O)N1c1ccc(F)cc1",   # ★★ CHAMPION: QED 0.9484, thienyl-fluorophenyl lactam, NOVEL
    "O=C(O)C1CC(c2ccsc2)C(=O)N1c1cccc(F)c1",   # QED 0.9484, meta-F isomer, NOVEL
    "O=C(O)C1CC(c2ccsc2)CN1C(=O)c1ccccc1",      # QED 0.9481, thienyl-benzoyl pyrrolidine, NOVEL
    "O=C(O)C1CC(c2ccc(F)cc2)C(=O)N1c1ccccc1",   # QED 0.9478, fluorophenyl-phenyl lactam, NOVEL
    "O=C(O)C1CC(c2ccc(F)cc2)CN1C(=O)c1ccccc1",  # QED 0.9477, fluorophenyl-benzoyl pyrrolidine, NOVEL
]

# --- PREVIOUS CHAMPION (for reference) ---
PREV_BEST = "O=C(O)C1CC(c2ccc(F)cc2)N(C(=O)c2ccco2)C1"  # QED 0.9461, furoyl pyrrolidine

# --- OPTIMIZATION SUMMARY ---
STRATEGY_NOTES = """
=== DRUG DISCOVERY OPTIMIZATION — PHASE 2 COMPLETE ===

30 experiments total (10 original + 20 extended), ~350+ molecules evaluated.

CHAMPION: 4-(thiophen-3-yl)-1-(4-fluorophenyl)-5-oxopyrrolidine-3-carboxylic acid
  SMILES: O=C(O)C1CC(c2ccsc2)C(=O)N1c1ccc(F)cc1
  QED: 0.9484 | Composite: 1.0 | MW: 305.3 | logP: 2.86
  HBD: 1 | HBA: 3 | TPSA: 57.6 | RotBonds: 3 | Rings: 3
  Lipinski: PASS | PAINS: CLEAN | SA: 3.26 | PubChem: CID 0 (NOVEL)

PHASE 2 KEY DISCOVERIES:
1. Benzoyl (vs furoyl) on pyrrolidine reduces HBA from 3 to 2, boosts QED from 0.9461 to 0.9477
2. gamma-Lactam (pyrrolidinone) integrates the C=O into the ring, reaching 0.9478
3. Thienyl replaces fluorophenyl at C4 — sweet spot at MW 305, logP 2.86 — QED 0.9484
4. Multiple isomers (para-F, meta-F, ortho-F on N-phenyl) all tie at 0.9484

SCAFFOLDS EXPLORED (experiments 11-31):
- Morpholines/oxazines (exp 11): max QED 0.9418 — O adds HBA, hurts score
- Piperazines (exp 12): max QED 0.9431 — extra N pushes logP too low
- Indoles (exp 13): max QED 0.8035 — NH donor kills QED
- Benzimidazoles (exp 14): max QED 0.8623 — NH again
- Tetrahydroisoquinolines (exp 15): max QED 0.9351 — fused ring too rigid
- Dihydrobenzofurans/chromanones (exp 16): max QED 0.9356 — O-ring suboptimal
- Azetidines (exp 17): max QED 0.9451 — 4-membered ring slightly worse
- Quinazolinones (exp 19): max QED 0.9444 — different family, close
- gamma-Lactams (exp 24-25): ★★★ QED 0.9478-0.9484 — new best scaffold
- Piperidinones (exp 27): max QED 0.9465 — 6-ring slightly worse than 5
- Isoindolinones (exp 28): max QED 0.9427 — fused bicyclic hurts

WHAT DRIVES HIGH QED:
- MW ~300-315 (sweet spot)
- logP ~2.7-3.1 (moderate lipophilicity)
- HBD = 1 (single acid OH)
- HBA = 2-3 (minimal heteroatoms)
- TPSA ~57 (low polar surface)
- RotBonds = 3 (constrained but not rigid)
- 2 aromatic + 1 aliphatic ring (optimal ring count)

WHAT KILLS QED:
- NH donors (indoles, benzimidazoles) — HBD=2 is punished
- Extra O/N in rings (morpholines, oxazines) — raises TPSA/HBA
- MW > 330 — steep QED penalty
- logP > 3.5 — greasy molecules score worse
- Fused bicyclics with >3 rings — ring count penalty

Novel molecules found (CID 0 on PubChem): 20+
Best composite score: 1.0 (capped — QED 0.85+ with all bonuses)
QED 0.9484 is likely near the theoretical ceiling for drug-like molecules.
"""
