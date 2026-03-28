#!/usr/bin/env python3
"""
FROZEN EVALUATOR — DO NOT MODIFY
Surfactant Design: Novel Biodegradable Detergent Molecules

Evaluates candidate surfactant molecules on cleaning potential,
environmental safety, and synthesizability using RDKit descriptors.

Usage:
    python prepare.py evaluate <smiles> [<smiles2> ...]
    python prepare.py baseline
    python prepare.py batch <file.py>
    python prepare.py compare <smiles1> <smiles2>
    python prepare.py render <smiles> <output.png>
"""

import sys
import json
import math
import importlib.util
import os

try:
    from rdkit import Chem, RDLogger
    from rdkit.Chem import Descriptors, rdMolDescriptors, AllChem, Draw
    from rdkit.Chem import Fragments
    from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams
except ImportError:
    print("ERROR: RDKit required. Install with: pip install rdkit")
    sys.exit(1)

# Suppress RDKit warnings
RDLogger.logger().setLevel(RDLogger.ERROR)

# ── Configuration ──────────────────────────────────────────────
# Optimal HLB range for detergents/heavy-duty cleaning
HLB_TARGET_LOW = 13.0
HLB_TARGET_HIGH = 15.0
HLB_TARGET_CENTER = 14.0

# Molecular weight bounds for practical surfactants
MW_MIN = 200
MW_MAX = 800

# Ideal LogP range for surfactants (need both polar and nonpolar character)
LOGP_MIN = 1.0
LOGP_MAX = 6.0
LOGP_IDEAL_CENTER = 3.5

# ── Known Surfactants Database ─────────────────────────────────
KNOWN_SURFACTANTS = {
    "SDS": {
        "smiles": "CCCCCCCCCCCCOS(=O)(=O)[O-].[Na+]",
        "name": "Sodium Dodecyl Sulfate",
        "hlb_lit": 40.0,
        "use": "benchmark anionic",
    },
    "Sodium_Stearate": {
        "smiles": "CCCCCCCCCCCCCCCCCC(=O)[O-].[Na+]",
        "name": "Sodium Stearate (soap)",
        "hlb_lit": 18.0,
        "use": "traditional soap",
    },
    "CTAB": {
        "smiles": "CCCCCCCCCCCCCCCC[N+](C)(C)C.[Br-]",
        "name": "Cetyltrimethylammonium Bromide",
        "hlb_lit": 10.0,
        "use": "cationic benchmark",
    },
    "CAPB": {
        "smiles": "CCCCCCCCCCCC(=O)NCCC[N+](C)(C)CC(=O)[O-]",
        "name": "Cocamidopropyl Betaine",
        "hlb_lit": 15.0,
        "use": "amphoteric, mild",
    },
    "Lauryl_Glucoside": {
        "smiles": "CCCCCCCCCCCCOC1OC(CO)C(O)C(O)C1O",
        "name": "Lauryl Glucoside",
        "hlb_lit": 13.6,
        "use": "nonionic, green",
    },
    "Sodium_Lauroyl_Sarcosinate": {
        "smiles": "CCCCCCCCCCCC(=O)N(C)CC(=O)[O-].[Na+]",
        "name": "Sodium Lauroyl Sarcosinate",
        "hlb_lit": 14.0,
        "use": "amino acid surfactant",
    },
    "Decyl_Glucoside": {
        "smiles": "CCCCCCCCCCOC1OC(CO)C(O)C(O)C1O",
        "name": "Decyl Glucoside",
        "hlb_lit": 14.5,
        "use": "nonionic, green",
    },
    "LAS": {
        "smiles": "CCCCCCCCCCCCc1ccc(S(=O)(=O)[O-])cc1.[Na+]",
        "name": "Linear Alkylbenzene Sulfonate",
        "hlb_lit": 11.7,
        "use": "anionic workhorse",
    },
}


# ── Helper Functions ───────────────────────────────────────────

def get_organic_fragment(mol):
    """Extract the largest organic fragment (strip counterions like Na+, Br-)."""
    frags = Chem.GetMolFrags(mol, asMols=True, sanitizeFrags=True)
    if not frags:
        return mol
    return max(frags, key=lambda m: m.GetNumHeavyAtoms())


def count_longest_carbon_chain(mol):
    """Estimate the longest continuous carbon chain length."""
    if mol is None:
        return 0
    # Find all carbon atoms
    carbon_idxs = [a.GetIdx() for a in mol.GetAtoms() if a.GetAtomicNum() == 6]
    if not carbon_idxs:
        return 0

    # BFS from each carbon to find longest carbon-only path
    max_chain = 0
    adj = {}
    for bond in mol.GetBonds():
        a1, a2 = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        if a1 in carbon_idxs and a2 in carbon_idxs:
            adj.setdefault(a1, []).append(a2)
            adj.setdefault(a2, []).append(a1)

    for start in carbon_idxs:
        visited = {start}
        stack = [(start, 1)]
        while stack:
            node, depth = stack.pop()
            max_chain = max(max_chain, depth)
            for nb in adj.get(node, []):
                if nb not in visited:
                    visited.add(nb)
                    stack.append((nb, depth + 1))
    return max_chain


def has_hydrophilic_head(mol):
    """Check for common hydrophilic head groups."""
    if mol is None:
        return False, []
    smarts_heads = {
        "sulfate": "[S](=O)(=O)[O-,OH]",
        "sulfonate": "[S](=O)(=O)[O-,OH]",
        "carboxylate": "[C](=O)[O-,OH]",
        "phosphate": "[P](=O)([O-,OH])([O-,OH])",
        "quaternary_N": "[N+]",
        "amine_oxide": "[N+]([O-])",
        "betaine": "[N+]([CH2][C](=O)[O-])",
        "polyol": "[OH].[OH]",
        "sugar": "[C]1[O][C]([CH2][OH])[C]([OH])[C]([OH])[C]1[OH]",
        "amide": "[C](=O)[NH,N]",
        "ether": "[C][O][C]",
        "hydroxyl": "[OH]",
    }
    found = []
    for name, smarts in smarts_heads.items():
        pat = Chem.MolFromSmarts(smarts)
        if pat and mol.HasSubstructMatch(pat):
            found.append(name)
    return len(found) > 0, found


def has_hydrophobic_tail(mol):
    """Check for adequate hydrophobic tail (alkyl chain >= 8 carbons)."""
    chain_len = count_longest_carbon_chain(mol)
    return chain_len >= 8, chain_len


# ── Scoring Functions ──────────────────────────────────────────

def calculate_amphiphilicity_score(mol):
    """
    Score how well the molecule is a surfactant (has both hydrophilic
    head and hydrophobic tail). 0.0 = not a surfactant, 1.0 = ideal.
    """
    has_head, head_groups = has_hydrophilic_head(mol)
    has_tail, chain_len = has_hydrophobic_tail(mol)

    score = 0.0

    # Head group scoring (0 to 0.5)
    if has_head:
        n_groups = len(head_groups)
        # More diverse head groups = better (up to a point)
        head_score = min(0.5, 0.2 + 0.1 * n_groups)
        score += head_score

    # Tail scoring (0 to 0.5)
    if has_tail:
        # Ideal chain length 10-14 carbons for detergents
        if 10 <= chain_len <= 14:
            tail_score = 0.5
        elif 8 <= chain_len < 10:
            tail_score = 0.3 + 0.1 * (chain_len - 8)
        elif 14 < chain_len <= 18:
            tail_score = 0.5 - 0.05 * (chain_len - 14)
        else:
            tail_score = 0.15
        score += tail_score

    return round(score, 4), head_groups, chain_len


def estimate_hlb(mol):
    """
    Estimate HLB (Hydrophilic-Lipophilic Balance) using Griffin's method
    adapted for computational estimation via TPSA and surface area.

    Returns HLB estimate (0-20 scale).
    """
    tpsa = Descriptors.TPSA(mol)
    labute_asa = Descriptors.LabuteASA(mol)

    if labute_asa <= 0:
        return 0.0

    # Griffin-inspired: HLB = 20 * (hydrophilic portion / total)
    # Use TPSA as proxy for hydrophilic surface
    hlb_raw = 20.0 * (tpsa / labute_asa)

    # Clamp to valid range
    return round(max(0.0, min(20.0, hlb_raw)), 2)


def calculate_hlb_score(hlb):
    """
    Score HLB proximity to detergent optimal range (13-15).
    Gaussian penalty for deviation from ideal.
    """
    if HLB_TARGET_LOW <= hlb <= HLB_TARGET_HIGH:
        return 1.0

    # Distance from nearest edge of optimal range
    if hlb < HLB_TARGET_LOW:
        dist = HLB_TARGET_LOW - hlb
    else:
        dist = hlb - HLB_TARGET_HIGH

    # Gaussian falloff (sigma=3 means score ~0.5 at 3 HLB units away)
    score = math.exp(-(dist ** 2) / (2 * 3.0 ** 2))
    return round(score, 4)


def estimate_log_cmc(mol):
    """
    Estimate log10(CMC in mM) using Klevens-type equation.
    Based on: log(CMC) = A - B * n_c
    where n_c is the effective carbon chain length.

    Lower CMC = more efficient surfactant.
    Returns log10(CMC in mM).
    """
    chain_len = count_longest_carbon_chain(mol)
    logp = Descriptors.MolLogP(mol)

    # Klevens approximation adapted for general surfactants
    # Ionic surfactants: log CMC ~ 1.6 - 0.29 * n_c
    # Nonionic surfactants: log CMC ~ 1.0 - 0.54 * n_c (per ethylene oxide)
    # We use a blended estimate based on LogP
    log_cmc = 2.0 - 0.28 * chain_len

    # Adjust for head group effects (polar head increases CMC)
    tpsa = Descriptors.TPSA(mol)
    if tpsa > 80:
        log_cmc += 0.3  # more polar head → higher CMC

    return round(log_cmc, 2)


def calculate_cmc_score(log_cmc):
    """
    Score CMC efficiency. Lower CMC is better.
    Optimal: log CMC < -1 (sub-millimolar)
    Good: log CMC -1 to 0
    Acceptable: log CMC 0 to 1
    Poor: log CMC > 1
    """
    if log_cmc <= -2.0:
        return 1.0
    elif log_cmc <= -1.0:
        return 0.9 + 0.1 * (-1.0 - log_cmc)
    elif log_cmc <= 0.0:
        return 0.7 + 0.2 * (0.0 - log_cmc)
    elif log_cmc <= 1.0:
        return 0.4 + 0.3 * (1.0 - log_cmc)
    elif log_cmc <= 2.0:
        return 0.1 + 0.3 * (2.0 - log_cmc)
    else:
        return 0.05


def calculate_biodegradability_score(mol):
    """
    Estimate biodegradability from structural features.
    Based on OECD 301 predictive rules.

    Favorable: linear chains, ester/amide bonds, hydroxyl groups
    Unfavorable: branching, halogens, quaternary carbons, aromatic rings, nitro groups
    """
    score = 0.5  # baseline

    # Count favorable features
    n_ester = len(mol.GetSubstructMatches(Chem.MolFromSmarts("[C](=O)[O][C]")))
    n_amide = len(mol.GetSubstructMatches(Chem.MolFromSmarts("[C](=O)[NH,N]")))
    n_hydroxyl = len(mol.GetSubstructMatches(Chem.MolFromSmarts("[OH]")))
    n_ether_linear = len(mol.GetSubstructMatches(Chem.MolFromSmarts("[CH2][O][CH2]")))

    score += 0.08 * min(n_ester, 3)       # ester bonds are hydrolyzable
    score += 0.06 * min(n_amide, 3)       # amide bonds are hydrolyzable
    score += 0.04 * min(n_hydroxyl, 4)    # hydroxyl aids microbial attack
    score += 0.03 * min(n_ether_linear, 3) # linear ethers are degradable

    # Count unfavorable features
    n_halogens = sum(1 for a in mol.GetAtoms() if a.GetAtomicNum() in [9, 17, 35, 53])
    n_aromatic = Descriptors.NumAromaticRings(mol)
    n_nitro = len(mol.GetSubstructMatches(Chem.MolFromSmarts("[N+](=O)[O-]")))
    n_quat_c = len(mol.GetSubstructMatches(Chem.MolFromSmarts("[CX4]([C])([C])([C])[C]")))

    # Branching penalty: count branch points
    n_branch = 0
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 6 and atom.GetDegree() >= 3:
            n_branch += 1

    score -= 0.15 * min(n_halogens, 3)    # halogens resist biodegradation
    score -= 0.08 * min(n_aromatic, 3)    # aromatics degrade slowly
    score -= 0.20 * min(n_nitro, 2)       # nitro groups are problematic
    score -= 0.06 * min(n_quat_c, 3)      # quaternary C blocks degradation
    score -= 0.02 * min(n_branch, 5)      # excessive branching

    # Linear alkyl chain bonus (primary structure of green surfactants)
    chain_len = count_longest_carbon_chain(mol)
    if chain_len >= 8:
        score += 0.10

    return round(max(0.0, min(1.0, score)), 4)


def calculate_aquatic_toxicity_score(mol):
    """
    Estimate aquatic safety from molecular properties.
    Based on ECOSAR-type QSAR models.

    Higher score = safer for aquatic life.
    """
    logp = Descriptors.MolLogP(mol)
    mw = Descriptors.MolWt(mol)

    # LogP-based toxicity estimation
    # LogP > 5: very bioaccumulative and toxic
    # LogP 3-5: moderate concern
    # LogP 1-3: generally safer
    # LogP < 1: low concern
    if logp <= 1.0:
        tox_score = 1.0
    elif logp <= 3.0:
        tox_score = 0.85 - 0.075 * (logp - 1.0)
    elif logp <= 5.0:
        tox_score = 0.70 - 0.20 * (logp - 3.0)
    elif logp <= 7.0:
        tox_score = 0.30 - 0.10 * (logp - 5.0)
    else:
        tox_score = 0.05

    # Halogen penalty (persistent organic pollutants)
    n_halogens = sum(1 for a in mol.GetAtoms() if a.GetAtomicNum() in [9, 17, 35, 53])
    tox_score -= 0.10 * min(n_halogens, 3)

    # Large MW molecules tend to be less acutely toxic (can't cross membranes)
    if mw > 500:
        tox_score += 0.05

    return round(max(0.0, min(1.0, tox_score)), 4)


def calculate_sa_score(mol):
    """
    Synthetic Accessibility score (1=easy to 10=hard).
    Normalized to 0-1 where 1.0 = easy to synthesize.
    """
    try:
        # RDKit's built-in SA score
        from rdkit.Chem import RDConfig
        sa_path = os.path.join(RDConfig.RDDataDir, 'FragmentDescriptors.csv')
        # Use a simplified SA estimation
        n_atoms = mol.GetNumHeavyAtoms()
        n_rings = Descriptors.RingCount(mol)
        n_stereo = rdMolDescriptors.CalcNumAtomStereoCenters(mol)
        n_spiro = rdMolDescriptors.CalcNumSpiroAtoms(mol)

        # Penalize complexity
        complexity = (
            0.5 * max(0, n_atoms - 20) / 20  # atom count penalty
            + 0.2 * max(0, n_rings - 2) / 3  # ring penalty
            + 0.15 * n_stereo / 3             # stereocenter penalty
            + 0.15 * n_spiro / 2              # spiro penalty
        )
        sa_norm = max(0.0, 1.0 - complexity)
        return round(sa_norm, 4)
    except Exception:
        return 0.5


def calculate_structural_validity(mol):
    """
    Check if molecule is structurally valid as a surfactant.
    Returns score and list of issues.
    """
    issues = []
    score = 1.0

    mw = Descriptors.MolWt(mol)
    if mw < MW_MIN:
        issues.append(f"MW too low ({mw:.0f} < {MW_MIN})")
        score -= 0.3
    if mw > MW_MAX:
        issues.append(f"MW too high ({mw:.0f} > {MW_MAX})")
        score -= 0.3

    logp = Descriptors.MolLogP(mol)
    if logp < LOGP_MIN:
        issues.append(f"LogP too low ({logp:.1f}), no hydrophobic character")
        score -= 0.2
    if logp > LOGP_MAX + 2:
        issues.append(f"LogP too high ({logp:.1f}), insoluble")
        score -= 0.3

    n_heavy = mol.GetNumHeavyAtoms()
    if n_heavy < 12:
        issues.append(f"Too few atoms ({n_heavy}), not a viable surfactant")
        score -= 0.3
    if n_heavy > 80:
        issues.append(f"Too many atoms ({n_heavy}), impractical")
        score -= 0.2

    return round(max(0.0, score), 4), issues


# ── Main Evaluation ────────────────────────────────────────────

def evaluate_molecule(smiles):
    """
    Evaluate a single SMILES string as a surfactant candidate.
    Returns a dict with all metrics and composite score.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": f"Invalid SMILES: {smiles}", "composite_score": 0.0}

    # Get the organic fragment (strip counterions)
    organic = get_organic_fragment(mol)

    # Basic descriptors
    mw = round(Descriptors.MolWt(organic), 2)
    logp = round(Descriptors.MolLogP(organic), 2)
    tpsa = round(Descriptors.TPSA(organic), 2)
    hbd = Descriptors.NumHDonors(organic)
    hba = Descriptors.NumHAcceptors(organic)
    n_rotatable = Descriptors.NumRotatableBonds(organic)

    # Surfactant-specific metrics
    amphi_score, head_groups, chain_len = calculate_amphiphilicity_score(organic)
    hlb = estimate_hlb(organic)
    hlb_score = calculate_hlb_score(hlb)
    log_cmc = estimate_log_cmc(organic)
    cmc_score = calculate_cmc_score(log_cmc)
    biodeg_score = calculate_biodegradability_score(organic)
    aquatic_score = calculate_aquatic_toxicity_score(organic)
    sa_score = calculate_sa_score(organic)
    validity_score, validity_issues = calculate_structural_validity(organic)

    # ── Composite Score ────────────────────────────────────
    # Weighted combination of all metrics
    composite = (
        0.20 * amphi_score       # Must be a surfactant
        + 0.20 * hlb_score       # HLB in detergent range
        + 0.15 * cmc_score       # Efficient micelle formation
        + 0.20 * biodeg_score    # Environmentally degradable
        + 0.15 * aquatic_score   # Safe for waterways
        + 0.10 * sa_score        # Practical to synthesize
    )

    # Validity gate: if not structurally valid, penalize hard
    composite *= validity_score

    # ── Bonuses ────────────────────────────────────────────
    # Green surfactant bonus: biodegradable + low toxicity
    if biodeg_score >= 0.7 and aquatic_score >= 0.7:
        composite += 0.03

    # Sweet spot bonus: good HLB + low CMC
    if hlb_score >= 0.8 and cmc_score >= 0.7:
        composite += 0.02

    # Amphiphilic excellence: strong head + good tail
    if amphi_score >= 0.8:
        composite += 0.02

    # Cap at 1.0
    composite = round(min(1.0, composite), 4)

    return {
        "smiles": smiles,
        "composite_score": composite,
        "amphiphilicity": amphi_score,
        "head_groups": head_groups,
        "chain_length": chain_len,
        "hlb": hlb,
        "hlb_score": hlb_score,
        "log_cmc": log_cmc,
        "cmc_score": cmc_score,
        "biodegradability": biodeg_score,
        "aquatic_safety": aquatic_score,
        "sa_score": sa_score,
        "validity_score": validity_score,
        "validity_issues": validity_issues,
        "mw": mw,
        "logp": logp,
        "tpsa": tpsa,
        "hbd": hbd,
        "hba": hba,
        "rotatable_bonds": n_rotatable,
    }


def check_novelty(smiles):
    """Check if molecule exists in PubChem."""
    try:
        import urllib.request
        import urllib.parse
        encoded = urllib.parse.quote(smiles, safe="")
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{encoded}/cids/JSON"
        req = urllib.request.Request(url, headers={"User-Agent": "AutoLab/1.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        cids = data.get("IdentifierList", {}).get("CID", [])
        if cids and cids[0] != 0:
            return {"novel": False, "cid": cids[0]}
        return {"novel": True, "cid": 0}
    except Exception:
        return {"novel": True, "cid": 0, "note": "PubChem unreachable, assumed novel"}


# ── CLI Interface ──────────────────────────────────────────────

def print_result(result):
    """Pretty-print evaluation result."""
    if "error" in result:
        print(f"ERROR: {result['error']}")
        return

    print(f"\n{'='*60}")
    print(f"  SMILES:          {result['smiles']}")
    print(f"  Composite Score: {result['composite_score']:.4f}")
    print(f"{'='*60}")
    print(f"  Amphiphilicity:  {result['amphiphilicity']:.4f}  (head: {', '.join(result['head_groups']) or 'none'}, chain: C{result['chain_length']})")
    print(f"  HLB:             {result['hlb']:.2f}  (score: {result['hlb_score']:.4f}, target: {HLB_TARGET_LOW}-{HLB_TARGET_HIGH})")
    print(f"  log(CMC):        {result['log_cmc']:.2f}  (score: {result['cmc_score']:.4f})")
    print(f"  Biodegradability:{result['biodegradability']:.4f}")
    print(f"  Aquatic Safety:  {result['aquatic_safety']:.4f}")
    print(f"  Synthesizability:{result['sa_score']:.4f}")
    print(f"  Validity:        {result['validity_score']:.4f}  {result['validity_issues'] or '(ok)'}")
    print(f"  ────────────────────────────────────")
    print(f"  MW: {result['mw']}  LogP: {result['logp']}  TPSA: {result['tpsa']}")
    print(f"  HBD: {result['hbd']}  HBA: {result['hba']}  RotBonds: {result['rotatable_bonds']}")
    print()


def run_baseline():
    """Evaluate all known surfactant baselines."""
    print("\n" + "=" * 70)
    print("  SURFACTANT DESIGN — BASELINE EVALUATION")
    print("=" * 70)

    results = []
    for name, info in KNOWN_SURFACTANTS.items():
        result = evaluate_molecule(info["smiles"])
        result["name"] = name
        result["use"] = info["use"]
        results.append(result)

    # Sort by composite score
    results.sort(key=lambda x: x["composite_score"], reverse=True)

    print(f"\n{'Name':<30} {'Composite':>9} {'Amphi':>6} {'HLB':>5} {'HLBsc':>6} {'CMCsc':>6} {'Biodeg':>6} {'Aquatic':>7} {'SA':>5}")
    print("-" * 110)
    for r in results:
        print(
            f"{r['name']:<30} {r['composite_score']:>9.4f} "
            f"{r['amphiphilicity']:>6.3f} {r['hlb']:>5.1f} {r['hlb_score']:>6.3f} "
            f"{r['cmc_score']:>6.3f} {r['biodegradability']:>6.3f} "
            f"{r['aquatic_safety']:>7.3f} {r['sa_score']:>5.3f}"
        )

    print(f"\nBest baseline: {results[0]['name']} = {results[0]['composite_score']:.4f}")
    print(f"Target: composite_score > 0.85 (novel biodegradable detergent)")
    return results


def run_batch(module_path):
    """Evaluate all candidates from a Python module."""
    spec = importlib.util.spec_from_file_location("candidates", module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    best_smiles = getattr(mod, "BEST_SMILES", None)
    candidates = getattr(mod, "CANDIDATES", [])

    all_smiles = []
    if best_smiles:
        all_smiles.append(("BEST", best_smiles))
    for c in candidates:
        if isinstance(c, dict):
            all_smiles.append((c.get("name", "candidate"), c["smiles"]))
        elif isinstance(c, str):
            all_smiles.append(("candidate", c))

    results = []
    for name, smi in all_smiles:
        r = evaluate_molecule(smi)
        r["label"] = name
        results.append(r)
        print_result(r)

    if results:
        best = max(results, key=lambda x: x["composite_score"])
        print(f"\n>>> BEST: {best['label']} = {best['composite_score']:.4f} ({best['smiles']})")
    return results


def render_molecule(smiles, output_path):
    """Render molecule to PNG."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        print(f"ERROR: Invalid SMILES: {smiles}")
        return
    img = Draw.MolToImage(mol, size=(600, 400))
    img.save(output_path)
    print(f"Rendered to {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python prepare.py [evaluate|baseline|batch|compare|render|novelty] ...")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "baseline":
        run_baseline()

    elif cmd == "evaluate":
        if len(sys.argv) < 3:
            print("Usage: python prepare.py evaluate <smiles> [<smiles2> ...]")
            sys.exit(1)
        for smi in sys.argv[2:]:
            result = evaluate_molecule(smi)
            print_result(result)
            print(json.dumps(result, indent=2, default=str))

    elif cmd == "batch":
        if len(sys.argv) < 3:
            print("Usage: python prepare.py batch <module.py>")
            sys.exit(1)
        run_batch(sys.argv[2])

    elif cmd == "compare":
        if len(sys.argv) < 4:
            print("Usage: python prepare.py compare <smiles1> <smiles2>")
            sys.exit(1)
        r1 = evaluate_molecule(sys.argv[2])
        r2 = evaluate_molecule(sys.argv[3])
        print_result(r1)
        print_result(r2)
        diff = r1["composite_score"] - r2["composite_score"]
        winner = "FIRST" if diff > 0 else "SECOND" if diff < 0 else "TIE"
        print(f">>> {winner} wins by {abs(diff):.4f}")

    elif cmd == "novelty":
        if len(sys.argv) < 3:
            print("Usage: python prepare.py novelty <smiles>")
            sys.exit(1)
        result = check_novelty(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif cmd == "render":
        if len(sys.argv) < 4:
            print("Usage: python prepare.py render <smiles> <output.png>")
            sys.exit(1)
        render_molecule(sys.argv[2], sys.argv[3])

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: evaluate, baseline, batch, compare, render, novelty")
        sys.exit(1)


if __name__ == "__main__":
    main()
