# autolab Proposals — 2026-03-24
## Hypothesis Engine: Weekly Intelligence Synthesis → Executable Experiments

**Generated:** 2026-03-24 15:00 UTC
**Intelligence Sources:**
- Scientific Scouts (4): ArXiv Experimental (20 papers), Papers With Code (15 papers), bioRxiv CompBio (12 papers), Nature/Science (10 papers)
- Tech/AI Intelligence (web-sourced): GitHub Trending, AI Model Releases, ArXiv AI/Agents, Speculative Decoding benchmarks
**Proposals Generated:** 11
**Distribution:** 4 scientific, 4 tech/AI, 3 cross-domain

---

## Summary Table

| # | Title | Category | Feasibility | Impact | Priority | Recommended |
|---|-------|----------|-------------|--------|----------|-------------|
| 1 | FLIP2-Optimizer | biology | 5 | 5 | 25 | **RECOMMENDED** |
| 2 | PODGen-Materials | materials | 5 | 5 | 25 | **RECOMMENDED** |
| 3 | SpecForge-Benchmark | AI/ML | 5 | 5 | 25 | **RECOMMENDED** |
| 4 | iScore-Drug-Affinity | chemistry | 5 | 4 | 20 | |
| 5 | AutoResearchClaw-Eval | AI/ML | 5 | 4 | 20 | |
| 6 | GRACE-Alloy-Screener | materials | 4 | 5 | 20 | |
| 7 | NucleoBench-Algorithm-Mixer | biology | 4 | 4 | 16 | |
| 8 | OpenClaw-Plugin-Benchmark | software-engineering | 5 | 3 | 15 | |
| 9 | CVAE-Protein-Designer + GRACE | cross-domain (bio×materials) | 4 | 5 | 21* | |
| 10 | EvoScientist-ROM-Collective | cross-domain (AI×science) | 4 | 5 | 21* | |
| 11 | Solvent-Mixture-ML-Optimizer | cross-domain (chemistry×AI) | 5 | 4 | 21* | |

*Cross-domain proposals receive +1 bonus to priority score.

---

## SCIENTIFIC PROPOSALS (from scout reports)

---

### Proposal 1: FLIP2-Optimizer
**Source:** bioRxiv "FLIP2: Expanding Protein Fitness Landscape Benchmarks" + Nature "Protein Design with LLMs" + ArXiv "Atomic Trajectory Modeling with SSMs"
**Type:** experiment
**Category:** biology
**Hypothesis:** Simple models often match or outperform fine-tuned protein language models on FLIP2's 7 new protein engineering datasets (Spearman ~0.65). A systematic ensemble of classical ML + state space models for trajectory dynamics can push correlation to 0.80+ by exploiting physicochemical features and temporal protein dynamics that language models miss.
**Method:**
- Download FLIP2 benchmark (7 datasets: enzymes, PPIs, light-sensitive proteins) and cache ESM-2 embeddings
- Engineer 50+ feature sets (physicochemical, structure-derived, topological descriptors)
- Train ensemble: Ridge, XGBoost, LightGBM, Neural Net with voting/stacking
- Add JAX-based State Space Model for trajectory dynamics on embeddings
- Karpathy Loop: evolve architecture, ensemble weights, SSM hyperparams; measure Spearman on frozen test split
**Metrics:** Spearman correlation ≥0.80 (avg across 7 datasets); generalization >0.75 on unseen proteins; SSM inference <1s per trajectory
**Feasibility:** 5 — Public benchmark, scikit-learn + PyTorch, CPU-viable with cached embeddings, 2-3h runtime
**Impact:** 5 — Publishable (NeurIPS/ICLR), extends drug-discovery, new protein-fitness domain for autolab
**Priority Score:** 25
**Estimated iterations:** 8-10
**Dependencies:** scikit-learn, PyTorch, HuggingFace Transformers, JAX, pandas, numpy

**Ready-to-use prompt:**
> Research and implement a protein fitness landscape optimizer on the FLIP2 benchmark. Download 7 FLIP2 datasets (enzymes, PPIs, light-sensitive proteins). Extract ESM-2 embeddings (cache). Engineer 50+ physicochemical/structural feature sets. Train ensemble (Ridge, XGBoost, LightGBM, NN) with voting/stacking. Add JAX SSM for trajectory dynamics. Freeze metrics: primary = Spearman correlation (7-dataset avg), baseline 0.65, target 0.80+. Evolve via Karpathy Loop for 8-10 iterations. Success: Spearman ≥0.80 avg, >0.75 on hold-out proteins, inference <1s.

---

### Proposal 2: PODGen-Materials
**Source:** Nature npj Comp Mat "Materials discovery acceleration by conditional generative methodology" + ArXiv "ML interatomic potentials for electrolytes" + ArXiv "Small-Data ML for β-Ga₂O₃ epitaxy"
**Type:** experiment
**Category:** materials
**Hypothesis:** PODGen's conditional generative framework (VAE + property prediction ensemble) explored limited compositions. By replicating in PyTorch and iterating over generator architecture (VAE vs diffusion), ensemble configs (RF, NN, GNN), and inverse sampling strategies, autolab can discover 10+ novel materials not in JARVIS/MATBENCH with optimized band gap or thermal conductivity, achieving MAE <0.10 eV (vs baseline 0.15).
**Method:**
- Scaffold PyTorch project with conditional VAE generator + 3-model property ensemble
- Download JARVIS (10K materials), freeze 20% test set
- Implement conditional generation: target properties → candidate materials
- Karpathy Loop: evolve generator architecture, ensemble weights, sampling strategy, inverse design method
- Validate novelty (Tanimoto <0.3) and synthesizability heuristics
**Metrics:** Property prediction MAE <0.10 eV (band gap); success rate >80% on test; novelty >90% of top 50 candidates not in JARVIS; diversity Tanimoto <0.3
**Feasibility:** 5 — PyTorch + pymatgen + JARVIS all open; CPU 4 cores × 2h
**Impact:** 5 — Novel materials discovery, publishable (npj Computational Materials), extends materials-discovery experiment
**Priority Score:** 25
**Estimated iterations:** 6-8
**Dependencies:** PyTorch, torch_geometric, pymatgen, RDKit, ASE, scikit-learn, JARVIS dataset

**Ready-to-use prompt:**
> Replicate and optimize PODGen conditional generative materials discovery. Scaffold PyTorch project: conditional VAE + property prediction ensemble. Download JARVIS (10K materials), freeze 20% test. Implement inverse design: target band gap/thermal conductivity → candidate compositions. Freeze metrics: MAE <0.10 eV (baseline 0.15), novelty >90%, diversity Tanimoto <0.3. Evolve: generator (VAE latent dim 32-256, vs diffusion), ensemble (RF, NN, GNN), sampling (Gumbel, beam search, gradient ascent). 6-8 Karpathy iterations. Deliverables: prepare.py, optimizer.py, METRICS.md, results.tsv, top 10 novel compositions.

---

### Proposal 3: iScore-Drug-Affinity
**Source:** bioRxiv "iScore: ML-Based Scoring for de novo Drug Discovery" + ArXiv "Persistent local Laplacian binding affinity prediction"
**Type:** experiment
**Category:** chemistry
**Hypothesis:** iScore achieved R=0.78 Pearson on CASF 2016 binding affinity, but the vast descriptor engineering space (geometric, physicochemical, topological, persistent Laplacian) and ensemble weighting strategies remain underexplored. Systematic exploration with SHAP-guided feature selection and active learning on hard negatives can push R>0.85.
**Method:**
- Download CASF 2016 (280 PDB complexes), freeze 50 test complexes
- Implement 15 descriptor families including novel persistent Laplacian features
- Train base models: RF, XGBoost, Ridge, SVM; then ensemble (voting, stacking, blending)
- Active learning: iterative hard-negative re-weighting
- SHAP ablation: recursive feature elimination for interpretability
**Metrics:** Pearson R >0.85 on CASF hold-out (baseline 0.78); RMSE <1.1 eV (baseline 1.34); screening power >80%
**Feasibility:** 5 — scikit-learn + RDKit, 280 complexes = fast iteration, <2h CPU
**Impact:** 4 — Extends existing drug-discovery experiment, stable 2+ year baseline, publishable (PLoS CB)
**Priority Score:** 20
**Estimated iterations:** 5-7
**Dependencies:** scikit-learn, RDKit, SHAP, pandas, numpy, CASF 2016 dataset

**Ready-to-use prompt:**
> Extend iScore binding affinity prediction on CASF 2016. Download 280 PDB complexes, freeze 50 for test. Implement 15 descriptor families (geometric distances/angles, physicochemical logP/HBDA, topological persistent homology, Laplacian eigenvalues). Train RF + XGBoost + Ridge + SVM ensemble with voting/stacking/blending. Apply active learning on hard negatives. SHAP feature importance + recursive elimination. Freeze metrics: Pearson R (baseline 0.78, target >0.85), RMSE (baseline 1.34, target <1.1), screening power >80%. 5-7 Karpathy iterations.

---

### Proposal 4: NucleoBench-Algorithm-Mixer
**Source:** bioRxiv "NucleoBench: Large-Scale Benchmark of Nucleic Acid Design Algorithms" + ArXiv "ReSCALE: Gumbel + Sequential Halving for LLM Reasoning"
**Type:** experiment
**Category:** biology
**Hypothesis:** NucleoBench benchmarked 9 nucleic acid design algorithms across 16 tasks in 400K+ experiments. AdaBeam wins ~14/16 tasks. Algorithm hybridization (ensemble of AdaBeam + FastSeqProp + Ledidi) with ReSCALE-inspired sequential halving for early elimination of poor branches can beat AdaBeam on 15+/16 tasks with 20% faster convergence.
**Method:**
- Download NucleoBench benchmark (400K experiment grid, 16 biological tasks)
- Compute AdaBeam baseline statistics, split 8 tasks for evolution / 8 for validation
- Implement algorithm ensemble combinator (voting, Kalman filter, mixture-of-experts)
- Add task classifier: meta-learner predicts best algorithm per task type
- Apply sequential halving to eliminate poor algorithm branches early
**Metrics:** Task win rate 15+/16 (baseline ~14); convergence speed <6.5 iterations (baseline ~8 median); eval budget <200 (baseline ~250)
**Feasibility:** 4 — JAX + scikit-optimize + biopython; 400K grid is large but algorithm mixing is fast; CPU-viable
**Impact:** 4 — New domain for autolab (nucleic acid design), publishable, generalizable meta-learning approach
**Priority Score:** 16
**Estimated iterations:** 5-6
**Dependencies:** JAX, scikit-optimize, numpy, scipy, biopython, NucleoBench dataset

**Ready-to-use prompt:**
> Optimize nucleic acid design algorithms on NucleoBench. Download 400K experiment grid covering 16 biological tasks (TFBS, gene expression, RNA structure). Compute AdaBeam baseline (best-in-class, wins ~14/16). Split: 8 tasks evolution, 8 validation. Implement algorithm hybridization: ensemble voting for AdaBeam + Ledidi + FastSeqProp. Add meta-learner for task-specific algorithm selection. Apply sequential halving (ReSCALE-inspired) for early branch elimination. Freeze metrics: win rate (target 15+/16), convergence <6.5 iter (baseline 8), evals <200 (baseline 250). 5-6 Karpathy iterations.

---

## TECH/AI PROPOSALS (from web intelligence)

---

### Proposal 5: SpecForge-Benchmark
**Source:** ArXiv "SpecForge: Flexible Training Framework for Speculative Decoding" (2603.18567) + ArXiv "Scaling Up, Speeding Up: Benchmark of Speculative Decoding for Test-Time Scaling" (2509.04474) + NVIDIA SPEED-Bench
**Type:** experiment
**Category:** AI/ML
**Hypothesis:** Speculative decoding went from research to production in 2025-2026 (built into vLLM, SGLang, TensorRT-LLM) with 2-3x speedups at low concurrency. However, no systematic open benchmark compares n-gram-based, model-based, and training-based methods on reasoning tasks (math, code, science) with controlled test-time compute budgets. autolab can build the first unified comparison and discover which method dominates per task type.
**Method:**
- Implement 3 speculative decoding families: n-gram (simple pattern matching), model-based (small draft model), training-based (MTP heads)
- Define 4 reasoning task categories: math (GSM8K), code (HumanEval), science (MMLU-STEM), planning (WebArena subset)
- Fixed compute budget: measure tokens/second and accuracy at 1x, 2x, 5x, 10x test-time compute
- Karpathy Loop: optimize draft model size, n-gram window, acceptance threshold per task
- Compare against autoregressive baseline and Saguaro (speculative speculative decoding)
**Metrics:** Speedup ratio (tokens/sec vs autoregressive baseline) ≥2.5x; accuracy preservation ≥99% of baseline; task-specific winner identification across 4 categories
**Feasibility:** 5 — SpecForge is open-source, benchmarks are public (GSM8K, HumanEval, MMLU), CPU-viable with small models (Qwen 0.8B as draft)
**Impact:** 5 — Production-relevant, fills benchmarking gap, publishable, directly useful for autolab inference optimization
**Priority Score:** 25
**Estimated iterations:** 6-8
**Dependencies:** PyTorch, vLLM or SGLang, HuggingFace Transformers, Qwen-3.5-0.8B (draft), datasets (GSM8K, HumanEval, MMLU)

**Ready-to-use prompt:**
> Build a unified speculative decoding benchmark for reasoning tasks. Implement 3 decoding families: n-gram pattern matching, model-based (Qwen 0.8B draft), training-based (MTP heads). Test on 4 task categories: math (GSM8K), code (HumanEval), science (MMLU-STEM), planning. Fixed compute budgets: 1x, 2x, 5x, 10x test-time compute. Freeze metrics: speedup ratio (target ≥2.5x), accuracy preservation (≥99%), per-task winner. Compare to autoregressive baseline + Saguaro. Karpathy Loop: optimize draft size, n-gram window, acceptance thresholds. 6-8 iterations.

---

### Proposal 6: AutoResearchClaw-Eval
**Source:** GitHub "AutoResearchClaw: Fully autonomous research from idea to paper" (4.1K stars, v0.3.2 Mar 22, 2026) + Karpathy autoresearch (inspiration for autolab)
**Type:** experiment
**Category:** AI/ML
**Hypothesis:** AutoResearchClaw claims a 23-stage fully autonomous research pipeline (idea → literature → experiments → paper). autolab can rigorously evaluate this claim by feeding it 5 controlled research questions with known answers, measuring quality of literature review (citation accuracy), experiment design (statistical rigor), and paper quality (reviewer scores). This tests the frontier of autonomous research — directly relevant to autolab's own mission.
**Method:**
- Install AutoResearchClaw v0.3.2 in sandboxed environment
- Define 5 research prompts with known ground-truth answers (published papers autolab already has results for)
- Run AutoResearchClaw on each prompt, capture: wall-clock time, citations retrieved, experiment code generated, statistical tests used, final paper
- Score: citation accuracy (% real papers vs hallucinated), experiment reproducibility (does code run?), statistical validity (correct tests?), paper quality (automated reviewer rubric)
- Compare AutoResearchClaw output vs autolab's own results on same questions
**Metrics:** Citation accuracy ≥80% (real papers); experiment reproducibility ≥60% (code runs); statistical validity ≥70% (correct tests); wall-clock <4h per paper
**Feasibility:** 5 — Open source, CLI tool, runs on CPU, autolab has ground-truth comparisons from existing experiments
**Impact:** 4 — Meta-experiment (evaluating autonomous research), directly informs autolab evolution, high community interest
**Priority Score:** 20
**Estimated iterations:** 5 (one per research prompt)
**Dependencies:** AutoResearchClaw v0.3.2, Python 3.10+, LLM API access (Claude/GPT), OpenAlex/Semantic Scholar APIs

**Ready-to-use prompt:**
> Evaluate AutoResearchClaw's autonomous research pipeline. Install v0.3.2 in sandbox. Define 5 research prompts with known ground-truth (use autolab's completed experiments as reference: json-transformer, ray-tracer, fertilizer-design). Run AutoResearchClaw on each, capture: citations retrieved, experiment code, statistical tests, final paper. Score: citation accuracy (target ≥80% real papers), reproducibility (target ≥60% code runs), statistical validity (target ≥70%), time <4h. Compare output quality vs autolab's own results. Document strengths/weaknesses for autolab self-improvement.

---

### Proposal 7: OpenClaw-Plugin-Benchmark
**Source:** GitHub Trending "OpenClaw" (210K+ stars, breakout 2026) + obra/superpowers (92K stars, agentic skills framework)
**Type:** software
**Category:** software-engineering
**Hypothesis:** OpenClaw's explosive growth (9K → 210K stars in 60 days) with 50+ integrations represents a new paradigm for local AI assistants. autolab can build and benchmark a plugin system, measuring: integration latency, context window efficiency, and task completion rate across messaging platforms. This tests whether local-first AI assistants can match cloud API performance.
**Method:**
- Study OpenClaw plugin architecture and ACP (Agent Communication Protocol) specification
- Build 3 test plugins: file-organizer, code-reviewer, research-summarizer
- Benchmark: latency (ms per tool call), context efficiency (tokens used vs useful), task completion (% correct on 20 predefined tasks)
- Compare: local Ollama backend vs cloud API backend
- Karpathy Loop: optimize plugin response parsing, context window packing, tool routing
**Metrics:** Plugin latency <500ms per call; context efficiency >70% useful tokens; task completion ≥85% on 20 tasks; local vs cloud performance gap <15%
**Feasibility:** 5 — OpenClaw is open-source, Ollama available, plugin API documented
**Impact:** 3 — Software engineering contribution, less scientific but highly practical, extends autolab's tooling
**Priority Score:** 15
**Estimated iterations:** 4-5
**Dependencies:** OpenClaw, Ollama, Python 3.10+, small open model (Qwen 3.5 4B or similar)

**Ready-to-use prompt:**
> Build and benchmark an OpenClaw plugin system. Study OpenClaw ACP spec and plugin architecture. Create 3 test plugins: file-organizer (FS operations), code-reviewer (static analysis), research-summarizer (web search + synthesis). Benchmark: latency <500ms/call, context efficiency >70% useful tokens, task completion ≥85% on 20 tasks. Compare Ollama local vs cloud API backends. Freeze metrics before testing. Karpathy Loop: optimize response parsing, context packing, tool routing. 4-5 iterations.

---

### Proposal 8: GRACE-Alloy-Screener
**Source:** Nature npj "Graph Atomic Cluster Expansion for ML Interatomic Potentials" + ArXiv "Janus Aminobenzene-Graphene Anode for Na-ion Batteries" + ArXiv "Ideal band structures for thermoelectrics"
**Type:** experiment
**Category:** materials
**Hypothesis:** GRACE ML potentials trained on the largest materials datasets create a new Pareto front for accuracy vs efficiency. autolab can use GRACE for high-throughput screening of 10,000+ alloy structures (high-entropy alloys, Heusler compounds) in <4h CPU, identifying 50+ novel candidates for batteries or thermoelectrics, with >0.85 Spearman correlation to DFT on validation subset.
**Method:**
- Download GRACE pre-trained model and JARVIS/ICSD reference datasets
- Generate composition space: quaternary HEAs (1000 → 5000 → 10000 structures progressive)
- Batch GRACE inference with ASE + multiprocessing
- Property ranking with ensemble voting (GRACE + surrogate fallback)
- Validate: top 10 structures vs DFT reference on hold-out compositions
**Metrics:** Screening throughput ≥1500 structures/hour (baseline DFT ~10); ranking correlation >0.85 Spearman vs DFT; novel discovery >40% of top 50 not in ICSD/JARVIS
**Feasibility:** 4 — GRACE model public, ASE/pymatgen mature; structure generation may need domain expertise
**Impact:** 5 — Battery/thermoelectric materials urgently needed, extends materials-discovery, publishable
**Priority Score:** 20
**Estimated iterations:** 3-4
**Dependencies:** ASE, MACE/GRACE, pymatgen, scikit-learn, JARVIS + ICSD datasets, numpy, scipy

**Ready-to-use prompt:**
> High-throughput alloy screening with GRACE ML potentials. Download GRACE pre-trained model. Generate quaternary HEA composition space (1000→5000→10000 structures). Batch GRACE inference via ASE + multiprocessing. Target properties: band gap, thermal conductivity, formation energy. Ranking: ensemble voting (GRACE + surrogate). Freeze metrics: throughput ≥1500 struct/hr, Spearman >0.85 vs DFT, novelty >40% of top 50. Progressive screening: filter early, deep evaluation late. Validate top 10 vs DFT. 3-4 Karpathy iterations.

---

## CROSS-DOMAIN PROPOSALS (science meets AI)

---

### Proposal 9: CVAE-Protein-Designer + GRACE Validator
**Source:** PLOS CB "CVAE for PHA Synthase Design" + Nature npj "GRACE ML Potentials" + bioRxiv "ProteinMCP: Agentic Protein Engineering"
**Type:** experiment
**Category:** cross-domain (biology × materials)
**Hypothesis:** Protein design (CVAE generates enzyme variants) and materials validation (GRACE evaluates structural stability) are treated as separate domains. Combining them creates an end-to-end pipeline: CVAE generates metalloenzyme variants → GRACE validates metal-binding site stability → ESM-2 predicts function. This cross-domain pipeline can discover stable, functional metalloenzyme variants faster than either approach alone.
**Method:**
- Implement CVAE on UniProt metalloenzyme sequences (~1000 examples)
- Generate 10,000 variants with conservation constraints on catalytic residues
- Use GRACE to evaluate metal-binding site energetics (coordination geometry stability)
- ESM-2 embeddings for function prediction (activity proxy)
- Karpathy Loop: optimize CVAE latent space + GRACE filtering threshold + ESM-2 confidence cutoff
**Metrics:** Functional variant rate ≥30% (predicted functional / total generated); metal site stability >90% (GRACE pass rate); diversity >0.5 (1 - mean pairwise sequence identity); pipeline wall-clock <3h
**Feasibility:** 4 — Each component exists (CVAE, GRACE, ESM-2); integration requires cross-domain glue code
**Impact:** 5 — Novel cross-domain methodology, publishable (Nature Methods), extends both drug-discovery and materials-discovery
**Priority Score:** 21 (20 + 1 cross-domain bonus)
**Estimated iterations:** 6-8
**Dependencies:** PyTorch, ASE, MACE/GRACE, HuggingFace Transformers (ESM-2), biopython, RDKit, UniProt data

**Ready-to-use prompt:**
> Cross-domain experiment: CVAE protein design + GRACE materials validation for metalloenzyme engineering. Implement CVAE on UniProt metalloenzyme sequences (~1000). Generate 10K variants preserving catalytic residues. Filter with GRACE: evaluate metal-binding site coordination geometry stability. Score with ESM-2 embeddings for activity prediction. Freeze metrics: functional rate ≥30%, metal site stability >90%, diversity >0.5, time <3h. Karpathy Loop: optimize latent dim, GRACE threshold, ESM-2 cutoff. 6-8 iterations. Novel: first pipeline combining generative biology + ML potentials validation.

---

### Proposal 10: EvoScientist-ROM-Collective
**Source:** Papers With Code "EvoScientist" (1.6K stars) + ArXiv "ROM: Overthinking Mitigation" (2603.22016) + Papers With Code "MetaClaw: Meta-Learning in the Wild" (2.5K stars)
**Type:** experiment
**Category:** cross-domain (AI × science)
**Hypothesis:** EvoScientist (multi-agent evolutionary discovery) + ROM (inference efficiency without retraining) + MetaClaw (continuous meta-learning) form a trifecta for autolab. A multi-agent collective where each agent specializes in a domain (materials, drug, protein), shares discoveries via persistent memory, and uses ROM to reason 50% faster can achieve 85% discovery success rate (vs 60% single-agent baseline) with 2.5x fewer iterations.
**Method:**
- Scaffold 3 specialized agents (materials-agent, drug-agent, protein-agent) each in separate worktrees
- Implement shared persistent memory layer (lab/journal.md + graph-based knowledge store)
- Add ROM detection head on frozen LLM backbone for inference efficiency
- MetaClaw meta-learning: agents update policies based on sibling successes
- Karpathy Loop: evolve communication protocol, meta-learning rate, ROM thresholds per domain
**Metrics:** Discovery success rate ≥85% (baseline 60% single-agent); convergence ≤6 iterations (baseline ~15); inference latency <1.5s per agent call (baseline 2.5s)
**Feasibility:** 4 — All frameworks open-source; multi-agent coordination adds complexity; CPU-viable with small models
**Impact:** 5 — Platform-level innovation for autonomous discovery, extends artificial-life, publishable (ICML/JMLR)
**Priority Score:** 21 (20 + 1 cross-domain bonus)
**Estimated iterations:** 8-10
**Dependencies:** PyTorch, HuggingFace Transformers, EvoScientist framework, autolab git + worktrees, RAG frameworks

**Ready-to-use prompt:**
> Build a multi-agent discovery collective combining EvoScientist + ROM + MetaClaw. Scaffold 3 agents: materials-agent, drug-agent, protein-agent (separate worktrees). Shared memory: lab/journal.md + graph knowledge store. ROM: add detection head on frozen LLM for 50% inference speedup. MetaClaw: meta-learn from sibling agent successes. Freeze metrics: success rate ≥85% (baseline 60%), convergence ≤6 iter (baseline 15), latency <1.5s (baseline 2.5s). Karpathy Loop: evolve communication protocol, meta-learning rate, ROM thresholds. 8-10 iterations. This is autolab's self-improvement experiment.

---

### Proposal 11: Solvent-Mixture-ML-Optimizer
**Source:** Nature npj "30,000+ Solvent Mixtures Dataset via Classical MD" + ArXiv "CurvZO: Zeroth-Order Optimization" + GitHub Trending (RAGFlow, speculative decoding production tools)
**Type:** experiment
**Category:** cross-domain (chemistry × AI optimization)
**Hypothesis:** A public dataset of 30,000+ solvent mixtures with calculated properties (viscosity, diffusivity, density) enables ML-driven formulation optimization. Applying CurvZO (zeroth-order optimization, no gradients needed) to navigate the composition space can discover optimal solvent formulations for battery electrolytes or catalysis solvents using only forward passes — making it CPU-friendly and applicable to black-box property predictors.
**Method:**
- Download 30K solvent mixture dataset, split 80/20 train/test
- Train property predictors: NN, RF, XGBoost for viscosity, diffusivity, density
- Implement CurvZO optimizer: curvature-guided zeroth-order search over composition space
- Define target: minimize viscosity + maximize diffusivity for battery electrolyte application
- Karpathy Loop: evolve model architecture, CurvZO perturbation budget, curvature signal, sparse update strategy
**Metrics:** Property prediction MAE <5% normalized error (3 properties); active learning efficiency: reach 5% error with ≤30% of data; novel formulation discovery: ≥5 compositions with Pareto-optimal viscosity/diffusivity not in training set
**Feasibility:** 5 — Public dataset, standard ML, CurvZO is forward-pass only (CPU-friendly), clear targets
**Impact:** 4 — Practical application (battery electrolytes), novel optimization method application, extends fertilizer-design patterns
**Priority Score:** 21 (20 + 1 cross-domain bonus)
**Estimated iterations:** 5-7
**Dependencies:** scikit-learn, PyTorch (optional), numpy, scipy, pandas, CurvZO optimizer (custom implementation), 30K mixture dataset

**Ready-to-use prompt:**
> Optimize solvent mixture formulations using ML + zeroth-order optimization. Download 30K solvent mixture dataset (viscosity, diffusivity, density). Train property predictors: NN + RF + XGBoost ensemble. Implement CurvZO zeroth-order optimizer (no gradients, forward passes only) to search composition space. Target: minimize viscosity + maximize diffusivity for battery electrolytes. Freeze metrics: prediction MAE <5% normalized, sample efficiency ≤30% data for 5% error, ≥5 Pareto-optimal novel formulations. Karpathy Loop: evolve model, CurvZO perturbation/curvature, sparse updates. 5-7 iterations.

---

## RANKING BY PRIORITY SCORE

| Rank | Proposal | Priority | Category |
|------|----------|----------|----------|
| 1 | FLIP2-Optimizer | 25 | scientific |
| 2 | PODGen-Materials | 25 | scientific |
| 3 | SpecForge-Benchmark | 25 | tech/AI |
| 4 | CVAE-Protein + GRACE | 21* | cross-domain |
| 5 | EvoScientist-ROM-Collective | 21* | cross-domain |
| 6 | Solvent-Mixture-ML | 21* | cross-domain |
| 7 | iScore-Drug-Affinity | 20 | scientific |
| 8 | AutoResearchClaw-Eval | 20 | tech/AI |
| 9 | GRACE-Alloy-Screener | 20 | materials |
| 10 | NucleoBench-Algorithm-Mixer | 16 | scientific |
| 11 | OpenClaw-Plugin-Benchmark | 15 | tech/AI |

**TOP 3 RECOMMENDED:** FLIP2-Optimizer, PODGen-Materials, SpecForge-Benchmark

---

## EXECUTION PLAN

**Week 1 (immediate):** Launch top 3 in parallel worktrees
- FLIP2-Optimizer: protein fitness landscape (CPU, 2-3h)
- PODGen-Materials: generative materials discovery (CPU, 2-3h)
- SpecForge-Benchmark: speculative decoding comparison (CPU, 3-4h)

**Week 2:** Launch cross-domain proposals
- CVAE-Protein + GRACE: metalloenzyme design pipeline
- Solvent-Mixture-ML: battery electrolyte optimization
- iScore-Drug-Affinity: binding affinity ensemble

**Week 3:** Meta-experiments
- EvoScientist-ROM-Collective: autolab self-improvement
- AutoResearchClaw-Eval: autonomous research evaluation

**Week 4:** Integration and publication
- Cross-reference results, attempt proposal combinations
- Document findings for submission

---

## WEAK SIGNALS (monitor, don't execute yet)

1. **Qwen 3.5 Small (0.8B-9B) multimodal** — potential draft model for SpecForge; monitor benchmarks
2. **obra/superpowers (92K stars)** — agentic skills framework; may complement OpenClaw plugin work
3. **NVIDIA Nemotron 3 Super (120B)** — enterprise coding model; too large for autolab CPU but results inform nanoGPT direction
4. **Quantum protein design (bioRxiv)** — requires proprietary hardware; monitor for classical approximation papers
5. **SAE interpretability (bioRxiv)** — 30% feature stability too low; monitor for improvements

---

## DEDUPLICATION CHECK

Verified against BACKLOG.md — no duplicates:
- 001 json-transformer (done) — no overlap
- 002 markdown-link-checker (ready) — no overlap
- 003 git-commit-analyzer (ready) — no overlap
- 004 api-rate-limiter (ready) — no overlap
- 005 llm-routing-research (ready) — SpecForge-Benchmark is complementary (different angle: decoding vs routing)
- 006 ray-tracer (done) — no overlap
- Existing experiments (fertilizer-design, drug-discovery, etc.) — proposals EXTEND, not duplicate

---

*Generated: 2026-03-24 15:00 UTC*
*Engine: CEREBRO Hypothesis Engine v2*
*Sources: 4 scientific scouts (57 papers), web intelligence (GitHub trending, AI news, ArXiv AI)*
*Confidence: High — 11/11 proposals pass feasibility filter, 8/11 have frozen public benchmarks*
