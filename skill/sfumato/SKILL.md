---
name: sfumato
description: >-
  Sfumato — Dual-Track Cross-Domain Ideation (Explicit Analogy + Blind Isomorphic Reframing)
  using isolated parallel subagents and a clean-context selector to erase domain boundaries,
  break LLM homogenization, and maximize peak (Top-1) creative quality.
  Trigger explicitly when the user invokes `/sfumato`, `/sfm`, or asks to run Sfumato.
  Trigger autonomously ONLY when the user asks for high-ceiling, non-obvious brainstorming on
  hard open-ended problems (new product strategy, game mechanics, system breakthroughs, escaping
  AI clichés) — do NOT auto-trigger on trivial naming, minor copy tweaks, or closed-ended tasks.
---

# Sfumato (`/sfumato`, `/sfm`) — Cross-Domain Ideation

Named after Leonardo da Vinci's *sfumato* technique (dissolving rigid borders to let new forms emerge), this skill dissolves a problem's domain borders to escape LLM mode collapse (*Artificial Hivemind*) and maximize the **peak creativity ceiling (Top-1 hit rate)**.

## Core Principle: The Domain-Masking Trade-off

- **Track A — Explicit Analogy** *(original problem visible + assigned remote domain)*: High hit-rate and surgical precision against domain-specific constraints, but vulnerable to partial homogenization back toward industry clichés.
- **Track B — Blind Isomorphic Reframing** *(original domain vocabulary completely erased → solved blind in an isolated session → back-translated)*: Lower average hit-rate (some ideas won't translate cleanly), but **zero cliché gravity**, producing true outlier mutations impossible in Track A.
- **Stage 2 — Clean-Context Selection**: A fresh, uncontaminated evaluator filters out surface metaphors ("jargon cosplay") and selects the highest-ceiling Top-1~3 ideas.

---

## Step-by-Step Procedure

### 1. Frame the Problem (Neutral & Compact)
Distill the user's request into a crisp 3–5 bullet problem brief:
- **Core Goal** (what must change)
- **Structural Constraints & Incentive Polarity** (hard limits + whether actors are **zero-sum/adversarial**, **cooperative**, or **platform-refereed**)
- **Why Obvious Fixes Fail** (explicitly ban the top 2–3 clichés so neither track wastes budget on them)

### 2. Sample Truly Distant Domains (Single Command — Never LLM Choice)
Never ask an LLM to "pick random domains" (it repeats ants, jazz, and chess). Run the bundled stratified sampler directly (no need to run `--list-clusters` first):

- **Available macro-clusters (11):** `biology_ecology`, `physics_engineering`, `history_institutions`, `intelligence_conflict`, `markets_law`, `craft_operations`, `art_performance`, `social_anthropology`, `cognition_pedagogy`, `materials_chemistry`, `earth_navigation_grids`
- **Default (`dual-track`):** `--k 4` (2 Explicit + 2 Blind). Use `--k 6` for `deep`, `--k 11` for `sweep`, or `--all` ONLY when the user explicitly requests `max` / `/sfm-max`.
- **Claude Code Safety Profile:** When running on **Claude / Claude Code**, always append `--safe-profile claude` to exclude bio-pathogen, nuclear, cyber/EW, and espionage domains that can trigger false-positive safety refusals during Blind Masking (66 rich domains — exactly 6 per cluster across all 11 clusters — remain available). On Antigravity/Codex, omit it to use the full 74-domain pool across 11 clusters.

```powershell
python "<skill_dir>/scripts/sample_domains.py" --k 4 --exclude-clusters <same_cluster_if_any>
# On Claude Code:
python "<skill_dir>/scripts/sample_domains.py" --k 4 --safe-profile claude --exclude-clusters <same_cluster_if_any>
```

### 3. Prepare Track B Isomorphic Masks via a 3-Line Structural Skeleton (Crucial!)
Before spawning Track B subagents, do **NOT** jump straight from the original problem to a remote-domain story (that leaks clichés or loses constraints). Use a 2-step masking pass:
1. **Extract a 3-Line Domain-Neutral Structural Skeleton:**
   - `Actors & Incentive Polarity:` (zero-sum/adversarial vs. cooperative vs. platform-refereed)
   - `Core Asymmetry / Bottleneck:` (where effort, information, or friction is lopsided)
   - `Why Static Controls Fail:` (exact failure mode of obvious fixes)
2. **Map Skeleton → Target Domain + Zero-Leak Check:**
   - Rewrite the skeleton using 100% native nouns of the target domain (**zero** leaked original-domain jargon).
   - **Strict Polarity Preservation:** Never map zero-sum enemies onto a cooperative central authority (and vice versa) — mismatched polarity is the #1 cause of Track B translation loss.

See [prompt_templates.md](./references/prompt_templates.md) for the exact templates and masking checklist.

### 4. Launch Isolated Parallel Subagents (No Cross-Talk!)
Spawn all Track A and Track B solvers **in parallel in separate, clean-context subagents** (`invoke_subagent` with `TypeName: "self"`, `Model: "inherit"` in Antigravity; `Agent` tool in Claude Code).
- **Hard Rule 1 (No Cross-Talk):** Divergent solvers must NEVER see each other's outputs (prevents *Diversity Collapse*).
- **Hard Rule 2 (Pure Internal Knowledge):** Instruct each subagent **not** to call tools, read files, or search the web, and to propose exactly 2 concrete structural mechanisms.
- **UX Hygiene:** While waiting for parallel subagents, keep intermediate status notes to a bare minimum (1 short line) and never analyze partial results before all solvers return.

### 5. Back-Translate Track B (Mechanism Only, Never Cosplay)
For each Track B output:
- Extract the **causal mechanism + trade-off** and translate it cleanly into the original problem's language.
- **Be ruthless:** If a Track B idea only maps via a strained pun or relies on an impossible assumption (e.g., cooperative central ledger in an adversarial problem), discard it cleanly and log the reason. High ceiling requires tolerating discards.

### 6. Clean-Context Red-Team Triage (Stage 2a) & Hardening Pass (Stage 2b)
Normalize surviving Track A + translated Track B (+ Direct Anchor if used) candidates into an identical, unlabeled format (`Candidate 1..N`) and run **Stage 2a** (1 fresh clean-context evaluator subagent) using [prompt_templates.md](./references/prompt_templates.md):
1. **Cut Surface Metaphors:** Reject any idea whose underlying causal mechanism is identical to a standard cliché with fancy domain jargon pasted on top.
2. **Red-Team Killer-Flaw Triage:** Classify every candidate's flaws into **Unfixable** (disqualify from Top-1: e.g., fundamental polarity mismatch, wash-trading/sybil break, banned AI judge) vs. **Fixable Edge-Case** (promotable to Stage 2b Hardening).
3. **Select Top-1 Champion + 2 Distinct Runners-Up (+ Optional Wildcard).**
4. **Stage 2b — Clean-Context Hardening & Grafting Pass *(optional in `fast`, default in `dual-track`/`deep`)*:**
   - Take ONLY the winning Top-1 candidate (whether Cross-Domain or Direct Anchor — **never force-graft a polarity-mismatched cross-domain seed over a stronger Direct Anchor**) + its single biggest Red-Team edge-case critique (and optionally graft 1 practical primitive from a runner-up).
   - Run 1 clean-context engineering pass to patch that exact edge case without diluting the core non-obvious mechanism.
5. **Report Conclusion-First:** Lead with the hardened Top-1 Champion + 2 Runners-Up (+ Wildcard if any), each showing Mechanism, Why It's Hard to Defeat/Copy, Concrete Trade-Off, and Source Track/Domain, plus compact Red-Team notes.

---

## Modes & Defaults

| Mode | Configuration | When to Use |
|---|---|---|
| `dual-track` *(default)* | **K=4** (2 Explicit + 2 Blind) → Red-Team Selector | Standard fast dogfooding & serious brainstorming |
| `deep` | **1 Direct Anchor + K=6** (3 Explicit + 3 Blind) → Red-Team Selector | High-stakes breakthroughs — guarantees `max(Direct, Explicit, Blind) ≥ Direct` floor while raising the ceiling |
| `fast` | **K=3** (3 Explicit) → Red-Team Selector | Quick practical ideation when time/tokens are tight |
| `sweep` *(opt-in only)* | **1 Direct Anchor + K=11** (1 per macro-cluster, alternating Explicit/Blind) → Red-Team Selector | Full 11-cluster coverage in one wave without selector overload |
| `max` (`/sfm-max`, *opt-in only*) | **All 66 (Claude) / 74 domains** → **2-Round Tournament** (11 Cluster Playoffs → 12-finalist Grand Final + Stage 2b Hardening) | Exhaustive high-budget brainstorming ("Company-Card Mode") for major strategy, product moats, or core mechanics |

> **Why `Direct Anchor` in `deep` / `sweep` / `max`?** On engineering-native problems where a direct domain solution is already near-optimal, including 1 isolated `Direct Baseline` candidate in the unlabeled selector pool prevents regressions below baseline while letting Track A/B win whenever a cross-domain breakthrough genuinely dominates.

### Opt-In `max` (`/sfm-max`) Tournament Protocol & Guardrails
- **NEVER auto-trigger `max` or `sweep`.** Run ONLY when the user explicitly asks for `sweep`, `max`, or `/sfm-max`.
- **Mandatory Pre-Flight Confirmation (`max`):** Before spawning any subagents in `max` mode, display the exact session count (~78 sessions on `--safe-profile claude` / ~86 on `full`) and ask the user to confirm.
- **Why 2-Round Tournament (Never Dump 148 Ideas into 1 Selector):** Dumping 130+ raw ideas into one Stage 2 evaluator degrades judgment (*Lost-in-the-Middle*). Instead:
  1. **Round 1 — Cluster Playoffs (11 waves):** Run `sample_domains.py --all` (with `--safe-profile claude` on Claude). Execute in cluster waves (6–8 concurrent subagents per wave to respect API rate limits). After each cluster finishes, 1 fresh Cluster Red-Team Judge picks that cluster's **Top-1 Champion** (optionally 1 Wildcard).
  2. **Round 2 — Grand Final:** Pass the **11 unlabeled Cluster Champions + 1 Direct Anchor (12 finalists)** into 1 fresh Clean-Context Grand Final Red-Team Selector + Stage 2b Hardening Pass.

## Validation Checklist
- [ ] Domains were sampled via `scripts/sample_domains.py` in a single call (default `--k 4`).
- [ ] Every Track B prompt contains **zero** leaked terms from the original domain AND preserves **incentive polarity**.
- [ ] All divergent subagents ran isolated with zero shared conversation history and zero tool calls.
- [ ] Final picks were selected by a clean-context evaluator and change the **causal/incentive structure**, not just wording.
