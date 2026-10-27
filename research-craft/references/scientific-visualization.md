# Scientific Visualization

Read when creating or auditing plots, figures, tables, diagrams, or visual explanations.

## Start from the scientific question

Choose the visual by the comparison: distribution, change over time, relationship, composition, spatial pattern, uncertainty, ranking, or model diagnostics. Do not select a chart because it looks impressive. Use a table when exact values matter more than shape.

## Integrity

- Preserve units, sample sizes, denominators, transformations, aggregation, and uncertainty definition.
- Use common scales for direct comparisons; disclose truncation, log scales, smoothing, normalization, and excluded observations.
- Show raw observations or distributions when aggregation could hide heterogeneity. Use intervals or distributions instead of unqualified error bars.
- Avoid dual axes, 3D decoration, area/volume encodings, rainbow maps, and visually amplified differences unless scientifically necessary and clearly justified.
- Distinguish missing, zero, below-detection, and not-applicable values.

## Reproducibility and accessibility

Generate publication figures from data with a saved script or declarative specification when possible. Record source experiment/data, filter, aggregation, plotting command/script, software version, and output path in `figure_table.csv`. Use readable typography, color-blind-safe palettes, sufficient contrast, redundant encodings, and captions that state what is shown without overstating why.

Before delivery, verify labels, units, legends, ordering, uncertainty, numerical agreement with registries, raster/vector suitability, and readability at final publication size. A visual is evidence presentation, not evidence by itself.

Use `design -> generate -> export -> render -> inspect -> repair -> rerender`. Inspect the delivered format, not only the plotting canvas. Verify physical dimensions, fonts, embedded raster resolution, clipping, transparency/background behavior, grayscale separation, redundant non-color encodings, and the actual target-journal requirements as of the access date. Automated palette or metadata checks are screening aids, not accessibility or publisher-compliance certificates.

Prefer editable vector output for line art and diagrams; use an explicit high-resolution raster only when the data or submission rules require it. Refuse implicit overwrite for formal outputs when practical, and write provenance alongside the artifact rather than embedding private source data into it.

For a scientific model, neural-network architecture, computation graph, or method/system framework diagram, read [scientific-diagram-design.md](scientific-diagram-design.md) before drawing. Its topology contract, boundary-port routing, deterministic SVG checks, and render-inspect-repair gate are mandatory for that artifact family.
