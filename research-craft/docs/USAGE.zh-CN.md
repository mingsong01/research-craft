# 实际使用、命令与故障处理

下列CLI命令均在**可安装Skill目录**执行；若当前位于仓库根目录，先 `cd research-craft`。普通科研使用不必记命令，直接告诉Codex材料、限制和交付目标即可。

## 哪些材料有用

| 任务 | 最有用的输入 | 需要的交付 |
| --- | --- | --- |
| 异常指标 | 原始CSV、指标定义、split/seed、配置、checkpoint、完整相关错误 | 核查结果、可比性、候选解释与下一项判别检查 |
| 模型图 | 实际forward、模块实现、已知张量形状、方法定义、目标尺寸 | 拓扑合同、候选布局、编辑源、实际渲染与检查 |
| 改论文 | 原段落、上下文、技术事实/表格、版本与写作范围 | 完整改文、具体理由、来源核对与保留限制 |
| 翻译 | 完整原文、术语、公式及其条件、是否仅语言处理 | 忠实译文和语义核对；科学疑点单列 |
| 回复审稿 | 完整评论、现有证据、实际正文、已做/拟做工作清单 | 逐条关切、缺口、补证、正文与正式回信 |

材料不足时，标明未知即可；不要要求模型补造结果或根据示意图猜真实尺寸。

## 只读工具

```text
python scripts/research.py --root <project> doctor
python scripts/research.py --root <project> fingerprint data/metrics.csv
python scripts/research.py --root <project> summarize-csv data/metrics.csv --columns score --key run --evidence
python scripts/research.py --root <project> read-slice notes/source.txt --range 12:28 --range 46:51
python scripts/research.py --root <project> read-slice notes/source.txt --range 12:28 --expect-sha256 <prior-sha256>
```

- doctor只报告可用工具/状态，不初始化、不探测网络。
- fingerprint给路径、字节数、修改时间和SHA；hash不是内容正确性或实验真实性证明。
- summarize-csv默认流式计算；--key核对缺键/重复；--evidence增加同流hash、原始极值字符串、记录/物理行和非法值诊断。
- 非有限/非数字示例只保留前3项，exhaustive会说明是否完整；不能把示例数量当全部异常数量。极值并列也不能只核查首次出现的那行。
- 默认聚合使用浮点，不是精确十进制算术；作科学主张时回到原字符串、单位和具体记录。整体均值不能代替分组配对。
- read-slice只支持本地UTF-8文本；1-based闭区间，不接受重叠/越EOF范围；保留原换行，BOM从解码文本去除但原字节仍计入SHA。不是PDF/Word公式解析器。
- hash与旧版不同会拒绝复用；对活跃写入文件应先冻结稳定版本。全文件hash扫描有I/O成本，简单问题不必强制使用。

## 必要时启用追踪

```text
python scripts/research.py --root <project> init --preset standard
python scripts/research.py --root <project> issue add --title "Metric definition mismatch" --summary "Check split and threshold" --next-action "Compare source rows"
python scripts/research.py --root <project> list issues --limit 10
python scripts/research.py --root <project> audit
```

init仅在需要追踪的任务运行。minimal/standard/strict调整记录默认值，不授予工具执行权限；list limit必须正数，0不代表无限。audit检查记录/链接结构，不验证实验科学结论。

写作映射按需通过 writing add 创建；不要手改CSV破坏ID或链接。状态保存当前问题和下一步，不复制全部聊天。恢复先读状态、活动条目与必要详情；版本变化应回源，不能信旧摘要。

## 绘制并检查一个现成合成示例

```text
python scripts/vendor/figure-spec/figure_renderer.py render demo/publication/unet-multiscale/figure-spec.json --output output/multiscale.svg
python scripts/diagram_svg_qa.py lint output/multiscale.svg --spec demo/publication/unet-multiscale/topology.json --width-mm 180 --json
node scripts/bybit_svg_profile.mjs output/multiscale.svg
```

这些命令生成矢量并作确定性筛查，不等于已经看过实际PNG/PDF或达到美学要求。输出文件请使用新路径；已有同名产物先核对，避免覆盖正式稿。

真实图需要额外提供真实结构证据，检查训练专用线型、箭头落点、跳连、融合符号、tensor/token语义、图例和最终字号。复杂图比较两个实质布局；若85mm缩放不可读，改为合理的单栏重排或使用双栏，不直接宣布通过。

## 一个合成写作前后对照

下面数字只为说明判断方法，**不是研究结果，也不来自私有论文或封存评测题**。

已给条件：同一测试成员、单seed；F1由0.8020升至0.8130，Recall由0.9010降至0.8920；未做机制干预和跨站点验证。

**修改前**

> All metrics improved, proving that the proposed mechanism is universally robust.

**可支撑的修订**

> In the reported single-seed comparison on the same test samples, F1 increased from 0.8020 to 0.8130, while recall decreased from 0.9010 to 0.8920. These observations indicate a trade-off; they do not establish the proposed mechanism or cross-site robustness.

实际改变：删去“所有指标改善”的错误概括；保留不利Recall；将观察与机制证明分开；限制到单seed和已给样本。语言更流畅不是唯一判据，科学力度准确才是关键。

若Reviewer追问稳定性，现有证据不能写“we have confirmed stability”。可以拟议：

> The current comparison is limited to one seed. We propose matched repetitions with fixed sample membership and a validation-derived threshold to assess stability. These repetitions have not yet been completed.

这是**计划型草稿**，不是已完成返修正文；实际提交时必须按真正已做工作、正文版本和位置改写。

## 常见问题

**没有激活？** 检查复制的是内部完整Skill、SKILL.md的name为research-craft、目录被当前宿主发现；刷新或重启会话再明确调用。不同位置有同名Skill时先核对，不把两版混用。

**缺Python/Node/渲染工具？** 先doctor。普通解释仍可处理；需要工具的操作标未完成。不要自动为简单任务安装整套环境，更不能把未运行检查写成通过。

**图不够漂亮？** 查看实际渲染中的具体问题：层级、留白、特征表达、创新模块、连接、字体或信息密度。针对缺陷局部改，不靠重复渐变/阴影或无目标再生成。

**是否必须建立隔离/付费评测系统？** 不需要。用现有环境完成真实科研任务，做必要本地检查和人工前后对照即可；这不意味着可以把共享环境称作保密隔离或独立A/B。

**是否减少75% Token？** 没有此结论。输出bytes、实际模型usage、时间和返工分别讨论；不要把更短的回答当科学质量提升。

**能替研究者背书论文吗？** 不能。作者负责来源、方法、数据、学术规范和投稿。Skill辅助分析和制作，不认证真实实验、导师身份、审稿通过或期刊接受。

## 本地维护检查

```text
python -B -m unittest discover -s tests -v
python -B evals/run_evals.py
python -B demo/run_demo.py
```

tests验证实现与回归，evals验证离线契约；二者不是自主科研能力评分。按变更选择必要检查，不为普通使用反复跑所有测试。公开图文的SVG源和PNG见同级images/；六张说明图是原创工作流示意，没有真实实验曲线。
