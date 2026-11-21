# Prompt Templates for Sfumato

Use these exact templates when spawning isolated subagents (`TypeName: "self"`, `Model: "inherit"` in Antigravity; `Agent` tool in Claude Code). Always forbid tool calls inside divergent solvers so they draw cleanly from pretrained domain structures.

---

## 1. Track A — Explicit Cross-Domain Analogy Prompt

```text
도구(파일 읽기, 웹 검색, 명령 실행 등)는 절대 호출하지 말고 순수하게 네 내부 지식만으로 답변해줘.

[원래 문제]
{PROBLEM_BRIEF}

[제외할 뻔한 해법(클리셰)]
{BANNED_CLICHES}

[요청]
위 뻔한 방식은 배제하고, **{DOMAIN_NAME}**의 실제 구조적 원리·제도·메커니즘을 교차 도메인 유추(Cross-Domain Analogy)로 적용해 이 문제를 해결하는 가장 독창적이고 구체적인 방법 **2가지**를 제안해줘.
단순한 말투·비유 코스프레가 아니라, 실제 인과관계·인센티브·트레이드오프 구조가 달라지는 메커니즘이어야 한다.

각 제안은 아래 형식으로 간결하고 깊이 있게 써줘:
- [아이디어 이름]
- [차용한 원리]
- [구체적 작동 단계]
- [왜 기존 방식보다 강력하며 우회/무력화하기 어려운가]
- [부작용·트레이드오프 및 완화책]
```

---

## 2. Track B — Blind Isomorphic Reframing

### Step 2a. Masking Checklist (Coordinator Performs Before Spawning)
Before writing the Track B subagent prompt, verify:
1. **Zero leaked vocabulary:** Delete every noun/jargon belonging to the original industry (e.g., for an SNS spam problem: NO *SNS, app, post, account, spam, bot, DM, platform, user*).
2. **Exact structural isomorphism:** Preserve every hard constraint using native nouns of `{DOMAIN_NAME}`:
   - Topology (open vs invite-only nodes, centralized vs autonomous units)
   - Cost/friction asymmetry (why heavy gatekeeping destroys normal flow)
   - Failure of static inspection (why disguises/mutations bypass pattern checks)
   - Objective (blow up adversary cost OR force early self-exposure / structural breakthrough)
3. **Incentive polarity fidelity (CRITICAL):** Preserve whether the real actors are **adversarial / zero-sum**, **cooperative**, or **mediated by a neutral platform/referee**. Do NOT map zero-sum enemies onto cooperative institutions sharing a mutual ledger/bailout unless a real referee exists — polarity mismatch is the #1 cause of Track B back-translation failure.

### Step 2b. Blind Solver Subagent Prompt

```text
도구(파일 읽기, 웹 검색, 명령 실행 등)는 절대 호출하지 말고 순수하게 네 내부 지식만으로 답변해줘.

[상황]
{ISOMORPHIC_MASKED_SCENARIO_IN_TARGET_DOMAIN}

[요청]
{MASKED_BANNED_CLICHES} 같은 뻔한 방식 말고, **{DOMAIN_NAME}**의 실제 원리를 활용해 위 문제의 핵심 제약을 정면으로 돌파하는 가장 독창적이고 구체적인 설계 **2가지**를 제안해줘.

각 설계는 아래 형식으로 간결하고 깊이 있게 써줘:
- [설계 이름]
- [핵심 원리]
- [작동 단계]
- [왜 회피/무력화하기 어려운가]
- [부작용·트레이드오프]
```

### Step 2c. Back-Translation Rule (Coordinator Performs After Blind Solver Returns)
- Map ONLY the **causal mechanism, incentive shift, and trade-off** back to the original problem's concrete product/system primitives.
- **Discard ruthlessly:** If translating a Blind idea requires stretching a metaphor or breaks down in the real domain, drop it and note it as a translation loss. Do NOT pad weak ideas.

---

## 3. Stage 2 — Clean-Context Red-Team Gate & Top-K Selector Prompt

Spawn 1 fresh clean-context subagent (after stripping all track labels and noisy framing transcripts):

```text
도구 호출 없이 순수 판단으로만 답변해줘.

[원래 문제]
{PROBLEM_BRIEF}

[후보 아이디어 목록 (출처 비공개)]
{NORMALIZED_ANONYMIZED_CANDIDATES}

[평가 규칙 — 3단계 레드팀 게이트 + 최고점(Max Ceiling) 선발]
1. **표면 비유(코스프레) 즉시 탈락:** 타 분야 용어만 빌려 썼을 뿐 실제 인과 구조가 기존 뻔한 해법과 동일한 후보는 탈락시킨다.
2. **레드팀 치명결함 게이트 (Top-1 진입 필수 관문):** 각 후보에 대해 아래 3가지를 냉정하게 검증해 치명적 결함이 있으면 Top-1 자격을 박탈한다:
   - (a) **역선택(Adverse Selection):** 공격자/봇보다 정상 유저·일반 참여자를 더 심하게 괴롭히거나 탈락시키지 않는가?
   - (b) **시빌/자전거래 악용(Exploit):** 신원인증 없이 계정 2개 공모·허수거래로 쉽게 뚫리거나 차익 파밍을 당하지 않는가?
   - (c) **구현 불가능성/금지 전제 위반:** 금지된 요소(예: 숨은 AI 심판 봇, 적자 보조금)를 몰래 전제하거나 자동화가 불가능하지 않은가?
3. **생존 후보 중 최고점(Top-1) 선발:** 레드팀 게이트를 통과한 후보들 중, **구조적 참신성 × 실전 파급력**이 가장 높은 Champion을 선발한다. 차순위(2~3위)는 Top-1과 서로 다른 메커니즘 축을 대표해야 한다.

[출력 형식]
1. **Top-1 (Champion):** 후보 번호, 핵심 메커니즘 2줄 요약, 왜 뻔하지 않고 강력한지, 가장 치명적인 리스크 1개
2. **차순위 추천 (2~3위):** 각 3줄 요약
3. **와일드카드 (선택, 최대 1건):** 레드팀 결함으로 Top-1은 못 올랐지만 발상 자체가 날카로워 보완 가치가 있는 돌연변이
4. **레드팀 탈락 사유 한 줄 정리:** 표면 비유 또는 치명결함으로 탈락시킨 후보들
```
