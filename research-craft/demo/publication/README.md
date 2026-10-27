# Editable publication examples

These original, synthetic examples demonstrate diagram grammar, not experimental
results or a verified real research model. Each folder contains an editable FigureSpec,
an independently listed topology contract and native SVG. No paper artwork is embedded.

| Example | Target width | Reading task |
|---|---:|---|
| multimodal-A | 180 mm | Horizontal modality convergence; primary choice for the current eight-node contract |
| multimodal-B | 85 mm | The **same** nodes and typed edges reflowed as a vertical trunk; taller single-column alternative |
| unet-multiscale | 180 mm | Two descending scales, corresponding skips, concat and upsampling; volumes depict stage outputs |
| transformer-residual | 180 mm | Pre-norm ordering and separate residual entry ports on explicit addition nodes |
| ssm-gating | 180 mm | Local mixing / one forward state path versus an input-dependent gate, with explicit multiplication |

For multimodal A/B, fusion and refinement internals and feature dimensions are unknown.
Do not invent them from these examples. The three educational block/scale examples have
their own synthetic contracts; they do not reproduce U-Net, Swin, MambaVision or SAM.
Repeated tokens/planes and projected volume sizes are symbolic. Warm color indicates
the declared visual focus, not a claim that a generic operation is scientifically novel.

See `references/model-architecture-patterns.md` for regeneration commands and the five
independent acceptance dimensions. Keep local topology/geometry QA, the existing Bybit
profile and native final-size review separate. Distribute SVG/JSON as the editable source;
PNG previews and PDF exports live in the project validation handoff for this increment.
The root development helper `tools/build_diagram_design_examples.py` can regenerate all
examples without a model call. Individual JSON files render with the Skill's existing CLI.
