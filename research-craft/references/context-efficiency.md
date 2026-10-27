# Context efficiency with recoverable scientific evidence

Load only for large sources, repeated retrieval, session recovery or cost measurement. This is an operating method for the existing workflow, not a new memory service or routing engine. Quality and the requested deliverable determine the necessary detail; do not default to terse scientific answers.

## Choose and reuse context

- HOT: scope/authorization, accepted decisions, active question, important limits and the current state if tracking exists. QUICK work needs no workspace initialization.
- WARM: the active registry row, relevant reference section and a short decision note. Use positive `list --limit N` and `--id` when known; do not dump registries to find one record.
- COLD: immutable raw sources, papers, code, logs and old notes. Search paths/headings/symbols first, then retrieve the smallest scientifically sufficient span. Expand for definitions, assumptions, contradictions or cross-references; a search hit is not proof.
- Within the current task, retain a small retrieval note: relative source, hash/version, covered ranges, purpose and unresolved dependencies. Reuse only when both content identity and scope remain valid. Recheck identity after edits, version changes or uncertain recovery; a remembered path, timestamp or summary alone is insufficient.
- Batch independent targeted searches/reads. Do not reread unchanged full files, repeat a failed broad search unchanged, or delegate solely to shorten context. Use existing search/CLI tools; no new service is required.

## Recoverability and protected content

Every compressed note needs `raw_ref`: accessible source/version (prefer SHA-256), precise locator (line/page/section/CSV record/symbol), transformation/filter, coverage/omissions and its interpretation status. A hash alone is not a recovery location. If the original cannot be accessed, label the note incomplete and do not base a consequential claim on it.

Keep these exact spans available; summaries may index them but cannot replace them:

| Content | Preserve and verify on return to source |
| --- | --- |
| Results/data | Original numeric strings, significant digits, units, denominators, adverse outcomes, split/sample membership, seed and full configuration; aggregates do not validate group comparability. |
| Formulas/methods | Symbols, operators, definitions, dimensions, assumptions and validity conditions, including surrounding qualifications. |
| Reviewer/advisor | Complete compound reviewer comment; mentor negations, conditions, limits and attribution uncertainty. A summary must not become a confirmed quotation. |
| Argument/diagnosis | Claim-evidence links, competing explanations, unresolved conflicts, actual failure and full relevant traceback. Proposed work never becomes completed work. |

For UTF-8 text, the existing helper provides exact decoded spans and hashes the same input stream:

```text
python <skill>/scripts/research.py --root <project> read-slice notes/source.txt --range 12:28 --range 46:51
python <skill>/scripts/research.py --root <project> read-slice notes/source.txt --range 12:28 --expect-sha256 <previous-hash>
```

Ranges are 1-based, inclusive and disjoint; output declares whether the whole file is present. A changed hash, overlapping/invalid span or end beyond EOF is an error, not silently truncated evidence. The UTF-8 BOM is omitted from decoded text, original newlines remain, and SHA-256 covers original bytes. This scans the source to verify identity; prefer an existing trusted immutable snapshot when repeated full hashing would dominate I/O. It is not a PDF parser or semantic summarizer. For inaccessible/binary/unsupported sources, use an available local reader with page/region identity or report the gap; do not install a converter automatically.

## Bound tool output without hiding evidence

- Logs/tests: save complete stdout/stderr and exit status first. Present outcome, scope, all active failures/warnings and a source locator. Suppress repetitive successes only when irrelevant; on failure inspect the full relevant trace. A repeated error may encode different seeds or conditions; do not deduplicate it blindly.
- CSV: `summarize-csv file.csv --columns score --key run --evidence` streams existing aggregates with same-stream SHA, raw extrema, CSV record/physical-line locators and separate nonfinite/nonnumeric counts. Its invalid examples are capped and explicitly marked exhaustive or partial. Default mode remains compatible. Follow the source for every excluded observation, tied extreme, subgroup/member, exact value used in a claim or configuration; finite aggregates and the first extreme do not replace those records. Floating-point aggregates are not exact decimal arithmetic.
- JSON/experiment logs: select keys/conditions needed for the question; retain schema, units, missing/invalid counts and adverse cases. Never flatten away nested run/split identities. If selection would discard relevant evidence, widen it.
- Repositories: locate files, definitions and callers before reading bodies; expand to call sites, configuration and tests when needed to establish behavior. Symbol names alone do not verify tensor semantics.
- Papers: locate methods/results/limitations, then read definitions, captions, table notes and dependencies together. Keep original formula/table values and page/figure IDs. Abstract-only retrieval cannot establish detailed novelty or method claims.
- Large QA JSON: retain its full raw artifact; a compact view must include exit status, scope, every active finding and dispositions, with a recovery pointer. A summary PASS never substitutes for unrun render review or scientific verification. If extraction fails, show the original error instead of declaring an empty result.

## Resume and avoid unnecessary rework

Use existing state/registry/note fields; no schema change. Store scope, source identities, accepted decisions, limits, protected-span locators, failures/rival explanations, unresolved issues and the next discriminating action. Do not duplicate the conversation or private source corpus in state. On resume verify the active row and source versions, then expand only missing dependencies. Obsolete summaries must be invalidated explicitly.

Keep accepted artifacts and stage closures. Redraw, rewrite or propose another experiment only for a specific defect, changed requirement or decision-relevant uncertainty; record the reason and observable exit condition. This does not remove initial alternative-layout comparison for complex diagrams, final-size rendering, claim checks or necessary reviewer supplements. Stop when the authorized evidence is sufficient.

## Measure cost and quality separately

For comparable tasks freeze inputs, environment, allowed tools, success criteria and both instruction versions. Save actual commands, outputs, elapsed time, errors/rework and duplicate ranges. Bytes and tool calls measure transport/work, not model tokens or writing quality.

Use provider/host usage when attributable: input, output, cached input, cache-write input and reasoning output. Check whether cache/reasoning are subsets before adding; deduplicate response IDs and record the cutoff. Missing usage is `null`, never estimated from bytes/4. Implementation-session totals are not task A/B measurements. Compute complete cost per qualified task only with full execution usage, applicable prices and independently checked task success; account for failed attempts and retries. Preserve sufficient scientific reasoning and requested output regardless of a cost target.

Verify protected-source recovery, writing/diagram/data regressions and task selection separately. Offline fixed-output replay can validate retrieval mechanics; it cannot prove autonomous selection, model quality or token savings. Independent fresh-session A/B with matched inputs and blind quality review remains necessary for those claims.
