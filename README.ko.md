<div align="center">

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/960px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg" height="230" alt="모나리자 — 레오나르도 다빈치의 스푸마토" />
  &nbsp;&nbsp;
  <img src="https://upload.wikimedia.org/wikipedia/commons/c/c5/Leonardo_Design_for_a_Flying_Machine%2C_c._1488.jpg" height="230" alt="다빈치 비행기계 스케치 (1488)" />
  &nbsp;&nbsp;
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Da_Vinci_Vitruve_Luc_Viatour.jpg/960px-Da_Vinci_Vitruve_Luc_Viatour.jpg" height="230" alt="비트루비우스적 인간 — 교차 도메인 비례" />
</p>

# 🎨 Sfumato (스푸마토)

### *도메인의 경계를 지워 AI 동질화(Artificial Hivemind)를 깨고, 탐색 다양성의 테스트 타임 스케일링을 여는 초경량 스킬*

<p>
  <a href="./README.md">English</a> · <a href="./README.ko.md"><strong>한국어</strong></a> · <a href="./README.ru.md">Русский</a> · <a href="./README.zh-CN.md">简体中文</a>
</p>

<p>
  <img src="https://img.shields.io/badge/9%ED%9A%8C_%EB%B2%A4%EC%B9%98%EB%A7%88%ED%81%AC_%EB%8B%A4%EC%96%91%EC%84%B1-9%2F9_%EC%A0%84%EC%8A%B9_(60_vs_34)-B83B2A?style=for-the-badge" alt="9/9 다양성 전승" />
  <img src="https://img.shields.io/badge/K=12_%EC%8A%A4%EC%BC%80%EC%9D%BC%EB%A7%81-3.0%C3%97_(18_vs_6)-8E2F21?style=for-the-badge" alt="3.0x 스케일링" />
  <img src="https://img.shields.io/badge/Claude_Opus_5.5-%EA%B1%B0%EC%A0%88_0%EA%B1%B4_(safe--profile)-2F5D62?style=for-the-badge" alt="Claude 거절 0건" />
  <img src="https://img.shields.io/badge/%EC%99%B8%EB%B6%80_%EC%9D%98%EC%A1%B4%EC%84%B1-0_(Pure_Stdlib)-5C4E3F?style=for-the-badge" alt="외부 의존성 0" />
</p>

> *'스푸마토(Sfumato, 연기처럼 경계를 흐린다)'는 레오나르도 다빈치가 딱딱한 윤곽선을 지워 전혀 새로운 형상을 끌어낸 회화 기법입니다. 다빈치는 한 분야에 갇히지 않고 해부학·유체역학·축성술·광학의 원리를 서로 이식해 발명을 만들어냈습니다.*
>
> **Sfumato**는 외부 RAG도, 파인튜닝도, 외부 라이브러리도 없이 **평문 파일 4개(`/sfumato`, `/sfm`)**만으로 AI 에이전트의 아이디어 탐색 폭을 넓히고 하방(`Direct Anchor`)을 지키면서 돌파구를 찾습니다.

</div>

---

## 🔥 문제의식: 왜 LLM은 아무리 다시 물어도 똑같은 아이디어만 낼까?

코딩이나 엄밀한 추론에서는 **관련 있는 깨끗한 컨텍스트**만 넣는 게 정석입니다. 무관한 정보는 주의를 분산시켜 정확도를 떨어뜨립니다.

**하지만 열린 브레인스토밍에서는 정반대 현상이 벌어집니다.**

아무리 완전히 격리된 새 세션에서 12번을 반복해 물어도, LLM은 통계적으로 가장 무난한 3~6개의 교과서 클리셰로 수렴합니다(*Artificial Hivemind*, NeurIPS 2025). `temperature`를 높이면 독창적이 되기 전에 논리가 먼저 무너지고, 멀티에이전트 토론을 붙이면 합의 편향 때문에 다양성이 오히려 더 쪼그라듭니다(*Diversity Collapse*, 2026).

> **🧪 실제 파일럿에서 포착된 스모킹 건 (`OSS-PR`):**
> *"오픈소스 저장소의 AI 슬롭 PR 홍수를 막는 법"*을 물었을 때, 서로 완전히 격리된 **3개 세션**(`Direct Baseline 1`, `Direct Baseline 2`, 심지어 `열역학 Explicit`까지)이 **독립적으로 똑같은 예시 패키지 문자열 `pkg@pr-4821` / `pkg@patch-4821`을 생성**했습니다.
>
> 반면 Sfumato의 **Blind 동형 마스킹(Track B)** 세션들은 단 1건도 `4821`이나 Baseline 클리셰에 빠지지 않았습니다.

---

## 📈 탐색 다양성의 테스트 타임 스케일링 (실측 데이터, `K = 1..12`)

*"방망이를 더 많이 휘두르면 실제로 새로운 구조적 메커니즘이 계속 나오는가?"*를 검증하기 위해, 대표적 공개 난제(**양면 마켓플레이스의 감시·벌금·보조금 없는 직거래 이탈 방지**)에서 **완전 격리 12세션(총 24아이디어)**을 돌려 인과 메커니즘 기준으로 엄격히 중복 제거했습니다.

<p align="center">
  <img src="./assets/scaling_curve.svg" alt="Sfumato vs Direct Best-of-N 스케일링 곡선" width="100%" />
</p>

| 지표 (`K = 12` 격리 세션 · 각 24개 아이디어 생성) | Direct Best-of-N | **Sfumato Dual-Track** | 격차 |
|---|---:|---:|---:|
| **발견된 고유 구조 메커니즘 수** | `6 / 24` (`25.0%`) | **`18 / 24` (`75.0%`)** | **3.0배** |
| **후반 4세션(9~12회차, 8개)의 신규 메커니즘 수** | `0개` *(완전 포화)* | **`+5개` *(여전히 상승 중)*** | **포화 없음** |
| **Track B(블라인드) 고유율 / Baseline 중복 수** | — | **`83.3%` / `0건` 중복** | 클리셰 중력 0 |
| **순서교차 블라인드 A/B 심판 (`AB` · `BA`)** | `0–2` *(21:24, 20:23)* | **`2–0` 완승 *(24:21, 23:20)*** | 위치 편향 제거 |

> **핵심 결론:** **Direct Best-of-N**은 세션을 아무리 늘려도 6종에서 즉시 벽에 막혀 평탄화(75% 중복)됩니다. 반면 **Sfumato**는 세션 수(`K`)를 늘릴수록 매번 다른 클러스터에서 고유 메커니즘이 계속 발굴되는 **탐색 다양성의 테스트 타임 스케일링**을 열어줍니다.

---

## 🌍 다중 난제 · 교차 모델 벤치마크 (다양성 `9 / 9` 전승)

*"마켓플레이스 게임이론 말고 **감성·UX 설계**, **오픈 웹 크롤러 방어**, **소프트웨어 아키텍처**, 그리고 **Claude Opus 5.5** 같은 타 모델에서도 통하는가?"*

**동일 후보 예산(`Iso-Candidate-Budget`: Stage 1 격리 솔버 4회 × 2아이디어 = 방식당 8개 후보) + 순서교차 블라인드 심판(`AB`·`BA`)**으로 공개 난제 **7종(Gemini 4 Neon)**과 **Claude Opus 5.5 교차 모델 2종**을 검증했습니다. Claude에서는 민감한 생물·사이버·방첩 8개 도메인을 제외한 `--safe-profile claude`를 적용해 **24회 호출 동안 안전 거절 0건**을 기록했습니다. *(Sfumato는 Stage 1 후보 수는 동일하되 코디네이터 마스킹·역번역과 Stage 2a/2b 평가 호출이 추가됩니다 — 아래 비용 표 참고.)*

<p align="center">
  <img src="./assets/multi_problem_benchmark.svg" alt="다중 난제 및 교차 모델 벤치마크: 다양성 9/9 전승" width="100%" />
</p>

### 기본 실행 결과 (`python tools/summarize_benchmarks.py benchmarks/v2 --strict` 출력과 100% 일치)

| 공개 난제 | 모델 | Direct 고유/8 | Sfumato 고유/8 | 다양성 배수 | 기본 블라인드 `AB · BA` (30점) | 최종 판정 |
|---|---|---:|---:|---:|---|---|
| **`MKT-DIS`** *(마켓플레이스 직거래 방지)* | Gemini 4 Neon | 3 / 8 | **7 / 8** | **2.33×** | **24:21 · 23:20** | **Sfumato 2–0 승** |
| **`UX-ONBOARD`** *(빈 화면 공포 해소 · 감성 UX, v2.0)* | Gemini 4 Neon | 4 / 8 | **7 / 8** | **1.75×** | **25:20 · 24:21** | **Sfumato 2–0 승** |
| **`WEB-SCRAPE`** *(오픈 웹 vs 대규모 AI 스크래퍼)* | Gemini 4 Neon | 6 / 8 | **7 / 8** | **1.17×** | **22:18 · 20:18** | **Sfumato 2–0 승** |
| **`OSS-PR`** *(오픈소스 AI 슬롭 PR 홍수 방어)* | Gemini 4 Neon | 2 / 8 | **5 / 8** | **2.50×** | **21:17 · 18:21** | **Split 1–1** |
| **`AI-ARCH`** *(AI 코딩 에이전트 아키텍처 침식)* | Gemini 4 Neon | 4 / 8 | **7 / 8** | **1.75×** | **23:22.5 · 22.5:24** | **Split 1–1** |
| **`DOC-ROT`** *(자가 치유 조직 문서 부패, v1.2 기본)* | Gemini 4 Neon | 2 / 8 | **6 / 8** | **3.00×** | 22:24 · 21:24 | Direct 2–0 *(아래 v2.0 절제 참고)* |
| **`GAME-SNOWBALL`** *(스노우볼 vs 억지 고무줄, v1.2)* | Gemini 4 Neon | 5 / 8 | **7 / 8** | **1.40×** | 22:23 · 21:23 | Direct 2–0 *(아래 v2.0 절제 참고)* |
| **`MKT-DIS`** *(교차 모델 · `--safe-profile claude`)* | **Claude Opus 5.5** | 4 / 8 | **7 / 8** | **1.75×** | 18:19 · **20:17** | **Split 1–1** *(거절 0)* |
| **`DOC-ROT`** *(교차 모델 · `--safe-profile claude`)* | **Claude Opus 5.5** | 4 / 8 | **7 / 8** | **1.75×** | 20:22 · 20:22 | Direct 2–0 *(Anchor 미포함 · 거절 0)* |
| **전체 누적 (기본 9회 · 방식당 72아이디어)** | **2개 모델** | `34 / 72` (`47.2%`) | **`60 / 72` (`83.3%`)** | **1.76×** | **9 Sfumato : 9 Direct** | **다양성 9/9 · 3승 3무 3패** |

### v2.0 Stage 2b 동등 경화(Equal-Hardening) 절제 실험 (성공·역효과 모두 공개)

| 공개 난제 | v1.2 기본 (`S:D`) | v2.0 동등 경화 (`S:D`) | Sfumato 변화 | 판정 및 교훈 |
|---|---:|---:|---:|---|
| **`DOC-ROT`** | `43 : 48` *(0–2)* | **`46 : 48`** *(23:22 · 23:26)* | **+3** | **Split 1–1** — 수정 가능한 크로스도메인 원석(`thermodynamics_cryogenics`) 경화로 격차 해소 |
| **`GAME-SNOWBALL`** *(v1.2 풀, 억지 접목)* | `43 : 46` *(0–2)* | `39 : 45` *(20:22 · 19:23)* | **−4** | **Direct 2–0** — 극성이 안 맞는 원석을 억지로 접목하면 오히려 악화됨을 입증 (Anchor 우선 원칙 확립) |
| **`GAME-SNOWBALL`** *(Pool v2.0: 74도메인 / 11클러스터)* | `43 : 46` *(0–2)* | **`46 : 39`** *(고유 8/8)* | **+3** | **Sfumato 2–0 승** — 인지·재료·전력망 클러스터 확충으로 극성 미스매치 해소 ([로그](./benchmarks/v2/ablations/game_snowball_pool_v2_results.json)) |

### 독립 교차 모델 블라인드 심판 감사 (동일 모델 자기평가 편향 제거)

동일 모델 패밀리 자기평가 편향을 점검하기 위해, **Claude Opus 5.5**를 독립 읽기 전용 심판(`AB`·`BA` 순서 교차)으로 투입해 **Gemini 4 Neon 기본 7개 난제의 우승안 쌍**을 재채점했습니다([`benchmarks/v2/cross_model_judges/claude_on_gemini.json`](./benchmarks/v2/cross_model_judges/claude_on_gemini.json)).

- **교차 모델 심판 결과:** **3승(`MKT-DIS` 2–0, `WEB-SCRAPE` 2–0, `AI-ARCH` 2–0) · 1무(`GAME-SNOWBALL` 1–1) · 3패(`UX-ONBOARD`, `OSS-PR`, `DOC-ROT` v1.2)** — **7 Sfumato : 7 Direct** (7문제 중 6문제에서 순서 편향 0).
- **데이터가 정직하게 말해주는 사실:**
  - **모델과 무관하게 입증된 강점:** **다양성 9/9 전승(`K=4` 1.76배, `K=12` 3.0배)**으로 Direct 프롬프팅이 닿지 못하는 구조적 대안을 일관되게 발굴하며, `MKT-DIS`·`WEB-SCRAPE`는 Gemini와 Claude 심판 모두에서 2–0 완승(`AI-ARCH`는 Claude 심판 2–0 승)을 거뒀습니다.
  - **솔직한 한계(문제당 시드 `n=1`):** 강력한 4회 Direct Best-of-N 대비 단발 Top-1 승률은 호각(`9:9` 기본, `7:7` 교차 심판)이며, Track B(블라인드)는 단독 1위보다는 클리셰를 깨는 와일드카드·관점 전환 공급원으로 빛납니다. 그래서 **Sfumato v2.2는 `dual-track`과 `deep` 모드 모두에 Direct Anchor를 기본 포함**해 하방(`≥ Direct`)을 잠그면서 1.7~3배 넓은 탐색 공간을 확보합니다.
- **재현 로그 및 종단간 실행 기록:**
  - 기본 9회 + v2.0 Stage 2b 절제 2건(`v2_ablation_*.json`) 로컬 검증: `python tools/summarize_benchmarks.py benchmarks/v2 --strict` *(별도 Pool v2.0 실행 로그는 [`game_snowball_pool_v2_results.json`](./benchmarks/v2/ablations/game_snowball_pool_v2_results.json)에 수록)*
  - 구조화 벤치마크 요약 및 채점 근거: [`benchmarks/v2/`](./benchmarks/v2/)
  - Claude Opus 5.5 독립 교차 심판 로그: [`benchmarks/v2/cross_model_judges/claude_on_gemini.json`](./benchmarks/v2/cross_model_judges/claude_on_gemini.json)
  - v2.1 아카이브 종단간 실행 기록 (`sample_domains.py` → 격리 솔버 4개 요약 → Stage 2a `PASS/HARDEN/KILL` → Stage 2b 경화; v2.2에서는 이 기록에 등장하는 정규식 누출 스크립트를 폐기하고 공유 골격·전체 프롬프트 재독으로 단순화): [`benchmarks/v2/transcripts/alert_fatigue_v2_1_full_transcript.md`](./benchmarks/v2/transcripts/alert_fatigue_v2_1_full_transcript.md)

---

## 🏛️ Sfumato v2.2 작동 원리: *도메인 마스킹 트레이드오프*

기존 교차 도메인 유추 연구는 대부분 **Explicit Analogy**(*"생물학 원리로 마켓플레이스 문제를 풀어봐"*)만 씁니다. 원문제 어휘가 프롬프트에 남아 있어 일부 해법이 여전히 기존 업계 클리셰로 끌려가는 **부분 동질화**가 발생합니다.

반대로 원문제 어휘를 100% 지우는 **Blind Isomorphic Masking**은 클리셰 중력을 0으로 끊어 극단적 돌연변이를 만들어내지만, 역번역 손실 때문에 평균 타율은 낮습니다.

**Sfumato v2.2는 Direct Anchor와 두 크로스도메인 트랙을 상호 격리 병렬로 실행한 뒤, 공유 구조 골격 기반 마스킹과 클린 컨텍스트 레드팀 트리아지·선택적 경화로 최고점(Top-1)을 완성합니다.**

<p align="center">
  <img src="./assets/architecture_codex.svg" alt="Sfumato v2.2 아키텍처 다이어그램" width="100%" />
</p>

1. **극성 인식 클러스터 층화 코드 난수 (`sample_domains.py`):** LLM에게 "아무 분야나 골라봐"라고 하면 매번 *개미·재즈·체스*만 고릅니다. Sfumato는 11개 대분류 **74개 고밀도 메커니즘 도메인**에서 파이썬 난수로 겹치지 않게 뽑으며, 기본적으로 `mechanisms` 힌트를 생략해 도메인 내부 동질화를 막습니다(`--include-hints`로 선택 활성화). `--polarity` (`adversarial | cooperative | physical_loop | human_ux | systems_ops`)로 최소 절반은 문제 극성과 구조적으로 맞는 클러스터에서 추출하고, Claude에서는 `--safe-profile claude`로 **11개 전 클러스터 균등 6개씩 66개 안전 도메인·거절 0건**을 유지합니다.
2. **Direct Anchor *(`dual-track`·`deep` 기본 포함 · 하방 보장)*:** 익명 셀렉터 풀에 정면 Baseline 1개를 기본 포함해 `max(Direct, Explicit, Blind) ≥ Direct` 하방을 잠급니다.
3. **Track A — Explicit Analogy *(고타율·정밀 타격)*:** 원문제 브리프 + 배정 원격 도메인 → 도메인 고유의 공격면을 정밀 저격.
4. **Track B — Blind Isomorphic Masking *(최고점 돌연변이 · 공유 3줄 구조 골격 + 고유 제약 내재화)*:**
   - 원문제를 한 번 **비공개 3줄 도메인 중립 구조 골격**(행위자·비용 부담자·인센티브 극성 · 핵심 비대칭 · 정적 통제 실패 원인)으로 압축하고, 팬아웃 전 원문제 브리프와 대조해 극성·비용 부담자 정합성을 먼저 확정합니다.
   - 각 원격 분야 실무자가 실제로 다룰 법한 독립 시나리오로 `{USER_LANGUAGE}`에 맞춰 재작성하되, 금지 클리셰는 별도 목록이 아니라 시나리오 안의 물리·제도적 제약으로 자연스럽게 녹여 넣은 뒤 발송 직전 전체 프롬프트를 1회 재독합니다(실무성·원본 용어 혼입 여부·극성 보존 점검).
   - 원래 문제를 전혀 모르는 격리 세션이 순수 타 분야 해법을 도출 → **원문제 클리셰 중력 = 0**.
   - 인과 메커니즘과 트레이드오프만 역번역 (억지 비유는 과감히 폐기).
5. **Stage 2a/2b — 클린 컨텍스트 레드팀 트리아지(`PASS / HARDEN / KILL`) & 선택적 경화:**
   - **Stage 2a:** 출처가 지워진 깨끗한 평가자가 표면 비유 코스프레·역선택·시빌/자전거래 악용·현실성을 점검해 모든 후보를 `PASS` / `HARDEN`(수정 가능한 단일 약점 명시) / `KILL`로 3분류합니다.
   - **Stage 2b:** 최종 선발된 Top-1 1건의 단일 운영 약점만 정밀 보강하며(필요 시 통과한 차순위 후보의 실무 장치 1개를 선택 접목 — 더 강한 Direct Anchor 위에 극성이 안 맞는 원석을 억지 접목하지 않음), 핵심 비클리셰 메커니즘은 희석하지 않습니다.
   - **글로벌 다국어 중립 템플릿:** `prompt_templates.md`와 `domain_pool.json`은 영어 기준으로 정비되고 모든 프롬프트에 `Respond in {USER_LANGUAGE}.`를 명시해, 한국어·영어·러시아어·중국어 등 사용자 언어에 맞춰 일관되게 출력합니다.

---

## ⚡ 비포 / 애프터 실제 사례: 양면 마켓플레이스 직거래 이탈 방지 (`MKT-DIS`)

> **문제:** 프리랜서·과외·청소·인테리어 플랫폼에서 첫 매칭 후 수수료(10~20%)를 아끼려 카톡·현금 직거래로 빠져나가는 문제. *(금지 클리셰: 채팅 검열·위약금·단순 에스크로/보험·적자 캐시백·수수료 무료화)*

| 방식 | 실제 도출된 아이디어 | 결정적 차이 |
|---|---|---|
| **Direct Best-of-N**<br>*(12세션 · 24아이디어)* | 24개 중 18개가 똑같은 3종 반복: *T+0 역에스크로*, *단골 장부 승계*, *취소 공실 백필*. | 실무적으론 탄탄하지만 기존 핀테크·운영 정석의 울타리 안에 갇힘. |
| **Sfumato · 최종 우승**<br>*(기생생물학 · 유성생식의 2배 비용)* | **🏆 키메라 교차 재조합 프로토콜** *(Gemini·Claude 심판 모두 2–0 완승)* — 반복 수수료(15~18%) 중 5~7%를 매 N회차 **독립 제3자 전문가의 10~15% 교차 검증 슬롯**(과외 블라인드 모의진단, 인테리어 열화상·수평 감리, 개발 시니어 크로스리뷰)으로 환원. | 1:1 현금 직거래는 제3자 검증을 물리적으로 복제할 수 없어 담합 가격 구간이 소멸하며, **공급자가 직거래를 제안하는 순간 '품질 검증 회피(레몬 신호)'로 역전**됨. |
| **Sfumato · Track B 블라인드**<br>*(옴부즈만 · 암호학적 공증)* | **영지식 청렴·면책 공증 트랙** — 단가·산출물 커밋과 보복 불가 내부고발 부존재 증명으로 법인·관리단·팀 발주자에게 **감사 통과·배임 의심 면책권** 부여. | 직거래를 "15% 절약"이 아닌 "법인/이사회 배임 리스크 노출"로 재정의. |
| **Sfumato · Track B 블라인드**<br>*(인류학 · 쿨라 링)* | **쿨라 계보 각인제** — 온플랫폼 거래 산출물에만 장인·공정 계보를 각인해 2차 시장 가치(주택 매도 가치·VC/M&A IP 실사·공식 포트폴리오) 증폭. | 직거래 산출물은 계보가 끊긴 '무명품'이 되어 제3자 시장 가치가 증발. |
| **Sfumato · 레드팀 방어 사례**<br>*(유체역학 · 벤투리 이젝터)* | **벤투리 부압(음의 수수료) 흡입기** — 긴급/법인 고마진 수요(160) 호출옵션 차익으로 반복 거래 수수료를 마이너스(수요자 90 → 공급자 93)로 역전. | 기발한 물리 이식이었지만, **레드팀 게이트가 "지인 허수거래 차익거래(90→93)" 치명 허점을 즉시 적발해 Top-1 오선발을 차단!** |

<details>
<summary><strong>📊 전체 12세션(24아이디어) 누적 발산 로그 펼치기 (Sfumato 18종 vs Direct 6종)</strong></summary>

<br/>

#### Direct Best-of-N (`K = 1..12`, 24개 → **고유 6종**, K=8부터 완전 평탄화)
1. **단골 장부 자산화 & 승계 로열티** *(12세션 중 6회 출현)*
2. **T+0 역에스크로 · 만기 변환 정산** *(6회)*
3. **취소 공실 자동 백필 & 대타 백업** *(6회)*
4. **앵커 단골 신규 수수료 배당권** *(4회)*
5. **유휴 슬롯 현물 수수료 정산** *(1회)*
6. **B2B 투입재 도매 차익 & 세무 증빙 레일** *(3회)*

#### Sfumato Dual-Track (`K = 1..12`, 24개 → **고유 18종**, K=12에서도 계속 상승 중)
| 회차 | 트랙 · 원격 도메인 | 새로 발견된 고유 메커니즘 | 누적 |
|---:|---|---|---:|
| 1 | Explicit · 유체역학 | ① 벤투리 음의 수수료 호출옵션 흡입 · ② 미세유체 다중 층류 분획 | 2 |
| 2 | Blind · 해상 무역 길드 | ③ 다자 상계청산(Giro) 장부 · ④ 공인 적하목록 합적 & 제3자 권리 분리 | 4 |
| 3 | Explicit · 기생생물학 | ⑤ **키메라 교차 재조합 (🏆 2–0 우승)** · ⑥ 역에스크로 대사 시차 변환 | 6 |
| 4 | Blind · 기계식 시계 공학 | ⑦ 차동 르몽투아르 소득·용량 평활화 허브 *(1건 번역 손실 폐기)* | 7 |
| 5 | Explicit · 재난 의학 트리아지 | ⑧ 동적 재평가 스코프 크립 자동 격리 방패 *(1건 층류 분획과 중복)* | 8 |
| 6 | Blind · 컨테이너 항만 물류 | ⑨ 양면 듀얼 사이클링 공차 제로 왕복 체인 · ⑩ 버퍼 야드 시차 분리(Drop-and-Hook) | 10 |
| 7 | Explicit · 근세 축성·병참학 | ⑪ 중앙 병참고 종량제 툴 라이선스 & 잔여 자재 반품권 *(1건 대타와 중복)* | 11 |
| 8 | Blind · 옴부즈만·내부고발 | ⑫ 영지식 청렴·배임 면책 공증 트랙 · ⑬ 임계치 익명 하도급 조기경보 에스크로 | 13 |
| 9 | Explicit · 건축 동선 유도 | ⑭ 오픈 아트리움 라이브 공정 쇼윈도(CPTED 자연 감시) *(1건 왕복 체인과 중복)* | 14 |
| 10 | Blind · 전자전·신호처리 | ⑮ 전역 충돌 정렬 다자 스케줄 멀티플렉싱 *(1건 번역 손실 폐기)* | 15 |
| 11 | Explicit · 식물 균근 네트워크 | ⑯ 3차 영양단계 외부 보험·여신사 프라이밍 시그널링 *(1건 중복)* | 16 |
| 12 | Blind · 인류학 증여 경제 | ⑰ 쿨라 계보 2차 시장 가치 각인제 · ⑱ 포틀래치/하우 다자 지연 호혜 타임뱅크 | **18** |

</details>

---

## 🚀 설치 및 사용법 (평문 파일 4개 · 외부 의존성 0)

Sfumato 본체는 [`skill/sfumato/`](./skill/sfumato/) 안의 **직접 열어볼 수 있는 4개 파일**이 전부입니다:
- `SKILL.md` — 스킬 지침, 멀티 에이전트 실행 가이드(Claude Code · Antigravity · Codex CLI) 및 워크플로
- `references/prompt_templates.md` — 언어 중립(`{USER_LANGUAGE}`) Anchor · Explicit · Blind · Stage 2a 트리아지 · Stage 2b 경화 템플릿
- `resources/domain_pool.json` — 11개 대분류 클러스터 × 74개 메커니즘 도메인(`66`개 Claude-safe, 클러스터당 6개 균등) + 극성 친화도 태그
- `scripts/sample_domains.py` — 파이썬 표준 라이브러리만 사용하는 극성 인식 층화 샘플러 (네트워크 호출·파일 쓰기 없음)

**Claude Code**에서는 한 줄로 바로 설치하거나, 저장소를 클론해 파일 내용을 확인한 뒤 사용 중인 에이전트의 글로벌 스킬 폴더에 복사할 수 있습니다:

```bash
# Claude Code 원스텝 마켓플레이스 설치 (v2.1.275+)
/plugin install sfumato --marketplace Excelsus4/sfumato
```

```bash
git clone https://github.com/Excelsus4/sfumato.git && cd sfumato

# Claude Code (+ --safe-profile claude가 적용된 /sfm · /sfm-max 단축 커맨드)
cp -r skill/sfumato ~/.claude/skills/sfumato
cp commands/*.md ~/.claude/commands/

# Antigravity (agy)
cp -r skill/sfumato ~/.gemini/config/skills/sfumato

# Codex CLI
cp -r skill/sfumato ~/.codex/skills/sfumato
```

<details>
<summary>로컬 복사 도우미 스크립트 (클론 후 <code>--dry-run</code> 미리보기 지원)</summary>

```bash
# macOS / Linux
bash tools/install.sh --dry-run
bash tools/install.sh --target claude   # 또는 agy | codex | all | auto
```

```powershell
# Windows PowerShell
.\tools\install.ps1 -DryRun
.\tools\install.ps1 -Target claude      # 또는 agy | codex | all | auto
```

</details>

### 사용 예시 및 실행 모드별 비용

```text
/sfm 비대칭 3진영 RTS에서 스노우볼링과 억지 고무줄을 동시에 해결할 새 메카닉 뽑아줘
/sfumato deep 모드로 오픈소스 AI 슬롭 PR 홍수 방어법 브레인스토밍해줘
/sfm-max 우리 제품의 3년 해자를 만들 비선형 리텐션 구조 전수 탐색해줘
```

| 모드 | Stage 1 솔버 구성 | 총 격리 호출 수 | 예상 토큰 비용 (단일 Direct 대비) | 적합한 상황 |
|---|---|---:|---:|---|
| `fast` | `3 Explicit` (`--k 3 --mode explicit-only`) | `4회` *(3 + Stage 2a)* | 약 4~5× | 토큰·시간이 빠듯할 때 빠르게 비클리셰 대안 도출 |
| `dual-track` *(기본)* | `1 Direct Anchor + 2 Explicit + 1 Blind` (`--k 3`) | `5~6회` *(4 + Stage 2a + 선택 2b)* | 약 6~8× | 일상적인 고난도 브레인스토밍 (벤치마크 표준 구성 · `≥ Direct` 하방 보장) |
| `deep` | `1 Direct Anchor + 3 Explicit + 3 Blind` (`--k 6`) | `8~9회` *(7 + Stage 2a + 선택 2b)* | 약 10~12× | 막힌 핵심 전략·아키텍처 난제에서 최대 탐색 폭이 필요할 때 |
| `sweep` *(선택 전용)* | `1 Direct Anchor + 11도메인` (`--k 11`, 전 클러스터 1개씩) | `13~14회` *(12 + Stage 2a + 선택 2b)* | 약 15~18× | 11개 지식 축 전체 1회전 커버 |
| `max` (`/sfm-max`, *선택 전용*) | **가용 전수 66(Claude) / 74개** (`--all`) + **1 Direct Anchor** → **2라운드 토너먼트** | `79~80` / `87~88회` | 약 80~90× | 토큰을 아끼지 않는 핵심 전략·메카닉 전수 탐색 *(실행 전 호출 수 필수 확인)* |

---

## 📚 연구 기반

Sfumato는 2025~2026년 LLM 창의성 연구의 네 가지 흐름 위에 설계되었습니다:
- **Artificial Hivemind: The Open-Ended Homogeneity of Language Models (and Beyond)** — Liwei Jiang 외, *NeurIPS 2025 D&B* ([arXiv:2510.22954](https://arxiv.org/abs/2510.22954)): 열린 아이디어 발산에서 발생하는 모델 내부 반복 및 모델 간 동질화 현상을 규명.
- **Diversity Collapse in Multi-Agent LLM Systems: Structural Coupling and Collective Failure in Open-Ended Idea Generation** — Nuo Chen 외, 2026 ([arXiv:2604.18005](https://arxiv.org/abs/2604.18005)): 밀집된 멀티에이전트 토론·합의 구조가 의미 다양성을 붕괴시킴을 입증 → Sfumato Stage 1의 엄격한 **무교신(zero-crosstalk) 병렬 격리** 근거.
- **Unlocking LLM Creativity in Science through Analogical Reasoning** — Andrew Shen, Shaul Druckmann, James Zou, 2026 ([arXiv:2605.11258](https://arxiv.org/abs/2605.11258)): 구조적 교차 도메인 유추가 해법의 다양성과 참신성을 대폭 끌어올림을 검증.
- **Assessing the Effect of Cross-Domain Mapping on Creativity in Humans and Large Language Models** — Qiawen Ella Liu, Marina Dubova, Henry Conklin, Takumi Harada, Thomas L. Griffiths, 2026 ([arXiv:2603.19087](https://arxiv.org/abs/2603.19087)): 프론티어 LLM은 출처 도메인이 충분히 멀고 구조적·기능적 관계를 이식할 때 독창성 향상을 얻음을 규명.
- **Sfumato의 엔지니어링 기여:** *Explicit Analogy*(고타율·부분 동질화)와 *Blind Isomorphic Masking*(저타율·클리셰 중력 0·극단적 관점 전환) 사이의 **도메인 마스킹 트레이드오프**를 **Direct Anchor 하방 보장**, **극성 인식 코드 난수**, **공유 골격·고유 제약 내재화 마스킹**, **클린 컨텍스트 레드팀 트리아지·선택적 경화**로 하나의 경량 워크플로에 통합했습니다.

---

<div align="center">

<img src="https://upload.wikimedia.org/wikipedia/commons/5/5f/Codex_Atlanticus.jpg" width="460" alt="레오나르도 다빈치 — 코덱스 아틀란티쿠스" />

*“영혼이 손과 함께 일하지 않는 곳에 예술은 없다.” — 레오나르도 다빈치*

<sub>본 문서에 사용된 레오나르도 다빈치의 모든 도판은 Wikimedia Commons 퍼블릭 도메인입니다.</sub>

</div>
