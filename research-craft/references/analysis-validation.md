# Analysis Validation and Decision Readiness

Read when reviewing an analysis, notebook, spreadsheet, chart, report, recommendation, or manuscript result before it is shared or used for a decision. Validate the reasoning artifact; use `data-quality.md` separately when the underlying source may be unreliable.

## Inventory before judging

Identify the actual question, audience, decision, headline claims, numbers, sources, time windows, populations, filters, baselines, and stated caveats. Confirm the artifact answers the intended question rather than an easier neighboring question.

Validate:

- metric definitions, formulas, units, denominators, aggregation, and independent spot calculations;
- population, sampling, exclusions, missingness handling, comparison window, and baseline fairness;
- statistical assumptions, uncertainty, effect size, multiplicity, and causal identification where relevant;
- consistency between text, tables, figures, code, experiment records, and source data;
- whether visual emphasis and written language match the magnitude and strength of evidence;
- alternative explanations, sensitivity to reasonable choices, and limitations that alter the decision.

Classify findings by consequence rather than count:

- `CRITICAL`: invalidates the central result, comparison, or decision.
- `MAJOR`: materially changes a central estimate, claim strength, or reproducibility.
- `MODERATE`: does not overturn the conclusion but needs correction or qualification.
- `MINOR`: presentation or maintainability issue with no material scientific effect.

Give each non-minor finding a location, observation, evidence, consequence, and smallest corrective action. A long checklist with no prioritization is not a useful audit.

Trace each load-bearing claim to evidence. A correct calculation can still support the wrong decision if its scope, population, grain, or estimand is mismatched.

## Conclude with readiness

Use one of three bounded outcomes:

- `READY`: evidence and analysis support the stated use within declared scope.
- `READY WITH CAVEATS`: usable only if named limitations accompany the conclusion.
- `NOT READY`: a material data, method, calculation, provenance, or claim gap remains.

Report `Can Claim`, `Cannot Claim`, the most decision-relevant defect, and the smallest verification or repair needed. Do not rewrite the artifact merely to make it sound more certain.
