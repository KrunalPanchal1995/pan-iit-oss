"""Session 1 (Level 1): a point load on a simply supported beam: reactions, shear and moment.

Run:  python start.py 1
Educational model only. Never use it to design a real structure.
"""
# %% [markdown]
# # Session 1: what a beam does with a load
# **A. Real-world problem.** A plank across a stream bends when you stand on it. Two things
# hold it up: the two banks. How much of your weight does each bank carry? Where inside the
# plank is the bending worst? Engineers answer with three pictures: the *reactions* at the
# supports, the *shear force diagram* and the *bending moment diagram*.
#
# **Plan.** (1) find the reactions with two balance rules, (2) cut the beam at x and find the
# internal shear V and moment M, (3) draw both diagrams, (4) see where M is largest.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: reactions from balance
# A simply supported beam of span `L` rests on a support at x = 0 (A) and x = L (B). A downward
# point load `P` acts at distance `a` from A (and `b = L - a` from B). The beam does not move,
# so two things must balance:
#
#     forces:   RA + RB = P
#     turning about A:   RB * L = P * a     ->   RB = P * a / L,   RA = P * b / L
#
# The support nearer the load carries more of it.

# %%
def reactions(P, a, L):
    """Support reactions (RA, RB) in the unit of P, for a load P at distance a from A."""
    b = L - a
    return P * b / L, P * a / L


# %% [markdown]
# ## Step 2: cut the beam and look inside
# Cut the beam at x and keep the left piece. Its inside face must supply
#
# * a vertical force **V(x)** (shear force): V = RA, minus P once the cut is past the load;
# * a turning effect **M(x)** (bending moment): M = RA * x, minus P * (x - a) past the load.

# %%
def shear(x, P, a, L):
    """Shear force V(x), same unit as P."""
    ra, _ = reactions(P, a, L)
    x = np.asarray(x, dtype=float)
    return np.where(x < a, ra, ra - P)


def moment(x, P, a, L):
    """Bending moment M(x), unit of P times unit of length (sagging positive)."""
    ra, _ = reactions(P, a, L)
    x = np.asarray(x, dtype=float)
    return np.where(x < a, ra * x, ra * x - P * (x - a))


# %% [markdown]
# ## Step 3: where is the bending worst?
# M rises with slope RA, peaks under the load, then falls with slope -RB. So
#
#     M_max = RA * a = P * a * b / L,   and for a centred load  M_max = P * L / 4.
#
# V changes sign exactly where M peaks: slope of M = V.

# %%
def max_moment(P, a, L):
    return P * a * (L - a) / L


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    P, L = 12.0, 8.0                       # kN, m
    fig, axes = plt.subplots(3, 1, figsize=(7, 7), sharex=True)
    x = np.linspace(0, L, 601)
    for a, c in ((2.0, "tab:blue"), (4.0, "tab:orange")):
        ra, rb = reactions(P, a, L)
        axes[0].plot(x, shear(x, P, a, L), c, label=f"load at {a:g} m: RA={ra:.1f}, RB={rb:.1f} kN")
        axes[1].plot(x, moment(x, P, a, L), c, label=f"load at {a:g} m: M max {max_moment(P, a, L):.1f} kN m")
        print(f"a={a}: RA={ra:.2f} kN, RB={rb:.2f} kN, Mmax={max_moment(P, a, L):.2f} kN m")
    axes[0].set_ylabel("shear force V (kN)")
    axes[1].set_ylabel("bending moment M (kN m)")
    for ax in axes[:2]:
        ax.axhline(0, color="k", lw=0.8)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    axes[0].set_title("Shear and moment, simply supported beam, P = 12 kN, L = 8 m")
    # the beam drawing
    axes[2].plot([0, L], [0, 0], "k", lw=6)
    for a, c in ((2.0, "tab:blue"), (4.0, "tab:orange")):
        axes[2].annotate("", xy=(a, 0.1), xytext=(a, 1.0), arrowprops=dict(color=c, width=2))
    axes[2].set_ylim(-0.5, 1.2)
    axes[2].set_yticks([])
    axes[2].set_xlabel("position along the beam x (m)")
    axes[2].set_title("The two load positions (arrows)", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "shear_moment.png", dpi=120)

    pos = np.linspace(0, L, 121)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(pos, max_moment(P, pos, L), label="M max = P a b / L")
    ax2.plot(L / 2, P * L / 4, "ro", label="centre load: P L / 4 = 24 kN m")
    ax2.set_xlabel("load position a from support A (m)")
    ax2.set_ylabel("largest bending moment (kN m)")
    ax2.set_title("The worst place for a load is the middle")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "moment_vs_position.png", dpi=120)
    print("centre load Mmax =", max_moment(P, L / 2, L), "kN m")

# %% [markdown]
# ## Where this stops
# This session says how big the forces inside the beam are, not whether the beam is strong or
# stiff enough. For that we need the cross-section and the material: Session 2.
