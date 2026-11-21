<div align="center">

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/960px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg" height="230" alt="Mona Lisa — Leonardo da Vinci's Sfumato" />
  &nbsp;&nbsp;
  <img src="https://upload.wikimedia.org/wikipedia/commons/c/c5/Leonardo_Design_for_a_Flying_Machine%2C_c._1488.jpg" height="230" alt="Design for a Flying Machine, c. 1488" />
  &nbsp;&nbsp;
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Da_Vinci_Vitruve_Luc_Viatour.jpg/960px-Da_Vinci_Vitruve_Luc_Viatour.jpg" height="230" alt="Vitruvian Man — Cross-Domain Proportion" />
</p>

# 🎨 Sfumato

### *Dissolve domain boundaries. Break the Artificial Hivemind. Unlock Test-Time Scaling for Creativity.*

<p>
  <a href="./README.md"><strong>English</strong></a> · <a href="./README.ko.md">한국어</a>
</p>

<p>
  <img src="https://img.shields.io/badge/Diversity_Across_9_Runs-9%2F9_Undefeated_(60_vs_34)-B83B2A?style=for-the-badge" alt="9/9 Diversity Undefeated" />
  <img src="https://img.shields.io/badge/K=12_Scaling-3.0%C3%97_(18_vs_6)-8E2F21?style=for-the-badge" alt="3.0x Scaling" />
  <img src="https://img.shields.io/badge/Claude_Opus_5.5-0_Refusals_(safe--profile)-2F5D62?style=for-the-badge" alt="Claude 0 Refusals" />
  <img src="https://img.shields.io/badge/Dependencies-Zero_(Pure_Stdlib)-5C4E3F?style=for-the-badge" alt="Zero Dependencies" />
</p>

> *"Sfumato" (Italian: evaporated like smoke) is Leonardo da Vinci's painting technique of dissolving harsh outlines so entirely new forms emerge. Leonardo didn't stay inside one discipline — he ported anatomy, fluid dynamics, fortification, and optics into each other.*
>
> **Sfumato** is an ultra-lightweight agent skill (`/sfumato`, `/sfm`) that does the same for frontier LLMs — **with zero external RAG, zero fine-tuning, and zero dependencies.**

</div>

---

## 🔥 The Problem: Standard LLMs Hit an *Artificial Hivemind* Wall

For coding and reasoning, **clean, strictly relevant context** is king. Irrelevant context distracts attention and kills accuracy.

**For brainstorming, the exact opposite happens.**

When you ask an LLM to brainstorm a hard open-ended problem — even across 12 completely isolated sessions — it collapses into the same 3–6 safe textbook clichés (*Artificial Hivemind*, NeurIPS). Raising `temperature` breaks coherence before it creates real conceptual leaps. Multi-agent debate makes it *worse* (*Diversity Collapse*).

> **🧪 Real Smoking Gun from Our Pilot (`OSS-PR`):**
> Across isolated runs solving *"how to stop AI-generated slop PRs in open-source repos"*, **three completely separate sessions** (`Direct Baseline 1`, `Direct Baseline 2`, and even an `Explicit Thermodynamics` session) **independently invented the exact same example package string: `pkg@pr-4821` / `pkg@patch-4821`.**
>
> **Zero** sessions in Sfumato's **Blind Isomorphic Masking** track touched `4821` — or any Baseline cliché.

---

## 📈 Test-Time Scaling for Creativity (Real Measured Data, `K = 1..12`)

We ran **12 completely isolated sessions (24 ideas each)** on a classic hard product problem — *stopping buyer-seller disintermediation (off-platform cash deals) in two-sided marketplaces without chat surveillance, fines, or deficit subsidies* — using strict deduplication of underlying causal mechanisms:

<p align="center">
  <img src="./assets/scaling_curve.svg" alt="Test-Time Scaling for Creativity: Sfumato vs. Direct Best-of-N" width="100%" />
</p>

| Metric (`K = 12` isolated runs, 24 ideas each) | Direct Best-of-N | **Sfumato Dual-Track** | Delta |
|---|---:|---:|---:|
| **Unique Structural Mechanisms Discovered** | `6 / 24` (`25.0%`) | **`18 / 24` (`75.0%`)** | **3.0×** |
| **New Mechanisms in Runs 9–12 (last 8 ideas)** | `0` *(hard plateau)* | **`+5` *(still climbing)* ** | **∞** |
| **Track B (Blind) Uniqueness / Baseline Overlap** | — | **`83.3%` / `0` overlaps** | Zero cliché gravity |
| **Order-Swapped Blind A/B Judge (`AB` & `BA`)** | `0–2` *(21:24, 20:23)* | **`2–0` Win *(24:21, 23:20)*** | Position-debiased |

> **Key Takeaway:** Swinging harder with **Direct Best-of-N** doesn't work — it flatlines at `6` mechanisms (75% repetition). **Sfumato unlocks Test-Time Scaling for Creativity:** every additional swing explores a genuinely orthogonal mechanism cluster, pushing the **maximum creativity ceiling (Top-1)** higher.

---

## 🌍 Multi-Problem & Cross-Model Benchmark (`9 / 9` Undefeated on Diversity)

Does this hold outside marketplace game theory — including **emotional UX design**, **open-web anti-scraping**, **software architecture**, and **other frontier models** like **Claude Opus 5.5**?

We ran **strict Iso-Compute benchmarks** (`4 isolated runs × 2 ideas = 8 ideas/method`, order-swapped `AB`/`BA` Blind Judges) across **7 public hard problems** on Gemini 4 Neon plus **2 cross-model replications** on **Claude Opus 5.5** using `--safe-profile claude` (which filters out 8 bio/CBRN/cyber/espionage domains so Claude hits **0 safety refusals across 24 isolated calls**):

<p align="center">
  <img src="./assets/multi_problem_benchmark.svg" alt="Multi-Problem and Cross-Model Benchmark: 9/9 Undefeated on Diversity" width="100%" />
</p>

| Public Hard Problem | Model | Direct Unique/8 | Sfumato Unique/8 | Gain | Blind `AB · BA` (30pt) | Verdict |
|---|---|---:|---:|---:|---|---|
| **`MKT-DIS`** *(Marketplace Disintermediation)* | Gemini 4 Neon | 3 / 8 | **7 / 8** | **2.33×** | **24:21 · 23:20** | **Sfumato 2–0 Win** |
| **`UX-ONBOARD`** *(Blank-Canvas Fear · Emotion/UX, v2.0)* | Gemini 4 Neon | 4 / 8 | **7 / 8** | **1.75×** | **25:20 · 24:21** | **Sfumato 2–0 Win** |
| **`WEB-SCRAPE`** *(Open Web vs. Mass AI Scrapers)* | Gemini 4 Neon | 6 / 8 | **7 / 8** | **1.17×** | **22:18 · 20:18** | **Sfumato 2–0 Win** |
| **`OSS-PR`** *(Open-Source AI-Slop PR Flood)* | Gemini 4 Neon | 2 / 8 | **5 / 8** | **2.50×** | **21:17 · 18:21** | **Split 1–1** *(Agg +1)* |
| **`AI-ARCH`** *(AI Agent Architectural Erosion)* | Gemini 4 Neon | 4 / 8 | **7 / 8** | **1.75×** | **23:22.5 · 22.5:24** | **Split 1–1** |
| **`DOC-ROT`** *(Self-Healing Org Doc Rot, v2.0)* | Gemini 4 Neon | 2 / 8 | **6 / 8** | **3.00×** | **23:22 · 23:26** | **Split 1–1** *(+3pt vs v1.2)* |
| **`GAME-SNOWBALL`** *(Snowball vs. Rubber-Banding)* | Gemini 4 Neon | 5 / 8 | **7 / 8** | **1.40×** | 22:23 · 21:23 | Direct 2–0 *(honest miss)* |
| **`MKT-DIS`** *(Cross-Model · `--safe-profile claude`)* | **Claude Opus 5.5** | 4 / 8 | **7 / 8** | **1.75×** | 18:19 · **20:17** | **Split 1–1** *(Agg +2 · 0 refusals)* |
| **`DOC-ROT`** *(Cross-Model · `--safe-profile claude`)* | **Claude Opus 5.5** | 4 / 8 | **7 / 8** | **1.75×** | 20:22 · 20:22 | Direct 2–0 *(no Anchor · 0 refusals)* |

- **Grand Total (9 runs, 72 ideas/method):** **9 / 9 undefeated on diversity** — `60 / 72 (83.3%)` unique mechanisms vs. Direct `34 / 72 (47.2%)` (**1.76×**).
- **7-Problem v2.0 Blind Judge Record:** **9 Sfumato vs. 5 Direct (`64.3%`)** — **3 Wins, 3 Splits, 1 Loss** (and **0 losses** on all 6 problems where a cross-domain mechanism survived to Top-1).
- **Reproducible Raw Logs:** Every raw JSON transcript and judge rubric is published in [`benchmarks/v2/`](./benchmarks/v2/) — verify locally with `python tools/summarize_benchmarks.py benchmarks/v2`.

> **⚖️ Where Sfumato Shines — and Where It Doesn't:**
> - **Shines brightest** on open-ended strategy, incentive/mechanism design, non-obvious UX & behavioral design (`UX-ONBOARD` 2–0), and breaking entrenched industry clichés.
> - **Honest limitation (`GAME-SNOWBALL`):** On tightly coupled real-time physics/balance loops with small sample budgets (`K=3`), unlucky institutional draws can lose to a strong Direct Baseline — and our v2.0 ablation proved **forced cross-domain grafting makes it worse (`43 → 39`)**. Use `deep` mode (`Direct Anchor + K=6`) for tight engineering/systems loops so the anchor locks your floor (`≥ Direct`).

---

## 🏛️ How Sfumato v2.0 Works: The *Domain-Masking Trade-Off*

Most cross-domain prompting papers use **Explicit Analogy** (*"apply biology to solve marketplace churn"*). Because the original problem's words stay in the prompt, the LLM still suffers **partial homogenization** back toward industry clichés.

Conversely, **pure Blind Reframing** (hiding the original problem completely) breaks cliché gravity 100%, but has a lower hit-rate because some abstract solutions don't translate cleanly back.

**Sfumato v2.0 pairs both tracks in parallel — then runs a Clean-Context Red-Team Triage + Optional Hardening pass:**

<p align="center">
  <img src="./assets/architecture_codex.svg" alt="Sfumato Architecture Diagram" width="100%" />
</p>

1. **Cluster-Stratified Code RNG + Safety Profiles (`sample_domains.py`):** Never ask an LLM to "pick random domains" (it repeats *ants, jazz, and chess*). Sfumato samples from **40 mechanism-rich domains across 8 disjoint macro-clusters** using pure Python `random`. Pass `--safe-profile claude` to exclude 8 sensitive bio/cyber/espionage domains (leaving 32 domains across all 8 clusters with **0 safety refusals on Claude Opus 5.5**).
2. **Track A — Explicit Analogy *(High Hit-Rate)*:** Original brief + assigned remote domain → surgical hits against domain-specific attack surfaces.
3. **Track B — Blind Isomorphic Masking *(Max Ceiling · v2.0 3-Line Structural Skeleton)*:**
   - First distill the problem into a **3-line domain-neutral Structural Skeleton** (*State Variables · Incentive Polarity · Irreducible Trade-Off*), then rewrite it into the target field with a **0-leak vocabulary check**.
   - A fresh, isolated subagent solves the masked twin purely inside the remote field — **physically incapable of emitting original-domain clichés.**
   - Back-translate only the causal mechanism & trade-off (ruthlessly discard strained translations).
4. **Direct Anchor *(`deep` mode · Floor Guarantee)*:** Includes 1 isolated Direct Baseline solver in the unlabeled pool so `max(Direct, Explicit, Blind) ≥ Direct` — never worse than standard prompting on engineering-native problems.
5. **Stage 2a/2b — Clean-Context Red-Team Triage & Selective Hardening *(v2.0)*:**
   - **Stage 2a:** A fresh, uncontaminated evaluator cuts surface jargon cosplay, screens every candidate for **Adverse Selection**, **Sybil/Wash-Trading exploits**, and **feasibility**, and tags fixable gems as `HARDEN` instead of binary-killing them.
   - **Stage 2b:** Hardens *only* the Top-1 winner's single biggest operational weakness (without forcing cross-domain grafts when the `Direct Anchor` legitimately wins). This turned `DOC-ROT` from `0–2` to `1–1` (+3pt) and drove `UX-ONBOARD` to a `2–0` sweep.

---

## ⚡ Before / After Showcase: Marketplace Disintermediation (`MKT-DIS`)

> **Problem:** Freelancers, tutors, cleaners, and contractors meet buyers on a platform, then move to WhatsApp/cash for repeat jobs to dodge the 10–20% fee. *Banned clichés: chat filtering, fines, simple escrow/insurance, cashbacks, or 0% fees.*

| Method | What It Produced | Why It Differs |
|---|---|---|
| **Direct Best-of-N**<br>*(12 runs, 24 ideas)* | Repeated the same 3 core ideas 18 times: *T+0 Reverse Escrow*, *Transferable Client-Book*, *Idle-Slot Backfill*. | High practical quality, but stuck inside the exact same fintech/ops playbook. |
| **Sfumato · Winner**<br>*(Parasitology · Two-Fold Cost of Sex)* | **🏆 Chimeric Task Recombination** *(Blind Judge 2–0 Winner)* — Redirect 5–7% of the repeat fee into an independent **3rd-party cross-verification slot every N sessions** (blind mock-exam for tutoring, thermal/level cross-inspection for renovations, senior async review for code). | Direct 1:1 cash deals *physically cannot* replicate independent 3rd-party checks, collapsing the collusion price zone — and **proposing cash off-platform becomes a "Lemon Signal" of dodging quality audit.** |
| **Sfumato · Track B Blind**<br>*(Ombudsman & Cryptographic Whistleblowing)* | **Zero-Knowledge Safe-Harbor Attestation** — Seal pricing/deliverable commits + retaliation-proof whistleblower absence proof so corporate/HOA/team buyers get **audit-proof anti-kickback immunity**. | Reframed disintermediation from "saving 15%" into "eliminating embezzlement/kickback liability for institutional buyers." |
| **Sfumato · Track B Blind**<br>*(Anthropology · Kula Ring)* | **Kula Pedigree Provenance Chain** — On-platform jobs stamp verifiable craftsman lineage onto outputs (boosting home resale value, VC/M&A IP due diligence, or credential portability). | Off-platform work becomes an "unpedigreed nameless artifact" that loses downstream third-party resale value. |
| **Sfumato · Red-Team Catch**<br>*(Fluid Dynamics · Venturi Ejector)* | **Venturi Negative-Fee Capacity Suction** — Charge *-3%* (buyer pays 90, supplier gets 93) funded by ±24–48h shift call-options exercised during urgent B2B spikes (160). | Brilliant physics transfer — **and Sfumato's v1.2 Red-Team Gate instantly caught its wash-trading arbitrage exploit (90→93)** before it could steal Top-1! |

<details>
<summary><strong>📊 Inspect All 18 Unique Sfumato Mechanisms vs. 6 Direct Mechanisms (Full K = 1..12 Log)</strong></summary>

<br/>

#### Direct Best-of-N (`K = 1..12`, 24 ideas → **6 unique**, flatlined at K=8)
1. **Transferable Client-Book & Succession Royalty** *(appeared 6× across 12 runs)*
2. **T+0 Reverse-Escrow / Maturity Transformation** *(appeared 6×)*
3. **Idle-Slot Backfill & Context-Synced Hot-Swap** *(appeared 6×)*
4. **Anchor-Client Patronage Revenue-Share Equity** *(appeared 4×)*
5. **Perishable-Capacity In-Kind Barter Fee** *(1×)*
6. **B2B Wholesale Input & Tax-Arbitrage Rail** *(3×)*

#### Sfumato Dual-Track (`K = 1..12`, 24 ideas → **18 unique**, still climbing at K=12)
| Run | Track · Remote Domain | New Unique Mechanisms Discovered | Cum. |
|---:|---|---|---:|
| 1 | Explicit · `fluid_microfluidics` | ① Venturi Negative-Fee Shift-Option Suction · ② Laminar Co-Flow Unbundling | 2 |
| 2 | Blind · `maritime_trade_guilds` | ③ Multilateral Giro Netting Ledger · ④ Manifest Co-Loading & Third-Party Lien Shield | 4 |
| 3 | Explicit · `parasitology_coevolution` | ⑤ **Chimeric Cross-Recombination (🏆 2–0 Winner)** · ⑥ Reverse-Escrow Metabolic Decoupling | 6 |
| 4 | Blind · `horology_escapement` | ⑦ Differential Remontoir Income/Capacity Smoothing *(1 discarded: translation loss)* | 7 |
| 5 | Explicit · `disaster_triage` | ⑧ Dynamic Retriage Scope-Creep Shield *(1 overlapped Co-Flow)* | 8 |
| 6 | Blind · `container_port_logistics` | ⑨ Dual-Cycling Return-Leg Backhaul Chaining · ⑩ Buffer-Yard Drop-and-Hook Async Decoupling | 10 |
| 7 | Explicit · `siege_fortification` | ⑪ Metered Tool-License & Unused-Material Return Magazine *(1 overlapped Backup)* | 11 |
| 8 | Blind · `ombudsman_whistleblower` | ⑫ Zero-Knowledge Anti-Kickback Safe-Harbor · ⑬ Threshold Anonymous Subcontractor Early-Warning | 13 |
| 9 | Explicit · `architectural_wayfinding` | ⑭ Open-Atrium Live Work-Log Showroom (CPTED Natural Surveillance) *(1 overlapped Backhaul)* | 14 |
| 10 | Blind · `electronic_warfare_pls` | ⑮ Global Conflict-Aligned Multi-Party Schedule Multiplexing *(1 discarded: translation loss)* | 15 |
| 11 | Explicit · `mycorrhizal_plant_defense` | ⑯ Tri-Trophic External Insurer/Lender Priming Signal *(1 overlapped Clearing)* | 16 |
| 12 | Blind · `gift_economy_reciprocity` | ⑰ Kula Pedigree Resale-Value Provenance · ⑱ Potlatch/Hau Generalized Triadic Time-Bank Ring | **18** |

</details>

---

## 🚀 Quick Start (Zero Dependencies)

Sfumato is just **4 lightweight files** (`SKILL.md`, `domain_pool.json`, `sample_domains.py`, `prompt_templates.md`). Install in one command for **Claude Code** (including `/sfm` shortcut with `--safe-profile claude`), **Antigravity (`agy`)**, or **Codex CLI**:

```bash
# macOS / Linux — one-line install (auto-detects installed agents, or pass --target claude|agy|codex|all)
curl -fsSL https://raw.githubusercontent.com/Excelsus4/sfumato/main/tools/install.sh | bash
```

```powershell
# Windows PowerShell — one-line install
irm https://raw.githubusercontent.com/Excelsus4/sfumato/main/tools/install.ps1 | iex
```

<details>
<summary>Local checkout with <code>--dry-run</code> preview or manual copy</summary>

```bash
# Preview before installing (macOS / Linux)
git clone https://github.com/Excelsus4/sfumato.git && cd sfumato
bash tools/install.sh --dry-run
bash tools/install.sh --target all
```

```powershell
# Preview before installing (Windows PowerShell)
git clone https://github.com/Excelsus4/sfumato.git; Set-Location sfumato
.\tools\install.ps1 -DryRun
.\tools\install.ps1 -Target all
```

```bash
# Manual copy (zero scripts)
cp -r skill/sfumato ~/.claude/skills/sfumato && cp commands/sfm.md ~/.claude/commands/sfm.md
cp -r skill/sfumato ~/.gemini/config/skills/sfumato
cp -r skill/sfumato ~/.codex/skills/sfumato
```

</details>

### Usage

```text
/sfm Design a non-obvious mechanic to prevent snowballing in a 3-faction asymmetric RTS
/sfumato deep mode: How do we defend open-source repos from AI-slop PR floods without paywalls?
```

| Mode | Pipeline | Best For |
|---|---|---|
| `dual-track` *(default)* | `2 Explicit + 2 Blind` → Red-Team Selector | Everyday high-ceiling brainstorming |
| `deep` | `1 Direct Anchor + 3 Explicit + 3 Blind` → Red-Team Selector | Stuck strategic problems (guarantees `≥ Direct` floor) |
| `fast` | `3 Explicit` → Red-Team Selector | Quick practical hits under tight token budgets |

---

## 📚 Research Foundations

Sfumato builds directly on four converging lines of 2024–2026 LLM creativity research:
- **Artificial Hivemind** — Jiang et al. (*NeurIPS Best Paper*): documents intra- and inter-model homogenization on open-ended ideation.
- **Diversity Collapse in Multi-Agent LLM Systems** — shows dense debate/consensus topologies crush semantic diversity; motivates Sfumato's strict **zero-crosstalk** parallel Stage 1.
- **Unlocking LLM Creativity in Science through Analogical Reasoning** (Shen et al., 2026) & **Assessing Cross-Domain Mapping in Humans and LLMs** (Liu et al., 2026) — validates structural relational transfer over surface metaphors.
- **Sfumato's Distinct Contribution:** Formalizes the **Domain-Masking Trade-Off** between *Explicit Analogy* (high hit-rate, partial homogenization) and *Blind Isomorphic Masking* (lower hit-rate, zero cliché gravity, heavy-tail mutations), unified with a **Direct Anchor** and **Clean-Context Red-Team Gate**.

---

<div align="center">

<img src="https://upload.wikimedia.org/wikipedia/commons/5/5f/Codex_Atlanticus.jpg" width="460" alt="Leonardo da Vinci — Codex Atlanticus" />

*“Where the spirit does not work with the hand, there is no art.” — Leonardo da Vinci*

<sub>All Leonardo da Vinci artworks are Public Domain via Wikimedia Commons.</sub>

</div>
