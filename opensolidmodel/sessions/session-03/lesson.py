"""Session 3 (Level 3): a sketch constraint solver: dimensions in, consistent corner points out.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: how a CAD sketch keeps its corners where you told it
# **A. Real-world problem.** In a CAD sketch you do not type coordinates. You say "this line is horizontal, this
# one is 40 mm long, these two are perpendicular", and the program finds the corner points. When you change
# 40 to 60, the points move and the sketch stays consistent. How can a program find the points from such statements,
# know whether you have said enough, and notice when two statements contradict each other?
#
# Educational model: points in a plane and five kinds of constraint, solved with Newton's method.
# Not a CAD program; the sketch must have at most a few dozen points.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
RHO = 7850.0   # density of steel (kg/m^3)


# %% [markdown]
# ## Step 1: every constraint is an equation that must be zero
# The unknowns are all the coordinates x_0, y_0, x_1, y_1, ... Each constraint gives one or two residuals, numbers
# that are zero when the statement is true:
#
#     ("fix", i, X, Y)     point i is at (X, Y)             x_i - X,  y_i - Y
#     ("dist", i, j, d)    points i and j are d apart       |p_j - p_i| - d
#     ("horiz", i, j)      the line i-j is horizontal       y_j - y_i
#     ("vert", i, j)       the line i-j is vertical         x_j - x_i
#     ("perp", i, j, k)    the angle i-j-k is 90 degrees    (p_i - p_j) . (p_k - p_j)
#
# We also need the Jacobian: the table of how each residual changes when each coordinate changes.

# %%
def system(x, constraints):
    """Return the residual vector r and the Jacobian J of all constraints at the coordinates x."""
    n2 = len(x)
    res, rows = [], []

    def row():
        return np.zeros(n2)

    for c in constraints:
        kind = c[0]
        if kind == "fix":
            _, i, vx, vy = c
            r1, r2 = row(), row()
            r1[2 * i], r2[2 * i + 1] = 1, 1
            res += [x[2 * i] - vx, x[2 * i + 1] - vy]
            rows += [r1, r2]
        elif kind == "dist":
            _, i, j, d = c
            if d <= 0:
                raise ValueError("a distance must be positive")
            dx, dy = x[2 * j] - x[2 * i], x[2 * j + 1] - x[2 * i + 1]
            ln = max(float(np.hypot(dx, dy)), 1e-12)
            r1 = row()
            r1[2 * j], r1[2 * j + 1], r1[2 * i], r1[2 * i + 1] = dx / ln, dy / ln, -dx / ln, -dy / ln
            res.append(ln - d)
            rows.append(r1)
        elif kind in ("horiz", "vert"):
            _, i, j = c
            k = 1 if kind == "horiz" else 0
            r1 = row()
            r1[2 * j + k], r1[2 * i + k] = 1, -1
            res.append(x[2 * j + k] - x[2 * i + k])
            rows.append(r1)
        elif kind == "perp":
            _, i, j, k = c
            ax, ay = x[2 * i] - x[2 * j], x[2 * i + 1] - x[2 * j + 1]
            bx, by = x[2 * k] - x[2 * j], x[2 * k + 1] - x[2 * j + 1]
            r1 = row()
            r1[2 * i], r1[2 * i + 1], r1[2 * k], r1[2 * k + 1] = bx, by, ax, ay
            r1[2 * j], r1[2 * j + 1] = -bx - ax, -by - ay
            res.append(ax * bx + ay * by)
            rows.append(r1)
        else:
            raise ValueError(f"unknown constraint '{kind}'")
    return np.array(res, dtype=float), (np.array(rows) if rows else np.zeros((0, n2)))


# %% [markdown]
# ## Step 2: Newton's method, and how many degrees of freedom are left
# Start from a rough guess of the points. At each step solve J dx = -r for the smallest correction dx
# (least squares, so extra freedom is not used up) and move x by dx. When the residuals are zero the sketch satisfies
# every constraint. The rank of J at the solution tells how many independent statements were made:
#
#     degrees of freedom = 2 (number of points) - rank(J)
#
# zero means fully constrained (the shape is fixed), more than zero means under-constrained (you can still drag
# something). A constraint count larger than the rank means some statements were redundant. If the residuals
# cannot be brought to zero, the statements contradict each other.

# %%
def solve(points0, constraints, tol=1e-11, max_iter=60):
    """Find points that satisfy all constraints, starting from a guess. Returns (points, info)."""
    x = np.asarray(points0, dtype=float).ravel().copy()
    n = len(x) // 2
    if len(x) % 2 or n == 0:
        raise ValueError("give an (n, 2) array of starting points")
    it = 0
    for it in range(max_iter):
        r, jac = system(x, constraints)
        nr = float(np.linalg.norm(r))
        if nr < tol:
            break
        dx = np.linalg.lstsq(jac, -r, rcond=None)[0]
        t = 1.0
        while t > 1e-4 and np.linalg.norm(system(x + t * dx, constraints)[0]) > nr:
            t /= 2                                       # shorten the step if it makes things worse
        x = x + t * dx
    r, jac = system(x, constraints)
    nr = float(np.linalg.norm(r))
    if nr > 1e-8:
        raise ValueError(f"the constraints cannot all be satisfied (residual {nr:.2g}): they contradict each other, or no such sketch exists")
    rank = int(np.linalg.matrix_rank(jac, tol=1e-9))
    return x.reshape(n, 2), {"iterations": it, "residual": nr, "dof": 2 * n - rank, "redundant": len(r) - rank}


def status(info):
    if info["dof"] == 0:
        return "fully constrained" + (f" ({info['redundant']} redundant, consistent)" if info["redundant"] else "")
    return f"under-constrained: {info['dof']} degree(s) of freedom left"


# %% [markdown]
# ## Step 3: a parametric L-bracket
# The L-shaped outline of Session 2 as six points. The statements are the ones a designer would make: the first
# corner is at the origin, each edge is horizontal or vertical with a given length. The thickness t appears twice
# and the inner edges use the equations b - t and h - t. To rebuild after a change, we solve again starting from the
# previous solution, so the sketch does not flip to a mirror image.

# %%
def l_bracket_constraints(b, h, t):
    if not (0 < t < min(b, h)):
        raise ValueError("need 0 < t < min(b, h)")
    return [("fix", 0, 0.0, 0.0), ("horiz", 0, 1), ("dist", 0, 1, b), ("vert", 1, 2), ("dist", 1, 2, t),
            ("horiz", 2, 3), ("dist", 2, 3, b - t), ("vert", 3, 4), ("dist", 3, 4, h - t),
            ("horiz", 4, 5), ("dist", 4, 5, t)]


ROUGH_L = [(0.5, -0.4), (48, 1.5), (49, 6), (6, 4.5), (4, 51), (-1, 49)]   # a hand-drawn L, a little crooked: the guess only picks the orientation


def build_l_bracket(b, h, t, guess=None):
    return solve(ROUGH_L if guess is None else guess, l_bracket_constraints(b, h, t))


def shoelace_area(points):
    p = np.asarray(points, dtype=float)
    return float(abs(np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1])) / 2)


def bracket_mass_kg(b, h, t, length_mm, guess=None):
    pts, _ = build_l_bracket(b, h, t, guess)
    return RHO * shoelace_area(pts) * length_mm * 1e-9


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    tri = [("fix", 0, 0, 0), ("horiz", 0, 1), ("dist", 0, 1, 4), ("dist", 0, 2, 3), ("dist", 1, 2, 5)]
    p, info = solve([(0, 0), (3, 0.5), (0.5, 2)], tri)
    print("3-4-5 triangle:", p.round(6).tolist(), status(info), f"after {info['iterations']} steps")
    print("angle at p0 is a right angle:", abs(np.dot(p[1] - p[0], p[2] - p[0])) < 1e-9)
    p2, _ = solve([(0, 0), (3, 0.5), (0.5, -2)], tri)
    print("starting below the axis picks the mirror image:", p2[2].round(6).tolist())
    _, info2 = solve([(0, 0), (3, 0.5), (0.5, 2)], tri[:-1])
    print("without the last distance:", status(info2))
    _, info3 = solve([(0, 0), (3, 0.5), (0.5, 2)], tri + [("perp", 1, 0, 2)])
    print("with a perpendicular statement that is already true:", status(info3))
    try:
        solve([(0, 0), (3, 0.5), (0.5, 2)], [tri[0], tri[1], tri[2], tri[3], ("dist", 1, 2, 8)])
    except ValueError as e:
        print("conflict:", e)

    pts, info = build_l_bracket(50, 50, 5)
    print("L 50 x 50 x 5:", pts.round(6).tolist(), status(info))
    print(f"area {shoelace_area(pts):.1f} mm2 (formula b t + (h - t) t = {50 * 5 + 45 * 5}), mass of 200 mm = {bracket_mass_kg(50, 50, 5, 200):.3f} kg")

    ts = np.linspace(2, 15, 27)
    guess, masses = None, []
    for t in ts:                                       # rebuild with continuity
        pts, _ = build_l_bracket(60, 40, float(t), guess)
        guess = pts
        masses.append(RHO * shoelace_area(pts) * 200 * 1e-9)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(ts, masses, "o-", color="tab:blue")
    ax.set_xlabel("thickness t (mm)")
    ax.set_ylabel("mass of a 200 mm long bracket (kg)")
    ax.set_title("Rebuilding a 60 x 40 mm L-bracket for many thicknesses")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "bracket_mass_vs_t.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    for (b, h, t), col in (((60, 40, 5), "tab:blue"), (((60, 40, 10)), "tab:red")):
        pts, _ = build_l_bracket(b, h, t)
        c = np.vstack([pts, pts[:1]])
        ax2.plot(c[:, 0], c[:, 1], "-o", color=col, label=f"t = {t} mm")
    ax2.set_aspect("equal")
    ax2.set_xlabel("x (mm)")
    ax2.set_ylabel("y (mm)")
    ax2.set_title("Same dimensions b = 60, h = 40; only the thickness changes")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "sketch_rebuild.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Real sketches also have arcs, tangent and symmetry constraints, and thousands of points. This solver handles only
# lines and distances, and it does not tell you which of two valid mirror images you wanted: the starting guess
# decides. The roadmap adds arcs and a solid feature tree.
