# Prompt Templates for Sfumato

Use these templates when spawning isolated subagents:
- **Antigravity (`agy`):** `invoke_subagent` with `TypeName: "self"`, `Model: "inherit"`
- **Claude Code:** `Agent` tool (fresh subagent, no shared history)
- **Codex CLI:** isolated subagent if supported, or sequential clean-context `codex exec` / isolated turns with zero prior solver outputs

Always forbid tool calls inside divergent solvers so they draw cleanly from pretrained domain structures, and pass `{USER_LANGUAGE}` (matching the user's prompt language, e.g., English, Korean, Russian, Simplified Chinese) so outputs never drift into a hardcoded language.

---

## 0. Direct Anchor Prompt (Default in `dual-track` & `deep` Modes)

```text
Do NOT call any tools (no file reads, no web search, no shell commands). Answer purely from internal knowledge. Respond in {USER_LANGUAGE}.

[Problem]
{PROBLEM_BRIEF}

[Banned Clichés (Do NOT propose these or thin reskins of them)]
{BANNED_CLICHES}

[Request]
Propose the 2 strongest, most concrete structural mechanisms to solve this problem directly within its native domain — without falling back on the banned clichés above.
Every proposal must change the underlying causal, incentive, or operational trade-off structure, not just UI wording or surface policy.

Format each proposal concisely with depth:
- [Mechanism Name]
- [Core Structural Principle]
- [Concrete Operating Steps]
- [Why It Beats Obvious Fixes & Resists Gaming/Bypass]
- [Key Trade-Offs & Mitigations]
```

---

## 1. Track A — Explicit Cross-Domain Analogy Prompt

```text
Do NOT call any tools (no file reads, no web search, no shell commands). Answer purely from internal knowledge. Respond in {USER_LANGUAGE}.

[Original Problem]
{PROBLEM_BRIEF}

[Banned Clichés (Do NOT propose these or thin reskins of them)]
{BANNED_CLICHES}

[Request]
Exclude the obvious approaches above. Using Cross-Domain Analogy, port actual structural principles, institutions, or physical/operational mechanisms from **{DOMAIN_NAME}** to solve this problem. Propose **2** original, concrete mechanisms.
Do NOT do jargon cosplay or surface metaphors — the underlying causal chain, incentive polarity, or trade-off structure must genuinely change.

Format each proposal concisely with depth:
- [Mechanism Name]
- [Borrowed Principle from {DOMAIN_NAME}]
- [Concrete Operating Steps]
- [Why It Beats Obvious Fixes & Resists Gaming/Bypass]
- [Key Trade-Offs & Mitigations]
```

---

## 2. Track B — Blind Isomorphic Reframing

### Step 2a. 3-Line Structural Skeleton & Code-Verified Zero-Leak Masking (Coordinator Performs Before Spawning)
First, distill the problem into a **3-line domain-neutral Structural Skeleton** (zero original-industry words):
```text
- Actors & Incentive Polarity: <e.g., zero-sum rivals / two cooperative parties vs. a third-party mediator / novice creator vs. complex tool>
- Core Asymmetry / Bottleneck: <exact cost, information, physics, or cognitive imbalance>
- Why Static Controls Fail: <exact failure mode of obvious rules, filters, or tutorials>
```
Then rewrite that skeleton entirely inside `{DOMAIN_NAME}` and verify:
1. **Code-verified zero leaked vocabulary:** Extract 8–15 banned nouns/jargon from the original problem (e.g., for an SNS spam problem: `sns,app,post,account,spam,bot,dm,platform,user`; list irregular inflections explicitly, since ASCII matching covers base + plural/possessive `s`/`es`/`'s`) and run `python "<skill_dir>/scripts/check_leak.py" --terms "<banned_terms>" --text "<masked_scenario>"` (or `--file <masked_file>` / stdin). Do NOT spawn the Blind solver until it exits `0` (`PASS`).
2. **Exact structural isomorphism:** Preserve topology, friction limits, failure modes, and asymmetric costs using 100% native nouns of `{DOMAIN_NAME}`.
3. **Incentive polarity fidelity (CRITICAL):** Preserve whether the real actors are **adversarial / zero-sum**, **cooperative**, **physical-loop**, or **mediated by a neutral referee**. Never map zero-sum enemies onto cooperative institutions sharing a mutual ledger/bailout unless a real referee exists — polarity mismatch is the #1 cause of Track B back-translation failure.

### Step 2b. Blind Solver Subagent Prompt

```text
Do NOT call any tools (no file reads, no web search, no shell commands). Answer purely from internal knowledge. Respond in {USER_LANGUAGE}.

[Scenario]
{ISOMORPHIC_MASKED_SCENARIO_IN_TARGET_DOMAIN}

[Request]
Do NOT propose obvious fixes like {MASKED_BANNED_CLICHES}. Using real principles from **{DOMAIN_NAME}**, propose **2** original, concrete designs that directly break the core constraint above.

Format each design concisely with depth:
- [Design Name]
- [Core Principle]
- [Operating Steps]
- [Why It Resists Evasion / Failure]
- [Trade-Offs & Side Effects]
```

### Step 2c. Back-Translation Rule (Coordinator Performs After Blind Solver Returns)
- Port ONLY the **causal mechanism, incentive/physics shift, and trade-off** back into the original problem's concrete primitives.
- **Discard ruthlessly:** If translating a Blind idea requires a strained pun or relies on an impossible assumption (e.g., cooperative trust in a zero-sum game), drop it cleanly and log it as a translation loss. Do NOT pad weak ideas.

---

## 3. Stage 2a — Clean-Context Red-Team Triage & Top-K Selector Prompt (v2.0)

Strip all track labels, domain names, and framing transcripts, normalize surviving candidates into an identical anonymous format (`Candidate 1..N`), and spawn **1 fresh clean-context subagent**:

```text
Do NOT call any tools. Answer purely by critical engineering and mechanism-design judgment. Respond in {USER_LANGUAGE}.

[Original Problem & Constraints]
{PROBLEM_BRIEF}

[Candidate Ideas (Anonymized — Sources Hidden)]
{NORMALIZED_ANONYMIZED_CANDIDATES}

[Evaluation Rules — 3-Step Red-Team Triage + Peak-Ceiling Selection]
1. **Cut Surface Metaphors (KILL):** Reject any candidate whose real causal structure is identical to a banned cliché with fancy terminology pasted on top.
2. **Red-Team Flaw Triage (PASS / HARDEN / KILL):** Stress-test every remaining candidate against:
   - (a) **Adverse Selection:** Does it hurt legitimate users/newcomers more than bad actors or edge cases?
   - (b) **Sybil / Wash-Trading / Gaming Exploit:** Can 2 colluding accounts, bots, or degenerate strategies trivially farm or break it?
   - (c) **Feasibility & Premise Violations:** Does it sneak in a banned premise (e.g., hidden AI judge, deficit subsidy) or fail basic operational/UX feasibility?
   Classify every candidate explicitly into one of three buckets:
   - `PASS`: Ready as-is (no structural blocker).
   - `HARDEN`: High-ceiling core mechanism, but has **1 specific fixable operational/edge-case weakness** worth repairing in Stage 2b.
   - `KILL`: Unfixable structural flaw (fundamental polarity mismatch, fatal exploit, or cliché cosplay). Disqualified from Top-1.
3. **Select Top-1 Champion + 2 Distinct Runners-Up:** Pick the highest **Structural Novelty × Practical Impact** winner from `PASS` and `HARDEN` candidates (never force a weaker cross-domain candidate over a genuinely stronger one). Runners-up (#2, #3) must represent genuinely distinct mechanism axes from Top-1.

[Required Output Format]
1. **Triage Table:** For every candidate (`Candidate 1..N`), state `PASS | HARDEN | KILL` + 1-line rationale.
2. **Top-1 (Champion):** Candidate #, status (`PASS` or `HARDEN`), 2-line core mechanism summary, why it is non-obvious and strong, and **Single Biggest Fixable Flaw** (explicitly formatted for Stage 2b Hardening).
3. **Runners-Up (#2 and #3):** Candidate #, 3-line summary each, plus 1 concrete practical primitive (if any) that could strengthen Top-1.
4. **Wildcard (Optional, max 1):** A `KILL`-ed mutation whose core insight is still sharp enough to note for the user.
```

---

## 4. Stage 2b — Clean-Context Hardening & Selective Grafting Pass (v2.0)

Run **1 fresh clean-context subagent** ONLY on the **winning Top-1 candidate** from Stage 2a (skip if Stage 2a rated Top-1 `PASS` with no meaningful operational flaw, or in `fast` mode). Never force-graft a polarity-mismatched cross-domain seed over a stronger Direct Anchor:

```text
Do NOT call any tools. Answer from a rigorous, practical engineering and product-design perspective. Respond in {USER_LANGUAGE}.

[Original Problem & Constraints]
{PROBLEM_BRIEF}

[Stage 2a Winning Top-1 Candidate]
{TOP1_CANDIDATE}

[Single Biggest Fixable Flaw Diagnosed by Red-Team]
{SINGLE_BIGGEST_FLAW}

[Optional Grafting Primitive (1 proven practical mechanism from a passing runner-up; omit if none)]
{OPTIONAL_GRAFT_PRIMITIVE}

[Request]
Repair and harden ONLY the diagnosed operational/edge-case weakness so the design is immediately shippable — **without diluting the core non-obvious mechanism or reverting it into a generic cliché.**
Output a crisp final spec:
- [Final Mechanism Name]
- [Core Structural Mechanism]
- [Concrete Operating Flow]
- [How the Diagnosed Flaw Is Resolved]
- [Remaining Trade-Offs & Rollout Boundary]
```
