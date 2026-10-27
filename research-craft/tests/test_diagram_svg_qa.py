import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "diagram_svg_qa.py"
SPEC = importlib.util.spec_from_file_location("diagram_svg_qa", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def svg(path_d: str, extra_node: bool = False) -> str:
    obstacle = (
        '<g data-node-id="mid" data-role="generic"><rect x="105" y="70" width="50" height="35" fill="#F3F4F6"/></g>'
        if extra_node else ""
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 130">
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="2" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L8,4 L0,8 L2,4 Z"/></marker></defs>
<g data-node-id="a" data-role="encoder"><rect x="10" y="15" width="80" height="30" fill="#DCEEF8"/></g>
<g data-node-id="b" data-role="output"><rect x="140" y="15" width="80" height="30" fill="#F8DDD7"/></g>
{obstacle}
<path data-edge-id="a-b" data-source="a" data-target="b" d="{path_d}" fill="none" marker-end="url(#arrow)"/>
</svg>'''


class DiagramSvgQaTests(unittest.TestCase):
    def test_boundary_clearance_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "ok.svg"
            target.write_text(svg("M 95,30 L 129,30"), encoding="utf-8")
            report = MODULE.lint_svg(target)
            self.assertEqual("PASS", report["status"], report)

    def test_arrow_endpoint_inside_node_is_hard_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "bad.svg"
            target.write_text(svg("M 95,30 L 150,30"), encoding="utf-8")
            report = MODULE.lint_svg(target)
            codes = {finding["code"] for finding in report["findings"]}
            self.assertEqual("FAIL", report["status"])
            self.assertTrue({"center-to-center-arrow", "arrowhead-occluded"} & codes)
            self.assertGreater(report["hard_failures"], 0)

    def test_topology_spec_detects_missing_edge(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "figure.svg"
            contract = root / "topology.json"
            target.write_text(svg("M 95,30 L 129,30"), encoding="utf-8")
            contract.write_text(json.dumps({"nodes": ["a", "b"], "edges": [
                {"source": "a", "target": "b"}, {"source": "b", "target": "a"}
            ]}), encoding="utf-8")
            report = MODULE.lint_svg(target, contract)
            self.assertIn("missing-edge", {finding["code"] for finding in report["findings"]})

    def test_router_avoids_obstacle(self):
        source = MODULE.Rect(10, 30, 70, 36)
        target = MODULE.Rect(250, 30, 70, 36)
        obstacle = MODULE.Rect(135, 10, 60, 80)
        points = MODULE.route_manhattan(source, target, [obstacle])
        self.assertGreaterEqual(len(points), 4)
        self.assertTrue(all(
            not MODULE._segment_hits_rect(a, b, obstacle.expanded(1))
            for a, b in zip(points, points[1:])
        ))


if __name__ == "__main__":
    unittest.main()
