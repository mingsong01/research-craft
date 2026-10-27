# Reviewer revision and evidence-grounded research guidance

Read for substantive reviewer/advisor comments, supplementary experiment selection,
response letters and submission consistency. Reuse the chain and optional reviewer_map.csv
in evidence-writing.md; do not introduce another workspace or tracking schema.

## Resolve the concern before polishing the answer

Keep the exact reviewer wording and a stable comment ID in the private work record.
Split a compound comment into its distinct demands; retain the connection to the original.
Distinguish a DIRECT concern from an inferred interpretation. Do not answer an easier
question or assume that a mentor's interpretation overrides the actual reviewer text.

For each substantive item, establish:

`Original comment → core concern → technical requirement → available evidence → missing
discriminating evidence → minimal experiment/analysis → actual manuscript revision →
formal response → version/meaning/location consistency`.

The deliverable includes the revised passage or a justified no-change decision, not
just advice. Record planned / author-reported / inspected / independently reproduced
actions distinctly. A reported experiment can support an attributed draft; the assistant
not having run it does not show the authors did not run it. Do not insert internal audit
qualifiers into every manuscript sentence or imply misconduct from absent local records.

Choose the branch that matches the actual problem:

- **Clarity defect:** evidence exists but the explanation is missing. Repair the passage,
  verify it and explain the change; no redundant experiment is necessary.
- **Evidence deficit:** define the claim and the result that would distinguish alternatives;
  plan the smallest adequate contrast, including a non-positive/indeterminate outcome.
  Do not claim it completed until the corresponding artifact is available.
- **Actual error:** acknowledge and correct it explicitly; inspect dependent tables,
  conclusions and reply items. Diplomatic wording must not hide the error.
- **Not applicable / reviewer misunderstanding:** respectfully state the verified scope,
  why the requested test would not resolve the concern, and the smallest valid alternative
  or limitation. Do not fabricate results to agree with the reviewer.
- **Unresolvable under present evidence:** narrow the claim, disclose the relevant boundary
  and state the missing requirement. Do not certify the item as fully resolved.

## Apply guidance as judgments, not authority

Classify a guidance source before using it: confirmed source content, interpretation,
scientific procedure candidate, domain-specific suggestion, personal presentation preference
or one-off response strategy. A speaker label is not a verified identity or a verbatim
quote. An observed later edit is not proof that the advice caused the edit or acceptance.
Keep historical adoption states, especially partial and not-traceable, separate from
what is now independently checked.

### Novelty and motivation

Identify the innovation object: underlying mathematical operator, task-specific module,
architecture/interaction, empirical observation or deployment contribution. Trace closest
prior work and the implemented difference. Do not call a classical operator fundamentally
new merely because it is differentiable; equally, do not erase a supported architectural
contribution because its primitives are known. A vague "new mechanism" needs a specified
operation, difference and evidence. Revise introduction, contributions and conclusion
together when the contribution boundary changes.

### Counterintuitive ablation and mechanism

Lock the questioned table rows, comparator, metric direction and protocol before replying.
Present standalone harm and joint gain as observations first. Incremental and factorial
tables with different backbones or fixed modules are different contrasts, not interchangeable
replications. Explain why they can differ without inventing a causal explanation.

If two modules' joint effect is in question, a matched 2×2 contrast may discriminate
conditional effects. Do not demand all 2^k combinations by default. If stability across
seeds or order is the actual concern, one four-cell report does not answer it: seek
appropriate repetitions/order controls or explicitly limit the claim. Interpret positive,
non-positive and indeterminate outcomes before choosing the narrative.

Literature may motivate an upsampling/boundary or analogous mechanism, but does not
demonstrate that mechanism in this dataset. Separate definition/known operation from a
candidate explanation of the measured change. Suggest a mechanism-isolating test only
when it would resolve the disputed inference; no compulsory huge experiment catalogue.

### Fair comparisons and qualitative evidence

If a named baseline is unavailable, verify actual availability and date when making a
current claim; explain an appropriate substitution and its limitation. Do not label a
competitor lightweight from parameter count alone or claim its authors intended that
design without checking the source. Do not browse or disclose private manuscripts to
external services just to settle a public literature question.

For qualitative evidence, specify candidate pool, sample IDs, difficulty/selection rules,
crop, threshold and display mapping. Include informative failure/boundary cases when
relevant. More impressive examples are not an audit of representativeness; different
samples in two papers are not a controlled visual comparison. A recommendation to check
selection is not evidence the check was performed.

### Loss choices, efficiency and tables

A prior use of a loss supports precedent, not superiority. Explain task rationale and
the available controlled comparison. A DNC entry means non-convergence under the stated
setting, not intrinsic unsuitability; tuning/protocol fairness must be addressed before
generalizing. Best tested settings are not universal optima or statistical significance.

Show the task metric next to meaningful cost measures when the concern is accuracy versus
efficiency. Params/FLOPs are not latency; timing requires device, batch, input size,
precision, warmup, synchronization and measurement scope where applicable. Report the
actual trade-off and resource constraint, not an ungrounded deployment promise. Arrange
columns around the comparison task, preserve units and avoid fixed column-order mandates.

### Categories and subgroup claims

Resolve the basis for a partition before adding attractive plots: category definitions,
reference/selection rule, sample unit, membership, ambiguous cases and any stability
criterion that is actually claimed. Counts summing to N check arithmetic, not validity.
Frequency plots can illustrate a category but do not verify a classification procedure.
Distinguish a retrospective exploratory split from a prespecified test. Do not attribute
a later threshold/resampling algorithm to an earlier provisional mentor remark.

## Draft the formal response from completed work

Start the substantive answer with the questioned object and direct resolution. Then
state what changed, the decisive evidence/contrast, what it supports and the actual
manuscript location. Keep courtesy proportionate. Long digressions and empty thanks
do not improve responsiveness, but brevity cannot remove inconvenient evidence.

Use exact quoted revisions only when they match the delivered text. If the manuscript
has not been patched, label the passage and response as **proposed**, not "we have added".
If evidence is supplemental or response-only, name that location and do not imply it is
in the main paper. Do not invent page/line/figure/table numbers; leave a working location
unverified until it can be checked, and block a submission-ready claim until resolved.

Check the reply against every demand, including requests for uncertainty, code release,
failure cases or alternative order. A reassuring combination table does not automatically
resolve stability, causality and generalization concerns. Record partial resolution.

## Final revision-package audit

1. Bind the comment, evidence, manuscript source, rendered PDF and response to exact
   versions. Preserve files privately; no raw correspondence in a distributable Skill.
2. Walk each item: claim made in response → actual diff/passage → cited evidence → correct
   location. Reconcile section/table renumbering and highlighted versus clean variants.
3. Cross-check numerical changes, unfavorable metrics, notation, terminology, citations,
   units and contribution boundaries across abstract through conclusion and reply.
4. Render relevant supplied tables/pages when extraction interleaves columns or loses
   superscripts. A text parser does not certify layout or mathematical fidelity.
5. For an actual submission task, check the named venue's current official requirements
   for format, anonymity, supplements and disclosure. Do not assume another venue's rules,
   declare compliance without checks or submit without explicit authorization.
6. Report resolved, partially resolved, missing and inapplicable items with their reasons.
   Separate scientific quality, language fidelity, package consistency and engineering
   checks. Offline contract tests are not a peer review or a model-quality benchmark.

Before/after evaluation must inspect the actual revised argument and response, not the
presence of words such as gap, reviewer or limitation. Keep an unchanged positive control:
good bounded prose should survive the workflow without unnecessary rewriting.
