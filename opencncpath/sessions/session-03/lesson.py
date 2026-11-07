"""Session 3 (Level 3): pocketing strategies, scallops and a height-map simulation.

Educational toolpath geometry only. Real machining needs trained operators,
machine-specific post-processing and safety checks. Feeds and speeds here are
teaching numbers, not recommended cutting conditions.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: simulate the removed material and check it
# **A. Real-world problem.** A toolpath that looks right can still leave material behind,
# cut too much, or take twice as long as it should. We simulate the cutter on a grid of
# heights (a *height-map*) and compare the removed volume and the leftover ridges with formulas.
#
# **Plan.** (1) a height-map and a cutter stamp, (2) raster and contour-parallel paths,
# (3) scallop height for a ball-end cutter, (4) MRR and chip load, (5) corners, gouges and
# cutters that do not fit, (6) a pocket with a round boss, from G-code to volume check.

# %%
import math
import pathlib
import re

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: a height-map and a cutter stamp
# The stock is a grid of cells; each stores the height of the material top (0 = original top,
# -5 = 5 mm down). A flat-end cutter at (x, y) with tip height z sets every cell within its
# radius to at most z. A ball-end cutter of radius r leaves a rounded surface:
# height = z + r - sqrt(r^2 - rho^2) at distance rho from the axis.

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


# %% [markdown]
# ## Step 2: two pocketing strategies
# *Raster (zigzag)*: parallel lines spaced by the stepover s. *Contour-parallel*: the pocket
# outline offset inwards by r, then by r + s, r + 2s, ... until nothing is left (rings, like a
# spiral). Both keep the cutter centre inside the (w - D) x (h - D) rectangle.

# %%
def n_lines(span, s):
    """Lines needed to cover a span with spacing at most s (end lines included)."""
    return math.ceil(span / s - 1e-9) + 1


def raster_path(w, h, d, s):
    """Zigzag centre path for a w x h rectangular pocket and cutter diameter d."""
    r, n = d / 2, n_lines(h - d, s)
    ys = np.linspace(r, h - r, n)
    pts = []
    for j, y in enumerate(ys):
        a, b = (r, w - r) if j % 2 == 0 else (w - r, r)
        pts += [(a, y), (b, y)]
    return np.array(pts)


def contour_path(w, h, d, s):
    """Rings of inward rectangle offsets (first ring at the cutter radius), joined into one path."""
    r, pts, k = d / 2, [], 0
    while True:
        x0, y0, x1, y1 = r + k * s, r + k * s, w - r - k * s, h - r - k * s
        if x1 - x0 < -1e-9 or y1 - y0 < -1e-9:
            break
        if y1 - y0 < 1e-9:
            pts += [(x0, y0), (x1, y0)]
        elif x1 - x0 < 1e-9:
            pts += [(x0, y0), (x0, y1)]
        else:
            pts += [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
        k += 1
    return np.array(pts)


def path_length(pts):
    return float(np.hypot(*np.diff(np.asarray(pts, dtype=float), axis=0).T).sum())


# %% [markdown]
# ## Step 3: ridges (scallops) left by a ball-end cutter
# Neighbouring passes s apart leave a ridge midway. The ball surface at horizontal distance
# s/2 from its axis is r - sqrt(r^2 - (s/2)^2) above the tip, so the ridge height is
# h = r - sqrt(r^2 - (s/2)^2). Inverse: s = 2 sqrt(2 r h - h^2).

# %%
def cusp_height(r, s):
    half = min(s / 2.0, r)
    return r - math.sqrt(r * r - half * half)


def stepover_for_cusp(r, h):
    return 2.0 * math.sqrt(2.0 * r * h - h * h)


def simulate_cusp(r, s, n_pass=5, res=0.025, length=12.0):
    """Measured ridge height between the middle passes of n_pass parallel ball-end passes."""
    ymid = (n_pass - 1) * s / 2.0
    hm = HeightMap(0.0, length, -res / 2 - 0.5 * s, (n_pass - 1) * s + 0.5 * s, res)
    tip = -1.0
    for k in range(n_pass):
        hm.cut_polyline([(-r, k * s), (length + r, k * s)], tip, r, ball=True)
    rows = (hm.yc > ymid + 1e-9) & (hm.yc < ymid + s - 1e-9)      # between passes 3 and 4
    cols = (hm.xc > r) & (hm.xc < length - r)
    return float(hm.h[np.ix_(rows, cols)].max() - tip)


# %% [markdown]
# ## Step 4: material removal rate and chip load
# MRR = width of cut * depth of cut * feed (mm^3/min). Chip load (feed per tooth)
# f_z = F / (N z) with spindle speed N (rev/min) and z teeth.

# %%
def mrr(ae, ap, feed):
    """Material removal rate, mm^3/min (ae = radial width, ap = axial depth, mm)."""
    return ae * ap * feed


def chip_load(feed, rpm, teeth):
    """Feed per tooth in mm."""
    return feed / (rpm * teeth)


def line_cut_volume(r, ap, length, res=0.05):
    """Simulated volume of a single straight flat-end cut of the given length."""
    hm = HeightMap(-r - 1, length + r + 1, -r - 1, r + 1, res)
    hm.cut_polyline([(0.0, 0.0), (length, 0.0)], -ap, r)
    return hm.removed_volume()


# %% [markdown]
# ## Step 5: corners, leftovers, wrong offsets and cutters that do not fit
# A round cutter cannot reach into a sharp inside corner: each corner keeps
# r^2 (1 - pi/4) of leftover area. A stepover larger than the cutter diameter leaves strips.
# An offset in the wrong direction gouges the walls. A slot narrower than the cutter cannot
# be cut at all; the planner must say so.

# %%
def corner_leftover(r):
    """Total leftover area (mm^2) in the four inside corners of a rectangular pocket."""
    return 4 * r * r * (1 - math.pi / 4)


def pocket_cleared_area(path, w, h, r, res=0.1, margin=0.0):
    """Simulate a flat cutter along path; return (cleared area, area cut outside the pocket)."""
    hm = HeightMap(-margin, w + margin, -margin, h + margin, res)
    hm.cut_polyline(path, -1.0, r)
    cut = hm.h < -1e-9
    inside = (hm.xc[None, :] >= 0) & (hm.xc[None, :] <= w) & (hm.yc[:, None] >= 0) & (hm.yc[:, None] <= h)
    return float((cut & inside).sum() * res ** 2), float((cut & ~inside).sum() * res ** 2)


def wrong_offset_gouge_area(w, h, r):
    """Analytic area cut outside the pocket when the centre path is OFFSET OUTWARDS by r."""
    return (w + 4 * r) * (h + 4 * r) - (4 - math.pi) * r * r - w * h


def plan_slot(length, width, d):
    """Centre line of a straight slot, or a clear message if the cutter is too big."""
    if d > width + 1e-12:
        return None, f"cutter diameter {d:g} mm is wider than the {width:g} mm slot: cannot cut"
    r = d / 2
    return [(r, width / 2), (length - r, width / 2)], "ok"


def check_inside_corner(corner_radius, d):
    """An inside corner cannot be sharper than the cutter radius."""
    if corner_radius + 1e-12 < d / 2:
        return f"corner radius {corner_radius:g} mm is smaller than the cutter radius {d / 2:g} mm: leftover remains"
    return "ok"


# %% [markdown]
# ## Step 6: G-code for a pocket with a round boss, then simulate that G-code
# Rows are split where the cutter centre would enter a circle of radius (boss radius + r); the
# cutter lifts over the boss. A full circle G3 trims around it and a wall lap finishes the outline. We parse the text back
# and cut the height-map from the parsed moves.

# %%
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
# ## Step 7: see it

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    W, H, D = 40.0, 30.0, 6.0
    for name, path in (("raster s=4", raster_path(W, H, D, 4)), ("contour s=4", contour_path(W, H, D, 4))):
        cl, out = pocket_cleared_area(path, W, H, D / 2)
        print(f"{name}: length {path_length(path):.1f} mm, cleared {cl:.1f} of {W * H:g} mm^2")
    for s in (1, 2, 3, 4):
        print(f"ball r=3, s={s}: formula {cusp_height(3, s):.4f} mm, simulated {simulate_cusp(3, s):.4f} mm")
    prog = boss_pocket_gcode(W, H, 5, D, 2, 4, 300, 100, (20, 15), 12)
    mv = read_moves(prog)
    hm = HeightMap(0, W, 0, H, 0.1)
    simulate_moves(hm, mv, D / 2)
    exp = boss_expected_volume(W, H, 5, D, 12)
    print(f"boss pocket: simulated {hm.removed_volume():.0f} mm^3, expected {exp:.0f} mm^3, time {gcode_time_s(mv):.0f} s")

    fig, axs = plt.subplots(1, 3, figsize=(13, 4.4))
    ax = axs[0]
    im = ax.imshow(hm.h, origin="lower", extent=(0, W, 0, H), cmap="viridis")
    fig.colorbar(im, ax=ax, label="material height (mm)", fraction=0.046)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title("Simulated pocket with a 12 mm boss")
    ss = np.linspace(1.0, 6.0, 51)
    ax = axs[1]
    ax.plot(ss, [path_length(raster_path(W, H, D, s)) / 300 * 60 for s in ss], label="raster")
    ax.plot(ss, [path_length(contour_path(W, H, D, s)) / 300 * 60 for s in ss], label="contour-parallel")
    ax.set_xlabel("stepover (mm)")
    ax.set_ylabel("one-layer cutting time (s) at 300 mm/min")
    ax.set_title("Bigger stepover, shorter time")
    ax.legend()
    ax.grid(alpha=0.3)
    ax = axs[2]
    rs = np.linspace(0.5, 5, 40)
    ax.plot(rs, [corner_leftover(r) for r in rs], label="formula 4 r^2 (1 - pi/4)")
    ax.set_xlabel("cutter radius (mm)")
    ax.set_ylabel("leftover in four corners (mm^2)")
    ax.set_title("Inside corners: bigger cutter, more left")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "boss_and_tradeoffs.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ss = np.linspace(0.2, 4.0, 60)
    ax2.plot(ss, [cusp_height(3, s) for s in ss], label="formula, r = 3 mm")
    ax2.plot([1, 2, 3, 4], [simulate_cusp(3, s) for s in (1, 2, 3, 4)], "o", label="height-map simulation")
    ax2.set_xlabel("stepover (mm)")
    ax2.set_ylabel("ridge height (mm)")
    ax2.set_title("Ball-end ridge height against stepover")
    ax2.legend()
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "cusp_height.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
