"""Session 2 (Level 2): G-code, offset curves, arcs and machining time.

Educational toolpath geometry only. Real machining needs trained operators,
machine-specific post-processing and safety checks.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: G-code, offsets, arcs and time
# **A. Real-world problem.** A CNC controller reads text lines such as `G1 X10 Y5 F300`.
# Can you write that text yourself, read it back, and predict how long a 40 x 30 mm pocket,
# 5 mm deep, takes with a 6 mm cutter?
#
# **Plan.** (1) write G0/G1 lines, (2) parse them back, (3) offset an outline by the cutter
# radius, (4) add arcs G2/G3, (5) plan a pocket and estimate its time.

# %%
import math
import pathlib
import re

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: write G-code words
# A G-code line is a list of *words*: a letter and a number. `G0` = rapid move (fast, not
# cutting), `G1` = straight cutting move, `X Y Z` = target coordinates in mm, `F` = feed in
# mm/min. We assume millimetres (G21) and absolute coordinates (G90).

# %%
def num(v):
    """Format a number for G-code: at most 3 decimals, no trailing zeros."""
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class Program:
    """A tiny G-code writer. The text lives in self.lines."""

    def __init__(self):
        self.lines = ["G21 (millimetres)", "G90 (absolute coordinates)"]

    def rapid(self, x=None, y=None, z=None):
        self.lines.append("G0" + self._xyz(x, y, z))

    def cut(self, x=None, y=None, z=None, f=None):
        self.lines.append("G1" + self._xyz(x, y, z) + (f" F{num(f)}" if f is not None else ""))

    def arc(self, ccw, x, y, i, j, f=None):
        """G3 (counter-clockwise) or G2 (clockwise) arc to (x, y); (i, j) = centre minus start."""
        self.lines.append(("G3" if ccw else "G2") + f" X{num(x)} Y{num(y)} I{num(i)} J{num(j)}"
                          + (f" F{num(f)}" if f is not None else ""))

    @staticmethod
    def _xyz(x, y, z):
        return "".join(f" {k}{num(v)}" for k, v in (("X", x), ("Y", y), ("Z", z)) if v is not None)

    def text(self):
        return "\n".join(self.lines) + "\n"


# %% [markdown]
# ## Step 2: parse your own G-code back
# Reading the text back and rebuilding the geometry is how you *verify* a program. Words are
# modal: a missing X, Y, Z keeps its last value, and G and F stay active until changed.

# %%
WORD = re.compile(r"([A-Z])\s*(-?\d+\.?\d*|-?\.\d+)")


def parse_gcode(text):
    """Return a list of moves {kind, p0, p1, f, ij}. kind is G0, G1, G2 or G3."""
    pos, kind, feed, moves = [0.0, 0.0, 0.0], None, None, []
    for raw in text.splitlines():
        line = re.sub(r"\(.*?\)|;.*", "", raw).upper()
        words = {m.group(1): float(m.group(2)) for m in WORD.finditer(line)}
        g = words.get("G")
        if g in (0, 1, 2, 3):
            kind = f"G{int(g)}"
        if "F" in words:
            feed = words["F"]
        if not any(k in words for k in "XYZ"):
            continue
        new = [words.get("X", pos[0]), words.get("Y", pos[1]), words.get("Z", pos[2])]
        moves.append({"kind": kind, "p0": tuple(pos), "p1": tuple(new), "f": feed,
                      "ij": (words.get("I", 0.0), words.get("J", 0.0))})
        pos = new
    return moves


# %% [markdown]
# ## Step 3: lengths, arcs and time
# A line has length |p1 - p0|. An arc with centre c has radius r = |p0 - c| and, if it is
# correct, also |p1 - c| = r. Its length is r times the swept angle (radians).
# Machining time = length / feed (mm divided by mm/min gives minutes).

# %%
def arc_geometry(move):
    """(centre, radius, sweep in radians) of a G2/G3 move; a full circle sweeps 2 pi."""
    x0, y0, _ = move["p0"]
    x1, y1, _ = move["p1"]
    cx, cy = x0 + move["ij"][0], y0 + move["ij"][1]
    a0, a1 = math.atan2(y0 - cy, x0 - cx), math.atan2(y1 - cy, x1 - cx)
    sweep = (a1 - a0) % (2 * math.pi) if move["kind"] == "G3" else (a0 - a1) % (2 * math.pi)
    if sweep < 1e-12 and abs(x1 - x0) + abs(y1 - y0) < 1e-12:
        sweep = 2 * math.pi
    return (cx, cy), math.hypot(x0 - cx, y0 - cy), sweep


def arc_end_radius_error(move):
    """|end radius - start radius| of an arc: a valid arc has 0 (mm)."""
    (cx, cy), r, _ = arc_geometry(move)
    return abs(math.hypot(move["p1"][0] - cx, move["p1"][1] - cy) - r)


def move_length(move):
    if move["kind"] in ("G2", "G3"):
        _, r, sweep = arc_geometry(move)
        return math.hypot(r * sweep, move["p1"][2] - move["p0"][2])
    return float(np.linalg.norm(np.subtract(move["p1"], move["p0"])))


def program_time_s(moves, rapid_rate=3000.0):
    """Seconds: cutting moves at their F, rapids at an assumed rapid rate (mm/min)."""
    t = 0.0
    for m in moves:
        rate = rapid_rate if m["kind"] == "G0" else m["f"]
        t += move_length(m) / rate * 60.0
    return t


def sample_xy(moves, step=0.25):
    """Points along the XY projection of the cutting moves (for geometry checks)."""
    pts = []
    for m in moves:
        if m["kind"] == "G0":
            continue
        n = max(2, int(move_length(m) / step) + 2)
        t = np.linspace(0.0, 1.0, n)
        if m["kind"] == "G1":
            a, b = np.array(m["p0"][:2]), np.array(m["p1"][:2])
            pts.extend(a + tt * (b - a) for tt in t)
        else:
            (cx, cy), r, sweep = arc_geometry(m)
            a0 = math.atan2(m["p0"][1] - cy, m["p0"][0] - cx)
            sgn = 1.0 if m["kind"] == "G3" else -1.0
            pts.extend((cx + r * math.cos(a0 + sgn * sweep * tt),
                        cy + r * math.sin(a0 + sgn * sweep * tt)) for tt in t)
    return np.array(pts)


# %% [markdown]
# ## Step 4: the toolpath is an offset curve
# The part outline is where the cutter *edge* must go; the centre must be r away from it.
# Pocket (cut inside the outline): shrink a w x h rectangle by r on every side.
# Profile (cut around a part): grow it by r; the corners become arcs of radius r.

# %%
def offset_rect(w, h, r, inside=True):
    """Corners (x0, y0, x1, y1) of the centre path for the rectangle [0, w] x [0, h].
    Returns None if an inside offset would make a side negative (cutter too big)."""
    if inside:
        if 2 * r > min(w, h) + 1e-12:
            return None
        return (r, r, w - r, h - r)
    return (-r, -r, w + r, h + r)


def dist_to_rect_outline(pt, w, h):
    """Distance from a point to the closed boundary of the rectangle [0, w] x [0, h]."""
    x, y = pt
    dx, dy = max(-x, 0.0, x - w), max(-y, 0.0, y - h)
    if dx > 0 or dy > 0:
        return math.hypot(dx, dy)
    return min(x, w - x, y, h - y)


def profile_gcode(w, h, r, z, f):
    """G-code that goes round the OUTSIDE of the rectangle with a cutter of radius r (CCW)."""
    p = Program()
    p.rapid(0, -r, 5)
    p.cut(z=z, f=f)
    p.cut(w, -r, f=f)
    p.arc(True, w + r, 0, 0, r)
    p.cut(w + r, h)
    p.arc(True, w, h + r, -r, 0)
    p.cut(0, h + r)
    p.arc(True, -r, h, 0, -r)
    p.cut(-r, 0)
    p.arc(True, 0, -r, r, 0)
    p.rapid(z=5)
    return p.text()


# %% [markdown]
# ## Step 5: plan a rectangular pocket
# The centre must cover a (w - D) x (h - D) rectangle. Raster (zigzag) lines run along x,
# spaced by at most the stepover s. Number of lines n = ceil(span / s) + 1, spaced evenly.
# Layers = ceil(depth / depth_of_cut).

# %%
def plan_pocket(w, h, depth, d, doc, stepover, feed, plunge_feed=100.0):
    """Plan a raster pocket. Raises ValueError if the cutter does not fit."""
    if d > min(w, h) + 1e-12:
        raise ValueError(f"cutter diameter {d:g} mm does not fit a {w:g} x {h:g} mm pocket")
    if stepover > d + 1e-12:
        raise ValueError("stepover larger than the cutter diameter leaves uncut strips")
    span_y, line_len = h - d, w - d
    n_lines = math.ceil(span_y / stepover - 1e-9) + 1
    s_act = span_y / (n_lines - 1) if n_lines > 1 else 0.0
    layers = math.ceil(depth / doc - 1e-9)
    per_layer = n_lines * line_len + span_y
    cut_len = layers * per_layer
    plunge_len = depth + 0.5          # the first plunge also covers 0.5 mm of air above the stock
    time_s = cut_len / feed * 60 + plunge_len / plunge_feed * 60
    return {"r": d / 2, "n_lines": n_lines, "stepover_actual": s_act, "layers": layers,
            "dz": depth / layers, "per_layer": per_layer, "cut_len": cut_len,
            "plunge_len": plunge_len, "time_s": time_s}


def pocket_gcode(w, h, depth, d, doc, stepover, feed, plunge_feed=100.0):
    """Raster pocket G-code. Pocket corner at (0, 0), stock top at Z = 0, floor at Z = -depth."""
    pl = plan_pocket(w, h, depth, d, doc, stepover, feed, plunge_feed)
    r, p = pl["r"], Program()
    p.rapid(z=5)
    p.rapid(r, r)
    p.rapid(z=0.5)
    for k in range(1, pl["layers"] + 1):
        if k > 1:
            p.rapid(r, r)
        p.cut(z=-k * pl["dz"], f=plunge_feed)
        for j in range(pl["n_lines"]):
            if j > 0:
                p.cut(y=r + j * pl["stepover_actual"], f=feed)
            p.cut(x=(w - r) if j % 2 == 0 else r, f=feed)
    p.rapid(z=5)
    return p.text()


# %% [markdown]
# ## Step 6: see it

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    w, h, r = 40.0, 30.0, 3.0
    print("inside offset  :", offset_rect(w, h, r, True))
    print("outside offset :", offset_rect(w, h, r, False))
    prof = parse_gcode(profile_gcode(w, h, r, -2, 200))
    print(f"profile path length = {sum(move_length(m) for m in prof if m['kind'] != 'G0'):.2f} mm")
    pl = plan_pocket(40, 30, 5, 6, 2, 4.5, 300)
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in pl.items()})
    prog = pocket_gcode(40, 30, 5, 6, 2, 4.5, 300)
    print(prog.splitlines()[:12])
    print(f"parsed time = {program_time_s(parse_gcode(prog)):.1f} s")

    fig, axs = plt.subplots(1, 2, figsize=(10, 4.6))
    ax = axs[0]
    ax.add_patch(plt.Rectangle((0, 0), w, h, fill=False, ec="k", lw=2, label="part outline"))
    ax.plot(*sample_xy(prof).T, "C0-", lw=1.5, label="outside centre path (lines + arcs)")
    x0, y0, x1, y1 = offset_rect(w, h, r, True)
    ax.plot([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0], "C3--", lw=1.5, label="inside centre path (pocket)")
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title("Toolpath = outline offset by the cutter radius (3 mm)")
    ax.legend(fontsize=7, loc="upper right")
    ax.grid(alpha=0.3)
    ax = axs[1]
    first = [m for m in parse_gcode(prog) if m["kind"] == "G1" and m["p0"][2] == m["p1"][2] == -pl["dz"]]
    ax.add_patch(plt.Rectangle((0, 0), 40, 30, fill=False, ec="k", lw=2))
    ax.plot(*sample_xy(first).T, "C0-", lw=1)
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title("First layer of the 40 x 30 mm pocket: 7 lines")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "offsets_and_pocket.png", dpi=120)

    ss = np.linspace(1.0, 6.0, 51)
    ts = [plan_pocket(40, 30, 5, 6, 2, s, 300)["time_s"] for s in ss]
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(ss, ts)
    ax2.set_xlabel("stepover (mm)")
    ax2.set_ylabel("machining time (s)")
    ax2.set_title("Pocket time against stepover (F = 300 mm/min)")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "time_vs_stepover.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
