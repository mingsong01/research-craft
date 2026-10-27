# Statistics, Causality, and Quantitative Reasoning

Read for quantitative experiments, statistical claims, causal language, uncertainty, or formal derivations.

## Define the target

State the population, unit of analysis, estimand, intervention/exposure, outcome, time horizon, and decision the estimate informs. Distinguish descriptive, predictive, explanatory, and causal questions; their evidence requirements differ.

## Design before inference

- Identify sampling, assignment, repeated measures, clusters, censoring, missingness, exclusions, and stopping rules.
- Prefer randomization or a defensible identification strategy for causal claims. Name confounders, mediators, colliders, selection effects, spillovers, and interference when relevant.
- Check independence, distributional, linearity, variance, measurement, and model-specification assumptions. Use diagnostics or robust alternatives rather than silently assuming them.
- Define the primary outcome and analysis before observing results. Label post-hoc subgroup, metric, threshold, and model choices exploratory.

Before selecting a named test or model, determine the outcome scale, number and dependency of groups, pairing/repeated measures, clustering/nesting, censoring, distributional shape, sample size, missingness mechanism, and target contrast. A familiar test is not valid merely because the data type appears to match. Preserve the design structure in the analysis.

Run diagnostics appropriate to the model rather than treating a normality test as a universal gate. Inspect residual structure, variance, functional form, influential observations, dependence, separation/identifiability, convergence, and calibration as applicable. If an assumption is materially violated, report the planned analysis, the observed failure, the justified robust/non-parametric/transformed/model-based alternative, and how interpretation changes.

## Report evidence, not just p-values

Report sample size, effect estimate, uncertainty interval, units, direction, practical threshold, missing/excluded observations, and analysis method. Treat statistical significance, effect size, practical importance, and evidence for a mechanism as separate questions. Correct or disclose multiplicity when many hypotheses, metrics, subgroups, or checkpoints were inspected.

Do not interpret failure to reject as proof of equivalence. Equivalence or non-inferiority needs a prespecified margin and suitable design. Avoid retrospective power calculations; use prospective precision/power reasoning where it changes design.

Define the smallest effect size of interest or practical decision threshold before using terms such as meaningful, negligible, equivalent, or non-inferior. Report exact estimates and intervals even when threshold decisions are required. Do not let a statistically significant trivial effect outrank a practically important uncertain effect, and do not let a wide interval masquerade as evidence of no effect.

For Bayesian work, state the model, priors, likelihood, convergence and predictive diagnostics, interval convention, and the exact posterior quantity answering the question. A Bayes factor or posterior probability inherits the model and prior assumptions; it is not assumption-free evidence.

## Robustness

Use sensitivity analyses that target material assumptions: alternative specifications, outliers, missing-data handling, clustering, seed variation, negative controls, placebo tests, or bounds. Do not multiply analyses merely to find a favorable result.

For mathematical or algorithmic claims, state assumptions, derive steps, check dimensions/units, test boundary and degenerate cases, and use a small numerical verification when useful. A numerical check supports a derivation but does not replace proof.

Use multiplicity control or an explicitly hierarchical analysis when many outcomes, groups, subgroups, checkpoints, seeds, or model variants create multiple opportunities for a favorable result. Distinguish prespecified primary evidence from sensitivity, exploratory, and discovery analyses in both records and prose.

## Causal language gate

Use causal language only when the design and assumptions identify a causal estimand. Otherwise say association, prediction, or consistency with a mechanism. Explicitly list plausible alternative causal structures and the evidence that would distinguish them.
