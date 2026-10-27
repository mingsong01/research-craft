# Historical model evaluation

These results describe an earlier frozen candidate. Subsequent diagram, writing and context updates are covered by local engineering checks, not by the comparison below. See [current coverage](PUBLISHING_SNAPSHOT.md).

The release candidate preserves the v1.3.0 architecture and workspace schema 1. Its scoped changes address computational evidence attribution, neutral numerical wording when metric semantics are unknown, and the distinction between prespecification and evidenced preregistration.

## Completed verification

- The main confirmation round used **8 new cases + 4 regressions**, generating **24 paired responses**, scored by **two independent evaluator sessions** using the same model and effort.
- Four development cases first verified the original writing correction, attributable-run boundaries and a known-metric control.
- Actual manuscript and reviewer-response files were inspected. Editable SVGs were rendered and inspected; all six required nodes and seven edges passed topology/geometry checks with visible arrows and no unrelated-node occlusion.
- The full round preserved the writing and diagram regressions but exposed one unsupported preregistration term. Its raw result remained BLOCKED; bounded arbitration confirmed that issue.
- A one-sentence patch was created separately. Both affected original computational cases were rerun as development and passed.
- **Four fresh targeted cases** then produced **eight new paired responses**, with two independent evaluator sessions. Candidate technical scores were **8/8 on all four**, with no hard failure or loss to the baseline. The targeted confirmation gate passed.
- The **ten unaffected cases** retain their previous evidence because their exact task-relevant instruction packets are byte-identical. They were not regenerated or relabeled as new holdout results.
- The standalone suite has **40 passing tests**, offline behavioral-contract checks, and an isolated end-to-end demo. Archive extraction was tested without the development directory or upstream checkout.

Model: `gpt-5.6-sol`, reasoning effort: `medium`, through Codex CLI with the signed-in OpenAI service. Only Skill instructions, anonymous synthetic cases and generated outputs were supplied to the model harness. No original private research corpus was supplied. A/B labels were randomized and version paths removed from scoring packets. Two quota-interrupted diagram attempts were preserved internally and retried once after the service reset.

## Scope and limitations

These results support correction of identified defects and preservation of tested behaviors. They do not establish universal expertise, statistical superiority, native-platform execution that has not occurred, or independent human peer review. Some cases still reached the rubric ceiling. The final patch used targeted confirmation, not a newly generated full 12-case suite.

Fixed task-relevant instruction packets were supplied. Native Skill discovery and autonomous reference selection were not measured. Cumulative model usage includes cached context and tool turns; no billing or general token-saving claim is made. Main hot instructions and workflow architecture were not expanded.
