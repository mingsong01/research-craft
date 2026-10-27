# ML and Computer Vision Checks

Read only for ML/CV experiments.

- Verify train/validation/test separation, leakage, split identity, preprocessing, augmentation, class balance, seed, checkpoint selection, epochs, model size, and evaluation code.
- Compare baselines under the same data, training budget, parameter accounting, and metric definition.
- Report parameters/FLOPs and latency only with their measurement methods and environment.
- Use error cases, subgroup analysis, robustness checks, and repeated seeds when they answer the research question.
- Choose ablation variants to isolate module effects and plausible interactions; avoid an exponential grid without decision value.
- For sensitivity, report the evaluated range, trend, plateau, neighboring stability, degradation, and cost trade-off. Claim only "best among evaluated settings."

Define the independent experimental unit: seed, training run, fold, dataset, subject, site, or deployment interval. Image-, patch-, query-, or token-level observations nested inside one run are not independent training replicates. Pair seeds/splits across methods when appropriate and preserve the pairing in analysis.

Separate model-selection evidence from final test evidence. Do not tune architecture, checkpoint, thresholds, prompts, retrieval settings, or preprocessing on the final test set. Report whether the chosen checkpoint/epoch was selected per run or globally and whether all baselines received comparable search budgets.

For classification/detection/segmentation, inspect calibration, threshold dependence, class/subgroup performance, prevalence sensitivity, and error cases when they affect use. For deployment claims, measure end-to-end latency/throughput, memory, energy or cost under the actual batch size, precision, device, concurrency, and warm-up—not only FLOPs or kernel time.
