# Scientific Diagram Design

Read only for research model diagrams, neural-network architectures, computation graphs, and method/system frameworks. The canonical deliverable is an editable vector artifact, normally SVG. Scientific correctness and visible connectivity outrank decoration.

## 0. Define the visual argument

Before drawing, define one sentence stating what the reader should understand, the evidence-bearing entities and relationships, exact labels/symbols that must remain verbatim, intended physical width, editable/export formats, and any details that must remain `UNKNOWN`. A paper figure is a visual argument: every panel, inset, icon, and annotation must explain a claim, mechanism, comparison, boundary, or decision.

For a high-stakes figure, inspect up to three relevant published examples or user-supplied references and extract only reusable composition properties: reading direction, density, hierarchy, palette roles, shape grammar, and annotation style. Do not reproduce another paper's unique scientific content, topology, icons, or trade dress. Record the source and license for imported assets. Never send private manuscript text or unpublished data to an external reference or generation service without explicit authorization.

## 1. Recover topology before layout

Create a compact topology contract before drawing:

- stable node IDs for inputs, stages, branches, skip/residual routes, fusion/junctions, novel modules, outputs, and auxiliary paths;
- directed edges with `source`, `target`, and type (`main`, `skip`, `auxiliary`, `feedback`, or `training-only`);
- groups/stages and any known order or scale hierarchy;
- unresolved facts that must remain `UNKNOWN` rather than being invented.

Inspect the executed or documented computation path, not class names alone. A visual abstraction may compress repeated ordinary operations, but it must not add/delete/reverse edges, remove a real branch, merge semantically different modules, or fabricate internals. For a non-trivial model, retain a small JSON/YAML node-and-edge list as the topology source of truth and give the rendered SVG matching `data-node-id`, `data-source`, and `data-target` metadata.

## 2. Choose layout from graph structure

For paper model architectures, read [model-architecture-patterns.md](model-architecture-patterns.md)
for architecture-specific visual grammar, two-composition comparison, optional editable
feature/token expressions, and five independent acceptance dimensions. Do not default
every model to identical flowchart boxes. Worked vector sources are in `demo/publication/`.

Use the smallest layout that preserves the reading task:

| Structure | Primary layout | Routing treatment |
|---|---|---|
| Serial pipeline | left-to-right layered | short horizontal routes |
| Encoder-decoder | symmetric U/stage layout | aligned main path; skip lanes above/below |
| Stage hierarchy | layered or nested groups | stage gutters; no container crossings |
| Multi-branch fusion | aligned lanes to a real fusion node | separated fan-out/fan-in; bus when clearer |
| Main + auxiliary | dominant main lane plus quieter auxiliary lane | dashed auxiliary route in outer gutter |
| Iterative/recurrent | main path plus labeled return loop | loop outside node field; arrow direction explicit |

Place and size all nodes before routing. Use real label dimensions, alignment, and group padding. Optimize in order: zero incorrect/missing connections; zero node intersections; visible arrowheads; low crossing count; short routes; few bends; compact occupied area. Grow or reflow the canvas rather than clipping a legal route or shrinking labels below readability.

Use a 4 px structural grid for node origins, widths, heights, padding, and major gaps. Prefer gaps from 20, 24, 32, 40, or 48 px and internal padding from 8, 12, or 16 px. This rhythm is adapted from the high-adoption Diagram Design skill; text baselines, marker geometry, stroke widths, and optical corrections may sit off-grid.

Choose the composition as well as the topology:

- **stage / layered** for a paper model architecture with one dominant reading direction;
- **panorama** for a system with inputs, a core, outputs, and a small number of explanatory side panels;
- **swimlane** for parallel roles, variants, scales, or processing families;
- **free graph** only when the topology itself is the message and a layered arrangement would mislead.

For a single paper panel, aim for at most 9–12 primary visual units and 12–16 visible routes. Repeated layers may be compressed into a labeled stack, but never compress away a decision-relevant branch or interaction. Split into an overview plus a detail inset when labels, crossings, or route lengths remain crowded. Complexity budgets guide legibility; they never authorize deleting topology.

For a full multi-panel paper figure, assign each panel one job and one takeaway. Use a horizontal narrative, balanced grid, hierarchical hero-plus-support, or schematic-above/results-below composition according to the scientific story. Keep panel letters, gutters, alignment, and typography consistent. Do not fabricate data panels; link real plots to their source data and plotting script.

## 3. Route connectors at visible boundaries

Never draw center-to-center arrows. For each directed edge:

1. select a source port on the visible source boundary and a compatible target port on the visible target boundary;
2. start the path about 5 px outside the source boundary;
3. account for marker geometry when ending the path: for the default 8×8 notched marker with `refX=2`, the tip extends 6 px, so stop the path about 11 px before the target boundary to leave a visible 5 px tip gap;
4. use orthogonal/Manhattan segments by default; choose a direct dogleg only when clear;
5. otherwise route through a stage gutter or obstacle-clear waypoint; keep 12–20 px from unrelated nodes;
6. reserve separated lanes for parallel edges and distinguish skip/auxiliary routes with dash pattern plus a label or route position, never color alone;
7. keep the last segment long enough to make direction obvious.

When several connections leave the same node side, distribute their ports in the order of the far endpoints rather than stacking them at the side center. For editable draw.io output, run the directly vendored MIT port allocator:

```text
python <skill>/scripts/vendor/drawio-skill/edgeports.py figure.drawio
```

It is deterministic and preserves already pinned hand-tuned ports. It solves boundary stacking, not mid-route obstacle crossings; SVG/draw.io waypoints and the topology inspection are still required.

If two unavoidable orthogonal routes cross, keep the primary route uninterrupted and place one small bridge/hop on the less important, dashed, or auxiliary route. Never bridge both. Do not use a bridge to excuse a route through a node.

Use the vendored, unmodified MIT-licensed router from `scripts/vendor/ml-architecture-diagram/routing.py` for node placement routes. Call `route_panel_edges(positions, edges, groups)` and consume each returned `_route_points`; do not recreate its A*/gutter/crossing logic. For three or more edges sharing a source or target, use its `fanout_bundle_geometry` or `fanin_bundle_geometry` instead of drawing coincident independent routes. Apply the marker-tip offset after routing so the painted tip remains outside the target fill.

Then run both QA layers. The Bybit profile executes the vendored upstream parser, geometry model, and mature lint checks; its thin adapter excludes only upstream house-style rules that conflict with this skill's required Manhattan routing, semantic palette, scientific title alignment, or wide stage gutters:

```text
node <skill>/scripts/bybit_svg_profile.mjs figure.svg
```

Run the local topology contract check separately. It supplements—rather than replaces—the vendored tools by validating research-specific node/edge IDs and the known hidden-arrowhead failure:

```text
python <skill>/scripts/diagram_svg_qa.py lint figure.svg --spec topology.json --json
```

For publication delivery, add `--width-mm <actual final width>`. This enables
physical text, connector-stroke and arrow-size screening (defaults: 7.5 pt,
0.5 pt and 2.5 pt respectively). These are declared screening thresholds, not
universal venue requirements. A venue-specific override needs its source and
an explicit recorded justification; never lower thresholds merely to pass.

Report the layers separately:

- **Scientific topology:** compare the supplied node/edge contract, then audit
  its correspondence to the designated model version. A matching synthetic
  contract does not prove a real model. Legacy string-node/endpoint-edge
  contracts remain supported, but cannot certify omitted semantics. Optional
  node objects can specify `operation`, `stage`, `tensor_shape`, and
  `execution: training-only`; edges can specify `id`, `type`, and `train_only`.
  Preserve matching metadata in SVG. Conflicting fields, repeated identities,
  extra or missing connections and changed fusion semantics fail. Distinct
  same-pair/same-type parallel connections currently need explicit junction
  nodes; this checker does not certify a multigraph port abstraction.
- **Geometry and technical checks:** direct rect/circle/ellipse/polygon nodes
  and M/L/H/V routes are certified. Nested translation and positive uniform
  scaling are resolved in world coordinates. Rotation, reflection, shear,
  nonuniform scale, nested viewports, CSS transforms and curved routes fail
  explicitly until normalized or verified by a suitable native tool. That
  failure must remain visible; native inspection does not retroactively make
  an unsupported local check pass. Bybit and local results must both be read.
- **Visual and paper suitability:** physical screening alone cannot approve
  typography, perceived hierarchy, glyph coverage, grayscale separation or
  reading effort. The CLI always leaves visual review `NOT_REVIEWED`. Inspect
  the actual final-width color/grayscale renders and exported PDF, record
  observations and limitations separately, and repair before delivery.

`training-only` is an execution condition, not a decorative color. It defaults
to a dashed FigureSpec connector; an explicit solid style is invalid. Preserve
its typed contract and non-color encoding, label training-only nodes, and never
place those nodes on an ordinary inference path. A skip can remain active at
inference: do not label all dashed paths as training-only. Use distinct dashes
or direct labels when both occur.

The renderer uses stroke-matched 8/12/16 px notched markers and compensates for
their painted forward extent. Folded-route labels follow the actual polyline,
with text clearance; do not place them at the endpoints' straight-line midpoint.

The Bybit adapter retains the same pre-existing compatibility decisions for
brand palette, Manhattan right angles, wide stage gutters and title alignment.
It now exposes every upstream finding and disposition rather than hiding them.
No additional check is disabled. Independently verify palette/legend/contrast,
route clearance and final-size grouping; retain all remaining errors. A warning
needs an artifact-specific disposition, not a blanket waiver. The bundled
complex demo is intended for 180 mm width; its 85 mm shrink must fail physical
screening. Use a different composition for single-column delivery.

Arrowhead occlusion, visually ambiguous direction, a wrong/missing edge, or a connector crossing a key unrelated node is a hard failure. Do not deliver until repaired and rerendered.

## 4. Use a restrained visual grammar

- rounded rectangle: learnable/custom module;
- rectangle: generic deterministic operation;
- stacked blocks: repeated layers or feature maps;
- circle: operator, merge, split, or junction;
- quiet group container: stage or module family.

Highlight novelty with semantic color, a slightly stronger border, a clear label, and grouping. Do not use extreme saturation, oversized blocks, or several-fold line-weight changes.

### Semantic palette

Use 3–5 main roles in one figure. The extended defaults below are color-blind-aware and must be paired with labels, shape, border, or line style so grayscale remains interpretable.

| Role | Fill | Stroke | Use |
|---|---|---|---|
| Generic / ordinary | `#F3F4F6` | `#6B7280` | ordinary operations/context |
| Encoder / extraction | `#DCEEF8` | `#0072B2` | features/backbone |
| Enhancement | `#FCE8D5` | `#E69F00` | enhancement/refinement |
| Fusion | `#ECE4F6` | `#7B61A8` | concatenate/add/multi-scale fusion |
| Attention / selection | `#DDF3EF` | `#009E73` | attention/gating/selection |
| Suppression / filtering | `#E5F1DF` | `#4C7F3B` | filtering/suppression |
| Output / key result | `#F8DDD7` | `#D55E00` | output or restrained focal highlight |

Do not use rainbow scales or red/green as the sole distinction. A legend is a contract: every legend role/color must match the actual nodes, and unused legend entries must be removed.

### Choose one visual profile

Do not mix the profiles within one figure.

**Scientific semantic — default for ML/network figures.** Use the role palette above when the reader must distinguish encoder, fusion, attention, filtering, output, or other scientific functions. Limit the active figure to 3–5 roles and retain labels/shape/dash redundancy.

**Editorial one-accent — best for method overviews and framework figures.** Adapted from the 42k-Star Diagram Design skill:

- paper `#F5F5F5`, ink `#2D3142`, muted `#4F5D75`, soft `#7A8399`;
- focal accent `#EB6C36`, accent tint `rgba(235,108,54,0.08)`, external-link blue `#2E5AA8`;
- use one or two focal elements only; ordinary nodes remain paper/ink/muted.

**Presentation dark — optional, never the default paper submission.** Adapted from the 7k-Star Cocoon architecture-diagram skill:

- background `#020617`, panel `#0F172A`, ordinary stroke `#94A3B8`;
- role accents cyan `#22D3EE`, emerald `#34D399`, violet `#A78BFA`, amber `#FBBF24`, rose `#FB7185`;
- use opaque node underlays so routes cannot show through translucent fills;
- keep the exported canonical diagram local and self-contained; do not introduce remote fonts, CDN scripts, analytics, or raster-only PDF export.

**Paper sketch — optional for talks, ideation, or approachable explainers.** Borrow the tested light-paper, lane, icon, and editable-source approach from Archscribe/Excalidraw. Do not use sketch jitter for precise tensor dimensions, small operator labels, or geometry whose alignment conveys meaning. Always retain a clean SVG or editable Excalidraw/draw.io source.

### Aesthetic hierarchy gate

- Give the eye one first destination, a clear reading direction, and no more than two focal nodes.
- Use color for semantic role or focal priority, never decoration alone.
- Keep containers quiet: 2–5% ink wash, thin border, and at least 16 px between a container label and its first node.
- Put the legend outside the node/route field. Do not let it occupy a semantic group or trust boundary.
- Align related nodes and equalize visually equivalent widths/heights. Use optical centering for icons and short labels.
- Prefer whitespace over card chrome, gradients, glows, drop shadows, decorative grids, and excessive icons in publication figures.
- Use icons only when they reduce reading time. A repeated icon family must share stroke weight, scale, and visual language.

## 5. Professional defaults

These are starting points, not journal mandates. Check current official requirements only when the user names a venue.

- font: Arial, Helvetica, or Liberation Sans; retain a portable sans-serif fallback;
- final-size body labels: 7.5–9 pt; stage headings 9–11 pt;
- node border: 1.0–1.4 pt; novel module up to 1.5 pt;
- connectors: 1.0–1.25 pt; skip/auxiliary 1.0–1.2 pt with redundant dash/label encoding;
- default arrowhead: 8×8 user-space marker, `refX=2`, `refY=4`, `orient=auto`;
- corner radius: 5–8 px; internal padding: 8–12 px;
- spacing rhythm: 8 px; adjacent modules: 28–40 px; group/stage gutters: 20–32 px;
- line-to-label clearance: at least 10 px; routed obstacle clearance: normally 12–20 px.

Use at most three font registers: human-readable names in sans, technical values such as tensor sizes/protocols in mono when useful, and an optional restrained display face for a standalone title. Do not set every label in monospace merely to look technical. For Chinese, Japanese, or Korean labels, use an installed or bundled CJK sans fallback and keep essential text at roughly 12 px or larger in the SVG source; shorten or wrap before shrinking.

At intended paper width, never solve crowding by reducing essential labels below the readable range. Shorten labels, reflow stages, split a detail panel, or enlarge the canvas.

## 6. Select the authoring tool deliberately

- SVG/native vector: preferred canonical paper artifact and deterministic QA;
- draw.io: structured collaborative editing and handoff;
- native PowerPoint shapes: team editing and presentation reuse;
- Figma: polished manual vector composition;
- Graphviz/ELK: graph-heavy layered auto-layout or port-constrained routing;
- TikZ: LaTeX-native precision and document-integrated typography;
- Inkscape/Illustrator: final manual refinement after topology is locked.

High-adoption declarative engines are optional tools, not mandatory dependencies:

- Mermaid is appropriate for a fast text-first draft and simple flows; refine or replace it when routing, port placement, or publication composition matters.
- D2/ELK or Graphviz is appropriate for dense graph-heavy auto-layout; inspect the actual SVG and retain the topology contract.
- Excalidraw is appropriate when the user explicitly wants an approachable hand-drawn editable artifact.
- Python Diagrams is appropriate for cloud/provider architecture, not as a default ML-computation renderer.

Do not vendor these large engines into this Skill. Detect and use an installed engine when it fits, export SVG, then run the same topology, arrow, accessibility, and final-size gates. Engine popularity does not waive artifact QA.

PNG is a preview or venue-specific raster export, not the editable source. Export PDF when the submission workflow benefits from it.

### Bundled deterministic renderer

When no stronger native editor is required, use the bundled MIT FigureSpec renderer. It turns compact JSON into editable, self-contained SVG without an external service:

```text
python <skill>/scripts/vendor/figure-spec/figure_renderer.py validate figure-spec.json
python <skill>/scripts/vendor/figure-spec/figure_renderer.py render figure-spec.json --output figure.svg
```

The local adaptation emits topology metadata for QA, accepts explicit `waypoints`, clips routes to shape boundaries, and leaves a visible gap between arrow tips and node fills. Prefer orthogonal waypoints for publication diagrams. Save the JSON next to the SVG as the source of truth, then run the normal SVG QA and rendered inspection. Use this renderer for deterministic structured figures, not organic biological illustrations or photorealistic graphical abstracts.

### Optional generative composition reference

For organic mechanisms, graphical abstracts, or domain objects that are expensive to construct from primitives, an image generator may produce one or two composition references. Use them only for layout, hierarchy, and shape inspiration. Rebuild scientific labels, topology, arrows, quantitative content, and editable objects in SVG/draw.io/PPTX. Raster text, connections, and measurements remain untrusted until reconstructed and verified. Stop after two candidate rounds unless another round has a concrete repair target.

### Reference-driven editable reconstruction

When the user supplies a paper figure, sketch, or screenshot as a visual reference, follow the checkpointed editable-first pattern validated by the MIT-licensed Scientific Illustrator project:

1. recover the topology and divide the figure into semantic regions before drawing;
2. rebuild text, nodes, connectors, groups, legends, and quantitative labels as editable vector objects;
3. rasterize only the smallest irreducible region, such as a micrograph or complex texture, and preserve its source/license;
4. render and inspect each completed region before continuing, so a local alignment or routing defect does not propagate;
5. finish with a whole-figure comparison at the intended output size, then rerun topology and connector QA.

Do not claim that a live PowerPoint, WPS, Figma, or draw.io document was edited unless the host connection and saved artifact were actually verified. A generated `.pptx` or `.drawio` file is an editable working copy, not proof that a particular open window was controlled.

## 7. Generate, render, inspect, repair, rerender

Completion requires both deterministic QA and inspection of the actual render:

1. route with the vendored ML Architecture Diagram router, or render an explicit JSON FigureSpec with the bundled deterministic renderer, and generate editable SVG from the topology contract;
2. run `bybit_svg_profile.mjs` plus `diagram_svg_qa.py lint`; repair every error or, for an upstream stylistic warning, record the explicit disposition;
3. render at intended publication width, not only at full-screen zoom;
4. inspect the rendered pixels for visible arrowheads and obvious direction, topology fidelity, node/edge/text overlap, clipping, unintended crossings, alignment, whitespace, legend-color agreement, label accuracy, innovation hierarchy, and final-size readability;
5. inspect a grayscale render and a color-vision-deficiency simulation when tools permit; otherwise ensure redundant labels/shapes/dashes and record the unperformed simulation;
6. repair and rerender changed artifacts; repeat until the lint is clean and human inspection passes.

Add an explicit taste pass after correctness is green. For high-stakes work, compare at most two or three materially different layouts against the same topology contract; do not create cosmetic variants that add no information:

- first-glance focal point matches the scientific contribution;
- visual weight is balanced rather than top- or side-heavy;
- repeated modules have consistent geometry and spacing;
- secondary annotations are visibly quieter than the main computation;
- no orphan label, accidental near-alignment, tiny isolated gap, or excessively long detour remains;
- the figure still reads when printed in grayscale and when reduced to the intended column width.

XML validity or file existence alone is not evidence of completion. Automated geometry cannot reliably judge typography, perceptual balance, or every transformed/curved SVG; render inspection remains mandatory.

## 8. Provenance and benchmark lineage

The complete Bybit SVG lint runtime and the ML Architecture Diagram obstacle router are vendored without source edits under `scripts/vendor/`; their MIT licenses and pinned commit files are included beside the code. The draw.io multi-edge port allocator and its validation dependency are vendored unmodified from the MIT-licensed `Agents365-ai/drawio-skill`, with pinned commit and license. `bybit_svg_profile.mjs` is only a compatibility adapter.

Archify informs route-quality, visual verification, and deterministic evidence patterns; Diagram Design informs the editorial profile, 4 px grid, complexity budget, multilingual typography, restrained focal hierarchy, and bridge/hop convention; Cocoon Architecture Diagram informs the optional dark semantic profile, whitespace, containers, and legend discipline; Archscribe informs panorama/swimlane/free-graph selection, editable multi-format delivery, and paper-sketch mode. These are adapted workflow/design rules under their MIT licenses, not copied runtimes. Cocoon's arrows-behind-nodes convention is explicitly not adopted because it can hide arrowheads; this Skill's boundary-clearance hard failure remains authoritative.

K-Dense Scientific Schematics informs final-size, color-blind, grayscale, and iterative scientific review. Anthropic's PPTX skill informs only the general render-inspect-fix-rerender QA pattern; no proprietary text, code, templates, or assets are copied.

OpenGHz FigureSpec supplies the bundled deterministic JSON-to-SVG renderer under MIT; it is pinned and attributed beside the adapted source. Scientific Illustrator informs checkpointed region-by-region reconstruction, editable-object priority, minimal raster fallback, and truthful host verification. AgentFigureGallery informs bounded human-selected visual references rather than unconstrained style imitation. Neuromechanist Research Skills informs one-theme-per-project discipline and the strict split between deterministic measurements and perceptual review. Academic Figures informs multi-panel narrative layouts, editable layers, and final-width planning. Codex Paper Figure Skill informs editable-first draw.io reconstruction after optional raster ideation. Google PaperVizAgent/PaperBanana and Crafter are research benchmarks for reference-driven planning, candidate critique, and editable delivery only; their multi-agent/product architecture is not copied or introduced here, and PaperBanana's stated commercial/patent restrictions make direct workflow reuse inappropriate for this commercializable Skill.
