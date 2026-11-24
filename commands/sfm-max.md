---
description: Exhaustive Sfumato Tournament (opt-in only) — sweeps ALL eligible domains via 2-round Cluster Playoffs + Grand Final Red-Team
argument-hint: <high-stakes problem statement>
---

Read and execute the installed `sfumato` skill (from the active plugin's `skill/sfumato/SKILL.md` or `~/.claude/skills/sfumato/SKILL.md`) in **explicit `max` mode (2-Round Cluster-Playoff Tournament)**.

**MANDATORY SAFETY GATE:**
1. Always pass `--all --safe-profile claude` to `sample_domains.py` (66 safe domains across all 11 clusters — verified at 0 bio/cyber refusals in benchmarks).
2. **STOP and confirm with the user BEFORE spawning any subagents**, stating the exact planned session count (**79–80 isolated sessions**: 66 Stage-1 remote solvers across 11 cluster waves + 1 Direct Anchor solver + 11 Cluster Red-Team Judges + 1 Grand Final Judge + optional Stage 2b Hardening) so tokens are never spent accidentally.
3. Only after explicit user confirmation, run Round 1 in cluster waves (1 cluster = 6 domains per wave, 1 isolated Cluster Judge picks Top-1 Cluster Champion) alongside 1 isolated Direct Anchor solver, then feed the 11 Cluster Champions + 1 Direct Anchor (12 unlabeled finalists) into Round 2 Grand Final Red-Team Triage + optional Stage 2b Hardening.

$ARGUMENTS
