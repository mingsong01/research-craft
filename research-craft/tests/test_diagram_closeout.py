"""Test explicit closeout grammar and editable semantics, not aesthetic taste."""
import importlib.util
import os
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(os.environ.get("RESEARCH_CRAFT_UNDER_TEST", Path(__file__).resolve().parents[1]))
loader = importlib.util.spec_from_file_location("closeout_renderer", ROOT / "scripts/vendor/figure-spec/figure_renderer.py")
R = importlib.util.module_from_spec(loader)
loader.loader.exec_module(R)
NS = {"s": "http://www.w3.org/2000/svg"}


def fixture():
    return {"canvas": {"width": 420, "height": 300}, "style": {"font_size": 20},
            "nodes": [{"id": "module", "label": "Refine", "x": 210, "y": 130, "width": 210, "height": 180}], "edges": []}


class CloseoutTests(unittest.TestCase):
    def test_header_is_text_inside_existing_node(self):
        spec = fixture()
        spec["nodes"][0]["header"] = "Proposed module"
        root = ET.fromstring(R.render_svg(spec))
        self.assertEqual(len(root.findall(".//s:g[@data-node-id]", NS)), 1)
        header = root.find(".//s:text[@data-decoration='module-header']", NS)
        self.assertIsNotNone(header)
        self.assertEqual(header.text, "Proposed module")
        self.assertFalse(root.findall(".//s:path[@data-source]", NS))

    def test_header_does_not_accept_colliding_or_unsupported_content(self):
        for fields in ({"header": "A\nB"}, {"header": "A", "height": 30}, {"header": "A", "shape": "tensor"},
                       {"header": "A", "representation": "tokens"}, {"header": "Far too wide " * 8}):
            spec = fixture()
            spec["nodes"][0].update(fields)
            self.assertTrue(any(i.startswith("CRITICAL") for i in R.validate_spec(spec)), fields)

    def test_header_input_cannot_add_active_svg(self):
        spec = fixture()
        spec["nodes"][0]["header"] = "<script>"
        root = ET.fromstring(R.render_svg(spec))
        self.assertFalse(root.findall(".//s:script", NS))
        self.assertIn("<script>", [t.text for t in root.findall(".//s:text", NS)])

    def test_unknown_or_orphan_representation_style_is_rejected(self):
        for fields in ({"representation_style": "semantic"}, {"representation": "tokens", "representation_style": "guess"}):
            spec = fixture()
            spec["nodes"][0].update(fields)
            self.assertTrue(any(i.startswith("CRITICAL") for i in R.validate_spec(spec)))

    def test_semantic_tokens_are_horizontal_editable_tiles(self):
        spec = fixture()
        spec["nodes"][0].update(representation="tokens", representation_style="semantic")
        root = ET.fromstring(R.render_svg(spec))
        glyph = root.find(".//s:g[@data-decoration='tokens']", NS)
        tiles = []
        for path in glyph.findall("s:path", NS):
            size = re.search(r"h([\d.]+) v([\d.]+)", path.get("d"))
            if size:
                tiles.append(tuple(map(float, size.groups())))
        self.assertTrue(tiles)
        self.assertTrue(all(width > height for width, height in tiles))
        self.assertFalse(root.findall(".//s:image", NS))

    def test_legend_line_style_is_real_svg_and_not_an_edge(self):
        spec = fixture()
        spec["labels"] = [{"text": "Training only", "x": 60, "y": 260, "anchor": "start", "line_style": "dotted"}]
        root = ET.fromstring(R.render_svg(spec))
        sample = root.find(".//s:path[@data-decoration='legend-sample']", NS)
        self.assertIsNotNone(sample)
        self.assertEqual(sample.get("stroke-dasharray"), "3,3")
        self.assertFalse(root.findall(".//s:path[@data-source]", NS))

    def test_invalid_or_centered_line_sample_is_not_silently_accepted(self):
        for fields in ({"anchor": "start", "line_style": "imaginary"}, {"anchor": "middle", "line_style": "solid"}):
            spec = fixture()
            spec["labels"] = [dict(text="Legend", x=60, y=260, **fields)]
            self.assertTrue(any(i.startswith("CRITICAL") for i in R.validate_spec(spec)))


if __name__ == "__main__":
    unittest.main()
