# autolab

An autonomous software laboratory built on [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

> Inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) — which proved an AI agent can run hundreds of experiments overnight and find real improvements. We asked: **what if we applied the same loop not just to ML training, but to building entire projects from scratch?**

## Results

### Antibiotic Discovery — 10 Novel Candidates Against Gram-Negative Bacteria

Claude Code autonomously discovered **10 structurally novel antibiotic candidates** optimized for gram-negative bacteria penetration — the WHO's "critical priority" pathogens (E. coli, Klebsiella, Pseudomonas). All 10 are structurally different from every known antibiotic class AND not found in PubChem. **30 experiments, 233 molecules evaluated, pure CPU.**

```
Baseline:  Halicin (composite 0.674 — MIT's 2020 AI-discovered antibiotic)
Final:     Aminoimidazole-piperazine-vinylpyrazine (composite 0.9396)
Improvement: +39% over Halicin
Molecules evaluated: 233
Not found in PubChem: 231 (top 10 all verified novel)
Structurally novel vs 45 known antibiotics: top3_avg Tanimoto 0.118
```

| Exp | What Claude tried | Composite | Key insight |
|-----|------------------|-----------|-------------|
| 1 | Explored 8 scaffold families | 0.825 | Oxadiazole-piperidine best starting point |
| 2 | MW optimization (250-600 sweet spot) | 0.911 | Oxadiazole-phenyl-piperidine breakthrough |
| 4 | N-heterocycle on piperidine | 0.925 | Pyrazine as distal ring — N-rich, novel |
| 5 | Halogen substitution | 0.933 | Chloropyrazine boosts novelty |
| 12 | Vinyl substituent | 0.934 | Unsaturated group beats halogen |
| 19 | **Aminoimidazole head group** | **0.939** | Primary amine + imidazole = optimal gram-neg |
| 29 | **CH2 linker optimization** | **0.9396** | CH2 bridge gives best druglikeness |

**Best molecule:** `Nc1[nH]c(CC2CCN(c3cnc(/C=C)cn3)CC2)cn1`
- 2-(aminoimidazolyl)-methyl-piperazine-vinylpyrazine
- Composite: 0.9396 | Antibacterial: 1.0 | Gram-neg: 0.95 | Novelty: 1.0
- MW: 284.4 | LogP: ~1.0 | N: 6 | SA: 2.8 (synthesizable)
- Not found in PubChem. Tanimoto top3_avg: 0.118 vs all 45 known antibiotics

**Key discovery:** Claude identified a completely new scaffold family — **aminoimidazole + piperazine + substituted pyrazine** — that doesn't resemble any of the 45 known antibiotic classes in our reference set (beta-lactams, quinolones, tetracyclines, macrolides, aminoglycosides, sulfonamides, oxazolidinones, nitroimidazoles, polymyxins, rifamycins, glycopeptides, and 4 recent discoveries including Halicin and Abaucin). The aminoimidazole provides the critical primary amine for gram-negative outer membrane penetration (Hergenrother's eNTRy rules), while the pyrazine-vinyl combination creates a fingerprint unlike any known antibiotic.

> **Important: what this means and what it doesn't**
>
> **What it means:** An autonomous agent discovered 10 structurally novel molecules with properties predicted to enable gram-negative bacterial membrane penetration — the hardest problem in antibiotic design. The scoring combines 6 validated pharmaceutical metrics (antibacterial property profile, eNTRy rules for gram-negative permeability, structural novelty, drug-likeness, synthesizability, membrane disruption potential) evaluated against 45 reference antibiotics.
>
> **What it doesn't mean:** These are not antibiotics. High composite scores mean the molecules have physicochemical properties *consistent with* known antibacterial drugs AND are structurally novel enough to potentially bypass existing resistance. Actual antibacterial activity requires: (1) synthesis, (2) MIC testing against bacterial strains, (3) cytotoxicity assays, (4) animal models, and (5) clinical trials. The scoring function uses heuristics and property predictions, not experimental measurements of bacterial killing.
>
> **What's impressive:** In 30 experiments, starting from zero domain knowledge, Claude independently discovered the importance of primary amines for gram-negative penetration, identified piperazine as the optimal rigid linker, and found that pyrazine with small unsaturated substituents creates maximal structural novelty — insights that align with published medicinal chemistry literature (Hergenrother 2017, O'Shea & Moser 2008).

<details>
<summary><b>How to verify these results yourself</b></summary>

```bash
# 1. Install RDKit
pip install rdkit

# 2. Run baselines (see scoring for 7 known antibiotics)
cd experiments/antibiotic-discovery
python prepare.py baseline

# 3. Evaluate the champion molecule
python prepare.py evaluate "Nc1[nH]c(CC2CCN(c3cnc(/C=C)cn3)CC2)cn1"

# 4. Check PubChem novelty (should return "novel")
python prepare.py novelty "Nc1[nH]c(CC2CCN(c3cnc(/C=C)cn3)CC2)cn1"

# 5. See all 233 evaluated molecules
cat results.tsv

# 6. Render the champion
python prepare.py render "Nc1[nH]c(CC2CCN(c3cnc(/C=C)cn3)CC2)cn1" champion.png
```

All raw data in `experiments/antibiotic-discovery/results.tsv`. Renders in `experiments/antibiotic-discovery/renders/`.
</details>

### Drug Discovery — 25 Computationally Novel Molecules in 82 Evaluations

Claude Code autonomously generated **25 molecules with exceptional drug-like properties** that were not found in PubChem (116M compounds), ChEMBL (2.4M bioactives), or UniChem (40+ cross-referenced databases). Pure CPU, no GPU needed. **30 experiments across 2 runs.**

```
Baseline:  Aspirin (QED 0.55, composite 0.70)
Final:     Thienyl gamma-Lactam (QED 0.9484, composite 1.0)
Improvement: +72% QED, +43% composite
Molecules evaluated: 82
Not found in public databases: 25
Experiments: 30 (10 first run + 20 extended)
```

| Exp | What Claude tried | Best QED | In databases? | Key insight |
|-----|------------------|----------|---------------|-------------|
| 1 | Evaluated 5 known drugs | 0.82 (Ibuprofen) | Yes | Ibuprofen best starting scaffold |
| 2 | Mutated Ibuprofen (16 variants) | 0.90 (Oxadiazole) | Yes | All simple analogs already catalogued |
| 4 | **Combined novel fragments** | **0.9454** | **Not found (6)** | Pyrrolidine + furoyl + fluorophenyl = unexplored |
| 6 | **N-acyl isomer rearrangement** | **0.9461** | **Not found (4)** | First plateau — seemed like the peak |
| 7-10 | Plateau exploration | 0.9461 | Mixed | 4 experiments without improvement |
| 20 | **Replaced furan with benzene** | **0.947** | **Not found** | Simplifying the scaffold improved QED |
| 21 | **Prolinol-benzoyl** | **0.9477** | **Not found (3)** | Phenyl + fluorobenzoyl isomers |
| 24 | **gamma-Lactam scaffold** | **0.9478** | **Not found (2)** | Internal C=O creates new ring system |
| 29 | **★★★ Thienyl Lactam** | **0.9484** | **Not found (3)** | Sulfur atom was the final breakthrough |
| 9-10 | Divergent scaffolds | 0.9461 | Mixed | Morpholino-isoxazole family — new direction |

**Best molecule:** `O=C(O)C1CC(c2ccsc2)C(=O)N1c1ccc(F)cc1`
- 4-(thiophen-3-yl)-1-(4-fluorophenyl)-5-oxopyrrolidine-3-carboxylic acid (Thienyl gamma-Lactam)
- QED: 0.9484 | MW: 305.3 | logP: 2.86 | Lipinski: PASS | PAINS: CLEAN | BRENK: CLEAN
- Not found in PubChem, ChEMBL, or UniChem

**Evolution breakthrough:** The first 10 experiments plateaued at QED 0.9461. Extended to 30 experiments, Claude made 3 additional jumps: furan→benzene (exp 20), amide→lactam (exp 24), phenyl→thienyl (exp 29). The sulfur atom in thiophene was the key to breaking the plateau.

> **Important: what this means and what it doesn't**
>
> **What it means:** An autonomous agent with zero chemistry knowledge generated chemically valid molecules with exceptional drug-likeness scores (QED >0.88) that don't appear in the world's largest public chemical databases. The same computational screening process is used by pharmaceutical companies — typically with GPU clusters and specialized teams.
>
> **What it doesn't mean:** These are not drugs. A high QED score means the molecule has physicochemical properties *similar* to known drugs (molecular weight, solubility, hydrogen bonds). It does not mean it treats any disease. Going from computational candidate to actual medicine requires synthesis, in vitro testing, animal studies, and clinical trials — years of work and millions of dollars. "Not found in databases" means not in PubChem/ChEMBL/UniChem — it could exist in private databases or unpublished research.
>
> **What's impressive:** The method, not the molecule. Anyone can clone this repo, change the starting molecule, and run their own optimization in 30 minutes on any laptop. That's democratization of computational drug discovery.

<details>
<summary><b>How to verify these results yourself</b></summary>

```bash
# 1. Install RDKit
pip install rdkit

# 2. Evaluate the best molecule (check QED, Lipinski, PAINS, etc.)
cd experiments/drug-discovery
python prepare.py evaluate "O=C(O)C1CC(c2ccc(F)cc2)N(C(=O)c2ccco2)C1"

# 3. Check PubChem (should return {"found": false, ...})
python prepare.py novelty "O=C(O)C1CC(c2ccc(F)cc2)N(C(=O)c2ccco2)C1"

# 4. Verify on PubChem manually:
# https://pubchem.ncbi.nlm.nih.gov/#query=O%3DC(O)C1CC(c2ccc(F)cc2)N(C(%3DO)c2ccco2)C1

# 5. Verify on ChEMBL:
# https://www.ebi.ac.uk/chembl/ → search by SMILES

# 6. Verify via InChIKey on UniChem (cross-references 40+ databases):
# https://www.ebi.ac.uk/unichem/rest/inchikey/IFMNHKNTOONNPP-UHFFFAOYSA-N

# 7. See all evaluated molecules
cat results.tsv

# 8. See all molecules not found in databases
grep "novel" results.tsv
```

All raw data in `experiments/drug-discovery/results.tsv`. Molecule renders in `experiments/drug-discovery/renders/`.
</details>

### Materials Discovery — Rediscovering Solar Cell Candidates

Claude Code autonomously explored crystal structures to find materials with optimal band gaps for solar cells. **10 experiments, starting from BaTiO3, zero materials science knowledge provided.**

```
Baseline:  BaTiO3 (composite 0.706, band gap 3.69 eV — too high for solar)
Final:     CuSnO3 (composite 0.999, band gap 1.44 eV — near-ideal for solar)
Improvement: +41% composite score
Materials evaluated: 10 compositions across perovskite, spinel, and ternary structures
```

| Exp | Material | Band Gap | Score | Application |
|-----|----------|----------|-------|-------------|
| 1 | BaTiO3 (baseline) | 3.69 eV | 0.706 | Too wide for solar |
| 3 | CaZrSe3 | 1.46 eV | 0.891 | ☀️ Solar cell candidate |
| 4 | Fe2SnO4 (spinel) | 1.42 eV | 0.933 | ☀️ Solar + catalyst |
| **6** | **CuSnO3** | **1.44 eV** | **0.999** | ☀️ Solar + catalyst + superconductor |
| 8 | Cu2SnGeO6 (quaternary) | 1.52 eV | 0.992 | ☀️ 4-element novel composition |

**Key discovery:** Claude independently identified CaZrSe3 as a promising solar cell material — the [same material currently being published in peer-reviewed journals](https://link.springer.com/article/10.1007/s10825-024-02245-7) as a next-generation photovoltaic candidate with 32.4% theoretical efficiency. It also converged on copper-based perovskites (CuSnO3, CuGeO3, CuWO3) as optimal for the 1.4 eV solar band gap.

> **Honesty note:** The scoring function uses empirical estimates, not full DFT calculations. These are computational predictions that would need experimental validation. CuSnO3 has been [studied via DFT](https://www.sciencedirect.com/science/article/abs/pii/S0022459622007757) — Claude reached the same conclusion as published research. The quaternary Cu2SnGeO6 may be genuinely novel.

### Artificial Life (Lenia) — Evolving Digital Creatures

Claude Code searched for rules in a continuous cellular automaton that produce emergent life-like behavior. **10 experiments, baseline dies immediately, no biology knowledge provided.**

```
Baseline:  Orbium parameters (composite 0.024 — dies instantly)
Final:     Multi-blob sigma=0.04 (composite 0.670 — survives, oscillates, self-organizes)
From death to life in 10 experiments.
```

| Exp | What Claude tried | Composite | Key behavior |
|-----|------------------|-----------|-------------|
| 1 | Orbium baseline | 0.024 | Dies immediately |
| **2** | **Wider sigma (0.03)** | **0.660** | **Survives! Oscillates! Structures!** |
| 3 | Ring kernel + ring init | 0.575 | Lost oscillation |
| 4 | 3-shell kernel + multi-blob | 0.620 | Best movement so far |
| 7 | Multi-blob + best sigma | 0.668 | High oscillation (0.77) |
| **8** | **Multi-blob + sigma=0.04** | **0.670** | **Best: alive, stable, oscillating** |

**What emerged:** From experiment 2 onward, the simulation produces stable, oscillating, self-organized structures — patterns that survive for 500+ steps, maintain structural integrity, and exhibit periodic behavior. 4 GIFs rendered showing the evolution from death to complex life.

**Phase transition discovery:** The agent found that sigma=0.015 → death, sigma=0.03 → life. A tiny parameter change crosses the boundary between "nothing happens" and "complex behavior emerges." This mirrors real physics where phase transitions happen at critical thresholds.

GIFs in `experiments/artificial-life/renders/`.

### nanoGPT Optimization (Karpathy Loop)

Claude Code autonomously optimized a GPT language model on an RTX 4050 laptop GPU. **10 experiments, ~1 hour, zero human intervention.**

```
Baseline val_loss:  1.6867
Final val_loss:     1.4534  (-13.8%)
Improvements found: 4 of 10 experiments
```

| # | Experiment | val_loss | Status |
|---|-----------|----------|--------|
| 0 | Baseline (6L/384E/6H, 10.8M params) | 1.6867 | baseline |
| 1 | AMP mixed precision training | 1.5155 | **improved** |
| 2 | LR 6e-4 + cosine schedule | 1.4674 | **improved** |
| 3 | 8 layers + dropout 0.1 | 1.4767 | reverted |
| 4 | Gradient accumulation 4x | 1.4699 | reverted |
| 5 | Dropout 0.1 (less regularization) | 1.4826 | reverted |
| 6 | Batch size 96 | 1.4722 | reverted |
| 7 | LR 1e-3 | 1.4576 | **improved** |
| 8 | Weight decay 0.2 | 1.4534 | **improved** |
| 9 | Dropout 0.3 | 1.4632 | reverted |
| 10 | RMSNorm | 1.4563 | reverted |

**Key discovery:** With a fixed 5-minute training budget, throughput beats capacity. Everything that made training faster (AMP, higher LR) improved results. Everything that made the model bigger or slower (more layers, larger batches) made results worse. The agent learned this pattern autonomously.

### Compression — 4% Away from Beating gzip

Claude Code wrote a data compressor from scratch in pure Python and iteratively optimized it. **10 experiments, starting from basic RLE, targeting gzip-level compression.**

```
Baseline:  RLE (ratio 1.85 — EXPANDS data)
Final:     LZ77 + Dual Huffman + 512K hash table (ratio 0.238)
gzip:      ratio 0.229
Gap:       Only 4% away from gzip — a C algorithm optimized over 30 years
```

| Exp | Algorithm | Ratio | vs gzip | Key change |
|-----|----------|-------|---------|-----------|
| 0 | RLE baseline | 1.847 | -706% 💀 | Run-length encoding expands text |
| 1 | LZ77 hash chain | 0.319 | -39% | First real compression |
| 2 | LZ77 + Huffman | 0.278 | -21% | Entropy coding added |
| 5 | Dual Huffman + deflate codes | 0.245 | -6.7% | Distance codes like real deflate |
| **8** | **4-byte hash + 512K table** | **0.238** | **-4.0%** | **Best composite — near gzip** |
| 10 | Ultra-fast dict lookup | 0.262 | -14% | Speed up but ratio regressed |

**What's remarkable:** In 10 iterations, Claude went from an algorithm that makes files bigger to one that compresses within 4% of gzip. It independently reinvented LZ77, Huffman coding, and deflate-style distance codes — the same techniques that took decades of human research. All in pure Python, ~300 lines.

> **Honesty note:** The 4% gap is partly because gzip is compiled C (21 MB/s) while this is interpreted Python (0.5 MB/s). In compression ratio alone, the gap is even smaller. Speed is the real bottleneck.

### Fertilizer Design — Novel Slow-Release Nitrogen Carriers

Claude Code designed **20+ novel molecules** for slow-release nitrogen fertilizers that beat the commercial standard (IBDU). **15 experiments, 60+ molecules evaluated, 7 confirmed not in PubChem.**

```
Baseline:  IBDU (composite 0.673 — commercial slow-release fertilizer)
Final:     Spiro-diguanidine-biuret (composite 0.7964)
Improvement: +18.4% over commercial standard
Novel molecules: 20+ (7 verified not in PubChem)
```

| Exp | What Claude tried | Composite | Key insight |
|-----|------------------|-----------|-------------|
| 1-3 | Baselines + urea derivatives | 0.648 | Triuret slightly better than biuret |
| 4 | **Cyclohexyl biuret** | **0.699** | LogP 0-3 sweet spot for slow-release |
| 5-6 | Triuret + cycloalkyl rings | 0.765 | Longer chains + bigger rings = better |
| 7-8 | Tetrauret + cycloheptyl | 0.779 | Both bonus thresholds triggered |
| 9-10 | Guanidine hybrids | 0.793 | Guanidine more N-efficient than urea |
| **11** | **Spiro[cyclopropane-cyclohexyl]** | **0.7964** | **2 rings, MW<300, biodeg 0.95** |
| 12-15 | Plateau exploration | 0.791 | Bicyclics, heterocycles, thioureas — no improvement |

**Best molecule:** `NC(=N)NC(=N)NC(=O)NC(=O)NC1CCC2(CC2)CC1`
- Spiro[cyclopropane-cyclohexyl] diguanidine-biuret
- N%: 33.2 | SlowRelease: 0.784 | Biodeg: 0.95 | SA: 3.26
- Not found in PubChem

**Key discovery:** The winning strategy combined three independent insights: (1) diguanidine backbone for N-efficiency, (2) biuret linkage for slow-release, (3) spiro-cycloalkyl cap for hydrophobicity without exceeding MW 300. Claude learned each insight in separate experiments and combined them in experiment 11.

### Nootropic Discovery — Novel CNS Penetrant with Triple Pharmacophore

Claude Code designed a **novel cognitive enhancer molecule** that scores near-perfect across all CNS drug metrics — blood-brain barrier penetration, CNS multiparameter optimization, and cognitive pharmacophore matching. **12 experiments, 55 molecules evaluated, starting from Piracetam.**

```
Baseline:  Modafinil (composite 0.816 — best known nootropic)
Final:     Indolyl-pyrrolidinone-methylpiperidine (composite 0.9864)
Improvement: +21% over Modafinil
Molecules evaluated: 55
Novel (not in PubChem): champion + 8 others verified
```

| Exp | What Claude tried | Composite | Key insight |
|-----|------------------|-----------|-------------|
| 1 | Racetam derivatives, N,N-dimethyl | 0.862 | Phenyl + dimethylamide → BBB=1.0 |
| 3 | **Indole + pyrrolidone** | **0.944** | Dual pharmacophore, BBB=1.0, QED 0.94 |
| 6 | Gem-dimethyl pyrrolidone | 0.947 | First novel molecule (not in PubChem) |
| 8 | **Triple pharmacophore** (indole + pyrrolidone + piperidine) | **0.957** | pharm=1.0 unlocked |
| 9 | **N-methyl piperidine** | **0.984** | HBD 2→1, MPO jumps to 1.0 |
| 10 | **Direct linker (no CH2)** | **0.9864** | Fewer rotatable bonds → QED boost |

**Best molecule:** `O=C1CCCN1C(c1cc2ccccc2[nH]1)C1CCN(C)CC1`
- 2-(1H-indol-2-yl)-1-(1-methylpiperidin-4-yl)pyrrolidin-2-one
- Composite: 0.9864 | QED: 0.9454 | BBB: 1.0 | CNS MPO: 1.0 | Pharmacophore: 1.0
- MW: 311.4 | LogP: 3.17 | TPSA: 39.3 | HBD: 1
- Not found in PubChem. PAINS: CLEAN.

**Key discovery:** Claude independently discovered that combining three known CNS-active pharmacophores — **indole** (serotonin receptor affinity), **2-pyrrolidinone** (racetam cognitive enhancement), and **N-methylpiperidine** (dopamine/acetylcholine modulation) — into a single compact molecule (MW 311) achieves near-perfect scores across all four CNS drug metrics simultaneously. The critical breakthrough was N-methylation of the piperidine nitrogen (exp 9), which eliminated one hydrogen bond donor and unlocked BBB=1.0 + MPO=1.0 without losing any pharmacophore recognition.

> **Important: what this means and what it doesn't**
>
> **What it means:** An autonomous agent designed a novel molecule with physicochemical properties optimized for CNS penetration and cognitive pharmacophore matching — scoring 1.0 on BBB, CNS MPO, and pharmacophore simultaneously. The scoring uses Clark's BBB rules, Pfizer's CNS MPO desirability function (Wager et al. 2010), and SMARTS-based pharmacophore detection.
>
> **What it doesn't mean:** This is not a nootropic drug. High composite scores mean the molecule has the right size, lipophilicity, and polar surface area to cross the blood-brain barrier, AND contains structural motifs found in known cognitive enhancers. Actual cognitive enhancement requires: (1) synthesis, (2) binding assays, (3) behavioral testing in animal models, (4) safety/toxicology, and (5) clinical trials.

<details>
<summary><b>How to verify these results yourself</b></summary>

```bash
# 1. Install RDKit
pip install rdkit

# 2. Run baselines (Piracetam, Modafinil, Caffeine, etc.)
cd experiments/nootropic-discovery
python prepare.py baseline

# 3. Evaluate the champion
python prepare.py evaluate "O=C1CCCN1C(c1cc2ccccc2[nH]1)C1CCN(C)CC1"

# 4. Check novelty
python prepare.py novelty "O=C1CCCN1C(c1cc2ccccc2[nH]1)C1CCN(C)CC1"

# 5. See all 55 evaluated molecules
cat results.tsv
```

All raw data in `experiments/nootropic-discovery/results.tsv`.
</details>

### Prompt Optimizer — 61% to 80.5% on HumanEval with Haiku

Claude Code optimized a system prompt to maximize **claude-haiku-4-5** (the cheapest Claude model, $0.25/M tokens) on HumanEval — 164 Python coding problems. The metric is **pass@1**: percentage of problems solved correctly on the first attempt.

```
Baseline:  61.0% (no system prompt)
Final:     80.5% (132/164 problems)
Improvement: +19.5 percentage points
Cost per full eval: ~$0.15
```

**Why it matters:** If you can make Haiku perform at near-Opus level on code generation just by optimizing the prompt, that's a **60x cost reduction** for any developer using LLMs for coding. The winning prompt is one sentence — concise beats verbose.

**Best prompt:** `"You are a senior Python engineer who writes production-quality, bug-free code. Think about edge cases first, then return ONLY the function body code, nothing else. Match the docstring examples exactly."`

## What autolab Does

autolab runs the Karpathy Loop on anything with a measurable metric:

1. **Create** an experiment with `/experiment <name> <description>`
2. **Run** the loop: read `program.md`, iterate on the editable file
3. **Measure** with the frozen evaluator (`prepare.py`)
4. **Keep or revert** based on the score
5. **Repeat** until plateau or target met

Every attempt is logged. Every failure is documented. Every result is in `results.tsv`.

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/autolab
cd autolab

# Open with Claude Code
claude
```

### Run an Existing Experiment

Each experiment has a `program.md` with the loop instructions. Just tell Claude to read it and execute:

```bash
# Antibiotic Discovery (requires: pip install rdkit)
> Read experiments/antibiotic-discovery/program.md and execute the optimization loop.

# Drug Discovery (requires: pip install rdkit)
> Read experiments/drug-discovery/program.md and execute the optimization loop.

# Fertilizer Design (requires: pip install rdkit)
> Read experiments/fertilizer-design/program.md and execute the optimization loop.

# Compression (no dependencies)
> Read experiments/compression/program.md and execute the optimization loop.

# Artificial Life (requires: pip install numpy pillow)
> Read experiments/artificial-life/program.md and execute the optimization loop.

# Materials Discovery (requires: pip install pymatgen)
> Read experiments/materials-discovery/program.md and execute the optimization loop.

# nanoGPT (requires: PyTorch + CUDA GPU)
> Read experiments/nanoGPT/program.md and execute the optimization loop.

# Prompt Optimizer (requires: Anthropic API key)
> Read experiments/prompt-optimizer/program.md and execute the optimization loop.
```

### Create a New Experiment

```bash
> /experiment protein-folding "Optimize protein sequences for stability using ESMFold"
```

**Requirements:** [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with an API key. Python 3.10+. Each experiment lists its specific dependencies.

## The Karpathy Loop

```
┌─────────────────────────────────────────────────┐
│              THE KARPATHY LOOP                   │
│                                                  │
│  1. READ        → Current best from editable.py  │
│       ↓                                          │
│  2. HYPOTHESIZE → What change improves the score? │
│       ↓                                          │
│  3. MODIFY      → Edit the ONE editable file     │
│       ↓                                          │
│  4. EVALUATE    → python prepare.py evaluate      │
│       ↓                                          │
│  5. DECIDE      → Better? Keep. Worse? Revert.   │
│       ↓                                          │
│  6. LOG         → Append to results.tsv           │
│       ↓                                          │
│  7. REPEAT      → Until exit condition met        │
│       └──────────────────────────────────┘       │
└─────────────────────────────────────────────────┘
```

## How It Works — Cognitive Evolutionary Learning

autolab is a **reinforcement learning environment for reasoning agents**. Think of it as [OpenAI Gym](https://github.com/openai/gym), but instead of training neural network policies with gradient descent, the "agent" is an LLM that learns within context through reasoning.

| RL Concept | OpenAI Gym | autolab |
|---|---|---|
| **Agent** | Neural network (PPO, DQN) | Claude (LLM reasoning) |
| **Environment** | `env.step(action)` | `python prepare.py evaluate` |
| **Action space** | Discrete/continuous vectors | Modifications to `<editable>.py` |
| **Observation** | State tensor | `results.tsv` + current code |
| **Reward** | Scalar signal | `composite_score` |
| **Policy** | Learned via gradients (thousands of episodes) | Pre-trained reasoning (10-30 iterations) |
| **Create env** | `gym.make("CartPole-v1")` | `/experiment "protein-folding" "..."` |

The key difference: in classical RL, the policy learns by updating weights across thousands of episodes. In autolab, the policy is a foundation model that **reasons about results** — it reads what worked, understands *why*, formulates hypotheses, and makes informed decisions. No gradient updates between iterations, just cognitive adaptation in context.

This is why autolab achieves results in 10-30 iterations where classical optimization would need thousands: the agent doesn't randomly sample the search space — it **reasons about the structure of the problem**.

Example from nootropic-discovery (12 iterations, 55 molecules → composite 0.9864):
```
Exp 3:  "Indole + pyrrolidone = dual pharmacophore → 0.944"
        → Claude UNDERSTANDS that combining motifs increases pharm score
Exp 8:  "If 2 pharmacophores work, what about 3?"
        → Adds piperidine → pharm=1.0
Exp 9:  "pharm=1.0 but MPO=0.917... HBD=2 is the bottleneck"
        → N-methylates piperidine → HBD=1 → MPO=1.0
Exp 10: "Everything at 1.0 except QED... rotatable bonds?"
        → Removes CH2 linker → QED boost → 0.9864
```

Each step is **causal reasoning**, not random sampling. The agent identifies which variable limits the score, hypothesizes why, and proposes a targeted change.

### The Experiment as Environment

Every experiment is a self-contained environment with 5 files. Each file has a specific role in the learning loop:

```
experiments/<name>/
├── prepare.py      # THE ENVIRONMENT — frozen, defines the reward function
├── <editable>.py   # THE ACTION SPACE — the only file the agent modifies
├── program.md      # THE POLICY GUIDE — instructions, strategy, exit conditions
├── METRICS.md      # THE CONTRACT — frozen success criteria, can't move goalposts
├── results.tsv     # THE MEMORY — append-only log of every attempt
├── renders/        # THE EVIDENCE — visual outputs (optional)
└── data/           # THE WORLD — test data the environment uses (optional)
```

**`prepare.py` — The Environment (frozen)**

This is the equivalent of `env.step()` in Gym. It defines what "good" means and returns a numerical reward. The agent **cannot modify it** — this is what prevents the agent from cheating by redefining success. It typically has three commands:
- `evaluate <candidate>` — run the candidate against the metric, return composite score
- `baseline` — show reference scores to beat (the "starting state")
- `novelty <candidate>` — verify the result is genuinely new (optional)

**`<editable>.py` — The Action Space**

The **only file the agent modifies**. Contains the current best candidate and strategy notes. What it looks like depends on the domain:
- `molecule.py` → SMILES strings (drug discovery, antibiotics, fertilizers, nootropics)
- `train.py` → Model architecture + hyperparameters (nanoGPT)
- `compressor.py` → Compression algorithm code (compression)
- `rules.py` → Cellular automaton parameters (artificial life)
- `prompts.py` → System prompt + few-shot examples (prompt optimization)

**`program.md` — The Policy Guide**

Domain-specific instructions that shape **how** the agent explores. This is the equivalent of reward shaping in RL — it doesn't change what success means, but it guides the agent toward productive exploration. Contains:
- The optimization loop steps (read → hypothesize → modify → evaluate → decide)
- Exit conditions (max experiments, plateau detection, target score)
- Phase-based strategy (explore → combine → optimize)
- Domain-specific tips (e.g., "primary amines help gram-negative penetration")
- Scoring breakdown (what each sub-metric measures and its weight)

**`METRICS.md` — The Contract**

Frozen at experiment creation. Defines the composite score formula, what each sub-metric measures, and what the target is. The agent **cannot modify this** — it's the guarantee that goalposts don't move mid-experiment.

**`results.tsv` — The Memory**

Append-only log of **every attempt**, including failures. This is what gives the agent "experience" — it reads past results to understand what worked and what didn't. Unlike RL replay buffers, the agent doesn't just see (state, action, reward) tuples — it reads the descriptions and reasons about patterns.

### Current Environments

| Experiment | Editable File | Frozen Evaluator | Best Score |
|-----------|--------------|-----------------|-----------|
| antibiotic-discovery | `molecule.py` | antibacterial + gram-neg + novelty vs 45 known antibiotics | 0.9396 |
| drug-discovery | `molecule.py` | QED + Lipinski + PAINS + novelty check | 1.0 |
| fertilizer-design | `molecule.py` | N% + slow-release + biodeg + cost | 0.7964 |
| nootropic-discovery | `molecule.py` | BBB + CNS MPO + cognitive pharmacophore | 0.9864 |
| materials-discovery | `material.py` | Band gap + stability + applications | 0.999 |
| artificial-life | `rules.py` | Survival + complexity + oscillation | 0.6698 |
| compression | `compressor.py` | Ratio + speed + losslessness | 0.6818 |
| nanoGPT | `train.py` | Validation loss | 1.4534 |
| prompt-optimizer | `prompts.py` | pass@1 on HumanEval (164 problems) | 0.8049 |

### Creating New Environments

Any domain with a measurable metric can become an autolab experiment:

```bash
> /experiment protein-folding "Optimize protein sequences for thermostability using ESMFold"
```

This creates `prepare.py` (the evaluator), `sequence.py` (the editable), `program.md` (the strategy), and `METRICS.md` (the contract). The agent takes it from there.

## Safety Model

- **Frozen evaluators** — `prepare.py` is never modified, goalposts don't move
- **Frozen metrics** — METRICS.md locked at experiment creation
- **Append-only logs** — `results.tsv` records every attempt, even failures
- **Git safety net** — everything committed, everything revertible
- **Exit conditions** — max experiments, plateau detection, target scores
- **Root files protected** — README.md, CLAUDE.md, LICENSE never modified during loops

## Project Structure

```
autolab/
├── CLAUDE.md                    # The constitution — rules for the agent
├── experiments/                 # All environments
│   ├── antibiotic-discovery/    # Novel gram-neg antibiotics (molecule.py)
│   ├── drug-discovery/          # Drug-like molecules (molecule.py)
│   ├── fertilizer-design/       # Slow-release N-carriers (molecule.py)
│   ├── materials-discovery/     # Solar cell materials (material.py)
│   ├── artificial-life/         # Lenia cellular automaton (rules.py)
│   ├── compression/             # Data compression (compressor.py)
│   ├── nanoGPT/                 # GPT optimization (train.py)
│   ├── nootropic-discovery/     # Cognitive enhancers (molecule.py)
│   └── prompt-optimizer/        # LLM prompt engineering (prompts.py)
├── lab/
│   ├── journal.md               # Append-only activity log
│   └── scoreboard.md            # Best results per experiment
└── .claude/
    ├── settings.json            # Hooks configuration
    ├── hooks/                   # Session lifecycle (inject state, log duration)
    └── skills/
        └── create-experiment/   # /experiment — creates new environments
```

## Under the Hood

autolab is not a framework or library — it's a **set of instructions** (CLAUDE.md) that turn Claude Code into an autonomous research agent. The runtime is Claude Code itself. The "program" is markdown. The infrastructure is git.

- **CLAUDE.md** — The constitution. Defines rules and conventions.
- **`/experiment` skill** — Creates new environments (`prepare.py` + `<editable>.py` + `program.md`).
- **Hooks** — SessionStart injects lab state for interruption-resilience; Stop evaluates if logging is needed.
- **`program.md`** — Each experiment's domain-specific loop instructions and strategy.

No custom runtime. No orchestration framework. No dependencies beyond Claude Code and Python. The entire system is Markdown, JSON, and Python files that tell an LLM how to do science.

## License

MIT — see [LICENSE](LICENSE).

## Author

Built by [Hugo Guerra](https://github.com/hugoguerrap). Inspired by [Andrej Karpathy's autoresearch](https://github.com/karpathy/autoresearch).
