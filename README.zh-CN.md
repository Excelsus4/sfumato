<div align="center">

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/960px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg" height="230" alt="蒙娜丽莎 — 达·芬奇的晕涂法（Sfumato）" />
  &nbsp;&nbsp;
  <img src="https://upload.wikimedia.org/wikipedia/commons/c/c5/Leonardo_Design_for_a_Flying_Machine%2C_c._1488.jpg" height="230" alt="达·芬奇飞行器手稿（约 1488 年）" />
  &nbsp;&nbsp;
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Da_Vinci_Vitruve_Luc_Viatour.jpg/960px-Da_Vinci_Vitruve_Luc_Viatour.jpg" height="230" alt="维特鲁威人 — 跨领域比例" />
</p>

# 🎨 Sfumato

### *消融领域边界，打破「人工智能蜂群同质化」，释放探索多样性的测试时扩展（Test-Time Scaling）*

<p>
  <a href="./README.md">English</a> · <a href="./README.ko.md">한국어</a> · <a href="./README.ru.md">Русский</a> · <a href="./README.zh-CN.md"><strong>简体中文</strong></a>
</p>

<p>
  <img src="https://img.shields.io/badge/Diversity_Across_9_Runs-9%2F9_Undefeated_(60_vs_34)-B83B2A?style=for-the-badge" alt="9/9 多样性全胜" />
  <img src="https://img.shields.io/badge/K=12_Scaling-3.0%C3%97_(18_vs_6)-8E2F21?style=for-the-badge" alt="3.0倍扩展" />
  <img src="https://img.shields.io/badge/Claude_Opus_5.5-0_Refusals_(safe--profile)-2F5D62?style=for-the-badge" alt="Claude 0 拒答" />
  <img src="https://img.shields.io/badge/Dependencies-Zero_(Pure_Stdlib)-5C4E3F?style=for-the-badge" alt="零外部依赖" />
</p>

> *“Sfumato”（意大利语：如烟消散，中文常译作「晕涂法」）是列奥纳多·达·芬奇消融生硬轮廓、让全新形态自然浮现的绘画技法。达·芬奇从不把自己困在单一学科里——他将解剖学、流体力学、要塞筑城术与光学原理彼此移植，催生出惊人的发明。*
>
> **Sfumato** 是一款超轻量级智能体技能（`/sfumato`、`/sfm`），让前沿大语言模型也做到同样的事——**仅 5 个纯文本文件，无需外部 RAG、无需微调、零第三方依赖。**

</div>

---

## 🔥 核心痛点：为什么常规 LLM 总会撞上 *Artificial Hivemind* 之墙？

在写代码和严谨推理任务中，**干净且高度相关的上下文**就是王道。无关信息会分散注意力、拉低准确率。

**但在开放式头脑风暴中，情况恰恰相反。**

当你向 LLM 抛出一个开放难题——即便开启 12 个彼此完全隔离的新会话——模型仍会坍缩回那 3~6 个最安全、最教科书式的陈词滥调（*Artificial Hivemind*，NeurIPS 2025）。强行调高 `temperature` 往往在产生真正概念跃迁之前就先破坏了逻辑连贯性；而多智能体辩论甚至会让结果*更糟*（*Diversity Collapse*，2026）。

> **🧪 来自我们先导实验的「铁证」（`OSS-PR`）：**
> 在解决*「如何阻止开源仓库被 AI 生成的低质灌水 PR（AI-slop PR）淹没」*的隔离实验中，**三个彼此完全独立的会话**（`Direct Baseline 1`、`Direct Baseline 2`，甚至包括一个 `Explicit 热力学` 会话）**竟然各自独立发明了完全相同的示例包名：`pkg@pr-4821` / `pkg@patch-4821`。**
>
> 而在 Sfumato 的 **盲态同构掩码（Blind Isomorphic Masking）** 轨道中，**零个**会话触发 `4821` 或任何基线陈词滥调。

---

## 📈 探索多样性的测试时扩展（实测数据，`K = 1..12`）

我们在一个经典的硬核产品难题——*在不使用聊天监控、罚款或亏损补贴的前提下，阻止双边服务平台买卖双方私下现金跳单*——上运行了 **12 次完全隔离的会话（每种方法共 24 个方案）**，并对底层因果机制进行了严格去重：

<p align="center">
  <img src="./assets/scaling_curve.svg" alt="创造力的测试时扩展：Sfumato 对比 Direct Best-of-N" width="100%" />
</p>

| 指标（`K = 12` 隔离运行，各生成 24 个方案） | Direct Best-of-N | **Sfumato Dual-Track** | 差距 |
|---|---:|---:|---:|
| **发现的独立结构机制数量** | `6 / 24`（`25.0%`） | **`18 / 24`（`75.0%`）** | **3.0×** |
| **第 9–12 轮新增机制数（最后 8 个方案）** | `0` *（彻底平台期）* | **`+5` *（仍在上升）*** | **无平台期** |
| **Track B（盲态）唯一率 / 与基线重合数** | — | **`83.3%` / `0` 次重合** | 零陈词滥调引力 |
| **交叉换序盲评 A/B 裁判（`AB` 与 `BA`）** | `0–2` *（21:24, 20:23）* | **`2–0` 完胜 *（24:21, 23:20）*** | 消除位置偏置 |

> **核心结论：** 靠 **Direct Best-of-N** 盲目多抽几次根本没用——它在 `6` 种机制处就彻底锁死（75% 重复）。**Sfumato 打开了探索多样性的测试时扩展：** 每增加一次尝试，都能探索到正交的新机制簇，不断拓宽非显而易见候选方案的前沿。

---

## 🌍 多难题与跨模型基准测试（多样性 `9 / 9` 全胜）

这套方法在交易平台博弈论之外是否同样有效——例如**情感化 UX 设计**、**开放网络反 AI 爬虫**、**软件架构治理**，以及在 **Claude Opus 5.5** 等其他前沿模型上？

我们在 **等候选预算（Iso-Candidate-Budget：`4 次 Stage-1 隔离求解 × 2 方案 = 每法 8 候选`，交叉换序 `AB`/`BA` 盲评裁判）** 条件下，测试了 **Gemini 4 Neon 上的 7 个公开难题**，并在 **Claude Opus 5.5** 上使用 `--safe-profile claude`（过滤 8 个敏感生物/CBRN/网络战/反间谍领域）进行了 **2 项跨模型复现**，**24 次隔离调用实现 0 次安全拒答**。*（注：两者 Stage 1 候选数相同，Sfumato 另含协调器掩码/回译及 Stage 2a/2b 评审开销，详见下方算力成本表。）*

<p align="center">
  <img src="./assets/multi_problem_benchmark.svg" alt="多难题与跨模型基准测试：多样性 9/9 全胜" width="100%" />
</p>

### 主实验结果（与 `python tools/summarize_benchmarks.py benchmarks/v2 --strict` 100% 一致）

| 公开难题 | 模型 | Direct 独立/8 | Sfumato 独立/8 | 多样性倍率 | 主实验盲评 `AB · BA`（30 分） | 裁定 |
|---|---|---:|---:|---:|---|---|
| **`MKT-DIS`** *（双边平台防跳单）* | Gemini 4 Neon | 3 / 8 | **7 / 8** | **2.33×** | **24:21 · 23:20** | **Sfumato 2–0 胜** |
| **`UX-ONBOARD`** *（空白画布恐惧 · 情感 UX，v2.0）* | Gemini 4 Neon | 4 / 8 | **7 / 8** | **1.75×** | **25:20 · 24:21** | **Sfumato 2–0 胜** |
| **`WEB-SCRAPE`** *（开放网络对抗大规模 AI 爬虫）* | Gemini 4 Neon | 6 / 8 | **7 / 8** | **1.17×** | **22:18 · 20:18** | **Sfumato 2–0 胜** |
| **`OSS-PR`** *（开源项目防 AI 灌水 PR）* | Gemini 4 Neon | 2 / 8 | **5 / 8** | **2.50×** | **21:17 · 18:21** | **平局 1–1** |
| **`AI-ARCH`** *（AI 编程助手导致的架构侵蚀）* | Gemini 4 Neon | 4 / 8 | **7 / 8** | **1.75×** | **23:22.5 · 22.5:24** | **平局 1–1** |
| **`DOC-ROT`** *（组织文档腐烂自愈，v1.2 主实验）* | Gemini 4 Neon | 2 / 8 | **6 / 8** | **3.00×** | 22:24 · 21:24 | Direct 2–0 *（见下表 v2.0 消融）* |
| **`GAME-SNOWBALL`** *（滚雪球与橡皮筋机制，v1.2）* | Gemini 4 Neon | 5 / 8 | **7 / 8** | **1.40×** | 22:23 · 21:23 | Direct 2–0 *（见下表 v2.0 消融）* |
| **`MKT-DIS`** *（跨模型 · `--safe-profile claude`）* | **Claude Opus 5.5** | 4 / 8 | **7 / 8** | **1.75×** | 18:19 · **20:17** | **平局 1–1** *（0 拒答）* |
| **`DOC-ROT`** *（跨模型 · `--safe-profile claude`）* | **Claude Opus 5.5** | 4 / 8 | **7 / 8** | **1.75×** | 20:22 · 20:22 | Direct 2–0 *（无 Anchor · 0 拒答）* |
| **总计（9 轮主实验 · 每法 72 方案）** | **2 模型** | `34 / 72` (`47.2%`) | **`60 / 72` (`83.3%`)** | **1.76×** | **9 Sfumato : 9 Direct** | **9/9 多样性 · 3 胜 3 平 3 负** |

### v2.0 Stage 2b 对等加固消融实验（同时公开正向提升与负向回归）

| 难题 | v1.2 主实验 (`S:D`) | v2.0 对等加固 (`S:D`) | Sfumato 变化 | 裁定与结论 |
|---|---:|---:|---:|---|
| **`DOC-ROT`** | `43 : 48` *（0–2）* | **`46 : 48`** *（23:22 · 23:26）* | **+3** | **平局 1–1** — 精准修复跨领域原石（`thermodynamics_cryogenics`）追平差距 |
| **`GAME-SNOWBALL`** *（v1.2 领域池，强行嫁接）* | `43 : 46` *（0–2）* | `39 : 45` *（20:22 · 19:23）* | **−4** | **Direct 2–0** — 证实强行嫁接极性不匹配的领域反而掉分，绝不覆盖更强的 Direct Anchor |
| **`GAME-SNOWBALL`** *（Pool v2.0：74 领域 / 11 大类）* | `43 : 46` *（0–2）* | **`46 : 39`** *（8/8 独立）* | **+3** | **Sfumato 2–0 胜** — 扩充认知、材料与电网大类后彻底解决极性错配（[日志](./benchmarks/v2/ablations/game_snowball_pool_v2_results.json)） |

### 独立跨模型盲评审计（消除同模型自评偏置）

为排除同模型家族自评偏好，我们使用 **Claude Opus 5.5** 作为独立只读盲评裁判（`AB`/`BA` 换序），对 **Gemini 4 Neon 全部 7 组主实验优胜方案** 进行了复审（[`benchmarks/v2/cross_model_judges/claude_on_gemini.json`](./benchmarks/v2/cross_model_judges/claude_on_gemini.json)）：

- **跨模型裁判结果：** **3 胜（`MKT-DIS` 2–0、`WEB-SCRAPE` 2–0、`AI-ARCH` 2–0）、1 平（`GAME-SNOWBALL` 1–1）、3 负（`UX-ONBOARD`、`OSS-PR`、`DOC-ROT` v1.2）** — **7 Sfumato 对比 7 Direct**（7 题中有 6 题零顺序偏置）。
- **数据诚实证明了什么：**
  - **跨模型稳定优势：** **9 / 9 多样性全胜（K=4 为 `1.76×`，K=12 为 `3.0×`）**，稳定发掘常规直出难以触达的结构性机制，并在 `MKT-DIS` 与 `WEB-SCRAPE` 上同时赢得 Gemini 与 Claude 双裁判 2–0 完胜（`AI-ARCH` 在 Claude 下 2–0 胜）。
  - **诚实的局限（每题 `n=1` 种子）：** 面对强劲的 4 路 Direct Best-of-N，单次 Top-1 胜率接近均势（主实验 `9:9`，跨模型裁判 `7:7`），且 Track B 盲态轨道更偏向零陈词滥调的「破局外卡」而非高频直胜源。因此 **Sfumato v2.1 在 `dual-track` 与 `deep` 模式中均默认内置 Direct Anchor**，锁住不低于基线的下限（`≥ Direct`），同时提供 1.7–3.0× 的探索广度。
- **可复现日志与端到端执行记录：**
  - 本地验证全部 9 轮主实验与 2 组 v2.0 Stage 2b 消融（`v2_ablation_*.json`）：`python tools/summarize_benchmarks.py benchmarks/v2 --strict` *（单独的 Pool v2.0 实验记录见 [`game_snowball_pool_v2_results.json`](./benchmarks/v2/ablations/game_snowball_pool_v2_results.json)）*
  - 结构化基准摘要与裁判依据：[`benchmarks/v2/`](./benchmarks/v2/)
  - Claude Opus 5.5 独立跨模型审计：[`benchmarks/v2/cross_model_judges/claude_on_gemini.json`](./benchmarks/v2/cross_model_judges/claude_on_gemini.json)
  - v2.1 端到端完整执行记录（`sample_domains.py` → `check_leak.py` → 4 路隔离求解摘要 → Stage 2a `PASS/HARDEN/KILL` → Stage 2b 加固）：[`benchmarks/v2/transcripts/alert_fatigue_v2_1_full_transcript.md`](./benchmarks/v2/transcripts/alert_fatigue_v2_1_full_transcript.md)

---

## 🏛️ Sfumato v2.1 工作原理：*领域掩码权衡*

大多数跨领域提示词研究只使用 **显式类比（Explicit Analogy）**，原问题词汇残留导致局部同质化；纯 **盲态重构（Blind Reframing）** 虽能彻底切断陈词滥调引力，却常因回译失真拉低命中率。

**Sfumato v2.1 将 Direct Anchor 与双跨领域轨道完全隔离并行运行，并结合极性感知代码抽样、代码级零泄漏校验与干净上下文红队分诊/选择性加固：**

<p align="center">
  <img src="./assets/architecture_codex.svg" alt="Sfumato v2.1 架构图" width="100%" />
</p>

1. **极性感知分簇代码抽样（`sample_domains.py`）：** 纯 Python 标准库从 **11 大类 74 个高机制密度领域** 中分层抽取，默认隐藏 `mechanisms` 提示防止领域内二次坍缩（可用 `--include-hints` 开启），并通过 `--polarity`（`adversarial | cooperative | physical_loop | human_ux | systems_ops`）确保至少半数领域与问题激励极性契合。Claude Code 下使用 `--safe-profile claude` 保留 **66 个安全领域（11 大类每类恰好 6 个）** 并实现 **0 拒答**。
2. **Direct Anchor *（`dual-track` 与 `deep` 默认内置 · 下限保障）*：** 在匿名候选池中加入 1 路隔离直出方案，保证 `max(Direct, Explicit, Blind) ≥ Direct`。
3. **Track A — 显式类比 *（高命中率）*：** 原问题简报 + 远程领域 → 精准结构迁移。
4. **Track B — 盲态同构掩码 *（最高上限 · 三行结构骨架 + `check_leak.py`）*：**
   - 先提炼 **三行领域中立结构骨架**，改写进目标领域，并 **调用 `scripts/check_leak.py` 进行代码级 0 词泄漏校验** 后再派发子智能体。
   - 隔离求解器仅在远程学科内部求解——**物理隔绝原领域陈词滥调引力。**
   - 仅回译因果机制与权衡，果断淘汰牵强比喻。
5. **Stage 2a/2b — 干净上下文红队分诊（`PASS / HARDEN / KILL`）与选择性加固：**
   - **Stage 2a：** 匿名评估者剔除术语堆砌、逆向选择、女巫/刷单套利和不可行方案，将每个候选明确标为 `PASS`、`HARDEN`（附 1 项可修复弱点）或 `KILL`。
   - **Stage 2b：** 仅对胜出的 Top-1 精准修补其单一运营短板（可选嫁接 1 项来自通过评审的亚军方案的实务原语——绝不强行覆盖更优的 Direct Anchor）。
   - **多语言原生中立模板：** `prompt_templates.md` 与 `domain_pool.json` 采用英文规范并在每个模板注明 `Respond in {USER_LANGUAGE}.`，确保中/英/韩/俄等任意语言用户获得一致母语输出。

---

## ⚡ 对比案例：双边平台防私下跳单（`MKT-DIS`）

> **难题：** 自由职业者、家教、保洁与装修工人在平台完成首单匹配后，为省下 10–20% 抽佣转至私聊现金交易。*禁用老套方案：聊天监控、罚款、普通担保/保险、亏损补贴、0 抽佣。*

| 方法 | 实际产出 | 核心差异 |
|---|---|---|
| **Direct Best-of-N**<br>*(12 轮，24 方案)* | 18 次重复同样的 3 类套路：*T+0 反向托管*、*可转让客户账簿*、*空闲时段补位*。 | 实用度高，但始终困在既有的金融科技/运营套路里。 |
| **Sfumato · 优胜方案**<br>*(寄生虫学 · 有性生殖双重代价)* | **🏆 嵌合任务重组协议** *（Gemini 与 Claude 双裁判均 2–0 胜）* — 将复购抽佣中的 5–7% 转为每 N 次履约一次的 **独立第三方交叉核验槽位**（家教盲测诊断、装修热成像/水平复检、代码资深异步审查）。 | 一对一现金私单 *物理上无法复制* 第三方核验，合谋议价空间消失，且 **主动提议私下交易反而变成「回避质检的柠檬信号」**。 |
| **Sfumato · Track B 盲态**<br>*(监察专员 · 密码学吹哨)* | **零知识廉洁免责公证通道** — 密封报价/交付承诺 + 防报复吹哨缺失证明，为企业/业委会买家提供 **经得起审计的反回扣免责权**。 | 将跳单问题从「省 15% 佣金」重构为「消除机构买家的回扣/职务侵占审计风险」。 |
| **Sfumato · Track B 盲态**<br>*(人类学 · 库拉圈)* | **库拉谱系溯源链** — 仅平台内订单为交付物烙印可验证工匠谱系，放大二手市场价值（房产转售、VC/并购 IP 尽调）。 | 线下私单沦为断代「无名资产」，丧失下游第三方转售溢价。 |
| **Sfumato · 红队拦截案例**<br>*(流体力学 · 文丘里喷射器)* | **文丘里负抽佣吸力器** — 借助紧急 B2B 高溢价（160）调用期权补贴复购单形成 *-3%* 负费率（买家付 90、卖家拿 93）。 | 物理迁移极为巧妙，但 **红队闸门瞬间识破「熟人刷单套利（90→93）」致命漏洞**，拦截了误选。 |

<details>
<summary><strong>📊 查看全部 18 种 Sfumato 独立机制 vs. 6 种 Direct 机制（完整 K = 1..12 日志）</strong></summary>

<br/>

#### Direct Best-of-N（`K = 1..12`，24 方案 → **6 种独立机制**，K=8 即锁死）
1. **可转让客户账簿与继任版税** *（12 轮出现 6 次）*
2. **T+0 反向托管 / 期限转换结算** *（6 次）*
3. **取消空档自动补位与热切换替补** *（6 次）*
4. **锚定老客拉新分红权** *（4 次）*
5. **闲置时段实物折抵抽佣** *（1 次）*
6. **B2B 耗材集采价差与财税凭证通道** *（3 次）*

#### Sfumato Dual-Track（`K = 1..12`，24 方案 → **18 种独立机制**，K=12 仍在上升）
| 轮次 | 轨道 · 远程领域 | 新发现的独立机制 | 累计 |
|---:|---|---|---:|
| 1 | Explicit · `fluid_microfluidics` | ① 文丘里负抽佣期权吸力 · ② 微流控多相层流拆分 | 2 |
| 2 | Blind · `maritime_trade_guilds` | ③ 多边轧差清算账本（Giro） · ④ 拼箱舱单与第三方留置权隔离 | 4 |
| 3 | Explicit · `parasitology_coevolution` | ⑤ **嵌合交叉重组（🏆 2–0 优胜）** · ⑥ 代谢错峰反向托管 | 6 |
| 4 | Blind · `horology_escapement` | ⑦ 差动恒力装置收入/产能平滑枢纽 *（1 项回译损耗淘汰）* | 7 |
| 5 | Explicit · `disaster_triage` | ⑧ 动态复检防需求蔓延护盾 *（1 项重复）* | 8 |
| 6 | Blind · `container_port_logistics` | ⑨ 双向回程零空驶链 · ⑩ 缓冲堆场甩挂异步解耦 | 10 |
| 7 | Explicit · `siege_fortification` | ⑪ 计量工具授权与余料退库仓 *（1 项重复）* | 11 |
| 8 | Blind · `ombudsman_whistleblower` | ⑫ 零知识反回扣免责通道 · ⑬ 阈值匿名分包早期预警托管 | 13 |
| 9 | Explicit · `architectural_wayfinding` | ⑭ 开放中庭实时工序橱窗（CPTED） *（1 项重复）* | 14 |
| 10 | Blind · `electronic_warfare_pls` | ⑮ 全局冲突对齐多方排班复用 *（1 项回译损耗淘汰）* | 15 |
| 11 | Explicit · `mycorrhizal_plant_defense` | ⑯ 三级营养外部保险/放贷方预激信号 *（1 项重复）* | 16 |
| 12 | Blind · `gift_economy_reciprocity` | ⑰ 库拉谱系二级市场溢价认证 · ⑱ 夸富宴/豪三方延迟互惠时间银行 | **18** |

</details>

---

## 🚀 安装与使用（5 个纯文本文件 · 零外部依赖）

Sfumato 运行所需的全部内容都在 [`skill/sfumato/`](./skill/sfumato/) 目录下——仅包含 **5 个可直接审阅的文件**：
- `SKILL.md` — 技能指令、多智能体指南（Claude Code / Antigravity / Codex CLI）与执行流程
- `references/prompt_templates.md` — 语言无关（`{USER_LANGUAGE}`）的 Anchor、Explicit、Blind、Stage 2a 分诊与 Stage 2b 加固模板
- `resources/domain_pool.json` — 11 大类 74 个高机制密度领域池（`66` 个 Claude 安全领域，每类均衡 6 个，含极性亲和标签 `affinities`）
- `scripts/sample_domains.py` — 纯 Python 标准库极性感知分层抽样器（零网络请求、零磁盘写入）
- `scripts/check_leak.py` — Track B 掩码代码级零泄漏校验器（支持英文整词边界及中文/韩文/西里尔子串匹配）

克隆仓库、审阅文件内容后，将 `skill/sfumato` 复制到对应智能体的全局技能目录即可：

```bash
git clone https://github.com/Excelsus4/sfumato.git && cd sfumato

# Claude Code（含自动启用 --safe-profile claude 的 /sfm 与 /sfm-max 快捷指令）
cp -r skill/sfumato ~/.claude/skills/sfumato
cp commands/*.md ~/.claude/commands/

# Antigravity (agy)
cp -r skill/sfumato ~/.gemini/config/skills/sfumato

# Codex CLI
cp -r skill/sfumato ~/.codex/skills/sfumato
```

<details>
<summary>可选本地复制辅助脚本（克隆后支持 <code>--dry-run</code> 预览）</summary>

```bash
# macOS / Linux
bash tools/install.sh --dry-run
bash tools/install.sh --target claude   # 或 agy | codex | all | auto
```

```powershell
# Windows PowerShell
.\tools\install.ps1 -DryRun
.\tools\install.ps1 -Target claude      # 或 agy | codex | all | auto
```

</details>

### 使用方式与算力预算

```text
/sfm 为非对称三阵营 RTS 设计一种非显而易见的机制，解决滚雪球且避免生硬橡皮筋追赶
/sfumato deep 模式：如何在不设付费墙的情况下，抵御开源仓库里的 AI 低质灌水 PR？
/sfm-max 遍历全部 11 大类，为产品设计一条 3 年难以复制的非线性留存护城河
```

| 模式 | Stage 1 求解配置 | 隔离调用总次数 | 预估 Token 开销（对比单次 Direct） | 适用场景 |
|---|---|---:|---:|---|
| `fast` | `3 Explicit`（`--k 3 --mode explicit-only`） | `4 次` *（3 + Stage 2a）* | ~4–5× | Token 预算紧凑时快速获取跨领域方案 |
| `dual-track` *（默认）* | `1 Direct Anchor + 2 Explicit + 1 Blind`（`--k 3`） | `5–6 次` *（4 + Stage 2a + 可选 2b）* | ~6–8× | 日常高上限头脑风暴（与主基准配置一致；锁住 `≥ Direct` 下限） |
| `deep` | `1 Direct Anchor + 3 Explicit + 3 Blind`（`--k 6`） | `8–9 次` *（7 + Stage 2a + 可选 2b）* | ~10–12× | 高难度战略/架构破局，追求最大探索广度 |
| `sweep` *（按需启用）* | `1 Direct Anchor + 11 领域`（`--k 11`，每类 1 个） | `13–14 次` *（12 + Stage 2a + 可选 2b）* | ~15–18× | 单波次覆盖全部 11 个知识大类 |
| `max`（`/sfm-max`，*按需启用*） | **全部 66（Claude）/ 74 领域**（`--all`）+ **1 Direct Anchor** → **两轮锦标赛** | `79–80` / `87–88 次` | ~80–90× | 不计成本的穷尽式核心战略/机制探索 *（运行前强制确认会话数）* |

---

## 📚 研究基础

Sfumato 直接建立在 2025–2026 年四条交汇的 LLM 创造力研究脉络之上：
- **Artificial Hivemind: The Open-Ended Homogeneity of Language Models (and Beyond)** — Liwei Jiang 等，*NeurIPS 2025 D&B*（[arXiv:2510.22954](https://arxiv.org/abs/2510.22954)）：揭示大语言模型在开放式构思中的模型内与跨模型同质化现象。
- **Diversity Collapse in Multi-Agent LLM Systems: Structural Coupling and Collective Failure in Open-Ended Idea Generation** — Nuo Chen 等，2026（[arXiv:2604.18005](https://arxiv.org/abs/2604.18005)）：证明密集辩论与共识拓扑会压垮语义多样性，由此确立 Stage 1 严格**零串扰**并行架构。
- **Unlocking LLM Creativity in Science through Analogical Reasoning** — Andrew Shen, Shaul Druckmann, James Zou，2026（[arXiv:2605.11258](https://arxiv.org/abs/2605.11258)）：证实结构化跨领域类比能显著提升方案多样性与新颖性。
- **Assessing the Effect of Cross-Domain Mapping on Creativity in Humans and Large Language Models** — Qiawen Ella Liu, Marina Dubova, Henry Conklin, Takumi Harada, Thomas L. Griffiths，2026（[arXiv:2603.19087](https://arxiv.org/abs/2603.19087)）：揭示前沿 LLM 在源领域足够遥远且进行结构关系映射时获益最明显。
- **Sfumato 的工程贡献：** 将 *显式类比* 与 *盲态同构掩码* 之间的 **领域掩码权衡** 工程化，并与 **Direct Anchor 下限保障**、**极性感知代码抽样**、**代码级零泄漏校验（`check_leak.py`）** 及 **干净上下文红队分诊/选择性加固** 闭环融合。

---

<div align="center">

<img src="https://upload.wikimedia.org/wikipedia/commons/5/5f/Codex_Atlanticus.jpg" width="460" alt="列奥纳多·达·芬奇 — 大西洋古抄本" />

*“凡心灵未与双手同行之处，便无艺术。” — 列奥纳多·达·芬奇*

<sub>本文档所引用的列奥纳多·达·芬奇画作均来自 Wikimedia Commons 公共领域。</sub>

</div>
