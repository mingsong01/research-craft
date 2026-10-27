# 科研记录与实验管理

ResearchCraft 可以把科研过程中的问题、实验、证据、决策和修改关联起来。适合实验多、改稿周期长、需要复查结果来源或跨会话继续的项目。

[首页](../README.zh-CN.md) · [功能指南](FEATURES.zh-CN.md) · [English](RECORDS.en.md) · [辅助命令](USAGE.zh-CN.md)

![科研记录之间的关系与持续工作视图](images/research-records.png)

## 可以记录什么

| 类型 | 保存的信息 | 典型用途 |
| --- | --- | --- |
| 问题 `issues` | 现象、状态、根因、关联实验、下一步 | 追踪指标异常、代码问题或审稿关切 |
| 实验 `experiments` | 问题、类型、状态、关键变量、结果及关联证据 | 比较实验和保留失败过程 |
| 实验详情 `manifest.yaml` | 假设、对照、控制变量、数据/划分/seed、环境、代码版本、命令、指标、结果、局限 | 复查一项实验到底怎么做、能支持什么 |
| 证据 `evidence` | 主张、来源、支持状态、范围和限制 | 区分充分支持、部分支持、矛盾与未知 |
| 决策 `decisions` | 问题、选择、理由、依据、取舍 | 解释为何采用某个配置、分析或修订方案 |
| 变更 `changes` | 修改文件、原因、关联问题/决策、验证结果 | 跟踪代码与论文修改 |
| 时间日志 `journal` | 时间、类型、关联 ID、简要进展 | 查看主要工作时间线 |
| 写作映射 `writing` | 文献、检索、审稿、图表与论文修改的对应关系 | 核查论点、实验、正文和回复是否衔接 |
| 当前状态 `STATE.yaml` | 当前问题、活动实验/假设、阶段、阻塞、下一步 | 下次工作时快速接续 |
| 看板 `DASHBOARD.md` | 从记录生成的当前概览 | 方便阅读项目状态 |

假设保存在实验详情和当前活动状态中。看板是生成视图，CSV 记录和实验详情才是持久信息来源。

## 最简单的使用方式

在研究项目中打开 Codex，输入：

```text
请使用 $research-craft 为这个项目建立必要的科研记录。
当前问题是：新模型的 Recall 下降，原因尚不清楚。
请记录现象与已有证据，建立阈值排查实验计划，关联问题、实验和结果文件。
本次不运行实验；结束时更新当前状态、下一步和看板。
```

已有实验结果时，可以这样继续：

```text
请使用 $research-craft 更新实验记录。
本次运行命令和环境见 logs/run.txt，结果在 results/run-03.csv。
核对数据划分、seed、配置与指标，把实际结果、下降指标和限制写入对应实验。
将可支撑的主张关联为证据，记录采用方案的理由，并更新下一步。
```

只需解释一个问题时通常不用建工作区。需要记录时可采用 `standard`；`minimal` 默认更轻，`strict` 默认更详细。预设控制记录方式，工具操作权限仍遵循宿主和任务要求。

## 记录放在哪里

以下是按需积累后的目录示意，初次初始化只创建配置、状态和看板。

```text
your-project/
├── .research/
│   ├── config.yaml
│   ├── STATE.yaml
│   ├── DASHBOARD.md
│   ├── registry/
│   │   ├── issues.csv
│   │   ├── experiments.csv
│   │   ├── evidence.csv
│   │   ├── decisions.csv
│   │   ├── changes.csv
│   │   └── journal.csv
│   ├── experiments/<EXP-ID>/manifest.yaml
│   ├── writing/
│   │   ├── literature.csv
│   │   ├── literature_search.csv
│   │   ├── reviewer_map.csv
│   │   ├── figure_table.csv
│   │   └── paper_changes.csv
│   └── notes/
└── results/  logs/  data/  manuscript/
```

原始数据、日志和 checkpoint 可以留在现有目录，通过路径或 `fingerprint` 的 SHA-256 标识关联。实验产物应在实际生成后再保存相应文件。

## 实验从计划到结果

自然语言调用最方便。下面也提供手动操作方式：在安装的 Skill 目录中运行 PowerShell，将 `<your-project>` 替换为实际项目路径。

### 1. 初始化并登记问题

```powershell
$projectRoot = '<your-project>'
python scripts/research.py --root $projectRoot init --preset standard
$issueId = python scripts/research.py --root $projectRoot issue add --title 'Recall decrease' --summary 'Check threshold comparability' --next-action 'Compare threshold settings'
```

问题获得 `ISS-日期-序号` 形式的 ID。其他主要记录也有独立 ID，便于相互关联。

### 2. 建立实验计划

```powershell
$experimentId = python scripts/research.py --root $projectRoot experiment add --question 'Does threshold selection explain the recall difference?' --hypothesis 'Matched thresholds change the observed gap' --issue $issueId --baseline 'Current threshold' --changed 'Threshold selection' --controlled 'sample membership||seed||checkpoint' --metrics 'F1||Recall'
```

默认状态为 `planned`。此命令只记录计划，不启动训练或推理。可同时填写 `--dataset`、`--split`、`--seed`、`--environment` 和 `--command`，保存复查所需条件。

正式实验可选择 `--record-level FORMAL`，补全主要指标、判定标准、预期观察、反证观察与分析计划；干预类实验还应写明基线、改动和控制变量。使用以下命令检查计划字段：

```powershell
python scripts/research.py --root $projectRoot experiment validate --id $experimentId --level formal
```

上面的简略 TRACKED 示例尚未填全 FORMAL 字段，直接做 formal 检查会提示缺项；应按研究设计补充，而非将简略计划视为已通过检查。字段齐全检查也不等于实验设计已获得科学认证。

### 3. 在实际运行后更新结果

完成实际实验后，替换下面的结果与局限占位内容：

```powershell
python scripts/research.py --root $projectRoot experiment update --id $experimentId --status completed --result '<actual-result>' --limitations '<actual-limitations>'
```

若运行失败，可记录 `--status failed`，在 `--result` 中保留实际错误，并写明适用限制。失败或无改善的结果同样有助于排除解释。

### 4. 关联证据、决策与变更

```powershell
$evidenceId = python scripts/research.py --root $projectRoot evidence add --claim '<supported-claim>' --source 'results/run-03.csv' --status partial --scope '<tested-scope>' --limitation '<remaining-limitation>'
python scripts/research.py --root $projectRoot update experiments --id $experimentId --set "linked_evidence=$evidenceId"
$decisionId = python scripts/research.py --root $projectRoot decision add --problem '<decision-question>' --selected-option '<chosen-option>' --reason '<reason>' --evidence $evidenceId --limitation '<trade-off>'
python scripts/research.py --root $projectRoot change add --summary '<actual-change>' --files 'configs/run.yaml' --reason '<reason>' --linked-issue $issueId --linked-decision $decisionId --validation '<actual-check-result>'
```

`evidence --status` 可用 `verified`、`partial`、`unsupported`、`contradicted`、`invalidated`、`uncertain`。根据实际材料选择；状态是研究记录，不是工具对主张的自动认证。

### 5. 保存当前状态并查看

```powershell
python scripts/research.py --root $projectRoot state --active-problem 'Recall decrease' --active-issue $issueId --current-stage analysis --record-level TRACKED --active-experiments $experimentId --next-actions 'Review the matched comparison'
python scripts/research.py --root $projectRoot dashboard
python scripts/research.py --root $projectRoot audit
```

`audit` 检查字段、重复项和已支持的关联关系，帮助发现缺记录或断链；实验真伪、解释是否成立仍需依据原始材料判断。

## 查询、汇总与导出

```powershell
python scripts/research.py --root $projectRoot status
python scripts/research.py --root $projectRoot list issues --limit 10
python scripts/research.py --root $projectRoot list experiments --limit 10
python scripts/research.py --root $projectRoot list experiments --id $experimentId
python scripts/research.py --root $projectRoot list evidence --limit 10
python scripts/research.py --root $projectRoot list journal --limit 10
python scripts/research.py --root $projectRoot export --output .research/RESEARCH_SUMMARY.md
```

`list --limit` 使用正整数；查询适合只取当前需要的记录。`export` 生成便于阅读的摘要，不复制原始实验文件。需要更详细分析时，可沿 ID、路径和来源展开原件。

## 文献与写作记录

写作表通过 `writing add` 按需创建，`standard` 和 `strict` 默认开启该能力。

| 类型参数 | 对应文件 | 主要内容 |
| --- | --- | --- |
| `literature` | `literature.csv` | 标题、作者、年份、标识符、URL、核查状态和关联证据 |
| `search` | `literature_search.csv` | 问题、来源、检索式、过滤条件、筛选统计与限制 |
| `reviewer` | `reviewer_map.csv` | 评论 ID、核心关切、技术要求、问题/实验/证据及正文修改 |
| `figure` | `figure_table.csv` | 图表 ID、实验、数据来源、生成方法和验证状态 |
| `paper` | `paper_changes.csv` | 正文位置、改文、原因与关联证据 |

例如，将图表关联到实验：

```powershell
python scripts/research.py --root $projectRoot writing add figure --set 'item_id=Fig-2' --set "linked_experiment=$experimentId" --set 'data_source=results/run-03.csv' --set 'generation_method=plot script' --set 'status=draft'
```

完整审稿原文和论文正文可以保存在原文件中，通过记录对应；映射表用于追踪关系，并不代替阅读完整评论或正文。

## 中断后如何继续

```text
请使用 $research-craft 恢复这个项目。
先读当前 STATE、活动问题和相关实验，再沿证据链接查看必要原件。
说明已完成事项、失败或未决问题、下一步，然后继续当前任务。
```

`STATE.yaml` 保存当前工作，历史保留在 registry 和详情中。看板可重新生成。CSV/YAML 便于备份和版本管理；迁移前可用 `migrate --check` 只读检查，已支持的迁移会先备份。

当前记录保存在本地文件中，适合项目过程管理，不是后台实验调度器或强权限隔离服务。记录内请使用必要的元数据和路径，避免存放账号密钥、敏感样本内容或不宜处理的通信。
