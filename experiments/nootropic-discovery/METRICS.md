# nootropic-discovery — Frozen Metrics

**Frozen on:** 2026-03-24
**DO NOT MODIFY** — these criteria define experiment success.

## Composite Score Formula

```
composite = 0.25 × QED + 0.30 × BBB_score + 0.25 × CNS_MPO + 0.20 × cogn_pharm
```

## Success Criteria

| Metric | Target | Weight | Measurement |
|--------|--------|--------|-------------|
| QED | ≥ 0.70 | 25% | RDKit `QED.qed()` |
| BBB Score | ≥ 0.75 | 30% | Clark's CNS rules: TPSA, logP, MW, HBD |
| CNS MPO | ≥ 0.70 | 25% | Pfizer 6-parameter desirability (Wager 2010) |
| Cogn. Pharmacophore | ≥ 0.60 | 20% | SMARTS match: pyrrolidone, xanthine, indole, piperidine, benzimidazole |
| **Composite** | **≥ 0.85** | — | Weighted sum above (Modafinil=0.8162, beat it!) |
| PAINS | CLEAN | required | PAINS filter from FilterCatalog |
| Novelty | Not in PubChem | required | REST API check |

## Baselines to Beat (verified scores — 2026-03-24)

| Compound | Role | Composite |
|----------|------|-----------|
| Caffeine | Minimum | 0.6477 |
| Donepezil | Medium | 0.6663 |
| Piracetam | Medium | 0.7170 |
| Aniracetam | Medium | 0.7218 |
| **Modafinil** | **Current champion** | **0.8162** |
| 🏆 **Goal** | **Novel molecule, full success** | **≥ 0.85** |

> Note: Modafinil already exceeds 0.80. The experiment goal is to find a **novel molecule**
> (not in PubChem) that scores ≥ 0.85 — clearly surpassing all known baselines.

## Sub-metric Definitions

**BBB Score** — Blood-brain barrier penetration proxy (Clark 1999):
- logP optimal window: 1.0–3.5
- TPSA < 60 Å² (hard cut-off for CNS)
- MW < 350 Da
- HBD ≤ 2

**CNS MPO** — Pfizer multi-parameter optimization (Wager et al. 2010, J. Med. Chem.):
- logP ≤ 5 (1 pt), logP ≤ 4 (+0.5 pt bonus)
- MW ≤ 360 (1 pt)
- TPSA ≤ 90 (1 pt)
- HBD ≤ 3 (1 pt), HBD ≤ 1 (+0.5 pt bonus)
- Normalized to 0-1

**Cogn. Pharmacophore** — SMARTS match bonus system (base score 0.20):
- 2-Pyrrolidone ring (+0.35) — racetam core
- Piperidine ring (+0.20) — AChE inhibitor scaffold
- Indole (+0.25) — tryptamine/serotonergic
- Imidazole (+0.15) — cholinergic activity
- Benzimidazole (+0.20) — CNS penetrating scaffold
- Xanthine core (+0.20) — stimulant + cognitive modulator
- Capped at 1.0

## Verification Command

```bash
cd experiments/nootropic-discovery
python prepare.py baseline          # check baseline scores
python prepare.py evaluate "<SMILES>"    # evaluate candidate
python prepare.py novelty "<SMILES>"     # check PubChem
```
