import contextlib
import csv
import importlib.util
import io
import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "research.py"
SPEC = importlib.util.spec_from_file_location("research", SCRIPT)
research = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(research)


class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def run_main(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = research.main(["--root", str(self.root), *args])
        return code, stdout.getvalue(), stderr.getvalue()

    def init(self, preset="standard"):
        code, _, error = self.run_main("init", "--preset", preset)
        self.assertEqual(code, 0, error)

    def test_version_alignment(self):
        skill = (SCRIPT.parents[1] / "SKILL.md").read_text(encoding="utf-8")
        readme = (SCRIPT.parents[1] / "README.md").read_text(encoding="utf-8")
        match = re.search(r'^\s*version:\s*"([^"]+)"', skill, re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), research.SKILL_VERSION)
        self.assertIn(f"Skill version: `{research.SKILL_VERSION}`", readme)

    def test_init_is_minimal_and_idempotent(self):
        self.init()
        created = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file())
        self.assertEqual(created, [".research/DASHBOARD.md", ".research/STATE.yaml", ".research/config.yaml"])
        before = (self.root / ".research/config.yaml").read_text(encoding="utf-8")
        self.init("strict")
        self.assertEqual((self.root / ".research/config.yaml").read_text(encoding="utf-8"), before)

    def test_registry_id_generation_and_duplicate_protection(self):
        self.init()
        code, out, _ = self.run_main("issue", "add", "--title", "Anomaly")
        self.assertEqual(code, 0)
        first = out.strip()
        self.assertRegex(first, r"^ISS-\d{8}-001$")
        code, _, error = self.run_main("issue", "add", "--id", first, "--title", "Duplicate")
        self.assertEqual(code, 2)
        self.assertIn("Duplicate", error)
        rows = research.read_rows(self.root / ".research/registry/issues.csv")
        self.assertEqual(len(rows), 1)

    def test_registry_update_is_idempotent_and_validated(self):
        self.init()
        _, out, _ = self.run_main("evidence", "add", "--claim", "c", "--source", "result.csv", "--status", "partial")
        evidence_id = out.strip()
        for _ in range(2):
            code, _, error = self.run_main("update", "evidence", "--id", evidence_id, "--set", "status=invalidated", "--set", "limitation=bad metric")
            self.assertEqual(code, 0, error)
        rows = research.read_rows(self.root / ".research/registry/evidence.csv")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "invalidated")
        code, _, error = self.run_main("update", "evidence", "--id", evidence_id, "--set", "status=made-up")
        self.assertEqual(code, 2)
        self.assertIn("Evidence status", error)

    def test_explicit_ids_cannot_escape_workspace(self):
        self.init()
        code, _, error = self.run_main("experiment", "add", "--id", "../../outside", "--question", "q", "--hypothesis", "h")
        self.assertEqual(code, 2)
        self.assertIn("Invalid experiments ID", error)
        self.assertFalse((self.root.parent / "outside").exists())

    def test_state_update_remains_compact(self):
        self.init()
        code, _, error = self.run_main("state", "--active-problem", "Latency anomaly", "--next-actions", "check timer||run microbenchmark")
        self.assertEqual(code, 0, error)
        state = research.parse_simple_yaml(self.root / ".research/STATE.yaml")
        self.assertEqual(state["next_actions"], ["check timer", "run microbenchmark"])
        self.assertEqual(set(state), set(research.STATE_DEFAULTS))

    def test_experiment_manifest_and_no_git_degradation(self):
        self.init()
        with mock.patch.object(research, "git_metadata", return_value=("unavailable", "unknown")):
            code, out, error = self.run_main("experiment", "add", "--question", "Does x improve y?", "--hypothesis", "x improves y", "--changed", "x", "--controlled", "split||seed")
        self.assertEqual(code, 0, error)
        exp_id = out.strip()
        manifest = research.parse_simple_yaml(self.root / ".research/experiments" / exp_id / "manifest.yaml")
        self.assertEqual(manifest["commit"], "unavailable")
        self.assertEqual(manifest["git_dirty"], "unknown")
        self.assertEqual(manifest["controlled"], ["split", "seed"])

    def test_experiment_failure_cleans_partial_directory(self):
        self.init()
        original = research.write_registry
        def fail(*_args, **_kwargs):
            raise OSError("simulated")
        with mock.patch.object(research, "write_registry", side_effect=fail):
            with self.assertRaises(OSError):
                research.add_experiment(self.root, type("A", (), {"record_level":"TRACKED", "question":"q", "hypothesis":"h", "type":"controlled", "status":"planned", "issue":"", "baseline":"", "changed":"x", "controlled":"", "primary_metric":"", "decision_criterion":"", "expected_observation":"", "falsifying_observation":"", "analysis_plan":"", "dataset":"", "split":"", "seed":"", "environment":"", "run_command":"", "metrics":"", "id":""})())
        exp_root = self.root / ".research/experiments"
        self.assertFalse(exp_root.exists() and any(exp_root.iterdir()))
        research.write_registry = original

    def test_atomic_write_preserves_original_on_replace_failure(self):
        path = self.root / "record.txt"
        path.write_text("old", encoding="utf-8")
        with mock.patch.object(research.os, "replace", side_effect=OSError("simulated")):
            with self.assertRaises(OSError):
                research.atomic_write_text(path, "new")
        self.assertEqual(path.read_text(encoding="utf-8"), "old")
        self.assertEqual(list(self.root.glob("*.tmp")), [])

    def test_dashboard_and_export(self):
        self.init()
        self.run_main("issue", "add", "--title", "Unexpected latency", "--next-action", "define timer")
        self.run_main("state", "--next-actions", "define timer")
        code, _, error = self.run_main("dashboard")
        self.assertEqual(code, 0, error)
        dashboard = (self.root / ".research/DASHBOARD.md").read_text(encoding="utf-8")
        self.assertIn("Unexpected latency", dashboard)
        self.assertIn("define timer", dashboard)
        code, out, _ = self.run_main("export")
        self.assertEqual(code, 0)
        self.assertTrue((self.root / out.strip()).is_file())

    def test_audit_detects_header_and_schema_errors(self):
        self.init()
        self.run_main("issue", "add", "--title", "x")
        issue_path = self.root / ".research/registry/issues.csv"
        issue_path.write_text("bad,header\n1,2\n", encoding="utf-8")
        code, out, _ = self.run_main("audit")
        self.assertEqual(code, 1)
        self.assertIn("header mismatch", out)
        config = research.parse_simple_yaml(self.root / ".research/config.yaml")
        config["schema_version"] = 99
        research.atomic_write_text(self.root / ".research/config.yaml", research.dump_simple_yaml(config))
        code, out, _ = self.run_main("audit")
        self.assertEqual(code, 1)
        self.assertIn("schema_version", out)

    def test_schema_migration_check_and_backup(self):
        research_dir = self.root / ".research"
        research_dir.mkdir()
        research.atomic_write_text(research_dir / "config.yaml", "schema_version: 0\nrecording_mode: \"preview\"\n")
        code, out, _ = self.run_main("migrate", "--check")
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out)["supported"])
        code, out, error = self.run_main("migrate")
        self.assertEqual(code, 0, error)
        self.assertEqual(research.parse_simple_yaml(research_dir / "config.yaml")["schema_version"], 1)
        self.assertEqual(len(list((self.root / ".research-backups").glob("schema-0-*"))), 1)

    def test_secret_redaction_and_unsafe_path_rejection(self):
        self.init()
        code, _, error = self.run_main("journal", "add", "--type", "note", "--summary", "api_key=supersecretvalue")
        self.assertEqual(code, 0, error)
        text = (self.root / ".research/registry/journal.csv").read_text(encoding="utf-8")
        self.assertNotIn("supersecretvalue", text)
        self.assertIn("REDACTED", text)
        code, _, error = self.run_main("issue", "add", "--title", "x", "--detail-path", "../outside.md")
        self.assertEqual(code, 2)
        self.assertIn("project-relative", error)

    def test_writing_registry_is_lazy(self):
        self.init()
        self.assertFalse((self.root / ".research/writing").exists())
        code, out, error = self.run_main("writing", "init", "reviewer")
        self.assertEqual(code, 0, error)
        self.assertEqual(out.strip(), ".research/writing/reviewer_map.csv")

    def test_literature_registry_and_link_audit(self):
        self.init()
        _, evidence_out, _ = self.run_main("evidence", "add", "--claim", "method exists", "--source", "doi:10.example/x", "--status", "verified")
        evidence_id = evidence_out.strip()
        code, out, error = self.run_main(
            "writing", "add", "literature", "--set", "citation_id=CIT-001", "--set", "title=Primary paper",
            "--set", "source_type=journal", "--set", "identifier=doi:10.example/x", "--set", "accessed_at=2026-09-22",
            "--set", "verification=full-text-checked", "--set", f"linked_evidence={evidence_id}"
        )
        self.assertEqual(code, 0, error)
        self.assertEqual(out.strip(), "CIT-001")
        code, audit_out, _ = self.run_main("audit")
        self.assertEqual(code, 0, audit_out)

    def test_literature_search_registry_is_reproducible_and_lazy(self):
        self.init()
        path = self.root / ".research/writing/literature_search.csv"
        self.assertFalse(path.exists())
        code, out, error = self.run_main(
            "writing", "add", "search", "--set", "search_id=SEARCH-001", "--set", "date=2026-09-22",
            "--set", "question=Does method X improve retrieval?", "--set", "source=OpenAlex",
            "--set", "query=title:(method X)", "--set", "filters=2024-2026; peer reviewed",
            "--set", "hits=42", "--set", "screened=18", "--set", "included=7",
            "--set", "limitations=one index"
        )
        self.assertEqual(code, 0, error)
        self.assertEqual(out.strip(), "SEARCH-001")
        rows = research.read_rows(path)
        self.assertEqual(rows[0]["query"], "title:(method X)")
        code, _, error = self.run_main("writing", "add", "search", "--set", "search_id=SEARCH-001")
        self.assertEqual(code, 2)
        self.assertIn("Duplicate search_id", error)

    def test_doctor_and_fingerprint_are_read_only(self):
        code, out, error = self.run_main("doctor")
        self.assertEqual(code, 0, error)
        report = json.loads(out)
        self.assertFalse(report["workspace"]["present"])
        self.assertEqual(report["skill_version"], research.SKILL_VERSION)
        (self.root / "artifact.bin").write_bytes(b"research")
        code, out, error = self.run_main("fingerprint", "artifact.bin")
        self.assertEqual(code, 0, error)
        result = json.loads(out)
        self.assertEqual(result["bytes"], 8)
        self.assertEqual(result["sha256"], "66f62d1807d3821a3865f2573b69c74be033f1341240ac861fefc6d430bff5e0")
        self.assertFalse((self.root / ".research").exists())

    def test_audit_detects_broken_active_state(self):
        self.init()
        self.run_main("state", "--active-issue", "ISS-20000101-001")
        code, out, _ = self.run_main("audit")
        self.assertEqual(code, 1)
        self.assertIn("STATE active_issue references missing", out)

    def test_csv_summary_streams_compact_statistics(self):
        (self.root / "metrics.csv").write_text("step,score,label\n1,0.5,a\n2,0.7,b\n3,,c\n", encoding="utf-8")
        code, out, error = self.run_main("summarize-csv", "metrics.csv", "--columns", "score")
        self.assertEqual(code, 0, error)
        result = json.loads(out)
        self.assertEqual(result["rows"], 3)
        self.assertEqual(result["columns"]["score"]["missing"], 1)
        self.assertAlmostEqual(result["columns"]["score"]["mean"], 0.6)

    def test_csv_summary_checks_keys_without_memory_set(self):
        (self.root / "observations.csv").write_text("id,split,value\na,train,1\na,train,2\n,val,3\nb,test,4\n", encoding="utf-8")
        code, out, error = self.run_main("summarize-csv", "observations.csv", "--columns", "value", "--key", "id,split")
        self.assertEqual(code, 0, error)
        result = json.loads(out)
        self.assertEqual(result["key"]["missing_rows"], 1)
        self.assertEqual(result["key"]["duplicate_rows"], 1)
        self.assertEqual(result["key"]["distinct_complete_keys"], 2)

    def test_formal_experiment_requires_preregistration_contract(self):
        self.init()
        _, out, _ = self.run_main("experiment", "add", "--record-level", "FORMAL", "--question", "Does x improve y?", "--hypothesis", "x improves y")
        exp_id = out.strip()
        code, _, error = self.run_main("experiment", "validate", "--id", exp_id, "--level", "formal")
        self.assertEqual(code, 2)
        self.assertIn("primary_metric", error)
        code, audit_out, _ = self.run_main("audit")
        self.assertEqual(code, 1)
        self.assertIn("formal manifest", audit_out)

        self.temp.cleanup()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.init()
        code, out, error = self.run_main(
            "experiment", "add", "--record-level", "FORMAL", "--question", "Does x improve y?", "--hypothesis", "x improves y",
            "--baseline", "x off", "--changed", "x", "--controlled", "split||seed", "--primary-metric", "accuracy (%)",
            "--decision-criterion", ">= 1 point without cost regression", "--expected-observation", "accuracy rises",
            "--falsifying-observation", "no reproducible rise", "--analysis-plan", "paired seeds and effect interval"
        )
        self.assertEqual(code, 0, error)
        exp_id = out.strip()
        code, validation, error = self.run_main("experiment", "validate", "--id", exp_id)
        self.assertEqual(code, 0, error)
        self.assertTrue(json.loads(validation)["ok"])

    def test_schema_one_legacy_manifest_remains_compatible(self):
        self.init()
        _, out, _ = self.run_main("experiment", "add", "--question", "legacy question", "--hypothesis", "legacy hypothesis")
        exp_id = out.strip()
        path = self.root / ".research/experiments" / exp_id / "manifest.yaml"
        manifest = research.parse_simple_yaml(path)
        for key in ("record_level", "primary_metric", "decision_criterion", "expected_observation", "falsifying_observation", "analysis_plan", "environment", "can_claim", "cannot_claim", "exploratory_interpretations", "preregistered_at"):
            manifest.pop(key, None)
        research.atomic_write_text(path, research.dump_simple_yaml(manifest))
        code, out, _ = self.run_main("audit")
        self.assertEqual(code, 0, out)

    def test_audit_detects_broken_registry_links(self):
        self.init()
        self.run_main("change", "add", "--summary", "patch", "--reason", "test", "--linked-issue", "ISS-20000101-001")
        code, out, _ = self.run_main("audit")
        self.assertEqual(code, 1)
        self.assertIn("references missing ISS-20000101-001", out)

    def test_end_to_end_tracked_flow_audits_cleanly(self):
        self.init()
        _, issue_out, _ = self.run_main("issue", "add", "--title", "Latency regression", "--summary", "p95 increased", "--next-action", "isolate timer")
        issue_id = issue_out.strip()
        _, exp_out, _ = self.run_main("experiment", "add", "--question", "Is timer placement responsible?", "--hypothesis", "Moving the timer removes overhead", "--issue", issue_id, "--baseline", "current timer", "--changed", "timer placement", "--metrics", "p95_ms")
        exp_id = exp_out.strip()
        self.run_main("experiment", "update", "--id", exp_id, "--status", "completed", "--result", "No material change", "--limitations", "single machine")
        self.run_main("evidence", "add", "--claim", "Timer placement is not the main cause", "--source", f".research/experiments/{exp_id}/manifest.yaml", "--status", "partial", "--scope", "current workload", "--limitation", "single machine")
        self.run_main("state", "--active-problem", "Latency regression", "--active-issue", issue_id, "--current-stage", "diagnosis", "--active-experiments", exp_id, "--next-actions", "test cache state")
        self.run_main("dashboard")
        code, out, _ = self.run_main("audit")
        self.assertEqual(code, 0, out)
        self.assertTrue(json.loads(out)["ok"])


if __name__ == "__main__":
    unittest.main()
