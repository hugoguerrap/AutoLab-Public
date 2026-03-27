"""
Antibiotic Discovery — Evaluation Engine (FROZEN)
===================================================
DO NOT MODIFY THIS FILE. This is the frozen evaluation function.
Claude modifies molecule.py; this file scores the results.

Evaluates candidate antibiotic molecules on:
1. Antibacterial drug profile (MW, LogP, HBD/HBA tuned for antibiotics)
2. Gram-negative permeability (Hergenrother eNTRy rules)
3. Structural novelty vs known antibiotic classes
4. General drug-likeness (QED, PAINS, Lipinski)
5. Synthesizability (SA Score)
6. Membrane disruption potential (amphiphilic properties)
7. Novelty (PubChem check)

Based on:
- Stokes et al. 2020 (Halicin discovery, MIT)
- Richter et al. 2017 (eNTRy rules for gram-negative permeability)
- O'Shea & Moser 2008 (antibacterial property space)
"""

import sys
import json
import math
import urllib.request
import urllib.parse

try:
    from rdkit import Chem
    from rdkit.Chem import (
        Descriptors, QED, AllChem, Draw, FilterCatalog,
        rdMolDescriptors, Fragments, rdmolops
    )
    from rdkit.Chem.FilterCatalog import FilterCatalogParams
    from rdkit import DataStructs, RDLogger
    RDLogger.logger().setLevel(RDLogger.ERROR)

    # SA Score
    from rdkit.Chem import RDConfig
    import os, importlib.util
    sa_path = os.path.join(RDConfig.RDContribDir, 'SA_Score', 'sascorer.py')
    spec = importlib.util.spec_from_file_location("sascorer", sa_path)
    sascorer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sascorer)
except ImportError:
    print("ERROR: RDKit required. Install with: pip install rdkit")
    sys.exit(1)


# ============================================================
# KNOWN ANTIBIOTIC CLASSES (for novelty scoring)
# ============================================================

KNOWN_ANTIBIOTICS = {
    # Beta-lactams (HIGH RESISTANCE — penalize similarity)
    "penicillin_G": "CC1([C@@H](N2[C@H](S1)[C@@H](C2=O)NC(=O)Cc3ccccc3)C(=O)O)C",
    "amoxicillin": "CC1([C@@H](N2[C@H](S1)[C@@H](C2=O)NC(=O)[C@@H](c3ccc(O)cc3)N)C(=O)O)C",
    "cephalexin": "CC1=C(N2[C@@H](SC1)[C@@H](C2=O)NC(=O)[C@@H](c3ccccc3)N)C(=O)O",
    "meropenem": "C[C@@H]1[C@@H]2[C@H](C(=O)N2C(=C1S[C@H]3C[C@@H](NC3)C(=O)N(C)C)C(=O)[O-])C",
    "ceftriaxone": "CO/N=C(\\C(=O)N[C@@H]1C(=O)N2C(C(=O)[O-])=C(CSc3nc(=O)c(O)nn3C)CS[C@@H]12)c1csc(N)n1",
    "ampicillin": "CC1(C)S[C@@H]2[C@H](NC(=O)[C@@H](N)c3ccccc3)C(=O)N2[C@@H]1C(=O)O",

    # Fluoroquinolones (HIGH RESISTANCE — penalize similarity)
    "ciprofloxacin": "O=C(O)c1cn(C2CC2)c2cc(N3CCNCC3)c(F)cc2c1=O",
    "levofloxacin": "C[C@H]1COc2c(N3CCN(C)CC3)c(F)cc3c(=O)c(C(=O)O)cn1c23",
    "moxifloxacin": "OC(=O)c1cn(c2cc(N3C[C@H]4CNCC[C@@H]4C3)c(F)cc2c1=O)C1CC1",
    "norfloxacin": "CCn1cc(C(=O)O)c(=O)c2cc(F)c(N3CCNCC3)cc21",
    "ofloxacin": "CC1COc2c(N3CCN(C)CC3)c(F)cc3c(=O)c(C(=O)O)cn1c23",

    # Tetracyclines
    "tetracycline": "C[C@@]1(O)C(=C(/O)C2=O)[C@H](O)C3CC4=CC(O)=CC(O)=C4[C@@H](N(C)C)[C@@H]3[C@@H]1O2",
    "doxycycline": "O=C1C(C(N)=O)=C(O)[C@]2(O)C[C@H]3C[C@H]4c5c(O)cccc5[C@@](O)(C)[C@@H]4[C@@H](N(C)C)[C@@H]3[C@H]2C1=O",
    "tigecycline": "CN(C)[C@H]1[C@@H]2C[C@H]3Cc4c(O)c(/N=C/N(C)C)c(O)c(O)c4[C@@]3(O)C(=O)C(C(N)=O)=C(O)[C@]2(O)CC1=O",

    # Macrolides
    "erythromycin": "CC[C@@H]1OC(=O)[C@H](C)[C@@H](O[C@H]2C[C@@](C)(OC)[C@@H](O)[C@H](C)O2)[C@H](C)[C@@H](O[C@@H]3O[C@H](C)C[C@@H]([C@H]3O)N(C)C)[C@](C)(O)C[C@@H](C)C(=O)[C@H](C)[C@@H](O)[C@]1(C)O",
    "azithromycin": "CC[C@@H]1OC(=O)[C@H](C)[C@@H](O[C@H]2C[C@@](C)(OC)[C@@H](O)[C@H](C)O2)[C@H](C)[C@@H](O[C@@H]3O[C@H](C)C[C@@H]([C@H]3O)N(C)C)[C@](C)(O)C[C@@H](C)C[C@@H](C)N(C)C[C@@H](C)[C@@H](O)[C@]1(C)O",

    # Aminoglycosides
    "gentamicin": "OC1[C@H](O[C@@H]2[C@@H](N)C[C@@H](N)[C@H](O)[C@@H]2O)O[C@H](CO)[C@@H](O)[C@@H]1NC",
    "tobramycin": "NC[C@@H]1OC(O[C@@H]2[C@@H](N)C[C@@H](N)[C@H](O)[C@@H]2O)[C@H](O)[C@@H](O)[C@@H]1O",
    "amikacin": "NCC[C@H](O)C(=O)N[C@@H]1C[C@H](N)[C@@H](O[C@@H]2OC(CO)=CC(N)[C@H]2O)[C@H](O)[C@@H]1O[C@H]1O[C@H](CN)[C@@H](O)[C@H](O)[C@H]1O",

    # Sulfonamides
    "sulfamethoxazole": "Cc1cc(NS(=O)(=O)c2ccc(N)cc2)no1",
    "sulfadiazine": "Nc1ccc(S(=O)(=O)Nc2ncccn2)cc1",

    # Oxazolidinones
    "linezolid": "O=C(NCC1=CC=C(N2CCOCC2)C(F)=C1)C1CCCO1",
    "tedizolid": "O=C1OCN1c1ccc(-c2ncc(-c3ccc(F)cn3)n2C)cc1",

    # Nitroimidazoles
    "metronidazole": "Cc1ncc([N+](=O)[O-])n1CCO",
    "tinidazole": "CCS(=O)(=O)CCn1c([N+](=O)[O-])cnc1C",

    # Nitrofurans
    "nitrofurantoin": "O=C1CN(/N=C/c2ccc([N+](=O)[O-])o2)C(=O)N1",
    "furazolidone": "O=C1OCC(=NNC2=CC=C([N+]([O-])=O)O2)N1",

    # Diaminopyrimidines
    "trimethoprim": "COc1cc(Cc2cnc(N)nc2N)cc(OC)c1OC",
    "pyrimethamine": "CCc1nc(N)nc(N)c1-c1ccc(Cl)cc1",

    # Polymyxins / Lipopeptides
    "colistin_fragment": "CCCCCC(=O)NC(CC(N)=O)C(=O)NC(CCN)C(=O)NC(CC(N)=O)C(=O)O",
    "daptomycin_fragment": "CCCCCCCCCC(=O)NC(CC(=O)O)C(=O)NC(CC1=CNC2=CC=CC=C21)C(=O)O",

    # Rifamycins
    "rifampicin_core": "CC(=O)OC1C(O)=C2C(=O)C3(OC2c2c(C)cc(O)c(O)c21)OC(C)=CC3=O",

    # Glycopeptides (simplified)
    "vancomycin_fragment": "OC(=O)C(NC(=O)C(CC(N)=O)NC=O)Cc1ccc(Oc2cc(Cl)cc(O)c2)cc1",

    # Novel (recent discoveries — benchmarks)
    "halicin": "NC1=NC(=CS1)C1=CSC(=N1)N",
    "abaucin": "N#Cc1ccc(NC(=O)Nc2ccc(OC(F)(F)F)cc2)cc1",
    "teixobactin_fragment": "CC(C)C(NC(=O)C(CC(C)C)NC(=O)C(N)CO)C(=O)NC(C(=O)O)C(C)CC",
    "clovibactin_fragment": "CC(C)CC(NC(=O)C(CC(=O)O)NC(=O)C(N)CCCCN)C(=O)O",

    # Pleuromutilins
    "lefamulin": "CC(=O)OC1CC2(C)C(CC(=O)C2CO)C2CC(CSCCN3CCCC3)C(=C)C12",

    # Siderophore-conjugates
    "cefiderocol_fragment": "Nc1nc(Cl)c(Cc2cccc(O)c2O)s1",
}

# Classes with HIGH resistance — extra penalty for similarity
HIGH_RESISTANCE_CLASSES = {
    "penicillin_G", "amoxicillin", "cephalexin", "meropenem", "ceftriaxone", "ampicillin",
    "ciprofloxacin", "levofloxacin", "moxifloxacin", "norfloxacin", "ofloxacin",
}

# Pre-compute fingerprints for known antibiotics
KNOWN_FPS = {}
for name, smi in KNOWN_ANTIBIOTICS.items():
    mol = Chem.MolFromSmiles(smi)
    if mol:
        KNOWN_FPS[name] = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)


# ============================================================
# SCORING FUNCTIONS
# ============================================================

def calculate_antibacterial_profile(mol):
    """
    Score based on antibacterial drug property space.
    Antibiotics differ from typical drugs:
    - Higher MW tolerated (200-800 vs 150-500 for general drugs)
    - More polar (higher TPSA, more HBD/HBA)
    - More nitrogen atoms
    - More rigid (fewer rotatable bonds relative to size)

    Based on O'Shea & Moser 2008 and analysis of approved antibiotics.
    """
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hbd = Descriptors.NumHDonors(mol)
    hba = Descriptors.NumHAcceptors(mol)
    tpsa = Descriptors.TPSA(mol)
    rot_bonds = Descriptors.NumRotatableBonds(mol)
    n_count = sum(1 for a in mol.GetAtoms() if a.GetAtomicNum() == 7)
    rings = Descriptors.RingCount(mol)
    aromatic_rings = Descriptors.NumAromaticRings(mol)

    score = 0.0

    # MW: antibiotics sweet spot 250-600 (wider than general drugs)
    if 250 <= mw <= 600:
        score += 0.20
    elif 200 <= mw < 250 or 600 < mw <= 800:
        score += 0.10
    else:
        score += 0.0

    # LogP: antibiotics tend to be -2 to 4 (more polar tolerated)
    if -1 <= logp <= 3:
        score += 0.20  # Sweet spot
    elif -2 <= logp < -1 or 3 < logp <= 5:
        score += 0.10
    else:
        score += 0.0

    # Nitrogen count: antibiotics are nitrogen-rich
    if n_count >= 3:
        score += 0.15
    elif n_count >= 2:
        score += 0.10
    elif n_count >= 1:
        score += 0.05

    # TPSA: moderate-high for membrane interaction (60-180)
    if 60 <= tpsa <= 180:
        score += 0.15
    elif 40 <= tpsa < 60 or 180 < tpsa <= 220:
        score += 0.08

    # Rings: 2-5 is typical for antibiotics
    if 2 <= rings <= 5:
        score += 0.10
    elif rings == 1 or rings == 6:
        score += 0.05

    # At least one aromatic ring (pharmacophore anchor)
    if aromatic_rings >= 1:
        score += 0.10

    # HBD: 1-5 for antibiotics (more than general drugs)
    if 1 <= hbd <= 5:
        score += 0.05

    # HBA: 3-10 (more acceptors = more target interactions)
    if 3 <= hba <= 10:
        score += 0.05

    return min(1.0, score)


def calculate_gram_negative_score(mol):
    """
    Gram-negative permeability prediction based on Hergenrother's eNTRy rules (2017):
    1. Primary amine (ionizable, helps cross outer membrane porins)
    2. Low globularity (elongated shape penetrates porins better)
    3. Amphiphilicity (balance of polar and non-polar surfaces)
    4. Rigidity (fewer rotatable bonds relative to heavy atoms)

    Gram-negative bacteria (E. coli, Klebsiella, Pseudomonas) are the hardest targets.
    """
    smiles = Chem.MolToSmiles(mol)
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    tpsa = Descriptors.TPSA(mol)
    rot_bonds = Descriptors.NumRotatableBonds(mol)
    heavy_atoms = mol.GetNumHeavyAtoms()
    hbd = Descriptors.NumHDonors(mol)

    score = 0.0

    # Rule 1: Primary amine (NH2 group — most important for porin entry)
    has_primary_amine = False
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 7:  # Nitrogen
            # Check if it has at least 2 hydrogens and is not in a ring
            total_h = atom.GetTotalNumHs()
            if total_h >= 2 and not atom.IsInRing():
                has_primary_amine = True
                break
            # Also check for aromatic amine (like aniline)
            if total_h >= 2 and atom.GetIsAromatic():
                has_primary_amine = True
                break

    if has_primary_amine:
        score += 0.30  # Critical for gram-negative entry

    # Also accept secondary amine with some credit
    has_secondary_amine = False
    if not has_primary_amine:
        for atom in mol.GetAtoms():
            if atom.GetAtomicNum() == 7 and atom.GetTotalNumHs() >= 1:
                has_secondary_amine = True
                break
        if has_secondary_amine:
            score += 0.15

    # Rule 2: Low globularity (approximated by aspect ratio of molecular shape)
    # Proxy: ratio of rotatable bonds to heavy atoms (lower = more rigid/elongated)
    if heavy_atoms > 0:
        flexibility = rot_bonds / heavy_atoms
        if flexibility < 0.3:
            score += 0.20  # Rigid, good for porin entry
        elif flexibility < 0.5:
            score += 0.10
        else:
            score += 0.0  # Too floppy

    # Rule 3: Amphiphilicity (balance of LogP and TPSA)
    # Want moderate: not too hydrophobic, not too hydrophilic
    if 0 <= logp <= 2 and 60 <= tpsa <= 150:
        score += 0.20  # Good amphiphilic balance
    elif -1 <= logp <= 3 and 40 <= tpsa <= 180:
        score += 0.10

    # Rule 4: Size constraint (porins have size limits ~600 Da)
    if mw <= 600:
        score += 0.15
    elif mw <= 800:
        score += 0.05

    # Bonus: multiple ionizable groups (helps accumulation inside bacteria)
    ionizable_n = sum(1 for a in mol.GetAtoms()
                      if a.GetAtomicNum() == 7 and a.GetTotalNumHs() >= 1)
    if ionizable_n >= 2:
        score += 0.10

    # Penalty: too lipophilic (accumulates in membrane, doesn't reach cytoplasm)
    if logp > 4:
        score -= 0.15

    return min(1.0, max(0.0, score))


def calculate_novelty_score(mol):
    """
    Structural novelty vs known antibiotic classes.
    Uses Tanimoto similarity with Morgan fingerprints against ~45 known antibiotics.

    Higher score = more different from ALL known antibiotic classes.
    We WANT novelty because known classes have resistance mechanisms.

    Extra penalty for similarity to HIGH RESISTANCE classes (beta-lactams, quinolones).

    Uses average similarity to top-3 most similar + max similarity for a more
    discriminating score than just max alone.
    """
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)

    similarities = []
    for name, known_fp in KNOWN_FPS.items():
        sim = DataStructs.TanimotoSimilarity(fp, known_fp)
        similarities.append((sim, name))

    similarities.sort(reverse=True)
    max_similarity = similarities[0][0]
    most_similar_class = similarities[0][1]

    # Average of top-3 most similar (more robust than just max)
    top3_avg = sum(s for s, _ in similarities[:3]) / min(3, len(similarities))

    # Base novelty from top-3 average (this discriminates better)
    # top3_avg < 0.15 = very novel, > 0.35 = too similar
    if top3_avg < 0.12:
        novelty = 1.0
    elif top3_avg < 0.18:
        novelty = 0.70 + (0.18 - top3_avg) * 5.0  # 0.70-1.0
    elif top3_avg < 0.25:
        novelty = 0.40 + (0.25 - top3_avg) * (0.30 / 0.07)  # 0.40-0.70
    elif top3_avg < 0.35:
        novelty = 0.15 + (0.35 - top3_avg) * 2.5  # 0.15-0.40
    else:
        novelty = max(0.0, 0.15 - (top3_avg - 0.35))

    # Extra penalty if most similar is a HIGH RESISTANCE class
    if most_similar_class in HIGH_RESISTANCE_CLASSES and max_similarity > 0.25:
        novelty *= 0.5  # Harsh penalty — we don't want anything close to these

    # Penalty for very high max similarity to ANY known antibiotic
    if max_similarity > 0.5:
        novelty *= 0.3  # Very similar to a known antibiotic
    elif max_similarity > 0.4:
        novelty *= 0.6

    return novelty, max_similarity, most_similar_class, top3_avg


def calculate_druglikeness_score(mol):
    """General drug-likeness: QED + Lipinski + PAINS + Veber."""
    qed_score = QED.qed(mol)

    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hbd = Descriptors.NumHDonors(mol)
    hba = Descriptors.NumHAcceptors(mol)
    tpsa = Descriptors.TPSA(mol)
    rot = Descriptors.NumRotatableBonds(mol)

    # Relaxed Lipinski for antibiotics (Rule of 5 is too strict)
    violations = 0
    if mw > 800: violations += 1  # Relaxed from 500
    if logp > 6: violations += 1  # Relaxed from 5
    if hbd > 7: violations += 1   # Relaxed from 5
    if hba > 12: violations += 1  # Relaxed from 10
    lipinski_pass = violations <= 1

    # PAINS filter
    params = FilterCatalogParams()
    params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
    catalog = FilterCatalog.FilterCatalog(params)
    pains_clean = not catalog.HasMatch(mol)

    # Veber (oral bioavailability)
    veber_pass = tpsa <= 180 and rot <= 12  # Relaxed for antibiotics

    score = qed_score * 0.5  # QED is part of the score
    if lipinski_pass: score += 0.20
    if pains_clean: score += 0.20
    if veber_pass: score += 0.10

    return min(1.0, score), qed_score, lipinski_pass, pains_clean, veber_pass


def calculate_sa_score(mol):
    """Synthesizability: 1=easy, 10=hard. Normalize to 0-1."""
    sa = sascorer.calculateScore(mol)
    return max(0.0, (10 - sa) / 9), sa


def calculate_membrane_disruption(mol):
    """
    Estimate membrane disruption potential.
    Based on amphiphilic moment: balance of hydrophobic and hydrophilic surfaces.
    Molecules that can insert into bacterial membranes are a distinct mechanism.
    """
    logp = Descriptors.MolLogP(mol)
    tpsa = Descriptors.TPSA(mol)
    mw = Descriptors.MolWt(mol)
    rings = Descriptors.RingCount(mol)
    aromatic = Descriptors.NumAromaticRings(mol)
    hbd = Descriptors.NumHDonors(mol)

    score = 0.0

    # Amphiphilic: needs both polar and nonpolar regions
    if 0.5 <= logp <= 4 and tpsa >= 40:
        score += 0.30

    # Cationic character (ionizable amines at physiological pH)
    basic_n = sum(1 for a in mol.GetAtoms()
                  if a.GetAtomicNum() == 7 and a.GetTotalNumHs() >= 1
                  and not a.GetIsAromatic())
    if basic_n >= 1:
        score += 0.25

    # Rigid aromatic core (can stack in membrane)
    if aromatic >= 1 and rings >= 2:
        score += 0.20

    # Size: not too small (needs to span membrane), not too big
    if 250 <= mw <= 500:
        score += 0.15

    # Multiple H-bond donors (can disrupt membrane packing)
    if 2 <= hbd <= 5:
        score += 0.10

    return min(1.0, score)


def check_nitrogen_heterocycle_and_amine(mol):
    """Check if molecule has both a nitrogen heterocycle and a primary amine."""
    has_n_heterocycle = False
    has_primary_amine = False

    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 7:
            if atom.IsInRing():
                has_n_heterocycle = True
            if atom.GetTotalNumHs() >= 2 and not atom.IsInRing():
                has_primary_amine = True

    return has_n_heterocycle and has_primary_amine


def check_pubchem_novelty(smiles, timeout=10):
    """Check if molecule exists in PubChem."""
    try:
        mol = Chem.MolFromSmiles(smiles)
        canonical = Chem.MolToSmiles(mol)
        encoded = urllib.parse.quote(canonical, safe='')
        url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{encoded}/cids/JSON'
        req = urllib.request.Request(url, headers={'User-Agent': 'autolab-antibiotic/1.0'})
        resp = urllib.request.urlopen(req, timeout=timeout)
        data = json.loads(resp.read())
        cids = data.get('IdentifierList', {}).get('CID', [])
        if cids and cids[0] != 0:
            return 'known', cids[0]
        return 'novel', 0
    except Exception as e:
        if '404' in str(e) or 'NotFound' in str(e):
            return 'novel', 0
        return 'error', 0


# ============================================================
# MAIN EVALUATION
# ============================================================

def evaluate(smiles):
    """Full evaluation of an antibiotic candidate."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": f"Invalid SMILES: {smiles}", "composite_score": 0}

    try:
        Chem.SanitizeMol(mol)
    except:
        return {"error": f"Cannot sanitize: {smiles}", "composite_score": 0}

    # Calculate all sub-scores
    antibacterial = calculate_antibacterial_profile(mol)
    gram_neg = calculate_gram_negative_score(mol)
    novelty, max_sim, most_similar, top3_avg = calculate_novelty_score(mol)
    druglike, qed, lipinski, pains, veber = calculate_druglikeness_score(mol)
    sa_norm, sa_raw = calculate_sa_score(mol)
    membrane = calculate_membrane_disruption(mol)

    # Composite score (weighted)
    composite = (
        antibacterial * 0.25 +   # Antibacterial property profile
        gram_neg * 0.20 +         # Gram-negative permeability
        novelty * 0.15 +          # Structural novelty vs known classes
        druglike * 0.15 +         # General drug-likeness
        sa_norm * 0.10 +          # Synthesizability
        membrane * 0.05            # Membrane disruption potential
    )

    # Bonus: novel gram-negative active (the holy grail)
    if gram_neg > 0.6 and novelty > 0.7:
        composite = min(1.0, composite + 0.05)

    # Bonus: nitrogen heterocycle + primary amine (dual mechanism)
    if check_nitrogen_heterocycle_and_amine(mol):
        composite = min(1.0, composite + 0.03)

    # Molecular properties for logging
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hbd = Descriptors.NumHDonors(mol)
    hba = Descriptors.NumHAcceptors(mol)
    tpsa = Descriptors.TPSA(mol)
    n_count = sum(1 for a in mol.GetAtoms() if a.GetAtomicNum() == 7)

    return {
        "smiles": smiles,
        "canonical_smiles": Chem.MolToSmiles(mol),
        "composite_score": round(composite, 4),
        "antibacterial_score": round(antibacterial, 4),
        "gram_neg_score": round(gram_neg, 4),
        "novelty_score": round(novelty, 4),
        "druglike_score": round(druglike, 4),
        "sa_score_norm": round(sa_norm, 4),
        "membrane_score": round(membrane, 4),
        "qed": round(qed, 4),
        "mw": round(mw, 1),
        "logp": round(logp, 2),
        "hbd": hbd,
        "hba": hba,
        "tpsa": round(tpsa, 1),
        "n_atoms": n_count,
        "lipinski_pass": lipinski,
        "pains_clean": pains,
        "veber_pass": veber,
        "sa_raw": round(sa_raw, 2),
        "max_similarity": round(max_sim, 4),
        "top3_avg_similarity": round(top3_avg, 4),
        "most_similar_to": most_similar,
    }


def render_molecule(smiles, filename):
    """Render molecule to PNG."""
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
        print("  python prepare.py compare <SMILES1> <SMILES2>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "evaluate":
        smiles = sys.argv[2]
        result = evaluate(smiles)
        for k, v in result.items():
            print(f"  {k}: {v}")

    elif cmd == "novelty":
        smiles = sys.argv[2]
        status, cid = check_pubchem_novelty(smiles)
        print(f"  PubChem: {status} (CID: {cid})")

    elif cmd == "render":
        smiles = sys.argv[2]
        output = sys.argv[3] if len(sys.argv) > 3 else "molecule.png"
        ok = render_molecule(smiles, output)
        print(f"  Rendered: {ok} -> {output}")

    elif cmd == "compare":
        smi1, smi2 = sys.argv[2], sys.argv[3]
        mol1, mol2 = Chem.MolFromSmiles(smi1), Chem.MolFromSmiles(smi2)
        if mol1 and mol2:
            fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 2, nBits=2048)
            fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 2, nBits=2048)
            sim = DataStructs.TanimotoSimilarity(fp1, fp2)
            print(f"  Tanimoto similarity: {sim:.4f}")

    elif cmd == "baseline":
        print("=== ANTIBIOTIC BASELINES ===\n")
        baselines = [
            ("Ciprofloxacin (fluoroquinolone)", "O=C(O)c1cn(C2CC2)c2cc(N3CCNCC3)c(F)cc2c1=O"),
            ("Halicin (MIT novel, 2020)", "NC1=NC(=CS1)C1=CSC(=N1)N"),
            ("Trimethoprim (diaminopyrimidine)", "COc1cc(Cc2cnc(N)nc2N)cc(OC)c1OC"),
            ("Linezolid (oxazolidinone)", "O=C(NCC1=CC=C(N2CCOCC2)C(F)=C1)C1CCCO1"),
            ("Sulfamethoxazole (sulfonamide)", "Cc1cc(NS(=O)(=O)c2ccc(N)cc2)no1"),
            ("Nitrofurantoin (nitrofuran)", "O=C1CN(/N=C/c2ccc([N+](=O)[O-])o2)C(=O)N1"),
            ("Metronidazole (nitroimidazole)", "Cc1ncc([N+](=O)[O-])n1CCO"),
        ]
        for name, smi in baselines:
            result = evaluate(smi)
            if "error" not in result:
                print(f"{name}")
                print(f"  SMILES: {smi}")
                print(f"  Composite: {result['composite_score']:.4f}  |  "
                      f"Antibacterial: {result['antibacterial_score']:.3f}  |  "
                      f"GramNeg: {result['gram_neg_score']:.3f}  |  "
                      f"Novelty: {result['novelty_score']:.3f}")
                print(f"  MW: {result['mw']}  LogP: {result['logp']}  N: {result['n_atoms']}  "
                      f"TPSA: {result['tpsa']}  SA: {result['sa_raw']}")
                print(f"  Most similar to: {result['most_similar_to']} "
                      f"(Tanimoto: {result['max_similarity']:.3f}, top3_avg: {result['top3_avg_similarity']:.3f})")
                print()
            else:
                print(f"{name}: {result['error']}\n")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
