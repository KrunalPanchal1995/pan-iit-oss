"""Session 3 (Level 3): an elastic-plastic model, permanent set, 0.2 percent offset yield, uncertainty.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: simulating loading and unloading, and validating it
# **A. Real-world problem.** Real metals do not have a sharp yield point in a test machine: the
# curve bends smoothly. Engineers therefore *define* yield as the stress where a line parallel to
# the elastic slope, shifted by 0.2 percent strain, meets the curve (the "0.2 percent offset").
# Can we build a curve model, load and unload it, find the offset yield numerically, and check
# every number against a result we can work out by hand?
#
# **Plan.** (1) Ramberg-Osgood curve and a numerical inverse, (2) a one-dimensional plasticity
# solver with strain hardening (return mapping), (3) validation against hand formulas,
# (4) sensitivity to uncertain E and yield, (5) a limit case, (6) the mini-project: estimate E
# and yield from a noisy synthetic tensile test.
#
# *Simplified model: one axis, no necking, no rate or temperature effects, not a design tool.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the Ramberg-Osgood curve
# strain = s/E + 0.002 * (s / s02)^n.  The first term is Hooke's law. The second is the plastic
# strain; it is built so that at s = s02 it equals exactly 0.002 (0.2 percent). So s02 is the
# 0.2 percent offset yield *by construction*, which gives us a clean test for our numerical code.
# n controls how sharp the knee is (large n: sharp, like mild steel; small n: gradual).
# We need stress for a given strain, so we invert the formula by bisection (the strain is
# increasing in stress, so a root always exists).

# %%
def strain_ro(s, e, s02, n):
    s = np.asarray(s, dtype=float)
    return s / e + 0.002 * (s / s02) ** n


def stress_ro(eps, e, s02, n):
    """Invert strain_ro by bisection (works on arrays)."""
    eps = np.atleast_1d(np.asarray(eps, dtype=float))
    lo = np.zeros_like(eps)
    hi = np.full_like(eps, 4.0 * s02)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        above = strain_ro(mid, e, s02, n) > eps
        hi = np.where(above, mid, hi)
        lo = np.where(above, lo, mid)
    return 0.5 * (lo + hi)


def permanent_set_ro(eps_max, e, s02, n):
    """Unloading is elastic with slope E, so the strain left at zero stress is eps_max - s_max/E."""
    s_max = float(stress_ro(eps_max, e, s02, n)[0])
    return eps_max - s_max / e


# %% [markdown]
# ## Step 2: a plasticity solver with hardening (bilinear)
# We also keep a simpler bilinear metal: elastic slope E, then slope H after yield sy. A solver
# that walks along any strain path needs memory, because unloading follows a different line than
# loading. State: plastic strain `ep` and accumulated plastic strain `alpha`.
# At each step: trial stress s = E (eps - ep). If |s| exceeds the current yield
# sy + Hp*alpha, push the state back to the yield surface (return mapping), where
# Hp = E H / (E - H) is the plastic modulus that gives overall slope H.

# %%
def bilinear_path(strain_path, e, sy, h):
    """Stress for each strain of an arbitrary path (loading, unloading, reloading)."""
    hp = e * h / (e - h)
    ep, alpha, out = 0.0, 0.0, []
    for eps in strain_path:
        s_trial = e * (eps - ep)
        f = abs(s_trial) - (sy + hp * alpha)
        if f > 0.0:
            dg = f / (e + hp)
            ep += np.sign(s_trial) * dg
            alpha += dg
            s_trial = e * (eps - ep)
        out.append(s_trial)
    return np.array(out)


def load_unload_path(eps_max, n=200):
    return np.concatenate([np.linspace(0.0, eps_max, n), np.linspace(eps_max, 0.0, n)[1:]])


# %% [markdown]
# ## Step 3: validate against hand formulas
# For the bilinear metal loaded to eps_max > sy/E the exact answers are:
# * stress at the top: s_max = sy + H (eps_max - sy/E)
# * unloading slope: E
# * strain left at zero stress: eps_max - s_max/E.
#
# For the Ramberg-Osgood curve the 0.2 percent offset yield must come back as s02, and the
# initial slope as E. `offset_yield` finds the crossing of the data with the offset line.

# %%
def offset_yield(eps, s, e, offset=0.002, start_frac=0.2):
    """Stress where the curve meets the line s = E (eps - offset). Linear interpolation."""
    eps, s = np.asarray(eps), np.asarray(s)
    g = s - e * (eps - offset)
    i0 = int(np.argmax(s > start_frac * s.max()))
    idx = np.nonzero((g[i0:-1] > 0) & (g[i0 + 1:] <= 0))[0]
    if len(idx) == 0:
        return float("nan")
    i = i0 + idx[0]
    t = g[i] / (g[i] - g[i + 1])
    return float(s[i] + t * (s[i + 1] - s[i]))


# %% [markdown]
# ## Step 4: sensitivity to uncertain inputs
# Published E and yield are typical values; a real batch scatters. For the Session 2 steel bar
# (20 kN, 2 m, d = 16 mm) we vary one input at a time by plus and minus 10 percent.
# Extension is proportional to 1/E; factor of safety is proportional to sy.

# %%
def bar_response(e, sy, d_mm=16.0, force_kn=20.0, length_mm=2000.0):
    a = np.pi * d_mm ** 2 / 4.0
    s = force_kn * 1000.0 / a
    return {"ext": s * length_mm / e, "fos": sy / s}


def sensitivity(e=200000.0, sy=250.0, frac=0.10):
    base = bar_response(e, sy)
    rows = {}
    cases = {"E -10%": (e * (1 - frac), sy), "E +10%": (e * (1 + frac), sy),
             "yield -10%": (e, sy * (1 - frac)), "yield +10%": (e, sy * (1 + frac))}
    for name, (ee, ss) in cases.items():
        r = bar_response(ee, ss)
        rows[name] = (100 * (r["ext"] / base["ext"] - 1), 100 * (r["fos"] / base["fos"] - 1))
    return base, rows


# %% [markdown]
# ## Step 5: mini-project helpers, a synthetic tensile test
# `synthetic_test` makes stress-strain data from a hidden "true" material plus measurement noise.
# `fit_modulus` fits a straight line to the low-stress part; `offset_yield` (above) finds yield.
# The real project is to choose the fit window well and report E and yield with an error.

# %%
TRUE_E, TRUE_S02, TRUE_N = 205000.0, 310.0, 12.0


def synthetic_test(seed=0, noise_mpa=2.0, noise_strain=1e-5, emax=0.03, npts=1000):
    rng = np.random.default_rng(seed)
    eps_true = np.linspace(0.0, emax, npts)
    s_true = stress_ro(eps_true, TRUE_E, TRUE_S02, TRUE_N)
    return eps_true + rng.normal(0.0, noise_strain, npts), s_true + rng.normal(0.0, noise_mpa, npts)


def fit_modulus(eps, s, lo=0.10, hi=0.50):
    """Slope of a least-squares line through points with stress between lo and hi of the peak."""
    m = (s > lo * s.max()) & (s < hi * s.max())
    return float(np.polyfit(eps[m], s[m], 1)[0])


def estimate(seed=0):
    eps, s = synthetic_test(seed)
    e_fit = fit_modulus(eps, s)
    return e_fit, offset_yield(eps, s, e_fit)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    e, s02, n = 200000.0, 250.0, 10.0
    eps = np.linspace(0.0, 0.02, 801)
    s = stress_ro(eps, e, s02, n)
    print(f"offset yield from the numbers: {offset_yield(eps, s, e):.2f} MPa (s02 = {s02})")
    sl = (s[1] - s[0]) / (eps[1] - eps[0])
    print(f"initial slope: {sl / 1000:.1f} GPa (E = {e / 1000:.0f} GPa)")

    eps_max = 0.008
    smax = float(stress_ro(eps_max, e, s02, n)[0])
    ps = permanent_set_ro(eps_max, e, s02, n)
    print(f"load to {eps_max:.3%}: stress {smax:.1f} MPa, permanent set {ps:.5f} ({ps:.3%})")

    be, bsy, bh = 70000.0, 200.0, 7000.0
    path = load_unload_path(0.02)
    bs = bilinear_path(path, be, bsy, bh)
    exact_top = bsy + bh * (0.02 - bsy / be)
    left = 0.02 - exact_top / be
    k = 199 + int(np.argmax(bs[199:] <= 0.0))
    left_num = path[k - 1] + (path[k] - path[k - 1]) * bs[k - 1] / (bs[k - 1] - bs[k])
    print(f"bilinear solver top {bs[199]:.2f} MPa (exact {exact_top:.2f}); "
          f"strain left at zero stress {left_num:.5f} (exact {left:.5f})")

    base, rows = sensitivity()
    print(f"steel bar: extension {base['ext']:.3f} mm, FoS {base['fos']:.2f}")
    for k, (de, df) in rows.items():
        print(f"  {k:11s}: extension {de:+6.1f} %, FoS {df:+6.1f} %")

    for nn in (3, 10, 50):
        print(f"n = {nn:2d}: stress at 5% strain = {stress_ro(0.05, e, s02, nn)[0]:.1f} MPa")

    rs = np.array([estimate(k) for k in range(20)])
    print(f"20 synthetic tests: E mean {rs[:, 0].mean() / 1000:.1f} GPa "
          f"(max error {abs(rs[:, 0] / TRUE_E - 1).max():.2%}), yield mean {rs[:, 1].mean():.1f} MPa "
          f"(max error {abs(rs[:, 1] / TRUE_S02 - 1).max():.2%})")

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(eps * 100, s, "C0", lw=2, label="Ramberg-Osgood curve")
    ax.plot([ps * 100, eps_max * 100], [0, smax], "C3", lw=2, label="unloading (slope E)")
    ax.plot([ps * 100], [0], "ko")
    ax.annotate("permanent set", (ps * 100, 0), textcoords="offset points", xytext=(6, 10))
    xs = np.array([0.2, 1.2])
    ax.plot(xs, e * (xs / 100 - 0.002), "k--", lw=1, label="0.2% offset line")
    ax.plot([0.2 + s02 / e * 100], [s02], "s", color="C2", label=f"offset yield {s02:.0f} MPa")
    ax.set_xlim(0, 1.2)
    ax.set_ylim(0, 340)
    ax.set_xlabel("strain (percent)")
    ax.set_ylabel("stress (MPa)")
    ax.set_title("Load, unload, and the 0.2 percent offset yield")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "load_unload.png", dpi=120)

    e1, y1 = synthetic_test(1)
    efit = fit_modulus(e1, y1)
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.plot(e1 * 100, y1, ".", ms=3, color="C7", label="synthetic noisy data")
    ax2.plot(e1 * 100, stress_ro(np.clip(e1, 0, None), TRUE_E, TRUE_S02, TRUE_N), "C0", lw=1, label="hidden true curve")
    xx = np.array([0.2, 1.0])
    ax2.plot(xx, efit * (xx / 100 - 0.002), "k--", lw=1, label=f"offset line, E fit {efit / 1000:.0f} GPa")
    yfit = offset_yield(e1, y1, efit)
    ax2.plot([0.2 + yfit / efit * 100], [yfit], "s", color="C3", label=f"offset yield {yfit:.0f} MPa")
    ax2.set_xlim(0, 1.5)
    ax2.set_ylim(0, 450)
    ax2.set_xlabel("strain (percent)")
    ax2.set_ylabel("stress (MPa)")
    ax2.set_title("Mini-project: estimate E and yield from noisy data")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8, loc="lower right")
    fig2.tight_layout()
    fig2.savefig(OUT / "noisy_test.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Where this stops
# After the ultimate strength a real specimen necks and the engineering stress falls; this model
# keeps rising. It also ignores strain rate, temperature, fatigue and the 3D state of stress.
