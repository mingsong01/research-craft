#!/usr/bin/env python3
"""
ARIS FigureSpec → SVG Renderer v2

Adapted from OpenGHz/academic-human-in-the-loop at the pinned commit in
COMMIT.txt under the MIT License. Local changes add research-rd-workflow
topology metadata, waypoint routing, and visible-boundary arrow clearance.

Converts a FigureSpec JSON into publication-quality SVG for academic papers.
Deterministic: same spec = same SVG, every time.

Usage:
    python3 figure_renderer.py render spec.json [--output figures/output.svg] [--preview]
    python3 figure_renderer.py validate spec.json
    python3 figure_renderer.py schema
"""

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString


# ============================================================
# Constants & Defaults
# ============================================================

ARROW_SIZE = 12
SELF_LOOP_RADIUS = 25

# Allowed values for sanitization
ALLOWED_SHAPES = {"rect", "rounded", "circle", "diamond", "ellipse", "tensor"}
ALLOWED_STYLES = {"solid", "dashed", "dotted"}
ALLOWED_ANCHORS = {"start", "middle", "end"}
HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

DEFAULT_STYLE = {
    "font_family": "Arial, Helvetica, sans-serif",
    "font_size": 14,
    "bg_color": "#FFFFFF",
    "palette": ["#2563EB", "#10B981", "#7C3AED", "#EA580C", "#C62828",
                "#0D47A1", "#1B5E20", "#4A148C", "#BF360C", "#37474F"],
}

DEFAULT_NODE = {
    "width": 120,
    "height": 50,
    "shape": "rounded",
    "text_color": "#333333",
    "font_size": None,
}

DEFAULT_EDGE = {
    "style": "solid",
    "color": "#555555",
    "thickness": 2,
    "curve": False,
}

ARROW_TIP_GAP = 5


# ============================================================
# Sanitization
# ============================================================

def sanitize_color(val: str, fallback: str = "#555555") -> str:
    """Validate hex color, reject anything else."""
    if isinstance(val, str) and HEX_COLOR_RE.match(val):
        return val
    return fallback


def sanitize_text(val: str) -> str:
    """Strip XML-illegal characters from text. ElementTree escapes &<>, but some code points are invalid in XML."""
    if not isinstance(val, str):
        return str(val)
    # Remove XML-illegal code points: C0 controls (except \t\n\r), C1, surrogates, noncharacters
    val = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", val)
    # Remove BMP noncharacters (U+FDD0-U+FDEF, U+FFFE-U+FFFF) and surrogates
    val = re.sub(r"[\ud800-\udfff\ufdd0-\ufdef\ufffe\uffff]", "", val)
    return val


def estimate_text_width(text: str, font_size: int) -> float:
    """Estimate text width in px. Rough but consistent."""
    # Average character width ≈ 0.6 × font_size for sans-serif
    # CJK characters ≈ 1.0 × font_size
    width = 0
    for ch in text:
        if ord(ch) > 0x2E80:  # CJK range
            width += font_size * 1.0
        else:
            width += font_size * 0.6
    return width


# ============================================================
# Color Utilities
# ============================================================

def lighten_color(hex_color: str, factor: float = 0.85) -> str:
    """Lighten a hex color for node fills."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


# ============================================================
# Geometry: Shape-Aware Edge Clipping
# ============================================================

def clip_to_shape(cx, cy, target_x, target_y, w, h, shape):
    """Clip a line from (cx,cy) toward (target_x,target_y) to the shape boundary."""
    dx = target_x - cx
    dy = target_y - cy
    if dx == 0 and dy == 0:
        return cx, cy - h / 2  # default: top

    if shape == "circle":
        # True circle: use max(w,h)/2 to match renderer
        r = max(w, h) / 2
        angle = math.atan2(dy, dx)
        return cx + r * math.cos(angle), cy + r * math.sin(angle)

    elif shape == "ellipse":
        # Ellipse clipping: x²/a² + y²/b² = 1
        a = w / 2
        b = h / 2
        angle = math.atan2(dy, dx)
        return cx + a * math.cos(angle), cy + b * math.sin(angle)

    elif shape == "diamond":
        # Diamond: |x/a| + |y/b| = 1
        a = w / 2
        b = h / 2
        angle = math.atan2(dy, dx)
        cos_a = abs(math.cos(angle))
        sin_a = abs(math.sin(angle))
        if cos_a * b + sin_a * a == 0:
            return cx, cy
        scale = (a * b) / (cos_a * b + sin_a * a)
        return cx + scale * math.cos(angle), cy + scale * math.sin(angle)

    elif shape == "tensor":
        # Convex projected feature volume; intersect the actual silhouette.
        a, b = w / 2, h / 2
        depth = min(20, min(w, h) * .12)
        vertices = [(-a, -b + depth), (-a + depth, -b), (a, -b),
                    (a, b - depth), (a - depth, b), (-a, b)]
        hits = []
        for p, q in zip(vertices, vertices[1:] + vertices[:1]):
            ex, ey = q[0] - p[0], q[1] - p[1]
            det = dx * ey - dy * ex
            if abs(det) < 1e-12:
                continue
            t = (p[0] * ey - p[1] * ex) / det
            u = (p[0] * dy - p[1] * dx) / det
            if t >= 0 and 0 <= u <= 1:
                hits.append(t)
        t = min(hits)
        return cx + t * dx, cy + t * dy
    else:
        # Rectangle clipping
        a = w / 2
        b = h / 2
        if abs(dx) * b > abs(dy) * a:
            scale = a / abs(dx)
        else:
            scale = b / abs(dy)
        return cx + dx * scale, cy + dy * scale


def extend_outside(cx, cy, boundary_x, boundary_y, gap=ARROW_TIP_GAP):
    """Move a clipped boundary point away from the node centre by ``gap``."""
    dx, dy = boundary_x - cx, boundary_y - cy
    length = math.hypot(dx, dy)
    if length == 0:
        return boundary_x, boundary_y
    return boundary_x + gap * dx / length, boundary_y + gap * dy / length


def normalize_waypoints(raw):
    """Return valid ``(x, y)`` waypoint pairs from list/dict FigureSpec forms."""
    points = []
    for item in raw or []:
        if isinstance(item, dict):
            x, y = item.get("x"), item.get("y")
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            x, y = item
        else:
            continue
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            points.append((float(x), float(y)))
    return points


def polyline_midpoint(points):
    """Return the length-weighted midpoint of a polyline."""
    segments = []
    total = 0.0
    for start, end in zip(points, points[1:]):
        length = math.hypot(end[0] - start[0], end[1] - start[1])
        segments.append((start, end, length))
        total += length
    if total == 0:
        return points[0] if points else (0.0, 0.0)
    target = total / 2
    traversed = 0.0
    for start, end, length in segments:
        if traversed + length >= target:
            ratio = (target - traversed) / length if length else 0.0
            return (start[0] + ratio * (end[0] - start[0]),
                    start[1] + ratio * (end[1] - start[1]))
        traversed += length
    return points[-1]


# ============================================================
# Validation
# ============================================================

def port_endpoint(node, port, gap):
    """Explicit side ports; offset follows top-to-bottom or left-to-right."""
    side, offset = port["side"], port.get("offset", 0.5)
    x, y, w, h = node["x"], node["y"], node["width"], node["height"]
    if node.get("shape", "rounded") not in {"rect", "rounded"}:
        # Curved/diamond shapes accept cardinal ports only, checked by validation.
        vx, vy = {"left": (-1, 0), "right": (1, 0), "top": (0, -1), "bottom": (0, 1)}[side]
        bx, by = clip_to_shape(x, y, x + vx * 100, y + vy * 100, w, h, node["shape"])
        return bx + vx * gap, by + vy * gap
    return {"left": (x - w / 2 - gap, y - h / 2 + h * offset),
            "right": (x + w / 2 + gap, y - h / 2 + h * offset),
            "top": (x - w / 2 + w * offset, y - h / 2 - gap),
            "bottom": (x - w / 2 + w * offset, y + h / 2 + gap)}[side]


def edge_label_anchor(points, mode="midpoint"):
    if mode == "longest-horizontal":
        segments = [(a, b) for a, b in zip(points, points[1:])
                    if abs(a[1] - b[1]) < 1e-6 and abs(a[0] - b[0]) > 1e-6]
        if not segments:
            raise ValueError("longest-horizontal label requires a nonzero horizontal segment")
        a, b = max(segments, key=lambda pair: abs(pair[1][0] - pair[0][0]))
        return (a[0] + b[0]) / 2, a[1]
    return polyline_midpoint(points)


def validate_spec(spec: dict) -> list:
    """Validate FigureSpec, return list of issues."""
    issues = []

    # Top-level must be a dict
    if not isinstance(spec, dict):
        return [f"CRITICAL: spec must be a JSON object, got {type(spec).__name__}"]

    def finite_numbers(value):
        if isinstance(value, float) and not math.isfinite(value):
            return False
        if isinstance(value, dict):
            return all(finite_numbers(v) for v in value.values())
        if isinstance(value, list):
            return all(finite_numbers(v) for v in value)
        return True
    if not finite_numbers(spec):
        return ["CRITICAL: numeric values must be finite"]

    # Structure validation — ensure top-level fields are correct types
    canvas = spec.get("canvas", {})
    if not isinstance(canvas, dict):
        issues.append("CRITICAL: 'canvas' must be a dict")
        canvas = {}
    st_raw = spec.get("style", {})
    if not isinstance(st_raw, dict):
        issues.append("CRITICAL: 'style' must be a dict")
    if not isinstance(spec.get("nodes", []), list):
        issues.append("CRITICAL: 'nodes' must be a list")
    if not isinstance(spec.get("edges", []), list):
        issues.append("CRITICAL: 'edges' must be a list")
    if not isinstance(spec.get("groups", []), list):
        issues.append("CRITICAL: 'groups' must be a list")
    if not isinstance(spec.get("labels", []), list):
        issues.append("CRITICAL: 'labels' must be a list")

    # Early return if structure is fundamentally broken
    if any(i.startswith("CRITICAL: '") for i in issues):
        return issues

    # Canvas validation
    for dim in ("width", "height"):
        val = canvas.get(dim)
        if val is not None:
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                issues.append(f"CRITICAL: canvas.{dim} must be a number")
            elif val <= 0:
                issues.append(f"CRITICAL: canvas.{dim} must be positive")

    # Style validation
    st = spec.get("style", {})
    fs = st.get("font_size")
    if fs is not None and (isinstance(fs, bool) or not isinstance(fs, (int, float)) or fs <= 0):
        issues.append(f"CRITICAL: style.font_size must be a positive number")
    pal = st.get("palette")
    if pal is not None:
        if not isinstance(pal, list) or len(pal) == 0:
            issues.append(f"CRITICAL: style.palette must be a non-empty list of hex colors")
        else:
            for pi, pc in enumerate(pal):
                if not isinstance(pc, str) or not HEX_COLOR_RE.match(pc):
                    issues.append(f"CRITICAL: style.palette[{pi}] '{pc}' is not a valid hex color (#RRGGBB)")

    nodes = spec.get("nodes", [])
    if not nodes:
        issues.append("WARN: no nodes defined (labels/groups-only figure)")

    node_ids = set()
    for i, node in enumerate(nodes):
        if not isinstance(node, dict):
            issues.append(f"CRITICAL: nodes[{i}] must be a dict, got {type(node).__name__}")
            continue
        nid = node.get("id")
        if not nid:
            issues.append(f"CRITICAL: node[{i}] missing 'id'")
            continue
        if nid in node_ids:
            issues.append(f"CRITICAL: duplicate node id '{nid}'")
        node_ids.add(nid)
        if "label" not in node:
            issues.append(f"WARN: node '{nid}' missing 'label'")
        for coord in ("x", "y"):
            if coord not in node:
                issues.append(f"CRITICAL: node '{nid}' missing '{coord}'")
            elif isinstance(node[coord], bool) or not isinstance(node[coord], (int, float)):
                issues.append(f"CRITICAL: node '{nid}' {coord} must be a number, got {type(node[coord]).__name__}")
        for dim in ("width", "height"):
            val = node.get(dim)
            if val is not None and (isinstance(val, bool) or not isinstance(val, (int, float))):
                issues.append(f"CRITICAL: node '{nid}' {dim} must be a number, got {type(val).__name__}")
            elif val is not None and val <= 0:
                issues.append(f"CRITICAL: node '{nid}' {dim} must be positive ({val})")
        shape = node.get("shape", "rounded")
        if shape not in ALLOWED_SHAPES:
            issues.append(f"WARN: node '{nid}' unknown shape '{shape}', will use 'rounded'")
        representation = node.get("representation")
        representation_style = node.get("representation_style", "classic")
        if representation_style not in {"classic", "semantic"} or ("representation_style" in node and not representation):
            issues.append(f"CRITICAL: node '{nid}' representation_style requires a known representation and classic/semantic value")
        if representation is not None:
            if representation not in {"feature-map", "tokens"}:
                issues.append(f"CRITICAL: node '{nid}' unknown representation")
            if shape not in {"rect", "rounded"}:
                issues.append(f"CRITICAL: node '{nid}' representation requires a rectangular boundary")
            nfs = node.get("font_size", st.get("font_size", DEFAULT_STYLE["font_size"]))
            if isinstance(nfs, (int, float)) and not isinstance(nfs, bool) and nfs > 0:
                lines = len(str(node.get("label", "")).replace("\\n", "\n").splitlines()) + bool(node.get("sublabel"))
                nh, nw = node.get("height", DEFAULT_NODE["height"]), node.get("width", DEFAULT_NODE["width"])
                reserve = 2.2 if representation_style == "semantic" else 2.7
                if isinstance(nh, (int, float)) and nh < nfs * (reserve + lines * 1.5):
                    issues.append(f"CRITICAL: node '{nid}' needs more height for representation and text")
                if isinstance(nw, (int, float)) and nw < nfs * 3:
                    issues.append(f"CRITICAL: node '{nid}' needs more width for representation")
        if "emphasis" in node and not isinstance(node["emphasis"], bool):
            issues.append(f"CRITICAL: node '{nid}' emphasis must be boolean")
        if "header" in node:
            header = node["header"]
            if not isinstance(header, str) or not header.strip() or "\n" in header or "\\n" in header:
                issues.append(f"CRITICAL: node '{nid}' header must be nonempty single-line text")
            if shape not in {"rect", "rounded"} or representation:
                issues.append(f"CRITICAL: node '{nid}' header requires a plain rectangular module")
            nfs = node.get("font_size") or st.get("font_size", DEFAULT_STYLE["font_size"])
            if isinstance(nfs, (int, float)) and not isinstance(nfs, bool) and nfs > 3:
                nw, nh = node.get("width", DEFAULT_NODE["width"]), node.get("height", DEFAULT_NODE["height"])
                lines = len(str(node.get("label", "")).replace("\\n", "\n").splitlines()) + bool(node.get("sublabel"))
                if isinstance(nh, (int, float)) and nh < nfs * (2.1 + 1.5 * lines):
                    issues.append(f"CRITICAL: node '{nid}' needs more height for header and text")
                if isinstance(nw, (int, float)) and isinstance(header, str) and estimate_text_width(header, nfs - 3) > nw - 24:
                    issues.append(f"CRITICAL: node '{nid}' header exceeds available width")
            else:
                issues.append(f"CRITICAL: node '{nid}' header requires font_size greater than 3")

    for i, edge in enumerate(spec.get("edges", [])):
        if not isinstance(edge, dict):
            issues.append(f"CRITICAL: edges[{i}] must be a dict")
            continue
        src, dst = edge.get("from"), edge.get("to")
        if not src or not dst:
            issues.append(f"CRITICAL: edge[{i}] missing 'from' or 'to'")
        else:
            if src not in node_ids:
                issues.append(f"CRITICAL: edge[{i}] 'from' references unknown node '{src}'")
            if dst not in node_ids:
                issues.append(f"CRITICAL: edge[{i}] 'to' references unknown node '{dst}'")
        style = edge.get("style", "solid")
        if style not in ALLOWED_STYLES:
            issues.append(f"WARN: edge[{i}] unknown style '{style}', will use 'solid'")
        if edge.get("type", "main") not in {"main", "skip", "auxiliary", "feedback", "training-only", "residual", "conditioning"}:
            issues.append(f"CRITICAL: edge[{i}] unknown semantic type")
        if edge.get("type") == "training-only" and "style" in edge and edge["style"] not in {"dashed", "dotted"}:
            issues.append(f"CRITICAL: edge[{i}] training-only requires dashed or dotted style")
        for field, nid in (("source_port", src), ("target_port", dst)):
            if field not in edge:
                continue
            port = edge[field]
            if not isinstance(port, dict) or port.get("side") not in {"left", "right", "top", "bottom"}:
                issues.append(f"CRITICAL: edge[{i}] {field} requires a valid side")
                continue
            off = port.get("offset", 0.5)
            if isinstance(off, bool) or not isinstance(off, (int, float)) or not 0 <= off <= 1:
                issues.append(f"CRITICAL: edge[{i}] {field} offset must be within [0, 1]")
            n = next((n for n in nodes if isinstance(n, dict) and n.get("id") == nid), {})
            if n.get("shape", "rounded") not in {"rect", "rounded"} and off != 0.5:
                issues.append(f"CRITICAL: edge[{i}] nonrectangular ports require offset 0.5")
            if src == dst:
                issues.append(f"CRITICAL: edge[{i}] explicit ports on self loops are not supported")
        if edge.get("label_segment", "midpoint") not in {"midpoint", "longest-horizontal"}:
            issues.append(f"CRITICAL: edge[{i}] unknown label_segment")
        if edge.get("label_segment") == "longest-horizontal" and (edge.get("curve") or src == dst):
            issues.append(f"CRITICAL: edge[{i}] horizontal label placement requires a straight/polyline edge")

    for i, group in enumerate(spec.get("groups", [])):
        if not isinstance(group, dict):
            issues.append(f"CRITICAL: groups[{i}] must be a dict")
            continue
        node_ids_list = group.get("node_ids", [])
        if not isinstance(node_ids_list, list):
            issues.append(f"WARN: group[{i}] node_ids must be a list")
            continue
        for nid in node_ids_list:
            if nid not in node_ids:
                issues.append(f"WARN: group[{i}] references unknown node '{nid}'")

    # Edge numeric validation
    for i, edge in enumerate(spec.get("edges", [])):
        for field in ("thickness",):
            val = edge.get(field)
            if val is not None and (isinstance(val, bool) or not isinstance(val, (int, float))):
                issues.append(f"WARN: edge[{i}] {field} must be a number")

    # Group numeric validation
    for i, group in enumerate(spec.get("groups", [])):
        val = group.get("padding")
        if val is not None and (isinstance(val, bool) or not isinstance(val, (int, float))):
            issues.append(f"WARN: group[{i}] padding must be a number")

    # Free label numeric + anchor validation
    for i, label in enumerate(spec.get("labels", [])):
        if not isinstance(label, dict):
            issues.append(f"CRITICAL: labels[{i}] must be a dict")
            continue
        anchor = label.get("anchor")
        if anchor and anchor not in ALLOWED_ANCHORS:
            issues.append(f"WARN: label[{i}] unknown anchor '{anchor}', will use 'middle'")
        if "line_style" in label and (label["line_style"] not in ALLOWED_STYLES or anchor != "start"):
            issues.append(f"CRITICAL: label[{i}] line_style requires solid/dashed/dotted and start anchor")
        for field in ("x", "y", "font_size"):
            val = label.get(field)
            if val is not None and (isinstance(val, bool) or not isinstance(val, (int, float))):
                issues.append(f"WARN: label[{i}] {field} must be a number")

    # Node font_size validation
    for node in nodes:
        if not isinstance(node, dict):
            continue
        nid = node.get("id", "?")
        nfs = node.get("font_size")
        if nfs is not None and (isinstance(nfs, bool) or not isinstance(nfs, (int, float)) or nfs <= 0):
            issues.append(f"WARN: node '{nid}' font_size must be a positive number")

    # Overlap detection (shape-aware bounding for circles)
    if any(i.startswith("CRITICAL") for i in issues):
        return issues
    def _effective_bounds(n):
        w = n.get("width", DEFAULT_NODE["width"])
        h = n.get("height", DEFAULT_NODE["height"])
        if n.get("shape") == "circle":
            d = max(w, h)
            return d, d
        return w, h

    for i, a in enumerate(nodes):
        if not isinstance(a, dict):
            continue
        for j, b in enumerate(nodes):
            if i >= j or not isinstance(b, dict):
                continue
            ax, ay = a.get("x", 0), a.get("y", 0)
            bx, by = b.get("x", 0), b.get("y", 0)
            aw, ah = _effective_bounds(a)
            bw, bh = _effective_bounds(b)
            if (abs(ax - bx) < (aw + bw) / 2 - 5 and
                    abs(ay - by) < (ah + bh) / 2 - 5):
                issues.append(f"WARN: nodes '{a.get('id')}' and '{b.get('id')}' may overlap")

    return issues


# ============================================================
# SVG Renderer
# ============================================================

def render_svg(spec: dict) -> str:
    """Render FigureSpec to SVG string."""
    canvas = spec.get("canvas", {})
    width = canvas.get("width", 800)
    height = canvas.get("height", 400)
    style = {**DEFAULT_STYLE, **spec.get("style", {})}
    # Retain the selected Latin family and portable CJK fallbacks; declarations
    # do not guarantee installation, so native render inspection remains needed.
    font_family = style["font_family"]
    for family in ("PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC"):
        if family not in font_family:
            font_family += f", '{family}'"
    palette = style["palette"]
    base_fs = style["font_size"]

    svg = Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "viewBox": f"0 0 {width} {height}",
        "width": str(width),
        "height": str(height),
        "font-family": sanitize_text(font_family),
    })
    SubElement(svg, "style").text = "text { font-family: " + sanitize_text(font_family) + "; }"

    # Background
    SubElement(svg, "rect", {
        "x": "0", "y": "0",
        "width": str(width), "height": str(height),
        "fill": sanitize_color(style.get("bg_color", "#FFFFFF")),
    })

    # Defs: arrow markers
    defs = SubElement(svg, "defs")
    marker_colors = {"default": sanitize_color(DEFAULT_EDGE["color"])}
    for i, c in enumerate(palette):
        marker_colors[f"c{i}"] = sanitize_color(c)

    sizes = {8 if e.get("thickness", 2) <= 1.5 else 12 if e.get("thickness", 2) <= 2.5 else 16 for e in spec.get("edges", [])} or {12}
    for name, color in marker_colors.items():
        for size in sorted(sizes):
            marker = SubElement(defs, "marker", {
                "id": f"arrow-{name}-{size}",
                "markerWidth": str(size),
                "markerHeight": str(size),
                "refX": str(size / 4),
                "refY": str(size / 2),
                "orient": "auto",
                "markerUnits": "userSpaceOnUse",
            })
            SubElement(marker, "path", {
                "d": f"M0,0 L{size},{size / 2} L0,{size} L{size / 4},{size / 2} Z",
                "fill": color,
            })

    # Build node lookup with defaults applied
    node_map = {}
    for i, node in enumerate(spec.get("nodes", [])):
        n = {**DEFAULT_NODE, **node}
        n["fill"] = sanitize_color(n.get("fill") or lighten_color(palette[i % len(palette)]))
        n["stroke"] = sanitize_color(n.get("stroke") or palette[i % len(palette)])
        n["text_color"] = sanitize_color(n.get("text_color", DEFAULT_NODE["text_color"]))
        n["label"] = sanitize_text(n.get("label", ""))
        if n.get("sublabel"):
            n["sublabel"] = sanitize_text(n["sublabel"])
        if n.get("shape") not in ALLOWED_SHAPES:
            n["shape"] = "rounded"
        node_map[n["id"]] = n

    # --- Render groups (background layer) ---
    for group in spec.get("groups", []):
        gnodes = [node_map[nid] for nid in group.get("node_ids", []) if nid in node_map]
        if not gnodes:
            continue
        pad = group.get("padding", 20)
        def _node_extent(n):
            w, h = n["width"], n["height"]
            if n.get("shape") == "circle":
                d = max(w, h)
                return d, d
            return w, h

        min_x = min(n["x"] - _node_extent(n)[0] / 2 for n in gnodes) - pad
        min_y = min(n["y"] - _node_extent(n)[1] / 2 for n in gnodes) - pad
        max_x = max(n["x"] + _node_extent(n)[0] / 2 for n in gnodes) + pad
        max_y = max(n["y"] + _node_extent(n)[1] / 2 for n in gnodes) + pad

        SubElement(svg, "rect", {
            "x": f"{min_x:.1f}", "y": f"{min_y:.1f}",
            "width": f"{max_x - min_x:.1f}", "height": f"{max_y - min_y:.1f}",
            "fill": sanitize_color(group.get("fill", "#F5F5F5")),
            "stroke": sanitize_color(group.get("stroke", "#E0E0E0")),
            "stroke-width": "1", "rx": "8",
        })
        if group.get("label"):
            lbl = SubElement(svg, "text", {
                "x": f"{min_x + 8:.1f}", "y": f"{min_y + 16:.1f}",
                "font-size": str(base_fs - 2),
                "fill": "#555555", "font-weight": "bold",
            })
            lbl.text = sanitize_text(group["label"])

    # --- Render edges ---
    for edge_index, edge in enumerate(spec.get("edges", [])):
        e = {**DEFAULT_EDGE, **edge}
        src = node_map.get(e.get("from"))
        dst = node_map.get(e.get("to"))
        if not src or not dst:
            continue

        color = sanitize_color(e["color"])
        e_style = e["style"] if e["style"] in ALLOWED_STYLES else "solid"
        if e.get("type") == "training-only" and "style" not in edge:
            e_style = "dashed"

        # Find matching arrow marker
        marker_id = "arrow-default"
        for ci, pc in enumerate(palette):
            if color.lower() == pc.lower():
                marker_id = f"arrow-c{ci}"
                break
        marker_size = 8 if e["thickness"] <= 1.5 else 12 if e["thickness"] <= 2.5 else 16
        marker_id += f"-{marker_size}"
        marker_extension = marker_size * 0.75

        # Dash pattern
        dash_map = {"solid": "", "dashed": "8,4", "dotted": "3,3"}
        dash = dash_map.get(e_style, "")

        edge_attrs = {
            "data-source": str(src["id"]),
            "data-target": str(dst["id"]),
            "data-edge-type": sanitize_text(str(e.get("type", "main"))),
            "data-edge-id": sanitize_text(str(e.get("id", f"edge-{edge_index + 1}"))),
            "data-train-only": "true" if e.get("type") == "training-only" else "false",
        }

        # Self-loop (shape-aware: find top boundary)
        if src["id"] == dst["id"]:
            cx, cy = src["x"], src["y"]
            r = SELF_LOOP_RADIUS
            src_shape = src.get("shape", "rounded")
            # Find top anchor point based on shape
            top_x, top_y_pt = clip_to_shape(cx, cy, cx, cy - 100, src["width"], src["height"], src_shape)
            visible_y = top_y_pt - ARROW_TIP_GAP
            path_d = (f"M {top_x - 10},{visible_y} "
                      f"C {cx - r},{visible_y - r * 1.5} {cx + r},{visible_y - r * 1.5} {top_x + 10},{visible_y}")
            attrs = {
                "d": path_d,
                "stroke": color,
                "stroke-width": str(e["thickness"]),
                "fill": "none",
                "marker-end": f"url(#{marker_id})",
                **edge_attrs,
            }
            if dash:
                attrs["stroke-dasharray"] = dash
            SubElement(svg, "path", attrs)
        else:
            waypoints = normalize_waypoints(e.get("waypoints"))
            first_guide = waypoints[0] if waypoints else (dst["x"], dst["y"])
            last_guide = waypoints[-1] if waypoints else (src["x"], src["y"])

            # Shape-aware clipping plus a visible gap outside both node fills.
            sx, sy = clip_to_shape(src["x"], src["y"], first_guide[0], first_guide[1],
                                   src["width"], src["height"], src.get("shape", "rounded"))
            sx, sy = extend_outside(src["x"], src["y"], sx, sy)
            dx, dy = clip_to_shape(dst["x"], dst["y"], last_guide[0], last_guide[1],
                                   dst["width"], dst["height"], dst.get("shape", "rounded"))
            dx, dy = extend_outside(dst["x"], dst["y"], dx, dy, ARROW_TIP_GAP + marker_extension)
            if e.get("source_port"):
                sx, sy = port_endpoint(src, e["source_port"], ARROW_TIP_GAP)
            if e.get("target_port"):
                dx, dy = port_endpoint(dst, e["target_port"], ARROW_TIP_GAP + marker_extension)

            if waypoints:
                route_points = [(sx, sy), *waypoints, (dx, dy)]
                path_d = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in route_points)
            elif e.get("curve"):
                # Quadratic bezier with midpoint offset
                mx = (sx + dx) / 2
                my = (sy + dy) / 2
                # Offset perpendicular to the line
                length = math.sqrt((dx - sx) ** 2 + (dy - sy) ** 2) or 1
                offset = 30
                nx = -(dy - sy) / length * offset
                ny = (dx - sx) / length * offset
                path_d = f"M {sx:.1f},{sy:.1f} Q {mx + nx:.1f},{my + ny:.1f} {dx:.1f},{dy:.1f}"
            else:
                path_d = f"M {sx:.1f},{sy:.1f} L {dx:.1f},{dy:.1f}"

            attrs = {
                "d": path_d,
                "stroke": color,
                "stroke-width": str(e["thickness"]),
                "fill": "none",
                "marker-end": f"url(#{marker_id})",
                **edge_attrs,
            }
            if dash:
                attrs["stroke-dasharray"] = dash
            SubElement(svg, "path", attrs)

        # Edge label
        if e.get("label"):
            label_text = sanitize_text(e["label"])
            if src["id"] == dst["id"]:
                lx = src["x"]
                src_shape = src.get("shape", "rounded")
                _, top_pt = clip_to_shape(src["x"], src["y"], src["x"], src["y"] - 100,
                                          src["width"], src["height"], src_shape)
                ly = top_pt - SELF_LOOP_RADIUS * 1.2
            elif waypoints or e.get("label_segment") == "longest-horizontal":
                points = route_points if waypoints else [(sx, sy), (dx, dy)]
                lx, ly = edge_label_anchor(points, e.get("label_segment", "midpoint"))
                ly -= (base_fs - 3) * 0.3 + 10
            elif e.get("curve"):
                # Bezier midpoint at t=0.5: B(0.5) = (1-t)^2*P0 + 2(1-t)t*P1 + t^2*P2
                mx_ctrl = (sx + dx) / 2
                my_ctrl = (sy + dy) / 2
                length = math.sqrt((dx - sx) ** 2 + (dy - sy) ** 2) or 1
                offset = 30
                nx_ctrl = -(dy - sy) / length * offset
                ny_ctrl = (dx - sx) / length * offset
                qx, qy = mx_ctrl + nx_ctrl, my_ctrl + ny_ctrl
                lx = 0.25 * sx + 0.5 * qx + 0.25 * dx
                ly = 0.25 * sy + 0.5 * qy + 0.25 * dy - 8
            else:
                lx = (sx + dx) / 2
                ly = (sy + dy) / 2 - 8

            lbl = SubElement(svg, "text", {
                "x": f"{lx:.1f}", "y": f"{ly:.1f}",
                "font-size": str(base_fs - 3),
                "fill": "#555555", "text-anchor": "middle",
                "data-edge-label": edge_attrs["data-edge-id"],
            })
            lbl.text = label_text

    # --- Render nodes ---
    for node in spec.get("nodes", []):
        n = node_map[node["id"]]
        x, y = n["x"], n["y"]
        w, h = n["width"], n["height"]
        left, top = x - w / 2, y - h / 2
        shape = n.get("shape", "rounded")
        fill = n["fill"]
        stroke = n["stroke"]

        node_group = SubElement(svg, "g", {
            "data-node-id": str(n["id"]),
            "data-role": sanitize_text(str(n.get("role", "generic"))),
            "data-execution": sanitize_text(str(n.get("execution", "both"))),
        })
        for field in ("operation", "stage", "tensor_shape"):
            if field in n:
                value = json.dumps(n[field], separators=(",", ":")) if isinstance(n[field], (list, dict)) else str(n[field])
                node_group.set("data-" + field.replace("_", "-"), sanitize_text(value))

        if shape == "tensor":
            depth = min(20, min(w, h) * .12)
            right, bottom = left + w, top + h
            outline = [(left, top + depth), (left + depth, top), (right, top),
                       (right, bottom - depth), (right - depth, bottom), (left, bottom)]
            SubElement(node_group, "polygon", {
                "points": " ".join(f"{xx:.1f},{yy:.1f}" for xx, yy in outline),
                "fill": fill, "stroke": stroke, "stroke-width": "2",
            })
            for face, face_fill in [([(left, top + depth), (left + depth, top), (right, top), (right - depth, top + depth)], lighten_color(stroke, .91)),
                                    ([(right - depth, top + depth), (right, top), (right, bottom - depth), (right - depth, bottom)], lighten_color(stroke, .74))]:
                SubElement(node_group, "path", {
                    "d": "M " + " L ".join(f"{xx:.1f},{yy:.1f}" for xx, yy in face) + " Z",
                    "fill": face_fill, "stroke": stroke, "stroke-width": "1.5", "data-decoration": "tensor-face",
                })
        elif shape == "circle":
            r = max(w, h) / 2
            SubElement(node_group, "circle", {
                "cx": f"{x:.1f}", "cy": f"{y:.1f}", "r": f"{r:.1f}",
                "fill": fill, "stroke": stroke, "stroke-width": "2",
            })
        elif shape == "ellipse":
            SubElement(node_group, "ellipse", {
                "cx": f"{x:.1f}", "cy": f"{y:.1f}",
                "rx": f"{w / 2:.1f}", "ry": f"{h / 2:.1f}",
                "fill": fill, "stroke": stroke, "stroke-width": "2",
            })
        elif shape == "diamond":
            points = (f"{x:.1f},{top:.1f} {x + w / 2:.1f},{y:.1f} "
                      f"{x:.1f},{top + h:.1f} {x - w / 2:.1f},{y:.1f}")
            SubElement(node_group, "polygon", {
                "points": points,
                "fill": fill, "stroke": stroke, "stroke-width": "2",
            })
        else:
            rx = "8" if shape == "rounded" else "0"
            SubElement(node_group, "rect", {
                "x": f"{left:.1f}", "y": f"{top:.1f}",
                "width": f"{w:.1f}", "height": f"{h:.1f}",
                "fill": fill, "stroke": stroke,
                "stroke-width": "2", "rx": rx,
            })

        # Main label (supports \n for multi-line)
        fs = n.get("font_size") or base_fs
        # Handle multi-line: first replace literal \\n with \n, then split
        raw_label = n["label"].replace("\\n", "\n")
        label_lines = [line for line in raw_label.split("\n") if line]
        has_sub = bool(n.get("sublabel"))
        total_lines = len(label_lines) + (1 if has_sub else 0)
        line_height = fs * 1.5
        text_center_y = y
        if shape == "tensor":
            # Centre text on the front face, not on the projected silhouette.
            x -= depth / 2
            text_center_y += depth / 2
        if n.get("header"):
            header = SubElement(node_group, "text", {
                "x": f"{x:.1f}", "y": f"{top + fs * .95:.1f}", "font-size": str(fs - 3),
                "fill": n["text_color"], "text-anchor": "middle", "font-weight": "bold", "data-decoration": "module-header",
            })
            header.text = sanitize_text(n["header"])
            SubElement(node_group, "path", {
                "d": f"M{left + 16:.1f},{top + fs * 1.65:.1f} H{left + w - 16:.1f}",
                "fill": "none", "stroke": stroke, "stroke-width": "1.5", "data-decoration": "header-divider",
            })
            text_center_y = (top + fs * 2.1 + top + h) / 2
        if n.get("emphasis"):
            # An internal accent marks author-declared emphasis, not a new operator.
            SubElement(node_group, "path", {
                "d": f"M{left + 8:.1f},{top + 12:.1f} V{top + h - 12:.1f}",
                "fill": "none", "stroke": stroke, "stroke-width": "5",
                "data-decoration": "emphasis",
            })
        if n.get("representation"):
            # Symbolic only: repeated glyphs never encode actual channels/token counts.
            gy, gh = top + fs * 0.6, fs * 1.4
            gw = min(w - fs * 1.4, fs * 3.5)
            gx = x - gw / 2
            glyph = SubElement(node_group, "g", {"data-decoration": n["representation"],
                                                 "aria-label": "symbolic representation; counts are not dimensions"})
            if n.get("representation_style") == "semantic":
                if n["representation"] == "feature-map":
                    # Spatial planes, not quantitative maps or invented activations.
                    fw = gw * .64
                    for dx, dy in ((gw * .36, 0), (gw * .18, gh * .16), (0, gh * .32)):
                        xx, yy, hh = gx + dx, gy + dy, gh * .68
                        SubElement(glyph, "path", {"d": f"M{xx:.1f},{yy:.1f} h{fw:.1f} v{hh:.1f} h{-fw:.1f} Z",
                            "fill": fill, "stroke": stroke, "stroke-width": "1.9"})
                    SubElement(glyph, "path", {"d": f"M{gx + fw/3:.1f},{gy + gh*.32:.1f} v{gh*.68:.1f} M{gx + 2*fw/3:.1f},{gy + gh*.32:.1f} v{gh*.68:.1f} M{gx:.1f},{gy + gh*.66:.1f} h{fw:.1f}",
                        "fill": "none", "stroke": stroke, "stroke-width": "1.5"})
                else:
                    # Horizontal word-piece-like tiles with neutral text strokes.
                    for xx, yy, ww in ((gx, gy, gw * .38), (gx + gw * .45, gy, gw * .55), (gx + gw * .16, gy + gh * .57, gw * .68)):
                        hh = gh * .42
                        SubElement(glyph, "path", {"d": f"M{xx:.1f},{yy:.1f} h{ww:.1f} v{hh:.1f} h{-ww:.1f} Z",
                            "fill": fill, "stroke": stroke, "stroke-width": "1.9"})
                        SubElement(glyph, "path", {"d": f"M{xx + 4:.1f},{yy + hh/2:.1f} h{ww - 8:.1f}",
                            "fill": "none", "stroke": stroke, "stroke-width": "1.5"})
            elif n["representation"] == "feature-map":
                d = fs * 0.28
                for shift in (2 * d, d, 0):
                    SubElement(glyph, "path", {
                        "d": f"M{gx + shift:.1f},{gy + 2*d - shift:.1f} h{gw - 2*d:.1f} v{gh - 2*d:.1f} h{-gw + 2*d:.1f} Z",
                        "fill": fill, "stroke": stroke, "stroke-width": "1.7",
                    })
            else:
                tw = gw / 5
                for k in range(5):
                    xx = gx + k * tw
                    SubElement(glyph, "path", {
                        "d": f"M{xx:.1f},{gy:.1f} h{tw - 4:.1f} v{gh:.1f} h{-tw + 4:.1f} Z",
                        "fill": fill, "stroke": stroke, "stroke-width": "1.7",
                    })
            reserve = 2.2 if n.get("representation_style") == "semantic" else 2.7
            text_center_y = (top + fs * reserve + top + h) / 2
        start_y = text_center_y - (total_lines - 1) * line_height / 2 + fs * 0.35

        for li, line in enumerate(label_lines):
            lbl = SubElement(node_group, "text", {
                "x": f"{x:.1f}",
                "y": f"{start_y + li * line_height:.1f}",
                "font-size": str(fs),
                "fill": n["text_color"],
                "text-anchor": "middle",
                "font-weight": "bold",
            })
            lbl.text = line

        # Sublabel
        if has_sub:
            sub = SubElement(node_group, "text", {
                "x": f"{x:.1f}",
                "y": f"{start_y + len(label_lines) * line_height:.1f}",
                "font-size": str(fs - 3),
                "fill": "#555555",
                "text-anchor": "middle",
            })
            sub.text = sanitize_text(n["sublabel"])

    # --- Free labels ---
    for label in spec.get("labels", []):
        anchor = label.get("anchor", "middle")
        if anchor not in ALLOWED_ANCHORS:
            anchor = "middle"
        if label.get("line_style"):
            lx, ly = label.get("x", 0), label.get("y", 0) - label.get("font_size", base_fs) * .3
            attrs = {"d": f"M{lx - 46:.1f},{ly:.1f} H{lx - 12:.1f}", "fill": "none",
                     "stroke": sanitize_color(label.get("color", "#555555")), "stroke-width": "2.4", "data-decoration": "legend-sample"}
            if label["line_style"] != "solid":
                attrs["stroke-dasharray"] = {"dashed": "8,4", "dotted": "3,3"}[label["line_style"]]
            SubElement(svg, "path", attrs)
        lbl = SubElement(svg, "text", {
            "x": f"{label.get('x', 0):.1f}",
            "y": f"{label.get('y', 0):.1f}",
            "font-size": str(label.get("font_size", base_fs)),
            "fill": sanitize_color(label.get("color", "#555555")),
            "text-anchor": anchor,
        })
        lbl.text = sanitize_text(label.get("text", ""))

    # Pretty print
    raw = tostring(svg, encoding="unicode")
    pretty = parseString(raw).toprettyxml(indent="  ")
    # Remove xml declaration line
    lines = pretty.split("\n")
    return "\n".join(lines[1:])


# ============================================================
# PNG Preview
# ============================================================

def svg_to_png(svg_path: str, png_path: str) -> bool:
    """Convert SVG to PNG preview."""
    import subprocess

    # Try rsvg-convert
    try:
        result = subprocess.run(
            ["rsvg-convert", "-o", png_path, svg_path],
            capture_output=True, timeout=30
        )
        if result.returncode == 0:
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Try cairosvg
    try:
        os.environ.setdefault("DYLD_LIBRARY_PATH", "/opt/homebrew/lib")
        import cairosvg
        cairosvg.svg2png(url=svg_path, write_to=png_path)
        return True
    except Exception:
        pass

    print("Warning: could not convert SVG to PNG (install rsvg-convert or cairosvg)")
    return False


# ============================================================
# Schema (for documentation)
# ============================================================

SCHEMA_DOC = """\
FigureSpec JSON Schema:
{
  "title": "string — figure title (metadata only, not rendered)",
  "canvas": {"width": int, "height": int},
  "style": {
    "font_family": "CSS font string",
    "font_size": int (default 14),
    "bg_color": "#RRGGBB",
    "palette": ["#color1", "#color2", ...]
  },
  "nodes": [{
    "id": "string (required, unique)",
    "label": "string (required, supports \\\\n for multi-line)",
    "x": int (required, center x),
    "y": int (required, center y),
    "width": int (default 120),
    "height": int (default 50),
    "shape": "rounded | rect | circle | ellipse | diamond | tensor (symbolic feature volume)",
    "representation": "optional feature-map | tokens; illustrative inset, not a dimension count",
    "representation_style": "classic (default) | semantic; requires representation",
    "header": "optional single-line module role; plain rectangular nodes only, no representation",
    "emphasis": "optional boolean; internal accent on an author-declared focal module",
    "fill": "#RRGGBB (auto from palette)",
    "stroke": "#RRGGBB (auto from palette)",
    "text_color": "#RRGGBB (default #333333)",
    "font_size": int (override),
    "role": "semantic role used by downstream QA",
    "operation": "optional exact fusion/operation name for a typed contract",
    "stage": "optional exact stage identifier",
    "tensor_shape": "optional shape string or JSON array; never inferred",
    "execution": "both (default) | training-only",
    "sublabel": "string (smaller text below label)"
  }],
  "edges": [{
    "id": "optional stable ID; generated as edge-N when absent",
    "from": "node_id (required)",
    "to": "node_id (required, same as from = self-loop)",
    "label": "string",
    "style": "solid | dashed | dotted; training-only defaults to dashed and forbids explicit solid",
    "color": "#RRGGBB (default #555555)",
    "thickness": int (default 2),
    "curve": bool (default false),
    "type": "main | skip | auxiliary | feedback | training-only | residual | conditioning",
    "source_port": {"side": "left | right | top | bottom", "offset": "0..1, default 0.5"},
    "target_port": {"side": "left | right | top | bottom", "offset": "0..1, default 0.5"},
    "label_segment": "midpoint (default) | longest-horizontal; missing horizontal segment is an error",
    "waypoints": [[x, y], ...] or [{"x": x, "y": y}, ...]
  }],
  "groups": [{
    "id": "string",
    "label": "string",
    "node_ids": ["id1", "id2"],
    "fill": "#RRGGBB",
    "stroke": "#RRGGBB",
    "padding": int (default 20)
  }],
  "labels": [{
    "text": "string",
    "x": int, "y": int,
    "font_size": int,
    "color": "#RRGGBB",
    "anchor": "start | middle | end",
    "line_style": "optional solid | dashed | dotted sample before a start-anchored label"
  }]
}
"""


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="ARIS FigureSpec → SVG Renderer")
    subparsers = parser.add_subparsers(dest="command")

    p_render = subparsers.add_parser("render", help="Render FigureSpec JSON to SVG")
    p_render.add_argument("spec_file", help="FigureSpec JSON file")
    p_render.add_argument("--output", "-o", default=None, help="Output SVG path")
    p_render.add_argument("--preview", action="store_true", help="Also generate PNG preview")

    p_validate = subparsers.add_parser("validate", help="Validate FigureSpec JSON")
    p_validate.add_argument("spec_file", help="FigureSpec JSON file")

    subparsers.add_parser("schema", help="Print FigureSpec schema documentation")

    args = parser.parse_args()

    if args.command == "schema":
        print(SCHEMA_DOC)
        return

    if args.command == "validate":
        with open(args.spec_file, encoding="utf-8") as f:
            spec = json.load(f)
        issues = validate_spec(spec)
        critical = sum(1 for i in issues if i.startswith("CRITICAL"))
        if not issues:
            print("OK: FigureSpec is valid")
        else:
            for issue in issues:
                print(f"  {issue}")
            print(f"\n{len(issues)} issues ({critical} critical)")
        sys.exit(1 if critical else 0)

    if args.command == "render":
        with open(args.spec_file, encoding="utf-8") as f:
            spec = json.load(f)

        issues = validate_spec(spec)
        critical = [i for i in issues if i.startswith("CRITICAL")]
        if critical:
            print("ERROR: Cannot render - critical issues:")
            for i in critical:
                print(f"  {i}")
            sys.exit(1)

        if issues:
            print(f"WARNING: {len(issues)} warnings:")
            for i in issues:
                print(f"  {i}")

        svg_content = render_svg(spec)

        # Output path
        if args.output:
            output = args.output
        else:
            base = Path(args.spec_file).stem
            output = str(Path(args.spec_file).parent / f"{base}.svg")

        Path(output).parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"OK: SVG written: {output}")

        if args.preview:
            png_path = str(Path(output).with_suffix(".png"))
            if svg_to_png(output, png_path):
                print(f"OK: PNG preview: {png_path}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
