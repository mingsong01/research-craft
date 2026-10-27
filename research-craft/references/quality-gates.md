# Research Artifact Quality Gates

Read when the task produces or materially changes code, data, figures, tables, manuscripts, documents, presentations, or formal reports.

## Define completion evidence

Before creating the artifact, state the intended user-visible or scientific outcome and the cheapest sufficient evidence that would prove it. Match the validation surface to the deliverable:

- Code: executable tests, invariants, regression behavior, and relevant performance/correctness evidence.
- Data: schema, row/count reconciliation, units, missingness, transformations, and independent control totals when available.
- Figure/table: rendered inspection, data agreement, labels/units, uncertainty, accessibility, and provenance.
- Manuscript/report: claim-evidence consistency, citation verification, numerical cross-checks, structure, and rendered layout when applicable.
- Document/spreadsheet/presentation/PDF: use an available specialized skill and follow its native render/recalculate/inspect loop; preserve research provenance here rather than duplicating format mechanics.

## Generate, inspect, verify, iterate

1. Establish the baseline or source artifact and preserve it unless change is authorized.
2. Produce the smallest in-scope change.
3. Inspect the real artifact, not only source code or the command exit status.
4. Exercise the target flow or scientific comparison.
5. Compare the observed result with the expected result and record mismatches.
6. Fix supported defects and repeat only affected checks.
7. Report remaining untested states and limitations.

Completion claims require fresh evidence from the current state. For each claim, name the proving command or inspection, run the full check, read the exit status and failure count, and compare the output with the requirement. Do not infer that tests pass because a build passed, that an artifact is correct because it exists, or that a defect is fixed because code changed.

Use the cheapest proof that discriminates success from failure: a recalculated cell, rendered page, exact data reconciliation, plot inspection, test assertion, reproduced interaction, or independent calculation. Do not generate large validation dumps when a small targeted check suffices.

## Failure recovery

On failure, read the exact error, preserve the last valid artifact, localize the failing stage, and retry with a minimal patch. Do not restart the entire workflow or repeatedly apply the same failed action. A failed experiment remains recorded; a failed artifact generation should not replace a valid prior output.

## Completion report

For non-trivial work, report:

- Outcome: what changed or what conclusion is supported.
- Evidence: the observations, sources, or tests that support it.
- Validation: what was actually executed, inspected, rendered, or recalculated.
- Limitations: untested conditions, uncertainty, and unavailable tools/sources.
- Research trail: linked issue, experiment, evidence, decision, or change when tracking applies.

Avoid ceremony for QUICK tasks. The report should be proportional to risk and future reuse.
