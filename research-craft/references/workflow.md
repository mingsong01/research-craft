# Workflow Reference

Read this reference for non-trivial diagnosis, experiment design, implementation, or technical decisions.

## Frame

Capture only what changes the next action:

1. Research question or actual problem.
2. Expected and observed behavior; define the gap.
3. Existing evidence and material unknowns.
4. Candidate causes, including alternatives to the user's first explanation.
5. Observation that would support and observation that would contradict each serious hypothesis.

For diagnosis, follow `Expected -> Observed -> Gap -> Candidate causes -> Existing evidence -> Isolation test -> Root cause -> Fix -> Regression`. Rank tests by information gain divided by cost and risk. A test is useful when its possible outcomes distinguish candidate causes.

Freeze the observation before interpreting it: source or measurement, population/system, unit of observation, unit of analysis, uncertainty, exclusions, preprocessing, and whether it was expected or discovered after inspection. Keep observation, research question, hypothesis, mechanism, prediction, alternative explanation, and evidence as different objects.

Generate credible rivals before choosing a test. Include the proposed mechanism and, when plausible, measurement/processing artifacts, confounding, selection or attrition, reverse causation, context or boundary effects, stochastic variation, and competing mechanisms. For every serious candidate, specify:

- a discriminating prediction made before checking the target result;
- the observable and how it will be measured;
- a result that would count against the candidate under stated assumptions;
- an indeterminate result and what it would still teach;
- at least one rival that predicts a meaningfully different outcome.

Failure of one rival does not prove the survivor. Preserve unconsidered alternatives and auxiliary assumptions as limitations.

## Experiment contract

Before a FORMAL run, record question, hypothesis, baseline, changed variable, controlled variables, primary metric with unit/direction, decision criterion, expected observation, falsifying observation, and analysis plan. Add dataset, split, preprocessing, seed, environment, evaluation code, and commit when relevant. Run `research.py experiment validate --id <ID> --level formal` before execution. If important conditions differ materially, label the comparison `NOT DIRECTLY COMPARABLE`.

### Design reality gate

Do not run until the design is classified `READY`, `PILOT ONLY`, or `NOT READY` by answering:

1. Is the question measurable and would the result change a decision or claim?
2. What is the experimental unit, treatment-assignment unit, observation unit, and analysis unit?
3. Are replicates independent at the treatment-assignment level, or is this pseudoreplication—repeated observations being mistaken for independent replication?
4. Are treatment and seed, batch, day, operator, site, device, checkpoint, run order, or data split confounded?
5. Is the baseline concurrent, relevant, and evaluated under the same workload and measurement definition?
6. What nuisance factors require randomization, blocking, stratification, counterbalancing, or masking?
7. Can the design distinguish the leading hypotheses, including important interactions?
8. Is a cheaper pilot or isolation test sufficiently decisive?

Use randomization to balance uncontrolled causes in expectation, replication to estimate variability at the correct independent level, and blocking/local control to remove known nuisance variation. Preserve the generated allocation or run order and its seed. Match the analysis to blocks, clusters, nesting, repeated measures, and split-plot structure; analysis cannot repair a structurally confounded design.

For factorial work, decide whether the question concerns a main effect, marginal contribution, interaction, screening, or response-surface behavior. Do not infer an independent module contribution from `Full vs Without` when the effect can depend on other modules. Do not use a two-level design to claim an interior optimum or curvature.

After the run:

- validate raw output and measurement provenance before explanation;
- preserve `raw -> processed -> metrics -> analysis` lineage;
- retain failed runs as evidence;
- examine trend, trade-off, stability, failure mode, cost, robustness, scope, and limitations;
- state `Can Claim` and `Cannot Claim`;
- label post-result explanations `exploratory interpretation`.

Separate `ENGINEERING_VALID` from `CLAIM_ELIGIBLE`. A script that runs, a test that passes, or a favorable point estimate may establish engineering behavior without supporting the scientific claim.

Do not choose tests only after seeing which result is favorable. If the analysis changes after results are visible, preserve the original plan and label the new analysis exploratory. Separate statistical significance, effect magnitude, practical importance, and causal interpretation.

Ablations should answer the question, not mechanically enumerate combinations. Use individual, pairwise, interaction, or full variants only when they discriminate plausible explanations. Sensitivity analysis supports "best among evaluated settings," and should inspect trend, plateau, neighbor stability, degradation, and trade-offs.

## Solution and change

For important choices, compare at least A and B against correctness, performance, security, complexity, cost, compatibility, risk, and validation. Add C only if it is genuinely distinct. Prefer the minimum effective change. Record a decision only when a future collaborator may reasonably ask why it was made.

Implementation is not completion. Check: issue resolved, prior behavior intact, metrics not regressed, relevant tests pass, documentation and tracked claims remain consistent.

## Stop rule

Say `Evidence sufficient for current purpose` when the scoped decision or claim is supported. Continue only if a feasible next observation would materially change the decision, claim strength, or risk. Do not optimize for experiment count.
