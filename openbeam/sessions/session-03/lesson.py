"""Session 3 (Level 3): solve beams numerically with finite elements and check against formulas.

Run:  python start.py 3
Educational model only (Euler-Bernoulli, small deflections, elastic). Never use it to design a real structure.
"""
# %% [markdown]
# # Session 3: let the computer solve the beam
# **A. Real-world problem.** Real beams have distributed loads, several point loads and
# sections that change along their length. Formulas exist only for a few simple cases. The
# finite element method (FEM) chops the beam into short *elements*, writes a small
# stiffness relation for each, and solves them together. But how do we know the program is
# right? We run it on cases that have an exact answer, and we study what happens as the mesh
# gets finer. Only then do we trust it on cases that have no formula.
#
# **Plan.** (1) a 2-node Euler-Bernoulli element, (2) assemble and solve, (3) validate against
# the formulas of Session 2, (4) mesh convergence, (5) sensitivity to E and depth, (6) a limit
# of the theory (shear deformation).

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G_ACC = 9.81      # m/s^2
RHO = 7850.0      # steel density, kg/m^3


# %% [markdown]
# ## Step 1: the element
# Each node has two unknowns: deflection `w` (m, downward) and slope `theta` (rad). An element
# of length `le` and stiffness `EI` has the 4 x 4 stiffness matrix below. A uniform load `q`
# (N/m) on the element is replaced by equivalent nodal forces `q le / 2` and moments
# `+-q le^2 / 12`. A point load inside an element is shared to the nodes with the element's
# own shape functions (the "consistent" load).

# %%
def element_k(EI, le):
    return EI / le ** 3 * np.array([
        [12, 6 * le, -12, 6 * le],
        [6 * le, 4 * le ** 2, -6 * le, 2 * le ** 2],
        [-12, -6 * le, 12, -6 * le],
        [6 * le, 2 * le ** 2, -6 * le, 4 * le ** 2]])


def shape(xi, le):
    """Hermite shape functions at local coordinate xi in [0, 1]."""
    return np.array([1 - 3 * xi ** 2 + 2 * xi ** 3, le * (xi - 2 * xi ** 2 + xi ** 3),
                     3 * xi ** 2 - 2 * xi ** 3, le * (-xi ** 2 + xi ** 3)])


# %% [markdown]
# ## Step 2: assemble and solve
# `EI` may be a number or a function of x (a beam whose depth changes). Supports are
# "simple" (w = 0 at both ends) or "cantilever" (w = theta = 0 at x = 0). For a continuous beam
# give `supports=[(x, "pin"), ...]`: a "pin" holds w = 0 and a "fixed" support holds w = theta = 0
# at the node nearest x. Every support's upward reaction is returned in `reactions`.

# %%
def solve_beam(L, n, EI, q=0.0, points=(), support="simple", supports=None):
    """Euler-Bernoulli beam by finite elements.

    L span (m); n elements; EI constant (N m^2) or function EI(x); q uniform load (N/m, downward);
    points = [(x, P), ...] downward point loads (N); support = "simple" or "cantilever", or
    supports = [(x, "pin" or "fixed"), ...] for supports at any nodes (x must lie on a node).
    Returns dict with nodes x, deflection w (m, down), slope th, per-element mid-point arrays
    xm, M (N m, sagging positive) and V (N), and reactions = [(x, upward force N, moment N m), ...].
    """
    xs = np.linspace(0.0, L, n + 1)
    le = L / n
    ei = EI if callable(EI) else (lambda x: EI)
    K = np.zeros((2 * n + 2, 2 * n + 2))
    F = np.zeros(2 * n + 2)
    eis = np.array([ei(0.5 * (xs[e] + xs[e + 1])) for e in range(n)])
    for e in range(n):
        s = slice(2 * e, 2 * e + 4)
        K[s, s] += element_k(eis[e], le)
        F[s] += q * le * np.array([0.5, le / 12, 0.5, -le / 12])
    for xp, P in points:
        e = min(int(xp / le), n - 1)
        xi = (xp - xs[e]) / le
        F[2 * e:2 * e + 4] += P * shape(xi, le)
    if supports is None:
        supports = [(0.0, "pin"), (L, "pin")] if support == "simple" else [(0.0, "fixed")]
    fixed = []
    for xs_, kind in supports:
        i = int(round(xs_ / le))
        if abs(xs[i] - xs_) > 1e-9 * max(L, 1.0):
            raise ValueError(f"a support at x = {xs_} is not on a node; use a mesh whose nodes include it")
        fixed += [2 * i] if kind == "pin" else [2 * i, 2 * i + 1]
    free = [i for i in range(2 * n + 2) if i not in fixed]
    d = np.zeros(2 * n + 2)
    d[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    w, th = d[0::2], d[1::2]
    M = np.zeros(n)
    V = np.zeros(n)
    for e in range(n):
        de = d[2 * e:2 * e + 4]
        M[e] = -eis[e] * (de[3] - de[1]) / le                      # -EI w'' averaged over the element (w is downward)
        V[e] = -eis[e] / le ** 3 * (12 * de[0] + 6 * le * de[1] - 12 * de[2] + 6 * le * de[3])
    # reaction = applied load minus what the stiffness carries, at the held degrees of freedom
    r = F - K @ d
    reactions = [(xs[i], r[2 * i], r[2 * i + 1]) for i in sorted({f // 2 for f in fixed})]
    return {"x": xs, "w": w, "th": th, "xm": 0.5 * (xs[:-1] + xs[1:]), "M": M, "V": V, "reactions": reactions}


# %% [markdown]
# ## Step 3: validate against exact answers
# * simply supported, centre point load: w = P L^3 / (48 E I)
# * simply supported, uniform load: w = 5 q L^4 / (384 E I)
# * cantilever, tip load: w = P L^3 / (3 E I)
#
# (The first is the formula from Session 2; the others are standard textbook results.)

# %%
def exact_centre_point(P, L, EI):
    return P * L ** 3 / (48 * EI)


def exact_udl(q, L, EI):
    return 5 * q * L ** 4 / (384 * EI)


def exact_point(x, P, a, L, EI):
    """Exact deflection of a simply supported beam with a point load P at a, at position x."""
    x = np.asarray(x, dtype=float)
    b = L - a
    left = P * b * x * (L ** 2 - b ** 2 - x ** 2) / (6 * EI * L)
    xr = L - x
    right = P * a * xr * (L ** 2 - a ** 2 - xr ** 2) / (6 * EI * L)
    return np.where(x <= a, left, right)


# %% [markdown]
# ## Step 4: mesh convergence
# A good solver gets closer to the truth as the mesh is refined, and we want to know how fast.
# For a beam whose depth changes along x there is no simple formula, so we compare each mesh
# with a very fine one (the *reference*).

# %%
def tapered_EI(E, b, h0, h1, L):
    """EI(x) for a rectangular beam whose depth goes linearly from h0 at x = 0 to h1 at x = L."""
    return lambda x: E * b * (h0 + (h1 - h0) * x / L) ** 3 / 12.0


def convergence_table(L, EI, q, meshes=(2, 4, 8, 16, 32)):
    """Relative errors for a uniform load, simple supports: (n, deflection error, moment error at
    the element middle against the exact moment there, moment error against the true peak wL^2/8)."""
    wex, Mex = exact_udl(q, L, EI), q * L ** 2 / 8
    rows = []
    for n in meshes:
        r = solve_beam(L, n, EI, q=q)
        wmid = r["w"][n // 2]
        k = int(np.argmin(np.abs(r["xm"] - L / 2)))
        Mx = q * r["xm"][k] * (L - r["xm"][k]) / 2
        rows.append((n, abs(wmid - wex) / wex, abs(r["M"][k] - Mx) / Mex, abs(r["M"][k] - Mex) / Mex))
    return rows


# %% [markdown]
# ## Step 5: sensitivity
# How much does the deflection change when E or the depth h changes by a few percent? Theory:
# w is proportional to 1/E and to 1/h^3, so a 10% deeper beam deflects by 1/1.1^3 = 0.751 of before.

# %%
def sensitivity_slope(f, x0, rel=0.01):
    """Log-log slope d(ln f)/d(ln x) of f at x0 by a small relative step."""
    return float((np.log(f(x0 * (1 + rel))) - np.log(f(x0 * (1 - rel)))) / (np.log(1 + rel) - np.log(1 - rel)))


# %% [markdown]
# ## Step 6: where the theory stops (shear deformation)
# Euler-Bernoulli theory ignores that the beam also shears. For a centre load the extra
# deflection relative to the bending deflection is about  E h^2 / (kappa G L^2) for a
# rectangle (kappa = 5/6, E/G = 2 (1 + nu)). Short, deep beams (L/h below about 10) need a
# better theory.

# %%
def shear_deflection_ratio(L_over_h, nu=0.3, kappa=5.0 / 6.0):
    return 2 * (1 + nu) / (kappa * L_over_h ** 2)


# %% [markdown]
# ## Step 7: a design check built on the solver (used by the mini-project)
# Service load = uniform load + a point load at mid-span + the beam's own weight.

# %%
def isection_props(bf, tf, tw, h):
    """Area (m^2), second moment of area (m^4) of a symmetric I-section; lengths in m."""
    A = 2 * bf * tf + tw * (h - 2 * tf)
    I = (bf * h ** 3 - (bf - tw) * (h - 2 * tf) ** 3) / 12.0
    return A, I


def check_footbridge(L, w_line, P_mid, E, sigma_y, fos, section, n=240, ratio=360.0):
    """Returns dict with deflection w (m), stress (Pa), mass per metre (kg/m) and pass flags.

    w_line is the uniform service load in N/m (without self weight); section = (bf, tf, tw, h) in m.
    The solver gives the moment as an average over each element, so a fine mesh (n = 240) is used
    to make the peak moment accurate to better than 0.1%."""
    A, I = isection_props(*section)
    h = section[3]
    q = w_line + RHO * G_ACC * A
    r = solve_beam(L, n, E * I, q=q, points=[(L / 2, P_mid)])
    wmax = float(r["w"].max())
    Mmax = float(np.abs(r["M"]).max())
    stress = Mmax * (h / 2) / I
    out = {"w": wmax, "stress": stress, "mass": RHO * A, "I": I, "M": Mmax}
    out["ok_defl"] = wmax <= L / ratio
    out["ok_stress"] = stress * fos <= sigma_y
    out["ok"] = out["ok_defl"] and out["ok_stress"]
    return out


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    L, E, I = 4.0, 200e9, 8.0e-6
    EI = E * I
    P, q = 10e3, 5e3
    # validation
    r = solve_beam(L, 2, EI, points=[(L / 2, P)])
    print(f"centre load, 2 elements: FE {r['w'][1] * 1e3:.4f} mm, exact {exact_centre_point(P, L, EI) * 1e3:.4f} mm")
    r = solve_beam(L, 8, EI, q=q)
    print(f"UDL, 8 elements: FE {r['w'][4] * 1e3:.4f} mm, exact {exact_udl(q, L, EI) * 1e3:.4f} mm")
    r = solve_beam(L, 16, EI, points=[(1.3, P)])
    err = np.abs(r["w"] - exact_point(r["x"], P, 1.3, L, EI)).max()
    print(f"off-node point load at 1.3 m, 16 elements: largest nodal error {err:.2e} m")
    rc = solve_beam(L, 8, EI, points=[(L, P)], support="cantilever")
    print(f"cantilever tip load: FE {rc['w'][-1] * 1e3:.4f} mm, exact {P * L ** 3 / (3 * EI) * 1e3:.4f} mm")

    rows = convergence_table(L, EI, q)
    print("n   deflection err   moment err (at element middle)   moment err (against peak)")
    for n, ew, em, ep in rows:
        print(f"{n:3d}  {ew:.2e}   {em:.2e}   {ep:.2e}")

    # tapered beam convergence against a fine reference
    EIt = tapered_EI(E, 0.05, 0.12, 0.06, L)
    ref = solve_beam(L, 512, EIt, points=[(L, P)], support="cantilever")["w"][-1]
    print(f"tapered cantilever tip deflection, 512-element reference {ref * 1e3:.4f} mm")
    terr = []
    for n in (2, 4, 8, 16, 32):
        tip = solve_beam(L, n, EIt, points=[(L, P)], support="cantilever")["w"][-1]
        terr.append(abs(tip - ref) / ref)
        print(f"  n={n:3d}: tip {tip * 1e3:.4f} mm, relative error {terr[-1]:.2e}")

    # sensitivity
    f_E = lambda e: solve_beam(L, 8, e * I, points=[(L / 2, P)])["w"][4]
    f_h = lambda hh: solve_beam(L, 8, E * 0.05 * hh ** 3 / 12, points=[(L / 2, P)])["w"][4]
    print("slope of ln(w) against ln(E):", round(sensitivity_slope(f_E, E), 3), " against ln(h):", round(sensitivity_slope(f_h, 0.2), 3))
    for ratio in (20, 10, 5, 2):
        print(f"L/h = {ratio}: shear adds {100 * shear_deflection_ratio(ratio):.1f}% to the bending deflection")

    # figures
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    fine = solve_beam(L, 64, EI, q=q)
    ax[0].plot(fine["x"], -1e3 * fine["w"], "-", label="64 elements")
    c = solve_beam(L, 2, EI, q=q)
    ax[0].plot(c["x"], -1e3 * c["w"], "ro", label="2 elements (nodes only)")
    xx = np.linspace(0, L, 200)
    exact_shape = q * xx * (L ** 3 - 2 * L * xx ** 2 + xx ** 3) / (24 * EI)
    ax[0].plot(xx, -1e3 * exact_shape, "k--", lw=1, label="exact curve")
    ax[0].set_xlabel("position along the beam x (m)")
    ax[0].set_ylabel("deflection (mm, downward is negative)")
    ax[0].set_title("FE nodes lie on the exact curve")
    ax[0].grid(alpha=0.3)
    ax[0].legend(fontsize=8)
    ns = [r_[0] for r_ in rows]
    ax[1].loglog(ns, [r_[2] for r_ in rows], "o-", label="moment at element middle (UDL)")
    ax[1].loglog(ns, [max(r_[1], 1e-16) for r_ in rows], "s-", label="mid-span deflection (UDL)")
    ax[1].loglog(ns, terr, "^-", label="tapered cantilever tip")
    ax[1].loglog(ns, [terr[0] * (ns[0] / k) ** 2 for k in ns], "k:", label="slope -2 guide")
    ax[1].set_xlabel("number of elements n")
    ax[1].set_ylabel("relative error")
    ax[1].set_title("Mesh convergence")
    ax[1].grid(alpha=0.3, which="both")
    ax[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fe_validation.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ratios = np.linspace(2, 20, 100)
    ax2.plot(ratios, 100 * shear_deflection_ratio(ratios))
    ax2.axvline(10, color="r", ls="--", label="L/h = 10 rule of thumb")
    ax2.set_xlabel("span to depth ratio L/h")
    ax2.set_ylabel("shear deflection / bending deflection (%)")
    ax2.set_title("Where Euler-Bernoulli theory starts to fail")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "shear_limit.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Small deflections, straight elastic beams, one material. No buckling, no connections, no
# fatigue, no dynamic crowd loading. That is why this is a classroom model and never a design tool.
