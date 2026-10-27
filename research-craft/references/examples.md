# Compact Examples

These examples demonstrate decisions, not required phrasing.

## 1. ML parameter sensitivity - FORMAL

User: "Test whether learning rate 1e-4 is really best."

Action: preregister evaluated values, fixed split/seed/training budget, primary metric, stability criterion, and cost. Aggregate metrics programmatically. Conclude "best among evaluated settings" and report trend/neighbor stability; do not claim a theoretical optimum.

## 2. System performance anomaly - TRACKED

User: "Yesterday's network benchmark is 30% slower. Why?"

Action: define whether bytes and timing are application or wire level, compare environment/workload/cache/warm-up, then run the cheapest test distinguishing workload drift from system regression. Diagnose before modifying code.

## 3. Reviewer comment - FORMAL

User: "Reviewer 2 says the ablation is insufficient."

Action: identify the underlying concern (individual contribution or interaction), map existing evidence, design only the missing discriminative variant, update manuscript and response after evidence exists, and link figure/table to the experiment.

## 4. Simple question - QUICK

User: "What does this small helper return for an empty list?"

Action: inspect and answer. Do not initialize `.research/` or create a record.

## 5. Resume - TRACKED

User: "Continue yesterday's anomaly investigation."

Action: read applicable `AGENTS.md`, `.research/STATE.yaml`, one active issue row, and one detail only if necessary. Do not scan all experiments or raw logs.

## 6. Scientific figure - FORMAL

User: "Create a publication figure for these results."

Action: determine the scientific comparison, verify units and aggregation, show uncertainty and relevant distributions, use accessible encodings, generate from a reproducible script, and register the data/experiment provenance. Do not manipulate axes to amplify the result.

## 7. Frontier and novelty claim - FORMAL

User: "Is this idea new, and what is the latest work?"

Action: run a fresh, dated search across accessible authoritative indexes, inspect primary sources rather than snippets, seek contradictory work, distinguish preprints from final publications, and bound the conclusion to actual search coverage. Say "not identified in the searched sources," not "no prior work exists."
