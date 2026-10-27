# 辅助命令与常见问题

[功能与使用指南](FEATURES.zh-CN.md) · [科研记录与实验管理](RECORDS.zh-CN.md) · [首页](../README.zh-CN.md)

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

这些命令生成 SVG 并筛查结构与几何问题。随后用浏览器或图形工具查看实际预览，检查箭头、标签、层次、灰度和最终尺寸。新图建议输出到独立路径，保留正式稿。

真实模型图需结合代码或方法定义，核对训练路径、箭头、跳连、融合、特征语义和图例。复杂图可比较布局；85 mm 单栏若不可读，应重排或采用合适的双栏尺寸。

## 写作前后对照

以下是说明写作方法的**虚构教学示例**。

已给条件：同一测试成员、单seed；F1由0.8020升至0.8130，Recall由0.9010降至0.8920；未做机制干预和跨站点验证。

**修改前**

> All metrics improved, proving that the proposed mechanism is universally robust.

**可支撑的修订**

> In the reported single-seed comparison on the same test samples, F1 increased from 0.8020 to 0.8130, while recall decreased from 0.9010 to 0.8920. These observations indicate a trade-off; they do not establish the proposed mechanism or cross-site robustness.

实际改变：删去“所有指标改善”的错误概括；保留不利Recall；将观察与机制证明分开；限制到单seed和已给样本。语言更流畅不是唯一判据，科学力度准确才是关键。

若Reviewer追问稳定性，现有证据不能写“we have confirmed stability”。可以拟议：

> The current comparison is limited to one seed. We propose matched repetitions with fixed sample membership and a validation-derived threshold to assess stability. These repetitions have not yet been completed.

实际提交前，应按已完成工作更新回复措辞，并核对正文版本与位置。

## 常见问题

**没有激活？** 检查复制的是内部完整Skill、SKILL.md的name为research-craft、目录被当前宿主发现；刷新或重启会话再明确调用。不同位置有同名Skill时先核对，不把两版混用。

**缺少 Python、Node 或渲染工具？** 先用 doctor 查看可用环境。普通解释和写作通常可继续；需要相应工具的操作列为待完成。

**怎样继续改善图稿？** 指出预览中的具体问题，例如层次、留白、特征表达、连接或字体，并附上目标尺寸。明确反馈有助于进行有针对性的修改。

**需要单独购买 API 或部署服务吗？** 使用已有 Codex 环境即可；可用工具、账户额度及数据处理政策由宿主环境决定。

**怎样判断是否更高效？** 观察真实任务中的重复读取、无关输出、调用及返工，同时检查成果是否完整准确。目前没有通用 Token 节省比例。

**如何选择功能？** 查看[功能目录](FEATURES.zh-CN.md)。需要持续记录实验、问题和证据时，请阅读[记录指南](RECORDS.zh-CN.md)。

## 开发者本地检查

```text
python -B -m unittest discover -s tests -v
python -B evals/run_evals.py
python -B demo/run_demo.py
```

tests验证实现与回归，evals验证离线契约；二者不是自主科研能力评分。按变更选择必要检查，不为普通使用反复跑所有测试。说明图的可编辑 SVG 和 PNG 位于同级 images/。
