# autolab — Autonomous Experiment Laboratory

An autonomous agent that creates and evolves experiments using the Karpathy Loop: **hypothesis → experiment → measure → accept/reject → repeat.**

## How It Works

You give autolab an idea. It creates an experiment with a frozen evaluator and one editable file. Then it iterates: hypothesize, modify, measure, keep or revert. Until it plateaus or hits the target.

## The Karpathy Loop

Every experiment follows this cycle:

```
1. READ      → Understand current best from <editable>.py
2. HYPOTHESIZE → What modification might improve the score?
3. MODIFY    → Edit the ONE editable file
4. EVALUATE  → Run: python prepare.py evaluate <candidate>
5. DECIDE    → Better? Keep + commit. Worse? Revert + log.
6. LOG       → Append ALL results to results.tsv (even failures)
7. REPEAT    → Until exit condition met
```

## Experiment Structure

Every experiment has exactly this structure:

```
experiments/<name>/
├── prepare.py      # FROZEN evaluator — NEVER modify this
├── <editable>.py   # The ONLY file to modify during the loop
├── program.md      # Loop instructions, exit conditions, strategy
├── METRICS.md      # Frozen success criteria
├── results.tsv     # Append-only log of every attempt
├── renders/        # Visual evidence (optional)
└── data/           # Test data (optional)
```

**The separation is the key design choice:**
- `prepare.py` = frozen truth (defines what "good" means)
- `<editable>.py` = what Claude mutates (the candidates)
- Claude cannot move the goalposts because it cannot touch the evaluator.

## Skills

| Skill | Purpose | When |
|-------|---------|------|
| /experiment | Create a new Karpathy Loop experiment | When starting a new idea |

## Creating an Experiment

Use `/experiment <name> <description>` to create a new experiment. This:

1. Creates the directory structure in `experiments/<name>/`
2. Writes the frozen evaluator (`prepare.py`)
3. Creates the editable file with a baseline
4. Writes `program.md` with loop instructions
5. Creates `METRICS.md` with frozen success criteria
6. Validates that baseline runs correctly
7. Commits to git

## Running an Experiment

Tell Claude to read `program.md` and execute the loop:

```
> Read experiments/<name>/program.md and execute the optimization loop.
```

Each experiment's `program.md` contains domain-specific instructions: exit conditions, strategy phases, scoring breakdown, and tips.

## Setup (First Time)

If git identity is not configured for this repo:
```
git config user.name "autolab"
git config user.email "autolab@local"
```

## Safety Rules

These are non-negotiable:

1. **NEVER modify prepare.py.** It's the frozen evaluator.
2. **ONLY modify the editable file** during optimization loops.
3. **METRICS.md is frozen after creation.** No moving goalposts.
4. **Log ALL results to results.tsv.** Even failures teach us.
5. **One change per iteration.** Atomic, measurable, revertible.
6. **Exit conditions are real.** Max experiments, plateau detection, target score.
7. **Git is the safety net.** Everything is committed. Everything is revertible.
8. **NEVER modify root-level files during experiment loops.** These belong to autolab itself:
   - `README.md`, `CLAUDE.md`, `LICENSE`, `.claude/settings.json`

## File Structure

```
autolab/
├── CLAUDE.md                    # This file — the constitution
├── experiments/                 # All experiments live here
│   ├── antibiotic-discovery/    # Novel gram-neg antibiotics
│   ├── drug-discovery/          # Drug-like molecule optimization
│   ├── fertilizer-design/       # Slow-release nitrogen carriers
│   ├── materials-discovery/     # Solar cell materials
│   ├── artificial-life/         # Lenia cellular automaton
│   ├── compression/             # Data compression algorithm
│   ├── nanoGPT/                 # GPT optimization
│   ├── nootropic-discovery/     # Cognitive enhancer design
│   └── prompt-optimizer/        # LLM prompt engineering
├── lab/
│   ├── journal.md               # Append-only activity log
│   └── scoreboard.md            # Best results per experiment
└── .claude/
    ├── settings.json            # Hooks configuration
    ├── hooks/                   # Session hooks
    └── skills/
        └── create-experiment/   # /experiment skill
```

## Hooks

| Hook | Type | Purpose |
|------|------|---------|
| SessionStart | command | Inject lab state (experiments, journal, scoreboard) |
| SessionEnd | command | Log session duration |
| Stop | prompt | Evaluate if journal needs updating |

## Conventions

- Journal: append-only, format `[YYYY-MM-DD HH:MM:SS] ACTION | experiment | details`
- Commits: `exp N: description — composite score` (within experiments)
- Results TSV: experiment-specific columns, append-only

## Resuming After Interruption

The lab is designed for interruption-resilience:

- `lab/journal.md` records the last action taken
- Each experiment's `results.tsv` tracks progress
- SessionStart hook reads all of this and injects it as context

To resume: just open Claude Code in the autolab directory. The hook does the rest.
