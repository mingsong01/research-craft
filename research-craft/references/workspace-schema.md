# Workspace Schema v1

Read before creating, updating, auditing, or migrating `.research/`.

## Sources of truth

- `config.yaml`: workspace schema and small behavior overrides.
- `STATE.yaml`: current work only; never project history.
- `registry/*.csv`: durable issue, experiment, evidence, decision, change, and journal records.
- `experiments/<ID>/manifest.yaml`: full compact experiment metadata.
- `DASHBOARD.md`: generated view; never edit as a database.
- `notes/`: only for reasoning that does not fit a compact row.
- `writing/*.csv`: reviewer, figure/table, and manuscript traceability, created on demand.

Run `research.py --root <project> init [--preset minimal|standard|strict]`. Initial creation is limited to config, state, and dashboard. Registry and experiment files are lazy.

## Configuration

Schema v1 keys: `schema_version`, `recording_mode`, `network_policy`, `execution_policy`, `default_record_level`, `large_file_threshold_mb`, `journal_enabled`, `git_tracking`, and `writing_tracking`.

- `minimal`: QUICK by default, journal and writing tracking off.
- `standard`: TRACKED by default, local journal and writing tracking on.
- `strict`: FORMAL by default, network `research_only`, tracking on.

Configuration does not grant tool permission. Environment and user authorization still control execution.

## Registries

`issues.csv`: `issue_id,date,title,status,summary,root_cause,linked_experiment,next_action,detail_path`

`experiments.csv`: `experiment_id,date,question,type,status,key_variable,key_result,linked_issue,linked_evidence,detail_path`

`evidence.csv`: `evidence_id,claim,source,status,scope,limitation`

`decisions.csv`: `decision_id,problem,selected_option,reason,evidence,limitation,status`

`changes.csv`: `change_id,date,summary,files,reason,linked_issue,linked_decision,validation,status`

`journal.csv`: `timestamp,type,linked_id,summary`

Writing registries are also lazy. `literature.csv` uses `citation_id,title,authors,year,source_type,identifier,url,accessed_at,verification,linked_evidence`. `literature_search.csv` uses `search_id,date,question,source,query,filters,hits,screened,included,limitations`. Add writing rows through `research.py writing add` so duplicate identities and secrets are checked.

IDs use `<PREFIX>-YYYYMMDD-NNN`. The script holds a short workspace lock, checks the registry, writes a temporary file, and atomically replaces the destination. A duplicate or active lock stops the write.

## State

Keep only: `active_problem`, `active_issue`, `current_stage`, `record_level`, `active_experiments`, `active_hypotheses`, `blockers`, `next_actions`, and `updated_at`.

## Experiment manifest

Supported keys include `id`, `record_level`, `question`, `hypothesis`, `type`, `status`, `issue`, `baseline`, `changed`, `controlled`, `primary_metric`, `decision_criterion`, `expected_observation`, `falsifying_observation`, `analysis_plan`, `dataset`, `split`, `seed`, `environment`, `commit`, `git_dirty`, `command`, `metrics`, `result`, `can_claim`, `cannot_claim`, `exploratory_interpretations`, `limitations`, and `preregistered_at`.

TRACKED experiments may remain compact. FORMAL experiments must pass `experiment validate --level formal` before execution. Interventional FORMAL experiments additionally require baseline, changed variable, and controlled variables. Create only files with content; add `metrics.csv`, raw, processed, or analysis artifacts only when produced.

## Migration

Never silently change schema. `audit` reports mismatches. `migrate --check` is read-only. An explicit supported migration first copies `.research` to `.research-backups/schema-<old>-<timestamp>`, validates the copy, then applies atomic updates. Version 1 supports an explicit v0-to-v1 migration for early preview workspaces; unknown or newer schemas stop without mutation.

## Diagnostics and artifact identity

`doctor` reports local tool availability, workspace schema/policy, and a possible write lock without changing the project or probing the network. `fingerprint <relative-path>` streams a local file and reports size, modification time, and SHA-256; use it when an external dataset, checkpoint, raw result, or generated artifact needs stable identity without copying it into `.research/`.
