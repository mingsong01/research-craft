<div align="center">
<img src="docs/images/hero-banner.png" alt="研匠 ResearchCraft：证据驱动的科研分析、模型架构绘图、科技论文写作与审稿返修" width="100%" />

# 研匠 · research-craft

**把科研材料、专业判断、具体修改和最终成果连接起来。**

[English](README.md) · [快速开始](#快速开始) · [模型绘图](#模型架构绘图) · [论文与返修](#论文写作翻译与审稿返修) · [命令与实例](docs/USAGE.zh-CN.md) · [验证范围](PUBLISHING_SNAPSHOT.md)
</div>

`research-craft` 是面向 Codex 的**单一集成式科研 Skill**。科研分析、模型图、论文写作、翻译、审稿回复和上下文效率由同一个入口下的参考文件、脚本和示例提供，不需要分别安装四个 Skill。

当前公开快照：**2026-10-27**；Skill 标识 `research-craft`，版本 **1.3.1-rc.1**，workspace schema **1**。包含此前已完成的绘图、科研写作和上下文增量改进。候选标识不代表通用科研能力已获认证，也不表示这是一个稳定版语义版本发布。

本包可以使用现有 Codex 和已有工具，不要求额外购买模型 API、建立付费评测服务、启动多 Agent 或常驻 MCP。宿主账户和模型服务自身的额度、费用及数据处理条件仍由使用者负责确认。

## 为什么需要它

科研辅助的关键不是生成一段听起来专业的文字，而是回答：数值来自哪一次运行？比较条件是否一致？图上的连接是否对应代码？改文是否改变了原意？回信是否承诺了没有完成的实验？

本 Skill 提供一套轻量方法处理这些问题：先定位必要证据，再完成实际产物，最后核对结果与边界。简单问题直接回答；需要恢复或追溯时才建立记录。

![四类能力：科研分析、模型图、论文返修和上下文效率](docs/images/capability-map.png)

## 核心能力与交付

| 工作 | 实际处理内容 | 典型交付 |
| --- | --- | --- |
| 科研问题与文献 | 明确问题与假设；检索可用的公开原始来源；分析研究缺口和反证 | 有来源的分析、文献比较、尚未解决的问题 |
| 数据和实验 | 核对单位、分母、划分、样本成员、种子、阈值、重复值与非法值；检查比较公平性 | 数据核查、异常解释候选、最小判别实验计划 |
| 科研代码与日志 | 从入口、定义、调用者、配置和失败信息定位行为，不凭类名猜实现 | 具体代码定位、根因证据、必要时经授权实施的小修复 |
| 模型架构图 | 恢复真实数据流、选择架构对应的图形语言、比较布局、生成可编辑矢量并实际渲染 | FigureSpec、SVG、拓扑合同、预览和检查说明 |
| 科技论文 | 诊断章节与段落的科学论证，给出最小且完整的实际改文 | 修订段落、修改依据、保留内容与证据缺口 |
| 学术英文与翻译 | 核查术语、数字、单位、否定、条件、限定词及证据力度 | 忠实译文、自然专业的润色、单列科学修订建议 |
| Reviewer Response | 拆分复合关切，区分已有证据与缺口，规划补实验并同步正文和回信 | 逐条处理表、正文修订、正式回复草稿 |
| 上下文与恢复 | 按需选读、保留源身份及范围、查询有界记录、恢复关键状态 | 可回源摘要、精确片段、必要研究记录 |

## 快速开始

### 1. 取得完整目录

```bash
git clone https://github.com/mingsong01/research-craft.git
cd research-craft
```

仓库根目录用于阅读；其内部的 **research-craft/** 才是完整可安装 Skill。只下载图片或 README 无法得到可用 Skill。

### 2. 安装到一个科研项目

把内部整个目录复制到目标项目，得到：

```text
your-project/
└── .agents/skills/research-craft/
    ├── SKILL.md
    ├── references/
    ├── scripts/
    ├── assets/
    ├── demo/
    ├── tests/
    └── evals/
```

个人目录按当前官方约定为 `$HOME/.agents/skills/research-craft/`。已有同名安装时先备份和核对，不直接覆盖；某些旧环境使用 `.codex/skills`，请以宿主实际发现位置为准。[官方 Skills 目录说明](https://learn.chatgpt.com/docs/build-skills)

Windows PowerShell 可在下载的仓库根目录执行：

```powershell
$skillSource = (Resolve-Path '.\research-craft').Path
$skillTarget = Join-Path $HOME '.agents\skills\research-craft'
if (Test-Path -LiteralPath $skillTarget) {
    throw '目标已存在，请先核对或备份，避免覆盖。'
}
New-Item -ItemType Directory -Force (Split-Path $skillTarget) | Out-Null
Copy-Item -LiteralPath $skillSource -Destination $skillTarget -Recurse
```

Linux/macOS：

```bash
mkdir -p "$HOME/.agents/skills"
test ! -e "$HOME/.agents/skills/research-craft" && \
  cp -R ./research-craft "$HOME/.agents/skills/research-craft"
```

重新打开会话或刷新 Skill 发现后，可以用 `$research-craft` 或自然语言明确调用。本项目不会自动全局安装、购买服务或更改账户设置。

### 3. 从具体材料开始

```text
请使用 research-craft 分析这份训练日志和指标 CSV。
先核对 split、seed、checkpoint 和指标定义，保留下降指标与实际失败。
只分析，不修改代码，也不要执行训练。
```

```text
请根据这份模型的真实 forward 绘制可编辑架构图。
先恢复分支、跳连、融合与训练专用路径，未知维度不要补造。
比较两种有实质差异的布局，生成 SVG 并检查 180 mm 最终尺寸。
```

```text
请修改这段 Introduction：检查研究缺口、方法动机和贡献之间的递进关系。
给出实际英文修订稿与具体理由，不增加新实验、引用或优先权；正确内容请保留。
```

```text
请逐条分析这份 Reviewer Comment，保留完整原文。
列出现有证据、必要补证、正文改文与正式回复；未完成实验只能写成计划。
```

## 工作方式：足够严谨，保持轻量

![任务范围、证据定位、产出、核验和交付](docs/images/workflow-overview.png)

- **QUICK**：一次性问题或局部任务，默认不创建研究记录。
- **TRACKED**：需要恢复的排查或多阶段工作，维护少量状态、问题与进展。
- **FORMAL**：重要实验、基准比较、论文主张或返修，保留相应计划和证据链接；不意味着可以自动训练或投稿。

只有明确需要追踪时才初始化 `.research/`。它首先创建 config、STATE 与 dashboard；registry、实验详情及写作表按需生成。registry 和 manifest 是事实记录来源，dashboard 是生成视图。记录一个实验计划不等于该实验已经运行，也不等于外部平台正式预注册。

分析中保留七种判断标签：`FACT`、`DERIVED`、`INTERPRETATION`、`HYPOTHESIS`、`PROPOSAL`、`DECISION`、`UNKNOWN`。比如指标下降是观察、同口径差值是计算、某模块导致下降则是尚需排除混杂的解释。

## 模型架构绘图

![真实结构、拓扑合同、两种构图、矢量源、渲染复核和最终尺寸](docs/images/diagram-pipeline.png)

结构证据优先于外观。绘图前读取真实计算路径或充分的方法说明，整理输入、阶段、分支、融合、输出、残差和辅助损失；检查有向边、形状、执行条件与未知项。不能为了对称或美观增删节点、反转箭头、编造特征尺寸。

不同结构采用不同图形语言：Encoder–Decoder 强调尺度与同层跳连；Transformer 强调token、Q/K/V和残差；SSM强调有时间条件的递推、门控与状态；多模态强调模态来源、对齐和跨模态交互。三维特征体只在有助于说明特征语义时使用，不把所有模型画成同一种流程图。

复杂图先比较两个实质布局，再定稿。核验相互独立：**科学拓扑、信息表达、视觉设计、投稿尺寸、可编辑性**。SVG检查可发现结构和几何缺陷，但不能认证美观；必须查看实际导出，关注箭头、遮挡、图例、字体、灰度与缩小后的可读性。

### 已有实际图稿

下列为本项目公开的**合成架构示例**，不是某个真实训练模型的代码一致性或顶刊级能力认证。图稿由仓库内实际源文件渲染，源与合同可直接查看。

![合成跨模态模型图实际渲染](docs/images/example-multimodal.png)

[跨模态 SVG](demo/publication/multimodal-A/architecture.svg) · [FigureSpec](demo/publication/multimodal-A/figure-spec.json) · [拓扑合同](demo/publication/multimodal-A/topology.json)

![合成多尺度 Encoder–Decoder 实际渲染](docs/images/example-multiscale.png)

[多尺度 SVG](demo/publication/unet-multiscale/architecture.svg) · [FigureSpec](demo/publication/unet-multiscale/figure-spec.json) · [拓扑合同](demo/publication/unet-multiscale/topology.json)

两个布局按180 mm双栏检查；直接缩至85 mm并不保证可读。已有Bybit warning仍须查看及说明，不能关闭规则来换PASS。真实模型使用时还要对照实际代码；原生编辑器往返、跨平台字体和实际打印也不能由静态检查代替。

## 论文写作、翻译与审稿返修

![原始材料、诊断、最小修改、证据核对及实际输出](docs/images/writing-pipeline.png)

支持 Abstract、Introduction、Related Work、Method、Experiments、Results、Discussion、Limitations 和 Conclusion 的问题诊断。按具体章节/段落功能定位缺陷，不强制固定段数或万能句式。

- **动机与贡献**：已有工作到底解决了什么？缺口是否有来源？该设计怎样响应缺口？结果足以支持何种贡献范围？
- **Method**：总体框架、模块作用、符号、公式条件、图文码是否一致？抽取器漏掉数学对象时要回原件核对。
- **结果与讨论**：区分数据观察、解释、机制、竞争解释与局限；同时改善的指标与下降指标都要保留。
- **最小改文**：交付完整修订段落，说明具体修复和证据，不用建议清单替代用户要求的实际稿件；好的内容可以不改。
- **英文与翻译**：保留数字、有效位、单位、否定、条件、限定词和证据力度。发现科学错误时单列修订建议，不悄悄改变“忠实翻译”。
- **导师经验**：把指导转化为有条件的判断方法，不把身份未确认转写当逐字原话，也不把一次返修的列顺序或附录策略当普遍规范。

返修链路为：**完整评论 → 核心关切 → 技术要求 → 已有证据 → 缺口 → 最小必要补证 → 正文修订 → 正式回信 → 版本一致性核查**。缺数据、未做实验或无法完成的要求如实保留为partial/unresolved，不虚构“全部解决”、页码或新增结果。

[专项写作方法](references/scientific-writing.md) · [导师与返修判断](references/reviewer-revision.md) · [实际使用与合成前后示例](docs/USAGE.zh-CN.md)

## 上下文效率：减少冗余，保持可回源

![HOT/WARM/COLD以及原始证据回取](docs/images/context-efficiency.png)

已有机制包括按任务选读、HOT/WARM/COLD、末N条有界registry查询、流式CSV统计、同流SHA及精确行范围回取。它们避免反复全文读取和堆积无用输出，不要求压短所有科研回答。

摘要要能回到原文件/版本与具体行、页或记录。指标有效位、单位、split/成员、公式成立条件、完整审稿意见、导师否定/限制、不利结果与失败不能不可逆丢失。CSV的均值/极值也不能证明分组可比或成员一致。

目前不宣称“节省75% Token”：工具视图字节缩减不是实际模型input/output或总成本下降。是否省下无效工作，应结合真实任务的读取、调用、输出、返工和成果检查记录判断。

## 环境和文件

| 需要 | 说明 |
| --- | --- |
| Codex | 已有可正常使用的账户与工具权限；不依赖单独付费API |
| Python | 辅助脚本使用标准库；文档兼容目标3.9+，本快照本地使用实际版本见验证记录 |
| Node.js | SVG/Bybit相关流程使用；维护渲染建议22+，本机现有24 |
| 浏览器/PDF工具 | 实际渲染时使用已有Edge/Chromium等；缺失时报告未完成，不自动安装 |
| Git/Web/GPU | 按任务需要；普通研究记录不需要GPU、Docker、插件或MCP |

`SKILL.md`只保留入口和必要约束，`references/`按需读，`scripts/`是确定性工具，`assets/`保留模板和资源，`demo/`提供合成源与产物，`tests/`与`evals/`提供工程测试及离线契约。它们共同组成一个完整Skill，不是需要部署的服务。

## 验证范围与边界

当前已有110项工程测试、60项离线契约通过记录；本次公开包还会从新ZIP解压复跑这些检查。请查看[本快照验证说明](PUBLISHING_SNAPSHOT.md)及公开构建结果。旧模型评测摘要只属于其冻结历史版本，不迁移成当前源的新认证。

代码成功、英文流畅和SVG PASS都不能替代科研判断。当前仍有有限合成架构范围、85mm适配、真实模型一致性、独立审美/写作评价、部分指导归因及跨平台渲染未覆盖。没有承诺自动复现任意论文、普遍顶刊图稿、导师级指导或投稿接受率提升。

## 安全、许可和贡献

记录及脚本本地优先，不代表模型离线推理。未公开论文、审稿通讯、数据和凭证仍须按宿主模型服务边界处理。不要把本地研究状态、私人材料、原始模型日志或封存答案提交到公共仓库/Issue。

本次公开内容为通用Skill、原创说明图、合成示例、脚本、工程测试与已保留的第三方来源。**原创部分许可证仍由作者暂缓选择**，不因为公开可见或部分依赖使用MIT就把整个项目标成MIT/开源许可。[许可状态](LICENSE_STATUS.md) · [第三方来源与许可证](THIRD_PARTY_NOTICES.md)

欢迎提交脱敏、可公开的最小复现：预期与实际行为、命令/版本、必要证据、实际图稿或改文差异。请先界定具体缺陷，避免无目标重画、全文重写或不必要工具堆叠。此仓库不自动购买服务、运行训练、上传论文或执行付费模型评测。
