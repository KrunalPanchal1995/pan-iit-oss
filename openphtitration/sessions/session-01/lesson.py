"""Session 1 (Level 1): acids, bases, the pH scale and the shape of a titration curve.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: acids, bases and a titration curve
# **A. Real-world problem.** A lab wants to know how strong a bottle of acid is. They add a
# base from a tall glass tube (a *burette*) a little at a time. The liquid in the flask first
# changes slowly and then, all at once, jumps. That jump tells them the concentration.
#
# **Safety.** Handling real acids and bases needs supervision, goggles and a teacher.
# Everything here is a computer simulation.
#
# **Plan.** (1) the pH scale, (2) the pH of a strong acid or base, (3) add base to acid and
# draw the titration curve, (4) find the equivalence point.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
KW = 1e-14        # ion product of water at 25 degrees C (mol/L)^2


# %% [markdown]
# ## Step 1: the pH scale
# pH measures how much acid (H+ ions) a liquid has: `pH = -log10([H+])`, where `[H+]` is the
# concentration in mol/L. A smaller pH means more acid. pH 7 is neutral (pure water at 25 C),
# below 7 is acid, above 7 is basic. Each step of 1 in pH is a factor of 10 in [H+].
# Example: 0.1 mol/L of a strong acid has [H+] = 0.1, so pH = 1.

# %%
def ph_from_h(h):
    """pH of a solution with hydrogen-ion concentration h (mol/L)."""
    return -np.log10(h)


def ph_strong_acid(c):
    """pH of c mol/L of a strong acid such as HCl (ideal, c well above 1e-6)."""
    return ph_from_h(c) + 0.0       # + 0.0 turns -0.0 into 0.0


def ph_strong_base(c):
    """pH of c mol/L of a strong base such as NaOH at 25 C (ideal, c well above 1e-6)."""
    return 14.0 + np.log10(c)


def kind(ph):
    if abs(ph - 7.0) < 0.5:
        return "neutral"
    return "acidic" if ph < 7 else "basic"


# %% [markdown]
# ## Step 2: add base to acid
# We put `Va` mL of acid (concentration `Ca`) in a flask and add `Vb` mL of base
# (concentration `Cb`) from the burette. Acid and base cancel one another mole for mole:
#
#     moles of acid   = Ca * Va / 1000      (mol; Va in mL)
#     moles of base   = Cb * Vb / 1000
#     leftover        = (acid moles - base moles) / total volume
#
# If acid is left over, the leftover is [H+]. If base is left over, the leftover is [OH-]
# and pH = 14 + log10[OH-]. Exactly at the balance, only water is left: pH 7.

# %%
def strong_ph(Ca, Va, Cb, Vb):
    """pH of the flask after adding Vb mL of strong base (Cb, mol/L) to Va mL of strong acid (Ca)."""
    x = (Ca * Va - Cb * Vb) / (Va + Vb)       # leftover acid (+) or base (-), mol/L
    if x >= 0:
        h = (x + np.sqrt(x * x + 4 * KW)) / 2
    else:
        h = 2 * KW / (-x + np.sqrt(x * x + 4 * KW))
    return float(-np.log10(h))


def equivalence_volume(Ca, Va, Cb):
    """Volume of base (mL) that exactly cancels the acid: Ca * Va = Cb * Vb."""
    return Ca * Va / Cb


# %% [markdown]
# ## Step 3: the curve and the equivalence point
# We compute pH after every small step of base. The steep part is the *equivalence point*,
# where the moles of base added equal the moles of acid that were in the flask.

# %%
def titration_curve(Ca, Va, Cb, vmax):
    vb = np.linspace(0.0, vmax, 501)
    return vb, np.array([strong_ph(Ca, Va, Cb, v) for v in vb])


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    # Figure 1: the pH scale with examples
    fig, ax = plt.subplots(figsize=(9, 2.8))
    ax.imshow(np.linspace(0, 14, 256)[None, :], extent=[0, 14, 0, 1], aspect="auto", cmap="RdYlBu_r")
    examples = [("1 mol/L HCl", ph_strong_acid(1.0)), ("0.1 mol/L HCl", ph_strong_acid(0.1)),
                ("0.001 mol/L HCl", ph_strong_acid(1e-3)), ("pure water", 7.0),
                ("0.001 mol/L NaOH", ph_strong_base(1e-3)), ("0.1 mol/L NaOH", ph_strong_base(0.1)),
                ("1 mol/L NaOH", ph_strong_base(1.0))]
    for i, (name, ph) in enumerate(examples):
        ax.axvline(ph, color="k", lw=0.8)
        ax.text(ph, 1.04 + 0.28 * (i % 2), f"{name}\npH {ph:.0f}", ha="center", va="bottom", fontsize=7)
        print(f"{name:18s} pH {ph:5.2f}  {kind(ph)}")
    ax.set_ylim(0, 1.8)
    ax.set_yticks([])
    ax.set_xlim(-0.5, 14.5)
    ax.set_xlabel("pH (no unit)")
    ax.set_xticks(range(0, 15))
    ax.set_title("The pH scale at 25 C (ideal solutions)", pad=8)
    fig.tight_layout()
    fig.savefig(OUT / "ph_scale.png", dpi=120)

    # Figure 2: titration curve, 25 mL of 0.1 M HCl with 0.1 M NaOH
    Ca, Va, Cb = 0.1, 25.0, 0.1
    vb, ph = titration_curve(Ca, Va, Cb, 50.0)
    ve = equivalence_volume(Ca, Va, Cb)
    fig2, ax2 = plt.subplots(figsize=(6.5, 4.2))
    ax2.plot(vb, ph, color="tab:blue", lw=2)
    ax2.axvline(ve, color="gray", ls=":")
    ax2.plot([ve], [strong_ph(Ca, Va, Cb, ve)], "ro")
    ax2.annotate(f"equivalence point\n{ve:.1f} mL, pH {strong_ph(Ca, Va, Cb, ve):.0f}",
                 (ve, 7), (ve + 6, 4), arrowprops=dict(arrowstyle="->"))
    ax2.set_xlabel("volume of base added (mL)")
    ax2.set_ylabel("pH of the flask (no unit)")
    ax2.set_title("25 mL of 0.1 mol/L HCl titrated with 0.1 mol/L NaOH")
    ax2.set_ylim(0, 14)
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "titration_curve.png", dpi=120)
    for v in (0, 10, 20, 24, 24.9, 25, 25.1, 26, 30, 40):
        print(f"base added {v:5.1f} mL -> pH {strong_ph(Ca, Va, Cb, v):6.3f}")
