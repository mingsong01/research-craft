#!/usr/bin/env python3
"""Deterministic local workspace helper for ResearchCraft."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from collections import deque
from pathlib import Path, PureWindowsPath

SKILL_VERSION = "1.3.1-rc.1"
SCHEMA_VERSION = 1
FORMAL_COMMON_FIELDS = ["question", "hypothesis", "primary_metric", "decision_criterion", "expected_observation", "falsifying_observation", "analysis_plan"]
NON_INTERVENTION_TYPES = {"observational", "literature", "review", "analysis", "survey", "theoretical"}

REGISTRIES = {
    "issues": ["issue_id", "date", "title", "status", "summary", "root_cause", "linked_experiment", "next_action", "detail_path"],
    "experiments": ["experiment_id", "date", "question", "type", "status", "key_variable", "key_result", "linked_issue", "linked_evidence", "detail_path"],
    "evidence": ["evidence_id", "claim", "source", "status", "scope", "limitation"],
    "decisions": ["decision_id", "problem", "selected_option", "reason", "evidence", "limitation", "status"],
    "changes": ["change_id", "date", "summary", "files", "reason", "linked_issue", "linked_decision", "validation", "status"],
    "journal": ["timestamp", "type", "linked_id", "summary"],
}
PREFIXES = {"issues": "ISS", "experiments": "EXP", "evidence": "EVD", "decisions": "DEC", "changes": "CHG"}
ID_FIELDS = {k: v[0] for k, v in REGISTRIES.items() if k != "journal"}
EVIDENCE_STATUS = {"verified", "partial", "unsupported", "contradicted", "invalidated", "uncertain"}

PRESETS = {
    "minimal": {"recording_mode": "minimal", "network_policy": "research_only", "execution_policy": "confirm_high_risk", "default_record_level": "QUICK", "large_file_threshold_mb": 10, "journal_enabled": False, "git_tracking": True, "writing_tracking": False},
    "standard": {"recording_mode": "standard", "network_policy": "research_only", "execution_policy": "confirm_high_risk", "default_record_level": "TRACKED", "large_file_threshold_mb": 10, "journal_enabled": True, "git_tracking": True, "writing_tracking": True},
    "strict": {"recording_mode": "strict", "network_policy": "research_only", "execution_policy": "confirm_high_risk", "default_record_level": "FORMAL", "large_file_threshold_mb": 5, "journal_enabled": True, "git_tracking": True, "writing_tracking": True},
}

STATE_DEFAULTS = {
    "active_problem": "",
    "active_issue": "",
    "current_stage": "idle",
    "record_level": "QUICK",
    "active_experiments": [],
    "active_hypotheses": [],
    "blockers": [],
    "next_actions": [],
    "updated_at": "",
}

WRITING = {
    "reviewer": ("reviewer_map.csv", ["comment_id", "underlying_concern", "technical_requirement", "linked_issue", "linked_experiment", "linked_evidence", "manuscript_change", "response_status"]),
    "figure": ("figure_table.csv", ["item_id", "linked_experiment", "data_source", "generation_method", "validation", "status"]),
    "paper": ("paper_changes.csv", ["location", "change", "reason", "linked_evidence", "status"]),
    "literature": ("literature.csv", ["citation_id", "title", "authors", "year", "source_type", "identifier", "url", "accessed_at", "verification", "linked_evidence"]),
    "search": ("literature_search.csv", ["search_id", "date", "question", "source", "query", "filters", "hits", "screened", "included", "limitations"]),
}

CONFIG_KEYS = {"schema_version", "recording_mode", "network_policy", "execution_policy", "default_record_level", "large_file_threshold_mb", "journal_enabled", "git_tracking", "writing_tracking"}
CAPABILITY_COMMANDS = {"git": "git", "docker": "docker", "node": "node", "r": "Rscript", "pandoc": "pandoc", "latex": "latexmk", "gpu": "nvidia-smi"}

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I),
    re.compile(r"(?i)\b(api[_-]?key|password|passwd|secret|token)\b\s*[:=]\s*\S+"),
    re.compile(r"\b(?:sk|ghp|github_pat)_[A-Za-z0-9_-]{12,}\b"),
]


class ResearchError(RuntimeError):
    pass


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def today() -> str:
    return dt.date.today().isoformat()


def redact(value: object) -> str:
    text = "" if value is None else str(value)
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


def yaml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    return json.dumps(redact(value), ensure_ascii=False)


def dump_simple_yaml(data: dict[str, object]) -> str:
    return "".join(f"{key}: {yaml_scalar(value)}\n" for key, value in data.items())


def parse_simple_yaml(path: Path) -> dict[str, object]:
    data: dict[str, object] = {}
    if not path.exists():
        raise ResearchError(f"Missing file: {path}")
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ResearchError(f"Unsupported YAML at {path}:{number}")
        key, value = line.split(":", 1)
        value = value.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key.strip()):
            raise ResearchError(f"Invalid key at {path}:{number}")
        if value in {"true", "false"}:
            parsed: object = value == "true"
        else:
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                parsed = value
        data[key.strip()] = parsed
    return data


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False, dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    temp_path = Path(handle.name)
    try:
        with handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


@contextmanager
def workspace_lock(research: Path):
    research.mkdir(parents=True, exist_ok=True)
    lock = research / ".write.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise ResearchError(f"Workspace is locked by another writer: {lock}") from exc
    try:
        os.write(fd, f"pid={os.getpid()} time={now_iso()}\n".encode("utf-8"))
        os.close(fd)
        yield
    finally:
        try:
            os.close(fd)
        except OSError:
            pass
        lock.unlink(missing_ok=True)


def research_dir(root: Path) -> Path:
    return root.resolve() / ".research"


def require_workspace(root: Path) -> Path:
    path = research_dir(root)
    if not (path / "config.yaml").is_file():
        raise ResearchError("No research workspace. Ask the user to enable tracking, then run init.")
    return path


def validate_relative(value: str, field: str) -> None:
    if not value:
        return
    candidate = Path(value)
    if candidate.is_absolute() or PureWindowsPath(value).is_absolute() or ".." in candidate.parts:
        raise ResearchError(f"{field} must be a safe project-relative path: {value}")


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def csv_content(fields: list[str], rows: list[dict[str, str]]) -> str:
    import io
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows([{field: redact(row.get(field, "")) for field in fields} for row in rows])
    return stream.getvalue()


def registry_path(research: Path, kind: str) -> Path:
    return research / "registry" / f"{kind}.csv"


def next_id(kind: str, rows: list[dict[str, str]]) -> str:
    stamp = dt.date.today().strftime("%Y%m%d")
    prefix = PREFIXES[kind]
    pattern = re.compile(rf"^{prefix}-{stamp}-(\d{{3}})$")
    used = [int(match.group(1)) for row in rows if (match := pattern.match(row.get(ID_FIELDS[kind], "")))]
    number = max(used, default=0) + 1
    if number > 999:
        raise ResearchError(f"Daily ID space exhausted for {kind}")
    return f"{prefix}-{stamp}-{number:03d}"


def validate_id(kind: str, value: str) -> None:
    prefix = PREFIXES[kind]
    if not re.fullmatch(rf"{prefix}-\d{{8}}-\d{{3}}", value):
        raise ResearchError(f"Invalid {kind} ID; expected {prefix}-YYYYMMDD-NNN")


def write_registry(path: Path, kind: str, rows: list[dict[str, str]]) -> None:
    atomic_write_text(path, csv_content(REGISTRIES[kind], rows))


def append_registry(research: Path, kind: str, row: dict[str, object], requested_id: str = "") -> str:
    path = registry_path(research, kind)
    with workspace_lock(research):
        rows = read_rows(path)
        record_id = ""
        if kind != "journal":
            record_id = requested_id or next_id(kind, rows)
            validate_id(kind, record_id)
            field = ID_FIELDS[kind]
            if any(existing.get(field) == record_id for existing in rows):
                raise ResearchError(f"Duplicate {field}: {record_id}")
            row[field] = record_id
        normalized = {field: redact(row.get(field, "")) for field in REGISTRIES[kind]}
        rows.append(normalized)
        write_registry(path, kind, rows)
    return record_id


def update_registry(research: Path, kind: str, record_id: str, changes: dict[str, object]) -> None:
    path = registry_path(research, kind)
    field = ID_FIELDS[kind]
    with workspace_lock(research):
        rows = read_rows(path)
        matches = [row for row in rows if row.get(field) == record_id]
        if len(matches) != 1:
            raise ResearchError(f"Expected exactly one {record_id}; found {len(matches)}")
        for row in rows:
            if row.get(field) == record_id:
                for key, value in changes.items():
                    if key not in REGISTRIES[kind] or key == field:
                        raise ResearchError(f"Cannot update field {key}")
                    row[key] = redact(value)
        write_registry(path, kind, rows)


def git_metadata(root: Path) -> tuple[str, str]:
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root, text=True, capture_output=True, timeout=5, check=True).stdout.strip()
        dirty = "true" if subprocess.run(["git", "status", "--porcelain"], cwd=root, text=True, capture_output=True, timeout=5, check=True).stdout.strip() else "false"
        return commit or "unavailable", dirty
    except (OSError, subprocess.SubprocessError):
        return "unavailable", "unknown"


def initialize(root: Path, preset: str) -> None:
    research = research_dir(root)
    config_path = research / "config.yaml"
    state_path = research / "STATE.yaml"
    with workspace_lock(research):
        if config_path.exists():
            config = parse_simple_yaml(config_path)
            if int(config.get("schema_version", -1)) != SCHEMA_VERSION:
                raise ResearchError("Existing workspace schema differs; run migrate --check.")
        else:
            config = {"schema_version": SCHEMA_VERSION, **PRESETS[preset]}
            atomic_write_text(config_path, dump_simple_yaml(config))
        if not state_path.exists():
            state = dict(STATE_DEFAULTS)
            state["record_level"] = str(config.get("default_record_level", "TRACKED"))
            state["updated_at"] = now_iso()
            atomic_write_text(state_path, dump_simple_yaml(state))
    generate_dashboard(root, quiet=True)
    print(f"Research workspace initialized.\n\nMode: {config.get('recording_mode', preset)}\nTracking: enabled\nExternal network: current environment policy\n\nTry:\n\"Analyze this experiment anomaly.\"")


def state_update(root: Path, args: argparse.Namespace) -> None:
    research = require_workspace(root)
    path = research / "STATE.yaml"
    allowed = set(STATE_DEFAULTS) - {"updated_at"}
    changes = {}
    for key in allowed:
        value = getattr(args, key, None)
        if value is not None:
            changes[key] = value.split("||") if key in {"active_experiments", "active_hypotheses", "blockers", "next_actions"} and value else ([] if key in {"active_experiments", "active_hypotheses", "blockers", "next_actions"} else value)
    if not changes:
        raise ResearchError("No state fields supplied")
    with workspace_lock(research):
        state = parse_simple_yaml(path)
        state.update(changes)
        state["updated_at"] = now_iso()
        atomic_write_text(path, dump_simple_yaml({key: state.get(key, default) for key, default in STATE_DEFAULTS.items()}))
    print("State updated.")


def add_issue(root: Path, args: argparse.Namespace) -> None:
    research = require_workspace(root)
    validate_relative(args.detail_path, "detail_path")
    record_id = append_registry(research, "issues", {"date": today(), "title": args.title, "status": args.status, "summary": args.summary, "root_cause": args.root_cause, "linked_experiment": args.linked_experiment, "next_action": args.next_action, "detail_path": args.detail_path}, args.id)
    print(record_id)


def add_experiment(root: Path, args: argparse.Namespace) -> None:
    research = require_workspace(root)
    commit, dirty = git_metadata(root)
    manifest = {
        "id": "",
        "record_level": args.record_level,
        "question": args.question,
        "hypothesis": args.hypothesis,
        "type": args.type,
        "status": args.status,
        "issue": args.issue,
        "baseline": args.baseline,
        "changed": args.changed,
        "controlled": args.controlled.split("||") if args.controlled else [],
        "primary_metric": args.primary_metric,
        "decision_criterion": args.decision_criterion,
        "expected_observation": args.expected_observation,
        "falsifying_observation": args.falsifying_observation,
        "analysis_plan": args.analysis_plan,
        "dataset": args.dataset,
        "split": args.split,
        "seed": args.seed,
        "environment": args.environment,
        "commit": commit,
        "git_dirty": dirty,
        "command": args.run_command,
        "metrics": args.metrics.split("||") if args.metrics else [],
        "result": "",
        "can_claim": [],
        "cannot_claim": [],
        "exploratory_interpretations": [],
        "limitations": [],
        "preregistered_at": now_iso(),
    }
    registry = registry_path(research, "experiments")
    with workspace_lock(research):
        rows = read_rows(registry)
        record_id = args.id or next_id("experiments", rows)
        validate_id("experiments", record_id)
        if any(row.get("experiment_id") == record_id for row in rows):
            raise ResearchError(f"Duplicate experiment_id: {record_id}")
        exp_dir = research / "experiments" / record_id
        if exp_dir.exists():
            raise ResearchError(f"Experiment directory already exists: {exp_dir}")
        exp_dir.mkdir(parents=True)
        try:
            manifest["id"] = record_id
            atomic_write_text(exp_dir / "manifest.yaml", dump_simple_yaml(manifest))
            rows.append({field: redact(value) for field, value in {
                "experiment_id": record_id, "date": today(), "question": args.question, "type": args.type, "status": args.status,
                "key_variable": args.changed, "key_result": "", "linked_issue": args.issue, "linked_evidence": "", "detail_path": f".research/experiments/{record_id}/manifest.yaml",
            }.items()})
            write_registry(registry, "experiments", rows)
        except Exception:
            shutil.rmtree(exp_dir, ignore_errors=True)
            raise
    print(record_id)


def update_experiment(root: Path, args: argparse.Namespace) -> None:
    research = require_workspace(root)
    manifest_path = research / "experiments" / args.id / "manifest.yaml"
    with workspace_lock(research):
        manifest = parse_simple_yaml(manifest_path)
        rows = read_rows(registry_path(research, "experiments"))
        matches = [row for row in rows if row.get("experiment_id") == args.id]
        if len(matches) != 1:
            raise ResearchError(f"Expected one experiment registry row for {args.id}")
        list_fields = {"limitations", "can_claim", "cannot_claim", "exploratory_interpretations"}
        for key in ("status", "result", *sorted(list_fields)):
            value = getattr(args, key)
            if value is not None:
                manifest[key] = value.split("||") if key in list_fields and value else ([] if key in list_fields else value)
        for row in rows:
            if row.get("experiment_id") == args.id:
                if args.status is not None:
                    row["status"] = redact(args.status)
                if args.result is not None:
                    row["key_result"] = redact(args.result)
        old_manifest = manifest_path.read_text(encoding="utf-8")
        atomic_write_text(manifest_path, dump_simple_yaml(manifest))
        try:
            write_registry(registry_path(research, "experiments"), "experiments", rows)
        except Exception:
            atomic_write_text(manifest_path, old_manifest)
            raise
    print(f"Updated {args.id}")


def formal_manifest_missing(manifest: dict[str, object]) -> list[str]:
    missing = [field for field in FORMAL_COMMON_FIELDS if not manifest.get(field)]
    experiment_type = str(manifest.get("type", "")).lower()
    if experiment_type not in NON_INTERVENTION_TYPES:
        for field in ("baseline", "changed", "controlled"):
            if not manifest.get(field):
                missing.append(field)
    return missing


def validate_experiment(root: Path, args: argparse.Namespace) -> None:
    research = require_workspace(root)
    validate_id("experiments", args.id)
    manifest = parse_simple_yaml(research / "experiments" / args.id / "manifest.yaml")
    missing = formal_manifest_missing(manifest) if args.level == "formal" else []
    if missing:
        raise ResearchError(f"Experiment {args.id} is not ready for {args.level}: missing {', '.join(missing)}")
    print(json.dumps({"ok": True, "experiment_id": args.id, "level": args.level, "missing": []}, indent=2))


def add_evidence(root: Path, args: argparse.Namespace) -> None:
    if args.status not in EVIDENCE_STATUS:
        raise ResearchError(f"Evidence status must be one of: {', '.join(sorted(EVIDENCE_STATUS))}")
    record_id = append_registry(require_workspace(root), "evidence", {"claim": args.claim, "source": args.source, "status": args.status, "scope": args.scope, "limitation": args.limitation}, args.id)
    print(record_id)


def add_decision(root: Path, args: argparse.Namespace) -> None:
    record_id = append_registry(require_workspace(root), "decisions", {"problem": args.problem, "selected_option": args.selected_option, "reason": args.reason, "evidence": args.evidence, "limitation": args.limitation, "status": args.status}, args.id)
    print(record_id)


def add_change(root: Path, args: argparse.Namespace) -> None:
    for item in filter(None, args.files.split("||")):
        validate_relative(item, "files")
    record_id = append_registry(require_workspace(root), "changes", {"date": today(), "summary": args.summary, "files": args.files, "reason": args.reason, "linked_issue": args.linked_issue, "linked_decision": args.linked_decision, "validation": args.validation, "status": args.status}, args.id)
    print(record_id)


def add_journal(root: Path, args: argparse.Namespace) -> None:
    research = require_workspace(root)
    config = parse_simple_yaml(research / "config.yaml")
    if not config.get("journal_enabled", True):
        raise ResearchError("Journal is disabled by workspace configuration")
    append_registry(research, "journal", {"timestamp": now_iso(), "type": args.type, "linked_id": args.linked_id, "summary": args.summary})
    print("Journal entry added.")


def list_records(root: Path, args: argparse.Namespace) -> None:
    if args.limit <= 0:
        raise ResearchError("limit must be positive; refusing an accidental unbounded registry dump")
    research = require_workspace(root)
    path = registry_path(research, args.kind)
    rows = deque(maxlen=args.limit)
    if path.exists():
        with path.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if not args.id or args.kind == "journal" or row.get(ID_FIELDS[args.kind]) == args.id:
                    rows.append(row)
    print(json.dumps(list(rows), ensure_ascii=False, indent=2))


def update_record(root: Path, args: argparse.Namespace) -> None:
    if args.kind == "journal":
        raise ResearchError("Journal entries are append-only")
    changes: dict[str, str] = {}
    for assignment in args.set_values:
        if "=" not in assignment:
            raise ResearchError(f"Expected field=value: {assignment}")
        field, value = assignment.split("=", 1)
        field = field.strip()
        if field not in REGISTRIES[args.kind] or field == ID_FIELDS[args.kind]:
            raise ResearchError(f"Field cannot be updated for {args.kind}: {field}")
        if field in {"detail_path", "files"}:
            for item in filter(None, value.split("||")):
                validate_relative(item, field)
        if args.kind == "evidence" and field == "status" and value not in EVIDENCE_STATUS:
            raise ResearchError(f"Evidence status must be one of: {', '.join(sorted(EVIDENCE_STATUS))}")
        changes[field] = value
    if not changes:
        raise ResearchError("At least one --set field=value is required")
    validate_id(args.kind, args.id)
    update_registry(require_workspace(root), args.kind, args.id, changes)
    print(f"Updated {args.id}")


def dashboard_text(research: Path) -> str:
    state = parse_simple_yaml(research / "STATE.yaml")
    issues = [row for row in read_rows(registry_path(research, "issues")) if row.get("status") not in {"closed", "resolved", "cancelled"}][-5:]
    experiments = read_rows(registry_path(research, "experiments"))[-5:]
    decisions = read_rows(registry_path(research, "decisions"))[-5:]
    lines = ["# Research Dashboard", "", "Generated from STATE and registries. Do not edit as a database.", "", "## Active Issues", ""]
    lines.extend([f"- {row['issue_id']}: {row['title']} - {row['status']}" for row in issues] or ["- None"])
    lines += ["", "## Recent Experiments", ""]
    lines.extend([f"- {row['experiment_id']}: {row['question']} - {row['status']}" for row in experiments] or ["- None"])
    lines += ["", "## Pending Actions", ""]
    actions = state.get("next_actions", [])
    lines.extend([f"- {item}" for item in actions] if isinstance(actions, list) and actions else ["- None"])
    lines += ["", "## Recent Decisions", ""]
    lines.extend([f"- {row['decision_id']}: {row['selected_option']} - {row['status']}" for row in decisions] or ["- None"])
    lines += ["", f"_Updated: {now_iso()}_", ""]
    return "\n".join(lines)


def generate_dashboard(root: Path, quiet: bool = False) -> None:
    research = require_workspace(root)
    atomic_write_text(research / "DASHBOARD.md", dashboard_text(research))
    if not quiet:
        print("Dashboard updated.")


def show_status(root: Path) -> None:
    research = require_workspace(root)
    state = parse_simple_yaml(research / "STATE.yaml")
    result: dict[str, object] = {"state": state}
    active = str(state.get("active_issue", ""))
    if active:
        result["active_issue_record"] = next((row for row in read_rows(registry_path(research, "issues")) if row.get("issue_id") == active), None)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def init_writing(root: Path, kind: str) -> None:
    research = require_workspace(root)
    config = parse_simple_yaml(research / "config.yaml")
    if not config.get("writing_tracking", True):
        raise ResearchError("Writing tracking is disabled by workspace configuration")
    filename, fields = WRITING[kind]
    path = research / "writing" / filename
    with workspace_lock(research):
        if not path.exists():
            atomic_write_text(path, csv_content(fields, []))
    print(path.relative_to(root.resolve()).as_posix())


def add_writing_record(root: Path, args: argparse.Namespace) -> None:
    research = require_workspace(root)
    config = parse_simple_yaml(research / "config.yaml")
    if not config.get("writing_tracking", True):
        raise ResearchError("Writing tracking is disabled by workspace configuration")
    filename, fields = WRITING[args.kind]
    values: dict[str, str] = {}
    for assignment in args.set_values:
        if "=" not in assignment:
            raise ResearchError(f"Expected field=value: {assignment}")
        field, value = assignment.split("=", 1)
        field = field.strip()
        if field not in fields:
            raise ResearchError(f"Unknown {args.kind} field: {field}")
        values[field] = redact(value)
    identity = fields[0]
    if not values.get(identity):
        raise ResearchError(f"Writing record requires {identity}")
    path = research / "writing" / filename
    with workspace_lock(research):
        rows = read_rows(path)
        if any(row.get(identity) == values[identity] for row in rows):
            raise ResearchError(f"Duplicate {identity}: {values[identity]}")
        rows.append({field: values.get(field, "") for field in fields})
        atomic_write_text(path, csv_content(fields, rows))
    print(values[identity])


def doctor(root: Path) -> None:
    research = research_dir(root)
    report: dict[str, object] = {
        "skill_version": SKILL_VERSION,
        "python": {"available": True, "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"},
        "tools": {name: {"available": shutil.which(command) is not None} for name, command in CAPABILITY_COMMANDS.items()},
        "workspace": {"present": (research / "config.yaml").is_file()},
    }
    if (research / "config.yaml").is_file():
        config = parse_simple_yaml(research / "config.yaml")
        lock = research / ".write.lock"
        lock_age = None
        if lock.exists():
            lock_age = max(0, int(dt.datetime.now().timestamp() - lock.stat().st_mtime))
        report["workspace"] = {
            "present": True,
            "schema_version": config.get("schema_version"),
            "recording_mode": config.get("recording_mode"),
            "network_policy": config.get("network_policy"),
            "write_lock_present": lock.exists(),
            "write_lock_age_seconds": lock_age,
        }
    print(json.dumps(report, ensure_ascii=False, indent=2))


def fingerprint(root: Path, source: str) -> None:
    validate_relative(source, "source")
    root_resolved = root.resolve()
    path = (root_resolved / source).resolve()
    try:
        path.relative_to(root_resolved)
    except ValueError as exc:
        raise ResearchError("source must stay inside the project root") from exc
    if not path.is_file():
        raise ResearchError(f"Artifact not found: {source}")
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    modified = dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).replace(microsecond=0).isoformat()
    print(json.dumps({"path": Path(source).as_posix(), "bytes": size, "sha256": digest.hexdigest(), "modified_at": modified}, indent=2))


def audit(root: Path) -> int:
    research = require_workspace(root)
    errors: list[str] = []
    warnings: list[str] = []
    try:
        config = parse_simple_yaml(research / "config.yaml")
        schema = int(config.get("schema_version", -1))
        if schema != SCHEMA_VERSION:
            errors.append(f"schema_version is {schema}; expected {SCHEMA_VERSION}")
        unknown_config = set(config) - CONFIG_KEYS
        if unknown_config:
            warnings.append(f"config has unknown keys: {sorted(unknown_config)}")
    except (ResearchError, ValueError) as exc:
        errors.append(str(exc))
    try:
        state = parse_simple_yaml(research / "STATE.yaml")
        unknown = set(state) - set(STATE_DEFAULTS)
        if unknown:
            warnings.append(f"STATE has unknown keys: {sorted(unknown)}")
    except ResearchError as exc:
        errors.append(str(exc))

    known_ids: dict[str, set[str]] = {}
    rows_by_kind: dict[str, list[dict[str, str]]] = {}
    for kind, fields in REGISTRIES.items():
        path = registry_path(research, kind)
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != fields:
                errors.append(f"{path.name}: header mismatch")
            rows = list(reader)
        rows_by_kind[kind] = rows
        if kind != "journal":
            id_field = ID_FIELDS[kind]
            ids = [row.get(id_field, "") for row in rows]
            known_ids[kind] = set(ids)
            if len(ids) != len(set(ids)):
                errors.append(f"{path.name}: duplicate IDs")
        for row_number, row in enumerate(rows, 2):
            joined = " ".join(row.values())
            if any(pattern.search(joined) for pattern in SECRET_PATTERNS):
                errors.append(f"{path.name}:{row_number}: possible secret")
            for field in ({"detail_path", "files"} & set(row)):
                for item in filter(None, row[field].split("||")):
                    try:
                        validate_relative(item, field)
                    except ResearchError as exc:
                        errors.append(f"{path.name}:{row_number}: {exc}")
            if kind == "evidence" and row.get("status") not in EVIDENCE_STATUS:
                errors.append(f"{path.name}:{row_number}: invalid evidence status")

    def check_links(kind: str, field: str, target: str) -> None:
        for row_number, row in enumerate(rows_by_kind.get(kind, []), 2):
            for linked in filter(None, row.get(field, "").split("||")):
                if linked not in known_ids.get(target, set()):
                    errors.append(f"{kind}.csv:{row_number}: {field} references missing {linked}")

    check_links("issues", "linked_experiment", "experiments")
    check_links("experiments", "linked_issue", "issues")
    check_links("experiments", "linked_evidence", "evidence")
    check_links("decisions", "evidence", "evidence")
    check_links("changes", "linked_issue", "issues")
    check_links("changes", "linked_decision", "decisions")

    active_issue = str(state.get("active_issue", "")) if "state" in locals() else ""
    if active_issue and active_issue not in known_ids.get("issues", set()):
        errors.append(f"STATE active_issue references missing {active_issue}")
    active_experiments = state.get("active_experiments", []) if "state" in locals() else []
    if isinstance(active_experiments, list):
        for exp_id in active_experiments:
            if exp_id not in known_ids.get("experiments", set()):
                errors.append(f"STATE active_experiments references missing {exp_id}")

    writing_rows: dict[str, list[dict[str, str]]] = {}
    for writing_kind, (filename, fields) in WRITING.items():
        path = research / "writing" / filename
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != fields:
                errors.append(f"writing/{filename}: header mismatch")
            rows = list(reader)
        writing_rows[writing_kind] = rows
        identity = fields[0]
        ids = [row.get(identity, "") for row in rows]
        if len(ids) != len(set(ids)):
            errors.append(f"writing/{filename}: duplicate {identity}")
        for row_number, row in enumerate(rows, 2):
            joined = " ".join(str(value) for value in row.values())
            if any(pattern.search(joined) for pattern in SECRET_PATTERNS):
                errors.append(f"writing/{filename}:{row_number}: possible secret")

    writing_links = {
        "reviewer": [("linked_issue", "issues"), ("linked_experiment", "experiments"), ("linked_evidence", "evidence")],
        "figure": [("linked_experiment", "experiments")],
        "paper": [("linked_evidence", "evidence")],
        "literature": [("linked_evidence", "evidence")],
    }
    for writing_kind, links in writing_links.items():
        for row_number, row in enumerate(writing_rows.get(writing_kind, []), 2):
            for field, target in links:
                for linked in filter(None, row.get(field, "").split("||")):
                    if linked not in known_ids.get(target, set()):
                        errors.append(f"writing/{WRITING[writing_kind][0]}:{row_number}: {field} references missing {linked}")

    exp_ids = known_ids.get("experiments", set())
    exp_root = research / "experiments"
    if exp_root.exists():
        for directory in exp_root.iterdir():
            if directory.is_dir() and directory.name not in exp_ids:
                warnings.append(f"orphan experiment directory: {directory.name}")
    for exp_id in exp_ids:
        manifest = exp_root / exp_id / "manifest.yaml"
        if not manifest.is_file():
            errors.append(f"missing manifest for {exp_id}")
        else:
            try:
                manifest_data = parse_simple_yaml(manifest)
                if manifest_data.get("id") != exp_id:
                    errors.append(f"manifest ID mismatch for {exp_id}")
                if manifest_data.get("record_level") == "FORMAL":
                    missing = formal_manifest_missing(manifest_data)
                    if missing:
                        errors.append(f"formal manifest {exp_id} missing: {', '.join(missing)}")
                issue_id = str(manifest_data.get("issue", ""))
                if issue_id and issue_id not in known_ids.get("issues", set()):
                    errors.append(f"manifest {exp_id} references missing issue {issue_id}")
            except ResearchError as exc:
                errors.append(str(exc))

    print(json.dumps({"ok": not errors, "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


def export_summary(root: Path, output: str) -> None:
    validate_relative(output, "output")
    research = require_workspace(root)
    path = root.resolve() / output
    counts = {kind: len(read_rows(registry_path(research, kind))) for kind in REGISTRIES}
    content = dashboard_text(research) + "\n## Record Counts\n\n" + "\n".join(f"- {kind}: {count}" for kind, count in counts.items()) + "\n"
    atomic_write_text(path, content)
    print(path.relative_to(root.resolve()).as_posix())


class _DigestingReader(io.RawIOBase):
    """Hash the exact bytes consumed by a text/CSV reader without retaining the file."""
    def __init__(self, stream):
        super().__init__()
        self.stream = stream
        self.digest = hashlib.sha256()
        self.byte_count = 0

    def readable(self):
        return True

    def readinto(self, buffer):
        count = self.stream.readinto(buffer)
        if count:
            self.digest.update(memoryview(buffer)[:count])
            self.byte_count += count
        return count

    def close(self):
        try:
            self.stream.close()
        finally:
            super().close()


def _source_path(root: Path, source: str) -> Path:
    validate_relative(source, "source")
    path = (root.resolve() / source).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise ResearchError("source must stay inside the project root") from exc
    if not path.is_file():
        raise ResearchError(f"Source not found: {source}")
    return path


def _source_signature(path: Path):
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns, stat.st_ino


def read_slice(root: Path, source: str, ranges: list[str], expected: str | None = None) -> None:
    """Return exact decoded UTF-8 line ranges with a recoverable, versioned identity."""
    path = _source_path(root, source)
    spans = []
    for item in ranges:
        match = re.fullmatch(r"([1-9]\d*):([1-9]\d*)", item)
        if not match or int(match[1]) > int(match[2]):
            raise ResearchError("range must be positive START:END with START <= END")
        spans.append((int(match[1]), int(match[2])))
    ordered = sorted(spans)
    if any(b[0] <= a[1] for a, b in zip(ordered, ordered[1:])):
        raise ResearchError("overlapping ranges repeat content; request disjoint ranges")
    if expected and not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
        raise ResearchError("expected SHA-256 must contain 64 hexadecimal characters")
    initial = _source_signature(path)
    digesting = _DigestingReader(path.open("rb"))
    chunks = [[] for _ in spans]
    total = 0
    with io.TextIOWrapper(io.BufferedReader(digesting), encoding="utf-8-sig", newline="") as handle:
        for total, line in enumerate(handle, 1):
            for index, (start, end) in enumerate(spans):
                if start <= total <= end:
                    chunks[index].append(line)
    if initial != _source_signature(path):
        raise ResearchError("source changed during reading; use a stable version")
    digest = digesting.digest.hexdigest()
    if expected and digest.lower() != expected.lower():
        raise ResearchError("source changed since the expected SHA-256; refresh evidence before reuse")
    if any(end > total for _, end in spans):
        raise ResearchError(f"range exceeds source length ({total} lines); no silent truncation")
    print(json.dumps({"source": Path(source).as_posix(), "sha256": digest, "bytes": digesting.byte_count,
                      "total_lines": total, "encoding": "utf-8-sig (BOM omitted from decoded text)",
                      "complete_file": sum(b-a+1 for a,b in spans) == total,
                      "ranges": [{"start": a, "end": b, "text": "".join(chunk)} for (a,b),chunk in zip(spans,chunks)]},
                     ensure_ascii=False, indent=2))


def summarize_csv(root: Path, source: str, selected: str, key: str = "", evidence: bool = False) -> None:
    """Stream a CSV into compact numeric, missing-value, and optional key summaries."""
    validate_relative(source, "source")
    root_resolved = root.resolve()
    path = (root_resolved / source).resolve()
    try:
        path.relative_to(root_resolved)
    except ValueError as exc:
        raise ResearchError("source must stay inside the project root") from exc
    if not path.is_file():
        raise ResearchError(f"CSV not found: {source}")
    requested = [item.strip() for item in selected.split(",") if item.strip()]
    key_fields = [item.strip() for item in key.split(",") if item.strip()]
    key_db_path = None
    connection = None
    key_summary = None
    initial = _source_signature(path) if evidence else None
    digesting = _DigestingReader(path.open("rb")) if evidence else None
    evidence_rows = {}
    try:
        handle = io.TextIOWrapper(io.BufferedReader(digesting), encoding="utf-8-sig", newline="") if evidence else path.open("r", encoding="utf-8-sig", newline="")
        with handle:
            reader = csv.DictReader(handle)
            fields = reader.fieldnames or []
            columns = requested or fields
            unknown = sorted((set(columns) | set(key_fields)) - set(fields))
            if unknown:
                raise ResearchError(f"Unknown columns: {', '.join(unknown)}")
            if key_fields:
                temp = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3")
                key_db_path = Path(temp.name)
                temp.close()
                connection = sqlite3.connect(key_db_path)
                connection.execute("CREATE TABLE observed_keys (value TEXT PRIMARY KEY)")
                key_summary = {"fields": key_fields, "missing_rows": 0, "duplicate_rows": 0, "distinct_complete_keys": 0}
            stats = {name: {"missing": 0, "numeric_count": 0, "mean": 0.0, "m2": 0.0, "min": None, "max": None} for name in columns}
            if evidence:
                evidence_rows = {name: {"minimum": None, "maximum": None, "nonfinite_count": 0,
                                       "nonnumeric_count": 0, "invalid_examples": []} for name in columns}
            row_count = 0
            previous_end = reader.line_num
            for row in reader:
                row_count += 1
                record_lines = [previous_end + 1, reader.line_num]
                previous_end = reader.line_num
                if connection is not None and key_summary is not None:
                    values = [(row.get(name) or "").strip() for name in key_fields]
                    if any(not value for value in values):
                        key_summary["missing_rows"] = int(key_summary["missing_rows"]) + 1
                    else:
                        cursor = connection.execute("INSERT OR IGNORE INTO observed_keys(value) VALUES (?)", (json.dumps(values, ensure_ascii=False),))
                        if cursor.rowcount == 0:
                            key_summary["duplicate_rows"] = int(key_summary["duplicate_rows"]) + 1
                for name in columns:
                    raw = (row.get(name) or "").strip()
                    locator = {"record": row_count, "lines": record_lines, "raw_value": row.get(name),
                               "key": {k: row.get(k) for k in key_fields}} if evidence else None
                    if not raw:
                        stats[name]["missing"] += 1
                        continue
                    try:
                        value = float(raw)
                    except ValueError:
                        if evidence:
                            evidence_rows[name]["nonnumeric_count"] += 1
                            if len(evidence_rows[name]["invalid_examples"]) < 3:
                                evidence_rows[name]["invalid_examples"].append(locator)
                        continue
                    if not math.isfinite(value):
                        if evidence:
                            evidence_rows[name]["nonfinite_count"] += 1
                            if len(evidence_rows[name]["invalid_examples"]) < 3:
                                evidence_rows[name]["invalid_examples"].append(locator)
                        continue
                    item = stats[name]
                    if evidence:
                        if item["min"] is None or value < item["min"]:
                            evidence_rows[name]["minimum"] = locator
                        if item["max"] is None or value > item["max"]:
                            evidence_rows[name]["maximum"] = locator
                    item["numeric_count"] += 1
                    count = item["numeric_count"]
                    delta = value - item["mean"]
                    item["mean"] += delta / count
                    item["m2"] += delta * (value - item["mean"])
                    item["min"] = value if item["min"] is None else min(item["min"], value)
                    item["max"] = value if item["max"] is None else max(item["max"], value)
            if connection is not None and key_summary is not None:
                connection.commit()
                key_summary["distinct_complete_keys"] = connection.execute("SELECT COUNT(*) FROM observed_keys").fetchone()[0]
    finally:
        if connection is not None:
            connection.close()
        if key_db_path is not None:
            key_db_path.unlink(missing_ok=True)
    compact = {}
    for name, item in stats.items():
        count = item.pop("numeric_count")
        m2 = item.pop("m2")
        compact[name] = {
            "missing": item["missing"],
            "numeric_count": count,
            "min": item["min"],
            "max": item["max"],
            "mean": round(item["mean"], 12) if count else None,
            "sample_stddev": round(math.sqrt(m2 / (count - 1)), 12) if count > 1 else None,
        }
    result: dict[str, object] = {"source": source, "rows": row_count, "columns": compact}
    if key_summary is not None:
        result["key"] = key_summary
    if evidence:
        if initial != _source_signature(path):
            raise ResearchError("source changed during reading; use a stable CSV version")
        result["raw_ref"] = {"source": Path(source).as_posix(), "sha256": digesting.digest.hexdigest(),
                             "bytes": digesting.byte_count, "locator": "1-based data record and physical line range",
                             "scope": "finite numeric aggregate; not grouped comparability or membership validation"}
        for item in evidence_rows.values():
            item["invalid_examples_exhaustive"] = item["nonfinite_count"] + item["nonnumeric_count"] <= 3
        result["evidence"] = evidence_rows
    print(json.dumps(result, ensure_ascii=False, indent=2))


def migrate(root: Path, check: bool) -> None:
    research = require_workspace(root)
    config = parse_simple_yaml(research / "config.yaml")
    try:
        current = int(config.get("schema_version", 0))
    except (TypeError, ValueError) as exc:
        raise ResearchError("Invalid schema_version") from exc
    if current == SCHEMA_VERSION:
        print("Schema is current; no migration needed.")
        return
    if check:
        print(json.dumps({"current": current, "target": SCHEMA_VERSION, "supported": current == 0}))
        return
    if current != 0:
        raise ResearchError(f"No migration path from schema {current} to {SCHEMA_VERSION}")
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = root.resolve() / ".research-backups" / f"schema-{current}-{stamp}"
    if backup.exists():
        raise ResearchError(f"Backup target already exists: {backup}")
    shutil.copytree(research, backup)
    if not (backup / "config.yaml").is_file():
        raise ResearchError("Backup validation failed")
    with workspace_lock(research):
        upgraded = {"schema_version": SCHEMA_VERSION, **PRESETS["standard"], **{k: v for k, v in config.items() if k != "schema_version"}}
        atomic_write_text(research / "config.yaml", dump_simple_yaml(upgraded))
        state_path = research / "STATE.yaml"
        if not state_path.exists():
            state = dict(STATE_DEFAULTS)
            state["updated_at"] = now_iso()
            atomic_write_text(state_path, dump_simple_yaml(state))
    generate_dashboard(root, quiet=True)
    print(f"Migrated schema 0 to 1. Backup: {backup.relative_to(root.resolve()).as_posix()}")


def add_common_id(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--id", default="", help="Optional explicit ID; normally auto-generated")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage a local evidence-driven research workspace")
    parser.add_argument("--root", default=".", help="Project root (default: current directory)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {SKILL_VERSION}")
    commands = parser.add_subparsers(dest="command", required=True)

    init_p = commands.add_parser("init")
    init_p.add_argument("--preset", choices=sorted(PRESETS), default="standard")

    commands.add_parser("status")
    commands.add_parser("dashboard")
    commands.add_parser("audit")
    commands.add_parser("doctor")

    state_p = commands.add_parser("state")
    for key in set(STATE_DEFAULTS) - {"updated_at"}:
        state_p.add_argument(f"--{key.replace('_', '-')}", dest=key)

    list_p = commands.add_parser("list")
    list_p.add_argument("kind", choices=sorted(REGISTRIES))
    list_p.add_argument("--id", default="")
    list_p.add_argument("--limit", type=int, default=10)
    update_p = commands.add_parser("update")
    update_p.add_argument("kind", choices=sorted(set(REGISTRIES) - {"journal"}))
    update_p.add_argument("--id", required=True)
    update_p.add_argument("--set", dest="set_values", action="append", default=[], help="Repeat field=value")

    issue = commands.add_parser("issue")
    issue_sub = issue.add_subparsers(dest="action", required=True)
    issue_add = issue_sub.add_parser("add")
    add_common_id(issue_add)
    issue_add.add_argument("--title", required=True)
    issue_add.add_argument("--summary", default="")
    issue_add.add_argument("--status", default="open")
    issue_add.add_argument("--root-cause", default="")
    issue_add.add_argument("--linked-experiment", default="")
    issue_add.add_argument("--next-action", default="")
    issue_add.add_argument("--detail-path", default="")

    experiment = commands.add_parser("experiment")
    exp_sub = experiment.add_subparsers(dest="action", required=True)
    exp_add = exp_sub.add_parser("add")
    add_common_id(exp_add)
    exp_add.add_argument("--record-level", choices=["TRACKED", "FORMAL"], default="TRACKED")
    exp_add.add_argument("--question", required=True)
    exp_add.add_argument("--hypothesis", required=True)
    exp_add.add_argument("--type", default="controlled")
    exp_add.add_argument("--status", default="planned")
    exp_add.add_argument("--issue", default="")
    exp_add.add_argument("--baseline", default="")
    exp_add.add_argument("--changed", default="")
    exp_add.add_argument("--controlled", default="", help="Use || between values")
    exp_add.add_argument("--primary-metric", default="")
    exp_add.add_argument("--decision-criterion", default="")
    exp_add.add_argument("--expected-observation", default="")
    exp_add.add_argument("--falsifying-observation", default="")
    exp_add.add_argument("--analysis-plan", default="")
    exp_add.add_argument("--dataset", default="")
    exp_add.add_argument("--split", default="")
    exp_add.add_argument("--seed", default="")
    exp_add.add_argument("--environment", default="")
    exp_add.add_argument("--command", dest="run_command", default="")
    exp_add.add_argument("--metrics", default="", help="Use || between values")
    exp_update = exp_sub.add_parser("update")
    exp_update.add_argument("--id", required=True)
    exp_update.add_argument("--status")
    exp_update.add_argument("--result")
    exp_update.add_argument("--limitations", help="Use || between values")
    exp_update.add_argument("--can-claim", help="Use || between values")
    exp_update.add_argument("--cannot-claim", help="Use || between values")
    exp_update.add_argument("--exploratory-interpretations", help="Use || between values")
    exp_validate = exp_sub.add_parser("validate")
    exp_validate.add_argument("--id", required=True)
    exp_validate.add_argument("--level", choices=["formal"], default="formal")

    evidence = commands.add_parser("evidence")
    ev_sub = evidence.add_subparsers(dest="action", required=True)
    ev_add = ev_sub.add_parser("add")
    add_common_id(ev_add)
    ev_add.add_argument("--claim", required=True)
    ev_add.add_argument("--source", required=True)
    ev_add.add_argument("--status", choices=sorted(EVIDENCE_STATUS), required=True)
    ev_add.add_argument("--scope", default="")
    ev_add.add_argument("--limitation", default="")

    decision = commands.add_parser("decision")
    dec_sub = decision.add_subparsers(dest="action", required=True)
    dec_add = dec_sub.add_parser("add")
    add_common_id(dec_add)
    dec_add.add_argument("--problem", required=True)
    dec_add.add_argument("--selected-option", required=True)
    dec_add.add_argument("--reason", required=True)
    dec_add.add_argument("--evidence", default="")
    dec_add.add_argument("--limitation", default="")
    dec_add.add_argument("--status", default="accepted")

    change = commands.add_parser("change")
    ch_sub = change.add_subparsers(dest="action", required=True)
    ch_add = ch_sub.add_parser("add")
    add_common_id(ch_add)
    ch_add.add_argument("--summary", required=True)
    ch_add.add_argument("--files", default="", help="Project-relative paths separated by ||")
    ch_add.add_argument("--reason", required=True)
    ch_add.add_argument("--linked-issue", default="")
    ch_add.add_argument("--linked-decision", default="")
    ch_add.add_argument("--validation", default="")
    ch_add.add_argument("--status", default="completed")

    journal = commands.add_parser("journal")
    j_sub = journal.add_subparsers(dest="action", required=True)
    j_add = j_sub.add_parser("add")
    j_add.add_argument("--type", required=True)
    j_add.add_argument("--linked-id", default="")
    j_add.add_argument("--summary", required=True)

    writing = commands.add_parser("writing")
    w_sub = writing.add_subparsers(dest="action", required=True)
    w_init = w_sub.add_parser("init")
    w_init.add_argument("kind", choices=sorted(WRITING))
    w_add = w_sub.add_parser("add")
    w_add.add_argument("kind", choices=sorted(WRITING))
    w_add.add_argument("--set", dest="set_values", action="append", default=[], help="Repeat field=value")

    export_p = commands.add_parser("export")
    export_p.add_argument("--output", default=".research/RESEARCH_SUMMARY.md")
    summarize_p = commands.add_parser("summarize-csv")
    summarize_p.add_argument("source", help="Project-relative CSV path")
    summarize_p.add_argument("--columns", default="", help="Comma-separated columns; default is all")
    summarize_p.add_argument("--key", default="", help="Optional comma-separated key columns for exact missing and duplicate checks")
    summarize_p.add_argument("--evidence", action="store_true", help="Include input hash, exact extreme values/locators and invalid-value counts")
    slice_p = commands.add_parser("read-slice", help="Read exact UTF-8 ranges with source identity; no semantic compression")
    slice_p.add_argument("source", help="Project-relative UTF-8 text file")
    slice_p.add_argument("--range", dest="ranges", action="append", required=True, help="1-based inclusive START:END; repeat for disjoint ranges")
    slice_p.add_argument("--expect-sha256", help="Reject a source version different from this checksum")
    fingerprint_p = commands.add_parser("fingerprint")
    fingerprint_p.add_argument("source", help="Project-relative artifact path")
    migrate_p = commands.add_parser("migrate")
    migrate_p.add_argument("--check", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root)
    if not root.exists() or not root.is_dir():
        parser.error(f"Project root does not exist: {root}")
    try:
        if args.command == "init": initialize(root, args.preset)
        elif args.command == "status": show_status(root)
        elif args.command == "state": state_update(root, args)
        elif args.command == "issue" and args.action == "add": add_issue(root, args)
        elif args.command == "experiment" and args.action == "add": add_experiment(root, args)
        elif args.command == "experiment" and args.action == "update": update_experiment(root, args)
        elif args.command == "experiment" and args.action == "validate": validate_experiment(root, args)
        elif args.command == "evidence" and args.action == "add": add_evidence(root, args)
        elif args.command == "decision" and args.action == "add": add_decision(root, args)
        elif args.command == "change" and args.action == "add": add_change(root, args)
        elif args.command == "journal" and args.action == "add": add_journal(root, args)
        elif args.command == "list": list_records(root, args)
        elif args.command == "update": update_record(root, args)
        elif args.command == "dashboard": generate_dashboard(root)
        elif args.command == "audit": return audit(root)
        elif args.command == "doctor": doctor(root)
        elif args.command == "writing" and args.action == "init": init_writing(root, args.kind)
        elif args.command == "writing" and args.action == "add": add_writing_record(root, args)
        elif args.command == "export": export_summary(root, args.output)
        elif args.command == "summarize-csv": summarize_csv(root, args.source, args.columns, args.key, args.evidence)
        elif args.command == "read-slice": read_slice(root, args.source, args.ranges, args.expect_sha256)
        elif args.command == "fingerprint": fingerprint(root, args.source)
        elif args.command == "migrate": migrate(root, args.check)
        else: raise ResearchError("Unsupported command")
        return 0
    except ResearchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
