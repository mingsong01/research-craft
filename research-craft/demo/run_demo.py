#!/usr/bin/env python3
"""Run an isolated tracked investigation demo and print its compact trail."""

import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "research.py"


def run(root, *args):
    result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), *args], text=True, capture_output=True, check=True)
    return result.stdout.strip()


with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    print(run(root, "init"))
    issue = run(root, "issue", "add", "--title", "Unexpected p95 latency", "--summary", "p95 rose after a deployment", "--next-action", "verify measurement definition")
    experiment = run(root, "experiment", "add", "--question", "Is timer placement causing the apparent regression?", "--hypothesis", "Moving the timer removes the increase", "--issue", issue, "--baseline", "current timer", "--changed", "timer placement", "--controlled", "workload||concurrency||warm-up", "--metrics", "p95_ms")
    run(root, "experiment", "update", "--id", experiment, "--status", "completed", "--result", "No material change", "--limitations", "single machine")
    evidence = run(root, "evidence", "add", "--claim", "Timer placement is not the main cause", "--source", f".research/experiments/{experiment}/manifest.yaml", "--status", "partial", "--scope", "current workload", "--limitation", "single machine")
    run(root, "state", "--active-problem", "Unexpected p95 latency", "--active-issue", issue, "--current-stage", "diagnosis", "--record-level", "TRACKED", "--active-experiments", experiment, "--next-actions", "test cache state")
    run(root, "dashboard")
    print(f"\nIssue: {issue}\nExperiment: {experiment}\nEvidence: {evidence}")
    print("\nAudit:\n" + run(root, "audit"))
    print("\nDashboard:\n" + (root / ".research/DASHBOARD.md").read_text(encoding="utf-8"))
