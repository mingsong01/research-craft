#!/usr/bin/env python3
"""Research-specific topology QA plus adapters for vendored diagram tools.

Obstacle-aware routing is delegated to the unmodified MIT-licensed
``ml-architecture-diagram-skill`` router under ``scripts/vendor``. General SVG
linting is delegated to the vendored Bybit ``svg-diagram`` linter. This module
only adds the research topology contract and the explicit hidden-arrowhead gate.
"""

from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


Point = tuple[float, float]
Segment = tuple[Point, Point]
SVG_NS = "http://www.w3.org/2000/svg"
PATH_TOKEN = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?|[A-Za-z]")
MARKER_REF = re.compile(r"url\(#([^)]+)\)")


@dataclass(frozen=True)
class Rect:
    left: float
    top: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.left + self.width

    @property
    def bottom(self) -> float:
        return self.top + self.height

    @property
    def cx(self) -> float:
        return self.left + self.width / 2

    @property
    def cy(self) -> float:
        return self.top + self.height / 2

    def expanded(self, pad: float) -> "Rect":
        return Rect(self.left - pad, self.top - pad, self.width + 2 * pad, self.height + 2 * pad)

    def contains_open(self, point: Point) -> bool:
        x, y = point
        return self.left < x < self.right and self.top < y < self.bottom


def _num(value: str | None, default: float = math.nan) -> float:
    try:
        return float(value) if value is not None else default
    except ValueError:
        return default


def _segment_hits_rect(a: Point, b: Point, rect: Rect, eps: float = 1e-7) -> bool:
    """Return true when an orthogonal segment enters the rectangle interior."""
    if abs(a[0] - b[0]) <= eps:
        x = a[0]
        lo, hi = sorted((a[1], b[1]))
        return rect.left + eps < x < rect.right - eps and max(lo, rect.top + eps) < min(hi, rect.bottom - eps)
    if abs(a[1] - b[1]) <= eps:
        y = a[1]
        lo, hi = sorted((a[0], b[0]))
        return rect.top + eps < y < rect.bottom - eps and max(lo, rect.left + eps) < min(hi, rect.right - eps)
    return True


def _simplify(points: Sequence[Point]) -> list[Point]:
    result: list[Point] = []
    for point in points:
        if result and point == result[-1]:
            continue
        if len(result) >= 2:
            a, b = result[-2], result[-1]
            if (abs(a[0] - b[0]) < 1e-7 and abs(b[0] - point[0]) < 1e-7) or (
                abs(a[1] - b[1]) < 1e-7 and abs(b[1] - point[1]) < 1e-7
            ):
                result[-1] = point
                continue
        result.append(point)
    return result


def route_manhattan(
    source: Rect,
    target: Rect,
    obstacles: Iterable[Rect] = (),
    *,
    source_gap: float = 5.0,
    target_gap: float = 5.0,
    marker_tip_extension: float = 6.0,
    clearance: float = 14.0,
    port_stub: float = 14.0,
    prior_segments: Iterable[Segment] = (),
) -> list[Point]:
    """Adapt the vendored ML router to explicit painted-tip clearance."""
    vendor_path = Path(__file__).parent / "vendor/ml-architecture-diagram/routing.py"
    module_name = "research_rd_vendored_ml_routing"
    vendor = sys.modules.get(module_name)
    if vendor is None:
        module_spec = importlib.util.spec_from_file_location(module_name, vendor_path)
        if module_spec is None or module_spec.loader is None:
            raise RuntimeError(f"cannot load vendored router: {vendor_path}")
        vendor = importlib.util.module_from_spec(module_spec)
        sys.modules[module_name] = vendor
        module_spec.loader.exec_module(vendor)

    def box(rect: Rect) -> dict[str, float]:
        return {"x": rect.left, "y": rect.top, "w": rect.width, "h": rect.height}

    boxes = {"source": box(source), "target": box(target)}
    for index, obstacle in enumerate(obstacles):
        boxes[f"obstacle-{index}"] = box(obstacle)
    pullback = marker_tip_extension + target_gap
    points = vendor._route_one(
        "source", "target", boxes, list(prior_segments), [],
        clearance=clearance, stub=port_stub + pullback + 6.0,
    )
    if len(points) < 2:
        raise ValueError("vendored router returned no visible route")

    first, second = points[0], points[1]
    if abs(first[0] - second[0]) >= abs(first[1] - second[1]):
        points[0] = (first[0] + (source_gap if second[0] > first[0] else -source_gap), first[1])
    else:
        points[0] = (first[0], first[1] + (source_gap if second[1] > first[1] else -source_gap))
    previous, last = points[-2], points[-1]
    if abs(last[0] - previous[0]) >= abs(last[1] - previous[1]):
        points[-1] = (last[0] - (pullback if last[0] > previous[0] else -pullback), last[1])
    else:
        points[-1] = (last[0], last[1] - (pullback if last[1] > previous[1] else -pullback))
    return _simplify(points)


def path_d(points: Sequence[Point]) -> str:
    if len(points) < 2:
        raise ValueError("a route needs at least two points")
    commands = [f"M {points[0][0]:g},{points[0][1]:g}"]
    commands.extend(f"L {point[0]:g},{point[1]:g}" for point in points[1:])
    return " ".join(commands)


def parse_path(d: str) -> list[Point]:
    if re.sub(PATH_TOKEN, "", d).replace(",", "").strip():
        raise ValueError("invalid path syntax")
    tokens = PATH_TOKEN.findall(d.replace(",", " "))
    points: list[Point] = []
    command = None
    index = 0
    current = (0.0, 0.0)
    while index < len(tokens):
        token = tokens[index]
        if token.isalpha():
            command = token
            index += 1
            if command.upper() not in {"M", "L", "H", "V"}:
                raise ValueError(f"unsupported path command {command}; use M/L/H/V for deterministic QA")
            if command.upper() == "M" and points:
                raise ValueError("multiple subpaths cannot certify one directed connection")
        if command is None:
            raise ValueError("path lacks an initial command")
        relative = command.islower()
        upper = command.upper()
        if upper in {"M", "L"}:
            if index + 1 >= len(tokens):
                raise ValueError("path coordinate pair is incomplete")
            x, y = float(tokens[index]), float(tokens[index + 1])
            index += 2
            current = (current[0] + x, current[1] + y) if relative else (x, y)
        elif upper == "H":
            x = float(tokens[index]); index += 1
            current = (current[0] + x if relative else x, current[1])
        elif upper == "V":
            y = float(tokens[index]); index += 1
            current = (current[0], current[1] + y if relative else y)
        else:
            raise ValueError(f"unsupported path command {command}; use M/L/H/V for deterministic QA")
        if not all(math.isfinite(v) for v in current):
            raise ValueError("path coordinates must be finite")
        points.append(current)
        if upper == "M":
            command = "l" if relative else "L"
    return _simplify(points)


def _transforms(root: ET.Element, findings: list) -> dict:
    """Resolve nested translations and positive uniform scales; reject other transforms.

    The supported subset preserves orthogonal routes and isotropic marker geometry.
    Rotation, reflection, shear, CSS transforms and nested viewports need a native
    renderer/normalizer, rather than a false geometry PASS.
    """
    result = {}

    def visit(element, parent):
        scale, tx, ty = parent
        value = element.get("transform", "")
        local = (1.0, 0.0, 0.0)
        try:
            matches = list(re.finditer(r"([A-Za-z]+)\s*\(([^)]*)\)", value))
            if re.sub(r"([A-Za-z]+)\s*\(([^)]*)\)", "", value).strip():
                raise ValueError("invalid transform syntax")
            for match in matches:
                name, raw = match.groups()
                v = [float(x) for x in re.split(r"[\s,]+", raw.strip()) if x]
                if not all(math.isfinite(x) for x in v):
                    raise ValueError("nonfinite transform")
                if name == "translate" and len(v) in {1, 2}:
                    item = (1.0, v[0], v[1] if len(v) == 2 else 0.0)
                elif name == "scale" and len(v) in {1, 2} and v[0] > 0 and (len(v) == 1 or v[1] == v[0]):
                    item = (v[0], 0.0, 0.0)
                elif name == "matrix" and len(v) == 6 and v[1] == v[2] == 0 and v[0] == v[3] and v[0] > 0:
                    item = (v[0], v[4], v[5])
                else:
                    raise ValueError(f"unsupported {name}; normalize with a native vector tool")
                a, x, y = local
                b, u, w = item
                local = (a * b, x + a * u, y + a * w)
            a, x, y = local
            current = (scale * a, tx + scale * x, ty + scale * y)
            if "transform" in element.get("style", "").lower() or (_local(element) == "style" and re.search(r"\btransform\s*:", element.text or "", re.I)):
                raise ValueError("CSS transforms are outside the certified subset")
            if element is not root and _local(element) == "svg":
                raise ValueError("nested SVG viewports are outside the certified subset")
        except ValueError as error:
            findings.append({"severity": "error", "code": "unsupported-transform", "message": str(error)})
            current = parent
        result[id(element)] = current
        for child in element:
            visit(child, current)

    visit(root, (1.0, 0.0, 0.0))
    return result


def _world_point(point, transform):
    scale, tx, ty = transform
    return point[0] * scale + tx, point[1] * scale + ty


def _local(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def _shape_box(element: ET.Element) -> Rect | None:
    kind = _local(element)
    if kind == "rect":
        return Rect(_num(element.get("x"), 0), _num(element.get("y"), 0), _num(element.get("width")), _num(element.get("height")))
    if kind == "circle":
        cx, cy, radius = _num(element.get("cx")), _num(element.get("cy")), _num(element.get("r"))
        return Rect(cx - radius, cy - radius, 2 * radius, 2 * radius)
    if kind == "ellipse":
        cx, cy = _num(element.get("cx")), _num(element.get("cy"))
        rx, ry = _num(element.get("rx")), _num(element.get("ry"))
        return Rect(cx - rx, cy - ry, 2 * rx, 2 * ry)
    if kind == "polygon":
        values = [float(value) for value in re.findall(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?", element.get("points", ""))]
        if len(values) < 6 or len(values) % 2:
            return None
        xs, ys = values[0::2], values[1::2]
        return Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
    return None


def _node_shape(group: ET.Element) -> ET.Element | None:
    return next((child for child in group if _local(child) in {"rect", "circle", "ellipse", "polygon"}), None)


def _node_boxes(root: ET.Element, transforms=None, findings=None) -> tuple[dict[str, Rect], dict[str, str]]:
    boxes: dict[str, Rect] = {}
    roles: dict[str, str] = {}
    findings = findings if findings is not None else []
    seen = set()
    for group in root.iter():
        node_id = group.attrib.get("data-node-id")
        if not node_id:
            continue
        if node_id in seen:
            findings.append({"severity": "error", "code": "duplicate-node", "message": f"duplicate node ID {node_id}"})
        seen.add(node_id)
        shape = _node_shape(group)
        if shape is None:
            findings.append({"severity": "error", "code": "unsupported-node-shape", "message": f"node {node_id} needs a direct rect/circle/ellipse/polygon"})
            continue
        box = _shape_box(shape)
        if box is None or not all(math.isfinite(value) for value in (box.left, box.top, box.width, box.height)) or box.width <= 0 or box.height <= 0:
            findings.append({"severity": "error", "code": "invalid-node-geometry", "message": f"node {node_id} has invalid geometry"})
            continue
        if transforms:
            scale, tx, ty = transforms[id(shape)]
            box = Rect(box.left * scale + tx, box.top * scale + ty, box.width * scale, box.height * scale)
        boxes[node_id] = box
        roles[node_id] = group.attrib.get("data-role", "generic")
    return boxes, roles


def _marker_extensions(root: ET.Element) -> tuple[dict[str, float], list[dict[str, str]]]:
    extensions: dict[str, float] = {}
    findings: list[dict[str, str]] = []
    for marker in (item for item in root.iter() if _local(item) == "marker"):
        marker_id = marker.attrib.get("id")
        width, height = _num(marker.get("markerWidth")), _num(marker.get("markerHeight"))
        ref_x, ref_y = _num(marker.get("refX")), _num(marker.get("refY"))
        if not marker_id:
            continue
        if marker.get("markerUnits") != "userSpaceOnUse" or marker.get("orient") != "auto":
            findings.append({"severity": "error", "code": "marker-semantics", "message": f"marker {marker_id} needs markerUnits=userSpaceOnUse and orient=auto"})
        if not all(math.isfinite(value) for value in (width, height, ref_x, ref_y)) or width != height:
            findings.append({"severity": "error", "code": "marker-geometry", "message": f"marker {marker_id} needs finite square geometry"})
            continue
        try:
            if marker.get("viewBox") or marker.get("transform"):
                raise ValueError("marker viewBox/transform requires native normalization")
            xs = []
            for child in marker:
                if _local(child) == "polygon":
                    box = _shape_box(child)
                    if box:
                        xs.append(box.right)
                elif _local(child) == "path":
                    xs.extend(p[0] for p in parse_path(re.sub(r"[Zz]\s*$", "", child.get("d", ""))))
                else:
                    raise ValueError("only filled polygon/linear-path markers are certified")
            if not xs:
                raise ValueError("marker has no supported painted arrowhead")
            extensions[marker_id] = max(0.0, max(xs) - ref_x)
        except (ValueError, IndexError) as error:
            findings.append({"severity": "error", "code": "marker-geometry", "message": f"marker {marker_id}: {error}"})
    return extensions, findings


def _endpoint_gap(point: Point, prior: Point, box: Rect, tip_extension: float, target: bool) -> float:
    dx, dy = ((point[0] - prior[0], point[1] - prior[1]) if target
              else (prior[0] - point[0], prior[1] - point[1]))
    if abs(dx) >= abs(dy):
        if dx > 0:
            return box.left - (point[0] + tip_extension) if target else point[0] - box.right
        return (point[0] - tip_extension) - box.right if target else box.left - point[0]
    if dy > 0:
        return box.top - (point[1] + tip_extension) if target else point[1] - box.bottom
    return (point[1] - tip_extension) - box.bottom if target else box.top - point[1]


def _painted_marker_size(marker: ET.Element) -> float:
    """Smallest painted dimension, rather than the empty marker viewport."""
    boxes = []
    for child in marker:
        if _local(child) == "path":
            try:
                pts = parse_path(re.sub(r"[Zz]\s*$", "", child.get("d", "")))
            except (ValueError, IndexError):
                return math.nan
            if pts:
                xs, ys = zip(*pts)
                boxes.append(Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)))
        else:
            box = _shape_box(child)
            if box:
                boxes.append(box)
    if not boxes:
        return math.nan
    return min(max(b.right for b in boxes) - min(b.left for b in boxes),
               max(b.bottom for b in boxes) - min(b.top for b in boxes))


def lint_svg(svg_path: Path, spec_path: Path | None = None, *, width_mm: float | None = None,
             min_font_pt: float = 7.5, min_stroke_pt: float = 0.5, min_arrow_pt: float = 2.5) -> dict:
    findings: list[dict[str, str]] = []
    try:
        root = ET.parse(svg_path).getroot()
    except (ET.ParseError, OSError) as error:
        return {"status": "FAIL", "nodes": 0, "edges": 0, "errors": 1, "warnings": 0, "hard_failures": 1,
                "findings": [{"severity": "error", "code": "invalid-svg", "message": str(error)}],
                "layers": {name: {"status": "NOT_CHECKED"} for name in ("topology", "geometry", "publication", "visual")}}

    if _local(root) != "svg":
        findings.append({"severity": "error", "code": "invalid-svg", "message": "root must be svg"})

    view_box = [_num(value) for value in root.attrib.get("viewBox", "").replace(",", " ").split()]
    if len(view_box) != 4 or not all(math.isfinite(value) for value in view_box) or min(view_box[2:]) <= 0:
        findings.append({"severity": "error", "code": "invalid-viewbox", "message": "SVG needs a finite four-number viewBox"})
        view_box = [0, 0, 0, 0]
    transforms = _transforms(root, findings)
    boxes, roles = _node_boxes(root, transforms, findings)
    if not boxes:
        findings.append({"severity": "error", "code": "empty-diagram", "message": "no supported model nodes found"})
    markers, marker_findings = _marker_extensions(root)
    findings.extend(marker_findings)

    xml_ids = [e.get("id") for e in root.iter() if e.get("id")]
    for value, count in Counter(xml_ids).items():
        if count > 1:
            findings.append({"severity": "error", "code": "duplicate-svg-id", "message": f"SVG id {value} appears {count} times"})
    for node_id, box in boxes.items():
        if box.left < view_box[0] or box.top < view_box[1] or box.right > view_box[0] + view_box[2] or box.bottom > view_box[1] + view_box[3]:
            findings.append({"severity": "error", "code": "node-out-of-bounds", "message": f"node {node_id} is clipped by the viewBox"})
    ids = sorted(boxes)
    for index, left_id in enumerate(ids):
        a = boxes[left_id]
        for right_id in ids[index + 1:]:
            b = boxes[right_id]
            if max(a.left, b.left) < min(a.right, b.right) and max(a.top, b.top) < min(a.bottom, b.bottom):
                findings.append({"severity": "error", "code": "node-overlap", "message": f"nodes {left_id} and {right_id} overlap"})

    actual_edges: set[tuple[str, str]] = set()
    edge_records = []
    edge_ids = set()
    edge_keys = set()
    training_nodes = {e.get("data-node-id") for e in root.iter() if e.get("data-execution") == "training-only"}
    allowed_types = {"main", "skip", "auxiliary", "feedback", "training-only", "residual", "conditioning"}
    for path in (e for e in root.iter() if _local(e) == "path" and e.get("marker-end")):
        if not path.get("data-source") or not path.get("data-target"):
            findings.append({"severity": "error", "code": "unregistered-edge", "message": "every arrowed path needs source/target metadata"})
    edge_count = 0
    for path in (item for item in root.iter() if _local(item) == "path" and item.get("data-source") and item.get("data-target")):
        edge_count += 1
        source_id, target_id = path.get("data-source", ""), path.get("data-target", "")
        actual_edges.add((source_id, target_id))
        kind = path.get("data-edge-type", "main")
        edge_id = path.get("data-edge-id")
        key = (source_id, target_id, kind)
        if key in edge_keys or (edge_id and edge_id in edge_ids):
            findings.append({"severity": "error", "code": "duplicate-edge", "message": f"duplicate connection {source_id}->{target_id} ({kind})"})
        edge_keys.add(key)
        if edge_id:
            edge_ids.add(edge_id)
        edge_records.append({"source": source_id, "target": target_id, "type": kind, "id": edge_id})
        if kind not in allowed_types:
            findings.append({"severity": "error", "code": "invalid-edge-type", "message": f"unknown edge type {kind}"})
        dash_values = [_num(v) for v in re.split(r"[\s,]+", path.get("stroke-dasharray", "").strip()) if v]
        if kind == "training-only" and (not dash_values or not all(math.isfinite(v) and v > 0 for v in dash_values)):
            findings.append({"severity": "error", "code": "training-line-style", "message": f"training-only edge {source_id}->{target_id} needs a non-color dash encoding"})
        if path.get("data-train-only") in {"true", "false"} and (path.get("data-train-only") == "true") != (kind == "training-only"):
            findings.append({"severity": "error", "code": "edge-type-mismatch", "message": "train-only metadata conflicts with edge type"})
        if kind != "training-only" and {source_id, target_id} & training_nodes:
            findings.append({"severity": "error", "code": "training-node-in-inference", "message": f"ordinary edge {source_id}->{target_id} touches a training-only node"})
        if source_id not in boxes or target_id not in boxes:
            findings.append({"severity": "error", "code": "disconnected-route", "message": f"edge {source_id}->{target_id} references a missing node"})
            continue
        marker_match = MARKER_REF.fullmatch(path.get("marker-end", ""))
        if not marker_match or marker_match.group(1) not in markers:
            findings.append({"severity": "error", "code": "missing-arrowhead", "message": f"edge {source_id}->{target_id} lacks a valid marker-end"})
            continue
        try:
            points = [_world_point(p, transforms[id(path)]) for p in parse_path(path.get("d", ""))]
        except (ValueError, IndexError) as error:
            findings.append({"severity": "error", "code": "malformed-path", "message": f"edge {source_id}->{target_id}: {error}"})
            continue
        if len(points) < 2:
            findings.append({"severity": "error", "code": "disconnected-route", "message": f"edge {source_id}->{target_id} has no visible segment"})
            continue
        if any(abs(a[0] - b[0]) > 1e-7 and abs(a[1] - b[1]) > 1e-7 for a, b in zip(points, points[1:])):
            findings.append({"severity": "error", "code": "non-orthogonal-route", "message": f"edge {source_id}->{target_id} is not Manhattan-routed"})
        if boxes[source_id].contains_open(points[0]) or boxes[target_id].contains_open(points[-1]):
            findings.append({"severity": "error", "code": "center-to-center-arrow", "message": f"edge {source_id}->{target_id} begins or ends inside a node"})
        edge_scale = transforms[id(path)][0]
        marker_extension = markers[marker_match.group(1)] * edge_scale
        source_gap = _endpoint_gap(points[0], points[1], boxes[source_id], 0.0, False)
        target_gap = _endpoint_gap(points[-1], points[-2], boxes[target_id], marker_extension, True)
        if not 3.0 * edge_scale <= source_gap <= 16.0 * edge_scale:
            findings.append({"severity": "error", "code": "source-boundary-gap", "message": f"edge {source_id}->{target_id} source gap is {source_gap:.1f}px, expected 3–16px"})
        if not 3.0 * edge_scale <= target_gap <= 16.0 * edge_scale:
            findings.append({"severity": "error", "code": "arrowhead-occluded", "message": f"edge {source_id}->{target_id} painted tip gap is {target_gap:.1f}px; arrowhead may be hidden or disconnected"})
        last_length = abs(points[-1][0] - points[-2][0]) + abs(points[-1][1] - points[-2][1])
        if last_length < marker_extension + 6 * edge_scale:
            findings.append({"severity": "error", "code": "ambiguous-direction", "message": f"edge {source_id}->{target_id} final segment is too short to show direction"})
        for node_id, box in boxes.items():
            if node_id in {source_id, target_id}:
                continue
            if any(_segment_hits_rect(a, b, box.expanded(1.0)) for a, b in zip(points, points[1:])):
                findings.append({"severity": "error", "code": "edge-through-node", "message": f"edge {source_id}->{target_id} crosses unrelated node {node_id}"})

    legend = {item.attrib.get("data-legend-role"): item.attrib.get("fill", "").lower() for item in root.iter() if item.attrib.get("data-legend-role")}
    node_fills: dict[str, set[str]] = {}
    for group in root.iter():
        node_id = group.attrib.get("data-node-id")
        if not node_id:
            continue
        shape = _node_shape(group)
        if shape is not None:
            node_fills.setdefault(roles.get(node_id, "generic"), set()).add(shape.attrib.get("fill", "").lower())
    for role, fills in node_fills.items():
        if role in legend and legend[role] not in fills:
            findings.append({"severity": "error", "code": "legend-color-mismatch", "message": f"legend role {role} does not match node fill {sorted(fills)}"})

    semantic_coverage = False
    if spec_path:
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            expected_node_list = [n if isinstance(n, str) else n["id"] for n in spec["nodes"]]
            expected_nodes = set(expected_node_list)
            expected_records = spec["edges"]
            expected_edges = {(edge["source"], edge["target"]) for edge in expected_records}
            if len(expected_nodes) != len(expected_node_list):
                raise ValueError("contract has duplicate nodes")
            expected_keys = [(e["source"], e["target"], e.get("type", "main")) for e in expected_records]
            if len(expected_keys) != len(set(expected_keys)):
                raise ValueError("contract has duplicate connections")
            semantic_coverage = all("type" in e or "train_only" in e for e in expected_records)
            for expected in expected_records:
                if "train_only" in expected and not isinstance(expected["train_only"], bool):
                    raise ValueError("contract train_only must be boolean")
                if "train_only" in expected and "type" in expected and bool(expected["train_only"]) != (expected["type"] == "training-only"):
                    raise ValueError("contract train_only conflicts with type")
                candidates = [e for e in edge_records if (e["source"], e["target"]) == (expected["source"], expected["target"])]
                if expected.get("id"):
                    candidates = [e for e in candidates if e["id"] == expected["id"]]
                    if not candidates:
                        findings.append({"severity": "error", "code": "edge-id-mismatch", "message": f"contract edge ID {expected['id']} is absent"})
                kind = "training-only" if expected.get("train_only") else expected.get("type")
                if kind is not None and candidates and not any(e["type"] == kind for e in candidates):
                    findings.append({"severity": "error", "code": "edge-type-mismatch", "message": f"{expected['source']}->{expected['target']} must have type {kind}"})
                if expected.get("train_only") is False and any(e["type"] == "training-only" for e in candidates):
                    findings.append({"severity": "error", "code": "edge-type-mismatch", "message": "non-training contract edge was rendered training-only"})
            for node in spec["nodes"]:
                if isinstance(node, dict) and "execution" in node:
                    actual_execution = next((e.get("data-execution", "both") for e in root.iter() if e.get("data-node-id") == node["id"]), None)
                    if actual_execution is not None and actual_execution != node["execution"]:
                        findings.append({"severity": "error", "code": "node-execution-mismatch", "message": f"{node['id']} execution differs from contract"})
                if isinstance(node, dict):
                    actual = next((e for e in root.iter() if e.get("data-node-id") == node["id"]), None)
                    if actual is not None:
                        for field in ("operation", "stage", "tensor_shape"):
                            if field in node:
                                expected = json.dumps(node[field], separators=(",", ":")) if isinstance(node[field], (list, dict)) else str(node[field])
                                observed = actual.get("data-" + field.replace("_", "-"))
                                if isinstance(node[field], (list, dict)) and observed is not None:
                                    try:
                                        observed = json.dumps(json.loads(observed), separators=(",", ":"))
                                    except ValueError:
                                        pass
                                if observed != expected:
                                    findings.append({"severity": "error", "code": "node-semantic-mismatch", "message": f"{node['id']} {field}: expected {expected}, got {observed}"})
        except (OSError, ValueError, KeyError, TypeError) as error:
            findings.append({"severity": "error", "code": "invalid-contract", "message": str(error)})
            expected_nodes, expected_edges = set(), set()
        for missing in sorted(expected_nodes - set(boxes)):
            findings.append({"severity": "error", "code": "missing-node", "message": f"required node {missing} is absent"})
        for extra in sorted(set(boxes) - expected_nodes):
            findings.append({"severity": "error", "code": "extra-node", "message": f"unregistered node {extra} is present"})
        for missing in sorted(expected_edges - actual_edges):
            findings.append({"severity": "error", "code": "missing-edge", "message": f"required edge {missing[0]}->{missing[1]} is absent"})
        for extra in sorted(actual_edges - expected_edges):
            findings.append({"severity": "error", "code": "extra-edge", "message": f"edge {extra[0]}->{extra[1]} is not in the topology specification"})

    publication = {"status": "NOT_CHECKED", "reason": "supply --width-mm for physical-size screening; render review remains separate"}
    physical_codes = {"invalid-physical-size", "font-too-small", "stroke-too-thin", "arrow-too-small", "unknown-font-size"}
    if width_mm is not None:
        if not math.isfinite(width_mm) or width_mm <= 0 or view_box[2] <= 0 or any(not math.isfinite(x) or x <= 0 for x in (min_font_pt, min_stroke_pt, min_arrow_pt)):
            findings.append({"severity": "error", "code": "invalid-physical-size", "message": "width and physical thresholds must be finite and positive"})
        else:
            factor = width_mm * 72.0 / (25.4 * view_box[2])
            fonts = []
            def check_fonts(element, inherited=None):
                raw = element.get("font-size", inherited)
                style_size = re.search(r"(?:^|;)\s*font-size\s*:\s*([^;]+)", element.get("style", ""))
                if style_size:
                    raw = style_size.group(1)
                if _local(element) in {"text", "tspan"} and (element.text or "").strip():
                    size = _num(str(raw).removesuffix("px")) * transforms[id(element)][0] * factor
                    if not math.isfinite(size):
                        findings.append({"severity": "error", "code": "unknown-font-size", "message": "physical text size unavailable; explicit px/numeric font-size required"})
                    else:
                        fonts.append(size)
                        if size < min_font_pt:
                            findings.append({"severity": "error", "code": "font-too-small", "message": f"text '{''.join(element.itertext())}' is {size:.2f}pt; minimum {min_font_pt:g}pt"})
                for child in element:
                    check_fonts(child, raw)
            check_fonts(root)
            for path in (e for e in root.iter() if e.get("data-source")):
                scale = transforms[id(path)][0]
                stroke = _num(path.get("stroke-width"), 1) * scale * factor
                if stroke < min_stroke_pt:
                    findings.append({"severity": "error", "code": "stroke-too-thin", "message": f"connector is {stroke:.2f}pt; minimum {min_stroke_pt:g}pt"})
                match = MARKER_REF.fullmatch(path.get("marker-end", ""))
                marker = next((e for e in root.iter() if _local(e) == "marker" and match and e.get("id") == match.group(1)), None)
                if marker is not None and _painted_marker_size(marker) * scale * factor < min_arrow_pt:
                    findings.append({"severity": "error", "code": "arrow-too-small", "message": "arrowhead is below the physical screening threshold"})
            publication = {"width_mm": width_mm, "min_observed_font_pt": min(fonts) if fonts else None,
                           "thresholds_pt": {"font": min_font_pt, "stroke": min_stroke_pt, "arrow": min_arrow_pt}}
        publication["status"] = "FAIL" if any(f["code"] in physical_codes for f in findings) else "PASS"

    topology_codes = {"duplicate-node", "duplicate-edge", "missing-node", "extra-node", "missing-edge", "extra-edge", "edge-id-mismatch", "edge-type-mismatch", "invalid-edge-type", "training-line-style", "training-node-in-inference", "node-execution-mismatch", "node-semantic-mismatch", "unregistered-edge", "invalid-contract"}
    hard_codes = topology_codes | {"invalid-svg", "arrowhead-occluded", "ambiguous-direction", "edge-through-node", "disconnected-route", "missing-arrowhead", "center-to-center-arrow", "unsupported-transform", "malformed-path"}
    hard = sum(item["severity"] == "error" and item["code"] in hard_codes for item in findings)
    errors = sum(item["severity"] == "error" for item in findings)
    return {
        "status": "PASS" if errors == 0 else "FAIL",
        "nodes": len(boxes),
        "edges": edge_count,
        "errors": errors,
        "warnings": sum(item["severity"] == "warning" for item in findings),
        "hard_failures": hard,
        "findings": findings,
        "layers": {
            "topology": {"status": "FAIL" if any(f["severity"] == "error" and f["code"] in topology_codes for f in findings) else ("PASS" if spec_path else "NOT_CHECKED"),
                         "coverage": "edge types/execution conditions and node fields checked only where supplied" if semantic_coverage else "endpoint-only / legacy contract; execution semantics not certified",
                         "boundary": "compares supplied contract; does not establish correspondence to model code"},
            "geometry": {"status": "FAIL" if any(f["severity"] == "error" and f["code"] not in topology_codes | physical_codes for f in findings) else "PASS",
                         "coverage": "direct node primitives and orthogonal paths; translate/positive uniform scale supported"},
            "publication": publication,
            "visual": {"status": "NOT_REVIEWED", "reason": "actual render, fonts, grayscale and reader inspection required"},
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Route and lint editable scientific SVG diagrams")
    subparsers = parser.add_subparsers(dest="command", required=True)
    lint = subparsers.add_parser("lint", help="validate topology and SVG connector geometry")
    lint.add_argument("svg", type=Path)
    lint.add_argument("--spec", type=Path)
    lint.add_argument("--json", action="store_true")
    lint.add_argument("--width-mm", type=float, help="intended final width; enables physical screening")
    lint.add_argument("--min-font-pt", type=float, default=7.5)
    lint.add_argument("--min-stroke-pt", type=float, default=0.5)
    lint.add_argument("--min-arrow-pt", type=float, default=2.5)
    args = parser.parse_args(argv)
    report = lint_svg(args.svg, args.spec, width_mm=args.width_mm, min_font_pt=args.min_font_pt,
                      min_stroke_pt=args.min_stroke_pt, min_arrow_pt=args.min_arrow_pt)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"{report['status']}: {report['nodes']} nodes, {report['edges']} edges, {report['errors']} errors, {report['warnings']} warnings")
        for finding in report["findings"]:
            print(f"{finding['severity'].upper()} [{finding['code']}] {finding['message']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
