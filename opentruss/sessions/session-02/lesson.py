"""Session 2 (Level 2): method of joints, method of sections and determinacy.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: equilibrium of every pin gives every bar force
# **A. Real-world problem.** A 6 m footbridge truss carries a 10 kN load at midspan. Before
# anyone cuts steel, an engineer must know the force in every bar: which are pulled, which
# are pushed, and how big. Here we do that with statics only.
#
# **Plan.** (1) count bars, joints and supports to see whether statics is enough,
# (2) write equilibrium of each pin (sum Fx = 0, sum Fy = 0) as one linear system,
# (3) solve a three-bar bracket and a Warren truss, (4) check with the method of sections,
# (5) size the bars for a stress limit.
#
# Educational model: ideal pins, straight weightless bars, loads only at joints. Never use
# it for a real structure.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: determinacy, m + r = 2 j
# m bars, r support reactions, j joints. Each joint gives 2 equations (sum Fx, sum Fy), so
# there are 2 j equations for m + r unknowns. If m + r = 2 j, statics alone is enough
# (statically determinate). If m + r < 2 j the truss is a mechanism (it can move). If
# m + r > 2 j there are redundant bars (statically indeterminate): statics is not enough
# and Session 3 handles that with stiffness.

# %%
def determinacy(m, r, j):
    """Return 'determinate', 'mechanism' or 'indeterminate' from m + r compared with 2 j."""
    if m + r == 2 * j:
        return "determinate"
    return "mechanism" if m + r < 2 * j else "indeterminate"


# %% [markdown]
# ## Step 2: the method of joints as a linear system
# Take one pin. Bars pull on it along their axes. A bar in tension (force F > 0) pulls the
# pin towards the bar's other end. With direction cosines (cx, cy) pointing from this pin to
# the other end, the pin feels F * (cx, cy). Writing sum Fx = 0 and sum Fy = 0 for every pin
# gives A x = b where x holds all bar forces and support reactions.

# %%
def solve_by_joints(nodes, members, supports, loads):
    """Solve a determinate truss.

    nodes: (j, 2) coordinates in m.  members: list of (i, k) node pairs.
    supports: dict node -> (restrain_x, restrain_y) with 0/1 flags.
    loads: dict node -> (Fx, Fy) in kN (applied to the joint).
    Returns (forces, reactions): forces in kN, tension positive; reactions = list of
    (node, direction 0/1, value in kN).
    """
    nodes = np.asarray(nodes, float)
    j, m = len(nodes), len(members)
    reac = [(n, d) for n, fl in sorted(supports.items()) for d in (0, 1) if fl[d]]
    A = np.zeros((2 * j, m + len(reac)))
    for e, (i, k) in enumerate(members):
        vec = nodes[k] - nodes[i]
        c = vec / np.linalg.norm(vec)
        A[2 * i:2 * i + 2, e] += c      # tension pulls node i towards node k
        A[2 * k:2 * k + 2, e] -= c      # and node k towards node i
    for q, (n, d) in enumerate(reac):
        A[2 * n + d, m + q] = 1.0
    b = np.zeros(2 * j)
    for n, (fx, fy) in loads.items():
        b[2 * n] -= fx                   # loads move to the right-hand side with a minus sign
        b[2 * n + 1] -= fy
    x = np.linalg.solve(A, b)
    return x[:m], [(n, d, float(v)) for (n, d), v in zip(reac, x[m:])]


# %% [markdown]
# ## Step 3: a three-bar bracket
# A bracket on a wall: pin A at the top, B below it, joint C sticks out 2.0 m and carries
# the load. Members AC (sloping up to the wall), BC (horizontal) and AB (the vertical wall
# bar). A 12 kN load hangs at C. Hand check at C: AC pulls up and in, BC pushes out.

# %%
def bracket(load=12.0, reach=2.0, rise=1.5):
    nodes = [[0.0, rise], [0.0, 0.0], [reach, 0.0]]          # A, B, C
    members = [(0, 2), (1, 2), (0, 1)]                        # AC, BC, AB
    supports = {0: (1, 1), 1: (1, 0)}                         # A pinned, B horizontal roller
    forces, reac = solve_by_joints(nodes, members, supports, {2: (0.0, -load)})
    return forces, reac


# %% [markdown]
# ## Step 4: a Warren truss
# A Warren truss has sloping bars alternately up and down and no verticals. Our example:
# span 6 m, bottom joints every 2 m, equilateral triangles of side 2 m (height sqrt(3)
# = 1.732 m). That is 7 joints, 11 bars and 3 reactions (a pin and a roller):
# m + r = 14 = 2 j. The 10 kN load acts down on the top joint at midspan.

# %%
def warren(side=2.0, panels=3):
    """Nodes and members of a Warren truss with `panels` bottom panels of equilateral triangles."""
    h = side * np.sqrt(3.0) / 2.0
    bottom = [[side * i, 0.0] for i in range(panels + 1)]
    top = [[side * (i + 0.5), h] for i in range(panels)]
    nodes = bottom + top
    nb = panels + 1
    members = [(i, i + 1) for i in range(panels)]                      # bottom chord
    members += [(nb + i, nb + i + 1) for i in range(panels - 1)]       # top chord
    for i in range(panels):                                            # sloping bars
        members += [(i, nb + i), (nb + i, i + 1)]
    return np.array(nodes), members


def warren_example(load=10.0):
    nodes, members = warren()
    supports = {0: (1, 1), 3: (0, 1)}               # pin at the left foot, roller at the right foot
    mid_top = 5                                      # top joint at x = 3 m
    forces, reac = solve_by_joints(nodes, members, supports, {mid_top: (0.0, -load)})
    return nodes, members, forces, reac


# %% [markdown]
# ## Step 5: method of sections (a second route to the same answer)
# Instead of going pin by pin, cut the truss in two and write equilibrium of one piece.
# Cut through three bars. Taking moments about the point where two of them meet removes
# those two forces, leaving the third.
# Left piece, cut at x = 2.5 m: only the left reaction (5 kN up at x = 0) acts on it.
#   bottom chord: moment about the top joint at x = 3 m:  F_bottom * h = R * 3
#   top chord:    moment about the bottom joint at x = 2 m:  F_top * h = - R * 2

# %%
def sections_midspan(load=10.0, side=2.0):
    """Bottom-chord and top-chord forces (kN) in the middle panel by the method of sections."""
    h = side * np.sqrt(3.0) / 2.0
    r_left = load / 2.0                              # symmetric load: each support carries half
    f_bottom = r_left * 3.0 / h                      # tension
    f_top = -r_left * 2.0 / h                        # compression
    return float(f_bottom), float(f_top)


# %% [markdown]
# ## Step 6: size the bars for a stress limit
# Stress sigma = F / A. If the stress limit is sigma_allow (MPa = N/mm^2), a bar needs an
# area A = |F| / sigma_allow. With F in kN: A (mm^2) = 1000 |F| / sigma_allow.
# Compression bars also have a *buckling* concern: a long slim bar can bend sideways well
# below the stress limit, so in practice they are made thicker. Session 3 checks one case.

# %%
def required_area(force_kn, sigma_mpa):
    """Smallest bar area in mm^2 for a force in kN and an allowable stress in MPa."""
    return 1000.0 * abs(force_kn) / sigma_mpa


# %% [markdown]
# ## Step 7: see it

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    f, reac = bracket()
    print("bracket forces AC, BC, AB (kN):", np.round(f, 2), " reactions:", [(n, d, round(v, 2)) for n, d, v in reac])
    nodes, members, forces, reac = warren_example()
    print("Warren reactions:", [(n, d, round(v, 2)) for n, d, v in reac])
    for k, ((i, j), fk) in enumerate(zip(members, forces)):
        print(f"  bar {k:2d} ({i}-{j}): {fk:+.2f} kN")
    print("sections (bottom, top) =", np.round(sections_midspan(), 2))
    print("determinacy:", determinacy(len(members), 3, len(nodes)))
    print("largest force", round(float(np.abs(forces).max()), 2), "kN needs",
          round(required_area(np.abs(forces).max(), 150.0), 1), "mm^2 at 150 MPa")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    big = np.abs(forces).max()
    for (i, j), fk in zip(members, forces):
        col = "tab:blue" if fk > 1e-9 else ("tab:red" if fk < -1e-9 else "0.6")
        ax1.plot(nodes[[i, j], 0], nodes[[i, j], 1], color=col, lw=1 + 6 * abs(fk) / big)
    ax1.plot(nodes[:, 0], nodes[:, 1], "ko", ms=5)
    ax1.annotate("", xy=(3, 1.732), xytext=(3, 3.2), arrowprops=dict(arrowstyle="->", lw=2))
    ax1.text(3.15, 2.7, "10 kN")
    ax1.set_aspect("equal")
    ax1.set_xlabel("x (m)")
    ax1.set_ylabel("y (m)")
    ax1.set_ylim(-0.6, 3.6)
    ax1.set_title("Warren truss: blue tension, red compression")
    cols = ["tab:blue" if v > 0 else "tab:red" for v in forces]
    ax2.bar(range(len(forces)), forces, color=cols)
    ax2.axhline(0, color="gray", lw=0.8)
    ax2.set_xlabel("bar number")
    ax2.set_ylabel("force (kN, tension positive)")
    ax2.set_title("Force in every bar")
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "warren_forces.png", dpi=120)

    fig2, ax3 = plt.subplots(figsize=(6, 4))
    sig = np.linspace(50, 250, 81)
    ax3.plot(sig, [required_area(big, s) for s in sig], color="tab:blue")
    ax3.set_xlabel("allowable stress (MPa)")
    ax3.set_ylabel("area of the most loaded bar (mm^2)")
    ax3.set_title("Higher allowable stress needs less steel (10 kN load)")
    ax3.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "area_vs_stress.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
