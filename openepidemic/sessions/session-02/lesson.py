"""Session 2 (Level 2): the SIR equations, R0, herd immunity and the final size.

TEACHING TOOL ONLY. Invented numbers, simplified model. Not a forecast, not medical
advice, and not a basis for public-health decisions.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the SIR equations
# **A. Real-world problem.** A town wants to know two things before any outbreak: how many
# people would catch a new infection in total, and what share of the town must be protected
# (by vaccination, say) so the infection cannot spread. Both answers come from three
# equations and one number, R0.
#
# **Important.** Teaching model only: not a forecast, not medical advice, not a basis for
# public-health decisions.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the equations
# With N people, S + I + R = N always, and
#
#     dS/dt = -beta S I / N
#     dI/dt =  beta S I / N - gamma I
#     dR/dt =  gamma I
#
# beta [1/day] = infectious contacts per person per day, gamma [1/day] = recovery rate
# (1/gamma = days infectious). **R0 = beta / gamma.** The infection grows exactly when
# dI/dt > 0, i.e. when R0 * S / N > 1.

# %%
def r0(beta, gamma):
    return beta / gamma


def r_effective(R0, s_fraction):
    """Reproduction number when a fraction s of people is still susceptible."""
    return R0 * s_fraction


def herd_immunity_threshold(R0):
    """Share of people who must be immune so that R0 * (1 - share) < 1."""
    return max(0.0, 1.0 - 1.0 / R0)


def simulate(beta, gamma, N=10000, I0=10, days=160, R_init=0.0, dt=0.05):
    """Euler steps of size dt (days). Returns S, I, R, one value per day."""
    S, I, R = N - I0 - R_init, float(I0), float(R_init)
    out = [(S, I, R)]
    per_day = int(round(1 / dt))
    for _ in range(days):
        for _ in range(per_day):
            flow = beta * S * I / N * dt
            rec = gamma * I * dt
            S, I, R = S - flow, I + flow - rec, R + rec
        out.append((S, I, R))
    return np.array(out).T


# %% [markdown]
# ## Step 2: the final size
# When the outbreak is over, the fraction z of the town ever infected obeys
#
#     z = 1 - exp(-R0 z)
#
# (derived by dividing dS/dt by dR/dt; assumes almost everyone starts susceptible). There is
# no closed formula, so we solve it numerically with Newton's method.

# %%
def final_size(R0, z0=0.9):
    """Solve z = 1 - exp(-R0 z) by Newton's method; returns 0 if R0 <= 1."""
    if R0 <= 1.0:
        return 0.0
    z = z0
    for _ in range(100):
        f = z - (1 - np.exp(-R0 * z))
        df = 1 - R0 * np.exp(-R0 * z)
        z_new = z - f / df
        if abs(z_new - z) < 1e-13:
            return float(z_new)
        z = z_new
    return float(z)


def peak_fraction(R0):
    """Largest fraction infected at once, when almost everyone starts susceptible: 1 - (1 + ln R0) / R0."""
    return 1.0 - (1.0 + np.log(R0)) / R0 if R0 > 1 else 0.0


# %% [markdown]
# ## Step 3: design with vaccination
# A vaccine with efficacy e protects a fraction e of the people vaccinated (the rest stay
# susceptible, which is what "leaky" or imperfect protection means for the town as a whole).
# With coverage v, the protected share is v * e, and we need R0 * (1 - v * e) < 1:
#
#     v > (1 - 1/R0) / e

# %%
def protected_share(coverage, efficacy):
    return coverage * efficacy


def coverage_needed(R0, efficacy=1.0):
    """Smallest coverage that brings R_eff to 1. A value above 1 means: impossible by vaccination alone."""
    return herd_immunity_threshold(R0) / efficacy


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("R0 = 3 herd threshold:", round(herd_immunity_threshold(3.0), 4))
    print("final size R0 = 2:", round(final_size(2.0), 4), " R0 = 3:", round(final_size(3.0), 4))
    print("peak fraction R0 = 2:", round(peak_fraction(2.0), 4))
    print("coverage needed R0 = 3, e = 1.0 / 0.9 / 0.6:", [round(coverage_needed(3.0, e), 3) for e in (1.0, 0.9, 0.6)])

    gamma = 0.2
    S, I, R = simulate(0.4, gamma)
    print("simulated peak fraction (R0 = 2):", round(I.max() / 10000, 4), " final R:", round(R[-1] / 10000, 4))

    d = np.arange(len(S))
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for v, name in ((0.0, "no vaccination"), (0.3, "30% covered, e = 0.9"), (0.5, "50% covered, e = 0.9")):
        _, Iv, _ = simulate(0.4, gamma, R_init=protected_share(v, 0.9) * 10000)
        ax.plot(d, Iv, label=name)
        print(name, "peak infected:", round(Iv.max(), 1))
    ax.set_xlabel("day")
    ax.set_ylabel("people infected now (out of 10000)")
    ax.set_title("R0 = 2: more protection, lower and later peak")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "vaccination_curves.png", dpi=120)

    r0s = np.linspace(1.0, 5.0, 81)
    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    ax2.plot(r0s, [100 * final_size(x) for x in r0s], label="ever infected (final size)")
    ax2.plot(r0s, [100 * herd_immunity_threshold(x) for x in r0s], "--", label="herd immunity threshold")
    ax2.set_xlabel("R0 (no unit)")
    ax2.set_ylabel("percent of the town")
    ax2.set_title("Final size and herd immunity threshold versus R0")
    ax2.legend()
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "final_size.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Real vaccines wane, people mix unevenly, and the formulas assume a well-mixed town. The
# thresholds here are idealised teaching numbers, never targets for a real programme.
