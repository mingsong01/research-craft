# Third-Party Notices

This development candidate contains or adapts material from the following sources.

## Directly vendored code

- Bybit `svg-diagram`, MIT License. Unmodified lint runtime in `scripts/vendor/bybit-svg-lint/`; upstream commit is recorded in that directory.
- `ml-architecture-diagram-skill`, MIT License. Unmodified `routing.py` in `scripts/vendor/ml-architecture-diagram/`; upstream commit is recorded in that directory.
- `Agents365-ai/drawio-skill`, MIT License. Unmodified `edgeports.py`, `validate.py`, and `colorblind-safe.json` are stored under `scripts/vendor/drawio-skill/` and `assets/vendor/drawio-skill/`; upstream commit is recorded beside the scripts.
- `OpenGHz/academic-human-in-the-loop` FigureSpec, MIT License. The standard-library renderer is stored under `scripts/vendor/figure-spec/`; its module header and pinned metadata identify local changes for topology attributes, waypoint routing, cross-platform output, visible-boundary arrow clearance, routed labels, stroke-matched markers, training semantics and finite-input checks. The original upstream commit, checksum and license are retained beside the adapted source.

Their license texts are stored beside the vendored code.

## Adapted procedural material

- Jesse Vincent / `obra/superpowers`, MIT License, commit `8ca22dba9a94f28898bbce59f2537ff4d87c747d`. Adapted the systematic-debugging, test-driven-development, and verification-before-completion procedures. License: `licenses/superpowers-MIT.txt`.
- K-Dense Inc. / `scientific-agent-skills`, MIT License, commit `065b734670d7d990627dbc06a05b5a99be33f1f1`. Adapted selected procedures from hypothesis generation, experimental design, scientific critical thinking, exploratory data analysis, statistical analysis, literature review, scientific writing, peer review, and scientific visualization. License: `licenses/kdense-scientific-agent-skills-MIT.txt`.
- `tt-a1i/archify`, MIT License, commit `69cf672087289033af5138648d3875d3d73fc431`. Adapted route-quality, verification, and visual-composition patterns. License: `licenses/archify-MIT.txt`.
- `cathrynlavery/diagram-design`, MIT License, commit `57148ac6f7cf8f2d0080f23437ab2929bca15f3e`. Adapted editorial tokens, grid, complexity, typography, connector, accessibility, and taste-gate patterns. License: `licenses/diagram-design-MIT.txt`.
- `Cocoon-AI/architecture-diagram-generator`, MIT License, commit `4b9087d55268c79a935105439dbcd37b630fc3f3`. Adapted the optional dark semantic palette, containers, spacing, and legend discipline. License: `licenses/cocoon-architecture-diagram-MIT.txt`.
- `lazypay/Archscribe`, MIT License, commit `46ea42cfc6c557ab238867c390bb18320fd36769`. Adapted layout-selection, paper-sketch, and editable delivery patterns. License: `licenses/archscribe-MIT.txt`.
- `icebird1998/scientific-illustrator`, MIT License, v1.5.4 snapshot reviewed 2026-10-21. Adapted checkpointed region reconstruction, editable-object priority, minimal raster fallback, and truthful host-state verification. No plugin, MCP, PowerPoint, WPS, or draw.io application-control code was copied. License: `licenses/scientific-illustrator-MIT.txt`.

Adapted passages were compressed and integrated into this Skill's terminology, safety model, and low-context architecture. No upstream trademark or endorsement is implied.

## Workflow ideas only

- Anthropic artifact skills: render, inspect, repair, and rerender pattern. No proprietary text or code copied.
- `Dsadd4/AgentFigureGallery`, MIT License: bounded human-selected visual references and source-license awareness. No dataset, plotting runtime, or gallery code copied.

See `MARKET_BENCHMARK.md` for the selection rationale and capability mapping.
