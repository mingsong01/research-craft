# Security and Privacy Checks

Read only for security, privacy, or correctness claims involving adversaries.

State the security goal, adversary, trust boundary, assets, leakage, assumptions, correctness condition, and applicable formal definition. Separate a formal guarantee from empirical behavior.

New components can change leakage, attack surface, assumptions, and correctness. Inspect TEEs/enclaves, caches, Bloom filters, access trees, query decomposition, plaintext identifiers, persistent state, rollback, side channels, and failure handling as applicable. An enclave is not automatically secure.

For probabilistic structures such as Bloom filters, distinguish theoretical false-positive probability from end-to-end correctness or security impact. A small component probability alone does not prove negligible system risk; trace how a false result propagates and whether it is detected or recoverable.

Build the threat model before recommending controls: protected assets, entry points, principals, privilege levels, data flows, trust boundaries, attacker capabilities, abuse cases, and unacceptable outcomes. Distinguish preventive, detective, and recovery controls. Apply least privilege, secure defaults, fail-closed behavior, input validation, secret isolation, dependency/supply-chain checks, and auditable key/token lifecycle where relevant.

Prioritize findings by exploit preconditions, reachability, impact, affected scope, detectability, and remediation risk—not scanner count alone. Validate fixes with a safe reproduction or security test plus regression coverage. Do not claim penetration testing, formal verification, compliance, confidentiality, anonymity, or resistance to an adversary unless the corresponding scope and method were actually executed.

For privacy, distinguish collection minimization, purpose limitation, access control, retention/deletion, linkage/reidentification risk, and disclosure mechanism. Encryption at rest or in transit does not resolve excessive collection, metadata leakage, authorized-user misuse, or downstream retention.
