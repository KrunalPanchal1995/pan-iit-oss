"""Session 5 (Level 3): a contour-parallel pocket with a round boss, in one unbroken cut.

Educational toolpath geometry only. Real machining needs trained operators,
machine-specific post-processing and safety checks. Feeds and speeds here are
teaching numbers, not recommended cutting conditions.

Run:  python start.py 5
"""
# %% [markdown]
# # Session 5: a pocket with a boss, cut without lifting the cutter
# **A. Real-world problem.** The Session 3 program for a 40 x 30 mm pocket with a 12 mm boss
# lifts the cutter 25 times per layer: every row that meets the boss is cut in two pieces,
# and each piece is a lift, a rapid move and a plunge. It needs 315.5 s. A contour-parallel
# path follows the walls and the boss at a steady distance, so it can be one unbroken cut.
# The hard part is the join: as the rings move inward they touch the boss's ring, split into
# two crescents at the narrow neck and finally shrink to four points. Today we build that
# path from the *clearance field* (how far the cutter centre is from the nearest wall or
# boss), cut it with straight moves and arcs (G1, G2), and check time and volume.
#
# **Plan.** (1) the clearance field and the largest clearance, (2) one ring (level set) as
# lines and arcs, (3) rings that split, as a tree of loops, (4) joining the loops without a
# lift, (5) G-code with arcs, simulation and the comparison with the raster program,
# (6) failure cases.

# %%
import math
import pathlib
import re

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 0: the pieces from Session 3, unchanged
# `HeightMap`, the raster program `boss_pocket_gcode` (our baseline), the G-code reader (it
# already understands G2 and G3 arcs), the time and simulation helpers and the analytic volume.

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

    def cut_polyline(self, pts, z, r, ball=False):
        """Sweep the cutter along a polyline at constant tip height z."""
        pts = np.asarray(pts, dtype=float)
        for a, b in zip(pts[:-1], pts[1:]):
            n = max(1, int(np.ceil(np.linalg.norm(b - a) / self.res)))
            for t in np.linspace(0.0, 1.0, n + 1):
                self.stamp(*(a + t * (b - a)), z, r, ball)

    def removed_volume(self):
        """Volume of removed material in mm^3."""
        return float(-self.h.sum() * self.res ** 2)

    def removed_area(self, floor=-1e-9):
        """Footprint area (mm^2) of cells cut at all."""
        return float((self.h < floor).sum() * self.res ** 2)


def n_lines(span, s):
    """Lines needed to cover a span with spacing at most s (end lines included)."""
    return math.ceil(span / s - 1e-9) + 1


def corner_leftover(r):
    """Total leftover area (mm^2) in the four inside corners of a rectangular pocket."""
    return 4 * r * r * (1 - math.pi / 4)


def boss_pocket_gcode(w, h, depth, d, doc, s, feed, plunge, boss_c, boss_d, lift=1.0):
    r, R = d / 2, boss_d / 2 + d / 2
    layers = math.ceil(depth / doc - 1e-9)
    dz = depth / layers
    n = n_lines(h - d, s)
    ys = np.linspace(r, h - r, n)
    f = lambda v: f"{v:.3f}".rstrip("0").rstrip(".")
    out = ["G21", "G90", f"G0 Z{f(lift)}"]
    for k in range(1, layers + 1):
        z = -k * dz
        for j, y in enumerate(ys):
            dy = y - boss_c[1]
            if abs(dy) < R - 1e-9:
                half = math.sqrt(R * R - dy * dy)
                segs = [(r, boss_c[0] - half), (boss_c[0] + half, w - r)]
            else:
                segs = [(r, w - r)]
            if j % 2 == 1:
                segs = [(b, a) for a, b in reversed(segs)]
            for a, b in segs:
                out += [f"G0 X{f(a)} Y{f(y)}", f"G1 Z{f(z)} F{f(plunge)}", f"G1 X{f(b)} F{f(feed)}", f"G0 Z{f(lift)}"]
        out += [f"G0 X{f(boss_c[0] + R)} Y{f(boss_c[1])}", f"G1 Z{f(z)} F{f(plunge)}",
                f"G3 X{f(boss_c[0] + R)} Y{f(boss_c[1])} I{f(-R)} J0 F{f(feed)}", f"G0 Z{f(lift)}"]
        # wall pass: one lap round the pocket outline, which removes the scallops at the line ends
        out += [f"G0 X{f(r)} Y{f(r)}", f"G1 Z{f(z)} F{f(plunge)}", f"G1 X{f(w - r)} F{f(feed)}",
                f"G1 Y{f(h - r)}", f"G1 X{f(r)}", f"G1 Y{f(r)}", f"G0 Z{f(lift)}"]
    out.append("G0 Z5")
    return "\n".join(out) + "\n"


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
    """Sample points (x, y, z) along a parsed move."""
    a, b = np.array(m["a"]), np.array(m["b"])
    if m["kind"] in ("G2", "G3"):
        c = a[:2] + np.array(m["ij"])
        rad = float(np.hypot(*(a[:2] - c)))
        a0, a1 = math.atan2(*(a[1::-1] - c[1::-1])), math.atan2(*(b[1::-1] - c[1::-1]))
        sw = (a1 - a0) % (2 * math.pi) if m["kind"] == "G3" else (a0 - a1) % (2 * math.pi)
        if sw < 1e-12 and np.allclose(a[:2], b[:2]):
            sw = 2 * math.pi
        n = max(1, int(math.ceil(rad * sw / step)))
        sgn = 1.0 if m["kind"] == "G3" else -1.0
        u = np.linspace(0.0, 1.0, n + 1)
        ang = a0 + sgn * sw * u
        return np.stack([c[0] + rad * np.cos(ang), c[1] + rad * np.sin(ang), a[2] + (b[2] - a[2]) * u], axis=1)
    n = max(1, int(math.ceil(np.linalg.norm(b - a) / step)))
    u = np.linspace(0.0, 1.0, n + 1)[:, None]
    return a + u * (b - a)


def moves_length(moves, kinds=("G1", "G2", "G3")):
    total = 0.0
    for m in moves:
        if m["kind"] in kinds:
            pts = move_points(m, 0.02)
            total += float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())
    return total


def gcode_time_s(moves, rapid_rate=3000.0):
    t = 0.0
    for m in moves:
        rate = rapid_rate if m["kind"] == "G0" else m["f"]
        pts = move_points(m, 0.02)
        t += float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum()) / rate * 60.0
    return t


def simulate_moves(hm, moves, r):
    """Cut the height-map with every cutting move of a parsed program."""
    for m in moves:
        if m["kind"] == "G0":
            continue
        for x, y, z in move_points(m, hm.res):
            hm.stamp(x, y, z, r)
    return hm


def boss_expected_volume(w, h, depth, d, boss_d):
    """Analytic target: pocket minus boss minus four corner leftovers, times depth (mm^3)."""
    return (w * h - math.pi * (boss_d / 2) ** 2 - corner_leftover(d / 2)) * depth


# %% [markdown]
# ## Step 1: the clearance field
# The cutter centre may stand at (x, y) only if the whole cutter fits: it must be at least r
# from every wall and at least (boss radius + r) from the boss centre. Define the **clearance**
# phi(x, y) = min(x, w - x, y, h - y, distance to the boss centre - boss radius): the distance
# from the point to the nearest wall or to the boss. The centre may stand where phi >= r.
# The set phi = l (a *level set*) is a closed curve: the cutter centre path that stays exactly
# l away from everything. The first ring is l = r (the cutter touches the walls). Rings farther
# in have bigger l, until l reaches the **largest clearance** rho_max, the radius of the
# biggest circle that fits in the pocket without touching the boss.

# %%
def clearance(x, y, w, h, boss_c, boss_r):
    """Distance from (x, y) to the nearest wall or to the boss surface (mm)."""
    return min(x, w - x, y, h - y, math.hypot(x - boss_c[0], y - boss_c[1]) - boss_r)


def check_setup(w, h, boss_c, boss_d, d, s):
    """Refuse set-ups that have no pocket path (see Step 6)."""
    if min(w, h, d, s, boss_d) <= 0:
        raise ValueError("sizes, cutter diameter and stepover must be positive")
    if s > d + 1e-12:
        raise ValueError(f"stepover {s:g} mm is larger than the cutter diameter {d:g} mm: strips of material would be left")
    br = boss_d / 2
    gap = min(boss_c[0], w - boss_c[0], boss_c[1], h - boss_c[1]) - br
    if gap <= 0:
        raise ValueError("the boss must lie completely inside the pocket, away from every wall")
    if abs(gap - d) < 1e-9:
        raise ValueError(f"the cutter just fits (gap {gap:g} mm = diameter {d:g} mm) between the boss and a wall: no room to move along the gap")


def level_nonempty(w, h, boss_c, boss_r, ell):
    """True if some point has clearance >= ell: the shrunken rectangle must not lie inside the boss circle."""
    x0, y0, x1, y1 = ell, ell, w - ell, h - ell
    if x1 < x0 or y1 < y0:
        return False
    return any(math.hypot(x - boss_c[0], y - boss_c[1]) >= boss_r + ell for x in (x0, x1) for y in (y0, y1))


def max_clearance(w, h, boss_c, boss_d):
    """Largest clearance rho_max, by bisection (the shrunken rectangle gets smaller and the boss circle bigger as l grows)."""
    br = boss_d / 2
    lo, hi = 0.0, 0.5 * min(w, h)
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if level_nonempty(w, h, boss_c, br, mid):
            lo = mid
        else:
            hi = mid
    return lo


def level_offsets(rho, r, s):
    """Clearance of each ring: r, r + s, r + 2s, ... as long as it is at most rho. A last ring at rho is added
    only if the cutter, which reaches r beyond the last ring, would not reach the largest clearance."""
    if r > rho + 1e-12:
        raise ValueError(f"the cutter radius {r:g} mm does not fit: the largest clearance is only {rho:.3f} mm")
    offs = [r]
    while offs[-1] + s <= rho - 1e-9:
        offs.append(offs[-1] + s)
    if rho - offs[-1] > r:
        offs.append(rho)
    return [float(v) for v in offs]


# %% [markdown]
# ## Step 2: one ring as lines and arcs
# The level set phi = l is the boundary of "the rectangle shrunk by l, minus the disc of radius
# (boss radius + l)". It is made of **line pieces** (rectangle sides outside the disc) and **arc
# pieces** (the circle, inside the rectangle). We find where each side meets the circle (a
# quadratic equation), keep the parts of the side outside the disc, keep the arcs of the circle
# inside the rectangle, and chain the pieces end to start into closed loops. A piece is
# `("L", a, b)` or `("A", centre, radius, start_angle, sweep)`; the sweep is negative (clockwise,
# G2) because the material to be cut lies outside the circle.

# %%
TWO_PI = 2 * math.pi


def piece_start(p):
    if p[0] == "L":
        return p[1]
    _, c, R, a0, sw = p
    return (c[0] + R * math.cos(a0), c[1] + R * math.sin(a0))


def piece_end(p):
    if p[0] == "L":
        return p[2]
    _, c, R, a0, sw = p
    return (c[0] + R * math.cos(a0 + sw), c[1] + R * math.sin(a0 + sw))


def piece_length(p):
    return math.hypot(p[2][0] - p[1][0], p[2][1] - p[1][1]) if p[0] == "L" else abs(p[4]) * p[2]


def level_pieces(w, h, boss_c, boss_r, ell):
    """Line and arc pieces of the level set phi = ell (unordered)."""
    x0, y0, x1, y1 = ell, ell, w - ell, h - ell
    if x1 < x0 - 1e-12 or y1 < y0 - 1e-12:
        return []
    R = boss_r + ell
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    pieces, angles = [], []
    for i in range(4):
        P0, P1 = corners[i], corners[(i + 1) % 4]
        dx, dy = P1[0] - P0[0], P1[1] - P0[1]
        a = dx * dx + dy * dy
        if a < 1e-18:
            continue
        b = 2 * (dx * (P0[0] - boss_c[0]) + dy * (P0[1] - boss_c[1]))
        cc = (P0[0] - boss_c[0]) ** 2 + (P0[1] - boss_c[1]) ** 2 - R * R
        disc = b * b - 4 * a * cc
        ts = [0.0, 1.0]
        if disc > 1e-12:
            sq = math.sqrt(disc)
            for t in ((-b - sq) / (2 * a), (-b + sq) / (2 * a)):
                if 1e-9 < t < 1 - 1e-9:
                    ts.append(t)
                    angles.append(math.atan2(P0[1] + t * dy - boss_c[1], P0[0] + t * dx - boss_c[0]))
        ts.sort()
        for ta, tb in zip(ts[:-1], ts[1:]):
            if tb - ta < 1e-12:
                continue
            tm = 0.5 * (ta + tb)
            if math.hypot(P0[0] + tm * dx - boss_c[0], P0[1] + tm * dy - boss_c[1]) >= R:
                pieces.append(("L", (P0[0] + ta * dx, P0[1] + ta * dy), (P0[0] + tb * dx, P0[1] + tb * dy)))
    inside = lambda x, y: x0 + 1e-9 < x < x1 - 1e-9 and y0 + 1e-9 < y < y1 - 1e-9
    if angles:
        angles = sorted(a % TWO_PI for a in angles)
        for k in range(len(angles)):
            a, b = angles[k], angles[(k + 1) % len(angles)]
            if k == len(angles) - 1:
                b += TWO_PI
            mid = 0.5 * (a + b)
            if inside(boss_c[0] + R * math.cos(mid), boss_c[1] + R * math.sin(mid)):
                pieces.append(("A", boss_c, R, b, -(b - a)))
    elif boss_c[0] - R > x0 and boss_c[0] + R < x1 and boss_c[1] - R > y0 and boss_c[1] + R < y1:
        pieces.append(("A", boss_c, R, 0.0, -TWO_PI))     # the circle lies wholly inside: a closed hole
    return pieces


def chain_loops(pieces, tol=1e-6):
    """Join pieces end to start into closed loops (lists of pieces)."""
    rest, loops = list(pieces), []
    while rest:
        loop = [rest.pop(0)]
        while True:
            e, s0 = piece_end(loop[-1]), piece_start(loop[0])
            if math.hypot(e[0] - s0[0], e[1] - s0[1]) < tol:
                break
            for i, p in enumerate(rest):
                s_ = piece_start(p)
                if math.hypot(e[0] - s_[0], e[1] - s_[1]) < tol:
                    loop.append(rest.pop(i))
                    break
            else:
                raise ValueError("the pieces of this ring do not close")
        loops.append(loop)
    return loops


def sample_loop(loop, step=0.2):
    """Corner points of a loop, with arcs sampled every `step` mm (for area and inside tests)."""
    pts = []
    for p in loop:
        if p[0] == "L":
            pts.append(p[1])
        else:
            n = max(2, int(abs(p[4]) * p[2] / step) + 1)
            pts += [(p[1][0] + p[2] * math.cos(p[3] + p[4] * k / n), p[1][1] + p[2] * math.sin(p[3] + p[4] * k / n)) for k in range(n)]
    return pts


def signed_area(pts):
    """Shoelace area: positive for a counter-clockwise loop (an outside boundary), negative for a hole."""
    return 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))


def point_in_polygon(pt, poly):
    x, y, inside = pt[0], pt[1], False
    for (xa, ya), (xb, yb) in zip(poly, poly[1:] + poly[:1]):
        if (ya > y) != (yb > y) and x < xa + (y - ya) * (xb - xa) / (yb - ya):
            inside = not inside
    return inside


def level_loops(w, h, boss_c, boss_d, ell):
    """Closed loops of the ring at clearance ell. At an exact touching (circle tangent to a wall) a hair's
    difference of 1e-6 mm is tried, because two pieces then meet at one point."""
    br = boss_d / 2
    last = None
    for delta in (0.0, -1e-6, 1e-6, -1e-5):
        try:
            return chain_loops(level_pieces(w, h, boss_c, br, ell + delta))
        except ValueError as e:
            last = e
    raise last


def level_components(w, h, boss_c, boss_d, ell, point_size=0.05):
    """Separate pieces of free space at this clearance: each has one outside loop and its holes."""
    loops = level_loops(w, h, boss_c, boss_d, ell)
    samples = [sample_loop(lp) for lp in loops]
    areas = [signed_area(pt) for pt in samples]
    comps = []
    for lp, pt, ar in zip(loops, samples, areas):
        if ar > 0:
            xs, ys = [p[0] for p in pt], [p[1] for p in pt]
            comps.append({"ell": ell, "outer": lp, "poly": pt, "holes": [], "children": [],
                          "is_point": max(max(xs) - min(xs), max(ys) - min(ys)) < point_size})
    for lp, pt, ar in zip(loops, samples, areas):
        if ar <= 0:
            for c in comps:
                if point_in_polygon(pt[0], c["poly"]):
                    c["holes"].append(lp)
                    break
    return comps


# %% [markdown]
# ## Step 3: rings that split are a tree
# Compute the rings for l = r, ..., rho_max. Ring k+1 lies inside ring k, so every piece of
# ring k+1 has a **parent** piece of ring k: the one that contains it. One ring may have several
# children (the ring splits at the neck), and the last rings are single points. The result is a
# tree; walking it depth first (finish a branch before starting the next) visits every ring.
#
# For a 40 x 30 mm pocket with a 12 mm boss and a 6 mm cutter, rho_max = 7.9546 mm and the rings
# are l = 3, 5.477 and 7.9546 mm: one piece (the outside rectangle with the boss's circle as a
# hole), then two crescents (left and right of the boss), then four points (the four corners).

# %%
def build_tree(w, h, boss_c, boss_d, d, s, offs=None):
    """The rings as a tree of components. Returns (roots, levels, offsets, rho). `offs` overrides the ring schedule."""
    check_setup(w, h, boss_c, boss_d, d, s)
    rho = max_clearance(w, h, boss_c, boss_d)
    offs = level_offsets(rho, d / 2, s) if offs is None else offs
    levels = []
    for i, ell in enumerate(offs):
        e = ell - (1e-4 if abs(ell - rho) < 1e-9 else 0.0)     # a ring at the largest clearance sits just inside it
        levels.append(level_components(w, h, boss_c, boss_d, e))
    roots = levels[0]
    if len(roots) != 1:
        raise ValueError(f"the free space for the cutter centre has {len(roots)} separate parts: the cutter would have to lift between them")
    for upper, lower in zip(levels[:-1], levels[1:]):
        for c in lower:
            p0 = piece_start(c["outer"][0])
            for u in upper:
                if point_in_polygon(p0, u["poly"]) and not any(point_in_polygon(p0, sample_loop(hl)) for hl in u["holes"]):
                    u["children"].append(c)
                    break
            else:
                raise ValueError("a ring has no parent ring: the set-up is not supported")
    return roots, levels, offs, rho


# %% [markdown]
# ## Step 4: join the loops without lifting
# The cutter centre path is one chain of pieces. Inside a loop we follow its pieces. Between two
# loops we need a **link**: a straight line if it stays outside the circle of radius
# (boss radius + r) around the boss centre (the cutter would hit the boss otherwise), else a
# *tangent, arc, tangent* route: a straight line to the circle, along it, and a straight line
# off it. Both ways stay in the free space, which will be cut anyway. We enter each loop at the
# point of it nearest to where we are, by splitting the loop there.

# %%
def segs_length(segs):
    return sum(piece_length(p) for p in segs)


def _nearest_on_piece(p, q):
    """(distance, parameter t in [0, 1]) of the point of piece p nearest to q."""
    if p[0] == "L":
        ax, ay = p[1]
        bx, by = p[2]
        dx, dy = bx - ax, by - ay
        t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((q[0] - ax) * dx + (q[1] - ay) * dy) / (dx * dx + dy * dy)))
        return math.hypot(ax + t * dx - q[0], ay + t * dy - q[1]), t
    _, c, R, a0, sw = p
    ang = math.atan2(q[1] - c[1], q[0] - c[0])
    u = ((a0 - ang) % TWO_PI) / abs(sw) if sw < 0 else ((ang - a0) % TWO_PI) / abs(sw)
    if u > 1.0:                                   # the nearest point on the full circle is outside this arc: take the closer end
        cands = [0.0, 1.0]
    else:
        cands = [u]
    best = None
    for t in cands:
        a = a0 + sw * t
        dd = math.hypot(c[0] + R * math.cos(a) - q[0], c[1] + R * math.sin(a) - q[1])
        if best is None or dd < best[0]:
            best = (dd, t)
    return best


def first_nearest(items, dist, tol=1e-9):
    """The first item whose distance is within tol of the smallest (so that round-off cannot break a tie)."""
    vals = [dist(x) for x in items]
    lo = min(vals)
    return items[next(i for i, v in enumerate(vals) if v <= lo + tol)]


def _split(p, t):
    """Split a piece at parameter t: two pieces (None where one is empty)."""
    if t <= 1e-12:
        return None, p
    if t >= 1 - 1e-12:
        return p, None
    if p[0] == "L":
        m = (p[1][0] + t * (p[2][0] - p[1][0]), p[1][1] + t * (p[2][1] - p[1][1]))
        return ("L", p[1], m), ("L", m, p[2])
    _, c, R, a0, sw = p
    return ("A", c, R, a0, sw * t), ("A", c, R, a0 + sw * t, sw * (1 - t))


def enter_loop(loop, q):
    """Rotate a closed loop so that it starts at its point nearest to q. Returns (pieces, start point)."""
    best = first_nearest([(_nearest_on_piece(p, q), i) for i, p in enumerate(loop)], lambda v: v[0][0])
    (_, t), i = best
    a, b = _split(loop[i], t)
    rotated = ([b] if b else []) + loop[i + 1:] + loop[:i] + ([a] if a else [])
    return rotated, piece_start(rotated[0])


def link_route(p, q, boss_c, cut_r, w, h, r):
    """Pieces that take the cutter centre from p to q without entering the circle of radius cut_r round the boss."""
    if math.hypot(q[0] - p[0], q[1] - p[1]) < 1e-9:
        return []
    ax, ay = p
    dx, dy = q[0] - ax, q[1] - ay
    t = max(0.0, min(1.0, ((boss_c[0] - ax) * dx + (boss_c[1] - ay) * dy) / (dx * dx + dy * dy)))
    if math.hypot(ax + t * dx - boss_c[0], ay + t * dy - boss_c[1]) >= cut_r - 1e-9:
        return [("L", p, q)]
    dp, dq = math.hypot(p[0] - boss_c[0], p[1] - boss_c[1]), math.hypot(q[0] - boss_c[0], q[1] - boss_c[1])
    if dp < cut_r - 1e-6 or dq < cut_r - 1e-6:
        raise ValueError("a link starts inside the boss circle")
    ap, aq = math.atan2(p[1] - boss_c[1], p[0] - boss_c[0]), math.atan2(q[1] - boss_c[1], q[0] - boss_c[0])
    fp, fq = math.acos(min(1.0, cut_r / dp)), math.acos(min(1.0, cut_r / dq))
    best = None
    for sgn in (1.0, -1.0):                       # +1: counter-clockwise round the boss, -1: clockwise
        tp, tq = ap + sgn * fp, aq - sgn * fq
        sweep = sgn * (((tq - tp) * sgn) % TWO_PI)
        T1 = (boss_c[0] + cut_r * math.cos(tp), boss_c[1] + cut_r * math.sin(tp))
        T2 = (boss_c[0] + cut_r * math.cos(tq), boss_c[1] + cut_r * math.sin(tq))
        route = [("L", p, T1)] if math.hypot(T1[0] - p[0], T1[1] - p[1]) > 1e-9 else []
        route.append(("A", boss_c, cut_r, tp, sweep))
        if math.hypot(q[0] - T2[0], q[1] - T2[1]) > 1e-9:
            route.append(("L", T2, q))
        ok = all(clearance(x, y, w, h, boss_c, cut_r - r) >= r - 1e-6 for pc in route for x, y in sample_loop([pc], 0.1))
        if ok and (best is None or segs_length(route) < segs_length(best) - 1e-9):
            best = route
    if best is None:
        raise ValueError("no route round the boss stays inside the pocket: the cutter would have to lift")
    return best


def walk_tree(root, w, h, boss_c, boss_d, d, start):
    """Depth-first walk of the ring tree: all pieces of one unbroken cutter-centre path, starting at `start`."""
    r, cut_r = d / 2, boss_d / 2 + d / 2
    path, pos = [], start

    def go(q):
        nonlocal pos
        path.extend(link_route(pos, q, boss_c, cut_r, w, h, r))
        pos = q

    def nearest_dist(loop, q):
        return min(_nearest_on_piece(p, q)[0] for p in loop)

    def cut_loop(loop):
        nonlocal pos
        rot, st = enter_loop(loop, pos)
        go(st)
        path.extend(rot)
        pos = piece_end(rot[-1])

    def visit(c):
        nonlocal pos
        if c["is_point"]:
            xs, ys = [p[0] for p in c["poly"]], [p[1] for p in c["poly"]]
            go((0.5 * (min(xs) + max(xs)), 0.5 * (min(ys) + max(ys))))
        else:
            cut_loop(c["outer"])
            todo = list(c["holes"])
            while todo:
                nxt = first_nearest(todo, lambda lp: nearest_dist(lp, pos))
                todo.remove(nxt)
                cut_loop(nxt)
        todo = list(c["children"])
        while todo:
            nxt = first_nearest(todo, lambda ch: nearest_dist(ch["outer"], pos))
            todo.remove(nxt)
            visit(nxt)

    visit(root)
    return path


def densify(path, step=0.25):
    """Points along a chain of pieces, at most `step` mm apart."""
    pts = []
    for p in path:
        n = max(1, int(math.ceil(piece_length(p) / step)))
        if p[0] == "L":
            pts += [(p[1][0] + (p[2][0] - p[1][0]) * k / n, p[1][1] + (p[2][1] - p[1][1]) * k / n) for k in range(n)]
        else:
            pts += [(p[1][0] + p[2] * math.cos(p[3] + p[4] * k / n), p[1][1] + p[2] * math.sin(p[3] + p[4] * k / n)) for k in range(n)]
    pts.append(piece_end(path[-1]))
    return np.array(pts)


def uncovered_cells(path, w, h, boss_c, boss_d, r, res=0.25, slack=0.01):
    """Grid points of the pocket (outside the boss) farther than r from the path, apart from the unavoidable
    rounded leftovers in the four corners. Returns an array of (x, y). Each point of the path marks the grid
    points within r of it as covered."""
    xs, ys = np.arange(res / 2, w, res), np.arange(res / 2, h, res)
    X, Y = np.meshgrid(xs, ys)
    keep = np.hypot(X - boss_c[0], Y - boss_c[1]) >= boss_d / 2
    for cx, sx in ((0.0, 1.0), (w, -1.0)):
        for cy, sy in ((0.0, 1.0), (h, -1.0)):
            corner = (np.abs(X - cx) < r) & (np.abs(Y - cy) < r) & (np.hypot(X - (cx + sx * r), Y - (cy + sy * r)) > r)
            keep &= ~corner
    covered = np.zeros(X.shape, dtype=bool)
    R = r + slack
    for x, y in densify(path, res):
        i0, i1 = max(0, int((x - R - res / 2) / res)), min(len(xs), int((x + R - res / 2) / res) + 2)
        j0, j1 = max(0, int((y - R - res / 2) / res)), min(len(ys), int((y + R - res / 2) / res) + 2)
        covered[j0:j1, i0:i1] |= (X[j0:j1, i0:i1] - x) ** 2 + (Y[j0:j1, i0:i1] - y) ** 2 <= R * R
    bad = keep & ~covered
    return np.stack([X[bad], Y[bad]], axis=1)


def plan_pocket(w, h, boss_c, boss_d, d, s, refine=True):
    """The unbroken cutter-centre path of one layer, with the rings it is made of.
    With refine=True, rings are added where the check finds points farther than r from the path."""
    check_setup(w, h, boss_c, boss_d, d, s)
    r = d / 2
    rho = max_clearance(w, h, boss_c, boss_d)
    offs = level_offsets(rho, r, s)
    added = []
    for _ in range(12):
        roots, levels, offs, rho = build_tree(w, h, boss_c, boss_d, d, s, offs)
        path = walk_tree(roots[0], w, h, boss_c, boss_d, d, (r, r))
        bad = uncovered_cells(path, w, h, boss_c, boss_d, r) if refine else []
        if len(bad) == 0:
            break
        phi = np.array([clearance(x, y, w, h, boss_c, boss_d / 2) for x, y in bad])
        new = max(r, float(phi.max()) - 0.3 * r)            # a ring a little below the worst point passes close to it
        if any(abs(new - o) < 0.05 for o in offs):
            new = float(phi.max()) - 0.6 * r
        offs = sorted(offs + [min(new, rho - 1e-3)])
        added.append(offs[-1] if False else new)
    return {"path": path, "levels": levels, "offsets": offs, "rho": rho, "length": segs_length(path), "added": added,
            "uncovered": len(bad)}


def path_points(path, step=0.05):
    """Sampled points of a piece chain (for plots and clearance checks)."""
    return sample_loop(path, step) + [piece_end(path[-1])]


# %% [markdown]
# ## Step 5: G-code with arcs, the simulation and the comparison
# Per layer: rapid to the start, plunge once, follow the chain (G1 for lines, G2 for the
# clockwise arcs), lift. The program is parsed back, timed and run through the height-map.

# %%
def contour_gcode(w, h, depth, d, doc, s, feed, plunge, boss_c, boss_d, lift=1.0):
    plan = plan_pocket(w, h, boss_c, boss_d, d, s)
    path = plan["path"]
    layers = math.ceil(depth / doc - 1e-9)
    dz = depth / layers
    f = lambda v: f"{v:.3f}".rstrip("0").rstrip(".") if abs(v) > 5e-4 else "0"
    x0, y0 = piece_start(path[0])
    out = ["G21", "G90", f"G0 Z{f(lift)}"]
    for k in range(1, layers + 1):
        out += [f"G0 X{f(x0)} Y{f(y0)}", f"G1 Z{f(-k * dz)} F{f(plunge)}"]
        first = True
        for p in path:
            ex, ey = piece_end(p)
            if p[0] == "L":
                out.append(f"G1 X{f(ex)} Y{f(ey)}" + (f" F{f(feed)}" if first else ""))
            else:
                sx, sy = piece_start(p)
                if abs(p[4]) > TWO_PI - 1e-9:
                    ex, ey = sx, sy
                code = "G2" if p[4] < 0 else "G3"          # clockwise arcs follow the ring, counter-clockwise ones are links
                out.append(f"{code} X{f(ex)} Y{f(ey)} I{f(p[1][0] - sx)} J{f(p[1][1] - sy)}" + (f" F{f(feed)}" if first else ""))
            first = False
        out.append(f"G0 Z{f(lift)}")
    out.append("G0 Z5")
    return "\n".join(out) + "\n"


def simulate_contour(w, h, depth, d, doc, s, feed, plunge, boss_c, boss_d, res=0.1):
    """Generate, parse and simulate the program: (height-map, parsed moves, G-code text)."""
    hm = HeightMap(0, w, 0, h, res)
    text = contour_gcode(w, h, depth, d, doc, s, feed, plunge, boss_c, boss_d)
    mv = read_moves(text)
    simulate_moves(hm, mv, d / 2.0)
    return hm, mv, text


def boss_expected_volume_at(w, h, depth, d, boss_d):
    """Same target as Session 3 (boss_expected_volume), for any pocket size."""
    return boss_expected_volume(w, h, depth, d, boss_d)


def boss_intrusion_area(hm, boss_c, boss_d):
    """Area (mm^2) of cut cells whose centre lies inside the boss."""
    X, Y = np.meshgrid(hm.xc, hm.yc)
    inside = np.hypot(X - boss_c[0], Y - boss_c[1]) < boss_d / 2
    return float(((hm.h < -1e-9) & inside).sum() * hm.res ** 2)


def count_lifts(moves):
    """Moves that rise in z (a retract), and rapid moves in x and y."""
    ups = sum(1 for m in moves if m["b"][2] > m["a"][2] + 1e-9)
    rapid_xy = sum(1 for m in moves if m["kind"] == "G0" and (m["b"][0], m["b"][1]) != (m["a"][0], m["a"][1]))
    return ups, rapid_xy


# %% [markdown]
# ## Step 6: failure cases
# * a boss that touches or crosses a wall, or lies outside the pocket: refused;
# * a stepover larger than the cutter diameter: refused (strips would be left);
# * a cutter that does not fit anywhere (radius above the largest clearance): refused;
# * a boss so big that the cutter cannot pass between it and a wall: the free space has two
#   parts (left and right of a 20 mm boss in a 30 mm pocket with a 6 mm cutter), and a path
#   without a lift does not exist: refused. The fix is a lift between the two parts.

# %%
BOSS_TOO_BIG = (40.0, 30.0, (20.0, 15.0), 20.0, 6.0, 4.0)      # gaps of 5 mm above and below: the cutter cannot pass


# %% [markdown]
# ## Step 7: see it

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    BLUE, ORANGE, MAGENTA, GREY = "#0072b2", "#c86a00", "#d81b60", "#555555"
    W, H, D, S, DEPTH, DOC, FEED, PLUNGE = 40.0, 30.0, 6.0, 4.0, 5.0, 2.0, 300.0, 100.0
    C, BD = (20.0, 15.0), 12.0
    rho = max_clearance(W, H, C, BD)
    plan = plan_pocket(W, H, C, BD, D, S)
    print(f"largest clearance {rho:.4f} mm; rings at {[round(v, 3) for v in plan['offsets']]}; one-layer path {plan['length']:.1f} mm")
    base_text = boss_pocket_gcode(W, H, DEPTH, D, DOC, S, FEED, PLUNGE, C, BD)
    base_mv = read_moves(base_text)
    hm0 = HeightMap(0, W, 0, H, 0.1)
    simulate_moves(hm0, base_mv, D / 2)
    hm, mv, text = simulate_contour(W, H, DEPTH, D, DOC, S, FEED, PLUNGE, C, BD)
    exp = boss_expected_volume(W, H, DEPTH, D, BD)
    cut = lambda m_: [m for m in m_ if m["kind"] != "G0"]
    t0, t1 = gcode_time_s(cut(base_mv)), gcode_time_s(cut(mv))
    print(f"raster program: {len(base_text.splitlines())} lines, {count_lifts(base_mv)[0]} lifts, cutting time {t0:.1f} s, volume {hm0.removed_volume():.1f} mm^3")
    print(f"contour program: {len(text.splitlines())} lines, {count_lifts(mv)[0]} lifts, cutting time {t1:.1f} s, volume {hm.removed_volume():.1f} mm^3 (target {exp:.1f}, {100 * (hm.removed_volume() / exp - 1):+.3f} %)")

    # Figure 1: the clearance field and the path
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.4))
    ax = axs[0]
    gx, gy = np.meshgrid(np.linspace(0, W, 400), np.linspace(0, H, 300))
    phi = np.minimum.reduce([gx, W - gx, gy, H - gy, np.hypot(gx - C[0], gy - C[1]) - BD / 2])
    phi[np.hypot(gx - C[0], gy - C[1]) < BD / 2] = np.nan
    im = ax.imshow(phi, origin="lower", extent=(0, W, 0, H), cmap="Blues")
    fig.colorbar(im, ax=ax, label="clearance (mm)", fraction=0.046)
    ax.contour(gx, gy, np.nan_to_num(phi, nan=0.0), levels=plan["offsets"], colors=[ORANGE], linewidths=1.4)
    ax.add_patch(plt.Circle(C, BD / 2, fill=False, color=GREY))
    ax.set_aspect("equal"); ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)")
    ax.set_title("Clearance field; orange rings at " + ", ".join(f"{v:.1f}" for v in plan["offsets"]) + " mm", fontsize=9)
    ax = axs[1]
    pts = densify(plan["path"], 0.1)
    ax.plot(pts[:, 0], pts[:, 1], "-", color=BLUE, lw=1.2)
    ax.plot(*pts[0], "o", color=ORANGE, ms=7, label="plunge point")
    ax.add_patch(plt.Circle(C, BD / 2, fill=True, color="#dddddd"))
    ax.plot([0, W, W, 0, 0], [0, 0, H, H, 0], color=GREY)
    ax.set_aspect("equal"); ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)"); ax.legend(fontsize=8, loc="upper right")
    ax.set_title(f"One unbroken cutter-centre path: {plan['length']:.0f} mm per layer", fontsize=9)
    fig.tight_layout(); fig.savefig(OUT / "clearance_and_path.png", dpi=120, bbox_inches="tight")

    # Figure 2: raster with lifts against contour
    fig2, axs2 = plt.subplots(1, 2, figsize=(11, 4.4))
    ax = axs2[0]
    first = True
    for m in base_mv:
        if m["a"][2] == m["b"][2] and m["kind"] != "G0":
            q = move_points(m, 0.1)
            ax.plot(q[:, 0], q[:, 1], "-", color=BLUE, lw=1)
        elif m["kind"] == "G0" and (m["a"][0], m["a"][1]) != (m["b"][0], m["b"][1]) and m["a"][2] > 0.5:
            ax.plot([m["a"][0], m["b"][0]], [m["a"][1], m["b"][1]], "--", color=MAGENTA, lw=0.8, label="rapid move with the cutter lifted" if first else None)
            first = False
    ax.add_patch(plt.Circle(C, BD / 2, fill=True, color="#dddddd"))
    ax.set_aspect("equal"); ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)"); ax.legend(fontsize=8, loc="upper right")
    ax.set_title(f"Session 3 raster: {count_lifts(base_mv)[0] // 3} lifts per layer, {t0:.0f} s", fontsize=9)
    ax = axs2[1]
    bars = ax.bar(["raster (Session 3)", "contour (today)"], [t0, t1], color=[MAGENTA, BLUE])
    ax.axhline(200, color=GREY, ls="--"); ax.text(1.45, 203, "target 200 s", ha="right", fontsize=8)
    for b_, v in zip(bars, (t0, t1)):
        ax.text(b_.get_x() + b_.get_width() / 2, v + 4, f"{v:.1f} s", ha="center", fontsize=9)
    ax.set_ylabel("cutting time (s)"); ax.set_ylim(0, 360); ax.grid(alpha=0.3, axis="y")
    ax.set_title("Same pocket, same volume, 43 % less time", fontsize=9)
    fig2.tight_layout(); fig2.savefig(OUT / "raster_vs_contour.png", dpi=120, bbox_inches="tight")

    # Figure 3: the strips that "spacing at most the stepover" leaves where rings split
    W2, H2, C2, BD2 = 60.0, 40.0, (30.0, 20.0), 14.0
    fig3, axs3 = plt.subplots(1, 2, figsize=(11, 4.0))
    for ax, ref, ttl in ((axs3[0], False, "rings every 4 mm only"), (axs3[1], True, "plus rings where the check finds a gap")):
        pl = plan_pocket(W2, H2, C2, BD2, D, S, refine=ref)
        bad = uncovered_cells(pl["path"], W2, H2, C2, BD2, D / 2)
        q = densify(pl["path"], 0.1)
        ax.plot(q[:, 0], q[:, 1], "-", color=BLUE, lw=0.8)
        ax.add_patch(plt.Circle(C2, BD2 / 2, fill=True, color="#dddddd"))
        if len(bad):
            ax.plot(bad[:, 0], bad[:, 1], "s", color=MAGENTA, ms=3, label=f"uncut: {len(bad) * 0.0625:.1f} mm^2")
            ax.legend(fontsize=8, loc="upper right")
        ax.set_aspect("equal"); ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)")
        ax.set_title(f"60 x 40 pocket, 14 mm boss: {ttl} ({len(pl['offsets'])} rings)", fontsize=9)
    fig3.tight_layout(); fig3.savefig(OUT / "gap_at_split.png", dpi=120, bbox_inches="tight")

    # Figure 4: simulated height-map
    fig4, ax4 = plt.subplots(figsize=(6.2, 4.4))
    im = ax4.imshow(hm.h, origin="lower", extent=(0, W, 0, H), cmap="viridis")
    fig4.colorbar(im, ax=ax4, label="material height (mm)", fraction=0.046)
    ax4.set_xlabel("x (mm)"); ax4.set_ylabel("y (mm)")
    ax4.set_title(f"Simulated: {hm.removed_volume():.0f} mm^3 removed (target {exp:.0f})", fontsize=9)
    fig4.tight_layout(); fig4.savefig(OUT / "boss_contour_simulated.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.

