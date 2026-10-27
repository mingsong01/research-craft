# Research Software and Code

Read for scientific code, algorithm implementation, debugging, computational experiments, or performance engineering.

## Treat code changes as testable interventions

Establish an executable baseline and a failing or discriminative test before modification when feasible. Localize the mechanism, change the smallest surface, and compare against the same inputs, environment, and measurement definition. Separate correctness bugs, numerical issues, data issues, environment drift, and performance bottlenecks.

Use this four-phase debugging gate before proposing a fix:

1. **Root-cause investigation:** read the complete error/trace, reproduce it, inspect recent changes, and trace the bad value or state backward to its origin. Across component boundaries, record what enters, what exits, and which configuration/state was actually propagated.
2. **Pattern comparison:** find the nearest working example or authoritative implementation, read it completely, enumerate every relevant difference, and expose its dependencies and assumptions.
3. **Single-hypothesis test:** state one root-cause hypothesis and why the evidence supports it; make the smallest change or observation that can falsify it. If it fails, discard or revise the hypothesis rather than stacking another speculative fix.
4. **Minimal implementation:** first preserve a failing reproduction, then apply one root-cause fix and run the targeted test plus the relevant wider suite.

After three materially different failed fixes, stop. Reassess shared state, coupling, interfaces, and architectural assumptions before attempting another patch. Do not convert repeated guessing into an architectural rewrite without the user's authorization.

## Reproducibility

Record language/runtime, dependency and model versions, platform/hardware when material, random seeds, environment variables that affect behavior, command, configuration, commit, dirty state, and input identifiers. Prefer environment lockfiles already used by the project; do not introduce a new package manager only for record keeping.

Control nondeterminism or quantify it. Check numerical tolerance, floating-point precision, parallelism, device kernels, caching, warm-up, and hidden global state when relevant. A fixed seed does not guarantee deterministic execution.

## Computational evidence attribution

A tolerance specified before execution is prespecified; describe it as preregistered only when a registration record supports that status.

Keep implementation state separate from execution evidence. Report the strongest supported stage and do not promote it:

1. `DESIGNED`: an algorithm, patch, or experiment is specified but not implemented;
2. `IMPLEMENTED`: attributable code exists, but execution is not evidenced;
3. `EXECUTION_REPORTED`: a person or prior note says it ran, without inspectable run artifacts;
4. `ATTRIBUTABLE_RUN_EVIDENCE`: command/configuration, code identity, inputs, environment, and outputs can be linked to the same run;
5. `INDEPENDENTLY_REPRODUCED`: a fresh execution under stated conditions reproduces the decision-relevant result.

Before treating a computational result as evidence, reconcile the exact code variant or commit, dirty state, configuration, command, data/split identifiers, seed, environment, output artifact, and metric implementation. A code file that appears capable of producing a result is not run evidence; a detached log or result table is not attributable until its producing configuration and code identity are linked. If only a weaker stage is available, state that boundary and name the smallest missing artifact needed for the next stage.

## Verification ladder

Use the smallest sufficient combination of unit tests, property/invariant tests, integration tests, regression fixtures, differential checks against a trusted implementation, static analysis, and end-to-end tests. For scientific algorithms, include boundary, degenerate, adversarial, and conservation/unit checks where applicable.

Benchmarks must preserve correctness and define workload, timer boundaries, warm-up, repetitions, aggregation, environment, and uncertainty. Faster incorrect code is not an improvement. After implementation, connect the changed files, reason, decision, tests, metrics, and remaining limitations in the research trail.

Before claiming completion, identify the command or inspection that proves each claim, run it fresh and completely, read its exit status and failures, and report the observed result. A prior run, partial linter, successful build, generated file, or confident explanation is not completion evidence. For a regression test, demonstrate the red-green relationship when practical: the test must fail without the fix for the expected reason and pass with the fix; then run the relevant full suite.
