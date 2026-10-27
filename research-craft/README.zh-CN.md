<div align="center">
<img src="docs/images/hero-banner.png" alt="研匠 ResearchCraft：科研分析、模型架构绘图、科技论文写作与审稿返修" width="100%" />

# 研匠 · ResearchCraft

**让科研分析有依据，让实验有记录，让图稿和论文表达更清楚。**

[English](README.md) · [安装与开始使用](#安装与开始使用) · [功能与使用指南](docs/FEATURES.zh-CN.md) · [科研记录与实验管理](docs/RECORDS.zh-CN.md) · [命令参考](docs/USAGE.zh-CN.md)
</div>

`research-craft` 是面向 Codex 的科研 Skill，支持资料阅读、代码与实验分析、科研记录、模型架构绘图、论文写作、学术翻译和审稿回复。它帮助你定位原始依据、完成具体分析或修改，并保留结果与来源之间的联系。

**安装一个 Skill，按任务调用不同能力。** 下表中的功能共用 `research-craft` 入口，无需分别安装。可以直接描述研究问题，也可以用 `$research-craft` 明确调用。

版本：**1.3.1-rc.1**（候选版） · 研究工作区格式：**schema 1**

![ResearchCraft 能力地图](docs/images/capability-map.png)

## 功能与使用入口

选择最接近当前需求的一项。每个指南都说明适用场景、所需材料、可复制指令和预期结果。

| 功能 | 可以帮你做什么 | 所需材料 | 使用入口 |
| --- | --- | --- | --- |
| 研究问题与文献 | 比较方法、分析研究缺口、定位原始来源 | 研究问题、论文或检索范围 | [文献与研究定位](docs/FEATURES.zh-CN.md#01-研究问题与文献) |
| 科研代码与日志 | 追踪执行路径、定位错误和版本差异 | 代码入口、配置、日志、运行方式 | [代码与日志](docs/FEATURES.zh-CN.md#02-科研代码与日志) |
| 实验数据核查 | 检查指标口径、异常值、划分与可比性 | 原始数据、指标定义、实验配置 | [数据与指标](docs/FEATURES.zh-CN.md#03-实验数据与指标) |
| 实验设计 | 选择控制变量、消融和补充实验 | 假设、已有结果、资源限制 | [设计与补充实验](docs/FEATURES.zh-CN.md#04-实验设计与补充实验) |
| 科研记录与实验管理 | 关联问题、实验、证据、决策与修改，查询并恢复工作 | 项目目录、计划、实际运行及结果 | [记录功能完整指南](docs/RECORDS.zh-CN.md) |
| 模型架构绘图 | 整理拓扑、比较布局、制作可编辑矢量图 | 模型代码或方法定义、目标尺寸 | [模型图怎么画](docs/FEATURES.zh-CN.md#05-模型架构绘图) |
| 科技论文写作 | 诊断章节逻辑、修改段落与贡献表述 | 原文、上下文、方法与结果依据 | [论文诊断与修改](docs/FEATURES.zh-CN.md#06-科技论文写作) |
| 学术英文与翻译 | 中英互译、润色、术语与语义核对 | 完整原文、术语表、处理范围 | [翻译与润色](docs/FEATURES.zh-CN.md#07-学术英文与中英翻译) |
| 审稿返修 | 拆解关切、规划补证、同步正文与回信 | 完整评论、论文、已做与待做工作 | [Reviewer Response](docs/FEATURES.zh-CN.md#08-审稿意见与正式回复) |
| 科研指导讨论 | 将指导意见落实为具体修订与行动 | 指导记录、对应原文、研究限制 | [理解指导意见](docs/FEATURES.zh-CN.md#09-科研指导意见) |
| 多步骤任务与恢复 | 保存关键状态、继续中断的科研任务 | 当前目标、文件或已有研究记录 | [恢复工作](docs/FEATURES.zh-CN.md#10-多步骤任务与上下文恢复) |

## 安装与开始使用

### 1. 下载

```bash
git clone https://github.com/mingsong01/research-craft.git
cd research-craft
```

也可以在 GitHub 点击 **Code → Download ZIP**。仓库根目录用于阅读，内部的 **research-craft/** 是完整可安装 Skill。

### 2. 安装

将内部完整目录复制到下列位置之一：

| 范围 | 目标目录 |
| --- | --- |
| 单个研究项目 | `<your-project>/.agents/skills/research-craft/` |
| 当前用户的多个项目 | `$HOME/.agents/skills/research-craft/` |

目标目录中应保留 `SKILL.md` 及同级 `references/`、`scripts/`、`assets/` 等文件。已有同名安装时，请先备份或比较版本。部分旧环境使用 `.codex/skills`，以宿主实际支持的目录为准。[Codex Skills 目录说明](https://learn.chatgpt.com/docs/build-skills)

Windows PowerShell，个人安装示例，在下载的仓库根目录执行：

```powershell
$skillSource = (Resolve-Path '.\research-craft').Path
$skillTarget = Join-Path $HOME '.agents\skills\research-craft'
if (Test-Path -LiteralPath $skillTarget) {
    throw '目标已存在，请先核对或备份。'
}
New-Item -ItemType Directory -Force (Split-Path $skillTarget) | Out-Null
Copy-Item -LiteralPath $skillSource -Destination $skillTarget -Recurse
```

Linux/macOS，个人安装示例：

```bash
mkdir -p "$HOME/.agents/skills"
test ! -e "$HOME/.agents/skills/research-craft" && \
  cp -R ./research-craft "$HOME/.agents/skills/research-craft"
```

完成复制后，重新打开会话或刷新 Skill 列表。

### 3. 在 Codex 对话中提出任务

下面是**对话指令，不是终端命令**。将示例路径替换为工作区中的实际文件，或附上相应材料。

```text
请使用 $research-craft 分析 logs/train.log 和 results/metrics.csv。
解释新模型为何 F1 上升而 Recall 下降，先核对划分、阈值与配置。
请给出有来源的分析和下一步建议，本次不改代码或运行训练。
```

```text
请使用 $research-craft 为当前项目建立实验记录。
记录问题、假设、对照条件、指标、配置与结果位置。
将本次实验关联到问题和证据，更新当前状态，并生成便于查看的看板。
```

```text
请使用 $research-craft 根据 models/network.py 的 forward 绘制论文模型图。
目标是双栏 180 mm，保留可编辑 SVG。先整理结构并比较两种布局，
再提供图稿、实际预览，以及仍需要补充确认的结构信息。
```

```text
请使用 $research-craft 修改 manuscript/introduction.md。
结合 method.md 和 results.csv，检查研究缺口、动机与贡献的关系。
请给出完整英文修订稿、主要修改理由和仍需补充的依据。
```

[查看全部功能的调用方式](docs/FEATURES.zh-CN.md) · [了解实验记录的完整流程](docs/RECORDS.zh-CN.md)

## 科研记录与实验管理

ResearchCraft 可以在研究项目的 `.research/` 中保存结构化记录，让“为什么做、做了什么、结果在哪里、据此决定什么”形成可追踪的联系。

![科研记录与实验管理](docs/images/research-records.png)

| 记录 | 主要内容 |
| --- | --- |
| 问题 | 现象、状态、根因、关联实验与下一步 |
| 实验 | 问题与假设、对照变量、配置、状态、指标、结果和局限 |
| 证据 | 主张、来源、支持状态、适用范围与限制 |
| 决策 | 比较的选项、选择理由、依据和取舍 |
| 变更 | 修改的文件、原因、关联问题与验证结果 |
| 日志 | 简明时间线与关联记录 |
| 文献与写作 | 文献条目、检索记录、审稿处理、图表和论文章节映射 |
| 当前状态与看板 | 活动问题、实验、阻塞项、下一步及汇总视图 |

实验结果为失败或没有改善时，同样可以保留记录。数据、checkpoint 和原始日志通常留在原位置，通过路径和文件哈希关联，避免把大文件反复复制进记录。

[记录类型、目录与查询方式](docs/RECORDS.zh-CN.md) · [实验从计划到结果的操作示例](docs/RECORDS.zh-CN.md#实验从计划到结果)

## 工作方式

![从科研问题到可追溯成果](docs/images/workflow-overview.png)

ResearchCraft 先明确问题和材料，再定位证据、完成分析或制作，最后检查结果。记录详细程度按任务选择：**QUICK** 适合单次问题，通常直接给结果；**TRACKED** 保存持续工作的状态；**FORMAL** 为重要实验、论文主张和返修关联更完整的计划与证据。

研究记录按需创建。计划、已执行工作、观察与解释分别呈现，便于接续和复核。

## 模型架构绘图

![模型图的设计与制作流程](docs/images/diagram-pipeline.png)

绘图从真实计算路径或充分的方法定义开始，整理输入输出、模块、分支、融合、已知形状和运行条件，再选择视觉表达。

- **CNN / Encoder–Decoder**：突出特征尺度、层次和对应跳连。
- **Transformer**：突出 token、注意力角色、残差与模块层级。
- **Mamba / SSM**：突出状态、递推方向、门控与序列关系。
- **多尺度 / 多模态**：区分尺度或模态来源，表达对齐、交互和融合位置。

复杂图先比较布局，再细化。拓扑、信息表达、视觉质量、最终物理尺寸和可编辑性分别检查，实际预览用于复核箭头、标签、字体、灰度和留白。

### 图稿示例与源文件

以下**合成架构示例**展示特征符号、层次和连线表达，附带可编辑源与拓扑定义。

![跨模态合成架构示例](docs/images/example-multimodal.png)

[跨模态 SVG](demo/publication/multimodal-A/architecture.svg) · [FigureSpec](demo/publication/multimodal-A/figure-spec.json) · [拓扑定义](demo/publication/multimodal-A/topology.json)

![多尺度 Encoder–Decoder 合成架构示例](docs/images/example-multiscale.png)

[多尺度 SVG](demo/publication/unet-multiscale/architecture.svg) · [FigureSpec](demo/publication/unet-multiscale/figure-spec.json) · [拓扑定义](demo/publication/unet-multiscale/topology.json)

示例按 180 mm 布局，85 mm 单栏需要重新检查或排版。真实模型需对照其代码确认连接和维度。[使用方法](docs/FEATURES.zh-CN.md#05-模型架构绘图) · [兼容性与已知限制](PUBLISHING_SNAPSHOT.md)

## 论文写作、翻译与审稿回复

![从材料到论文修订和正式回复](docs/images/writing-pipeline.png)

方法覆盖 Abstract、Introduction、Related Work、Method、Experiments、Results、Discussion、Limitations 和 Conclusion。根据章节功能诊断问题，例如动机与设计脱节、贡献超出证据、公式条件不清、讨论遗漏下降指标。

修改给出完整段落和关键理由，检查术语、数值、公式条件及结论范围。语言润色与科学内容修订分别说明。审稿工作按“评论—关切—证据—补充工作—正文修改—回复”组织，已完成、拟开展和未解决的内容分别呈现。

[论文写作](docs/FEATURES.zh-CN.md#06-科技论文写作) · [翻译与润色](docs/FEATURES.zh-CN.md#07-学术英文与中英翻译) · [审稿回复](docs/FEATURES.zh-CN.md#08-审稿意见与正式回复) · [改文前后对照](docs/USAGE.zh-CN.md#写作前后对照)

## 上下文与长任务

![按需读取与证据回源](docs/images/context-efficiency.png)

按当前任务选读参考材料，用有界查询和流式统计处理记录与 CSV，保留原文件身份及精确位置。需要细节时，可回到相应版本、行、页或记录。这样有助于减少重复读取和无关输出，同时保留指标精度、公式条件、完整评论和不利结果。

实际效率取决于任务与宿主环境，目前没有经验证的通用 Token 节省比例。

## 环境与目录

| 组件 | 用途 |
| --- | --- |
| Codex | 运行 Skill，遵循账户额度、工具权限和数据设置 |
| Python | 记录、数据和测试脚本使用标准库；文档兼容目标为 3.9+ |
| Node.js | 部分 SVG 检查；可选 Chromium 导出流程建议 22+ |
| 浏览器或 PDF 工具 | 按任务实际渲染和查看图稿 |

普通阅读、记录和写作无需部署单独服务。`SKILL.md` 是入口；`references/` 是科研方法；`scripts/` 是辅助工具；`assets/` 是模板资源；`demo/` 是示例；`tests/` 和 `evals/` 是工程与离线契约检查。

## 质量、隐私与许可

本地工程检查包括 **110 项测试、60 项离线契约**及新 ZIP 解压运行。它们验证实现与约定，科研成果仍需结合原始证据和人工判断。[检查说明](RELEASE_CHECKS.md) · [兼容性与已知限制](PUBLISHING_SNAPSHOT.md)

研究记录保存在本地，对话和工具输出仍按宿主模型服务的数据政策处理。处理未公开论文、数据或审稿通信前，请确认相应权限；提交 Issue 时使用脱敏材料。[数据处理](SECURITY.md)

原创部分尚未指定项目级许可证；第三方组件保留各自许可和署名。使用与再分发前请阅读[许可说明](LICENSE_STATUS.md)与[第三方来源](THIRD_PARTY_NOTICES.md)。

欢迎反馈实际使用问题。附上任务、脱敏输入、预期与实际结果，有助于复现和改进。
