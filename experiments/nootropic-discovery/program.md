# Nootropic Discovery — Optimization Loop

## Objective

Discover novel cognitive enhancer molecules that **beat Donepezil** (composite ~0.70) on CNS drug-likeness:

- Blood-brain barrier penetrating: TPSA < 60 Å², logP 1-3.5, MW < 350, HBD ≤ 2
- CNS-optimized (Pfizer MPO ≥ 0.70)
- Drug-like (QED ≥ 0.70)
- Known nootropic pharmacophore (pyrrolidone, xanthine, indole, piperidine, benzimidazole)
- **Not found in PubChem** (genuinely novel)
- **Composite score ≥ 0.80**

## The Loop

For each experiment:

1. **Read** `molecule.py` — check BEST_SMILES, BEST_COMPOSITE, current HYPOTHESIS and CANDIDATES
2. **Hypothesize** — what structural modification improves BBB or cogn_pharm the most?
3. **Modify** `molecule.py` — update HYPOTHESIS string + CANDIDATES list with new SMILES
4. **Evaluate** — run `python prepare.py batch <SMILES1> <SMILES2> ...`
5. **Record** — append ALL results to `results.tsv` (even failures)
6. **Judge:**
   - `composite > BEST_COMPOSITE` → commit and update BEST_SMILES:
     ```
     git add molecule.py results.tsv
     git commit -m "exp N: [description] — composite X.XXXX, bbb=X.XX"
     ```
   - `composite ≤ BEST_COMPOSITE` → revert molecule.py: `git checkout molecule.py`
7. **Novelty check** when composite > 0.75: `python prepare.py novelty "<SMILES>"`
8. **Render** best molecule: `python prepare.py render "<SMILES>" renders/exp_N_name.png`
9. **Repeat** from step 1

## Rules

- **NEVER** modify `prepare.py` — it is the frozen truth
- **ONLY** modify `molecule.py`
- All SMILES must be RDKit-parseable (test with `python prepare.py evaluate "<smiles>"`)
- Evaluate 3-6 molecules per experiment round
- Log EVERY molecule to `results.tsv`, including failures and reversions
- Commit only when composite_score strictly improves

## Key Optimization Levers (in order of impact)

| Metric | Weight | What to change |
|--------|--------|----------------|
| **BBB Score** | 30% | ↓ TPSA (< 60), logP 1-3, MW < 350, HBD ≤ 2 |
| QED | 25% | Balance MW, rotatable bonds, rings |
| CNS MPO | 25% | MW ≤ 360, TPSA ≤ 90, HBD ≤ 3, logP ≤ 4 |
| Cogn. Pharm | 20% | Add pyrrolidone ring, xanthine motif, or indole |

**Single best move:** Replace any NH₂/CONH₂ with N(CH₃)₂ or CN(C)C → drops HBD to 0, ↑ BBB dramatically.

## Phase Strategy

### Phase 1 — Racetam derivatives (exp 1-4)
Start from Piracetam `NC(=O)CN1CCCC1=O`:
- N,N-dimethyl piracetam: `CN(C)C(=O)CN1CCCC1=O` — eliminates HBD, ↑ BBB
- N-methyl-2-pyrrolidone acetamide: `CN(C)C(=O)CN1CCCC1=O`
- 4-fluorobenzyl piracetam: swap terminal amide for fluorobenzamide
- Aniracetam with N,N-dimethyl: `CN(C)C(=O)CN1CCCC1=O` + phenyl variant

### Phase 2 — Xanthine hybrids (exp 5-8)
Start from 3-methylxanthine `O=C1NC(=O)c2nc(C)nc2N1`:
- Theophylline `Cn1cnc2c1c(=O)[nH]c(=O)n2` — lower MW than caffeine
- 8-chlorotheophylline: add Cl at C8 for metabolic blocking
- Theophylline-pyrrolidone linker: join via ethyl bridge
- 7-propargyltheophylline: small alkyne, ↑ logP moderately

### Phase 3 — Novel scaffolds (exp 9-12)
Go for structures with ZERO PubChem hits:
- Benzimidazole-2-acetamide: `NC(=O)Cc1nc2ccccc2[nH]1` — low TPSA, CNS-friendly
- Indole-2-N,N-dimethylcarboxamide: `CN(C)C(=O)c1cc2ccccc2[nH]1` — indole + no HBD
- Imidazo[1,2-a]pyridine-2-carboxamide: bicyclic, MW ~160, very CNS-friendly
- Pyrrolidone-benzimidazole conjugate: combine racetam core + benzimidazole

### Phase 4 — Fine-tune champion (exp 13-15)
Take the best scaffold from Phase 3 and:
- Fluorine scan: add F at each position, check if composite improves
- N-methyl scan: methylate any remaining NH → ↓ HBD → ↑ BBB
- Ring swap: phenyl → pyridine or thiophene → often ↓ logP + ↑ QED

## Exit Conditions

Stop when **any** of these is true:
- 15 experiments completed this session
- 5 consecutive experiments without improvement in composite_score
- composite ≥ 0.85 with a novel molecule (full success — celebrate!)
- Unrecoverable error

When done: update `molecule.py` BEST_SMILES with champion + write a brief summary.

## results.tsv Format

```
experiment	smiles	composite	qed	bbb_score	cns_mpo	cogn_pharm	pains	note
```

Example row:
```
exp_04	CN(C)C(=O)CN1CCCC1=O	0.7823	0.791	0.812	0.750	0.550	CLEAN	N,N-dimethyl piracetam — new best
```
