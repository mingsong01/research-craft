import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "scripts" / "vendor" / "figure-spec" / "figure_renderer.py"
QA = ROOT / "scripts" / "diagram_svg_qa.py"


class FigureSpecRendererTests(unittest.TestCase):
    def test_multibranch_spec_renders_and_passes_topology_qa(self):
        spec = {
            "canvas": {"width": 760, "height": 360},
            "style": {
                "font_size": 13,
                "palette": ["#0072B2", "#E69F00", "#7B61A8", "#D55E00"],
            },
            "nodes": [
                {"id": "input", "label": "Input", "x": 80, "y": 180, "width": 90, "height": 48, "role": "input"},
                {"id": "branch_a", "label": "Branch A", "x": 280, "y": 95, "width": 110, "height": 50, "role": "encoder"},
                {"id": "branch_b", "label": "Branch B", "x": 280, "y": 265, "width": 110, "height": 50, "role": "encoder"},
                {"id": "fusion", "label": "Fusion", "x": 500, "y": 180, "width": 92, "height": 72, "shape": "diamond", "role": "fusion"},
                {"id": "output", "label": "Prediction", "x": 680, "y": 180, "width": 110, "height": 50, "role": "output"},
            ],
            "edges": [
                {"from": "input", "to": "branch_a", "waypoints": [[160, 180], [160, 95]], "type": "main"},
                {"from": "input", "to": "branch_b", "waypoints": [[160, 180], [160, 265]], "type": "main"},
                {"from": "branch_a", "to": "fusion", "waypoints": [[405, 95], [405, 180]], "type": "main"},
                {"from": "branch_b", "to": "fusion", "waypoints": [[405, 265], [405, 180]], "type": "main"},
                {"from": "fusion", "to": "output", "type": "main"},
            ],
        }
        topology = {
            "nodes": [node["id"] for node in spec["nodes"]],
            "edges": [{"source": edge["from"], "target": edge["to"]} for edge in spec["edges"]],
        }

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            spec_path = tmp_path / "figure.json"
            topology_path = tmp_path / "topology.json"
            svg_path = tmp_path / "figure.svg"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            topology_path.write_text(json.dumps(topology), encoding="utf-8")

            render = subprocess.run(
                [sys.executable, str(RENDERER), "render", str(spec_path), "--output", str(svg_path)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(render.returncode, 0, render.stderr or render.stdout)
            self.assertTrue(svg_path.exists())

            lint = subprocess.run(
                [sys.executable, str(QA), "lint", str(svg_path), "--spec", str(topology_path), "--json"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(lint.returncode, 0, lint.stderr or lint.stdout)
            report = json.loads(lint.stdout)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["hard_failures"], 0)
            self.assertEqual(report["nodes"], 5)
            self.assertEqual(report["edges"], 5)

    def test_invalid_reference_is_rejected_before_render(self):
        spec = {
            "nodes": [{"id": "a", "label": "A", "x": 50, "y": 50}],
            "edges": [{"from": "a", "to": "missing"}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.json"
            path.write_text(json.dumps(spec), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(RENDERER), "validate", str(path)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unknown node", result.stdout)


if __name__ == "__main__":
    unittest.main()
