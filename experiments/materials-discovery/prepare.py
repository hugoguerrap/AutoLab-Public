"""
Materials Discovery — Evaluation & Novelty Check
==================================================
FROZEN FILE — Claude must NOT modify this.

Evaluates crystal structures for stability, useful properties,
and novelty against known materials databases.

Usage:
    python prepare.py evaluate           # Evaluate current material in material.py
    python prepare.py novelty            # Check if material exists in known databases
    python prepare.py baseline           # Show baseline materials for comparison
"""

import sys
import json
import math
import hashlib
import urllib.request
import urllib.parse
from datetime import datetime

# ============================================================
# FROZEN EVALUATION — DO NOT MODIFY
# ============================================================

def evaluate_material(composition: dict, lattice_params: dict, structure_type: str) -> dict:
    """
    Evaluate a hypothetical material based on composition and structure.

    Uses empirical rules and computational estimates:
    - Goldschmidt tolerance factor (perovskites)
    - Pauling electronegativity rules
    - Density estimation
    - Band gap estimation (empirical)
    - Formation energy estimation (empirical)
    - Stability checks

    Args:
        composition: dict of {element_symbol: fraction}, e.g. {"Ba": 1, "Ti": 1, "O": 3}
        lattice_params: {"a": float, "b": float, "c": float} in Angstroms
        structure_type: "perovskite", "rocksalt", "spinel", "fluorite", "binary", "ternary"

    Returns:
        dict with scores and properties
    """
    from pymatgen.core import Element, Composition

    results = {}

    # 1. Validate composition
    try:
        comp = Composition(composition)
        results["formula"] = comp.reduced_formula
        results["num_elements"] = len(comp.elements)
        results["total_atoms"] = comp.num_atoms
    except Exception as e:
        return {"error": f"Invalid composition: {e}", "score": 0.0}

    # 2. Calculate molecular weight and density estimate
    mw = comp.weight
    volume = lattice_params["a"] * lattice_params["b"] * lattice_params["c"]
    # Approximate: Z formula units per cell depends on structure
    z_map = {"perovskite": 1, "rocksalt": 4, "spinel": 8, "fluorite": 4, "binary": 2, "ternary": 2}
    z = z_map.get(structure_type, 2)
    density = (z * mw) / (volume * 0.6022)  # g/cm³ (0.6022 = Avogadro/1e24)
    results["molecular_weight"] = round(float(mw), 2)
    results["density_gcm3"] = round(density, 2)
    results["volume_A3"] = round(volume, 2)

    # 3. Electronegativity analysis
    elements = comp.elements
    electronegativities = []
    for el in elements:
        if el.X is not None:
            electronegativities.append(el.X)

    if len(electronegativities) >= 2:
        en_diff = max(electronegativities) - min(electronegativities)
        en_avg = sum(electronegativities) / len(electronegativities)
        results["electronegativity_diff"] = round(en_diff, 2)
        results["electronegativity_avg"] = round(en_avg, 2)
    else:
        en_diff = 0
        results["electronegativity_diff"] = 0
        results["electronegativity_avg"] = 0

    # 4. Band gap estimation (empirical model)
    # Based on electronegativity difference and structure type
    if en_diff > 2.5:
        band_gap_est = 4.0 + (en_diff - 2.5) * 2  # Wide gap insulator
    elif en_diff > 1.5:
        band_gap_est = 1.5 + (en_diff - 1.5) * 2.5  # Semiconductor
    elif en_diff > 0.5:
        band_gap_est = 0.2 + (en_diff - 0.5) * 1.3  # Narrow gap
    else:
        band_gap_est = 0.0  # Metallic

    # Structure type modifier
    bg_modifier = {"perovskite": 0.9, "rocksalt": 1.1, "spinel": 0.8, "fluorite": 1.2, "binary": 1.0, "ternary": 0.95}
    band_gap_est *= bg_modifier.get(structure_type, 1.0)
    results["band_gap_eV"] = round(band_gap_est, 2)

    # 5. Formation energy estimation (empirical)
    # More negative = more stable
    # Based on electronegativity difference and composition complexity
    formation_energy = -0.5 * en_diff - 0.1 * len(elements)
    if structure_type == "perovskite" and len(elements) == 3:
        formation_energy -= 0.3  # Perovskites tend to be stable
    results["formation_energy_eV"] = round(formation_energy, 2)

    # 6. Tolerance factor (for perovskites only)
    if structure_type == "perovskite" and len(elements) >= 3:
        # ABX3 structure: need ionic radii
        radii = {}
        for el in elements:
            r = el.atomic_radius
            if r is not None:
                radii[el.symbol] = float(r)

        if len(radii) >= 3:
            sorted_radii = sorted(radii.values())
            r_x = sorted_radii[0]  # smallest = anion-like
            r_b = sorted_radii[1]  # medium = B-site
            r_a = sorted_radii[-1]  # largest = A-site
            tolerance = (r_a + r_x) / (math.sqrt(2) * (r_b + r_x))
            results["tolerance_factor"] = round(tolerance, 3)
            # Ideal perovskite: 0.8 < t < 1.05
            results["perovskite_stable"] = 0.8 <= tolerance <= 1.05
        else:
            results["tolerance_factor"] = None
            results["perovskite_stable"] = None

    # 7. Stability checks
    checks_passed = 0
    total_checks = 5

    # Check 1: Reasonable density (0.5-25 g/cm³)
    if 0.5 <= density <= 25:
        checks_passed += 1
        results["density_check"] = "PASS"
    else:
        results["density_check"] = "FAIL"

    # Check 2: Charge balance (simplified)
    # For compounds with oxygen, check if likely charge-balanced
    has_oxygen = any(el.symbol == "O" for el in elements)
    has_metal = any(el.is_metal for el in elements)
    if has_oxygen and has_metal:
        checks_passed += 1
        results["charge_check"] = "PASS"
    elif not has_oxygen:
        checks_passed += 0.5
        results["charge_check"] = "PARTIAL"
    else:
        results["charge_check"] = "FAIL"

    # Check 3: Formation energy is negative (thermodynamically favorable)
    if formation_energy < 0:
        checks_passed += 1
        results["thermodynamic_check"] = "PASS"
    else:
        results["thermodynamic_check"] = "FAIL"

    # Check 4: Reasonable lattice parameters (2-20 Å)
    params = [lattice_params["a"], lattice_params["b"], lattice_params["c"]]
    if all(2.0 <= p <= 20.0 for p in params):
        checks_passed += 1
        results["lattice_check"] = "PASS"
    else:
        results["lattice_check"] = "FAIL"

    # Check 5: Elements exist and are stable
    unstable = [el for el in elements if el.Z > 103]  # Beyond Lr
    if not unstable:
        checks_passed += 1
        results["element_check"] = "PASS"
    else:
        results["element_check"] = "FAIL"

    results["checks_passed"] = checks_passed
    results["total_checks"] = total_checks

    # 8. Application scoring
    applications = []

    # Solar cell candidate: band gap 1.1-1.7 eV
    if 1.1 <= band_gap_est <= 1.7:
        applications.append("solar_cell")
        results["solar_score"] = round(1.0 - abs(band_gap_est - 1.4) / 0.3, 2)

    # LED candidate: band gap 1.8-3.5 eV
    if 1.8 <= band_gap_est <= 3.5:
        applications.append("LED")
        results["led_score"] = round(1.0 - abs(band_gap_est - 2.5) / 1.0, 2)

    # Thermoelectric candidate: narrow gap + heavy elements
    avg_mass = float(mw) / comp.num_atoms
    if 0.1 <= band_gap_est <= 1.0 and avg_mass > 50:
        applications.append("thermoelectric")
        results["thermoelectric_score"] = round(min(avg_mass / 100, 1.0), 2)

    # Transparent conductor: wide gap + metallic character possible
    if 3.0 <= band_gap_est <= 4.5:
        applications.append("transparent_conductor")

    # Catalyst: transition metals with moderate band gap
    has_transition = any(el.is_transition_metal for el in elements)
    if has_transition and band_gap_est < 2.0:
        applications.append("catalyst")

    # Superconductor candidate (very speculative): specific structure + elements
    sc_elements = {"Ba", "Cu", "La", "Y", "Sr", "Ca", "Bi", "Tl", "Hg", "Nb", "Ti"}
    has_sc_element = any(el.symbol in sc_elements for el in elements)
    if has_sc_element and has_oxygen and structure_type in ("perovskite", "ternary"):
        applications.append("superconductor_candidate")

    results["applications"] = applications
    results["num_applications"] = len(applications)

    # 9. Composite score
    # Weighted: stability (40%) + band gap usefulness (30%) + applications (20%) + novelty bonus (10%)
    stability_score = checks_passed / total_checks

    # Band gap usefulness: peaks at 1.4 eV (solar) and 2.5 eV (LED)
    bg_useful = max(
        math.exp(-((band_gap_est - 1.4) ** 2) / 0.5),  # Solar peak
        math.exp(-((band_gap_est - 2.5) ** 2) / 1.0),  # LED peak
        math.exp(-((band_gap_est - 0.5) ** 2) / 0.3),  # Thermoelectric peak
    )

    app_score = min(len(applications) / 3, 1.0)
    novelty_bonus = 0.1 if len(elements) >= 3 else 0.0

    composite = (0.4 * stability_score + 0.3 * bg_useful + 0.2 * app_score + novelty_bonus)
    results["composite_score"] = round(composite, 4)

    return results


def check_novelty(formula: str) -> dict:
    """Check if a material exists in the Materials Project database."""
    try:
        # Use Materials Project API (free, no key needed for basic search)
        encoded = urllib.parse.quote(formula)
        url = f"https://api.materialsproject.org/materials/summary/?formula={encoded}&_fields=material_id,formula_pretty,band_gap,formation_energy_per_atom&_limit=5"
        req = urllib.request.Request(url, headers={"User-Agent": "autolab/1.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())

        if data.get("data") and len(data["data"]) > 0:
            matches = data["data"]
            return {
                "novel": False,
                "matches": len(matches),
                "closest": matches[0] if matches else None,
                "database": "Materials Project"
            }
        else:
            return {"novel": True, "matches": 0, "database": "Materials Project"}
    except Exception as e:
        # If API fails, use formula hash as rough check
        return {"novel": "unknown", "error": str(e), "database": "Materials Project (failed)"}


def show_baselines():
    """Show known materials as baseline reference."""
    baselines = [
        {
            "name": "Silicon (solar cell standard)",
            "composition": {"Si": 1},
            "lattice": {"a": 5.43, "b": 5.43, "c": 5.43},
            "structure": "binary",
            "real_band_gap": 1.12,
            "real_application": "Solar cells, semiconductors"
        },
        {
            "name": "BaTiO3 (piezoelectric)",
            "composition": {"Ba": 1, "Ti": 1, "O": 3},
            "lattice": {"a": 4.01, "b": 4.01, "c": 4.01},
            "structure": "perovskite",
            "real_band_gap": 3.2,
            "real_application": "Capacitors, piezoelectrics"
        },
        {
            "name": "GaAs (solar/LED)",
            "composition": {"Ga": 1, "As": 1},
            "lattice": {"a": 5.65, "b": 5.65, "c": 5.65},
            "structure": "binary",
            "real_band_gap": 1.42,
            "real_application": "Solar cells, LEDs, lasers"
        },
        {
            "name": "TiO2 (photocatalyst)",
            "composition": {"Ti": 1, "O": 2},
            "lattice": {"a": 4.59, "b": 4.59, "c": 2.96},
            "structure": "binary",
            "real_band_gap": 3.2,
            "real_application": "Photocatalysis, sunscreen"
        },
        {
            "name": "CsPbI3 (perovskite solar)",
            "composition": {"Cs": 1, "Pb": 1, "I": 3},
            "lattice": {"a": 6.29, "b": 6.29, "c": 6.29},
            "structure": "perovskite",
            "real_band_gap": 1.73,
            "real_application": "Next-gen solar cells"
        }
    ]

    print("=" * 80)
    print("BASELINE MATERIALS")
    print("=" * 80)

    for b in baselines:
        result = evaluate_material(b["composition"], b["lattice"], b["structure"])
        print(f"\n--- {b['name']} ---")
        print(f"  Formula: {result.get('formula', 'N/A')}")
        print(f"  Band gap (estimated): {result.get('band_gap_eV', 'N/A')} eV (real: {b['real_band_gap']} eV)")
        print(f"  Density: {result.get('density_gcm3', 'N/A')} g/cm³")
        print(f"  Formation energy: {result.get('formation_energy_eV', 'N/A')} eV")
        print(f"  Checks: {result.get('checks_passed', 0)}/{result.get('total_checks', 5)}")
        print(f"  Applications: {', '.join(result.get('applications', []))}")
        print(f"  Real application: {b['real_application']}")
        print(f"  Composite score: {result.get('composite_score', 0)}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python prepare.py [evaluate|novelty|baseline]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "baseline":
        show_baselines()

    elif command == "evaluate":
        # Import current material from material.py
        sys.path.insert(0, ".")
        from material import MATERIALS

        print("=" * 80)
        print(f"EVALUATING {len(MATERIALS)} MATERIALS")
        print("=" * 80)

        for i, mat in enumerate(MATERIALS):
            result = evaluate_material(
                mat["composition"],
                mat["lattice"],
                mat["structure_type"]
            )
            print(f"\n--- Material {i+1}: {result.get('formula', 'Unknown')} ({mat.get('name', 'unnamed')}) ---")
            for k, v in sorted(result.items()):
                print(f"  {k}: {v}")

    elif command == "novelty":
        sys.path.insert(0, ".")
        from material import MATERIALS

        print("=" * 80)
        print("NOVELTY CHECK")
        print("=" * 80)

        for mat in MATERIALS:
            from pymatgen.core import Composition
            comp = Composition(mat["composition"])
            formula = comp.reduced_formula
            result = check_novelty(formula)
            status = "NOVEL" if result.get("novel") == True else "KNOWN" if result.get("novel") == False else "UNKNOWN"
            print(f"\n{formula}: {status}")
            if result.get("matches"):
                print(f"  Found {result['matches']} matches in {result['database']}")
            if result.get("error"):
                print(f"  Note: {result['error']}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
