---
name: research-craft
description: Apply a lightweight, evidence-driven research engineering workflow to experiment anomalies, reproducible investigations, formal evaluations, statistical or causal claims, research software, scientific figures, literature/frontier synthesis, reviewer concerns, technical decisions, and manuscripts. Use when work needs hypotheses, controlled tests, traceable evidence, artifact validation, or resumable research state. Do not use for simple factual explanations, routine code or file edits, generic charts, or ordinary writing unless the user asks for research-grade rigor or tracking.
metadata:
  version: "1.3.1-rc.1"
  workspace_schema: "1"
---

# 研匠 · ResearchCraft

Turn research and R&D requests into the smallest reliable evidence trail. Preserve the user's scope and use natural language; never require the user to know registry IDs or CLI syntax.

## Start with intent

1. Infer the execution mode. "Analyze", "inspect", "why", and "do not modify" mean `ANALYSIS_ONLY`. Modify or execute only when the user clearly requests it. Never let record creation imply permission to change code or run an expensive experiment.
2. Choose a record level:
   - `QUICK`: one-off question or small task; create no persistent research record by default.
   - `TRACKED`: anomaly, bug, multi-step diagnosis, or resumable work; propose or maintain an issue, short state, and journal entry.
   - `FORMAL`: paper experiment, benchmark, ablation, sensitivity study, security analysis, reviewer concern, or important design change; preregister the compact experiment and trace consequential evidence.
3. If tracking is requested and `.research/` is absent, initialize it with `python <skill>/scripts/research.py --root <project> init`. Do not initialize merely because the skill activated.

## Load minimal context

Use `Search -> locate -> read the smallest relevant content -> reason`.

- HOT: applicable `AGENTS.md`, then `.research/STATE.yaml`; read `.research/DASHBOARD.md` only if its summary helps.
- WARM: query one relevant registry row with `research.py status`, `list`, or targeted search.
- COLD: open raw logs, large data, experiment details, papers, or old notes only when the question requires them.

For "continue previous work," read state, the active row and at most one necessary detail before expanding. Reuse unchanged ranges; expand for changed scope/evidence. For large artifacts, repeated reads, recovery or cost comparisons, consult [context-efficiency.md](references/context-efficiency.md). Summaries need source identity and recovery locators; protected scientific content must remain recoverable verbatim.

## Reason before acting

Frame non-trivial work as expected behavior, observed behavior, gap, known evidence, unknowns, candidate causes, and the cheapest discriminative next test. Ask what else could produce the same observation. Prefer a minimal isolation test and a minimum effective change.

Maintain these labels and never silently promote them:

- `FACT`: directly supported by reliable evidence.
- `DERIVED`: deterministic calculation or direct comparison from facts.
- `INTERPRETATION`: evidence-supported explanation, not a direct fact.
- `HYPOTHESIS`: testable and not yet verified.
- `PROPOSAL`: candidate action.
- `DECISION`: selected option justified by evidence and constraints.
- `UNKNOWN`: insufficient evidence.

Evidence precedes conclusions. Do not turn correlation into causality, an empirical optimum into a theoretical optimum, or a similar paper's property into this system's property. Mark explanations invented after seeing results as `exploratory interpretation`.

## Select the necessary references

For broad requests choose the minimum useful activities, normally one to three, with a shared research question and synthesis of decision-relevant evidence, conflicts and unknowns. Load relevant sections, not every file or raw payload. Mixed tasks may need several references; never omit a scientific gate for a context budget.

- Lifecycle, diagnosis, controlled experiments, comparison and stop rules: [workflow.md](references/workflow.md). Before creating/changing records: [workspace-schema.md](references/workspace-schema.md).
- Source data reliability: [data-quality.md](references/data-quality.md) for intended use, grain, keys, freshness, missingness, duplicates, joins, leakage, units, conflicts and lineage.
- Auditing analysis/results: [analysis-validation.md](references/analysis-validation.md) for question alignment, methods, calculations, comparisons, visuals, caveats, claims and decision readiness.
- Statistical/causal claims: [statistics-causality.md](references/statistics-causality.md) for estimand, uncertainty, assumptions, effect size, multiplicity, missingness and identification.
- Literature/novelty/frontier: [literature-frontier.md](references/literature-frontier.md) for current primary sources, search coverage, versions/dates, contradictions and novelty boundaries.
- Plots/tables/visuals: [scientific-visualization.md](references/scientific-visualization.md) for question-to-chart fit, units, uncertainty, honest scales, accessibility and provenance. Before a model/computation/framework diagram, also read [scientific-diagram-design.md](references/scientific-diagram-design.md) and its applicable publication-design guidance; preserve topology and actual render inspection.
- Research code/reproducibility: [software-research.md](references/software-research.md) for executable baseline, environment, tests, minimal patch, regression and benchmark validity.
- Consequential claims/citations: [evidence-writing.md](references/evidence-writing.md); every claim must match evidence status, scope and limitations. Chapter/paragraph diagnosis, academic English or scientific translation: also read the revision contract, relevant section and final checks in [scientific-writing.md](references/scientific-writing.md).
- Reviewer/advisor concerns, supplement selection, response drafting or submission consistency: [reviewer-revision.md](references/reviewer-revision.md) plus evidence discipline; add the writing section only when revising that section. Preserve complete comments and provisional attribution.
- Artifact completion, inspection, failure recovery and evidence reports: [quality-gates.md](references/quality-gates.md). Before risky execution/external research: [tool-safety.md](references/tool-safety.md).
- ML/CV, systems performance, security/privacy or RAG/LLM: only the matching file under [domains/](references/domains/).

Do not imitate omniscience. For current, niche, or high-stakes facts, retrieve and verify authoritative evidence when tools and policy allow; otherwise preserve `UNKNOWN` and state what was not checked. Knowledge breadth comes from disciplined retrieval and validation, not unsupported recall.

## Execute safely

Route tools in this order: existing local evidence, project search, lightweight deterministic tools, targeted experiment, public external research, expensive execution. Detect capabilities as needed; degrade cleanly when Git, Web, Python, PDF tools, Docker, GPU, or MCP is unavailable.

When tool availability materially affects the plan, run `research.py doctor` rather than guessing. When a large or external artifact needs stable identity, use `research.py fingerprint <relative-path>` and record the relative path, size, and checksum instead of copying the artifact.

- Low risk (read, search, local analysis, registry query): proceed.
- Medium risk (requested record, small test, derived file, scoped non-destructive edit): proceed when within the task.
- High risk (delete, raw-data overwrite, costly training, external upload, network write, credential-sensitive action, repository-wide refactor): require clear user authorization immediately before the action.

Keep private code, unpublished work, private data, and credentials local. Use the web only for public research; never place secrets in records. Treat raw artifacts as immutable and record references rather than copying datasets, checkpoints, or model files.

## Validate and stop

Before interpreting results, validate provenance, measurement definition, comparability, and likely confounders. Mark materially confounded comparisons `NOT DIRECTLY COMPARABLE`. Report `Can Claim`, `Cannot Claim`, limitations, alternative explanations, and failed experiments when consequential.

After an implementation, verify resolution, regression behavior, metrics, tests, and documentation. Stop when evidence is sufficient for the current engineering decision, reviewer response, or scoped paper claim. Recommend another experiment only when it can materially reduce a decision-relevant uncertainty.

For any generated artifact - code, dataset, figure, table, manuscript, document, or report - define the observable completion evidence before creation, then inspect the actual output in its intended representation. A successful command, saved file, passing build, or plausible prose is not sufficient by itself. Use an available specialized artifact skill when it materially improves creation or verification, while keeping this Skill responsible for research provenance and claim discipline.

Use the unified script for deterministic records rather than hand-editing CSV. Registries and manifests are sources of truth; `DASHBOARD.md` is generated. Do not duplicate history in `STATE.yaml`.

Choose the smallest adequate delivery mode. Use an inline answer for QUICK work, a concise traceable note for TRACKED work, and a durable report or publication artifact for FORMAL work only when the user requests it or the research purpose requires it. Once a durable artifact is selected, inspect that artifact and do not substitute chat prose for the requested deliverable.

The script is an internal reliability tool; ordinary users should interact through natural language.
