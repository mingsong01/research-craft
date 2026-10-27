# Forward Evaluation Protocol

Use this protocol to compare Skill versions or the Skill against an ordinary no-Skill baseline.

1. Freeze the model, reasoning effort, tool availability, workspace fixture, and prompt.
2. Run each case in an isolated temporary workspace. Do not reveal expected behavior or rubric to the evaluated run.
3. Preserve the visible response, tool trace, generated artifacts, and workspace diff.
4. Apply deterministic checks first: forbidden writes, expected files, audit result, validation command, tests, and path safety.
5. Grade the remaining qualities using the case rubric. Cite concrete trace or artifact evidence for every score.
6. Compare versions blind when an independent reviewer is available. Otherwise disclose that the author also evaluated the result.
7. Record regressions, not only average score. A safety, privacy, fabrication, or scope violation is a release blocker even if the aggregate score improves.

Use `trigger_scenarios.json` separately to test activation precision. Include near-miss negatives so description changes do not make the Skill trigger on ordinary coding, translation, media, or file-format work.

For router cases, record which references and evidence sources were opened. Penalize unused lane activation, full-corpus loading, and raw payload dumping even when the final answer is factually acceptable. For systematic-review cases, treat an unreproducible query/screening trail or inflated review label as a release-blocking rigor defect.

The bundled `run_evals.py` validates the contracts and rubrics; it does not execute a model. Production release should add host-level recorded runs.

For chapter logic, scientific language, mentor interpretation and revision responses,
use [WRITING_PROTOCOL.md](WRITING_PROTOCOL.md) and its anonymous development packet.
Keep content-level evaluation, structured fact checks and the existing offline contracts
separate; preserve withheld cases for an independently evaluated run.
