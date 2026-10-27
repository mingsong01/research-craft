import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "scripts" / "vendor" / "drawio-skill"
FIGURE_SPEC = ROOT / "scripts" / "vendor" / "figure-spec"
UPSTREAM_SHA256 = {
    "scripts/vendor/drawio-skill/edgeports.py": "6425714e061bddfecf8350be6872373a2ab7aa2c02b2f8c99482a131244baa00",
    "scripts/vendor/drawio-skill/validate.py": "8cd2f795c3e8336967d3f54b8d0302d048af03d82416310992d1ed38aa06677b",
    "assets/vendor/drawio-skill/colorblind-safe.json": "36779242322a1a0d204a6c3b3582cb245a597db77126d0e502481701b59b1f29",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DiagramMarketSourceTests(unittest.TestCase):
    def test_drawio_runtime_is_hash_identical_to_upstream(self):
        # Hashes were checked against the retained upstream checkout at the
        # commit recorded in scripts/vendor/drawio-skill/COMMIT.txt.
        for relative, expected in UPSTREAM_SHA256.items():
            self.assertEqual(sha256(ROOT / relative), expected, relative)

    def test_drawio_port_allocator_demo(self):
        result = subprocess.run(
            [sys.executable, str(VENDOR / "edgeports.py"), "--demo"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "ok")

    def test_colorblind_style_has_redundant_semantic_roles(self):
        style = json.loads(
            (ROOT / "assets/vendor/drawio-skill/colorblind-safe.json").read_text(encoding="utf-8")
        )
        self.assertEqual(style["roles"]["service"], "primary")
        self.assertEqual(style["roles"]["database"], "success")
        self.assertNotEqual(
            style["palette"]["primary"]["strokeColor"],
            style["palette"]["success"]["strokeColor"],
        )
        self.assertEqual(style["shapes"]["database"], "shape=cylinder3")

    def test_market_sources_and_rejected_pattern_are_documented(self):
        reference = (ROOT / "references/scientific-diagram-design.md").read_text(encoding="utf-8")
        for phrase in (
            "Editorial one-accent",
            "Presentation dark",
            "Paper sketch",
            "Aesthetic hierarchy gate",
            "Cocoon's arrows-behind-nodes convention is explicitly not adopted",
            "Bundled deterministic renderer",
            "Optional generative composition reference",
            "Reference-driven editable reconstruction",
            "Scientific Illustrator",
            "editable working copy",
            "PaperVizAgent/PaperBanana",
        ):
            self.assertIn(phrase, reference)

    def test_figure_spec_is_pinned_attributed_and_commercially_usable(self):
        metadata = (FIGURE_SPEC / "COMMIT.txt").read_text(encoding="utf-8")
        license_text = (FIGURE_SPEC / "LICENSE").read_text(encoding="utf-8")
        renderer = (FIGURE_SPEC / "figure_renderer.py").read_text(encoding="utf-8")
        self.assertIn("a15ffd191515c19faad9310ae5f41c0cb1f6beda", metadata)
        self.assertIn("upstream_sha256", metadata)
        self.assertIn("MIT License", license_text)
        self.assertIn("Adapted from OpenGHz/academic-human-in-the-loop", renderer)
        self.assertIn('"data-source"', renderer)
        self.assertIn("ARROW_TIP_GAP = 5", renderer)

    def test_scientific_illustrator_adaptation_is_attributed(self):
        notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        license_text = (ROOT / "licenses/scientific-illustrator-MIT.txt").read_text(
            encoding="utf-8"
        )
        self.assertIn("icebird1998/scientific-illustrator", notices)
        self.assertIn("No plugin, MCP", notices)
        self.assertIn("MIT License", license_text)


if __name__ == "__main__":
    unittest.main()
