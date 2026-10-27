# Scientific writing: diagnose, revise and verify

Use for research manuscripts, substantive academic translation and section/paragraph
revision. Evidence statuses and reviewer tracking remain in evidence-writing.md.
Do not load this for ordinary editing unless research rigor is requested.

## Establish the revision contract

Identify the requested section, reader, scientific purpose, source version and output
language. Use the smallest supplied evidence set: relevant passage, neighboring argument,
method/result/table sources and the actual concern. Do not ingest the entire corpus for
one sentence; widen the window when a premise, term or cross-reference cannot be checked.
Missing context is an explicit unresolved item, not permission to invent a connection.

Separate two revision modes, and disclose a mixed change:

- **LANGUAGE:** preserve propositions, operations, numbers/units, negation, quantifiers,
  conditions, comparison sets, citations and degree of certainty. Improve expression only.
- **SCIENTIFIC:** change claim, explanation, comparison or structure only with an identified
  reason and supporting evidence. Label a new inference as interpretation; isolate a
  proposed experiment from an executed action. Do not smuggle this change into polishing.

For a substantial passage, write a compact diagnosis before revising: location → intended
paragraph function → actual claim/premise/evidence → missing or invalid link → minimal
repair → revised text → source and meaning check. This is a reasoning record, not a
mandatory long form for a simple edit. Keep effective original prose; make no edit when
the statement is already accurate and suitable. Do not turn every section into a warning.

A paragraph can orient, establish a gap, motivate a design, define an operation, report
an observation, compare, explain or delimit. Give it a dominant scientific job. Check
whether each sentence advances that job and whether the last sentence licenses the next
paragraph. Repair a missing premise or misplaced result before improving transitions.
Words such as therefore cannot supply absent evidence.

## Section diagnosis and smallest effective repair

### Abstract

- Purpose: make the problem, specific response, decisive evidence and bounded implication
  intelligible without the paper. Order and sentence count depend on the study and venue.
- Diagnose: generic significance instead of the actual problem; module inventory without
  a design rationale; a result without comparator/protocol; stronger scope than the body.
- Repair: replace one unsupported broad gap with the documented failure condition; connect
  the method to that condition; select the result that answers the question, retaining
  its dataset/metric/unit and exception when consequential. Do not cram every metric in.
- Language: direct task and method verbs, precise objects and consistent tense. Remove
  repeated adjectives and unsupported priority words; keep a supported novelty statement.
- Check: every number and contribution resolves to the final body; an abstract-only
  result or new implication stays unresolved. Judge explanatory completeness, not length.

### Introduction

- Purpose: establish importance → what is already possible → a specific unresolved
  problem → why the proposed response addresses it → testable, bounded contributions.
  This is an argument dependency, not a fixed number of paragraphs.
- Diagnose: "all existing methods fail" from selected papers; a gap consisting only of
  "no one combined these modules"; motivation inferred retrospectively from the final
  architecture; contributions merely naming components.
- Repair: identify the evidence-backed failure condition and the closest competing
  capability; explain the design difference that targets the condition; state what the
  experiments can discriminate. Unknown priority remains unknown pending source work.
- Language: use concrete limitations and technical nouns rather than superiority
  adjectives. Distinguish a known operator, a task-specific module and a new principle.
- Check: remove the proposed method temporarily: does the gap still describe a real
  scientific need? Does each contribution have an actual evidence path? Keep chronology
  honest; a later explanation is not proof of an original prespecified hypothesis.

### Related Work

- Purpose: classify relevant approaches by scientific principle and compare the choices
  that matter to the paper, rather than produce a chronological list of summaries.
- Diagnose: categories overlap without explanation; criticism based on titles; methods
  called lightweight or prior-free without checking their authors' claims; a straw-man gap.
- Repair: choose a comparison axis such as assumptions, representation or trade-off;
  place the nearest alternative; support each substantive limitation with the primary
  source and its scope. Mark papers not inspected instead of inventing evaluations.
- Language: separate what another paper reports from this manuscript's comparison.
  Describe an architectural difference without implying an unmeasured performance deficit.
- Check: the taxonomy leads to the actual research question; the proposed method receives
  the same qualification standard as competitors. Use literature-frontier.md if search is needed.

### Method

- Purpose: explain the overall computation, each necessary module and why it is used.
  Establish input/output, operations, symbols, assumptions and interactions before claims.
- Diagnose: equations do not implement the described operation; missing normalization
  axis, boundary/padding, stage or training/inference condition; rationale presented as
  proven mechanism; diagram and forward path disagree.
- Repair: reconstruct the operation from the available code/formula and name unresolved
  choices. Define an overloaded symbol or insert the missing dependency; preserve formula
  semantics during language edits. Do not invent dimensions or a branch to complete prose.
- Language: pair purpose with an exact operation; keep explanatory analogy separate from
  mathematical definition. Do not rewrite established technical terms for synonym variety.
- Check: text ↔ formula ↔ figure ↔ configuration/implementation, with evidence type stated.
  If only a schematic is supplied, implementation agreement remains unverified.

### Experiments

- Purpose: show which experiment answers which claim, with adequate controls and
  reproducible reporting. A result table alone does not define an experimental design.
- Diagnose: treatment changes optimizer and module together; seed/split/checkpoint/evaluator
  or analysis unit absent; selected hyperparameters evaluated on the selection set without
  disclosure; extra experiments unrelated to the uncertainty.
- Repair: specify the target contrast and existing settings; separate confounded results
  from a proposed controlled rerun; report missing facts explicitly in the working audit.
  Identify training repetitions versus repeated images, and exploratory versus confirmatory work.
- Language: executed methods in past tense where appropriate; planned runs in future or
  conditional form. Do not convert "reported" evidence into an independently reproduced run.
- Check: comparator fairness, units, hardware/timing definition, denominators, controls,
  decision criterion and uncertainty. Reuse workflow/statistics references for deeper design.

### Results

- Purpose: give the decisive observation, relevant comparison, magnitude and trade-off
  before explanation. Organize around questions, not every table row in sequence.
- Diagnose: all/best/stable claims despite an unfavorable metric; mixed baselines;
  percentage points confused with percent; a single run described as robust or significant.
- Repair: pair rows under the same protocol, compute the correct contrast and name the
  exception. Distinguish the final configuration from each incremental step. Report an
  observed combination gain without claiming a stable interaction or isolated mechanism.
- Language: identify subject, comparator and direction; use "in Table..." only with a
  verified location. Avoid a vague "performance improved" when the metrics disagree.
- Check: the text reproduces the supplied values, direction, scale and comparison set.
  An unfavorable result must not disappear merely because a revision becomes shorter.

### Discussion

- Purpose: interpret what the observations support, contrast plausible explanations,
  connect to prior work and define the scope of implications.
- Diagnose: a plausible mechanism stated as established; an external paper used to prove
  causality in this experiment; correlation or low p treated as mechanism evidence;
  no explanation of counterintuitive or non-positive results.
- Repair: separate observation → compatible explanation → rival/confound → discriminating
  evidence still needed. Keep an evidence-supported explanation; do not mechanically hedge
  definitions, established mathematics or genuinely isolated causal results.
- Language: certainty follows the source, not a fixed list of forbidden words. A concise
  qualification can bound a claim more clearly than adding "may" to every sentence.
- Check: a rival result would change the interpretation; clinical/domain/generalization
  claims do not exceed the population or evaluation actually studied.

### Limitations

- Purpose: identify the specific conditions under which a result or inference may fail.
- Diagnose: generic future work replacing a present weakness; seed/protocol/subset selection
  uncertainty omitted; an internal missing-log audit exaggerated into proof no experiment ran.
- Repair: name the actual design/evidence boundary and its consequence for interpretation;
  propose the smallest useful follow-up separately. Do not add invented weaknesses merely
  to create a balanced-sounding section.
- Language: concrete scope statements rather than self-denigration or defensive claims.
- Check: each limitation has a reason and constrains a specific conclusion; no claim of
  exhaustive robustness or applicability survives an unresolved relevant boundary.

### Conclusion

- Purpose: answer the original research question at the strength actually earned,
  distinguish current contribution from future directions and end without new evidence.
- Diagnose: universal robustness, theoretical optimality or fundamental novelty added
  only at the end; a contribution scope narrower in the response than in the manuscript.
- Repair: retain the demonstrated result and design object, remove unsupported extension,
  and state a relevant open direction without promising its outcome.
- Language: concise synthesis, not repeated abstract text or a list of module marketing names.
- Check: contribution, scope and numerical facts agree with abstract, results, limitations
  and the final response. A new conclusion claim requires evidence, not stylistic approval.

## Academic English and bilingual fidelity

1. Before translating, identify load-bearing propositions and terminology: actor/object,
   operation, relation, negation, quantifier, condition, number/unit, citation and certainty.
   Preserve anchors verbatim where required; keep an agreed glossary for recurring terms.
2. Draft natural target-language prose: explicit subject/verb, clear technical referents,
   conditions adjacent to the result they restrict, parallel comparisons. Split a long
   sentence when it resolves a scope ambiguity, not to enforce a sentence-length rule.
3. Compare source and target proposition by proposition. "No significant difference"
   is neither "no difference" nor "equivalent"; "only when" is not "whenever";
   "not necessarily" is not "does not"; tested-best is not globally optimal.
4. Check numbers, inequality signs, ranges, exponents, percentages/percentage points,
   singular/plural and formula variables independently. Do not silently normalize
   inconsistent source values; flag them and offer a conditional corrected version.
5. Check collocations and article/preposition/tense choices after scientific fidelity.
   Remove literal translation and empty nominal chains while preserving emphasis and
   causal direction. Do not substitute "proves" for "suggests" to sound more academic.
6. Separate a meaning correction from a language improvement in the change explanation.
   Back-translation can expose drift but is not sufficient proof of equivalence. Keep
   a scientific question unresolved rather than choosing the most fluent interpretation.

For LANGUAGE-only work, do not add experiments, numbers, references or limitations absent
from the supplied meaning. If a scientific defect becomes apparent, show the faithful
language edit and a separately marked scientific correction proposal.

## Final consistency and quality review

Freeze the manuscript/source/PDF/response version IDs or hashes. Audit consequential
claims across abstract, method, captions, tables, discussion, conclusion and response.
Record real locations in that exact version; an old page number is not a current one.
If TeX and PDF differ, first determine which is the intended master; do not silently
merge or call the mismatch a proven submission error.
An apparently missing equation value in extracted PDF/Word text can be a parser omission
(for example, an OMML math run). Check the native object or rendered source before
diagnosing missing author data; flat text does not certify subscripts or formula structure.

Evaluate actual before/after passages on: scientific validity and evidence fit; argument
continuity and paragraph function; technical specificity; semantic fidelity; natural
academic language; scope and cross-document consistency. Cite a concrete edit or preserved
sentence for each judgment. Keyword presence, shorter length and fluent grammar are not
writing-quality tests. Same-author self-review is useful but is not independent evaluation.

Sources: conditional procedures distilled from a single project's version/reviewer and
provisional speaker-labeled guidance records. Maintainer evidence maps are kept outside
the distributable Skill. No universal advisor authority or proven cross-project efficacy
is inferred; project-specific numbers, speaker identities and column orders are not rules.
