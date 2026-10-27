# Model architecture design: evidence, composition and proof

Use for paper model schematics, after scientific-diagram-design.md establishes the
topology contract. It is a design workflow, not a promise of automatic code recovery.
Use the existing FigureSpec/SVG/draw.io path; no new service or dependency is required.

## From code to a visual argument

1. Identify the actual forward entry, configuration and conditional execution. Follow
   instantiated modules and tensor producers/consumers, including functional operations,
   shared weights, reshapes, tokenization, scale changes, gates and loss-only branches.
   A class list or model name is insufficient. If safe local tracing already exists, use
   it alongside the source; do not run untrusted training code just to draw a diagram.
2. Write a node/typed-edge contract **before** layout. Record file/line/config evidence,
   exact operations and tensor shapes where known. Label unknown internals UNKNOWN.
   Separate a documented scientific fact from a visual abstraction or a design choice.
3. Decide what the figure explains: global feature flow, a scale hierarchy, an interaction,
   or the proposed mechanism. Use an overview and a separate detail panel if internals
   matter. A novelty accent on an opaque box is not an explanation of that mechanism.
   Without internal evidence, retain the opaque box and disclose the missing detail.
4. Freeze the contract. Compare at least two materially different compositions for a
   complex graph: different orientation, scale arrangement, panel allocation or branch
   organization. Recoloring or moving one box is not a second composition. Both must
   preserve exactly the same science. Record the choice using the five dimensions below.

## Choose a scientific graphic language

| Architecture | Useful expression | Evidence required / common failure |
|---|---|---|
| CNN / feature backbone | Feature volumes or maps for **representations**, compact operation bars for convolution/pooling; stage bands and explicit resolution labels | Volume sizes are symbolic unless mapped to actual dimensions; never claim channels from drawn depth. Avoid pseudo-3D on every computational block. |
| Encoder–decoder / U-Net | Descending and ascending scale hierarchy; align corresponding scales; reserve lateral skip lanes; explicit concat/add operator | Verify crop, resize and projection before fusion. A U shape does not prove that corresponding feature sizes agree. |
| Transformer | Overview of stages plus block detail; token sequence versus spatial feature grammar; normalization order, attention and MLP; separate residual entry ports | Do not guess head count, windowing, pre/post norm or repeated blocks. Attention arrows must match the actual queries/keys/values if these are drawn. |
| Mamba / SSM | Separate local mixing, state/scan branch, gating and projection; show scan direction or 2D flatten/restore only when evidenced | A rectangle named Mamba does not explain the mechanism. Do not import reverse scan, selective parameters or MambaVision's split from the name alone. |
| Multimodal | Distinct input lanes with stable semantic colors and explicit condition-injection ports; representation glyphs differ from compute modules | Do not imply cross-attention, shared encoders or symmetric interaction without evidence. Unknown fusion stays a named module, not an invented plus/concat. |
| Multiscale / pyramid | Resolution rows or a scale axis, lateral/top-down routes distinguished spatially; local inset for resize/fusion if needed | Keep feature scale and stage order separate. Label learned projection, interpolation and aggregation accurately. |

Use flat semantic color: neutral ink for ordinary compute, blue/teal for distinct
modalities or stage families, one restrained warm accent for the focal mechanism.
Assign meanings per figure and preserve them across panels. Text, position, labels and
line style must carry meaning when color disappears. Depth faces may clarify a feature
volume; gradients, shadows and decorative icons are not evidence of quality.

### Observable methods by architecture family

Apply these as conditional design decisions, not one template for every network.
Source links and exact figure/page observations appear in the source table below.

- **Encoder–decoder — U-Net Fig.1.** Its spatial levels descend and ascend while
  corresponding copy/crop routes run horizontally. First assign each evidenced spatial
  resolution a row; place encoder and corresponding decoder outputs on that row; reserve
  a skip lane before placing labels. Use shallow feature planes/volumes for outputs and
  compact, different shapes for fusion operators. One family color per side can guide
  reading; labels and row positions must survive grayscale. If a crop/resize is required,
  show it only from evidence. An ordinal decrease in drawn size must be captioned as
  schematic; it is not a calibrated H/W/channel plot. Prefer flat maps when depth adds
  no channel information or makes stage labels smaller.
- **Transformer — Swin Fig.3.** The original separates a stage overview from local
  attention/norm/MLP detail and writes repeat ranges outside blocks. Establish the stage
  reading direction first, then devote detail space to the actual changing mechanism;
  residuals get separate operator ports rather than ending on an arbitrary box side.
  Token strips distinguish sequences from spatial maps. Choose color by operation or
  stage family, and explicitly state which; keep norm order and repeats in text.
  Do not turn attention, normalization or an MLP into a 3D volume merely for decoration.
  Q/K/V, windows and head counts need implementation evidence, not analogy to Swin.
- **Mamba/SSM — MambaVision Fig.3.** The inspected figure distinguishes its branch
  containing SSM from a branch without SSM, then explicitly concatenates them. The
  transferable method is branch alignment, compact operation vocabulary and an explicit
  fusion symbol, **not** that scientific topology. Trace scan direction, gate activation
  and aggregation from the target model; place branches in aligned lanes and use color
  consistently for operation families or state versus gate. Show flatten/restore or
  multidirectional scan in a detail panel only when it is evidenced. A state path is
  better expressed as a sequence/scan than a spatial cuboid. The local `ssm-gating`
  example has a separate synthetic multiply contract; it does not reconstruct this paper.
- **Multimodal — SAM Fig.4.** The original has an asymmetric image backbone and prompt
  injection, distinct embedding glyphs and separate outputs. Allocate space by explanatory
  importance, not equal-size boxes. Preserve lane identity into the actual interaction;
  label a bypass with its source and the operation bypassed. Use spatial-plane versus
  horizontal word-piece-like glyphs for different representations, without inventing
  token contents. A role header can make the proposed module distinct from its name,
  but is not an internal mechanism diagram. Prefer 2D tokens and compute modules when
  spatial depth is unknown. Never imply that all multimodal models are symmetric or
  that an unspecified fusion means cross-attention.
- **Multiscale fusion — FPN Fig.2/3.** The inspected overview aligns scale levels; the
  local inset labels 2x up, 1x1 projection and an explicit **addition**. Place lateral
  inputs at corresponding scales, put the fusion where the paths actually meet and
  annotate resize/projection locally. Use one restrained color for the scale family or
  path role, not arbitrary new colors for every level. Write Concat when the target
  contract says concat: do not transplant FPN's plus symbol. Flat planes often explain
  pyramids more compactly than equal-size 3D boxes. Use volume depth only if the figure
  needs and can support a clear channel-axis meaning.

Do not use 3D feature blocks for scalar losses, gates, residual addition, attention
operators, text tokens or unknown internals. Also avoid them when perspective masks
connections, implies unverified channel growth, or collapses at the final paper size.
These are decisions about semantic suitability; a shallow symbolic volume remains a
valid option when its role and limitations are explicit.

## Existing renderer: optional publication grammar

`demo/publication/` provides editable JSON, independent topology contracts and SVGs.
Regenerate an individual example with the existing renderer CLI:

```text
python scripts/vendor/figure-spec/figure_renderer.py validate demo/publication/multimodal-A/figure-spec.json
python scripts/vendor/figure-spec/figure_renderer.py render demo/publication/multimodal-A/figure-spec.json --output figure.svg
python scripts/diagram_svg_qa.py lint figure.svg --spec demo/publication/multimodal-A/topology.json --width-mm 180 --json
node scripts/bybit_svg_profile.mjs figure.svg
```

- `representation: feature-map | tokens` adds editable SVG paths **inside** a rectangular
  node. The counts are symbolic, not actual channels or tokens; say so in the caption.
  Validation rejects unknown glyphs and insufficient vertical room. This does not add
  scientific nodes. Use source labels to distinguish a computation from its output.
  `representation_style: semantic` optionally gives feature planes a spatial grid and
  tokens horizontal word-piece-like tiles; `classic` remains the default. These are
  schematic glyphs, not activations, tokenizer internals or quantitative token counts.
- `shape: tensor` draws a projected feature-volume silhouette with exact boundary clipping
  and plain SVG faces. Use it for a representation, label its producing stage clearly,
  and declare symbolic sizes unless calibrated. No external image or proprietary font.
- `emphasis: true` adds an internal accent. It indicates a declared focus, not proof of
  novelty. It must never conceal a missing mechanism explanation.
  Alternatively, `header` adds one role line and a divider **inside the same plain
  rectangular node**. It rejects multiline, over-wide, too-short or glyph-combined
  specifications. It adds neither submodules nor topology; use existing text color
  for readable small headers rather than relying on a pale accent stroke color.
- A start-anchored free label may use `line_style: solid | dashed | dotted` to draw a
  matching editable line sample before its text. The sample is decoration, not an edge.
  Keep the legend's color/style meaning consistent with actual paths.
- Edges optionally accept `source_port` / `target_port` objects with `side` and `offset`.
  Offset 0..1 follows left-to-right on top/bottom and top-to-bottom on left/right.
  Nonrectangular shapes require the cardinal center (0.5); explicit self-loop ports
  are rejected. Place waypoints along the selected side normal, then run geometry QA.
  Wrong-side/diagonal approaches are not automatically repaired.
- `label_segment: longest-horizontal` anchors a waypoint label to the longest horizontal
  segment. It errors if none exists. It does not measure whether the text fits the
  segment or clear neighboring nodes: native rendering and lint remain necessary.
- Missing optional fields preserve the old output. Schema 1 and old node/edge contracts
  remain compatible. Curves/rotated/nonuniformly scaled scenes retain the earlier QA
  limitations; a new shape is not permission to bypass those checks.

For editable draw.io, preserve explicit ports, scientific IDs and waypoints; use the
existing allocator and validator. SVG→draw.io conversion has not been certified here.
Use the available editor only when its import preserves semantics and editability.

## Five independent acceptance dimensions

| Dimension | Inspect / evidence | Failure response |
|---|---|---|
| Scientific topology, hard gate | Source-backed contract; all nodes, typed routes, real operators, scale and train/inference conditions. Local QA plus manual graph walk. Contract-only proof must be labeled as such. | Fix the diagram or mark unresolved; aesthetics cannot compensate. |
| Information expression | Identify inputs, dominant path, scale/modality meaning, fusion inputs, focal mechanism and outputs without hunting through the caption. Compare A/B on these reading tasks. | Reorganize lanes/panels; expand a real mechanism; retain UNKNOWN rather than invent. |
| Visual design | Actual renders: hierarchy, alignment, rhythm, label spacing, route clarity, restrained palette, grayscale distinction, useful whitespace. Describe concrete defects and local repairs. | Change geometry/typography, then rerender. Do not score from an SVG lint result. |
| Publication fit | Named target width, legible text/strokes/arrows, no crop/overflow, editable source and matching vector PDF; check color and grayscale at final size. | Reflow/split, enlarge or change target format. Never shrink below the declared screen to obtain a pass. |
| Editability | SVG groups and stable scientific IDs, native text and vector paths, valid FigureSpec; edit a copy of a label and rerender to check the change takes effect while the contract remains intact. PDF alone is not the editable master. | Keep/repair source objects; do not flatten to an image or claim an untested editor round trip. |

Run technical geometry checks alongside all five dimensions; keep their results distinct.
For browser text measurements, inspect actual glyph bounds and containment. A symbolic
glyph above a centered text block can legitimately make the **text alone** off-center;
retain any lint warning and explain it with the complete rendered node. Do not disable
the rule globally. Row size differences may encode stage roles; accidental differences
still need repair. Absence of a lint error does not prove adequate whitespace.

At final width, review both a 96 dpi preview at native pixel size and a 300 dpi render;
inspect grayscale. Export PDF from the vector source and independently rasterize it
when a local renderer exists. Record unavailable font/print/color-vision checks, never
substitute static SVG validation for a visual review. A 300 dpi screen image is not an
actual print test. Preserve the before image, both candidates and the selected revision.

Use a defect ledger for a bounded revision: **observed defect → semantic/design intent →
specific change → before/after render → remaining limitation**. For visual acceptance,
answer the reading tasks with actual objects: can one identify the representation type,
dominant path, focal module and exact fusion without guessing from color or a lone
letter? Are repeated roles aligned, operator shapes distinct, and headers subordinate
to module names? Does whitespace clarify grouping rather than merely enlarge the image?
Record a concrete observation, not a generic "looks professional" verdict.

Measurable proxies can support this review: unchanged node/typed-edge sets, equal y at
matched scales, ordered feature-block sizes when declared ordinal, figure area per fixed
contract at the same physical width, actual font/line bounds, and successful editable
label regeneration. None measures aesthetic quality on its own. Do not optimize density
by shrinking text, nor call a synthetic contract PASS a real-model correctness result.

## Original-paper observations used in this increment

These are observations of the actual original figures, not proof that their full visual
styles are optimal. Learn composition; do not copy artwork, photos or scientific content.
Paper/author images stayed in internal validation, not the distributable Skill.

| Source / inspected figure | Observed design mechanism | Reusable choice / caution |
|---|---|---|
| [U-Net, author architecture / Fig.1](https://lmb.informatik.uni-freiburg.de/people/ronneber/u-net/) | Descend/ascend levels, horizontal copy/crop, channel/spatial labels and operation legend | Align scales, separate skip lanes; never transfer that model's channel counts. |
| [Swin, ICCV 2021 Fig.3, PDF p4](https://openaccess.thecvf.com/content/ICCV2021/papers/Liu_Swin_Transformer_Hierarchical_Vision_Transformer_Using_Shifted_Windows_ICCV_2021_paper.pdf) | Stage overview beside two block details; repeat ranges, attention variants, residual junctions | Separate overview/detail; avoid copying hard-to-read rotated labels. |
| [MambaVision, CVPR 2025 Fig.2/3, PDF p3/5](https://openaccess.thecvf.com/content/CVPR2025/papers/Hatamizadeh_MambaVision_A_Hybrid_Mamba-Transformer_Vision_Backbone_CVPR_2025_paper.pdf) | Stage bands, repeats and distinct operations; two mixer branches with explicit concat | Draw evidenced branches and fusion; don't infer all SSMs share this structure. |
| [SAM, ICCV 2023 Fig.4, PDF p5](https://openaccess.thecvf.com/content/ICCV2023/papers/Kirillov_Segment_Anything_ICCV_2023_paper.pdf) | Image encoder versus prompt injection, embedding strip, separate mask outputs | Separate representations from compute. No source photographs reused; local PDF font substitutions limit certification of tiny symbols. |
| [FPN, CVPR 2017 Fig.2/3, PDF p2/3](https://openaccess.thecvf.com/content_cvpr_2017/papers/Lin_Feature_Pyramid_Networks_CVPR_2017_paper.pdf), supplemental | Aligned scales, top-down/lateral paths, 2x up and 1x1 projection with explicit sum | Scale axes and operator semantics, not generic boxes with unexplained merging. |

Implementation mechanisms examined: [PlotNeuralNet](https://github.com/HarisIqbal88/PlotNeuralNet)
`layers/Box.sty`/`pycore/tikzeng.py` separates volume faces, labels and named anchors;
[diagram-design](https://github.com/cathrynlavery/diagram-design) specifies semantic color,
hierarchy and distributed fan ports; [Netron](https://github.com/lutzroeder/netron)
`source/grapher.js` passes measured label sizes and hierarchical edges into graph layout.
Use these ideas within the existing renderer, not their runtimes. The former supplies
editable TikZ but adds a LaTeX dependency; the latter is useful for computational graph
inspection but does not establish publication composition. Existing vendor attribution
and licenses remain intact. No third-party implementation code was added in this increment.

Current examples prove a limited, deterministic visual grammar on synthetic contracts.
They are not blind human ratings, venue acceptance or validation against an unavailable
real model. User review decides whether the visual level meets the intended standard.
