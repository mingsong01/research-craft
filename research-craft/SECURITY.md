# Security and Data Handling

## Local-first behavior

The Skill has no external telemetry and its bundled script uses only the Python standard library. Project records remain under `.research/` in open formats. It does not perform network requests.

Local-first describes artifact storage and deterministic helpers, not the hosting model. Instructions and tool outputs may be processed by the model service configured in the host; follow the host and organization's processing policies. No offline-inference or data-retention guarantee is implied by this Skill.

## Network and external tools

`network_policy` is advisory and cannot override Codex, organization, sandbox, or user permissions. Public web research must not include private code, unpublished manuscripts, private data, logs, or credentials. Uploads and network writes require explicit user intent.

## Secrets

The script redacts common token, password, private-key, and credential patterns before writing record values. This is defense in depth, not a secret scanner. Do not intentionally place secrets in `.research/`.

## Destructive and costly actions

Deletion, raw-data overwrite, costly training, external upload, credential-sensitive actions, and broad refactors are high risk and require clear authorization immediately before execution. Raw experiment artifacts are immutable by default.

## Integrity and recovery

Registry mutations validate fields, hold an exclusive workspace lock, reject duplicate IDs, write a temporary sibling, flush it, and atomically replace the target. Failed experiments remain recorded as `failed`. Schema migration is explicit and makes a backup before changes.

## Reporting issues

Before public distribution, the publisher should add a maintained private vulnerability-reporting channel and coordinated-disclosure policy. Do not include sensitive exploit details in a public issue.

## License and distribution

No license is selected by this Skill. The publisher must choose an appropriate `LICENSE`, ownership model, support policy, and distribution terms before external release.
