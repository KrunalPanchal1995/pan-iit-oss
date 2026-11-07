"""Session 1 (Level 1): three boxes, two arrows, and an outbreak curve.

TEACHING TOOL ONLY. The people here are invented. Not a forecast, not medical advice,
and not a basis for public-health decisions.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: S, I and R - three boxes with arrows
# **A. Real-world problem.** When a new infection appears in a town, why do some outbreaks
# explode while others fizzle out? Modellers sort people into three boxes:
# **S**usceptible (could catch it), **I**nfected (have it and can pass it on) and
# **R**ecovered (had it, now immune). Two arrows move people: S -> I (infection) and
# I -> R (recovery).
#
# **Plan.** (1) move people by hand for one day, (2) let the computer repeat that for many
# small time steps, (3) find the day with the most people infected, (4) see that everything
# depends on how many people each case infects.
#
# **Important.** This is a teaching toy with invented numbers. It is not a forecast, not
# medical advice, and not a basis for public-health decisions.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: one small step
# A town of N = 1000 people, one of them infected. In a tiny time step `dt` (in days):
# * new infections = beta * S * I / N * dt  (beta = contacts that pass the infection, per day)
# * new recoveries = gamma * I * dt          (gamma = 1 / days a person stays infectious)
#
# S * I / N is large when there are many susceptible AND many infected people, because
# then meetings between the two kinds are common. The answers are averages, so fractions
# of a person (like 0.4995) are fine here.

# %%
def one_step(S, I, R, beta, gamma, N, dt):
    """Move people between the boxes for a time dt (days). Returns the new (S, I, R)."""
    new_infections = beta * S * I / N * dt
    new_recoveries = gamma * I * dt
    return S - new_infections, I + new_infections - new_recoveries, R + new_recoveries


# %% [markdown]
# ## Step 2: repeat many times
# We use steps of 0.1 day and keep one value per day. Small steps matter: with a step of a
# whole day the slopes are applied too long before being updated, and the curve is less accurate.

# %%
def run_outbreak(beta, gamma, N=1000, I0=1, days=120, dt=0.1):
    """Return arrays S, I, R with one value per day (length days + 1)."""
    S, I, R = float(N - I0), float(I0), 0.0
    out = [(S, I, R)]
    per_day = int(round(1 / dt))
    for _ in range(days):
        for _ in range(per_day):
            S, I, R = one_step(S, I, R, beta, gamma, N, dt)
        out.append((S, I, R))
    S_, I_, R_ = np.array(out).T
    return S_, I_, R_


# %% [markdown]
# ## Step 3: how many does each case infect?
# One infected person stays infectious for 1/gamma days and passes the infection on at rate beta, so
# infects about **beta / gamma** others (when almost everybody is still susceptible). We call
# this number R0, the *basic reproduction number*. If R0 is above 1, each case replaces itself
# with more than one case and the outbreak grows. If it is below 1, it dies away.

# %%
def r0(beta, gamma):
    return beta / gamma


def generations(R0, n=6):
    """Cases in generation 0, 1, 2, ... if every case infects R0 others (early phase)."""
    return [R0 ** k for k in range(n)]


def peak_of(I):
    """(day of the peak, number infected at the peak)."""
    k = int(np.argmax(I))
    return k, float(I[k])


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    beta, gamma = 0.5, 0.25
    S, I, R = run_outbreak(beta, gamma)
    day, top = peak_of(I)
    print("R0 =", r0(beta, gamma))
    print("people at the end: S, I, R =", round(S[-1], 1), round(I[-1], 2), round(R[-1], 1))
    print("peak day and peak infected:", day, round(top, 1))
    print("generations for R0 = 2:", generations(2.0))
    print("generations for R0 = 0.5:", generations(0.5))

    d = np.arange(len(S))
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(d, S, label="S susceptible")
    ax.plot(d, I, label="I infected")
    ax.plot(d, R, label="R recovered")
    ax.axvline(day, color="gray", ls=":")
    ax.set_xlabel("day")
    ax.set_ylabel("people (out of 1000)")
    ax.set_title("A toy outbreak (R0 = 2): infected people rise, peak, fall")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "sir_curves.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    for b, label in ((0.5, "R0 = 2.0 (grows)"), (0.25, "R0 = 1.0 (borderline)"), (0.125, "R0 = 0.5 (dies out)")):
        _, Ib, _ = run_outbreak(b, gamma)
        ax2.plot(d, Ib, label=label)
    ax2.set_xlabel("day")
    ax2.set_ylabel("people infected now")
    ax2.set_title("The curve depends on R0 = beta / gamma")
    ax2.legend()
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "r0_compare.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Real people differ in age and behaviour, meet in groups, and are counted late. Session 2
# turns these boxes and arrows into equations; Session 3 fits them to noisy data.
