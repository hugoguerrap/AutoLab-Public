"""
Fertilizer Design — Molecule Definition
=========================================
THIS IS THE FILE CLAUDE OPTIMIZES.

Define candidate fertilizer molecules by specifying SMILES strings.
Claude modifies these to discover novel nitrogen carriers with:
1. High nitrogen content (>20% N by mass)
2. Slow-release properties (slower dissolution than urea)
3. Biodegradability (EU 2026 compliant)
4. Low environmental impact (less runoff, less volatilization)
5. Affordable synthesis (common atoms, simple structure)
6. Novelty (not in PubChem)

The evaluate function in prepare.py is the FROZEN truth.
"""

# ============================================================
# CURRENT BEST MOLECULE — CHAMPION
# ============================================================

BEST_SMILES = "NC(=N)NC(=N)NC(=O)NC(=O)NC1CCC2(CC2)CC1"
BEST_COMPOSITE = 0.7964
# Spiro[cyclopropane-cyclohexyl] diguanidine-biuret
# N%: 33.20, MW: 295.3, SlowRelease: 0.784, Biodeg: 0.95
# Novel (not in PubChem), 2-ring system, LogP 0.14
# Beats IBDU (0.673) by +18.4%

# ============================================================
# TOP 10 MOLECULES DISCOVERED
# ============================================================

CANDIDATES = [
    {
        "smiles": "NC(=N)NC(=N)NC(=O)NC(=O)NC1CCC2(CC2)CC1",
        "name": "Spiro[cyclopropane-cyclohexyl] diguanidine-biuret (CHAMPION)",
        "notes": "Composite 0.7964. N% 33.2, SlowRel 0.784, MW 295. Novel. 2-ring system maximizes slow-release while staying under MW 300 for biodeg.",
    },
    {
        "smiles": "NC(=N)NC(=N)NC(=O)NC(=O)NCC1CCCCCC1",
        "name": "Diguanidine-biuret-methylenecycloheptyl",
        "notes": "Composite 0.7934. N% 33.0, SlowRel 0.735, MW 297. Novel. Methylene spacer to ring.",
    },
    {
        "smiles": "NC(=N)NC(=N)NC(=O)NC(=O)N(C)C1CCCCCC1",
        "name": "N-Methyl diguanidine-biuret-cycloheptyl",
        "notes": "Composite 0.7919. N% 33.0, SlowRel 0.735, MW 297. Novel. N-methylation variant.",
    },
    {
        "smiles": "NC(=N)NC(=N)NC(=S)NC(=O)NC1CCCCCC1",
        "name": "Thio-diguanidine-urea-cycloheptyl",
        "notes": "Composite 0.7918. N% 32.8, SlowRel 0.736, MW 299. Novel. Thiourea adds hydrophobicity.",
    },
    {
        "smiles": "NC(=N)NC(=N)NC(=O)NC(=O)NC1CCCCCC1",
        "name": "Diguanidine-biuret-cycloheptyl",
        "notes": "Composite 0.7916. N% 34.6, SlowRel 0.727, MW 283. Novel. Core optimized structure.",
    },
    {
        "smiles": "NC(=N)NC(=N)NC(=O)NC1CCCCCC1",
        "name": "Diguanidine-urea-cycloheptyl",
        "notes": "Composite 0.7816. N% 35.0, SlowRel 0.682, MW 240. Novel. Simpler variant, higher N%.",
    },
    {
        "smiles": "NC(=O)NC(=O)NC(=O)NC(=O)NC1CCCCCC1",
        "name": "N-Cycloheptyl tetrauret",
        "notes": "Composite 0.7786. N% 24.6, SlowRel 0.708, MW 285. Novel. Pure urea chain approach.",
    },
    {
        "smiles": "NC(=N)NC(=O)NC(=O)NC1CCCCC1",
        "name": "Guanidine-biuret-cyclohexyl",
        "notes": "Composite 0.7784. N% 30.8, SlowRel 0.655, MW 227. Novel. Good balance of properties.",
    },
    {
        "smiles": "NC(=O)NC(=O)NC(=O)NC(=O)NC1CCCCC1",
        "name": "N-Cyclohexyl tetrauret",
        "notes": "Composite 0.7764. N% 25.8, SlowRel 0.700, MW 271. Novel. Triggers both bonuses.",
    },
    {
        "smiles": "NC(=O)NC(=O)NC(=O)NC1CCCCCC1",
        "name": "N-Cycloheptyl triuret",
        "notes": "Composite 0.7647. N% 23.1, SlowRel 0.644, MW 242. Novel. First to cross 0.76.",
    },
]

# ============================================================
# OPTIMIZATION LOG — KEY DISCOVERIES
# ============================================================
# 15 experiments, 60+ molecules evaluated, 20+ novel structures found
#
# Winning strategy: Diguanidine-biuret backbone + hydrophobic cycloalkyl cap
#
# Key insights:
# 1. LogP 0-3 is critical for slow-release (+0.20), worth sacrificing solubility (10% weight)
# 2. Biuret/triuret backbone (NC(=O)N linkage) gives +0.15 slow-release bonus
# 3. MW 100-300 sweet spot: enough for slow-release but under 300 preserves biodeg 0.95
# 4. Guanidine (NC(=N)N) is more N-efficient than urea — same bonding pattern, no oxygen
# 5. Cycloalkyl rings add +0.05 per ring to slow-release AND push LogP positive
# 6. Spiro-cyclopropane on cyclohexane gives 2 rings while keeping MW < 300
# 7. Both composite bonuses triggered: slow_release > 0.6 + N% > 20, biodeg > 0.7 + slow_release > 0.5
# 8. SA score is the main limiter — bicyclic/bridged systems score worse
# 9. Thiourea (C=S) adds hydrophobicity without hurting biodeg (S is bio-friendly)
# 10. N-heterocyclic rings (piperidine) push LogP too negative, killing slow-release
