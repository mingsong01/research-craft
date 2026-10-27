# Feature and usage guide

All capabilities use the same `research-craft` Skill. Invoke `$research-craft` in Codex chat and describe the goal, materials, permitted actions and output. Example paths are placeholders.

[Home](../README.md) · [中文详细指南](FEATURES.zh-CN.md) · [Research records](RECORDS.en.md)

## 01 Research and literature

Provide a question, papers, notes and scope. Use it to compare assumptions, methods, evidence and limitations.

> Use $research-craft to review papers/ and notes/literature.md. Compare methods and identify sourced gaps, distinguishing published conclusions from hypotheses. Return a comparison and useful research questions.

Output: source-linked comparison, gap analysis and questions to test. Literature and search records can retain citations, queries and evidence links.

## 02 Code and logs

Provide entry points, commands, configurations and complete errors.

> Use $research-craft to diagnose logs/error.log against train.py and configs/run.yaml. Trace actual shapes and configuration, cite locations and propose a minimal repair. Start with read-only analysis.

Output: code locations, execution paths, supporting evidence and a repair plan. Issues and changes can retain the investigation trail.

## 03 Data and metrics

Provide raw tables, definitions, membership, seeds, thresholds and run identities.

> Use $research-craft to compare results/baseline.csv and results/proposed.csv. Check comparable conditions, retain numerical precision and adverse metrics, and identify source records. Keep raw data unchanged.

Output: comparability findings, anomalies and testable explanations. Aggregates alone do not establish causation.

## 04 Experiment planning

Provide the claim, current evidence, competing explanations and resource limits.

> Use $research-craft to plan controls and follow-ups for the claim that fusion improves generalization. Rank feasible tests, specify controlled variables and explain discriminating outcomes. Record the plan without starting training.

Output: prioritized experiments, interpretation criteria and resource trade-offs. See [experiment records](RECORDS.en.md).

## 05 Model diagrams

Provide forward paths, module definitions, known shapes and target size.

> Use $research-craft to diagram models/network.py and method.md at 180 mm. Recover topology, compare two layouts and deliver editable SVG plus an actual preview. Review topology, information, aesthetics, final size and editability separately.

Output: topology definition, layout choice, vector source, preview and checks. Unknown dimensions remain explicit; rendering-dependent checks require available tools.

## 06 Scientific writing

Provide the source passage, context, evidence and revision scope. Methods cover Abstract, Introduction, Related Work, Method, Experiments, Results, Discussion, Limitations and Conclusion.

> Use $research-craft to revise manuscript/introduction.md using method.md and results/table1.csv. Diagnose the gap, motivation and contribution chain. Return usable prose, reasons for key changes and remaining evidence gaps.

Output: diagnosis, revised passage and evidence-linked explanations. Manuscript maps can connect claims to experiments and revision locations.

## 07 Translation and editing

Provide the complete source, target language and glossary.

> Use $research-craft to translate manuscript/method-zh.md into academic English. Follow glossary.md and preserve equations, numbers, negation and conditions. Perform language conversion only; list scientific concerns separately.

Output: full translation or edited passage, terminology notes and semantic questions. A side-by-side check can be requested.

## 08 Reviewer responses

Provide complete comments, the current manuscript, results and a completed/proposed work list.

> Use $research-craft to address reviews/reviewer2.md. Map each concern to evidence, gaps, manuscript changes and a response. Distinguish completed work from proposals and verify numbers, references and locations.

Output: comment map, supplement plan, manuscript revisions and response draft. Reviewer records can link issues, experiments and evidence.

## 09 Research guidance

Provide sourced feedback, the corresponding passage and study constraints.

> Use $research-craft to interpret notes/supervision.md against manuscript/discussion.md. Explain the problem, rationale and conditions. Distinguish scientific corrections, preferences and study-specific strategies; propose revisions and verification.

Output: actionable interpretation, priorities and unresolved questions. Uncertain attribution remains explicit; important choices can become evidence-linked decisions.

## 10 Resumable tasks

Provide the project and current objective, with any existing research records.

> Use $research-craft to continue this revision. Read current state and relevant active records in .research/, locate the evidence for Method notation consistency, continue the task and update necessary state and source locations.

Output: a useful state summary, actual work and a traceable next step. One-off tasks generally need no persistent record.
