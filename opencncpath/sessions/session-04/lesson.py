"""Session 4 (Level 3): offset any convex polygon, find when the offset collapses, and cut a hexagonal pocket.

Educational toolpath geometry only. Real machining needs trained operators,
machine-specific post-processing and safety checks. Feeds and speeds here are
teaching numbers, not recommended cutting conditions.

Run:  python start.py 4
"""
# %% [markdown]
# # Session 4: offset any convex polygon
# **A. Real-world problem.** Sessions 2 and 3 could offset only a rectangle: shrink each side by
# the cutter radius. A hexagonal pocket (a nut seat, a bolt-head recess) has six sides at 120
# degrees, and a rectangle recipe does not work. How far does each corner of the cutter-centre path
# move? What happens when the offset gets larger than the pocket allows? And can the same idea
# give a full pocket path? Today we offset a convex polygon edge by edge, find the distance at
# which the offset collapses, fix the case where one edge disappears before the others, and cut a
# hexagonal pocket whose G-code we read back and simulate.
#
# **Plan.** (1) polygons and their angles, (2) offset edge by edge, (3) when an edge vanishes and
# when everything collapses, (4) rings and a pocket path for a hexagon, (5) G-code, simulation and
# check, (6) failure cases.

# %%
import math
import pathlib
import re

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 0: the pieces from Session 3, unchanged
# `HeightMap` (a grid of material heights that a flat cutter lowers), the G-code reader
# `read_moves`, `gcode_time_s` and `simulate_moves`, and the rectangle's corner leftover.

# %%
class HeightMap:
    def __init__(self, x0, x1, y0, y1, res):
        self.x0, self.y0, self.res = x0, y0, res
        self.nx, self.ny = int(round((x1 - x0) / res)), int(round((y1 - y0) / res))
        self.xc = x0 + (np.arange(self.nx) + 0.5) * res      # cell centres
        self.yc = y0 + (np.arange(self.ny) + 0.5) * res
        self.h = np.zeros((self.ny, self.nx))

    def stamp(self, x, y, z, r, ball=False):
        res = self.res
        i0, i1 = max(0, int((x - r - self.x0) / res) - 1), min(self.nx, int((x + r - self.x0) / res) + 2)
        j0, j1 = max(0, int((y - r - self.y0) / res) - 1), min(self.ny, int((y + r - self.y0) / res) + 2)
        if i0 >= i1 or j0 >= j1:
            return
        d2 = (self.xc[None, i0:i1] - x) ** 2 + (self.yc[j0:j1, None] - y) ** 2
        inside = d2 <= r * r
        surf = z + r - np.sqrt(np.maximum(r * r - d2, 0.0)) if ball else np.full(d2.shape, float(z))
        view = self.h[j0:j1, i0:i1]
        np.minimum(view, np.where(inside, surf, np.inf), out=view)

    def removed_volume(self):
        """Volume of removed material in mm^3."""
        return float(-self.h.sum() * self.res ** 2)


def corner_leftover(r):
    """Total leftover area (mm^2) in the four inside corners of a rectangular pocket."""
    return 4 * r * r * (1 - math.pi / 4)


TOKEN = re.compile(r"([GXYZIJF])(-?[0-9]*\.?[0-9]+)")


def read_moves(text):
    """Parse G0/G1/G3 text (modal) into dicts with kind, start, end, centre offsets, feed."""
    x = y = z = 0.0
    kind, feed, moves = "G0", 0.0, []
    for line in text.splitlines():
        t = {k: float(v) for k, v in TOKEN.findall(line.split("(")[0].upper())}
        if "G" in t and int(t["G"]) in (0, 1, 2, 3):
            kind = f"G{int(t['G'])}"
        feed = t.get("F", feed)
        if not ({"X", "Y", "Z"} & set(t)):
            continue
        nx_, ny_, nz_ = t.get("X", x), t.get("Y", y), t.get("Z", z)
        moves.append({"kind": kind, "a": (x, y, z), "b": (nx_, ny_, nz_), "ij": (t.get("I", 0.0), t.get("J", 0.0)), "f": feed})
        x, y, z = nx_, ny_, nz_
    return moves


def move_points(m, step):
    """Sample points (x, y, z) along a parsed straight move (this session uses G0 and G1 only)."""
    a, b = np.array(m["a"]), np.array(m["b"])
    n = max(1, int(math.ceil(np.linalg.norm(b - a) / step)))
    u = np.linspace(0.0, 1.0, n + 1)[:, None]
    return a + u * (b - a)


def moves_length(moves, kinds=("G1",)):
    return float(sum(np.linalg.norm(np.subtract(m["b"], m["a"])) for m in moves if m["kind"] in kinds))


def gcode_time_s(moves, rapid_rate=3000.0):
    t = 0.0
    for m in moves:
        rate = rapid_rate if m["kind"] == "G0" else m["f"]
        t += float(np.linalg.norm(np.subtract(m["b"], m["a"]))) / rate * 60.0
    return t


def simulate_moves(hm, moves, r):
    """Cut the height-map with every cutting move of a parsed program."""
    for m in moves:
        if m["kind"] == "G0":
            continue
        for x, y, z in move_points(m, hm.res):
            hm.stamp(x, y, z, r)
    return hm


# %% [markdown]
# ## Step 1: a convex polygon
# A polygon is a list of corners listed **counter-clockwise** (the inside is on the left when you
# walk along an edge). It is *convex* if every turn is to the left, that is, if the cross product
# of each pair of consecutive edge vectors is positive. At a corner the *interior angle* theta
# is 180 degrees minus the turning angle. A regular hexagon has six sides of equal length and six
# interior angles of 120 degrees; side a gives circumradius a and area (3 sqrt(3) / 2) a^2.
# The inward unit normal of an edge with direction (tx, ty) is (-ty, tx).

# %%
def regular_polygon(n, side, centre=(0.0, 0.0)):
    """Corners (counter-clockwise) of the regular n-gon with the given side length."""
    if n < 3:
        raise ValueError("a polygon needs at least 3 corners")
    R = side / (2.0 * math.sin(math.pi / n))
    return [(centre[0] + R * math.cos(2 * math.pi * k / n), centre[1] + R * math.sin(2 * math.pi * k / n)) for k in range(n)]


def polygon_area(pts):
    """Shoelace formula: positive for counter-clockwise corners (mm^2)."""
    return 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))


def polygon_perimeter(pts):
    return sum(math.hypot(x1 - x0, y1 - y0) for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))


def check_convex(pts, tol=1e-9):
    """Raise ValueError unless pts are the corners of a convex polygon listed counter-clockwise."""
    n = len(pts)
    if n < 3:
        raise ValueError("a polygon needs at least 3 corners")
    for i in range(n):
        a, b, c = pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if cross <= tol:
            raise ValueError("the corners must be convex and listed counter-clockwise (every turn to the left)")
    if polygon_area(pts) <= 0:
        raise ValueError("the polygon winds the wrong way (area is not positive)")


def interior_angles(pts):
    """Interior angle (radians) at each corner of a convex counter-clockwise polygon."""
    n, out = len(pts), []
    for i in range(n):
        p, q, r = pts[i - 1], pts[i], pts[(i + 1) % n]
        a, b = (p[0] - q[0], p[1] - q[1]), (r[0] - q[0], r[1] - q[1])
        out.append(math.atan2(abs(a[0] * b[1] - a[1] * b[0]), a[0] * b[0] + a[1] * b[1]))
    return out


def edge_lines(pts):
    """For each edge i (from corner i to corner i + 1): its inward unit normal n and c = n . p_i."""
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        L = math.hypot(x1 - x0, y1 - y0)
        n = (-(y1 - y0) / L, (x1 - x0) / L)
        out.append((n, n[0] * x0 + n[1] * y0))
    return out


def dist_to_edge_line(pt, line):
    """Signed distance from pt to an edge's line: positive on the inside (mm)."""
    n, c = line
    return n[0] * pt[0] + n[1] * pt[1] - c


# %% [markdown]
# ## Step 2: offset edge by edge
# Move every edge inwards by d along its normal. Two consecutive shifted lines meet in a new
# corner. That is all the recipe needs, and it explains the numbers:
#
# * the new corner lies on the bisector of the old one, **d / sin(theta / 2)** away from it;
# * every edge keeps its direction, but its length changes to
#   **L' = L - d (cot(theta_a / 2) + cot(theta_b / 2))**, with theta_a and theta_b the interior
#   angles at its two ends;
# * while no edge has vanished, the area is **A(d) = A - P d + d^2 (sum of cot(theta_i / 2))**, with
#   P the perimeter.
#
# For the hexagon of side 20 mm and d = 3 mm: the corner moves 3 / sin 60 = 3.464 mm, and each
# side shrinks from 20 to 20 - 3 x 2 x cot 60 = 16.536 mm.

# %%
def intersect_lines(l1, l2):
    (n1, c1), (n2, c2) = l1, l2
    det = n1[0] * n2[1] - n1[1] * n2[0]
    if abs(det) < 1e-12:
        raise ValueError("parallel edges have no common corner")
    return ((c1 * n2[1] - c2 * n1[1]) / det, (n1[0] * c2 - n2[0] * c1) / det)


def offset_edges(pts, d):
    """Edge-by-edge offset: shift each edge by d and intersect neighbours. Correct only while no edge vanishes."""
    check_convex(pts)
    lines = [(n, c + d) for n, c in edge_lines(pts)]
    return [intersect_lines(lines[i - 1], lines[i]) for i in range(len(pts))]


def corner_shift(theta, d):
    """How far a corner of interior angle theta moves along its bisector (mm)."""
    return d / math.sin(theta / 2.0)


def offset_edge_length(L, theta_a, theta_b, d):
    """Length of an edge after the offset d (negative means the edge has already vanished)."""
    return L - d * (1.0 / math.tan(theta_a / 2.0) + 1.0 / math.tan(theta_b / 2.0))


def edge_vanish_distance(pts):
    """The smallest offset d at which any edge has length zero (mm)."""
    n, th, best = len(pts), interior_angles(pts), math.inf
    for i in range(n):
        L = math.hypot(pts[(i + 1) % n][0] - pts[i][0], pts[(i + 1) % n][1] - pts[i][1])
        best = min(best, L / (1.0 / math.tan(th[i] / 2) + 1.0 / math.tan(th[(i + 1) % n] / 2)))
    return best


def offset_area_formula(pts, d):
    """Area of the offset polygon while no edge has vanished (mm^2)."""
    return polygon_area(pts) - polygon_perimeter(pts) * d + d * d * sum(1.0 / math.tan(t / 2.0) for t in interior_angles(pts))


def signed_edge_lengths(pts, ref):
    """Length of each edge measured along the direction of the same edge of the reference polygon (negative = reversed)."""
    out = []
    for i in range(len(pts)):
        a, b = ref[i], ref[(i + 1) % len(ref)]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        t = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
        p, q = pts[i], pts[(i + 1) % len(pts)]
        out.append((q[0] - p[0]) * t[0] + (q[1] - p[1]) * t[1])
    return out


# %% [markdown]
# ## Step 3: when an edge vanishes, and when everything collapses
# The edge-by-edge recipe silently breaks when an edge shrinks to zero before the others: the two
# neighbouring lines then cross *behind* each other and the "offset" polygon has a reversed
# edge. The correct offset is the **intersection of the shifted half-planes**: keep the part of
# the polygon that is at least d from every edge line. We compute it by clipping the polygon
# against one shifted line after another (Sutherland-Hodgman). Edges that vanish simply drop out
# of the result; when nothing is left, the offset has *collapsed* and the function says so
# (returns None). The **collapse distance** is the radius of the largest circle that fits
# inside the polygon (the inscribed circle); for a regular polygon it is the apothem
# a / (2 tan(pi / n)), which is 17.32 mm for the hexagon of side 20 mm.

# %%
def clip_halfplane(poly, n, c, eps=1e-12):
    """The part of a convex polygon with n . x >= c."""
    out, m = [], len(poly)
    for i in range(m):
        a, b = poly[i], poly[(i + 1) % m]
        sa = n[0] * a[0] + n[1] * a[1] - c
        sb = n[0] * b[0] + n[1] * b[1] - c
        if sa >= -eps:
            out.append(a)
        if (sa > eps and sb < -eps) or (sa < -eps and sb > eps):
            t = sa / (sa - sb)
            out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return out


def dedupe(poly, tol=1e-9):
    out = []
    for p in poly:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > tol:
            out.append(p)
    while len(out) > 1 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) <= tol:
        out.pop()
    return out


def offset_polygon(pts, d):
    """Inward offset of a convex polygon by d mm. None if it has collapsed; 1 or 2 points if it has degenerated to a point or a segment."""
    check_convex(pts)
    if d < 0:
        raise ValueError("an inward offset needs d >= 0 (a negative d would grow the polygon)")
    poly = [tuple(map(float, p)) for p in pts]
    for n, c in edge_lines(pts):
        poly = clip_halfplane(poly, n, c + d)
        if not poly:
            return None
    poly = dedupe(poly)
    return poly or None


def collapse_distance(pts, iters=200):
    """Largest d for which the offset is not empty: the inscribed-circle radius (mm), by bisection."""
    check_convex(pts)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    lo, hi = 0.0, max(max(xs) - min(xs), max(ys) - min(ys))
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if offset_polygon(pts, mid) is None:
            hi = mid
        else:
            lo = mid
    return lo


def apothem(n, side):
    """Distance from the centre of a regular n-gon to the middle of a side (mm)."""
    return side / (2.0 * math.tan(math.pi / n))


# %% [markdown]
# ## Step 4: rings and a pocket path for the hexagon
# A cutter of diameter D has radius r = D / 2; its centre must stay at least r from every wall, so
# the centre path is the polygon offset by r. To clear the whole pocket we cut rings at the
# offsets r, r + s, ... up to the collapse distance, with a stepover s no larger than D. The
# number of rings is n = ceil((rho - r) / s) + 1 with rho the collapse distance, and the spacing is
# spread evenly so that the last ring sits exactly at the collapse: a point for a regular
# polygon. Rings are cut from the wall inwards; between rings the cutter travels in a straight
# link inside the area it has already cleared, so it never lifts within a layer.

# %%
def ring_offsets(pts, d, s):
    """Offsets of the rings (mm) for a cutter of diameter d and stepover s. Raises ValueError if it cannot be done."""
    r, rho = d / 2.0, collapse_distance(pts)
    if r > rho + 1e-9:
        raise ValueError(f"cutter diameter {d:g} mm does not fit: the largest circle in this pocket has diameter {2 * rho:.3f} mm")
    if s > d + 1e-12:
        raise ValueError("stepover larger than the cutter diameter leaves uncut strips")
    span = rho - r
    if span < 1e-9:
        return [r]
    n = math.ceil(span / s - 1e-9) + 1
    return [float(v) for v in np.linspace(r, rho, n)]


def ring_points(pts, offset, start):
    """Corner list of one ring, closed, starting at the corner nearest to start (a point near the previous ring)."""
    poly = None
    for k in range(4):                    # the last ring sits on the collapse distance: allow for rounding
        poly = offset_polygon(pts, offset - k * 1e-9)
        if poly is not None:
            break
    if poly is None:
        raise ValueError("offset beyond the collapse distance")
    if len(poly) < 3:
        return poly
    k = min(range(len(poly)), key=lambda i: math.hypot(poly[i][0] - start[0], poly[i][1] - start[1]))
    poly = poly[k:] + poly[:k]
    return poly + [poly[0]]


def pocket_path(pts, d, s):
    """The centre path for one layer as a single polyline: all rings from the wall inwards, joined by short links."""
    path, start = [], pts[0]
    for off in ring_offsets(pts, d, s):
        ring = ring_points(pts, off, start)
        path.extend(ring)
        start = ring[-1]
    return np.array(path)


def path_length(path):
    return float(np.hypot(*np.diff(np.asarray(path, dtype=float), axis=0).T).sum())


def corner_leftover_polygon(pts, r):
    """Area (mm^2) a round cutter of radius r cannot reach in the corners: r^2 (cot(theta/2) - (pi - theta)/2) per corner."""
    return sum(r * r * (1.0 / math.tan(t / 2.0) - (math.pi - t) / 2.0) for t in interior_angles(pts))


def expected_volume(pts, depth, d):
    """Analytic target: polygon area minus the corner leftovers, times the depth (mm^3)."""
    return (polygon_area(pts) - corner_leftover_polygon(pts, d / 2.0)) * depth


# %% [markdown]
# ## Step 5: G-code for the hexagonal pocket, then simulate that G-code
# Per layer: rapid to the start of the outermost ring, plunge once, cut all the rings in one
# unbroken path, lift. The layers number ceil(depth / depth_of_cut). We parse the text back, take
# the cutting time from the parsed moves, cut the height-map with them and compare the volume
# with the analytic target.

# %%
def pocket_gcode(pts, depth, d, doc, s, feed, plunge, lift=1.0):
    path = pocket_path(pts, d, s)
    layers = math.ceil(depth / doc - 1e-9)
    dz = depth / layers
    f = lambda v: f"{v:.3f}".rstrip("0").rstrip(".") or "0"
    out = ["G21", "G90", f"G0 Z{f(lift)}"]
    for k in range(1, layers + 1):
        z = -k * dz
        out += [f"G0 X{f(path[0][0])} Y{f(path[0][1])}", f"G1 Z{f(z)} F{f(plunge)}"]
        out += [f"G1 X{f(x)} Y{f(y)} F{f(feed)}" for x, y in path[1:]]
        out.append(f"G0 Z{f(lift)}")
    out.append("G0 Z5")
    return "\n".join(out) + "\n"


def simulate_pocket(pts, depth, d, doc, s, feed, plunge, res=0.05):
    """Generate, parse and simulate the program: (height-map, parsed moves, G-code text)."""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    pad = 0.5
    hm = HeightMap(min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad, res)
    text = pocket_gcode(pts, depth, d, doc, s, feed, plunge)
    mv = read_moves(text)
    simulate_moves(hm, mv, d / 2.0)
    return hm, mv, text


def cut_outside_area(hm, pts):
    """Area (mm^2) of cut cells whose centre lies outside the polygon."""
    X, Y = np.meshgrid(hm.xc, hm.yc)
    inside = np.ones(X.shape, dtype=bool)
    for n, c in edge_lines(pts):
        inside &= (n[0] * X + n[1] * Y - c) >= 0
    return float(((hm.h < -1e-9) & ~inside).sum() * hm.res ** 2)


# %% [markdown]
# ## Step 6: failure cases
# * a polygon that is not convex (an L-shape) or is listed clockwise: refused;
# * a negative offset (that would grow the polygon): refused;
# * an offset beyond the collapse distance: `None`;
# * a cutter whose diameter is more than the inscribed circle: refused with a clear message;
# * the edge-by-edge recipe after an edge has vanished: reversed edge, wrong area. The trapezoid
#   below (base 40 mm, top 4 mm, height 20 mm) loses its top edge at d = 4.49 mm but does not
#   collapse until d = 8.91 mm, so between those the correct offset is a triangle.

# %%
TRAPEZOID = [(0.0, 0.0), (40.0, 0.0), (22.0, 20.0), (18.0, 20.0)]
L_SHAPE = [(0.0, 0.0), (20.0, 0.0), (20.0, 10.0), (10.0, 10.0), (10.0, 20.0), (0.0, 20.0)]

# %% [markdown]
# ## Step 7: see it

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    BLUE, ORANGE, MAGENTA, GREY = "#0072b2", "#c86a00", "#d81b60", "#555555"
    side, D, s, depth, doc, feed, plunge = 20.0, 6.0, 4.0, 5.0, 2.0, 300.0, 100.0
    hexa = regular_polygon(6, side)
    off = offset_polygon(hexa, 3.0)
    print("hexagon area", round(polygon_area(hexa), 3), "perimeter", polygon_perimeter(hexa))
    lines = edge_lines(hexa)
    worst = max(abs(dist_to_edge_line(v, lines[i - 1]) - 3.0) for i, v in enumerate(offset_edges(hexa, 3.0)))
    print("offset corners (edge by edge) vs 3 mm from the two neighbouring edges: worst error", worst)
    print("corner shift", round(corner_shift(math.pi * 2 / 3, 3.0), 4), " new side", round(math.hypot(off[1][0] - off[0][0], off[1][1] - off[0][1]), 4),
          " formula", round(offset_edge_length(side, 2 * math.pi / 3, 2 * math.pi / 3, 3.0), 4))
    print("area of the offset hexagon", round(polygon_area(off), 3), " formula", round(offset_area_formula(hexa, 3.0), 3))
    rho = collapse_distance(hexa)
    print("collapse distance", round(rho, 6), " apothem", round(apothem(6, side), 6), " offset just inside has", len(offset_polygon(hexa, rho - 1e-6)), "corners; just outside:", offset_polygon(hexa, rho + 1e-6))
    trap_edge, trap_rho = edge_vanish_distance(TRAPEZOID), collapse_distance(TRAPEZOID)
    naive, good = offset_edges(TRAPEZOID, 6.0), offset_polygon(TRAPEZOID, 6.0)
    print("trapezoid: edge vanishes at", round(trap_edge, 4), " collapses at", round(trap_rho, 4))
    print("   at d = 6: edge-by-edge corners", [tuple(round(v, 2) for v in p) for p in naive], " signed edge lengths", [round(v, 2) for v in signed_edge_lengths(naive, TRAPEZOID)])
    print("   clipping gives", [tuple(round(v, 2) for v in p) for p in good], " area", round(polygon_area(good), 3), "vs edge-by-edge", round(polygon_area(naive), 3))
    offs = ring_offsets(hexa, D, s)
    path = pocket_path(hexa, D, s)
    print("rings", len(offs), "offsets", [round(v, 3) for v in offs], " one-layer path", round(path_length(path), 2), "mm")
    hm, mv, text = simulate_pocket(hexa, depth, D, doc, s, feed, plunge)
    exp = expected_volume(hexa, depth, D)
    print(f"G-code: {len(text.splitlines())} lines, cutting time {gcode_time_s(mv):.1f} s, simulated {hm.removed_volume():.1f} mm^3, expected {exp:.1f} mm^3 ({100 * (hm.removed_volume() / exp - 1):+.2f} %), cut outside {cut_outside_area(hm, hexa):.3f} mm^2")

    # Figure 1: offset hexagon and the vanishing edge of the trapezoid
    fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.6))
    ax = axs[0]
    for d_, col in ((0.0, GREY), (3.0, BLUE), (8.0, ORANGE), (14.0, MAGENTA)):
        p = offset_polygon(hexa, d_)
        q = p + [p[0]]
        ax.plot([a for a, b in q], [b for a, b in q], "-", color=col, label=f"offset {d_:g} mm")
    ax.plot([0], [0], "k+")
    ax.set_aspect("equal"); ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)"); ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2); ax.grid(alpha=0.3)
    ax.set_title("Hexagon, side 20 mm: offsets shrink and keep the shape", fontsize=9)
    ax = axs[1]
    closed = lambda p: p + [p[0]]
    ax.plot(*zip(*closed(TRAPEZOID)), color=GREY, label="trapezoid")
    ax.plot(*zip(*closed(offset_polygon(TRAPEZOID, 3.0))), color=BLUE, label="offset 3 mm (4 corners)")
    ax.plot(*zip(*closed(offset_polygon(TRAPEZOID, 6.0))), color=ORANGE, label="offset 6 mm (clipping: a triangle)")
    ax.plot(*zip(*closed(offset_edges(TRAPEZOID, 6.0))), color=MAGENTA, ls="--", label="offset 6 mm edge by edge (wrong)")
    ax.set_aspect("equal"); ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)"); ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2); ax.grid(alpha=0.3)
    ax.set_title("An edge vanishes at 4.49 mm, before the collapse at 8.91 mm", fontsize=9)
    fig.tight_layout(); fig.savefig(OUT / "offsets_and_vanishing_edge.png", dpi=120, bbox_inches="tight")

    # Figure 2: area against the offset, formula and clipping
    fig2, ax2 = plt.subplots(figsize=(6.4, 4))
    ds = np.linspace(0, rho, 200)
    ax2.plot(ds, [polygon_area(offset_polygon(hexa, x)) if len(offset_polygon(hexa, x)) > 2 else 0.0 for x in ds], color=BLUE, label="area of the offset hexagon")
    ax2.plot(ds, [offset_area_formula(hexa, x) for x in ds], color=ORANGE, ls="--", label="A - P d + d^2 sum cot(theta/2)")
    ax2.axvline(rho, color=GREY, ls=":"); ax2.text(rho - 0.3, 600, "collapse\n17.32 mm", ha="right", fontsize=8)
    ax2.set_xlabel("offset d (mm)"); ax2.set_ylabel("area (mm^2)"); ax2.grid(alpha=0.3); ax2.legend(fontsize=8)
    ax2.set_title("The formula and the clipped offset agree for the hexagon", fontsize=9)
    fig2.tight_layout(); fig2.savefig(OUT / "area_vs_offset.png", dpi=120)

    # Figure 3: pocket path and simulated height-map
    fig3, axs3 = plt.subplots(1, 2, figsize=(10.4, 4.6))
    ax = axs3[0]
    ax.plot(*zip(*closed([tuple(p) for p in hexa])), color=GREY)
    ax.plot(path[:, 0], path[:, 1], "-", color=BLUE, lw=1.2)
    ax.plot(path[0, 0], path[0, 1], "o", color=ORANGE, ms=6, label="plunge point")
    ax.set_aspect("equal"); ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)"); ax.grid(alpha=0.3); ax.legend(fontsize=8)
    ax.set_title(f"{len(offs)} rings joined into one path ({path_length(path):.0f} mm per layer)", fontsize=9)
    ax = axs3[1]
    xs_, ys_ = [p[0] for p in hexa], [p[1] for p in hexa]
    im = ax.imshow(hm.h, origin="lower", extent=(min(xs_) - 0.5, max(xs_) + 0.5, min(ys_) - 0.5, max(ys_) + 0.5), cmap="viridis")
    fig3.colorbar(im, ax=ax, label="material height (mm)", fraction=0.046)
    ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)")
    ax.set_title(f"Simulated pocket: {hm.removed_volume():.0f} mm^3 removed (target {exp:.0f})", fontsize=9)
    fig3.tight_layout(); fig3.savefig(OUT / "hexagon_pocket.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
