# Data Quality and Semantic Context

Read when the trustworthiness of a dataset, query result, dashboard, log, or metric source is itself in question. This is source QA, not validation of the conclusions drawn from the source.

## Establish intended use and grain

Before profiling, identify the downstream decision, unit of analysis, expected grain, candidate key, time semantics, units, source owner, freshness expectation, and any canonical metric definition. A dataset can be internally clean yet unsuitable for the question.

Create a bounded manifest before content-heavy analysis: paths or identifiers, formats, sizes, row/column counts where cheap, schemas, partitioning, modification dates, checksums when identity matters, and access constraints. Use it to choose the narrowest files and columns; do not load the dataset merely to discover what exists.

Check the highest-value risks first:

- schema or type drift, missing required fields, invalid values, and unit mismatches;
- missingness patterns, duplicate keys, unexpected row-count changes, and broken referential coverage;
- timestamp, timezone, cutoff, late-arrival, and freshness errors;
- leakage across train/validation/test or future information entering earlier observations;
- join multiplication, dropped populations, filters, eligibility rules, and denominator changes;
- conflicts between nominally equivalent sources or metric definitions;
- transformation lineage and whether a reproducible path exists from raw to derived data.

Use programmatic aggregation before loading data into context. `research.py summarize-csv <file> --columns ... --key ...` performs streaming column summaries and disk-backed exact key checks without copying the source into `.research/`.

## Report decision risk

Report concrete observations separately from likely causes. Explain which analyses or claims each defect could bias, the affected scope, and whether the data is `usable`, `usable with caveats`, or `not ready for the stated use`. Recommend the smallest remediation or automated check that protects the intended use.

When sources disagree, do not silently choose one. Compare definition, grain, population, time window, transformations, freshness, and provenance. Preserve the disagreement as `UNKNOWN` until reconciled.

For stable team-specific semantics, create an on-demand note only when it will be reused. Keep canonical metric definitions, grains, joins, filters, time rules, and known caveats together; do not duplicate them across registries and reports.

Never repair source data silently. Preserve raw inputs, write a derived output, and record every coercion, imputation, exclusion, deduplication, relabeling, and unit conversion. Validate control totals or invariants after transformation.
