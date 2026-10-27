"""Behavioral counterexamples; also runnable against an immutable baseline."""
import copy
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(os.environ.get("RESEARCH_CRAFT_UNDER_TEST", Path(__file__).resolve().parents[1]))


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


QA = load("reliability_qa", "scripts/diagram_svg_qa.py")
RENDER = load("reliability_renderer", "scripts/vendor/figure-spec/figure_renderer.py")
NS = "http://www.w3.org/2000/svg"


def simple_svg():
    return ET.fromstring('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 150" width="360">
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="2" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L8,4 L0,8 L2,4 Z"/></marker></defs>
<g data-node-id="a"><rect x="25" y="40" width="90" height="50"/><text x="40" y="65" font-size="16">A</text></g>
<g data-node-id="b"><rect x="220" y="40" width="90" height="50"/><text x="240" y="65" font-size="16">B</text></g>
<path data-edge-id="ab" data-source="a" data-target="b" data-edge-type="main" d="M120,65 L209,65" fill="none" stroke="#555555" stroke-width="2" marker-end="url(#arrow)"/>
</svg>''')


def contract(kind="main"):
    return {"nodes": ["a", "b"], "edges": [{"id": "ab", "source": "a", "target": "b", "type": kind}]}


class ReliabilityTests(unittest.TestCase):
    def check_svg(self, root, spec=None, **options):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "figure.svg"
            ET.ElementTree(root).write(path, encoding="utf-8")
            sp = None
            if spec is not None:
                sp = Path(temp) / "topology.json"
                sp.write_text(json.dumps(spec), encoding="utf-8")
            return QA.lint_svg(path, sp, **options)

    def assert_rejected(self, root, code, spec=None, **options):
        result = self.check_svg(root, spec, **options)
        self.assertEqual(result["status"], "FAIL", result)
        self.assertIn(code, {f["code"] for f in result["findings"]}, result)

    def test_duplicate_node_is_rejected(self):
        root = simple_svg()
        root.append(copy.deepcopy(next(e for e in root if e.get("data-node-id") == "a")))
        self.assert_rejected(root, "duplicate-node", contract())

    def test_duplicate_edge_is_rejected(self):
        root = simple_svg()
        root.append(copy.deepcopy(next(e for e in root if e.get("data-source"))))
        self.assert_rejected(root, "duplicate-edge", contract())

    def test_wrong_edge_type_is_rejected(self):
        self.assert_rejected(simple_svg(), "edge-type-mismatch", contract("skip"))

    def test_training_contract_cannot_be_drawn_as_inference(self):
        self.assert_rejected(simple_svg(), "edge-type-mismatch", contract("training-only"))

    def test_training_line_requires_noncolor_encoding(self):
        root = simple_svg()
        next(e for e in root if e.get("data-source")).set("data-edge-type", "training-only")
        self.assert_rejected(root, "training-line-style", contract("training-only"))

    def test_conflicting_training_contract_is_rejected(self):
        root = simple_svg()
        edge = next(e for e in root if e.get("data-source"))
        edge.set("data-edge-type", "training-only")
        edge.set("stroke-dasharray", "8,4")
        spec = contract("main")
        spec["edges"][0]["train_only"] = True
        self.assert_rejected(root, "invalid-contract", spec)

    def test_false_training_condition_without_type_is_enforced(self):
        root = simple_svg()
        edge = next(e for e in root if e.get("data-source"))
        edge.set("data-edge-type", "training-only")
        edge.set("stroke-dasharray", "8,4")
        spec = contract()
        spec["edges"][0].pop("type")
        spec["edges"][0]["train_only"] = False
        self.assert_rejected(root, "edge-type-mismatch", spec)

    def test_contract_training_condition_must_be_boolean(self):
        spec = contract()
        spec["edges"][0]["train_only"] = "false"
        self.assert_rejected(simple_svg(), "invalid-contract", spec)

    def test_node_execution_both_cannot_silently_change(self):
        root = simple_svg()
        edge = next(e for e in root if e.get("data-source"))
        edge.set("data-edge-type", "training-only")
        edge.set("stroke-dasharray", "8,4")
        next(e for e in root if e.get("data-node-id") == "b").set("data-execution", "training-only")
        spec = contract("training-only")
        spec["nodes"] = ["a", {"id": "b", "execution": "both"}]
        self.assert_rejected(root, "node-execution-mismatch", spec)

    def test_training_node_cannot_be_on_inference_path(self):
        root = simple_svg()
        next(e for e in root if e.get("data-node-id") == "b").set("data-execution", "training-only")
        self.assert_rejected(root, "training-node-in-inference", contract())

    def test_valid_training_edge_passes(self):
        root = simple_svg()
        edge = next(e for e in root if e.get("data-source"))
        edge.set("data-edge-type", "training-only")
        edge.set("stroke-dasharray", "8,4")
        self.assertEqual("PASS", self.check_svg(root, contract("training-only"))["status"])

    def test_zero_dash_cannot_disguise_training_line(self):
        root = simple_svg()
        edge = next(e for e in root if e.get("data-source"))
        edge.set("data-edge-type", "training-only")
        edge.set("stroke-dasharray", "0,0")
        self.assert_rejected(root, "training-line-style", contract("training-only"))

    def test_fusion_operator_mismatch_is_rejected(self):
        root = simple_svg()
        next(e for e in root if e.get("data-node-id") == "b").set("data-operation", "add")
        spec = contract()
        spec["nodes"] = ["a", {"id": "b", "operation": "concat"}]
        self.assert_rejected(root, "node-semantic-mismatch", spec)

    def test_tensor_shape_mismatch_is_rejected(self):
        root = simple_svg()
        next(e for e in root if e.get("data-node-id") == "b").set("data-tensor-shape", "[1,32,64,64]")
        spec = contract()
        spec["nodes"] = ["a", {"id": "b", "tensor_shape": [1, 64, 64, 64]}]
        self.assert_rejected(root, "node-semantic-mismatch", spec)

    def test_node_transform_outside_canvas_is_rejected(self):
        root = simple_svg()
        next(e for e in root if e.get("data-node-id") == "a").set("transform", "translate(0,1000)")
        self.assert_rejected(root, "node-out-of-bounds", contract())

    def test_nested_translation_of_complete_diagram_passes(self):
        root = simple_svg()
        group = ET.SubElement(root, f"{{{NS}}}g", {"transform": "translate(5,5)"})
        for e in list(root):
            if e is not group and not e.tag.endswith("defs"):
                root.remove(e)
                group.append(e)
        self.assertEqual("PASS", self.check_svg(root, contract())["status"])

    def test_uniform_scale_and_translation_passes(self):
        root = simple_svg()
        root.set("viewBox", "0 0 740 320")
        group = ET.SubElement(root, f"{{{NS}}}g", {"transform": "translate(5,5) scale(2)"})
        for e in list(root):
            if e is not group and not e.tag.endswith("defs"):
                root.remove(e)
                group.append(e)
        self.assertEqual("PASS", self.check_svg(root, contract())["status"])

    def test_unregistered_arrow_cannot_evade_topology(self):
        root = simple_svg()
        extra = copy.deepcopy(next(e for e in root if e.get("data-source")))
        extra.attrib.pop("data-source")
        root.append(extra)
        self.assert_rejected(root, "unregistered-edge", contract())

    def test_shape_transform_is_not_ignored(self):
        root = simple_svg()
        next(e for e in root.iter() if e.tag.endswith("rect")).set("transform", "translate(0,1000)")
        self.assert_rejected(root, "node-out-of-bounds", contract())

    def test_unsupported_rotation_is_explicit_failure(self):
        root = simple_svg()
        next(e for e in root if e.get("data-node-id") == "a").set("transform", "rotate(30)")
        self.assert_rejected(root, "unsupported-transform", contract())

    def test_curve_command_cannot_be_silently_tokenized_as_line(self):
        root = simple_svg()
        next(e for e in root if e.get("data-source")).set("d", "M120,65 Q160,10 209,65")
        self.assert_rejected(root, "malformed-path", contract())

    def test_old_endpoint_only_contract_remains_supported(self):
        old = {"nodes": ["a", "b"], "edges": [{"source": "a", "target": "b"}]}
        self.assertEqual("PASS", self.check_svg(simple_svg(), old)["status"])

    def test_original_editable_demo_geometry_remains_supported(self):
        fixtures = Path(__file__).parent / "fixtures"
        report = QA.lint_svg(fixtures / "legacy-cross-modal.svg", fixtures / "legacy-topology.json")
        self.assertEqual("PASS", report["status"], report)

    def test_layers_do_not_claim_visual_review_from_static_lint(self):
        result = self.check_svg(simple_svg(), contract())
        self.assertEqual("NOT_REVIEWED", result["layers"]["visual"]["status"])
        self.assertEqual("NOT_CHECKED", result["layers"]["publication"]["status"])

    def test_small_physical_text_is_rejected(self):
        self.assert_rejected(simple_svg(), "font-too-small", contract(), width_mm=35)

    def test_adequate_physical_size_passes_screening(self):
        result = self.check_svg(simple_svg(), contract(), width_mm=180)
        self.assertEqual("PASS", result["layers"]["publication"]["status"], result)

    def test_tiny_physical_arrow_is_rejected(self):
        root = simple_svg()
        next(e for e in root if e.get("data-source")).set("stroke-width", "0.1")
        self.assert_rejected(root, "stroke-too-thin", contract(), width_mm=180)

    def test_tiny_painted_arrow_cannot_hide_in_large_marker_canvas(self):
        root = simple_svg()
        marker = next(e for e in root.iter() if e.tag.endswith("marker"))
        marker.set("refX", "0.25")
        marker.set("refY", "0.5")
        marker[0].set("d", "M0,0 L1,0.5 L0,1 Z")
        self.assert_rejected(root, "arrow-too-small", contract(), width_mm=180)

    def test_small_tspan_cannot_evade_font_screening(self):
        root = simple_svg()
        text = next(e for e in root.iter() if e.tag.endswith("text"))
        ET.SubElement(text, f"{{{NS}}}tspan", {"font-size": "1"}).text = "tiny"
        self.assert_rejected(root, "font-too-small", contract(), width_mm=180)

    def test_arrow_paint_extent_not_marker_canvas_controls_tip(self):
        root = simple_svg()
        marker = next(e for e in root.iter() if e.tag.endswith("marker"))
        marker.set("markerWidth", "10")
        marker.set("markerHeight", "10")
        marker.set("refX", "8")
        marker.set("refY", "4")
        # Painted tip is x=8, exactly at refX. Stop 5 px from target.
        next(e for e in root if e.get("data-source")).set("d", "M120,65 L215,65")
        self.assertEqual("PASS", self.check_svg(root, contract())["status"])

    def test_invalid_physical_size_is_rejected(self):
        self.assert_rejected(simple_svg(), "invalid-physical-size", contract(), width_mm=-1)

    def test_waypoint_label_tracks_real_route(self):
        spec = {"canvas": {"width": 500, "height": 300}, "nodes": [
            {"id": "a", "x": 80, "y": 200, "label": "A"},
            {"id": "b", "x": 400, "y": 200, "label": "B"}],
            "edges": [{"from": "a", "to": "b", "waypoints": [[80, 60], [400, 60]], "label": "route"}]}
        root = ET.fromstring(RENDER.render_svg(spec))
        label = next(e for e in root.iter() if e.tag.endswith("text") and e.text == "route")
        self.assertLessEqual(abs(float(label.get("y")) - 60), 20)

    def test_training_default_is_visibly_distinct(self):
        spec = {"nodes": [{"id": "a", "label": "A", "x": 80, "y": 80},
                          {"id": "b", "label": "B", "x": 300, "y": 80}],
                "edges": [{"from": "a", "to": "b", "type": "training-only"}]}
        root = ET.fromstring(RENDER.render_svg(spec))
        edge = next(e for e in root.iter() if e.get("data-source"))
        self.assertTrue(edge.get("stroke-dasharray"))

    def test_nonfinite_coordinates_are_rejected_before_render(self):
        spec = {"nodes": [{"id": "a", "label": "A", "x": math.nan, "y": 80}]}
        self.assertTrue(any(i.startswith("CRITICAL") for i in RENDER.validate_spec(spec)))

    def test_spec_rejects_explicit_solid_training_path(self):
        spec = {"nodes": [{"id": "a", "label": "A", "x": 80, "y": 80},
                          {"id": "b", "label": "B", "x": 300, "y": 80}],
                "edges": [{"from": "a", "to": "b", "type": "training-only", "style": "solid"}]}
        self.assertTrue(any(i.startswith("CRITICAL") for i in RENDER.validate_spec(spec)))

    def test_checked_demo_satisfies_both_lint_tools(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "figure.svg"
            spec = json.loads((ROOT / "demo/diagram/figure-spec.json").read_text(encoding="utf-8"))
            target.write_text(RENDER.render_svg(spec), encoding="utf-8")
            local = QA.lint_svg(target, ROOT / "demo/diagram/topology.json")
            self.assertEqual("PASS", local["status"], local)
            result = subprocess.run(["node", str(ROOT / "scripts/bybit_svg_profile.mjs"), str(target)], capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
