#!/usr/bin/env python3
"""Render the exported ASCII STL parts as a shaded, exploded SVG preview."""
from pathlib import Path
import math
import re

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / "assets" / "hackpad16-cad-preview.svg"
PARTS = [
    ("lower_tray", "#26364a", (0, 0, 0), "Lower tray"),
    ("switch_plate", "#e2e8ed", (0, 0, 17), "Switch plate"),
    ("service_hatch", "#344960", (0, 0, -3), "Service hatch"),
    ("encoder_bezel", "#f17b35", (87, 18, 18), "Encoder bezel"),
    ("hackpad16_badge", "#f17b35", (60, 112, 19), "Raised badge"),
]
CAM = (1 / math.sqrt(3), -1 / math.sqrt(3), 1 / math.sqrt(3))
RIGHT = (1 / math.sqrt(2), 1 / math.sqrt(2), 0)
UP = (1 / math.sqrt(6), -1 / math.sqrt(6), -2 / math.sqrt(6))
LIGHT = (-0.35, -0.45, 0.82)


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def normalize(a):
    n = math.sqrt(dot(a, a))
    return tuple(x/n for x in a) if n else (0, 0, 1)


def rgb(hexcolor):
    return tuple(int(hexcolor[i:i+2], 16) for i in (1, 3, 5))


def shade(hexcolor, amount):
    base = rgb(hexcolor)
    factor = 0.48 + 0.52 * max(0, amount)
    return "#" + "".join(f"{min(255, int(c*factor)):02x}" for c in base)


def load_triangles(path):
    text = path.read_text()
    # OpenSCAD's ASCII STL output. Read each facet's three vertex lines.
    verts = re.findall(r"\bvertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)", text)
    if not verts or len(verts) % 3:
        raise ValueError(f"Could not parse STL triangles in {path}")
    pts = [tuple(map(float, v)) for v in verts]
    return [pts[i:i+3] for i in range(0, len(pts), 3)]


triangles = []
for part, color, offset, label in PARTS:
    path = HERE / f"{part}.stl"
    for tri in load_triangles(path):
        tri = [tuple(p[i] + offset[i] for i in range(3)) for p in tri]
        normal = normalize(cross(tuple(tri[1][i]-tri[0][i] for i in range(3)), tuple(tri[2][i]-tri[0][i] for i in range(3))))
        # Keep only camera-facing facets for a compact, clean outer shell.
        facing = dot(normal, CAM)
        if facing <= 1e-6:
            continue
        projected = [(dot(p, RIGHT), dot(p, UP)) for p in tri]
        depth = sum(dot(p, CAM) for p in tri) / 3
        lit = max(0, dot(normal, LIGHT))
        triangles.append((depth, projected, shade(color, lit), label))

if not triangles:
    raise SystemExit("No visible triangles found")

# SVG coordinates: SVG y points down, while projected y points up.
all_pts = [p for _, pts, _, _ in triangles for p in pts]
minx, maxx = min(p[0] for p in all_pts), max(p[0] for p in all_pts)
miny, maxy = min(p[1] for p in all_pts), max(p[1] for p in all_pts)
model_w, model_h = maxx-minx, maxy-miny
scale = min(1020/model_w, 700/model_h)
width, height = 1200, 900
xoff = (width-model_w*scale)/2
# Reserve top/bottom for title and the part legend.
yoff = 92 + (700-model_h*scale)/2

def xy(p):
    return (xoff+(p[0]-minx)*scale, yoff+(maxy-p[1])*scale)

parts = []
for _, pts, fill, _label in sorted(triangles, key=lambda t: t[0]):
    points = " ".join(f"{x:.2f},{y:.2f}" for x,y in map(xy, pts))
    parts.append(f'<polygon points="{points}" fill="{fill}"/>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900" role="img" aria-labelledby="title desc">
<title id="title">Hackpad 16 enclosure — CAD preview</title>
<desc id="desc">Shaded exploded isometric view generated directly from the OpenSCAD STL exports: lower tray, switch plate, service hatch, encoder bezel, and raised badge.</desc>
<defs><linearGradient id="bg" x2="0" y2="1"><stop stop-color="#f8fafc"/><stop offset="1" stop-color="#e8eef4"/></linearGradient><filter id="shadow" x="-10%" y="-10%" width="120%" height="120%"><feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#31445a" flood-opacity=".12"/></filter></defs>
<rect width="1200" height="900" rx="28" fill="url(#bg)"/>
<text x="72" y="67" font-family="Inter,Arial,sans-serif" font-size="30" font-weight="700" fill="#17283b">HACKPAD 16 · ENCLOSURE CAD</text>
<text x="74" y="96" font-family="Inter,Arial,sans-serif" font-size="15" fill="#5e7082">Exploded preview · 120 × 120 mm case · generated from printable STL geometry</text>
<g filter="url(#shadow)" stroke="#17283b" stroke-opacity=".22" stroke-width=".22" stroke-linejoin="round">{''.join(parts)}</g>
<line x1="70" y1="810" x2="1130" y2="810" stroke="#c7d2de"/>
<g font-family="Inter,Arial,sans-serif" font-size="15" fill="#31445a">
<circle cx="84" cy="846" r="8" fill="#26364a"/><text x="101" y="851">Lower tray</text>
<circle cx="267" cy="846" r="8" fill="#e2e8ed" stroke="#8292a1"/><text x="284" y="851">Switch plate</text>
<circle cx="462" cy="846" r="8" fill="#344960"/><text x="479" y="851">Service hatch</text>
<circle cx="655" cy="846" r="8" fill="#f17b35"/><text x="672" y="851">Encoder bezel</text>
<circle cx="846" cy="846" r="8" fill="#f17b35"/><text x="863" y="851">Raised badge</text>
<text x="1125" y="851" text-anchor="end" fill="#718195">OpenSCAD · mm</text>
</g></svg>'''
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg)
print(f"Wrote {OUT} ({len(triangles)} visible facets)")
