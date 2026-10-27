import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE_SHA256 = {
    # Authorized context-efficiency candidate; schema/template pins stay unchanged.
    # Historical release bytes are preserved separately, not redefined by this pin.
    "scripts/research.py": "4220c00911c8c3a2e3f02fab37d3d95b73d2ab109e9e3533324ce9c441040b70",
    "assets/templates/experiment-manifest.yaml": "2489ed5fbce06d5bf819104a6a5f51ff60b2a24bf648a7d91961bbaf20f56f5c",
    "references/workspace-schema.md": "b16caafe96573451833f8cd5d95127d56abf215112aed734ed79c41b114df10b",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MarketBenchmarkTests(unittest.TestCase):
    def test_pinned_release_runtime_and_workspace_schema_files(self):
        for relative, expected in BASELINE_SHA256.items():
            self.assertEqual(sha256(ROOT / relative), expected, relative)

    def test_upstream_licenses_and_provenance_are_present(self):
        notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        benchmark = (ROOT / "MARKET_BENCHMARK.md").read_text(encoding="utf-8")
        self.assertIn("obra/superpowers", notices)
        self.assertIn("scientific-agent-skills", notices)
        self.assertIn("Snapshot date: 2026-10-21", benchmark)
        self.assertIn("Star counts are approximate public snapshots", benchmark)
        self.assertIn("tt-a1i/archify", benchmark)
        self.assertIn("cathrynlavery/diagram-design", benchmark)
        self.assertIn("Agents365-ai/drawio-skill", benchmark)
        self.assertIn("69cf672087289033af5138648d3875d3d73fc431", benchmark)
        self.assertIn("57148ac6f7cf8f2d0080f23437ab2929bca15f3e", benchmark)
        self.assertIn("7aa92f73819766eb914fffac66762cf2adb5d828", benchmark)
        self.assertIn("OpenGHz/academic-human-in-the-loop", benchmark)
        self.assertIn("neuromechanist/research-skills", benchmark)
        self.assertIn("PaperBanana", benchmark)
        for relative in (
            "licenses/superpowers-MIT.txt",
            "licenses/kdense-scientific-agent-skills-MIT.txt",
            "licenses/archify-MIT.txt",
            "licenses/diagram-design-MIT.txt",
            "licenses/cocoon-architecture-diagram-MIT.txt",
            "licenses/archscribe-MIT.txt",
        ):
            self.assertIn("MIT License", (ROOT / relative).read_text(encoding="utf-8"))

    def test_execution_level_craft_is_present(self):
        required = {
            "references/workflow.md": ["Design reality gate", "pseudoreplication", "ENGINEERING_VALID"],
            "references/software-research.md": ["four-phase debugging gate", "Single-hypothesis test", "fresh"],
            "references/statistics-causality.md": ["smallest effect size of interest", "equivalence", "multiplicity"],
            "references/evidence-writing.md": ["Scientific prose craft", "confidential", "manuscript change"],
            "references/literature-frontier.md": ["Pilot the search", "full text", "Synthesize by question or theme"],
            "references/scientific-visualization.md": ["render -> inspect -> repair -> rerender", "final publication size"],
            "references/domains/ml-cv.md": ["independent experimental unit", "final test set", "end-to-end latency"],
            "references/domains/systems-performance.md": ["Freeze workload-defining parameters", "tail latency", "correctness oracle"],
            "references/domains/security-privacy.md": ["Build the threat model", "fail-closed", "reidentification risk"],
            "references/domains/rag-llm.md": ["corpus snapshot", "judge-model", "tool success"],
        }
        for relative, phrases in required.items():
            text = (ROOT / relative).read_text(encoding="utf-8")
            for phrase in phrases:
                self.assertIn(phrase, text, f"{relative}: {phrase}")

    def test_hard_craft_cases_are_unique_and_adversarial(self):
        cases = json.loads((ROOT / "evals/market_craft_cases.json").read_text(encoding="utf-8"))
        self.assertEqual(len(cases), 10)
        self.assertEqual(len({case["id"] for case in cases}), 10)
        for case in cases:
            self.assertTrue(case["hidden_trap"])
            self.assertGreaterEqual(len(case["required_behaviors"]), 3)
            self.assertTrue(case["hard_failures"])


if __name__ == "__main__":
    unittest.main()
