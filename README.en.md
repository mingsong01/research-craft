<div align="center">
<img src="research-craft/docs/images/hero-banner.png" alt="ResearchCraft: evidence-driven scientific analysis, model diagrams, academic writing and reviewer response" width="100%" />

# ResearchCraft · research-craft

**Connect source evidence, scientific judgment and checked research artifacts.**

[中文完整说明](README.md) · [Usage and commands](research-craft/docs/USAGE.zh-CN.md) · [Snapshot checks](research-craft/PUBLISHING_SNAPSHOT.md)
</div>

ResearchCraft is **one integrated Codex Skill** for scientific analysis, editable model diagrams, manuscript revision, faithful translation and reviewer response. Its references, scripts and examples are loaded as needed. The four capability areas are not four separate installations or autonomous agents.

Public snapshot: **2026-10-27**. Skill identifier: `research-craft`. Skill version: `1.3.1-rc.1`; workspace schema **1**. This includes the completed diagram, writing and context improvements; the candidate identifier is not a universal scientific-quality certification or a stable-release claim.

## What you can do

![Capability map](research-craft/docs/images/capability-map.png)

| Task | Work performed | Deliverable |
| --- | --- | --- |
| Research questions and literature | Define the question; locate primary sources, conflicts and novelty boundaries | Source-grounded synthesis with explicit unknowns |
| Experiments and data | Check units, denominators, split membership, seeds, thresholds and comparability; preserve adverse results | Data audit, competing explanations and a discriminating test plan |
| Code and logs | Locate executed paths, configuration and actual failures | Specific diagnosis, minimal authorized patch and relevant regression evidence |
| Model diagrams | Recover topology, choose architecture-specific visual language, compare layouts and inspect actual exports | Editable FigureSpec/SVG, topology contract and previews |
| Scientific writing | Diagnose paragraph purpose and argument dependencies; make a minimal effective revision | Actual revised text, source checks and unresolved issues |
| Translation and polishing | Preserve terminology, numbers, negation, conditions and claim strength | Faithful language revision; separate scientific correction proposals |
| Reviewer response | Resolve every substantive concern against evidence and manuscript changes | Supplement plan, revised passages and formal response draft |
| Context and recovery | Select relevant references, bound queries and keep recoverable source identities | Precise excerpts and the smallest sufficient research state |

## Install and start

```bash
git clone https://github.com/mingsong01/research-craft.git
cd research-craft
```

Copy the **inner research-craft/** folder into your research repository at `.agents/skills/research-craft/`. Personal installations use `$HOME/.agents/skills/research-craft/` under the current [official discovery conventions](https://learn.chatgpt.com/docs/build-skills). Older hosts may use another configured location. Check and back up an existing installation before copying; this repository does not install itself globally.

```text
your-project/.agents/skills/research-craft/
  SKILL.md
  references/
  scripts/
  assets/
  demo/
  tests/
  evals/
```

Refresh skill discovery or start a new session. Invoke `$research-craft`, or name the Skill in a natural-language request:

```text
Analyze these logs and metrics. Check split, seed, checkpoint and metric
definitions first. Preserve failures and adverse findings. Analyze only;
do not change code or start training.
```

```text
Draw an editable architecture diagram from this model's actual forward path.
Recover branches, skips, fusion and training-only connections. Do not invent
unknown shapes. Compare two substantive layouts and inspect the 180 mm export.
```

```text
Revise this Introduction. Diagnose the gap, motivation and contribution chain.
Return the actual revised English passage and specific reasons. Keep accurate
sentences; do not invent citations, priority claims or experimental results.
```

```text
Address each reviewer concern using the complete original comment. Separate
existing evidence, missing evidence, proposed supplements, manuscript revision
and response. Never describe a proposed experiment as completed.
```

## A lightweight workflow

![Workflow](research-craft/docs/images/workflow-overview.png)

QUICK work creates no research record by default. TRACKED work retains a small resumable state. FORMAL work traces consequential experiments, claims or reviewer decisions. Initialization is conditional on the task, not a side effect of activation.

The helper initially creates only config, STATE and a generated dashboard. Registries, experiment details and writing maps are lazy. Registry/manifest records are authoritative; a dashboard is a view. Recording a plan does not prove an experiment ran or establish external preregistration.

FACT, DERIVED, INTERPRETATION, HYPOTHESIS, PROPOSAL, DECISION and UNKNOWN remain distinct. A measured drop, its calculated magnitude and an explanation for the drop are different kinds of statements.

## Model diagrams

![Diagram pipeline](research-craft/docs/images/diagram-pipeline.png)

Recover the documented or executed computation before choosing a composition. Preserve stable nodes, directed typed edges, skips, fusion, known shapes and training/inference conditions. A cleaner layout does not authorize changing scientific content.

Encoder–Decoder designs emphasize scales and aligned skips; Transformers emphasize tokens, attention roles and residuals; SSM designs emphasize recurrence and gating; multimodal diagrams distinguish sources, alignment and interaction. Feature volumes should convey known structure rather than decoration.

For complex figures, compare two genuinely different layouts. Accept topology, information, visual quality, final physical size and editability separately. Automated SVG checks screen structural/geometric issues; they cannot certify aesthetics. Render and inspect arrows, labels, gray-scale distinction, fonts and cropping at the intended size.

### Actual repository examples

These are **synthetic architecture examples**, not independently verified implementations of a real trained model. Their original vector sources and contracts are included.

![Synthetic multimodal example](research-craft/docs/images/example-multimodal.png)

[Editable SVG](research-craft/demo/publication/multimodal-A/architecture.svg) · [FigureSpec](research-craft/demo/publication/multimodal-A/figure-spec.json) · [Contract](research-craft/demo/publication/multimodal-A/topology.json)

![Synthetic multiscale example](research-craft/docs/images/example-multiscale.png)

[Editable SVG](research-craft/demo/publication/unet-multiscale/architecture.svg) · [FigureSpec](research-craft/demo/publication/unet-multiscale/figure-spec.json) · [Contract](research-craft/demo/publication/unet-multiscale/topology.json)

The layouts target 180 mm. Direct scaling to 85 mm remains limited. Existing Bybit warnings are retained and require applicable explanations, not disabled rules. Real-code agreement, native-editor round trips, printing and cross-platform rendering require task-specific verification.

## Scientific writing and reviewer revision

![Writing pipeline](research-craft/docs/images/writing-pipeline.png)

Guidance covers Abstract, Introduction, Related Work, Method, Experiments, Results, Discussion, Limitations and Conclusion. Diagnose the specific argument or paragraph function rather than impose fixed paragraph counts or stock phrases.

A revision should deliver the actual passage, explain the smallest effective repair and check its evidence. Method revisions preserve definitions, equations and validity conditions; results distinguish observations, explanations, mechanisms and limits. Good bounded prose may remain unchanged.

Language-only work must preserve scientific meaning. Keep numerical precision, units, negation, conditions, uncertainty and claim strength. If the source contains a scientific defect, provide a faithful language rendering and a separately identified correction proposal.

Conditional guidance distilled from research experience is not universal mentor authority. Unconfirmed speaker identity is not a verified quotation; a particular table order or appendix strategy is not an academic standard.

The response chain is complete comment → core concern → technical requirement → existing evidence → gap → minimal discriminating supplement → manuscript change → response → version audit. Preserve partial or unresolved items and real manuscript locations. Do not invent completed experiments, citations or resolution.

## Context efficiency without evidence loss

![Context efficiency](research-craft/docs/images/context-efficiency.png)

Use targeted references, HOT/WARM/COLD loading, bounded registry queries, streaming CSV summaries and exact source recovery. The helper supports same-stream SHA-256 identity, source ranges and raw extreme-value strings. A summary is not a substitute for sample membership, complete reviewer wording, formula conditions, adverse metrics or relevant failure traces.

No task-level percentage of Token savings is claimed. Tool-view byte reduction is not actual model input/output usage or complete task cost. Inspect unnecessary reads, verbose payloads, repeated calls and avoidable rework in real tasks, while preserving sufficient scientific detail.

## Runtime and verification

Use an existing Codex account and available tools; no additional model API purchase, GPU, Docker, agent suite or permanent MCP is required. Python helpers use the standard library (documented target 3.9+). SVG lint/render work may need Node.js and an existing browser; Node 22+ is recommended for the optional Chromium export helper. Missing tools must be disclosed, not silently treated as completed checks.

The current engineering record is 110 unit tests and 60 offline contracts. The public archive is also checked after fresh extraction. See [snapshot scope](research-craft/PUBLISHING_SNAPSHOT.md). Historical model evaluation describes its frozen version only and is not a new evaluation of this snapshot.

## Privacy, licensing and contribution

Local-first records do not mean offline model inference. The host's model service may process instructions and tool outputs. Keep unpublished research, correspondence, credentials, private corpora and raw model logs out of public Issues and repositories.

The original-work license remains deferred by the publisher. Public visibility does not make all original work MIT-licensed; retained third-party licenses apply to their respective components. Read [license status](research-craft/LICENSE_STATUS.md) and [third-party notices](research-craft/THIRD_PARTY_NOTICES.md). No upstream endorsement is implied.

Contributions should identify a concrete defect with a lawful, sanitized minimal example, expected/actual behavior and relevant source/artifact checks. Improve an actual task rather than add unnecessary process. This Skill does not promise universal paper reproduction, publication acceptance, top-journal aesthetics, advisor-level judgment or independent quality certification.


[Local build checks](verification/local-checks.json)
