"""Optional publication grammar contracts; no model/API dependencies."""
import importlib.util
import os
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(os.environ.get("RESEARCH_CRAFT_UNDER_TEST", Path(__file__).resolve().parents[1]))
loader = importlib.util.spec_from_file_location("design_renderer", ROOT / "scripts/vendor/figure-spec/figure_renderer.py")
R = importlib.util.module_from_spec(loader)
loader.loader.exec_module(R)
NS = {"s": "http://www.w3.org/2000/svg"}


def fixture():
    return {"canvas": {"width": 600, "height": 300}, "nodes": [
        {"id": "a", "x": 100, "y": 150, "width": 140, "height": 180, "label": "A"},
        {"id": "b", "x": 450, "y": 150, "width": 140, "height": 180, "label": "B"}],
        "edges": [{"from": "a", "to": "b", "source_port": {"side": "right", "offset": .25},
                   "target_port": {"side": "left", "offset": .25}}]}


class DesignTests(unittest.TestCase):
    def test_ports_change_actual_edge_endpoints(self):
        root = ET.fromstring(R.render_svg(fixture()))
        path = next(p for p in root.findall("s:path", NS) if p.get("data-source"))
        self.assertEqual(path.get("d"), "M 175.0,105.0 L 366.0,105.0")

    def test_invalid_port_cannot_silently_fall_back(self):
        for value in ({"side": "left", "offset": 1.1}, {"side": "middle"}, {"side": "left", "offset": True}):
            spec = fixture()
            spec["edges"][0]["source_port"] = value
            self.assertTrue(any(i.startswith("CRITICAL") for i in R.validate_spec(spec)), value)

    def test_nonrectangular_offcenter_ports_rejected(self):
        spec = fixture()
        spec["nodes"][0]["shape"] = "diamond"
        self.assertTrue(any("nonrectangular ports" in i for i in R.validate_spec(spec)))

    def test_long_horizontal_label_avoids_vertical_midpoint(self):
        points = [(30, 70), (30, 500), (220, 500)]
        self.assertEqual(R.edge_label_anchor(points, "longest-horizontal"), (125, 500))
        with self.assertRaises(ValueError):
            R.edge_label_anchor([(30, 70), (30, 500)], "longest-horizontal")

    def test_representation_is_editable_and_not_a_scientific_node(self):
        spec = fixture()
        spec["nodes"][0]["representation"] = "feature-map"
        root = ET.fromstring(R.render_svg(spec))
        self.assertEqual(len(root.findall(".//s:g[@data-node-id]", NS)), 2)
        glyph = root.find(".//s:g[@data-decoration='feature-map']", NS)
        self.assertIsNotNone(glyph)
        self.assertEqual(len(glyph.findall("s:path", NS)), 3)
        self.assertFalse(root.findall(".//s:image", NS))

    def test_representation_cannot_crush_labels(self):
        spec = fixture()
        spec["nodes"][0].update(representation="tokens", height=30)
        self.assertTrue(any("more height" in i for i in R.validate_spec(spec)))

    def test_unknown_grammar_rejected(self):
        spec = fixture()
        spec["nodes"][0]["representation"] = "invented"
        spec["edges"][0]["label_segment"] = "guess"
        issues = R.validate_spec(spec)
        self.assertTrue(any("unknown representation" in i for i in issues))
        self.assertTrue(any("unknown label_segment" in i for i in issues))

    def test_legacy_output_stays_identical(self):
        # Baseline byte comparison is performed by the stage verifier on original demos.
        spec = fixture()
        spec["edges"][0].pop("source_port")
        spec["edges"][0].pop("target_port")
        root = ET.fromstring(R.render_svg(spec))
        path = next(p for p in root.findall("s:path", NS) if p.get("data-source"))
        self.assertEqual(path.get("d"), "M 175.0,150.0 L 366.0,150.0")

    def test_tensor_clips_actual_silhouette_not_empty_corner(self):
        x, y = R.clip_to_shape(0, 0, -200, -100, 200, 100, "tensor")
        self.assertAlmostEqual(x, -92)
        self.assertAlmostEqual(y, -46)

    def test_tensor_faces_do_not_add_nodes_or_edges(self):
        spec = fixture()
        spec["nodes"][0]["shape"] = "tensor"
        spec["edges"][0]["source_port"]["offset"] = .5
        root = ET.fromstring(R.render_svg(spec))
        self.assertEqual(len(root.findall(".//s:g[@data-node-id]", NS)), 2)
        self.assertEqual(len(root.findall(".//s:path[@data-decoration='tensor-face']", NS)), 2)
        self.assertEqual(len(root.findall(".//s:path[@data-source]", NS)), 1)

    def test_straight_vertical_horizontal_label_request_errors(self):
        spec = fixture()
        spec["nodes"][1].update(x=100, y=500)
        spec["edges"][0].update(source_port={"side": "bottom"}, target_port={"side": "top"}, label="flow", label_segment="longest-horizontal")
        with self.assertRaises(ValueError):
            R.render_svg(spec)

    def test_invalid_representation_dimensions_report_without_crash(self):
        for width, height in [(10, 180), (140, "invalid")]:
            spec = fixture()
            spec["nodes"][0].update(representation="tokens", width=width, height=height)
            self.assertTrue(any(i.startswith("CRITICAL") for i in R.validate_spec(spec)))

    def test_horizontal_anchor_on_curve_not_silently_ignored(self):
        spec = fixture()
        spec["edges"][0].update(curve=True, label_segment="longest-horizontal")
        self.assertTrue(any("straight/polyline" in i for i in R.validate_spec(spec)))


if __name__ == "__main__":
    unittest.main()
