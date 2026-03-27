"""
Artificial Life (Lenia) — Rules Definition
============================================
THIS IS THE FILE CLAUDE OPTIMIZES.

Define universe rules by specifying parameters for the Lenia simulation.
Claude modifies these to discover rules that produce emergent life-like behavior.

Parameters:
    mu (float): Center of growth function (0.0-0.5). Controls "how much neighbor energy triggers growth"
    sigma (float): Width of growth function (0.001-0.1). Controls "how strict the growth rule is"
    radius (int): Kernel radius in cells (5-20). Controls "how far a cell can see"
    beta_peaks (list of (center, width)): Shell structure of the kernel. Controls "how influence is distributed"
    kernel_type (str): "gaussian" or "ring"
    init_type (str): "circle", "ring", "random_blob", "multi_blob"
    dt (float): Time step (0.01-0.5). Controls "how fast things change"

The evaluate function in prepare.py is the FROZEN truth.
"""

# ============================================================
# KNOWN RULES LIBRARY — Reference configurations
# ============================================================

RULES_LIBRARY = {
    "orbium": {
        "mu": 0.15,
        "sigma": 0.015,
        "radius": 13,
        "beta_peaks": [(0.5, 0.15)],
        "kernel_type": "gaussian",
        "init_type": "circle",
        "dt": 0.1,
    },
    "geminium": {
        "mu": 0.14,
        "sigma": 0.014,
        "radius": 10,
        "beta_peaks": [(0.5, 0.15), (0.8, 0.1)],
        "kernel_type": "gaussian",
        "init_type": "circle",
        "dt": 0.1,
    },
    "static_blob": {
        "mu": 0.3,
        "sigma": 0.05,
        "radius": 8,
        "beta_peaks": [(0.3, 0.2)],
        "kernel_type": "gaussian",
        "init_type": "circle",
        "dt": 0.1,
    },
}

# ============================================================
# CURRENT RULES — Claude: modify these to maximize composite_score
# ============================================================

CURRENT_RULES = {
    "experiment": {
        "mu": 0.15,
        "sigma": 0.04,
        "radius": 13,
        "beta_peaks": [(0.5, 0.15)],
        "kernel_type": "gaussian",
        "init_type": "multi_blob",
        "dt": 0.1,
    },
}

# ============================================================
# OPTIMIZATION NOTES
# ============================================================
# What produces interesting life:
#   - mu around 0.1-0.2 (too low = dies, too high = explodes)
#   - sigma around 0.01-0.03 (controls selectivity)
#   - Multiple beta peaks create richer interactions
#   - Ring kernel_type creates different dynamics than gaussian
#   - dt affects speed vs stability tradeoff
#
# What to try:
#   - Multiple shells: beta_peaks = [(0.3, 0.1), (0.6, 0.1), (0.9, 0.05)]
#   - Ring kernels: kernel_type = "ring"
#   - Different initializations: "multi_blob" for interaction between groups
#   - Vary radius: larger = more complex but slower
#   - Fine-tune mu/sigma: small changes can switch between death/life/explosion
#
# Goals:
#   - survival_score > 0.5 (stays alive)
#   - movement_score > 0.3 (moves!)
#   - complexity_score > 0.4 (organized, not noise)
#   - stability_score > 0.5 (doesn't fluctuate wildly)
#   - structure_score > 0.2 (distinct components)
#   - oscillation_score > 0.3 (periodic behavior = life-like)
