"""Session 3 (Level 3): a direct-stiffness truss solver, validated and stress-tested.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: one solver for any 2D pin-jointed truss
# **A. Real-world problem.** Statics (Session 2) fails when a truss has extra bars, and it
# says nothing about how far the truss sags. A footbridge must be strong *and* stiff. We
# build the method that computer programs use: the direct stiffness method, in which each
# bar is a spring and the whole truss is one equation K u = f.
#
# **Plan.** (1) one bar as a spring, (2) assemble all bars into K, (3) apply supports and
# solve, (4) recover bar forces, (5) validate against hand results, equilibrium and a
# virtual-work formula, (6) compare Pratt, Howe and Warren, (7) test a missing bar,
# stiffness changes and Euler buckling.
#
# Educational model: ideal pins, small deflections, straight weightless bars. Not for real
# structures.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: one bar is a spring along its own axis
# A bar from joint i to joint k has length L and axial stiffness EA/L (E = Young's modulus,
# A = cross-section area). With direction cosines c = cos(angle), s = sin(angle), the bar
# contributes the 4 x 4 matrix (EA/L) * [[c c, c s, -c c, -c s], [c s, s s, -c s, -s s],
# [-c c, -c s, c c, c s], [-c s, -s s, c s, s s]] to the joints it touches.
# Units: lengths in m, forces in kN, EA in kN, displacements in m.

# %%
def member_geometry(nodes, members):
    """Lengths and direction cosines (cx, cy) of every bar."""
    nodes = np.asarray(nodes, float)
    vec = np.array([nodes[k] - nodes[i] for i, k in members])
    length = np.linalg.norm(vec, axis=1)
    return length, vec / length[:, None]


def assemble_k(nodes, members, EA):
    """Global stiffness matrix (2 j x 2 j). EA is one number or one value per bar (kN)."""
    nodes = np.asarray(nodes, float)
    EA = np.broadcast_to(np.asarray(EA, float), (len(members),))
    length, cs = member_geometry(nodes, members)
    K = np.zeros((2 * len(nodes), 2 * len(nodes)))
    for e, (i, k) in enumerate(members):
        c, s = cs[e]
        blk = np.array([[c * c, c * s], [c * s, s * s]])
        dofs = [2 * i, 2 * i + 1, 2 * k, 2 * k + 1]
        ke = EA[e] / length[e] * np.block([[blk, -blk], [-blk, blk]])
        K[np.ix_(dofs, dofs)] += ke
    return K


# %% [markdown]
# ## Step 2: supports, the solve, and the recovery of forces
# Supports remove unknowns: we keep only the free degrees of freedom (dofs), solve
# K_ff u_f = f_f, and then recover each bar force from its stretch:
# F = (EA/L) * ((u_k - u_i) . (c, s)). Positive F = tension. Reactions follow from
# R = K u - f at the fixed dofs.
# A truss that is a *mechanism* has a singular K_ff: some motion costs no energy. We detect
# it from the rank of K_ff (or a huge condition number).

# %%
def free_dofs(n_nodes, supports):
    fixed = {2 * n + d for n, fl in supports.items() for d in (0, 1) if fl[d]}
    return [d for d in range(2 * n_nodes) if d not in fixed], sorted(fixed)


def is_mechanism(K, free):
    """True when the free-dof stiffness matrix is rank deficient (the truss can move freely)."""
    Kff = K[np.ix_(free, free)]
    return bool(np.linalg.matrix_rank(Kff) < len(free))


def solve_truss(nodes, members, EA, supports, loads):
    """Direct stiffness solution. Returns dict with u (j, 2) in m, forces (kN, tension +), reactions (2j,) in kN."""
    nodes = np.asarray(nodes, float)
    K = assemble_k(nodes, members, EA)
    free, fixed = free_dofs(len(nodes), supports)
    if is_mechanism(K, free):
        raise ValueError("mechanism: the stiffness matrix is singular (a bar is missing or supports are too few)")
    f = np.zeros(2 * len(nodes))
    for n, (fx, fy) in loads.items():
        f[2 * n] += fx
        f[2 * n + 1] += fy
    u = np.zeros(2 * len(nodes))
    u[free] = np.linalg.solve(K[np.ix_(free, free)], f[free])
    length, cs = member_geometry(nodes, members)
    EAv = np.broadcast_to(np.asarray(EA, float), (len(members),))
    forces = np.array([EAv[e] / length[e] * (u[2 * k:2 * k + 2] - u[2 * i:2 * i + 2]) @ cs[e]
                       for e, (i, k) in enumerate(members)])
    R = np.zeros(2 * len(nodes))
    R[fixed] = (K @ u - f)[fixed]
    return {"u": u.reshape(-1, 2), "forces": forces, "reactions": R}


def joint_residuals(nodes, members, forces, reactions, loads):
    """Net force on every joint (j, 2); all zeros when every pin is in equilibrium."""
    nodes = np.asarray(nodes, float)
    _, cs = member_geometry(nodes, members)
    res = np.array(reactions, float).reshape(-1, 2)
    for e, (i, k) in enumerate(members):
        res[i] += forces[e] * cs[e]
        res[k] -= forces[e] * cs[e]
    for n, (fx, fy) in loads.items():
        res[n] += (fx, fy)
    return res


# %% [markdown]
# ## Step 3: three bridge shapes under the same load
# Each is 8 m long with 4 panels of 2 m and a height of 2 m. Bottom joints sit on the deck;
# a pin at the left foot, a roller at the right foot, and a 10 kN load at midspan.
# Pratt: diagonals slope down towards the middle. Howe: diagonals slope up towards the
# middle. Warren: only sloping bars, alternately up and down.

# %%
def bridge(kind, span=8.0, panels=4, height=2.0):
    """Return nodes, members for 'pratt', 'howe' or 'warren' (panels must be even)."""
    dx = span / panels
    bottom = [[dx * i, 0.0] for i in range(panels + 1)]
    mem = [(i, i + 1) for i in range(panels)]
    if kind == "warren":
        top = [[dx * (i + 0.5), height] for i in range(panels)]
        nb = panels + 1
        mem += [(nb + i, nb + i + 1) for i in range(panels - 1)]
        for i in range(panels):
            mem += [(i, nb + i), (nb + i, i + 1)]
        return np.array(bottom + top, float), mem
    top = [[dx * i, height] for i in range(1, panels)]
    nb = panels + 1
    t = lambda i: nb + i - 1                       # index of the top joint above bottom joint i
    mem += [(t(i), t(i + 1)) for i in range(1, panels - 1)]
    mem += [(i, t(i)) for i in range(1, panels)]   # verticals
    mem += [(0, t(1)), (panels, t(panels - 1))]    # inclined end posts
    half = panels // 2
    for i in range(1, half):
        if kind == "pratt":
            mem += [(t(i), i + 1), (t(panels - i), panels - i - 1)]
        else:
            mem += [(i, t(i + 1)), (panels - i, t(panels - i - 1))]
    return np.array(bottom + top, float), mem


def standard_case(kind, load=10.0, EA=80000.0, **kw):
    nodes, members = bridge(kind, **kw)
    panels = int(round(nodes[:, 0].max() / 2.0))
    n_bottom = len([1 for x, y in nodes if y == 0.0])
    supports = {0: (1, 1), n_bottom - 1: (0, 1)}
    mid = n_bottom // 2
    return nodes, members, supports, {mid: (0.0, -load)}, EA


def tension_members(members, forces, tol=1e-6):
    return [m for m, f in zip(members, forces) if f > tol]


# %% [markdown]
# ## Step 4: an independent check of the deflection, by virtual work
# Unit-load (virtual work) formula: the deflection of a joint in the direction of a unit
# load placed there is delta = sum over bars of F_i f_i L_i / (EA)_i, where F_i are the
# bar forces for the real load and f_i those for a unit load at that joint.
# Simple case (the Session 1 truss): two sloping bars of length Ls and a bottom tie of
# length L, load P at the apex. Then F = -P/(2 sin t), f = -1/(2 sin t) for the sloping
# bars, F = P/(2 tan t), f = 1/(2 tan t) for the tie.

# %%
def virtual_work_deflection(forces, unit_forces, length, EA):
    return float(np.sum(forces * unit_forces * length / EA))


def triangle_apex_deflection(P, span, height, EA):
    """Closed-form apex deflection (m, downwards) of the two-bar-plus-tie truss."""
    th = np.arctan2(height, span / 2.0)
    Ls = np.hypot(span / 2.0, height)
    top = 2 * (P / (2 * np.sin(th))) * (1 / (2 * np.sin(th))) * Ls / EA
    tie = (P / (2 * np.tan(th))) * (1 / (2 * np.tan(th))) * span / EA
    return float(top + tie)


# %% [markdown]
# ## Step 5: when a bar goes missing, and when a bar buckles
# Remove one diagonal and the stiffness matrix becomes singular: the truss is a mechanism.
# For a compression bar the Euler load for a pin-ended column is P_cr = pi^2 E I / L^2
# (I = second moment of area). Used here only as a check that a compression bar does not
# fail by sideways bending. For a solid round bar of area A, I = A^2 / (4 pi).

# %%
def euler_load_kn(E_gpa, area_mm2, length_m):
    """Euler buckling load (kN) of a pin-ended solid round bar."""
    I_m4 = (area_mm2 * 1e-6) ** 2 / (4 * np.pi)
    return float(np.pi ** 2 * E_gpa * 1e6 * I_m4 / length_m ** 2)


# %% [markdown]
# ## Step 6: size a footbridge (mini-project tools)
# Fully stressed sizing: every bar gets the area |F| / sigma_allow, but not less than a
# minimum area. If the sag is above the limit, all areas are scaled up together (for a
# determinate truss the sag is proportional to 1/area). Weight = density * sum(A L).
# Illustrative numbers only.

# %%
def size_truss(nodes, members, supports, loads, sigma_mpa=150.0, a_min_mm2=100.0, E_gpa=200.0, limit_mm=None):
    """Return dict(area, weight_kg, sag_mm, scaled) for a determinate truss."""
    length, _ = member_geometry(nodes, members)
    f0 = solve_truss(nodes, members, E_gpa * 300.0, supports, loads)["forces"]
    area = np.maximum(np.abs(f0) * 1000.0 / sigma_mpa, a_min_mm2)
    scaled = 1.0
    sag = -solve_truss(nodes, members, E_gpa * area, supports, loads)["u"][:, 1].min() * 1000.0
    if limit_mm is not None and sag > limit_mm:
        scaled = sag / limit_mm
        area = area * scaled
        sag = limit_mm
    weight = float(7850.0 * np.sum(area * 1e-6 * length))
    return {"area": area, "weight_kg": weight, "sag_mm": float(sag), "scaled": float(scaled)}


def footbridge_case(kind, line_load=6.0):
    """12 m footbridge, 6 panels of 2 m, height 2 m, uniform deck load line_load (kN/m)."""
    nodes, members = bridge(kind, span=12.0, panels=6, height=2.0)
    n_bottom = 7
    supports = {0: (1, 1), n_bottom - 1: (0, 1)}
    loads = {i: (0.0, -line_load * 2.0) for i in range(1, n_bottom - 1)}
    return nodes, members, supports, loads


# %% [markdown]
# ## Step 7: see it
# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.6))
    for ax, kind in zip(axs, ("pratt", "howe", "warren")):
        nodes, members, supports, loads, EA = standard_case(kind)
        r = solve_truss(nodes, members, EA, supports, loads)
        F, u = r["forces"], r["u"]
        big = np.abs(F).max()
        for (i, k), fk in zip(members, F):
            col = "tab:blue" if fk > 1e-6 else ("tab:red" if fk < -1e-6 else "0.6")
            ax.plot(nodes[[i, k], 0], nodes[[i, k], 1], color=col, lw=1 + 5 * abs(fk) / big)
        d = nodes + 200 * u
        for (i, k) in members:
            ax.plot(d[[i, k], 0], d[[i, k], 1], "k--", lw=0.7)
        ax.set_aspect("equal")
        ax.set_title(f"{kind}: max sag {-u[:, 1].min() * 1000:.2f} mm (drawn x200)", fontsize=9)
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        ax.set_ylim(-0.8, 2.6)
        nt = len(tension_members(members, F))
        print(f"{kind:7s}: {len(members)} bars, {nt} in tension, "
              f"max tension {F.max():+.2f} kN, max compression {F.min():+.2f} kN, "
              f"sag {-u[:, 1].min() * 1000:.3f} mm")
    fig.tight_layout()
    fig.savefig(OUT / "three_trusses.png", dpi=120)

    # sensitivity of sag to member stiffness (determinate trusses: forces do not change)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    eas = np.linspace(40000, 200000, 40)
    for kind in ("pratt", "howe", "warren"):
        nodes, members, supports, loads, _ = standard_case(kind)
        sag = [-solve_truss(nodes, members, ea, supports, loads)["u"][:, 1].min() * 1000 for ea in eas]
        ax2.plot(eas / 1000, sag, label=kind)
    ax2.set_xlabel("bar stiffness EA (MN)")
    ax2.set_ylabel("largest sag (mm)")
    ax2.set_title("Sag is inversely proportional to EA")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "sag_vs_ea.png", dpi=120)

    nodes, members, supports, loads, EA = standard_case("pratt")
    try:
        solve_truss(nodes, members[:-1], EA, supports, loads)
    except ValueError as err:
        print("missing bar ->", err)
    A = 300.0
    print("Euler load of a 2 m long solid bar of 300 mm^2:", round(euler_load_kn(200.0, A, 2.0), 3), "kN")
    for kind in ("pratt", "howe", "warren"):
        nodes, members, supports, loads = footbridge_case(kind)
        r = size_truss(nodes, members, supports, loads, limit_mm=24.0)
        print(f"footbridge {kind:7s}: weight {r['weight_kg']:.0f} kg, sag {r['sag_mm']:.1f} mm, scale {r['scaled']:.2f}")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
