#!/usr/bin/env python3
"""
nootropic-discovery — Frozen Evaluator (DO NOT MODIFY)
=======================================================
Evaluate molecules for cognitive enhancement potential using CNS-specific metrics.

Usage:
    python prepare.py baseline              # Show known nootropic baselines + scores
    python prepare.py evaluate <SMILES>     # Evaluate a single molecule
    python prepare.py novelty  <SMILES>     # Check PubChem novelty
    python prepare.py render   <SMILES> <outfile.png>   # Render molecule
    python prepare.py batch    <s1> <s2>... # Evaluate multiple, print best

Composite formula (FROZEN):
    composite = 0.25 * QED + 0.30 * BBB + 0.25 * CNS_MPO + 0.20 * cogn_pharm
"""

import sys
import json
import urllib.request
import urllib.parse

from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, QED
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

RDLogger.logger().setLevel(RDLogger.ERROR)

# ── FROZEN WEIGHTS ─────────────────────────────────────────────────────────────
WEIGHTS = {"qed": 0.25, "bbb": 0.30, "cns_mpo": 0.25, "cogn_pharm": 0.20}
TARGET  = 0.80   # composite score to beat

# ── BASELINES ──────────────────────────────────────────────────────────────────
BASELINES = {
    "Caffeine":    ("Cn1cnc2c1c(=O)n(C)c(=O)n2C",          "Xanthine — baseline stimulant"),
    "Piracetam":   ("NC(=O)CN1CCCC1=O",                     "Racetam — prototype nootropic"),
    "Aniracetam":  ("O=C1CCN1CC(=O)c1ccccc1",               "Racetam — AMPA modulator"),
    "Modafinil":   ("NC(=O)CS(=O)C(c1ccccc1)c1ccccc1",      "Wakefulness agent, high QED"),
    "Donepezil":   ("COc1cc2c(cc1OC)C(=O)CC2CC1CCN(Cc2ccccc2)CC1",
                                                             "AChE inhibitor — hardest baseline"),
}

# ── CNS PHARMACOPHORE SMARTS ────────────────────────────────────────────────────
# Each entry: (name, SMARTS, score_contribution)
COGN_PHARMACOPHORES = [
    ("pyrrolidone",   "O=C1CCCN1",         0.35),   # 2-pyrrolidone = racetam core
    ("piperidine",    "C1CCNCC1",           0.20),   # donepezil scaffold
    ("indolyl",       "c1ccc2[nH]ccc2c1",  0.25),   # indole (tryptamine family)
    ("imidazolyl",    "c1cn[nH]c1",        0.15),   # imidazole
    ("benzimidazole", "c1ccc2[nH]cnc2c1",  0.20),   # benzimidazole — CNS friendly
    ("xanthine_core", "O=C1NC(=O)c2ncnc21", 0.20),  # xanthine/purine core
    ("lactam_5",      "O=C1CCNC1",         0.10),   # 5-membered lactam variant
]


# ── SCORING FUNCTIONS ──────────────────────────────────────────────────────────

def score_bbb(mol):
    """Blood-brain barrier penetration (Clark's CNS rules).
    Optimal: logP 1-3.5, TPSA < 60 Å², MW < 350, HBD ≤ 2
    """
    logp = Descriptors.MolLogP(mol)
    tpsa = Descriptors.TPSA(mol)
    mw   = Descriptors.MolWt(mol)
    hbd  = Descriptors.NumHDonors(mol)

    s_logp = 1.0 if 1.0 <= logp <= 3.5 else max(0.0, 1 - abs(logp - 2.25) / 2.5)
    s_tpsa = 1.0 if tpsa <= 60         else max(0.0, 1 - (tpsa - 60) / 70)
    s_mw   = 1.0 if mw   <= 350        else max(0.0, 1 - (mw - 350) / 200)
    s_hbd  = 1.0 if hbd  <= 2          else max(0.0, 1 - (hbd - 2) / 3)

    return round((s_logp + s_tpsa + s_mw + s_hbd) / 4, 4)


def score_cns_mpo(mol):
    """Pfizer CNS MPO: 6 desirability criteria (Wager et al. 2010).
    Each criterion scores 0 or 1, total normalized to 0-1.
    """
    logp = Descriptors.MolLogP(mol)
    mw   = Descriptors.MolWt(mol)
    tpsa = Descriptors.TPSA(mol)
    hbd  = Descriptors.NumHDonors(mol)

    score = 0.0
    score += 1.0 if logp <= 5.0 else 0.0
    score += 1.0 if logp <= 4.0 else 0.5   # extra credit for logP ≤ 4
    score += 1.0 if mw   <= 360 else 0.0
    score += 1.0 if tpsa <= 90  else 0.0
    score += 1.0 if hbd  <= 3   else 0.0
    score += 1.0 if hbd  <= 1   else 0.5   # extra credit for very low HBD

    return round(min(1.0, score / 6.0), 4)


def score_cogn_pharm(mol):
    """Match known cognitive-enhancer pharmacophores via SMARTS."""
    base = 0.20
    score = base
    for name, smarts, weight in COGN_PHARMACOPHORES:
        try:
            patt = Chem.MolFromSmarts(smarts)
            if patt and mol.HasSubstructMatch(patt):
                score += weight
        except Exception:
            pass
    return round(min(1.0, score), 4)


def check_pains(mol):
    params = FilterCatalogParams()
    params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
    catalog = FilterCatalog(params)
    return "CLEAN" if not catalog.HasMatch(mol) else "PAINS"


# ── EVALUATE ───────────────────────────────────────────────────────────────────

def evaluate(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": f"Invalid SMILES: {smiles}"}
    try:
        Chem.SanitizeMol(mol)
    except Exception as e:
        return {"error": f"Sanitization failed: {e}"}

    qed   = round(QED.qed(mol), 4)
    bbb   = score_bbb(mol)
    mpo   = score_cns_mpo(mol)
    pharm = score_cogn_pharm(mol)
    pains = check_pains(mol)

    mw   = round(Descriptors.MolWt(mol), 1)
    logp = round(Descriptors.MolLogP(mol), 3)
    tpsa = round(Descriptors.TPSA(mol), 1)
    hbd  = Descriptors.NumHDonors(mol)
    hba  = Descriptors.NumHAcceptors(mol)

    composite = round(
        WEIGHTS["qed"]       * qed   +
        WEIGHTS["bbb"]       * bbb   +
        WEIGHTS["cns_mpo"]   * mpo   +
        WEIGHTS["cogn_pharm"]* pharm,
        4
    )

    return {
        "smiles":          smiles,
        "mw":              mw,
        "logp":            logp,
        "tpsa":            tpsa,
        "hbd":             hbd,
        "hba":             hba,
        "qed":             qed,
        "bbb_score":       bbb,
        "cns_mpo":         mpo,
        "cogn_pharm":      pharm,
        "pains":           pains,
        "composite_score": composite,
        "beats_target":    composite >= TARGET,
    }


# ── NOVELTY ────────────────────────────────────────────────────────────────────

def check_novelty(smiles):
    encoded = urllib.parse.quote(smiles, safe="")
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{encoded}/cids/JSON"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
            cids = data.get("IdentifierList", {}).get("CID", [])
            return {"found": True, "pubchem_cids": cids, "novel": False, "count": len(cids)}
    except Exception as e:
        if "404" in str(e) or "NotFound" in str(e):
            return {"found": False, "novel": True, "note": "Not in PubChem ✓"}
        return {"error": str(e), "note": "Network error — verify manually at pubchem.ncbi.nlm.nih.gov"}


# ── RENDER ─────────────────────────────────────────────────────────────────────

def render(smiles, outfile):
    try:
        from rdkit.Chem import Draw
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            print(f"ERROR: Invalid SMILES"); return
        img = Draw.MolToImage(mol, size=(400, 300))
        img.save(outfile)
        print(f"Saved: {outfile}")
    except ImportError:
        print("ERROR: Pillow not installed. Run: pip install Pillow")


# ── BASELINE ───────────────────────────────────────────────────────────────────

def show_baselines():
    print("=" * 72)
    print("nootropic-discovery — Known Nootropic Baselines")
    print("=" * 72)
    scores = []
    for name, (smiles, note) in BASELINES.items():
        r = evaluate(smiles)
        if "error" in r:
            print(f"\n{name}: ERROR — {r['error']}")
            continue
        scores.append((name, r))
        print(f"\n{name}  ({note})")
        print(f"  SMILES : {smiles}")
        print(f"  MW={r['mw']}  logP={r['logp']}  TPSA={r['tpsa']}  HBD={r['hbd']}")
        print(f"  QED={r['qed']}  BBB={r['bbb_score']}  CNS-MPO={r['cns_mpo']}  Pharm={r['cogn_pharm']}")
        print(f"  PAINS: {r['pains']}")
        bar = "★" * int(r['composite_score'] * 20)
        print(f"  COMPOSITE: {r['composite_score']}  {bar}")

    print(f"\n{'─'*72}")
    print(f"TARGET: composite ≥ {TARGET}  (beat Donepezil ~0.70)")
    best = max(scores, key=lambda x: x[1]['composite_score'])
    print(f"BEST BASELINE: {best[0]} — {best[1]['composite_score']}")
    print("=" * 72)


# ── MAIN ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "baseline":
        show_baselines()

    elif cmd == "evaluate" and len(sys.argv) >= 3:
        result = evaluate(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif cmd == "novelty" and len(sys.argv) >= 3:
        result = check_novelty(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif cmd == "render" and len(sys.argv) >= 4:
        render(sys.argv[2], sys.argv[3])

    elif cmd == "batch" and len(sys.argv) >= 3:
        smiles_list = sys.argv[2:]
        results = []
        for s in smiles_list:
            r = evaluate(s)
            results.append(r)
            if "error" in r:
                print(f"  ✗ ERROR — {r['error']}  [{s[:50]}]")
            else:
                mark = "✓" if r["beats_target"] else "·"
                print(f"  {mark} composite={r['composite_score']} | bbb={r['bbb_score']} | mpo={r['cns_mpo']} | pharm={r['cogn_pharm']} | {s}")
        valid = [r for r in results if "error" not in r]
        if valid:
            best = max(valid, key=lambda x: x["composite_score"])
            print(f"\n  BEST THIS ROUND: composite={best['composite_score']} | pains={best['pains']}")
            print(f"  SMILES: {best['smiles']}")
    else:
        print(f"Unknown command or missing args: {sys.argv[1:]}")
        print(__doc__)
        sys.exit(1)
