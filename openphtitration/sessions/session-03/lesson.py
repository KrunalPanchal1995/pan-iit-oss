"""Session 3 (Level 3): weak-acid titration by solving the charge balance, with validation.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: titrating a weak acid, and finding the endpoint from noisy data
# **A. Real-world problem.** Vinegar is a weak acid (acetic acid). Its titration curve is not
# the strong-acid curve: it starts higher, has a flat "buffer" stretch, and its equivalence
# point is above pH 7. A real burette reading is also noisy. How do we compute the whole curve,
# check it against simple formulas, and still find the equivalence point from messy data?
#
# **Safety.** Real acids, bases and vinegar solutions need supervision; this is a simulation.
#
# **Plan.** (1) Ka and the charge balance, (2) a bisection root finder, (3) check against
# Henderson-Hasselbalch and half-equivalence, (4) buffer capacity, (5) noise and the
# derivative peak, (6) a failure case, very dilute acids, (7) the vinegar mini-project.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
KW = 1e-14                 # ion product of water at 25 C, (mol/L)^2
KA_ACETIC = 1.8e-5         # acid dissociation constant of acetic acid (standard value), mol/L
PKA_ACETIC = -np.log10(KA_ACETIC)


# %% [markdown]
# ## Step 1: the charge balance
# A weak acid HA only partly splits: `HA <-> H+ + A-`, with `Ka = [H+][A-]/[HA]`.
# Let `Ct` be the total acid ([HA] + [A-]) and `Na` the concentration of sodium ions from the
# base. The solution has no net charge, so
#
#     Na + [H+] = [OH-] + [A-]      with  [OH-] = Kw/[H+]  and  [A-] = Ct Ka / (Ka + [H+])
#
# This is one equation for one unknown, [H+]. We solve it numerically, with no formula for
# the root: bisection on the pH.

# %%
def bisect(f, lo, hi, tol=1e-12, max_iter=200):
    """Root of f between lo and hi by bisection; f(lo) and f(hi) must have opposite signs."""
    flo, fhi = f(lo), f(hi)
    if flo == 0:
        return lo
    if fhi == 0:
        return hi
    if flo * fhi > 0:
        raise ValueError("no sign change: the root is not bracketed")
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if fm == 0 or (hi - lo) < tol:
            return mid
        if flo * fm < 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
    return 0.5 * (lo + hi)


def charge_residual(ph, Ct, Na, pka):
    """Left side minus right side of the charge balance at this pH (mol/L).
    pka=None means a strong acid (fully split)."""
    h = 10.0 ** (-ph)
    a = Ct if pka is None else Ct * 10.0 ** (-pka) / (10.0 ** (-pka) + h)
    return Na + h - KW / h - a


def solve_ph(Ct, Na, pka=None):
    """pH from the total acid concentration Ct and sodium concentration Na (both mol/L)."""
    return bisect(lambda ph: charge_residual(ph, Ct, Na, pka), -2.0, 16.0)


def weak_ph(Ca, Va, Cb, Vb, pka=None):
    """pH after adding Vb mL of strong base (Cb) to Va mL of acid (Ca), by the charge balance.
    With pka=None the acid is strong (this reproduces Session 2)."""
    vt = Va + Vb
    return solve_ph(Ca * Va / vt, Cb * Vb / vt, pka)


def equivalence_volume(Ca, Va, Cb):
    return Ca * Va / Cb


# %% [markdown]
# ## Step 2: the Henderson-Hasselbalch shortcut
# When the flask holds both HA and A- (between the start and the equivalence point), the
# charge balance is approximately `pH = pKa + log10([A-]/[HA])`. Mole counts replace
# concentrations because both share the same volume:
# `n(A-) = Cb Vb` and `n(HA) = Ca Va - Cb Vb`. At half-equivalence they are equal, so pH = pKa.

# %%
def henderson_hasselbalch(Ca, Va, Cb, Vb, pka):
    n_base = Cb * Vb
    n_acid = Ca * Va - n_base
    return pka + np.log10(n_base / n_acid)


def pure_weak_acid_ph(C, pka):
    """pH of C mol/L of a weak acid alone (no base), from the same solver."""
    return solve_ph(C, 0.0, pka)


# %% [markdown]
# ## Step 3: buffer capacity
# How much base does it take to move the pH by one unit? `beta = d(Na)/d(pH)`, in mol/L per pH
# unit. The textbook (Van Slyke) formula is
# `beta = ln(10) ( [H+] + [OH-] + Ct Ka [H+] / (Ka + [H+])^2 )`.
# We compare it with a numerical derivative taken from the root finder. Largest value: at
# pH = pKa the last term is Ct/4, so beta = ln(10) Ct / 4 (about 0.576 Ct).

# %%
def beta_formula(ph, Ct, pka):
    h = 10.0 ** (-ph)
    ka = 10.0 ** (-pka)
    return np.log(10.0) * (h + KW / h + Ct * ka * h / (ka + h) ** 2)


def beta_numeric(Ct, Na, pka, dn=1e-6):
    """Numerical beta: tiny extra base dn (mol/L) divided by the pH change it causes."""
    return 2 * dn / (solve_ph(Ct, Na + dn, pka) - solve_ph(Ct, Na - dn, pka))


# %% [markdown]
# ## Step 4: noisy data and the derivative peak
# A real run has a reading error on the burette volume and on the pH meter. The equivalence
# point is where the curve is steepest, so we find the maximum of `dpH/dV`. We use the slopes
# between neighbouring points and refine the peak with a parabola through its three highest
# slopes.

# %%
def make_data(Ca, Va, Cb, pka, vmax, step, sd_volume=0.0, sd_ph=0.0, seed=0):
    """Synthetic run: the true curve, with Gaussian noise on the volume reading (mL) and the pH."""
    rng = np.random.default_rng(seed)
    v_true = np.arange(0.0, vmax + 1e-9, step)
    ph = np.array([weak_ph(Ca, Va, Cb, v, pka) for v in v_true])
    return v_true + rng.normal(0, sd_volume, v_true.size), ph + rng.normal(0, sd_ph, v_true.size)


def find_equivalence(v, ph):
    """Equivalence volume from the maximum of the first derivative dpH/dV."""
    order = np.argsort(v)
    v, ph = np.asarray(v)[order], np.asarray(ph)[order]
    dv = np.diff(v)
    keep = dv > 1e-9
    slope = np.diff(ph)[keep] / dv[keep]
    mid = 0.5 * (v[:-1] + v[1:])[keep]
    i = int(np.argmax(slope))
    if 0 < i < slope.size - 1:
        c = np.polyfit(mid[i - 1:i + 2], slope[i - 1:i + 2], 2)
        if c[0] < 0:
            vertex = -c[1] / (2 * c[0])
            if mid[i - 1] <= vertex <= mid[i + 1]:
                return float(vertex)
    return float(mid[i])


# %% [markdown]
# ## Step 5: a failure case, and the mini-project
# Ignoring water gives `pH = -log10(C)` for a strong acid. For C = 1e-8 mol/L that predicts
# pH 8, a basic acid, which is absurd: water itself supplies 1e-7 mol/L of H+. The charge
# balance already contains water, so the solver gets it right.
#
# Mini-project: vinegar is about 5 g of acetic acid per 100 mL; with molar mass 60.05 g/mol
# that is 50 / 60.05 = 0.833 mol/L. We dilute 10.00 mL to 100.00 mL, titrate 25.00 mL
# with 0.1000 mol/L NaOH, and work backwards.

# %%
def naive_strong_ph(C):
    """The textbook shortcut that ignores water: wrong for very dilute acids."""
    return -np.log10(C)


def vinegar_concentration(ve, cb=0.1, va=25.0, dilution=10.0):
    """Acetic acid concentration of the original vinegar (mol/L) from the endpoint ve (mL)."""
    return cb * ve / va * dilution


def vinegar_percent(c_mol_per_l, molar_mass=60.05):
    """Mass of acetic acid per 100 mL of vinegar (g/100 mL) from its concentration."""
    return c_mol_per_l * molar_mass / 10.0


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    Ca, Va, Cb, pka = 0.1, 25.0, 0.1, PKA_ACETIC
    ve = equivalence_volume(Ca, Va, Cb)
    print(f"pKa of acetic acid = {pka:.4f};  Ve = {ve} mL")

    # --- curve versus strong acid, HH comparison
    vb = np.linspace(0.0, 50.0, 401)
    weak = np.array([weak_ph(Ca, Va, Cb, v, pka) for v in vb])
    strong = np.array([weak_ph(Ca, Va, Cb, v, None) for v in vb])
    print(f"start pH weak {weak[0]:.3f} (strong {strong[0]:.3f});  half-equivalence pH {weak_ph(Ca, Va, Cb, ve / 2, pka):.4f} "
          f"(pKa {pka:.4f});  equivalence pH {weak_ph(Ca, Va, Cb, ve, pka):.3f};  at 30 mL {weak_ph(Ca, Va, Cb, 30.0, pka):.3f}")
    print("Henderson-Hasselbalch against exact:")
    vs = np.array([1.0, 2.5, 5.0, 12.5, 20.0, 23.0, 24.5])
    hh_ph = henderson_hasselbalch(Ca, Va, Cb, vs, pka)
    for v, h in zip(vs, hh_ph):
        print(f"  Vb {v:5.1f} mL  exact {weak_ph(Ca, Va, Cb, v, pka):.3f}  HH {h:.3f}  diff {h - weak_ph(Ca, Va, Cb, v, pka):+.3f}")

    fig, ax = plt.subplots(figsize=(7, 4.6))
    ax.plot(vb, strong, "--", color="gray", label="strong acid (same concentration)")
    ax.plot(vb, weak, color="tab:red", lw=2, label="acetic acid (exact charge balance)")
    vv = np.linspace(1.0, 24.5, 40)
    ax.plot(vv, henderson_hasselbalch(Ca, Va, Cb, vv, pka), "k.", ms=3, label="Henderson-Hasselbalch")
    ax.plot([ve / 2], [pka], "bo")
    ax.annotate("half-equivalence: pH = pKa", (ve / 2, pka), (20, 3), arrowprops=dict(arrowstyle="->"))
    ax.plot([ve], [weak_ph(Ca, Va, Cb, ve, pka)], "ro")
    ax.annotate("equivalence point, pH above 7", (ve, weak_ph(Ca, Va, Cb, ve, pka)), (30, 6.2), arrowprops=dict(arrowstyle="->"))
    ax.set_xlabel("volume of 0.1 mol/L NaOH added (mL)")
    ax.set_ylabel("pH of the flask (no unit)")
    ax.set_title("25 mL of 0.1 mol/L acetic acid titrated with NaOH")
    ax.set_ylim(0, 14)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "weak_acid_curve.png", dpi=120)

    # --- buffer capacity
    Ct = 0.05
    phs = np.linspace(1.5, 12.5, 200)
    form = beta_formula(phs, Ct, pka)
    num = []
    for ph in phs:
        h = 10.0 ** (-ph)
        na = Ct * 10.0 ** (-pka) / (10.0 ** (-pka) + h) + KW / h - h      # base needed to sit at this pH
        num.append(beta_numeric(Ct, na, pka) if na > 1e-5 else np.nan)
    fig2, ax2 = plt.subplots(figsize=(6.5, 4.2))
    ax2.plot(phs, form, lw=2, label="Van Slyke formula")
    ax2.plot(phs, num, "k.", ms=3, label="numerical derivative of the solver")
    ax2.axvline(pka, color="gray", ls=":")
    ax2.set_xlabel("pH (no unit)")
    ax2.set_ylabel("buffer capacity (mol/L per pH unit)")
    ax2.set_title("0.05 mol/L acetic acid / acetate: best buffer near pH = pKa")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "buffer_capacity.png", dpi=120)
    print(f"beta at pH = pKa (formula) {beta_formula(pka, Ct, pka):.4f}; ln(10) Ct/4 = {np.log(10) * Ct / 4:.4f}")

    # --- noise
    v, p = make_data(Ca, Va, Cb, pka, 40.0, 0.2, 0.03, 0.02, seed=1)
    est = find_equivalence(v, p)
    print(f"one noisy run: Ve = {est:.3f} mL (true {ve})")
    errs = []
    for s in range(300):
        v2, p2 = make_data(Ca, Va, Cb, pka, 40.0, 0.2, 0.03, 0.02, seed=100 + s)
        errs.append(find_equivalence(v2, p2) - ve)
    errs = np.array(errs)
    print(f"300 noisy runs: mean error {errs.mean():+.4f} mL, standard deviation {errs.std():.4f} mL")
    clean = find_equivalence(*make_data(Ca, Va, Cb, pka, 40.0, 0.2))
    print(f"noise-free derivative peak at {clean:.4f} mL (offset {clean - ve:+.4f} mL from Ve)")
    fig3, axs = plt.subplots(1, 2, figsize=(9, 3.8))
    axs[0].plot(v, p, "k.", ms=3)
    axs[0].set_xlabel("volume reading (mL)")
    axs[0].set_ylabel("pH reading (no unit)")
    axs[0].set_title("noisy titration data")
    order = np.argsort(v)
    mids = 0.5 * (v[order][1:] + v[order][:-1])
    axs[1].plot(mids, np.diff(p[order]) / np.diff(v[order]), "k.", ms=3)
    axs[1].axvline(est, color="r", label=f"peak at {est:.2f} mL")
    axs[1].axvline(ve, color="gray", ls=":", label=f"true Ve {ve:.1f} mL")
    axs[1].set_xlabel("volume (mL)")
    axs[1].set_ylabel("dpH/dV (pH units per mL)")
    axs[1].set_title("first derivative: the peak marks the equivalence point")
    axs[1].legend(fontsize=8)
    for a in axs:
        a.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "noisy_derivative.png", dpi=120)

    # --- sensitivity to concentration and the failure case
    for c in (0.1, 0.01, 0.001):
        e = equivalence_volume(c, Va, c)
        jump = weak_ph(c, Va, c, e * 1.01, pka) - weak_ph(c, Va, c, e * 0.99, pka)
        print(f"C = {c:g}: pH at start {weak_ph(c, Va, c, 0.0, pka):.2f}, equivalence {weak_ph(c, Va, c, e, pka):.2f}, "
              f"jump across +-1% of Ve {jump:.2f}")
    for c in (1e-6, 1e-7, 1e-8):
        print(f"strong acid {c:g} mol/L: naive pH {naive_strong_ph(c):.2f}, with water {solve_ph(c, 0.0, None):.3f}")
    print(f"acetic acid 1e-7 mol/L alone: pH {pure_weak_acid_ph(1e-7, pka):.3f}")
    cs = np.logspace(-9, -1, 100)
    fig4, ax4 = plt.subplots(figsize=(6.5, 4.2))
    ax4.semilogx(cs, [naive_strong_ph(c) for c in cs], "--", color="gray", label="textbook -log10(C), ignores water")
    ax4.semilogx(cs, [solve_ph(c, 0.0, None) for c in cs], color="tab:blue", lw=2, label="charge balance (includes water)")
    ax4.axhline(7, color="k", lw=0.6)
    ax4.set_xlabel("strong acid concentration (mol/L)")
    ax4.set_ylabel("pH (no unit)")
    ax4.set_title("Failure case: very dilute acid cannot give pH above 7")
    ax4.grid(alpha=0.3)
    ax4.legend(fontsize=8)
    fig4.tight_layout()
    fig4.savefig(OUT / "dilute_failure.png", dpi=120)

    # --- mini-project: vinegar
    c_true = 50.0 / 60.05
    c_dil = c_true / 10.0
    ve_true = equivalence_volume(c_dil, 25.0, 0.1)
    print(f"vinegar 5 g/100 mL = {c_true:.4f} mol/L; diluted {c_dil:.5f} mol/L; true Ve = {ve_true:.3f} mL")
    v, p = make_data(c_dil, 25.0, 0.1, pka, 35.0, 0.2, 0.03, 0.02, seed=7)
    ve_est = find_equivalence(v, p)
    c_est = vinegar_concentration(ve_est)
    print(f"estimated Ve {ve_est:.3f} mL -> vinegar {c_est:.4f} mol/L = {vinegar_percent(c_est):.3f} g/100 mL (error {100 * (c_est / c_true - 1):+.2f}%)")
