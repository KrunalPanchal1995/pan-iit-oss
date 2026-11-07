"""Session 2 (Level 2): pH and pOH, moles at equivalence, indicators and dilution.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the mathematics of a strong acid - strong base titration
# **A. Real-world problem.** You must pick an indicator (a dye that changes colour) for a
# titration, and you must turn a burette reading into a concentration. Both need numbers:
# the pH at every point, the volume at the equivalence point, and the pH range of the dye.
#
# **Safety.** Real acids, bases and indicators need supervision; this is a simulation.
#
# **Plan.** (1) pH, pOH and pH + pOH = 14, (2) the mole balance Ca Va = Cb Vb, (3) pH before,
# at and after equivalence, (4) choosing an indicator, (5) dilution C1 V1 = C2 V2.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
KW = 1e-14        # ion product of water at 25 degrees C, (mol/L)^2
# approximate, well-known pH ranges over which the dye changes colour
INDICATORS = {"methyl orange": (3.1, 4.4), "phenolphthalein": (8.2, 10.0)}


# %% [markdown]
# ## Step 1: pH, pOH and the water constant
# `pH = -log10[H+]` and `pOH = -log10[OH-]`. Water always keeps `[H+][OH-] = Kw = 1e-14`
# at 25 C. Taking -log10 of both sides gives `pH + pOH = 14`.

# %%
def ph_of_h(h):
    return -np.log10(h)


def poh_of_oh(oh):
    return -np.log10(oh)


def poh_from_ph(ph):
    """pOH from pH at 25 C: pH + pOH = 14."""
    return 14.0 - ph


def h_of_ph(ph):
    return 10.0 ** (-ph)


# %% [markdown]
# ## Step 2: moles balance, and the three regions
# Volumes are in mL and concentrations in mol/L, so `C * V` is in millimoles (mmol).
# Net leftover concentration `x = (Ca Va - Cb Vb) / (Va + Vb)`: positive means leftover acid,
# negative leftover base. Including water, `x = [H+] - Kw/[H+]`, and solving the quadratic gives
# `[H+] = (x + sqrt(x^2 + 4 Kw)) / 2`. At equivalence `x = 0` so `[H+] = 1e-7` and pH = 7.

# %%
def net_excess(Ca, Va, Cb, Vb):
    """Leftover strong acid (+) or strong base (-) in mol/L after adding Vb mL of base."""
    return (Ca * Va - Cb * Vb) / (Va + Vb)


def h_from_excess(x):
    """[H+] (mol/L) from the net excess x, numerically stable for both signs."""
    if x >= 0:
        return (x + np.sqrt(x * x + 4 * KW)) / 2
    return 2 * KW / (-x + np.sqrt(x * x + 4 * KW))


def strong_ph(Ca, Va, Cb, Vb):
    return float(-np.log10(h_from_excess(net_excess(Ca, Va, Cb, Vb))))


def equivalence_volume(Ca, Va, Cb):
    """Ca * Va = Cb * Ve  ->  Ve = Ca * Va / Cb  (mL)."""
    return Ca * Va / Cb


def unknown_concentration(Cb, Ve, Va):
    """Concentration of the acid in the flask (mol/L) from the equivalence volume."""
    return Cb * Ve / Va


def volume_at_ph(ph, Ca, Va, Cb):
    """Inverse of the curve: the base volume (mL) at which the flask has this pH.
    From Ca Va - Cb Vb = x (Va + Vb) with x = [H+] - Kw/[H+]."""
    h = h_of_ph(ph)
    x = h - KW / h
    return (Ca * Va - x * Va) / (Cb + x)


# %% [markdown]
# ## Step 3: choose an indicator
# A dye changes colour over a pH range (lo, hi). The colour change happens at the volume where
# the flask pH is inside that range. The titration error is how far that volume is from the
# true equivalence volume, as a percentage. A good indicator has its whole range on the steep
# part, so every volume at which the colour could change is within a small error.

# %%
def indicator_error_percent(lo, hi, Ca, Va, Cb):
    """Largest percentage error in the endpoint volume over the dye's colour range."""
    ve = equivalence_volume(Ca, Va, Cb)
    return max(abs(volume_at_ph(p, Ca, Va, Cb) - ve) for p in (lo, hi)) / ve * 100.0


def suitable(name, Ca, Va, Cb, tol_percent=2.0):
    lo, hi = INDICATORS[name]
    return indicator_error_percent(lo, hi, Ca, Va, Cb) <= tol_percent


def lowest_concentration(name, Va=25.0, tol_percent=2.0):
    """Smallest equal acid and base concentration (mol/L) for which the dye keeps its error
    within tol_percent. Found by bisection on log10(C)."""
    lo_c, hi_c = -6.0, 0.0           # log10 of concentration
    if not suitable(name, 10 ** hi_c, Va, 10 ** hi_c, tol_percent):
        return float("nan")
    for _ in range(60):
        mid = (lo_c + hi_c) / 2
        if suitable(name, 10 ** mid, Va, 10 ** mid, tol_percent):
            hi_c = mid
        else:
            lo_c = mid
    return 10 ** hi_c


# %% [markdown]
# ## Step 4: dilution
# Adding solvent does not change the moles of dissolved acid: `C1 V1 = C2 V2`.

# %%
def final_volume(C1, V1, C2):
    """Volume (same unit as V1) needed to dilute V1 of concentration C1 down to C2."""
    return C1 * V1 / C2


def titration_curve(Ca, Va, Cb, vmax, n=601):
    vb = np.linspace(0.0, vmax, n)
    return vb, np.array([strong_ph(Ca, Va, Cb, v) for v in vb])


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    Va, Cb = 25.0, 0.1
    fig, ax = plt.subplots(figsize=(7, 4.6))
    for c, col in ((0.1, "tab:blue"), (0.01, "tab:orange"), (0.001, "tab:green")):
        ve = equivalence_volume(c, Va, c)
        vb, ph = titration_curve(c, Va, c, 2 * ve)
        ax.plot(vb / ve, ph, color=col, lw=2, label=f"{c:g} mol/L acid and base")
        print(f"C = {c:g}: pH at 0 mL {ph[0]:.2f}, at Ve {strong_ph(c, Va, c, ve):.2f}, "
              f"at 1.1 Ve {strong_ph(c, Va, c, 1.1 * ve):.2f}")
    for name, (lo, hi), col in (("methyl orange", INDICATORS["methyl orange"], "salmon"),
                                ("phenolphthalein", INDICATORS["phenolphthalein"], "violet")):
        ax.axhspan(lo, hi, color=col, alpha=0.3)
        ax.text(0.03, (lo + hi) / 2, name, va="center", fontsize=8)
    ax.set_xlabel("base added / equivalence volume (no unit)")
    ax.set_ylabel("pH of the flask (no unit)")
    ax.set_title("Strong acid - strong base: coloured bands are indicator ranges")
    ax.set_ylim(0, 14)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "strong_curves_indicators.png", dpi=120)

    cs = np.logspace(-3, 0, 60)
    fig2, ax2 = plt.subplots(figsize=(6.5, 4.2))
    for name in INDICATORS:
        lo, hi = INDICATORS[name]
        err = [indicator_error_percent(lo, hi, c, Va, c) for c in cs]
        ax2.loglog(cs, err, lw=2, label=name)
    ax2.axhline(2.0, color="red", ls="--", label="2% limit")
    ax2.set_xlabel("acid and base concentration (mol/L)")
    ax2.set_ylabel("endpoint error (%)")
    ax2.set_title("Dilute solutions need a better matched indicator")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "indicator_error.png", dpi=120)
    for name in INDICATORS:
        print(f"{name}: error at 0.1 mol/L = {indicator_error_percent(*INDICATORS[name], 0.1, Va, 0.1):.3f}%, "
              f"at 0.001 mol/L = {indicator_error_percent(*INDICATORS[name], 0.001, Va, 0.001):.2f}%, "
              f"lowest concentration within 2% = {lowest_concentration(name):.4g} mol/L")
    print("dilute 10 mL of 1.0 M to 0.1 M needs final volume", final_volume(1.0, 10.0, 0.1), "mL")
