# Evidence and Writing

Read for formal claims, literature work, reviewer responses, figures/tables, or manuscript consistency checks.

## Evidence discipline

Create formal evidence only when it affects a technical decision, paper claim, or reviewer response. Link `Claim -> Evidence -> Source`; do not create evidence rows for every observation.

Statuses are `verified`, `partial`, `unsupported`, `contradicted`, `invalidated`, or `uncertain`. Never invent numeric confidence. Match claim scope to evidence scope and preserve important limitations.

Prefer primary papers, standards, official documentation, author repositories, raw results, reproducible calculations, and explicit user facts. Search around a concrete research question. A title, abstract snippet, or secondary article is not enough for a strong claim.

For FORMAL writing, separate drafting, evidence verification, and approval. Build an evidence outline before prose: section purpose, claim/evidence IDs, numeric/method/result sources, uncertainty, conflicts, and missing information. Unsupported material stays in an unresolved list; fluent wording never upgrades its status.

For chapter/paragraph diagnosis, academic English or bilingual revision, read
[scientific-writing.md](scientific-writing.md). For substantive reviewer/advisor concerns,
supplement selection, response drafting or submission-package consistency, read
[reviewer-revision.md](reviewer-revision.md). Load the relevant part, not both in full by default.
For a consequential revision, deliver the actual revised passage, why the smallest edit
resolves the problem, its source/claim check, and unresolved content; a list of advice is insufficient.

Never invent or silently complete citations, identifiers, quotations, numeric results, denominators, sample sizes, units, methods, software versions, approvals, registrations, authorship, funding, conflicts, availability statements, or manuscript locations. Use explicit `missing`, `unverified`, or `not applicable` states.

## Reviewer workflow

Use `Reviewer comment -> Underlying concern -> Technical requirement -> Existing evidence -> Missing evidence -> Minimal experiment or analysis -> Manuscript change -> Response -> Consistency audit`.

Do not start by polishing the response. First identify what would actually resolve the concern. Stop when evidence is sufficient for that concern; do not expand into unrelated experiments.

Treat unpublished manuscripts, reviews, and editorial correspondence as confidential. Confirm the user is authorized and follow the venue's current policy before using external services. Keep local processing as the default.

For each review comment, produce a bounded chain:

1. exact concern and manuscript location;
2. observable evidence or applicable criterion;
3. why it affects validity, interpretation, reproducibility, or clarity;
4. smallest proportionate action;
5. actual revised passage or artifact;
6. response that states exactly what changed and where.

If a request is not scientifically applicable, do not blindly agree or defensively refuse. Explain the mismatch, show the available evidence, narrow the claim or add a limitation where appropriate, and propose the smallest alternative that answers the underlying concern. Never claim a manuscript change that is absent from the delivered revision.

When writing tracking is enabled, create only the needed centralized CSV:

- `reviewer_map.csv`: reviewer comment to issue, experiment, evidence, manuscript change, and response status.
- `figure_table.csv`: figure/table to experiment, data source, generation method, and validation.
- `paper_changes.csv`: manuscript location, change, reason, supporting evidence, and status.
- `literature.csv`: bibliographic identity, source type, accessed date, verification state, and linked evidence for formal literature work.
- `literature_search.csv`: exact source, query, date, filters, hit/screening counts, and limitations for reproducible formal searches.

## Language strength

Before describing a numeric change as improvement or degradation, establish the metric's direction of benefit, scale, and units. If these are unspecified, report the supplied values and their arithmetic difference neutrally; do not invent units, percentages, or which direction is better. When direction and units are established, use them normally without unnecessary qualification.

- Direct reliable observation: "shows" or "was measured," within scope.
- Repeated consistent evidence: "supports" or "is consistent with."
- Plausible explanation: "suggests" or "may be explained by."
- Missing evidence: retain `UNKNOWN` and say what cannot be claimed.

Never translate empirical improvement into a theoretical guarantee, one dataset into universality, the best tested value into a theoretical optimum, or correlation into a mechanism. Verify that manuscript numbers agree with experiment records and that every important figure/table can be traced to its data.

## Scientific prose craft

Draft from a claim-evidence outline, not from a desired narrative. Each paragraph should have one scientific job: orient the question, report an observation, compare with a baseline, interpret within evidence, or state a limitation/implication. Put the load-bearing result early; retain necessary numbers, units, denominators, intervals, and scope. Remove generic significance language, duplicated conclusions, inflated novelty, and procedural narration that does not help the reader evaluate the science.

Reconcile methods and results after revision: populations, analysis sets, exclusions, sample sizes, units, labels, timepoints, model/checkpoint versions, tables, figures, abstract, and conclusion must agree. A legitimate difference must be named rather than silently normalized.

## Reporting standards

For FORMAL publication work, identify whether a discipline-, study-, dataset-, model-, or venue-specific reporting guideline applies. Verify the current official version rather than relying on remembered checklist items. Use the guideline as a completeness aid, not as a substitute for scientific judgment. Record which guideline/version was checked, which items are not applicable, and any unmet items that affect interpretation.

Never claim compliance with a reporting standard, systematic-review protocol, benchmark policy, or reproducibility checklist unless every applicable requirement was actually checked.
