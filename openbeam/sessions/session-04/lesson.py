"""Session 4 (Level 3): the envelope of shear and moment as a load group crosses a span.

Educational model only. Never use it to design or assess a real bridge.
Run:  python start.py 4
"""
# %% [markdown]
# # Session 4: a load that moves
# **A. Real-world problem.** A lorry crosses a bridge. The bending moment at mid-span is not
# one number: it changes as the axles roll along, and every section of the beam has its own
# worst moment at its own worst position. The *envelope* is the curve of the worst value at
# every section. Designing for one fixed position can be too small (the wrong place) or too
# large (both axles at mid-span, which cannot happen). We build the envelope by sweeping the
# load group along the span, check it against two independent routes (influence lines and a
# closed-form worst position), and then use it to choose a girder.
#
# **Plan.** (1) statics of a group of point loads, (2) influence lines as an independent route,
# (3) sweep the group and record the envelope, (4) the worst position by hand, (5) stress and
# deflection limits, then pick the lightest girder.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G_ACC = 9.81      # m/s^2
RHO = 7850.0      # steel density, kg/m^3


# %% [markdown]
# ## Step 1: statics of a group of point loads
# A *group* is a list of `(offset, P)` pairs: the load P (N, downward) of each axle and its
# distance `offset` (m) ahead of the rear axle. The group's position `s` is where the rear axle
# is on the beam, so axle i is at `x_i = s + offset_i`. Only axles with 0 <= x_i <= L are on the
# span (an axle outside carries no load into this beam). For a simply supported span of length L:
#
#     R_A = sum P_i (L - x_i) / L,    R_B = sum P_i x_i / L
#     V(x) = R_A - (loads to the left of x),   M(x) = R_A x - sum over left loads of P_i (x - x_i)
#
# Shear V is taken just to the right of the section; the moment is positive when it sags.

# %%
def make_group(loads, spacings):
    """Group from axle loads (N) and the gaps between neighbouring axles (m): offsets start at 0."""
    loads = [float(p) for p in loads]
    if not loads or len(spacings) != len(loads) - 1:
        raise ValueError("need one load per axle and one spacing between each pair of axles")
    if any(p < 0 for p in loads) or any(d <= 0 for d in spacings):
        raise ValueError("loads must not be negative and spacings must be positive")
    off = np.concatenate([[0.0], np.cumsum(spacings)])
    return [(float(o), p) for o, p in zip(off, loads)]


def _axles(group, s, L):
    """Positions and loads of the axles that are on the span when the rear axle is at s."""
    xs = np.array([s + o for o, _ in group])
    ps = np.array([p for _, p in group])
    on = (xs >= 0.0) & (xs <= L)
    return xs[on], ps[on]


def reactions(group, s, L):
    xs, ps = _axles(group, s, L)
    return float(np.sum(ps * (L - xs)) / L), float(np.sum(ps * xs) / L)


def shear(x, group, s, L):
    """Shear just right of the section at x (N), for the group at position s."""
    xs, ps = _axles(group, s, L)
    ra = np.sum(ps * (L - xs)) / L
    return float(ra - np.sum(ps[xs <= x]))


def moment(x, group, s, L):
    """Sagging bending moment (N m) at the section x, for the group at position s."""
    xs, ps = _axles(group, s, L)
    ra = np.sum(ps * (L - xs)) / L
    left = xs <= x
    return float(ra * x - np.sum(ps[left] * (x - xs[left])))


# %% [markdown]
# ## Step 2: influence lines, an independent route
# Put a *unit* load at position xi and ask what it does at one fixed section x. The answer, as a
# function of xi, is the influence line. For a simply supported beam:
#
#     moment at x:   eta_M(x, xi) = xi (L - x) / L   for xi <= x,    x (L - xi) / L   for xi > x
#     shear just right of x:   eta_V(x, xi) = -xi / L   for xi <= x,    (L - xi) / L   for xi > x
#
# The effect of a group is then the sum of load times influence ordinate over the axles on the
# beam. It uses no reactions and no free-body diagram, so it is a genuine second opinion on Step 1.

# %%
def influence_moment(x, xi, L):
    xi = np.asarray(xi, dtype=float)
    return np.where(xi <= x, xi * (L - x) / L, x * (L - xi) / L)


def influence_shear(x, xi, L):
    xi = np.asarray(xi, dtype=float)
    return np.where(xi <= x, -xi / L, (L - xi) / L)


def moment_by_influence(x, group, s, L):
    xs, ps = _axles(group, s, L)
    return float(np.sum(ps * influence_moment(x, xs, L)))


def shear_by_influence(x, group, s, L):
    xs, ps = _axles(group, s, L)
    return float(np.sum(ps * influence_shear(x, xs, L)))


# %% [markdown]
# ## Step 3: sweep the group and record the envelope
# Move the rear axle from just before the beam (so the first axle is about to enter) to just
# after the last axle has left, in small steps `ds`. At every position compute M and V at a row
# of sections and keep, section by section, the largest value (and for shear also the most
# negative one). With `both_directions=True` the group is also driven the other way round,
# because a lorry can cross in either direction.

# %%
def _sweep_arrays(group, L, nx, ds, mirrored=False):
    offs = np.array([o for o, _ in group])
    ps = np.array([p for _, p in group])
    if mirrored:                                   # the same vehicle driving the other way
        offs = offs.max() - offs[::-1]
        ps = ps[::-1]
    x = np.linspace(0.0, L, nx)
    s = np.arange(-offs.max(), L + ds * 0.5, ds)
    X = s[:, None] + offs[None, :]                  # axle positions, shape (positions, axles)
    on = (X >= 0.0) & (X <= L)
    Pm = np.where(on, ps[None, :], 0.0)
    ra = np.sum(Pm * (L - X), axis=1) / L
    M = np.zeros((len(s), nx))
    V = np.zeros((len(s), nx))
    for k in range(len(offs)):
        xk, pk = X[:, k][:, None], Pm[:, k][:, None]
        left = xk <= x[None, :]
        M += pk * np.where(left, xk * (L - x[None, :]) / L, x[None, :] * (L - xk) / L)
        V += pk * np.where(left, -xk / L, (L - xk) / L)
    return x, s, M, V


def envelope(group, L, nx=241, ds=0.01, both_directions=True):
    """Envelope of a load group crossing a simply supported span.

    Returns a dict with x, M_max (largest sagging moment at each section), V_max and V_min
    (largest and most negative shear), and where the overall peak moment happens:
    peak_M (N m), x_peak (m) and s_peak (position of the rear axle then)."""
    parts = [_sweep_arrays(group, L, nx, ds, False)]
    if both_directions:
        parts.append(_sweep_arrays(group, L, nx, ds, True))
    x = parts[0][0]
    M_max = np.max([p[2].max(axis=0) for p in parts], axis=0)
    V_max = np.max([p[3].max(axis=0) for p in parts], axis=0)
    V_min = np.min([p[3].min(axis=0) for p in parts], axis=0)
    j = int(np.argmax(M_max))
    i = int(np.argmax(parts[0][2][:, j])) if parts[0][2][:, j].max() >= M_max[j] - 1e-9 else int(np.argmax(parts[-1][2][:, j]))
    return {"x": x, "M_max": M_max, "V_max": V_max, "V_min": V_min, "peak_M": float(M_max[j]),
            "x_peak": float(x[j]), "s_peak": float(parts[0][1][i])}


# %% [markdown]
# ## Step 4: the worst position by hand
# The largest moment of all happens under one axle, when that axle and the *resultant* of the
# loads on the span are the same distance from mid-span, on opposite sides. (Put the resultant at
# distance e from the axle in question; the axle goes at L/2 - e/2 and the resultant at L/2 + e/2.)
# Axles that would then lie off the beam are dropped and the position is recomputed until the
# set of axles on the beam stops changing. For two equal loads P a distance d apart:
#
#     M_peak = P (L - d/2)^2 / (2 L)     (needs d <= 2 L / 3; the second axle is then on the span)
#
# and a single axle at mid-span gives P L / 4. The two formulas cross at d = 2 L (1 - 1/sqrt 2),
# about 0.586 L: for wider spacing the axles never help each other, and the larger of the two
# values is the answer.

# %%
def worst_moment_by_hand(group, L):
    """Largest moment (N m) of a group crossing a simply supported span, from the equal-distance rule.

    Returns (moment, rear-axle position s, section x). Checks the rule for each axle in turn."""
    offs = np.array([o for o, _ in group])
    ps = np.array([p for _, p in group])
    best = (0.0, 0.0, 0.0)
    for forward in (True, False):
        o = offs if forward else offs.max() - offs[::-1]
        p = ps if forward else ps[::-1]
        for i in range(len(o)):
            keep = np.ones(len(o), dtype=bool)
            for _ in range(len(o) + 1):
                R = p[keep].sum()
                if R == 0:
                    break
                e = (np.sum(p[keep] * o[keep]) / R) - o[i]          # resultant ahead of axle i by e
                xi_ = L / 2 - e / 2                                  # position of axle i
                pos = xi_ + (o - o[i])                               # all axles
                new = (pos >= -1e-12) & (pos <= L + 1e-12)
                if np.array_equal(new, keep):
                    break
                keep = new
            if not keep[i]:
                continue
            xs = xi_ + (o[keep] - o[i])
            Pk = p[keep]
            ra = np.sum(Pk * (L - xs)) / L
            m = ra * xi_ - np.sum(Pk[xs < xi_] * (xi_ - xs[xs < xi_]))
            if m > best[0]:
                best = (float(m), float(xi_ - o[i]), float(xi_))
    return best


def two_axle_peak(P, d, L):
    """Hand value for two equal loads P a distance d apart: the larger of P(L - d/2)^2/(2L) and P L/4."""
    return max(P * (L - d / 2) ** 2 / (2 * L), P * L / 4)


def support_shear_peak(group, L):
    """Largest shear next to a support (N): the left reaction with the heaviest arrangement."""
    return float(max(max(reactions(group, s, L)) for s in np.arange(-max(o for o, _ in group), L + 0.005, 0.005)))


# %% [markdown]
# ## Step 5: stress and deflection limits for a girder
# Take a symmetric I-section (flanges `bf` x `tf`, web `tw`, depth `h`, all in m). Bending stress
# is sigma = M c / I with c = h / 2. Dead load (the girder's own weight and the deck, a uniform
# load w in N/m) adds the moment w x (L - x) / 2 at every section, so the design moment at section
# x is envelope(x) + w x (L - x) / 2, and the largest of those over x governs. The mid-span
# deflection of the moving load uses the influence line of mid-span deflection,
#
#     eta_w(xi) = xi (3 L^2 - 4 xi^2) / (48 E I)   for xi <= L/2  (mirrored for xi > L/2),
#
# summed over the axles; the worst position is found by sweeping.

# %%
def isection_props(bf, tf, tw, h):
    """Area (m^2) and second moment of area (m^4) of a symmetric I-section."""
    hw = h - 2 * tf
    A = 2 * bf * tf + hw * tw
    I = (bf * h ** 3 - (bf - tw) * hw ** 3) / 12.0
    return A, I


def midspan_deflection(group, s, L, EI):
    xs, ps = _axles(group, s, L)
    xi = np.minimum(xs, L - xs)
    return float(np.sum(ps * xi * (3 * L ** 2 - 4 * xi ** 2) / (48 * EI)))


def max_midspan_deflection(group, L, EI, ds=0.005):
    offs = max(o for o, _ in group)
    return max(midspan_deflection(group, s, L, EI) for s in np.arange(-offs, L + ds * 0.5, ds))


def check_girder(group, L, section, E=200e9, sigma_y=250e6, fos=1.5, deck_w=0.0, defl_ratio=360.0,
                 env=None):
    """Stress and deflection check of a steel girder under a moving load group plus a uniform load.

    section = (bf, tf, tw, h) in m; deck_w is the uniform load (N/m) in addition to the girder's own weight.
    The deflection limit applies to the moving load only. Returns a dict."""
    A, I = isection_props(*section)
    w = deck_w + RHO * G_ACC * A
    env = envelope(group, L) if env is None else env
    x = env["x"]
    m_tot = env["M_max"] + w * x * (L - x) / 2
    M = float(m_tot.max())
    sigma = M * (section[3] / 2) / I
    defl = max_midspan_deflection(group, L, E * I)
    ok_stress = fos * sigma <= sigma_y
    ok_defl = defl <= L / defl_ratio
    return {"M": M, "x_M": float(x[int(np.argmax(m_tot))]), "sigma": sigma, "defl": defl, "limit": L / defl_ratio,
            "mass": RHO * A, "ok_stress": bool(ok_stress), "ok_defl": bool(ok_defl),
            "ok": bool(ok_stress and ok_defl), "w": w}


def lightest_depth(group, L, bf, tf, tw, depths, fixed_moment=None, **kw):
    """Lightest passing depth (m) of the family, or None. With fixed_moment (N m) the live-load
    envelope is replaced by that single moment at mid-span (a naive design) for comparison."""
    env = envelope(group, L)
    if fixed_moment is not None:
        env = dict(env)
        env["M_max"] = np.where(np.abs(env["x"] - L / 2) < 1e-9, fixed_moment, 0.0)
    for h in depths:
        r = check_girder(group, L, (bf, tf, tw, h), env=env, **kw)
        if r["ok"]:
            return float(h), r
    return None


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    L, P, d = 12.0, 10e3, 3.0
    grp = make_group([P, P], [d])
    env = envelope(grp, L)
    hand = two_axle_peak(P, d, L)
    print(f"two axles 2 x 10 kN, {d:g} m apart, L = {L:g} m: sweep peak {env['peak_M'] / 1e3:.3f} kN m at x = {env['x_peak']:.2f} m "
          f"(rear axle at {env['s_peak']:.2f} m); hand value {hand / 1e3:.3f} kN m")
    print(f"naive: both axles at mid-span {2 * P * L / 4 / 1e3:.1f} kN m; one axle at mid-span {P * L / 4 / 1e3:.1f} kN m")
    print(f"support shear peak {support_shear_peak(grp, L) / 1e3:.2f} kN (hand P (2L - d) / L = {P * (2 * L - d) / L / 1e3:.2f} kN)")

    # figure 1: snapshots and envelope
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    xx = np.linspace(0, L, 241)
    ax[0].fill_between(xx, 0, env["M_max"] / 1e3, color="#003f7f", alpha=0.15, label="envelope")
    ax[0].plot(xx, env["M_max"] / 1e3, color="#003f7f", lw=2)
    for s, col in ((2.0, "#c86a00"), (5.25 - 0.0, "#d81b60"), (7.0, "#5b6472")):
        ax[0].plot(xx, [moment(v, grp, s, L) / 1e3 for v in xx], color=col, lw=1.4, label=f"rear axle at {s:g} m")
    ax[0].set_xlabel("section x along the span (m)")
    ax[0].set_ylabel("bending moment (kN m)")
    ax[0].set_title(f"Moment envelope, peak {env['peak_M'] / 1e3:.1f} kN m at x = {env['x_peak']:.2f} m", fontsize=10)
    ax[0].legend(fontsize=8)
    ax[0].grid(alpha=0.3)
    ax[1].fill_between(xx, env["V_min"] / 1e3, env["V_max"] / 1e3, color="#003f7f", alpha=0.15)
    ax[1].plot(xx, env["V_max"] / 1e3, color="#003f7f", lw=2, label="largest shear")
    ax[1].plot(xx, env["V_min"] / 1e3, color="#c86a00", lw=2, label="most negative shear")
    ax[1].axhline(0, color="k", lw=0.8)
    ax[1].set_xlabel("section x along the span (m)")
    ax[1].set_ylabel("shear force (kN)")
    ax[1].set_title("Shear envelope: largest at the supports", fontsize=10)
    ax[1].legend(fontsize=8)
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "moment_shear_envelope.png", dpi=120)

    # figure 2: peak moment against axle spacing, sweep dots against hand formula
    ds_list = np.linspace(0.5, 12.0, 24)
    peaks = [envelope(make_group([P, P], [dd]), L, nx=121, ds=0.02)["peak_M"] / 1e3 for dd in ds_list]
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    dd = np.linspace(0.0, 12.0, 200)
    ax2.plot(dd, [two_axle_peak(P, v, L) / 1e3 for v in dd], color="#003f7f", lw=2, label="hand value: larger of the two formulas")
    ax2.plot(ds_list, peaks, "o", color="#c86a00", label="sweep")
    ax2.axhline(P * L / 4 / 1e3, color="gray", ls=":", label="one axle at mid-span, P L / 4")
    ax2.axvline(2 * L * (1 - 1 / np.sqrt(2)), color="gray", ls="--")
    ax2.text(2 * L * (1 - 1 / np.sqrt(2)) + 0.1, 33.0, "d = 0.586 L", fontsize=8)
    ax2.set_xlabel("axle spacing d (m)")
    ax2.set_ylabel("peak moment of the envelope (kN m)")
    ax2.set_title("Close axles help each other; far apart they do not", fontsize=10)
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "peak_vs_spacing.png", dpi=120)

    # mini-project: girder for the 12 m span
    depths = np.arange(0.15, 0.801, 0.01)
    bf, tf, tw = 0.15, 0.010, 0.006
    kw = dict(deck_w=3000.0, fos=1.5)
    print("girder for the 12 m span, flanges 150 x 10 mm, web 6 mm, deck 3 kN/m, fos 1.5, deflection limit L/360:")
    for name, fm in (("envelope (correct)", None), ("both axles at mid-span (too much)", 2 * P * L / 4), ("one axle at mid-span (too little)", P * L / 4)):
        h, r = lightest_depth(grp, L, bf, tf, tw, depths, fixed_moment=fm, **kw)
        true = check_girder(grp, L, (bf, tf, tw, h), **kw)
        print(f"  {name:36s} h = {1e3 * h:4.0f} mm, mass {r['mass']:.1f} kg/m; checked against the true envelope: stress {true['sigma'] / 1e6:.1f} MPa, "
              f"M {true['M'] / 1e3:.1f} kN m, {'PASS' if true['ok'] else 'FAIL'}")
    for h in depths[::5]:
        r = check_girder(grp, L, (bf, tf, tw, h), **kw)
        print(f"  h = {1e3 * h:4.0f} mm: M {r['M'] / 1e3:5.1f} kN m  stress {r['sigma'] / 1e6:6.1f} MPa  defl {1e3 * r['defl']:5.1f} mm  {'PASS' if r['ok'] else 'FAIL'}")

# %% [markdown]
# ## Where this stops
# One simply supported span, point axles, no impact factor, no lane loading, no lateral
# distribution between girders, no fatigue. Real bridge design codes specify the vehicles and
# the safety factors; this is a classroom model of the idea of an envelope.
