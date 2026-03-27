"""
Drug Discovery - Evaluation & Utilities (FROZEN - DO NOT MODIFY)
================================================================
This file defines how molecules are evaluated. The optimizer (Claude)
can only modify molecule.py. This file is the frozen truth.
"""

import json
import sys
import urllib.request
import urllib.parse
from rdkit import Chem
from rdkit.Chem import Descriptors, QED, Draw, AllChem, FilterCatalog
from rdkit.Chem.FilterCatalog import FilterCatalogParams

# Suppress RDKit warnings
from rdkit import RDLogger
RDLogger.logger().setLevel(RDLogger.ERROR)


def evaluate_molecule(smiles: str) -> dict:
    """Evaluate a molecule's drug-likeness properties.

    Returns dict with all metrics or None if invalid.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    # Sanitize
    try:
        Chem.SanitizeMol(mol)
    except:
        return None

    # Core properties
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hbd = Descriptors.NumHDonors(mol)
    hba = Descriptors.NumHAcceptors(mol)
    tpsa = Descriptors.TPSA(mol)
    rotatable = Descriptors.NumRotatableBonds(mol)
    rings = Descriptors.RingCount(mol)
    heavy_atoms = mol.GetNumHeavyAtoms()
    qed_score = QED.qed(mol)

    # Lipinski's Rule of 5
    lipinski_violations = 0
    if mw > 500: lipinski_violations += 1
    if logp > 5: lipinski_violations += 1
    if hbd > 5: lipinski_violations += 1
    if hba > 10: lipinski_violations += 1
    lipinski_pass = lipinski_violations <= 1

    # PAINS filter (pan-assay interference compounds)
    params = FilterCatalogParams()
    params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
    catalog = FilterCatalog.FilterCatalog(params)
    pains_clean = not catalog.HasMatch(mol)

    # Veber rules (oral bioavailability)
    veber_pass = tpsa <= 140 and rotatable <= 10

    # Synthetic accessibility (1=easy, 10=hard)
    from rdkit.Chem import RDConfig
    import os
    sys.path.append(os.path.join(RDConfig.RDContribDir, 'SA_Score'))
    try:
        import sascorer
        sa_score = sascorer.calculateScore(mol)
    except:
        sa_score = 5.0  # default middle value

    # Composite score: weighted combination
    # QED (0-1) is the primary metric
    # Bonuses for: Lipinski pass, PAINS clean, Veber pass, low SA
    composite = qed_score
    if lipinski_pass: composite += 0.05
    if pains_clean: composite += 0.05
    if veber_pass: composite += 0.03
    if sa_score < 4: composite += 0.02
    composite = min(composite, 1.0)

    return {
        "smiles": smiles,
        "canonical_smiles": Chem.MolToSmiles(mol),
        "qed": round(qed_score, 4),
        "composite_score": round(composite, 4),
        "mw": round(mw, 1),
        "logp": round(logp, 2),
        "hbd": hbd,
        "hba": hba,
        "tpsa": round(tpsa, 1),
        "rotatable_bonds": rotatable,
        "rings": rings,
        "heavy_atoms": heavy_atoms,
        "lipinski_pass": lipinski_pass,
        "lipinski_violations": lipinski_violations,
        "pains_clean": pains_clean,
        "veber_pass": veber_pass,
        "sa_score": round(sa_score, 2),
    }


def check_novelty_pubchem(smiles: str) -> dict:
    """Check if a molecule exists in PubChem database.

    Returns dict with: found (bool), cid (int or None), name (str or None)
    """
    try:
        encoded = urllib.parse.quote(smiles, safe='')
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{encoded}/property/IUPACName,MolecularFormula/JSON"
        req = urllib.request.Request(url, headers={"User-Agent": "autolab-drug-discovery/1.0"})
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read())
        props = data["PropertyTable"]["Properties"][0]
        return {
            "found": True,
            "cid": props.get("CID"),
            "name": props.get("IUPACName", "unknown"),
            "formula": props.get("MolecularFormula", "")
        }
    except:
        return {"found": False, "cid": None, "name": None, "formula": None}


def render_molecule(smiles: str, filepath: str, size=(400, 300)):
    """Render a molecule to a PNG image."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return False
    AllChem.Compute2DCoords(mol)
    Draw.MolToFile(mol, filepath, size=size)
    return True


def compare_molecules(smiles1: str, smiles2: str) -> float:
    """Calculate Tanimoto similarity between two molecules (0-1)."""
    mol1 = Chem.MolFromSmiles(smiles1)
    mol2 = Chem.MolFromSmiles(smiles2)
    if mol1 is None or mol2 is None:
        return 0.0
    fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 2, nBits=2048)
    fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 2, nBits=2048)
    from rdkit import DataStructs
    return DataStructs.TanimotoSimilarity(fp1, fp2)


# --- CLI interface for the optimizer ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python prepare.py evaluate <SMILES>")
        print("  python prepare.py novelty <SMILES>")
        print("  python prepare.py render <SMILES> <filepath>")
        print("  python prepare.py compare <SMILES1> <SMILES2>")
        print("  python prepare.py batch <file_with_smiles>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "evaluate" and len(sys.argv) >= 3:
        result = evaluate_molecule(sys.argv[2])
        if result:
            print(json.dumps(result, indent=2))
        else:
            print("ERROR: Invalid molecule")
            sys.exit(1)

    elif cmd == "novelty" and len(sys.argv) >= 3:
        result = check_novelty_pubchem(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif cmd == "render" and len(sys.argv) >= 4:
        ok = render_molecule(sys.argv[2], sys.argv[3])
        print("OK" if ok else "ERROR")

    elif cmd == "compare" and len(sys.argv) >= 4:
        sim = compare_molecules(sys.argv[2], sys.argv[3])
        print(f"Tanimoto similarity: {sim:.4f}")

    elif cmd == "batch" and len(sys.argv) >= 3:
        with open(sys.argv[2]) as f:
            for line in f:
                smi = line.strip()
                if smi:
                    result = evaluate_molecule(smi)
                    if result:
                        print(f"{result['canonical_smiles']}\t{result['qed']}\t{result['composite_score']}\t{result['mw']}\t{'PASS' if result['lipinski_pass'] else 'FAIL'}\t{'CLEAN' if result['pains_clean'] else 'PAINS'}")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
