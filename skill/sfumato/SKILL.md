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

- **Available macro-clusters (8):** `biology_ecology`, `physics_engineering`, `history_institutions`, `intelligence_conflict`, `markets_law`, `craft_operations`, `art_performance`, `social_anthropology`
- **Default (`dual-track`):** `--k 4` (2 Explicit + 2 Blind). Use `--k 6` ONLY when the user explicitly requests `deep` mode.
- **Claude Code Safety Profile:** When running on **Claude / Claude Code**, always append `--safe-profile claude` to exclude bio-pathogen, nuclear, cyber/EW, and espionage domains that can trigger false-positive safety refusals during Blind Masking (32 rich domains across all 8 clusters remain available). On Antigravity/Codex, omit it to use the full 40-domain pool.

```powershell
python "<skill_dir>/scripts/sample_domains.py" --k 4 --exclude-clusters <same_cluster_if_any>
# On Claude Code:
python "<skill_dir>/scripts/sample_domains.py" --k 4 --safe-profile claude --exclude-clusters <same_cluster_if_any>
```

### 3. Prepare Track B Isomorphic Masks (Crucial!)
Before spawning subagents, rewrite the problem brief for each Track B domain so that:
1. **Zero original-domain vocabulary survives** (no app/SNS/game/marketing/code terms if those belong to the original domain).
2. **All structural invariants survive** (topology, friction limits, failure modes, asymmetric costs).
3. **Incentive polarity is strictly preserved:** Never mask an **adversarial / zero-sum** conflict into a cooperative or centrally-refereed system (e.g., do not map rival armies to firms sharing one cooperative clearinghouse unless a real shared referee exists). Mismatched polarity is the #1 cause of Track B translation loss.

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

### 6. Clean-Context Red-Team Gate & Top-K Selection
Normalize surviving Track A + translated Track B candidates into an identical, unlabeled format (`Candidate 1..N`) and run **1 fresh clean-context evaluator subagent** using the 3-step rubric in [prompt_templates.md](./references/prompt_templates.md):
1. **Cut Surface Metaphors:** Reject any idea whose underlying causal mechanism is identical to a standard cliché with fancy domain jargon pasted on top.
2. **Red-Team Killer-Flaw Gate (Mandatory before ranking):** Test every candidate for:
   - **Adverse Selection:** Does it accidentally punish legitimate/casual users MORE than the adversary (e.g., 48h deadlines that 24/7 bots beat easier than humans)?
   - **Exploit / Sybil / Wash-Trading:** Can two colluding fake accounts trivially break or farm it (e.g., negative-fee arbitrage, self-vouching)?
   - **Constraint / Feasibility Violation:** Does it secretly rely on a banned mechanism (e.g., hidden AI judge) or impossible automation?
   Any candidate failing this gate is **disqualified from Top-1** (note it briefly as a "Wildcard needing redesign" if its core spark is still inspiring).
3. **Select for Peak Ceiling Among Survivors:** Pick **Top-1 (Champion)** + **2 Distinct Runners-Up** (maximizing structural diversity across picks), plus optional **1 Wildcard** if a Track B outlier sparked a sharp angle despite a fixable flaw.
4. **Report Conclusion-First:** Lead with the Top-1~3 picks (each showing: Mechanism, Why It's Hard to Defeat/Copy, Concrete Trade-Off, and Source Track/Domain), plus a compact summary of Red-Team cuts and cross-domain convergences.

---

## Modes & Defaults

| Mode | Configuration | When to Use |
|---|---|---|
| `dual-track` *(default)* | **K=4** (2 Explicit + 2 Blind) → Red-Team Selector | Standard fast dogfooding & serious brainstorming |
| `deep` | **1 Direct Anchor + K=6** (3 Explicit + 3 Blind) → Red-Team Selector | High-stakes breakthroughs — guarantees `max(Direct, Explicit, Blind) ≥ Direct` floor while raising the ceiling |
| `fast` | **K=3** (3 Explicit) → Red-Team Selector | Quick practical ideation when time/tokens are tight |

> **Why `Direct Anchor` in `deep` mode?** On engineering-native problems where a direct domain solution is already near-optimal, including 1 isolated `Direct Baseline` candidate in the unlabeled selector pool prevents regressions below baseline while letting Track A/B win whenever a cross-domain breakthrough genuinely dominates.

## Validation Checklist
- [ ] Domains were sampled via `scripts/sample_domains.py` in a single call (default `--k 4`).
- [ ] Every Track B prompt contains **zero** leaked terms from the original domain AND preserves **incentive polarity**.
- [ ] All divergent subagents ran isolated with zero shared conversation history and zero tool calls.
- [ ] Final picks were selected by a clean-context evaluator and change the **causal/incentive structure**, not just wording.
