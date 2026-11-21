---
description: Exhaustive Sfumato Tournament (opt-in only) — sweeps ALL eligible domains via 2-round Cluster Playoffs + Grand Final Red-Team
argument-hint: <high-stakes problem statement>
---

Read and execute the `sfumato` skill (`~/.claude/skills/sfumato/SKILL.md`) in **explicit `max` mode (2-Round Cluster-Playoff Tournament)**.

**MANDATORY SAFETY GATE:**
1. Always pass `--all --safe-profile claude` to `sample_domains.py` (66 safe domains across all 11 clusters, 0 bio/cyber refusals).
2. **STOP and confirm with the user BEFORE spawning any subagents**, stating the exact planned session count (~78 isolated sessions: 66 Stage-1 solvers across 11 cluster waves + 11 Cluster Red-Team Judges + 1 Grand Final Judge + optional Stage 2b Hardening) so tokens are never spent accidentally.
3. Only after explicit user confirmation, run Round 1 in cluster waves (1 cluster = 6 domains per wave, 1 isolated Cluster Judge picks Top-1 Cluster Champion), then feed the 11 Cluster Champions + 1 Direct Anchor into Round 2 Grand Final Red-Team + Stage 2b Hardening.

$ARGUMENTS
