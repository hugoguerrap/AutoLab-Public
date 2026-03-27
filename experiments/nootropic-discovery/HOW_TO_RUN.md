# nootropic-discovery

Autonomous discovery of novel cognitive enhancer scaffolds using the Karpathy Loop.

**Domain:** CNS pharmacology / computational drug design
**Inspired by:** Wager et al. (2010) CNS MPO paper + racetam literature
**Toolchain:** Python + RDKit (no GPU needed)

---

## What This Experiment Does

Optimizes small molecules for **CNS penetration + cognitive pharmacophore match** simultaneously:

| Metric | Why It Matters |
|--------|----------------|
| BBB Score | Drug must cross blood-brain barrier to work |
| CNS MPO | Pfizer's proven filter for oral CNS candidates |
| QED | General drug-likeness (absorption, toxicity) |
| Cogn. Pharm | Structural similarity to known nootropic scaffolds |

**Baseline to beat:** Modafinil (0.8162) — current champion among known nootropics
**Target:** composite ≥ 0.85, PAINS CLEAN, not found in PubChem (novel molecule)

---

## How to Run

```bash
cd autolab
claude --dangerously-skip-permissions
```

### Prompt — Standard Run

```
Read experiments/nootropic-discovery/program.md and execute the optimization loop.
Beat Donepezil (composite ~0.70) by discovering novel CNS-penetrating cognitive enhancer
scaffolds. Start with baseline evaluation, then explore racetam derivatives (Phase 1),
xanthine hybrids (Phase 2), and novel bicyclic scaffolds (Phase 3). Optimize for BBB
penetration above all else (weight 30%). Log everything to results.tsv. Check novelty
on PubChem for any molecule scoring > 0.75. Render the champion molecule.
```

### Prompt — Fast Explore (skip baselines, go straight to Phase 2)

```
Read experiments/nootropic-discovery/program.md. Skip Phase 1 baselines — Donepezil
is the bar at composite ~0.70. Jump directly to Phase 2 xanthine hybrids and Phase 3
novel scaffolds. Focus on minimizing TPSA below 60 and HBD to 0-1. Target composite
≥ 0.82. Log everything, check PubChem novelty on any molecule > 0.76.
```

### Prompt — Resume After Interruption

```
Read experiments/nootropic-discovery/program.md and results.tsv. Check the last entry
in results.tsv to see where we left off. Resume the optimization loop from there.
Current champion is in molecule.py BEST_SMILES. Keep going until composite ≥ 0.85
or 5 consecutive rounds without improvement.
```

### Prompt — Focused Sprint on One Scaffold

```
Read experiments/nootropic-discovery/program.md. The current best scaffold is
[INSERT SMILES]. Run a focused sprint: systematically apply every Phase 4 optimization
(fluorine scan, N-methylation, ring swap: phenyl→pyridine, amide→dimethylamide).
Evaluate all variants, keep best, log everything to results.tsv.
```

---

## Files

| File | Role | Modifiable? |
|------|------|-------------|
| `prepare.py` | Frozen evaluator — defines the metric | ❌ NEVER |
| `molecule.py` | Current candidates + champion | ✅ ONLY this one |
| `program.md` | Loop instructions + phase strategy | ❌ Reference only |
| `METRICS.md` | Frozen success criteria | ❌ Frozen |
| `results.tsv` | Append-only experiment log | ✅ Append only |
| `renders/` | Molecule visualizations | ✅ Output |

---

## Verify Baselines Before Running

```bash
cd experiments/nootropic-discovery
python prepare.py baseline
```

Scores verificados (2026-03-24):

| Molecule | Composite | Note |
|----------|-----------|------|
| Caffeine | 0.6477 | Xanthine baseline |
| Donepezil | 0.6663 | AChE inhibitor |
| Piracetam | 0.7170 | Racetam prototype |
| Aniracetam | 0.7218 | AMPA modulator |
| **Modafinil** | **0.8162** | **Current champion — beat this** |

Target: novel molecule ≥ 0.85 (not in PubChem)

---

## Key Chemical Insight

The single highest-leverage move is eliminating hydrogen bond donors (HBD):
- `NC(=O)...` → `CN(C)C(=O)...` drops HBD by 1, raises BBB significantly
- Every HBD costs ~5 Å² of TPSA — two HBD reductions can push TPSA below 60

Start there. Then worry about the pharmacophore ring.

---

## Related Papers

- Wager T.T. et al. (2010). *Moving beyond rules: The development of a CNS multiparameter optimization (MPO) scoring function.* ACS Chem. Neurosci.
- Clark D.E. (1999). *Rapid calculation of polar molecular surface area and its application to the prediction of transport phenomena.* J. Pharm. Sci.
- Winblad B. (2005). *Piracetam: A review of pharmacological properties and clinical uses.* CNS Drug Reviews.
- Malykh A.G. & Sadaie M.R. (2010). *Piracetam and piracetam-like drugs.* Drugs.
