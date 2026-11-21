# Sfumato v2.1 End-to-End Execution Trace (`ALERT-FATIGUE`)

This document publishes a complete end-to-end execution trace of **Sfumato v2.1** (`dual-track` default mode: `1 Direct Anchor + 2 Explicit + 1 Blind` → Clean-Context Stage 2a Red-Team Triage → Clean-Context Stage 2b Selective Hardening), including the recorded `sample_domains.py` draw, reproducible `check_leak.py` output, condensed summaries of all 4 isolated Stage 1 solver outputs, Track B back-translation, full Stage 2a anonymization & triage, and Stage 2b hardening.

- **Date:** 2026-11-22
- **Model:** Gemini 4 Neon (`inherit`, isolated fresh subagents per solver/evaluator, zero tool calls inside subagents)
- **Mode:** `dual-track` (`1 Direct Anchor + 2 Explicit + 1 Blind`)
- **Language:** English (`{USER_LANGUAGE} = English`)
- **Sampling Provenance Note:** Step 2 ran against an uncommitted intermediate working-tree snapshot (40 domains / 8 clusters with `affinities` tags) before the 74-domain / 11-cluster pool was merged into `domain_pool.json`. All 3 sampled domain IDs remain valid in HEAD, but this specific draw cannot be reproduced from any committed revision; `--seed 2026` below is recorded for provenance only.

---

## Step 1. Problem Framing

- **Core Goal:** Reduce noisy, low-actionability on-call pages in high-throughput microservices by >80% so engineers wake up only for true customer-impacting failures, without silently dropping novel, cascading, or slow-burn incidents.
- **Structural Constraints & Incentive Polarity:** Cooperative engineering organization (`systems_ops`) suffering from asymmetric blame — missing 1 real outage carries severe visible blame, while adding 10 hypersensitive alert rules carries zero immediate penalty for the rule author, creating a tragedy of the commons in shared on-call fatigue.
- **Banned Clichés:** Static threshold tuning, ML/LLM anomaly detection or AI alert deduplication, simple snooze/mute buttons, PagerDuty rotation expansion, or adding a dedicated L1 NOC tier.

---

## Step 2. Stratified Polarity-Aware Sampling (`sample_domains.py`)

Command invoked during the run (ran on an uncommitted intermediate 40-domain polarity-tagged working-tree pool; not reproducible from committed revisions — `--seed 2026` is listed for provenance only):
```bash
python skill/sfumato/scripts/sample_domains.py --k 3 --mode dual-track --polarity systems_ops --exclude-clusters craft_operations --seed 2026
```

Recorded Draw (note: `mechanisms` hints omitted by default to prevent hint priming):
```json
[
  {
    "track": "explicit",
    "cluster": "art_performance",
    "id": "architectural_wayfinding",
    "name": "Architectural Wayfinding & Behavioral Affordances",
    "affinities": [
      "human_ux",
      "cooperative",
      "systems_ops"
    ]
  },
  {
    "track": "blind",
    "cluster": "physics_engineering",
    "id": "thermodynamics_cryogenics",
    "name": "Thermodynamics & Cryogenic Thermal Management",
    "affinities": [
      "physical_loop",
      "systems_ops",
      "human_ux"
    ]
  },
  {
    "track": "explicit",
    "cluster": "intelligence_conflict",
    "id": "submarine_acoustics",
    "name": "Submarine Stealth & Acoustic Deception",
    "affinities": [
      "adversarial",
      "physical_loop"
    ]
  }
]
```

---

## Step 3. Track B 3-Line Structural Skeleton + Code-Verified Zero-Leak Masking

### 3-Line Domain-Neutral Structural Skeleton
- **Actors & Incentive Polarity:** Cooperative operators protecting a complex interconnected system under asymmetric blame — over-triggering protective alarms carries zero personal penalty, while missing one catastrophic failure carries severe blame, flooding the shared response channel.
- **Core Asymmetry / Bottleneck:** Hundreds of local components emit cheap transient spikes and coupled secondary ripples faster than a scarce human response crew can inspect, causing real early-stage structural failures to drown inside routine noise.
- **Why Static Controls Fail:** Fixed thresholds either blind the system to slow-burn compound failures or drown operators in false alarms; opaque automated filters cannot be trusted with novel failure modes; manual suppression simply shifts the failure into silent blindness.

### Track B Masked Scenario (`Thermodynamics & Cryogenic Thermal Management`)
> You are designing the thermal protection and quench-detection architecture for a large multi-stage superconducting cryostat (a segmented magnet ring with dozens of interconnected cold-mass modules sharing helium cooling loops).
>
> **Core Problem:** Every subsystem designer adds hypersensitive local temperature and pressure relief triggers to avoid personal blame for a catastrophic magnet quench. Because routine transient heat loads (eddy currents, valve cycling, ambient vibration) constantly ripple across coupled helium lines, the central cryo-control room is flooded with hundreds of non-critical thermal warnings per shift. Human cryo-operators suffer severe desensitization and miss genuine slow-burn thermal runaway or novel cascading leaks before irreversible coil damage occurs.
>
> **Hard Constraints:**
> 1. You cannot simply raise fixed Kelvin cutoffs (that misses slow-burn insulation degradation until too late).
> 2. You cannot install a black-box predictive controller to automatically ignore or silence sensors (untrusted for novel failure modes).
> 3. You cannot add manual silence switches or hire a larger watch crew.
> 4. Real runaway events that threaten the cold mass must always break through immediately, while routine coupled transient ripples must stop reaching the watch crew.

### Code-Verified Zero-Leak Check (`check_leak.py`)
Command:
```bash
python skill/sfumato/scripts/check_leak.py \
  --terms "alert,on-call,pager,microservice,incident,outage,server,service,deploy,monitoring,engineer,software,cloud,log,metric,latency,dashboard,snooze,mute,ML,LLM,AI" \
  --file track_b_mask.txt --json
```

Exact Output (exit code `0`):
```json
{
  "status": "PASS",
  "leaked_count": 0,
  "terms_checked": 22,
  "leaks": []
}
```

---

## Step 4. Stage 1 — Condensed Outputs from 4 Isolated Parallel Subagents (Zero Cross-Talk)

### 4.1 Direct Anchor Solver (`subagent: 625879bd`)

#### Proposal 1: Boundary-Only Dual-Signal Paging with Live Trace-Graph Causal Collapse
- **Core Structural Principle:** Decouple *waking a human* (strictly restricted to deterministic customer-impact signals) from *root-cause diagnosis* (internal resource/component metrics demoted to non-paging context), and route all pages through a live distributed-trace dependency DAG so cascading failures deterministically collapse onto the causal frontier rather than fanning out across upstream callers.
- **Concrete Operating Steps:**
  1. **Enforce a Router-Level Two-Class Paging Gate (Schema-Enforced, Not Policy):** Direct paging privileges are granted exclusively to (Class A) Multi-Window Error-Budget Burn (fast burn paired short+long windows; slow burn daytime-routed unless budget drops below floor) and (Class B) End-to-End Conservation & Invariant Tripwires (`orders_accepted == settled + explicitly_rejected + in_flight_within_SLA`, monotonic watermark progress, canary payload integrity) catching novel HTTP-200 failures. All internal cause alerts (CPU, GC, pod restarts, queue depth) are restricted to diagnostic annotations.
  2. **Auto-Derived Live Service DAG:** Continuously build the service dependency graph from live distributed tracing / service-mesh parent-child span edges (rolling 15-minute window).
  3. **Causal-Frontier Collapse with Bounded Failsafe Hold:** When multiple services breach simultaneously, page only the deepest breaching downstream node(s) (the causal frontier); hold upstream breaching services for 3–5 minutes and attach them as blast-radius metadata.
  4. **Deterministic Failsafe & Divergence Release:** Break the hold automatically if (a) downstream is unacked past SLA, (b) upstream errors carry trace-propagated attribution not originating from the held downstream node, or (c) upstream burn persists after downstream recovery.
- **Key Trade-Offs & Mitigations:** Aggressive trace sampling can hide causal edges (mitigate with 100% tail-based error capture and fail-open on unknown topology); upfront invariant modeling cost (prioritize edge gateways and async ledger boundaries first).

#### Proposal 2: Author-Bound Alert Probation, Victim-Audited Noise Budgets, and Sunset-by-Default Governance
- **Core Structural Principle:** Invert the asymmetric-blame tragedy of the commons by internalizing false-positive costs directly onto the rule author and owning service, separating noise adjudication from rule authorship, and converting rule persistence into an expiring privilege backed by deployment-gating accountability.
- **Concrete Operating Steps:**
  1. **Mandatory Author-Bound Probation:** Alert-as-code CI forces new/tightened custom paging rules into a 14–30 day author-only daytime probation tier; graduation requires >=80% verified actionable rate plus a linked diagnostic query/runbook.
  2. **Victim-Adjudicated Binary Disposition:** Closing any out-of-hours page requires a 1-click disposition by the paged responder (never the author): `Customer-Impacting / Actionable` (creates a customer-SLA incident record) vs. `Noise` (debits the owning service's monthly Page-Noise Budget).
  3. **Ownership Bounce + Deploy-Freeze Clock:** Exceeding noise budgets (e.g., >2 noisy pages/rule/14d or >4/service/month) bounces the rule off the shared pager onto the owning team's interrupt queue (never muted) and starts a 72-hour clock before CI freezes non-emergency feature deploys for that service.
  4. **CI-Enforced Rule TTLs (Sunset-by-Default):** Custom rules carry 60–90 day hard TTLs in code (auto-removal PR unless backed by quantitative true-positive proof), while standardized boundary SLOs bypass probation.
- **Key Trade-Offs & Mitigations:** Probation lag for newly discovered urgent failure modes (mitigate via standardized boundary templates bypassing probation + 14-day expiring director-signed emergency override).

---

### 4.2 Track A Explicit Solver #1 — `Architectural Wayfinding & Behavioral Affordances` (`subagent: 511ddacc`)

#### Proposal 1: Defensible-Space Alert Zoning & Co-Page Stoop Tether
- **Borrowed Principle:** Oscar Newman's *Defensible Space* territorial hierarchy (Public Corridor vs. Semi-Private Stoop), hospital/airport sight-triangle sign ordinances, and building egress code's "Crash-Bar Interlock" (forbidding lit `EXIT` signs over locked closets without a one-motion mitigation affordance).
- **Concrete Operating Steps:**
  1. **CI-Enforced Spatial Zoning:** Alert-as-code CI/OPA enforces two zones: **Public Egress Corridor** (strictly edge/customer-journey SLIs + flow-conservation invariants) and **Semi-Private Stoop** (every new/edited internal symptom rule deploys only to the author's daytime/local queue).
  2. **Crash-Bar Affordance Gate & Stoop Probation:** Internal rules graduate only after binding an executable remediation affordance (rollback, failover, load-shedding lever — no vague "investigate dashboard") and achieving >=75% verified mitigation-artifact yield across 14 days (or passing a synthetic fire-drill for rare catastrophic failures).
  3. **Co-Page Liability Tether & Auto-Demotion:** Non-actionable wake-ups accrue Stoop Debt: at Debt = 2 (in 30 days), a **Co-Page Tether** simultaneously wakes both the on-call engineer and the rule author (or `CODEOWNERS` lead); at Debt = 3, the rule automatically demotes back to the Author Stoop.
- **Key Trade-Offs & Mitigations:** Rare catastrophe alerts never fire 3 times in 14 days (mitigate via deterministic synthetic fire-drill verification); edge landmarks lag deep backend faults slightly (mitigate by pairing with runtime cascade/corridor handling).

#### Proposal 2: Telemetry Chicanes & Corridor-Backpressure Affordances
- **Borrowed Principle:** European bridge-pier flood waterlines (*Hochwassermarken*), Dutch *Woonerf* lane-narrowing traffic chicanes with keyed emergency fire-lanes, and transit-hub concourse backpressure sensing.
- **Concrete Operating Steps:**
  1. Compute two deterministic spatial signals: **Time-to-Wall (TTW)** (seasonally matched monotonic headroom slope) and **Corridor Backpressure** (backward-propagating retry/dwell slope across >=2 upstream caller hops).
  2. Embed progressive daytime friction inside CI/PR/deploy paths: Tier 1 (TTW 24–72h) renders inline Waterline strips in PRs/CLIs; Tier 2 (TTW 8–24h) requires explicit merge acknowledgment; Tier 3 (TTW <8h or >=2-hop backpressure) narrows feature deploys while unlocking a zero-wait **Emergency Fire Lane** strictly scoped by CI to reductive diffs (`git revert`, flag kills, scale-ups).
  3. Wake 24/7 on-call only at acute cliff (<2h TTW) or when backpressure reaches the Customer-Boundary Landmark; propagate Tier 2/3 friction one hop upstream onto active callers for dormant legacy services.

---

### 4.3 Track B Blind Solver #1 — `Thermodynamics & Cryogenic Thermal Management` (`subagent: c93da528`, ZERO software/alert vocabulary)

#### Blind Design 1: Sacrificial Phase-Change Latent-Heat Gate with Boiling-Crisis (CHF) Fast-Path
- **Core Principle:** Replace temperature-triggered alarms with a physical analog enthalpy integrator (a local two-phase saturated LHe buffer cooled by a rate-limited overhead condenser). Exploits isothermal latent-heat absorption ($Q = m h_{fg}$) and the discontinuous nucleate-to-film boiling crisis (Critical Heat Flux, CHF) to separate routine transients from slow-burn leaks and acute quenches.
- **Operating Steps:** Routine transient heat loads vaporize liquid isothermally at $T_{\text{sat}}$ and re-condense without tripping alarms. Persistent slow-burn leaks exceeding condenser capacity drain liquid inventory monotonically, tripping a hard physical liquid-level threshold (65% fill) even while $\Delta T \approx 0\text{ K}$. Acute quenches exceeding CHF trigger an instantaneous film-boiling pressure/superheat jump bypassing the slow integrator in milliseconds.

#### Blind Design 2: Control-Volume Entropy-Generation ($\dot{S}_{\text{gen}}$) & Isentropic-Advective Residual Architecture
- **Core Principle:** Replace local intensive-state alarms ($T, P$) with First- and Second-Law open-system conservation accounting across each module's inlet and outlet boundaries: $\dot{S}_{\text{gen},i} = \frac{dS_{\text{cv},i}}{dt} + \dot{m}_{\text{out}} s_{\text{out}} - \dot{m}_{\text{in}} s_{\text{in}} - \frac{\dot{Q}_{\text{ramp},i}}{T_i}$. Routine acoustic/pressure ripples are isentropic ($ds \approx 0$) and upstream warm slugs advect cleanly through healthy downstream modules ($\dot{S}_{\text{gen}} \approx 0$); only the faulted module where irreversible heat enters generates strictly positive net entropy ($\dot{S}_{\text{gen},i} > 0$).
- **Operating Steps:** Instrument inlet/outlet boundaries with deterministic equation-of-state tables. Escalate via two channels: (1) Cumulative Irreversibility Integral $\Sigma_i = \int \dot{S}_{\text{gen},i}\,dt$ catching tiny slow-burn insulation leaks before bulk $T$ rises, and (2) Instantaneous Irreversibility Rate $\dot{S}_{\text{gen},i} > \dot{S}_{\text{crit}}$ for sudden local quenches. Add a **Global Ring Closure Audit** ($\sum_i \dot{H}_{\text{net},i} + \dot{H}_{\text{headers}} = \dot{Q}_{\text{cryoplant}}$) so any sensor drift, telemetry drop, or masked module raises a deterministic **Metrology Closure Fault**.

---

### 4.4 Track A Explicit Solver #2 — `Submarine Stealth & Acoustic Deception` (`subagent: 420ae4ab`)

#### Mechanism 1: Self-Noise Floor Escrow & Blinding Co-Liability
- **Borrowed Principle:** Own-ship radiated noise budgeting ($NL_{\text{self}}$ mathematically blinds own passive sonar), mandatory pre-patrol Sound Range Trials (AUTEC), and continuous Noise & Vibration Monitoring (NVM) attributing acoustic indiscretions back to offending subsystems.
- **Concrete Operating Steps:**
  1. Cap the shared rotation with a fixed weekly non-actionable interruption ceiling (sleep hours weighted 3x) partitioned into quarterly per-team noise credits.
  2. Gate new rules behind 14-day automated Sound Range Trials (live traffic + synthetic fault injections).
  3. Audit every shared wake-up against objective telemetry artifacts (SLI burn, rollback/remediation commit, chaos drill); after 2 acoustic indiscretions in 30 days, auto-detach ("raft isolate") the rule onto the authoring team's local pager (still live, never muted).
  4. **Masking Co-Liability:** Whenever a real customer outage suffers delayed detection/response, postmortems pull the prior 6-hour Self-Noise Ledger and assign formal team reliability-budget co-liability to teams whose noisy rules raised the watch's detection noise floor.

#### Mechanism 2: Anti-Decoy Multi-Highlight Verification & Active Micro-Interrogation
- **Borrowed Principle:** Anti-decoy multi-highlight spatial extent (point-source decoys vs. spatially separated array highlights), LOFAR coherent time-integration of negative-SNR signals, and TMA leg / LPI active micro-interrogation ("clearing the baffles").
- **Concrete Operating Steps:**
  1. Strip individual rules of direct paging; treat them as unverified contacts.
  2. **Passive Gate A (Multi-Highlight Extent):** Escalate immediately only if correlated perturbations span >=2 independent topological failure boundaries on a live eBPF/mesh DAG.
  3. **Passive Gate B (Conservation-Law Coherent Integration):** Run signed-drift integrators $\int (R_{\text{in}} - R_{\text{out}})\,dt$ across multi-scale windows (15m/2h/12h) for alloc-reclaim, enqueue-dequeue, and lease-return to catch sub-noise slow burns.
  4. **Active Stage (Micro-Interrogation / Baffles-Clearing Sweep):** When a single-boundary contact persists >90s or a scheduled sweep spots an abrupt zero-error traffic drop, send a bounded (<0.5%) synthetic probe or idempotent shadow replay to both the suspect shard and a clean reference leg (alternate AZ/standby), paging immediately with differential proof if they diverge.

---

## Step 5. Track B Back-Translation (Coordinator)

- **Blind Design 1 → Candidate 5 (`Local Fault-Absorption Buffer Integrator & Discontinuous Flux-Crisis Fast-Path`):** Mapped two-phase latent-heat buffer to a bounded local transient-soak/retry capacity buffer with a steady-state drain ceiling, 65% inventory depletion slow-burn alarm, and discontinuous overload fast-path. *(Submitted to Stage 2a for Red-Team audit.)*
- **Blind Design 2 → Candidate 3 (`Control-Volume Net-Failure-Generation Accounting & Global Closure Audit`):** Mapped inlet/outlet entropy-generation conservation to per-service net locally generated RPC failure flux (`local_backlog_change + outward_failure_flux - inward_dependency_failure_flux - scheduled_work_load`), dual cumulative/instantaneous channels, plus a Global Edge-to-Leaf Closure Audit reconciling attributed failures against edge customer-observed failures. *(Submitted to Stage 2a for Red-Team audit.)*

### Anonymization Key (Hidden from Stage 2a Evaluator)
- `Candidate 1` = Track A Explicit #1 (`architectural_wayfinding` #2)
- `Candidate 2` = Direct Anchor (#2)
- `Candidate 3` = Track B Blind #1 (`thermodynamics_cryogenics` #2, back-translated)
- `Candidate 4` = Track A Explicit #2 (`submarine_acoustics` #1)
- `Candidate 5` = Track B Blind #1 (`thermodynamics_cryogenics` #1, back-translated)
- `Candidate 6` = Direct Anchor (#1)
- `Candidate 7` = Track A Explicit #1 (`architectural_wayfinding` #1)
- `Candidate 8` = Track A Explicit #2 (`submarine_acoustics` #2)

---

## Step 6a. Stage 2a — Clean-Context Red-Team Triage (`subagent: 72c4822b`, Sources Hidden)

### 1. Triage Table

| Candidate | Status | 1-Line Rationale |
|---|---|---|
| **Candidate 1** | `KILL` | Strictly gating night pages on `<2h TTW` or `>=2-hop` retry backpressure silently drops fail-fast outages and silent HTTP-200 corruption, while propagating CI friction upstream punishes innocent callers of legacy services (adverse selection). |
| **Candidate 2** | `KILL` | Probation (`>=80%` actionable in 14–30d) + 60–90d hard TTLs without synthetic proof silently delete rare-catastrophe detectors, and 1-click disposition creates an inverted-friction exploit where sleepy responders click "Noise" to avoid opening SLA incident records. |
| **Candidate 3** | `KILL` | Cross-service linear RPC failure-flux conservation fails physically under fan-out, retries, fallbacks, async queues, and bursty backlogs—producing chronic residuals that turn the Global Closure Audit itself into a noisy false-alarm source—with zero incentive layer. |
| **Candidate 4** | `HARDEN` | Masking Co-Liability brilliantly reverses asymmetric postmortem blame and pairs well with sleep-weighted escrow, synthetic trials, and objective audits, but lacks cascade collapse (all downstream SLI burns pass as valid) and risks adversarial blame politics in a cooperative org if uncalibrated. |
| **Candidate 5** | `KILL` | Cliché cosplay: a local soak buffer with a steady-state drain ceiling, 65% fill alarm, and fast-path spike bypass is leaky-bucket static threshold tuning in hydrology metaphors, leaving cascades, silent corruption, and asymmetric-blame incentives unsolved. |
| **Candidate 6** | `HARDEN` | Pragmatic CI-enforced boundary burn + end-to-end conservation invariants + trace-DAG frontier collapse with deterministic failsafe, but lacks post-deployment noise accountability against faux-SLO/invariant inflation and is vulnerable to trace-sampler dropout during overload storms. |
| **Candidate 7** | `HARDEN` | Strongest full-stack fit: pairs CI/OPA boundary-and-invariant zoning with mandatory executable remediation affordances, synthetic rare-failure drills, and a cooperative skin-in-the-game Co-Page Stoop Tether; needs cascade collapse inside the Shared Corridor and SLI-recovery verification on remediation scripts. |
| **Candidate 8** | `HARDEN` | Highest technical novelty (eBPF `>=2`-boundary extent gating, exact local signed conservation-drift integrators, and Active Differential Micro-Interrogation), but global single-boundary bugs pollute both suspect and reference legs equally (silent drop) and shadow replay risks side effects on mutating write paths. |

### 2. Top-1 (Champion)
- **Champion:** **Candidate 7 — Defensible-Space Alert Zoning & Co-Page Stoop Tether** (`HARDEN`)
  - *[Coordinator post-triage annotation: source = `Track A Explicit · architectural_wayfinding`]*
- **Single Biggest Fixable Flaw (Stage 2b Target):** Shared Egress Corridor cascade amplification (no topological collapse inside Corridor, risking multi-page storms and miscounting cascade victims as author noise strikes) + affordance-yield gaming via trivial no-op/restart levers + inherited legacy `CODEOWNERS` rule ambush.

### 3. Runners-Up & Wildcard
- **Runner-Up #2:** `Candidate 8` — live eBPF/service-mesh multi-boundary extent gating + active differential micro-interrogation *(paired in Stage 2b with Candidate 6's 3–5 min failsafe causal-frontier collapse primitive)*.
  - *[Coordinator post-triage annotation: Candidate 8 = `Track A Explicit · submarine_acoustics`; Candidate 6 = `Direct Anchor`]*
- **Runner-Up #3:** `Candidate 4` — objective telemetry-artifact verification + automated 6-hour pre-outage Masking Co-Liability ledger.
  - *[Coordinator post-triage annotation: source = `Track A Explicit · submarine_acoustics`]*
- **Wildcard:** `Candidate 3`'s *Global Edge-to-Leaf Closure Audit* — periodically reconciling attributed incidents against edge customer-observed failures to fire a deterministic Closure Fault whenever telemetry drops or aggressive gating silently masks a real outage.
  - *[Coordinator post-triage annotation: rescued from `KILL`-ed `Track B Blind · thermodynamics_cryogenics`]*

---

## Step 6b. Stage 2b — Clean-Context Hardening & Selective Grafting (`subagent: dcb780dd`)

### Final Mechanism Name
**Defensible-Space Alert Zoning with Causal-Frontier Collapse & Recovery-Coupled Stoop Tether**

### Summary of Hardened Spec
1. **CI/OPA Two-Zone Admission:** `zone: corridor` (strictly edge/customer-journey SLIs + flow-conservation invariants) vs. `zone: stoop` (all new internal symptom rules, routed only to authoring team's daytime queue). Every manifest must declare `owner`, a state-mutating executable `affordance` (no read-only dashboard links), `target_invariant`, `recovery_window`, and `lever_class` (`structural` vs. `ephemeral_lever`).
2. **Recovery-Coupled Graduation Gate:** Internal rules graduate only upon **>=75% verified yield across >=4 firings in 14 days** (or passing a synthetic fire-drill for rare failures) where executing the affordance emits a signed state-change diff AND restores the bound invariant by >=50% without re-firing within `churn_cooldown` (60 min). `ephemeral_lever` restarts/flushes face a stricter 4h non-recurrence / max 1-per-24h anti-band-aid cap.
3. **Runtime Causal-Frontier Collapse (Grafted Inside Corridor):** Live 60s eBPF/service-mesh RPC telemetry requires **>=70% RPC error-origin correlation** (not mere time proximity) to mark an upstream breach `HELD_CASCADE`, paging only the deepest breaching Causal Frontier `F` while holding upstream pages for 3 min (Tier-0) / 5 min (Tier-1) with **four deterministic fail-open releases**: (a) unacked frontier past 3 min SLA, (b) >25% local/mismatched RPC error origin, (c) residual burn 2 min post-frontier recovery, (d) stale/missing telemetry (>30s). Auto-cleared `cascade_absorbed` alerts are excluded from Stoop-Debt strikes.
4. **Co-Page Stoop Tether & 14-Day Custody Probation:** 2 non-actionable strikes in 30 days bind a Co-Page Tether waking both responder and rule `CODEOWNERS` author/lead; 3 strikes auto-demote via GitOps PR back to `zone: stoop` (mandatory Tier-0 edge SLIs stay Co-Page Tethered rather than going dark). Git-detected `CODEOWNERS` transfers trigger a **14-day Custody Probation Window** (`Adopt / Demote / Retire` PR) so inherited legacy rules never ambush new owners.
5. **Remaining Boundary:** Async broker hops (Kafka/SQS) intentionally fail open until producer-topic-consumer lineage invariants are registered; roll out in three 2-week phases (Shadow Tagging → New-Rule Zoning + Corridor Collapse → Legacy Amnesty + Co-Page Activation).
