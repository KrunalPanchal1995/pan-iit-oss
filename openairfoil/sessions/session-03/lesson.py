"""Session 3 (Level 3): a panel method for airfoil lift, plus a drag estimate, validated.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: compute the flow round any airfoil, then check it
# **A. Real-world problem.** Thin-airfoil theory ignores thickness and says nothing about the
# pressure on the surface. Can we compute the speed and pressure all round a real airfoil,
# prove the code is right on a case with an exact answer, and then estimate the airfoil's
# lift and drag, and pick a wing section for a small aircraft?
#
# **Plan.** (1) cut the surface into straight panels, (2) put a source on each panel and one
# shared vortex strength on all of them (the Hess-Smith method), (3) solve a linear system so
# no air flows through any panel and the flow leaves the trailing edge smoothly, (4) get Cp
# and CL, (5) validate, (6) add a skin-friction drag estimate, (7) choose an airfoil.
#
# **Model.** Two-dimensional, steady, incompressible, inviscid (potential) flow for the
# pressure; a flat-plate friction law for the drag. Free-stream speed 1 and chord 1, so all
# results are coefficients. A simplified teaching model, not a design tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
NU_AIR = 1.5e-5     # m2/s, kinematic viscosity of air near 20 degrees C


# %% [markdown]
# ## Step 1: the airfoil outline (from Session 2)
# The panel corners run clockwise: trailing edge, lower surface, nose, upper surface,
# trailing edge. Cosine spacing packs panels near the nose and the tail where the flow
# changes fastest.

# %%
def naca4(code, n=80):
    """NACA 4-digit outline as (X, Y), 2n panels, clockwise from the trailing edge."""
    if len(code) != 4 or not code.isdigit():
        raise ValueError("a NACA 4-digit code has exactly four digits, e.g. '2412'")
    m, p, t = int(code[0]) / 100, int(code[1]) / 10, int(code[2:]) / 100
    if (m > 0 and p == 0) or t == 0:
        raise ValueError("invalid NACA code")
    x = 0.5 * (1 - np.cos(np.linspace(0.0, np.pi, n + 1)))
    yt = 5 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1036 * x**4)
    if m > 0:
        front = x < p
        yc = np.where(front, m / p**2 * (2 * p * x - x**2), m / (1 - p) ** 2 * ((1 - 2 * p) + 2 * p * x - x**2))
        th = np.arctan(np.where(front, 2 * m / p**2 * (p - x), 2 * m / (1 - p) ** 2 * (p - x)))
    else:
        yc, th = np.zeros_like(x), np.zeros_like(x)
    xu, yu = x - yt * np.sin(th), yc + yt * np.cos(th)
    xl, yl = x + yt * np.sin(th), yc - yt * np.cos(th)
    return np.r_[xl[::-1], xu[1:]], np.r_[yl[::-1], yu[1:]]


def circle(n=80):
    """A unit circle as clockwise panels (for the validation against the exact solution)."""
    th = np.linspace(0.0, 2 * np.pi, n + 1)
    return np.cos(th), -np.sin(th)


# %% [markdown]
# ## Step 2: what one panel does to the air
# A panel j carries a source of strength q_j (air flows out of it) and a vortex of strength
# gamma (air swirls round it), both spread evenly along its length. In the panel's own
# coordinates (x along the panel, y across it, panel from 0 to l) a source sheet gives the
# velocity
#
#     u = q / (2 pi) ln(r1 / r2),      v = q / (2 pi) beta
#
# where r1, r2 are the distances to the panel ends and beta the angle the panel fills as
# seen from the point. A vortex sheet gives the same two numbers swapped:
# u = gamma beta / (2 pi), v = -gamma ln(r1 / r2) / (2 pi). Seen from its own midpoint a
# panel has beta = pi (it fills half the view) and ln(r1 / r2) = 0.

# %%
def panel_geometry(X, Y):
    """Midpoints, lengths, unit tangents and outward unit normals of the panels."""
    dx, dy = np.diff(X), np.diff(Y)
    length = np.hypot(dx, dy)
    tx, ty = dx / length, dy / length
    return 0.5 * (X[:-1] + X[1:]), 0.5 * (Y[:-1] + Y[1:]), length, tx, ty, -ty, tx


def influence(X, Y, xp, yp, self_panels=False):
    """Velocities at points (xp, yp) from unit source and unit vortex sheets on every panel.

    Returns (Usx, Usy, Uvx, Uvy), each of shape (points, panels), in global x and y."""
    _, _, length, tx, ty, _, _ = panel_geometry(X, Y)
    rx, ry = np.asarray(xp)[:, None] - X[None, :-1], np.asarray(yp)[:, None] - Y[None, :-1]
    xl, yl = rx * tx + ry * ty, -rx * ty + ry * tx                 # panel-local coordinates
    beta = np.arctan2(yl, xl - length) - np.arctan2(yl, xl)
    lg = 0.5 * np.log((xl**2 + yl**2) / ((xl - length) ** 2 + yl**2))
    if self_panels:                                                 # a panel seen from its own midpoint
        np.fill_diagonal(beta, np.pi)
        np.fill_diagonal(lg, 0.0)
    us, vs, uv, vv = lg / (2 * np.pi), beta / (2 * np.pi), beta / (2 * np.pi), -lg / (2 * np.pi)
    return us * tx - vs * ty, us * ty + vs * tx, uv * tx - vv * ty, uv * ty + vv * tx


# %% [markdown]
# ## Step 3: the linear system
# Unknowns: N source strengths and one vortex strength gamma. Equations:
#
# * flow tangency at each panel midpoint i: (V_inf + sum of all panel velocities) . n_i = 0
# * Kutta condition: the tangential speeds on the first and last panel (the two sides of
#   the trailing edge) are equal in size, so the air leaves the sharp edge smoothly.
#
# That is N + 1 linear equations, solved with `np.linalg.solve`. Then the tangential speed
# on each panel gives Cp = 1 - Vt^2, and summing -Cp n l gives the force. The total
# circulation Gamma = gamma x perimeter gives a second, independent lift: CL = 2 Gamma / c
# (Kutta-Joukowski). Without the Kutta row (and gamma = 0) the method gives zero lift; that
# is used for the circle test.

# %%
def solve_panels(X, Y, alpha_deg, kutta=True):
    """Hess-Smith panel method. Returns a dict with Cp, Vt, CL (pressure and circulation),
    the inviscid pressure drag and the source and vortex strengths."""
    a = np.radians(alpha_deg)
    xm, ym, length, tx, ty, nx, ny = panel_geometry(X, Y)
    n = len(xm)
    usx, usy, uvx, uvy = influence(X, Y, xm, ym, self_panels=True)
    an, at = usx * nx[:, None] + usy * ny[:, None], usx * tx[:, None] + usy * ty[:, None]
    bn = (uvx * nx[:, None] + uvy * ny[:, None]).sum(axis=1)
    bt = (uvx * tx[:, None] + uvy * ty[:, None]).sum(axis=1)
    fn, ft = np.cos(a) * nx + np.sin(a) * ny, np.cos(a) * tx + np.sin(a) * ty
    if kutta:
        m = np.zeros((n + 1, n + 1))
        m[:n, :n], m[:n, n] = an, bn
        m[n, :n], m[n, n] = at[0] + at[-1], bt[0] + bt[-1]
        sol = np.linalg.solve(m, np.r_[-fn, -(ft[0] + ft[-1])])
        q, gam = sol[:n], sol[n]
    else:
        q, gam = np.linalg.solve(an, -fn), 0.0
    vt = at @ q + bt * gam + ft
    cp = 1.0 - vt**2
    fx, fy = -np.sum(cp * nx * length), -np.sum(cp * ny * length)
    chord = X.max() - X.min()
    return {"cp": cp, "vt": vt, "x": xm, "y": ym, "q": q, "gamma": gam, "length": length,
            "cl": (fy * np.cos(a) - fx * np.sin(a)) / chord,
            "cd_pressure": (fx * np.cos(a) + fy * np.sin(a)) / chord,
            "cl_circulation": 2.0 * gam * length.sum() / chord,
            "source_total": float(np.sum(q * length))}


def airfoil_cl(code, alpha_deg, n=80):
    """Panel-method lift coefficient of a NACA 4-digit airfoil."""
    X, Y = naca4(code, n)
    return solve_panels(X, Y, alpha_deg)["cl"]


def alpha_for_cl(code, cl_target, n=80):
    """Angle (degrees) where the panel CL equals cl_target. CL is linear in alpha for a
    potential flow, so two solutions are enough to place the line exactly."""
    c0, c4 = airfoil_cl(code, 0.0, n), airfoil_cl(code, 4.0, n)
    return 4.0 * (cl_target - c0) / (c4 - c0)


def velocity_field(X, Y, alpha_deg, xp, yp):
    """Velocity (u, v) at any points outside the airfoil (free stream of speed 1)."""
    s = solve_panels(X, Y, alpha_deg)
    usx, usy, uvx, uvy = influence(X, Y, np.ravel(xp), np.ravel(yp))
    a = np.radians(alpha_deg)
    u = np.cos(a) + usx @ s["q"] + uvx.sum(axis=1) * s["gamma"]
    v = np.sin(a) + usy @ s["q"] + uvy.sum(axis=1) * s["gamma"]
    return u.reshape(np.shape(xp)), v.reshape(np.shape(xp))


# %% [markdown]
# ## Step 4: drag needs viscosity
# A potential flow has no friction, so it predicts zero drag on any closed body (d'Alembert's
# paradox); the small `cd_pressure` is only a numerical error. Real drag of a streamlined
# airfoil is mostly skin friction in the thin boundary layer. A classic estimate uses the
# Reynolds number Re = V c / nu, a fully turbulent flat-plate friction law and a form factor
# for the thickness (Hoerner):
#
#     Cf = 0.074 / Re^0.2       cd = 2 Cf (1 + 2 t/c + 60 (t/c)^4)
#
# The factor 2 is for the two surfaces. This is an estimate for small angles only: it does
# not know about laminar flow, separation or stall.

# %%
def reynolds(v, chord, nu=NU_AIR):
    """Reynolds number V c / nu (no unit)."""
    return v * chord / nu


def skin_friction(re):
    """Turbulent flat-plate friction coefficient 0.074 / Re^0.2 (valid roughly 5e5 to 1e7)."""
    if re <= 0:
        raise ValueError("Reynolds number must be positive")
    return 0.074 / re**0.2


def cd_profile(t_over_c, re):
    """Profile drag estimate of an airfoil at small angles (no unit)."""
    return 2.0 * skin_friction(re) * (1 + 2 * t_over_c + 60 * t_over_c**4)


# %% [markdown]
# ## Step 5: the mini-project: choose a wing section
# The 1000 kg aircraft of Session 1 cruises at 50 m/s with a 16 m2 wing and needs CL = 0.40
# (chord 1.5 m, so Re = 5 million). The wing spar needs a section at least 12 % thick, and
# to keep the cabin floor level in cruise the wing should meet the air at 0 to 3 degrees.
# Among the candidates, take the one with the lowest drag that meets both rules.

# %%
def choose_section(candidates, cl_cruise=0.40, re=5e6, t_min=0.12, alpha_range=(0.0, 3.0)):
    """Return (best code or None, table) where each table row is
    (code, alpha for cl_cruise, cd, section L/D, meets rules)."""
    rows = []
    for code in candidates:
        t = int(code[2:]) / 100
        a = alpha_for_cl(code, cl_cruise)
        cd = cd_profile(t, re)
        ok = t >= t_min - 1e-12 and alpha_range[0] <= a <= alpha_range[1]
        rows.append((code, a, cd, cl_cruise / cd, ok))
    good = [r for r in rows if r[4]]
    best = min(good, key=lambda r: r[2])[0] if good else None
    return best, rows


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from matplotlib.path import Path

    OUT.mkdir(exist_ok=True)

    # Worked example: NACA 0012 at 5 degrees, 160 panels
    X, Y = naca4("0012", 80)
    s = solve_panels(X, Y, 5.0)
    thin = 2 * np.pi * np.radians(5.0)
    print(f"NACA 0012, 5 deg: CL = {s['cl']:.4f} (circulation {s['cl_circulation']:.4f}), thin airfoil {thin:.4f}, "
          f"2 pi (1 + 0.77 t/c) alpha = {thin * (1 + 0.77 * 0.12):.4f}, pressure drag {s['cd_pressure']:.5f}")
    re = reynolds(50.0, 1.5)
    print(f"Re = {re:.3g}, Cf = {skin_friction(re):.5f}, cd = {cd_profile(0.12, re):.5f}, "
          f"L/D = {s['cl'] / cd_profile(0.12, re):.1f}")

    # Validation: the circle has an exact answer Cp = 1 - 4 sin^2(theta)
    cx, cy = circle(80)
    sc = solve_panels(cx, cy, 0.0, kutta=False)
    exact = 1 - 4 * np.sin(np.arctan2(sc["y"], sc["x"])) ** 2
    print(f"circle: largest Cp error {np.max(np.abs(sc['cp'] - exact)):.2e}")

    # Figure 1: validation. (left) circle vs exact; (right) CL vs alpha, panel vs thin theory
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    th = np.degrees(np.mod(np.arctan2(sc["y"], sc["x"]), 2 * np.pi))
    order = np.argsort(th)
    tt = np.linspace(0, 360, 200)
    axes[0].plot(tt, 1 - 4 * np.sin(np.radians(tt)) ** 2, "k-", lw=1, label="exact 1 - 4 sin^2")
    axes[0].plot(th[order], sc["cp"][order], "o", ms=3, color="#d9534f", label="panel method, 80 panels")
    axes[0].set_xlabel("angle round the circle (degrees)")
    axes[0].set_ylabel("pressure coefficient Cp (no unit)")
    axes[0].set_title("Validation: flow past a circle")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)
    al = np.arange(-4, 11, 1.0)
    for code, col in (("0012", "#1f6feb"), ("2412", "#2a9d8f"), ("4412", "#d9534f")):
        Xa, Ya = naca4(code, 80)
        axes[1].plot(al, [solve_panels(Xa, Ya, a)["cl"] for a in al], "o-", ms=3, color=col, label=f"NACA {code} panel")
    axes[1].plot(al, 2 * np.pi * np.radians(al), "k--", lw=1, label="thin theory, symmetric")
    axes[1].set_xlabel("angle of attack alpha (degrees)")
    axes[1].set_ylabel("lift coefficient CL (no unit)")
    axes[1].set_title("Panel method: thickness adds a few percent of lift")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "validation.png", dpi=120)

    # Figure 2: pressure distribution and streamlines round NACA 2412 at 4 degrees (the Target)
    X2, Y2 = naca4("2412", 80)
    s2 = solve_panels(X2, Y2, 4.0)
    up = np.arange(len(s2["x"])) >= len(s2["x"]) // 2       # second half of the panels is the upper surface
    fig2, axes = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1, 1.25]})
    axes[0].plot(s2["x"][up], s2["cp"][up], "-", color="#1f6feb", label="upper surface")
    axes[0].plot(s2["x"][~up], s2["cp"][~up], "-", color="#d9534f", label="lower surface")
    axes[0].invert_yaxis()
    axes[0].set_xlabel("x / c (fraction of the chord)")
    axes[0].set_ylabel("pressure coefficient Cp (suction up)")
    axes[0].set_title(f"NACA 2412 at 4 deg: CL = {s2['cl']:.3f}")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)
    gx, gy = np.meshgrid(np.linspace(-0.5, 1.5, 120), np.linspace(-0.6, 0.6, 72))
    u, v = velocity_field(X2, Y2, 4.0, gx, gy)
    inside = Path(np.c_[X2, Y2]).contains_points(np.c_[gx.ravel(), gy.ravel()]).reshape(gx.shape)
    speed = np.ma.masked_where(inside, np.hypot(u, v))
    u, v = np.ma.masked_where(inside, u), np.ma.masked_where(inside, v)
    pc = axes[1].pcolormesh(gx, gy, speed, cmap="coolwarm", vmin=0.4, vmax=1.6, shading="auto")
    axes[1].streamplot(gx, gy, u.filled(np.nan), v.filled(np.nan), color="k", linewidth=0.6, density=1.3, arrowsize=0.6)
    axes[1].fill(X2, Y2, color="0.6")
    axes[1].set_aspect("equal")
    axes[1].set_xlabel("x / c")
    axes[1].set_ylabel("y / c")
    axes[1].set_title("Streamlines and speed V / V_inf")
    fig2.colorbar(pc, ax=axes[1], label="V / V_inf (no unit)", shrink=0.8)
    fig2.tight_layout()
    fig2.savefig(OUT / "pressure_streamlines.png", dpi=120)

    # Figure 3: the mini-project
    cands = ["2408", "2412", "2415", "4412", "0012"]
    best, rows = choose_section(cands)
    for code, a, cd, ld, ok in rows:
        print(f"NACA {code}: alpha for CL 0.40 = {a:5.2f} deg, cd = {cd:.5f}, L/D = {ld:5.1f}, meets rules: {ok}")
    print("chosen section:", best)
    fig3, ax = plt.subplots(figsize=(7.5, 4))
    for k, (code, a, cd, ld, ok) in enumerate(rows):
        ax.bar(k, a, color="#2a9d8f" if ok else "#bbbbbb")
        ax.text(k, max(a, 0) + 0.15, f"cd {cd:.4f}\nL/D {ld:.0f}", ha="center", fontsize=8)
    ax.axhspan(0, 3, color="#2a9d8f", alpha=0.1, label="allowed angle 0 to 3 deg")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels([f"NACA {r[0]}" + (" (chosen)" if r[0] == best else "") for r in rows], fontsize=8)
    ax.set_ylabel("angle for CL = 0.40 (degrees)")
    ax.set_ylim(-1.5, 5.5)
    ax.set_title("Choose a wing section: CL 0.40, t/c at least 12 %, Re = 5 million (grey = rule broken)")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.3, axis="y")
    fig3.tight_layout()
    fig3.savefig(OUT / "choose_section.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The pressure comes from an inviscid model, and the drag from a flat-plate law that does
# not know the pressure. The roadmap couples the two: a boundary layer that grows along the
# surface under the computed pressure, finds where it turns turbulent or separates, and so
# predicts the drag polar and the stall. That is the Target.
