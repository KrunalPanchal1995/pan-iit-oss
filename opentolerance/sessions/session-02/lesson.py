"""Session 2 (Level 2): ISO-style fits (hole basis) and worst-case tolerance stacks.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: fits, limits and the worst-case stack
# **A. Real-world problem.** A 25 mm shaft must turn freely in a bearing bore, but a gear must
# stay put on another 25 mm shaft. Both are "a shaft in a hole"; only the fit differs. The ISO
# system names fits with a code such as 25 H7/g6. Today you decode it, compute the smallest and
# largest clearance, pick fits for two jobs, and add up tolerances along a chain of parts.
#
# *Educational model.* The table values below are the ISO 286 values for the size range
# 18 to 30 mm as we state them here; always check your own copy of the standard before you
# design a real part.

# %%
import itertools
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# International tolerance grades for nominal sizes over 18 up to 30 mm, in micrometres (um)
IT = {6: 13.0, 7: 21.0}
# Shaft fundamental deviations for the same size range, in um.
# g and h: the UPPER deviation es is given (g: -7, h: 0). p: the LOWER deviation ei is given (+22).
# js is symmetric: +-IT/2.
SHAFT_DEV = {"g": ("es", -7.0), "h": ("es", 0.0), "p": ("ei", 22.0)}


# %% [markdown]
# ## Step 1: tolerance zones in the hole-basis system
# Deviations are measured from the nominal size (25 mm here) in micrometres (1 um = 0.001 mm).
# **Hole basis:** the hole is always H, meaning its lower deviation EI is 0, so the hole zone is
# `[0, +IT]`. A shaft letter moves the shaft zone: `[ei, es]` with `es - ei = IT`.

# %%
def hole_zone(letter="H", grade=7):
    """(EI, ES) of the hole in um. Only the hole-basis hole H is supported."""
    if letter != "H":
        raise ValueError("hole-basis system: the hole letter is H")
    return 0.0, IT[grade]


def shaft_zone(letter, grade):
    """(ei, es) of the shaft in um."""
    it = IT[grade]
    if letter == "js":
        return -it / 2, it / 2
    kind, value = SHAFT_DEV[letter]
    if kind == "es":
        return value - it, value
    return value, value + it


def to_mm(nominal_mm, zone_um):
    """Convert a zone in um to limits in mm: nominal + deviation / 1000."""
    return tuple(round(nominal_mm + z / 1000.0, 6) for z in zone_um)


# %% [markdown]
# ## Step 2: clearance limits of a fit
#     minimum clearance = EI - es       (smallest hole, biggest shaft)
#     maximum clearance = ES - ei       (biggest hole, smallest shaft)
# Negative means interference. The fit is a **clearance fit** if the minimum is >= 0, an
# **interference fit** if the maximum is <= 0, otherwise a **transition fit** (either can occur).

# %%
def fit_limits(hole, shaft):
    """(min clearance, max clearance) in um from hole=(EI, ES) and shaft=(ei, es)."""
    return hole[0] - shaft[1], hole[1] - shaft[0]


def classify(min_c, max_c):
    if min_c >= 0:
        return "clearance"
    if max_c <= 0:
        return "interference"
    return "transition"


def fit(shaft_letter, shaft_grade, hole_grade=7):
    h = hole_zone("H", hole_grade)
    s = shaft_zone(shaft_letter, shaft_grade)
    lo, hi = fit_limits(h, s)
    return lo, hi, classify(lo, hi)


# %% [markdown]
# ## Step 3: choose a fit for a job (design problem)
# A job gives requirements on the clearance range. We test candidate fits against them.
# *Sliding bearing (illustrative requirement):* at least 5 um of clearance for an oil film, at
# most 45 um so it does not rattle. *Light press fit (illustrative):* interference in every
# build, at most 40 um so the hole is not over-stressed.

# %%
CANDIDATES = [("g", 6), ("h", 6), ("js", 6), ("p", 6)]


def choose_fits(min_c_required, max_c_allowed, hole_grade=7):
    """Names of candidate fits whose whole clearance range lies inside [min_c_required, max_c_allowed]."""
    out = []
    for letter, grade in CANDIDATES:
        lo, hi, _ = fit(letter, grade, hole_grade)
        if lo >= min_c_required and hi <= max_c_allowed:
            out.append(f"H{hole_grade}/{letter}{grade}")
    return out


# %% [markdown]
# ## Step 4: worst-case tolerance stack
# A gap is made by a chain of parts: lengths that add (sign +1) and lengths that subtract (-1):
#
#     gap = sum( sign_i * x_i ),  each x_i = nominal_i +- t_i
#
# In the worst case every part sits at its limit in the direction that hurts, so
# **the tolerances simply add**: gap tolerance = sum of t_i. We check this by trying all
# 2^n combinations of upper/lower limits (the "corners").

# %%
def worst_case_stack(signs, nominals, tols):
    """(nominal gap, lowest gap, highest gap) by adding the tolerances."""
    if any(t < 0 for t in tols):
        raise ValueError("tolerances must not be negative")
    nominal = float(np.dot(signs, nominals))
    total = float(np.sum(tols))
    return nominal, nominal - total, nominal + total


def corner_stack(signs, nominals, tols):
    """(lowest gap, highest gap) by trying every corner: each part at nominal - t or nominal + t."""
    gaps = []
    for pick in itertools.product((-1, 1), repeat=len(nominals)):
        x = np.asarray(nominals) + np.asarray(pick) * np.asarray(tols)
        gaps.append(float(np.dot(signs, x)))
    return min(gaps), max(gaps)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    h = hole_zone("H", 7)
    fig, axes = plt.subplots(1, 3, figsize=(9, 4), sharey=True)
    for ax, (letter, grade) in zip(axes, [("g", 6), ("js", 6), ("p", 6)]):
        s = shaft_zone(letter, grade)
        lo, hi, kind = fit(letter, grade)
        ax.axhline(0, color="k", lw=1)
        ax.bar(-0.2, h[1] - h[0], bottom=h[0], width=0.35, color="tab:blue", alpha=0.7, label="hole H7")
        ax.bar(0.2, s[1] - s[0], bottom=s[0], width=0.35, color="tab:orange", alpha=0.8, label="shaft")
        ax.set_title(f"25 H7/{letter}{grade}\n{kind}: {lo:g} to {hi:g} um", fontsize=9)
        ax.set_xticks([])
        ax.grid(alpha=0.3, axis="y")
        print(f"25 H7/{letter}{grade}: hole {to_mm(25, h)} mm, shaft {to_mm(25, s)} mm, clearance {lo:g} to {hi:g} um ({kind})")
    axes[0].set_ylabel("deviation from 25 mm (um)")
    axes[0].legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "fit_zones.png", dpi=120)

    signs = np.array([1, -1, -1, -1])
    nominals = np.array([40.0, 10.0, 12.0, 15.0])
    tols = np.array([0.10, 0.05, 0.05, 0.08])
    nom, lo, hi = worst_case_stack(signs, nominals, tols)
    clo, chi = corner_stack(signs, nominals, tols)
    print(f"stack: nominal gap {nom:.2f} mm, worst case {lo:.2f} to {hi:.2f} mm, corners {clo:.2f} to {chi:.2f} mm")
    print("sliding bearing candidates:", choose_fits(5, 45))
    print("light press candidates:", choose_fits(-40, -0.0001))

    fig2, ax2 = plt.subplots(figsize=(6.5, 3.6))
    names = ["housing", "plate 1", "plate 2", "plate 3"]
    ax2.barh(names, tols, color=["tab:blue", "tab:orange", "tab:orange", "tab:orange"])
    ax2.barh(["gap (sum)"], [tols.sum()], color="tab:green")
    ax2.set_xlabel("tolerance, plus or minus (mm)")
    ax2.set_title("Worst case: the gap tolerance is the sum of the part tolerances")
    ax2.grid(alpha=0.3, axis="x")
    fig2.tight_layout()
    fig2.savefig(OUT / "stack_sum.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Adding every tolerance is safe but pessimistic: it assumes every part is at its worst limit at
# the same time. Session 3 asks how likely that is.
