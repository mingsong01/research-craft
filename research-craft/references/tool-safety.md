# Tool and Data Safety

Read before external research, destructive operations, costly runs, external uploads, or handling potentially sensitive artifacts.

## Routing and permissions

Prefer existing local evidence, targeted search, deterministic computation, then a small discriminative experiment. External public research follows these. Expensive execution is last.

Analysis-only requests authorize reads and local non-mutating diagnostics, not code edits, record mutation, large experiments, or uploads. A request to record authorizes scoped `.research/` writes, not implementation. Require explicit intent immediately before high-risk actions.

## Data handling

- Default to local processing and no telemetry.
- Do not send private code, unpublished manuscripts, private datasets, logs, or credentials to external tools.
- Public web queries must be phrased without private content.
- Redact suspected API keys, passwords, tokens, private keys, and SSH credentials before recording.
- Do not copy large datasets, checkpoints, or model files into `.research/`; store a project-relative reference, identifier, size, and checksum only when useful.
- Never overwrite raw artifacts. Create a new processed output or versioned experiment instead.

`network_policy` describes preference (`offline`, `research_only`, `allowed`) but never bypasses environment policy or approvals. Optional services such as W&B, MLflow, Zotero, GitHub, Drive, Overleaf, or MCP are adapters; the core workflow must function without them.

## Capability degradation

Missing Git: use `commit: unavailable` and `git_dirty: unknown`.

Missing Web: continue locally and label external validation not performed.

Missing Python or specialized tools: use available deterministic tools or provide a reproducible command without pretending it ran.

Missing GPU/Docker: design or validate a smaller local test and leave the full run pending.

## Recovery

Registry writes must validate fields, acquire the workspace lock, write a temporary sibling, and atomically replace. A failed experiment remains with status `failed`. On write conflict, stop and report it; never merge ambiguous concurrent edits automatically.
