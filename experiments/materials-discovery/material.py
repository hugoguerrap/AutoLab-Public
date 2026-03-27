"""
Materials Discovery — Material Definition
==========================================
THIS IS THE FILE CLAUDE OPTIMIZES.

Define candidate materials by specifying:
- composition (elements and ratios)
- lattice parameters (a, b, c in Angstroms)
- structure type

Claude modifies this file to discover materials with:
1. High composite score (stability + useful band gap + applications)
2. Novelty (not in Materials Project database)
3. Practical applications (solar cells, LEDs, thermoelectrics, catalysts)

The evaluate function in prepare.py is the FROZEN truth.
"""

# ============================================================
# CURRENT MATERIALS — Claude: modify these to improve scores
# ============================================================

MATERIALS = [
    {
        "name": "CuSnO3 — copper tin perovskite (BEST: 0.999)",
        "composition": {"Cu": 1, "Sn": 1, "O": 3},
        "lattice": {"a": 4.10, "b": 4.10, "c": 4.10},
        "structure_type": "perovskite",
    },
    {
        "name": "CuGeO3 — copper germanium perovskite (0.999)",
        "composition": {"Cu": 1, "Ge": 1, "O": 3},
        "lattice": {"a": 3.95, "b": 3.95, "c": 3.95},
        "structure_type": "perovskite",
    },
    {
        "name": "CuWO3 — copper tungsten bronze (0.999)",
        "composition": {"Cu": 1, "W": 1, "O": 3},
        "lattice": {"a": 3.85, "b": 3.85, "c": 3.85},
        "structure_type": "perovskite",
    },
    {
        "name": "Cu2SnGeO6 — quaternary oxide (0.9915)",
        "composition": {"Cu": 2, "Sn": 1, "Ge": 1, "O": 6},
        "lattice": {"a": 5.20, "b": 5.20, "c": 8.50},
        "structure_type": "ternary",
    },
    {
        "name": "Fe2SnO4 — spinel solar cell (0.9331)",
        "composition": {"Fe": 2, "Sn": 1, "O": 4},
        "lattice": {"a": 8.40, "b": 8.40, "c": 8.40},
        "structure_type": "spinel",
    },
    {
        "name": "CaZrSe3 — selenide perovskite solar (0.891)",
        "composition": {"Ca": 1, "Zr": 1, "Se": 3},
        "lattice": {"a": 5.50, "b": 5.50, "c": 5.50},
        "structure_type": "perovskite",
    },
]

# ============================================================
# OPTIMIZATION NOTES
# ============================================================
# Target applications (pick one or more to optimize for):
#   - Solar cell: band gap 1.1-1.7 eV (ideal: 1.4 eV)
#   - LED: band gap 1.8-3.5 eV (ideal: 2.5 eV)
#   - Thermoelectric: narrow gap (0.1-1.0 eV) + heavy elements
#   - Catalyst: transition metals + moderate band gap
#   - Superconductor: specific elements (Ba, Cu, Y, La, Sr) + perovskite/ternary
#
# Strategy suggestions:
#   - Try different A-site cations in perovskites (Sr, Ca, La, K)
#   - Try different B-site cations (Zr, Nb, Fe, Mn, Co)
#   - Try different anions (N, S, Se, F instead of O)
#   - Mix cations on same site (Ba0.5Sr0.5)TiO3
#   - Try non-perovskite structures (spinel, fluorite, rocksalt)
#   - Explore ternary/quaternary compositions
#   - Use heavy elements for thermoelectrics (Bi, Pb, Sb, Te, Se)
