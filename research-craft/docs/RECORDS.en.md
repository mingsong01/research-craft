# Research records and experiment management

ResearchCraft links questions, experiments, evidence, decisions and changes in the research project's `.research/` directory.

[Home](../README.md) · [Feature guide](FEATURES.en.md) · [中文完整教程与命令](RECORDS.zh-CN.md)

![Research records and resumable work](images/research-records.png)

## What you can record

| Record | Contents |
| --- | --- |
| Issues | Symptoms, status, cause, experiment links and next actions |
| Experiments | Question, type, status, changed variable, result and evidence links |
| Experiment manifest | Hypothesis, controls, data/split/seed, environment, code identity, command, metrics, findings and limitations |
| Evidence | Claim, source, support status, scope and limits |
| Decisions | Selected option, rationale, evidence and trade-offs |
| Changes | Files, reasons, linked issue/decision and validation |
| Journal | Timestamped progress entries with linked IDs |
| Writing maps | Literature, searches, reviewers, figures and manuscript changes |
| Current state | Active problem, experiments, hypotheses, blockers and next steps |
| Dashboard | A readable view generated from the records |

Hypotheses live in experiment manifests and current state. Registries and manifests retain durable information; the dashboard is a view.

## Start through Codex chat

```text
Use $research-craft to track this project's recall decrease. Record the
issue and available evidence, create a threshold-comparison experiment
plan, link the records and update current state and the dashboard.
Do not run the experiment yet.
```

After a real run:

```text
Use $research-craft to update the experiment from logs/run.txt and
results/run-03.csv. Check the split, seed and configuration. Preserve
the actual results, adverse metrics and limits; link supported claims
to evidence and record the next decision.
```

One-off tasks generally need no workspace. `standard` enables tracking defaults; `minimal` is lighter and `strict` emphasizes detailed records. Presets do not grant execution permissions.

## Experiment lifecycle

1. Initialize the research workspace and add an issue.
2. Record the question, hypothesis, baseline, changed and controlled variables.
3. Add data, split, seed, environment and command details as available.
4. Carry out the actual experiment through your authorized workflow.
5. Update the record with its actual completion/failure status, findings and limits.
6. Add evidence and link decisions or changes to the supporting records.
7. Update current state and regenerate the dashboard.

Recording a plan does not execute training or inference. Failed and unfavorable results are retained. Large data, logs and checkpoints can remain at their existing location with paths and SHA-256 identities.

FORMAL plans require the primary metric, decision criterion, expected and falsifying observations, and analysis plan. Interventional plans also need the baseline, changed variable and controls. `experiment validate --level formal` checks required fields; it is not independent scientific validation.

## Queries and export

Run from the installable Skill directory and replace `<project>`:

```text
python scripts/research.py --root <project> status
python scripts/research.py --root <project> list experiments --limit 10
python scripts/research.py --root <project> list evidence --limit 10
python scripts/research.py --root <project> list journal --limit 10
python scripts/research.py --root <project> dashboard
python scripts/research.py --root <project> audit
python scripts/research.py --root <project> export --output .research/RESEARCH_SUMMARY.md
```

Lists use positive limits. The audit checks structure and supported links. Export creates a readable summary rather than copying raw artifacts. The [Chinese command walkthrough](RECORDS.zh-CN.md#实验从计划到结果) covers creation and updates with linked IDs.

## Literature, figures and reviewer records

`writing add` supports `literature`, `search`, `reviewer`, `figure` and `paper`. These map bibliographic and search information, reviewer concerns, figure/data provenance and manuscript changes to research evidence. They are created as needed. Keep complete comments and manuscripts in their source files.

## Continue later

Ask Codex to read current state and relevant active records, then follow evidence links to the necessary source detail. State describes current work; registries retain history. CSV/YAML records can be backed up or versioned, and the dashboard can be regenerated. Supported schema migration performs a backup; `migrate --check` is read-only.

This is local file-based process tracking, not a background experiment scheduler or a security isolation service. Keep credentials and sensitive contents out of records.
