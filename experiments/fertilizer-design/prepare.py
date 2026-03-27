"""
Fertilizer Design — Evaluation Engine (FROZEN)
================================================
DO NOT MODIFY THIS FILE. This is the frozen evaluation function.
Claude modifies molecule.py; this file scores the results.

Evaluates candidate fertilizer molecules on:
1. Nitrogen content (% by mass)
2. Water solubility (predicted via RDKit descriptors + empirical model)
3. Slow-release potential (molecular weight + LogP + H-bond network)
4. Biodegradability (structural indicators)
5. Environmental safety (nitrogen runoff risk)
6. Cost estimate (based on atomic composition)
7. Synthesizability (SA Score)
8. Novelty (PubChem check)
"""

import sys
import json
import math
import time
import urllib.request
import urllib.parse
from datetime import datetime

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, QED, rdMolDescriptors, AllChem
    from rdkit.Chem import Draw, RDConfig
    import os, importlib.util
    # Load SA Score from Contrib
    sa_path = os.path.join(RDConfig.RDContribDir, 'SA_Score', 'sascorer.py')
    spec = importlib.util.spec_from_file_location("sascorer", sa_path)
    sascorer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sascorer)
    from rdkit import RDLogger
    RDLogger.logger().setLevel(RDLogger.ERROR)
except ImportError:
    print("ERROR: RDKit required. Install with: pip install rdkit")
    sys.exit(1)


# ============================================================
# SCORING FUNCTIONS
# ============================================================

def calculate_n_content(mol):
    """Calculate nitrogen content as percentage of molecular weight."""
    formula = rdMolDescriptors.CalcMolFormula(mol)
    mw = Descriptors.MolWt(mol)
    n_count = sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() == 7)
    n_mass = n_count * 14.007
    return (n_mass / mw) * 100 if mw > 0 else 0


def calculate_p_content(mol):
    """Calculate phosphorus content as percentage."""
    mw = Descriptors.MolWt(mol)
    p_count = sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() == 15)
    p_mass = p_count * 30.974
    return (p_mass / mw) * 100 if mw > 0 else 0


def calculate_k_content(mol):
    """Calculate potassium content as percentage."""
    mw = Descriptors.MolWt(mol)
    k_count = sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() == 19)
    k_mass = k_count * 39.098
    return (k_mass / mw) * 100 if mw > 0 else 0


def predict_solubility_score(mol):
    """
    Predict water solubility score (0-1) using RDKit descriptors.
    Based on empirical correlation: high TPSA + low LogP + H-bond donors = more soluble.
    Fertilizers need moderate-to-high solubility (but not too high for slow-release).
    """
    logp = Descriptors.MolLogP(mol)
    tpsa = Descriptors.TPSA(mol)
    hbd = Descriptors.NumHDonors(mol)
    mw = Descriptors.MolWt(mol)

    # Solubility estimate (log scale, g/L approximation)
    # Based on Yalkowsky-Valvani type correlation
    log_sol = 0.5 - 0.01 * mw - 0.5 * logp + 0.005 * tpsa + 0.1 * hbd

    # For fertilizers, we want MODERATE solubility (not too fast, not too slow)
    # Ideal: 50-500 g/L range (log_sol ~1.7-2.7)
    # Urea is extremely soluble (1080 g/L) — we want slower
    if log_sol > 2.7:
        score = max(0, 1.0 - (log_sol - 2.7) * 0.3)  # Penalty for too soluble
    elif log_sol < 0.5:
        score = max(0, log_sol / 0.5 * 0.5)  # Penalty for too insoluble
    else:
        score = 0.5 + (log_sol - 0.5) / (2.7 - 0.5) * 0.5  # Linear scale in ideal range

    return min(1.0, max(0.0, score))


def calculate_slow_release_score(mol):
    """
    Estimate slow-release potential (0-1).
    Higher MW, more H-bonds, moderate LogP = slower dissolution.
    Presence of amide/urea groups = natural slow-release mechanism.
    """
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hba = Descriptors.NumHAcceptors(mol)
    hbd = Descriptors.NumHDonors(mol)
    rot_bonds = Descriptors.NumRotatableBonds(mol)
    rings = Descriptors.RingCount(mol)

    score = 0.0

    # Higher MW = slower dissolution (up to a point)
    if 100 <= mw <= 500:
        score += min(0.25, (mw - 60) / 440 * 0.25)  # Urea is 60

    # Moderate LogP (slightly hydrophobic = slower water penetration)
    if 0 <= logp <= 3:
        score += 0.20
    elif -1 <= logp < 0:
        score += 0.10

    # H-bond network (more bonds = more crystal stability)
    hb_score = min(0.20, (hba + hbd) / 10 * 0.20)
    score += hb_score

    # Amide/urea groups (natural slow-release)
    smiles = Chem.MolToSmiles(mol)
    if 'NC(=O)N' in smiles or 'NC(N)=O' in smiles:  # Urea linkage
        score += 0.15
    elif 'C(=O)N' in smiles or 'NC=O' in smiles:  # Amide
        score += 0.10

    # Rings add stability
    if rings >= 1:
        score += min(0.10, rings * 0.05)

    # Penalty for very small molecules (dissolve too fast)
    if mw < 80:
        score *= 0.5

    return min(1.0, max(0.0, score))


def calculate_biodegradability_score(mol):
    """
    Estimate biodegradability (0-1).
    Based on structural indicators:
    - C, H, N, O atoms only = likely biodegradable
    - Ester/amide bonds = hydrolyzable
    - No halides, heavy metals, or persistent rings
    """
    score = 0.5  # Start neutral

    atoms = set(atom.GetAtomicNum() for atom in mol.GetAtoms())

    # Bonus for bio-friendly atoms only
    bio_atoms = {1, 6, 7, 8, 15, 16}  # H, C, N, O, P, S
    if atoms.issubset(bio_atoms):
        score += 0.25

    # Penalty for halogens
    halogens = {9, 17, 35, 53}  # F, Cl, Br, I
    if atoms & halogens:
        score -= 0.2

    # Bonus for hydrolyzable bonds (ester, amide)
    smiles = Chem.MolToSmiles(mol)
    if 'C(=O)O' in smiles:  # Ester
        score += 0.10
    if 'C(=O)N' in smiles:  # Amide
        score += 0.10

    # Penalty for aromatic rings (slower to degrade)
    aromatic_rings = Descriptors.NumAromaticRings(mol)
    score -= aromatic_rings * 0.1

    # Bonus for small molecules (easier to degrade)
    mw = Descriptors.MolWt(mol)
    if mw < 300:
        score += 0.10

    return min(1.0, max(0.0, score))


def calculate_environmental_score(mol):
    """
    Environmental safety score (0-1).
    Lower runoff risk = higher score.
    Based on LogP (lipophilicity), volatility, and N-content.
    """
    logp = Descriptors.MolLogP(mol)
    mw = Descriptors.MolWt(mol)
    n_pct = calculate_n_content(mol)

    score = 0.5

    # LogP: moderate is best (not too water-soluble = less runoff, not too hydrophobic = not persistent)
    if 0 <= logp <= 2:
        score += 0.20
    elif -1 <= logp < 0 or 2 < logp <= 4:
        score += 0.10
    else:
        score -= 0.10

    # Higher MW = less volatile = less NH3 loss
    if mw > 100:
        score += 0.15
    elif mw > 150:
        score += 0.20

    # N content: more than urea (46%) is suspicious — too much N per molecule = runoff risk
    if n_pct > 46:
        score -= 0.15
    elif n_pct > 30:
        score += 0.05
    elif n_pct > 15:
        score += 0.10

    return min(1.0, max(0.0, score))


def estimate_cost_score(mol):
    """
    Rough cost estimate (0-1) based on atomic composition.
    Common atoms (C, H, N, O) = cheap. Rare atoms = expensive.
    """
    atom_cost = {
        1: 1.0,   # H — very cheap
        6: 0.9,   # C — cheap
        7: 0.85,  # N — moderate (Haber-Bosch)
        8: 0.95,  # O — cheap
        15: 0.7,  # P — moderate (phosphate rock)
        16: 0.8,  # S — cheap
        19: 0.6,  # K — moderate (potash)
        9: 0.5,   # F — expensive
        17: 0.7,  # Cl — cheap
        20: 0.8,  # Ca — cheap
        26: 0.75, # Fe — cheap
        30: 0.6,  # Zn — moderate
        25: 0.65, # Mn — moderate
        29: 0.5,  # Cu — moderate
        5: 0.6,   # B — moderate
    }

    total_cost = 0
    n_atoms = 0
    for atom in mol.GetAtoms():
        anum = atom.GetAtomicNum()
        total_cost += atom_cost.get(anum, 0.3)  # Unknown atoms are expensive
        n_atoms += 1

    avg_cost = total_cost / n_atoms if n_atoms > 0 else 0

    # Penalty for large molecules (more material per unit nutrient)
    mw = Descriptors.MolWt(mol)
    n_pct = calculate_n_content(mol)
    if n_pct > 0:
        cost_per_n = mw / (n_pct / 100)  # Mass per unit N
        # Urea: 60 / 0.46 = 130. Lower is better.
        efficiency_penalty = min(0.3, max(0, (cost_per_n - 130) / 500))
        avg_cost -= efficiency_penalty

    return min(1.0, max(0.0, avg_cost))


def calculate_sa_score(mol):
    """Synthesizability score (1-10, lower=easier). Normalize to 0-1."""
    sa = sascorer.calculateScore(mol)
    # SA score: 1 = easy, 10 = hard. Normalize: 1→1.0, 5→0.5, 10→0.0
    return max(0.0, (10 - sa) / 9)


def check_pubchem_novelty(smiles, timeout=10):
    """Check if molecule exists in PubChem. Returns 'novel', 'known', or 'error'."""
    try:
        mol = Chem.MolFromSmiles(smiles)
        canonical = Chem.MolToSmiles(mol)
        encoded = urllib.parse.quote(canonical, safe='')
        url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{encoded}/cids/JSON'
        req = urllib.request.Request(url, headers={'User-Agent': 'autolab-fertilizer/1.0'})
        resp = urllib.request.urlopen(req, timeout=timeout)
        data = json.loads(resp.read())
        cids = data.get('IdentifierList', {}).get('CID', [])
        if cids and cids[0] != 0:
            return 'known'
        return 'novel'
    except Exception as e:
        if '404' in str(e) or 'NotFound' in str(e):
            return 'novel'
        return 'error'


def evaluate(smiles):
    """
    Full evaluation of a fertilizer candidate.
    Returns dict with all metrics and composite score.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": f"Invalid SMILES: {smiles}", "composite_score": 0}

    # Sanitize
    try:
        Chem.SanitizeMol(mol)
    except:
        return {"error": f"Cannot sanitize: {smiles}", "composite_score": 0}

    # Calculate all metrics
    n_content = calculate_n_content(mol)
    p_content = calculate_p_content(mol)
    k_content = calculate_k_content(mol)
    total_nutrient = n_content + p_content + k_content

    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)

    solubility = predict_solubility_score(mol)
    slow_release = calculate_slow_release_score(mol)
    biodegradability = calculate_biodegradability_score(mol)
    environmental = calculate_environmental_score(mol)
    cost = estimate_cost_score(mol)
    sa = calculate_sa_score(mol)

    # Must have nitrogen (primary nutrient for most fertilizers)
    if n_content < 5:
        nutrient_score = 0.2  # Heavy penalty — not useful as N-fertilizer
    elif n_content >= 46:
        nutrient_score = 0.9  # As good as urea
    elif n_content >= 30:
        nutrient_score = 0.8
    elif n_content >= 20:
        nutrient_score = 0.7
    elif n_content >= 10:
        nutrient_score = 0.5
    else:
        nutrient_score = 0.3

    # Composite score (weighted)
    composite = (
        nutrient_score * 0.20 +       # Must carry nitrogen
        slow_release * 0.25 +          # KEY differentiator from urea
        solubility * 0.10 +            # Moderate solubility
        biodegradability * 0.15 +      # EU 2026 compliance
        environmental * 0.10 +         # Less runoff
        cost * 0.10 +                  # Economically viable
        sa * 0.10                      # Can be synthesized
    )

    # Bonus for slow-release + high N (the holy grail)
    if slow_release > 0.6 and n_content > 20:
        composite = min(1.0, composite + 0.05)

    # Bonus for biodegradable + slow-release (EU compliant)
    if biodegradability > 0.7 and slow_release > 0.5:
        composite = min(1.0, composite + 0.03)

    return {
        "smiles": smiles,
        "formula": rdMolDescriptors.CalcMolFormula(mol),
        "mw": round(mw, 1),
        "n_content_pct": round(n_content, 2),
        "p_content_pct": round(p_content, 2),
        "k_content_pct": round(k_content, 2),
        "total_nutrient_pct": round(total_nutrient, 2),
        "logp": round(logp, 2),
        "solubility_score": round(solubility, 4),
        "slow_release_score": round(slow_release, 4),
        "biodegradability_score": round(biodegradability, 4),
        "environmental_score": round(environmental, 4),
        "cost_score": round(cost, 4),
        "sa_score": round(sa, 4),
        "nutrient_score": round(nutrient_score, 4),
        "composite_score": round(composite, 4),
    }


def render_molecule(smiles, filename):
    """Render molecule to PNG image."""
    mol = Chem.MolFromSmiles(smiles)
    if mol:
        AllChem.Compute2DCoords(mol)
        Draw.MolToFile(mol, filename, size=(400, 300))
        return True
    return False


# ============================================================
# CLI INTERFACE
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python prepare.py evaluate <SMILES>")
        print("  python prepare.py novelty <SMILES>")
        print("  python prepare.py render <SMILES> <output.png>")
        print("  python prepare.py baseline")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "evaluate":
        smiles = sys.argv[2]
        result = evaluate(smiles)
        for k, v in result.items():
            print(f"  {k}: {v}")

    elif cmd == "novelty":
        smiles = sys.argv[2]
        status = check_pubchem_novelty(smiles)
        print(f"  PubChem: {status}")

    elif cmd == "render":
        smiles = sys.argv[2]
        output = sys.argv[3] if len(sys.argv) > 3 else "molecule.png"
        ok = render_molecule(smiles, output)
        print(f"  Rendered: {ok} -> {output}")

    elif cmd == "baseline":
        print("=== FERTILIZER BASELINES ===\n")
        baselines = [
            ("Urea", "NC(N)=O"),
            ("Biuret", "NC(=O)NC(N)=O"),
            ("Methyleneurea (CDU)", "O=CNC(=O)NC=O"),
            ("Isobutylidene diurea (IBDU)", "CC(C)/C=N/C(=O)NC(=O)N/N=C(/C)C"),
            ("Urea-formaldehyde (UF dimer)", "O=CNCCNC=O"),
            ("Glycine", "NCC(=O)O"),
            ("Ammonium carbamate", "NC(=O)[O-].[NH4+]"),
        ]
        for name, smi in baselines:
            result = evaluate(smi)
            if "error" not in result:
                print(f"{name} ({smi})")
                print(f"  N: {result['n_content_pct']}%  MW: {result['mw']}  "
                      f"SlowRel: {result['slow_release_score']:.3f}  "
                      f"Biodeg: {result['biodegradability_score']:.3f}  "
                      f"Composite: {result['composite_score']:.4f}")
                print()
            else:
                print(f"{name}: {result['error']}\n")
