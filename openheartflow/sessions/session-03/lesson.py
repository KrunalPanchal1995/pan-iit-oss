"""Session 3 (Level 3): the two-element Windkessel model solved with RK4.

Run:  python start.py 3
General education only: this is not medical advice and the model is not a diagnostic tool.
"""
# %% [markdown]
# # Session 3: the arteries as an elastic chamber (Windkessel)
# **A. Real-world problem.** The heart does not push steadily: it ejects blood in a short
# burst (systole) and rests (diastole). Yet the blood pressure in the arteries never drops to
# zero between beats. The big arteries are elastic: they swell during the burst, store blood,
# and squeeze it onwards while the heart rests, like the air chamber of an old fire engine
# pump (German: Windkessel). What sets the top and bottom pressure, and what happens when the
# arteries get stiffer?
#
# *This is general education. It is not medical advice and the model is not a diagnostic
# tool. The 120/80 target below is an illustrative number, not a norm for any person.*
#
# **Plan.** (1) write the model, one equation for the pressure P, (2) solve it with our own
# RK4, (3) validate against the exact decay in diastole and the mean-flow balance, (4) stiffen
# the arteries, change the heart rate, and break the model on purpose.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

HR0, SV0 = 70.0, 70.0          # typical textbook heart rate (beats/min) and stroke volume (mL)
SYSTOLE_FRACTION = 0.3         # the ejection lasts about 0.3 of the beat
N_STEPS = 300                  # RK4 steps per beat (a multiple of 10, so systole ends on a step)


# %% [markdown]
# ## Step 1: the model
# Two parts: an elastic compliance `C` (mL per mmHg: how much blood the arteries store per
# mmHg of pressure rise) and a peripheral resistance `R` (mmHg per mL/s). The ventricle
# pushes in a flow `Q_in(t)`, a half sine during the first 0.3 of each beat and zero after.
# The blood stored in `C` grows with inflow and drains through `R`:
#
#     C dP/dt = Q_in(t) - P / R
#
# The peak of the half sine is fixed so that one beat delivers exactly the stroke volume:
# `SV = integral of Q_in dt = 2 Q_peak T_s / pi`.

# %%
def inflow(t, hr=HR0, sv=SV0, frac=SYSTOLE_FRACTION):
    """Flow from the ventricle (mL/s) at time t (s): half sine in systole, zero in diastole."""
    period = 60.0 / hr
    ts = frac * period
    phase = t % period
    if phase >= ts:
        return 0.0
    return math.pi * sv / (2.0 * ts) * math.sin(math.pi * phase / ts)


# %% [markdown]
# ## Step 2: our own RK4
# The state is a vector `y` (here only one number, the pressure P). Runge-Kutta 4 takes four
# slope estimates per step and combines them; its error shrinks like dt^4.

# %%
def rk4_step(f, t, y, dt):
    k1 = f(t, y)
    k2 = f(t + dt / 2, y + dt / 2 * k1)
    k3 = f(t + dt / 2, y + dt / 2 * k2)
    k4 = f(t + dt, y + dt * k3)
    return y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def windkessel(R, C, hr=HR0, sv=SV0, beats=30, n=N_STEPS, frac=SYSTOLE_FRACTION, p0=None):
    """Integrate C dP/dt = Q_in - P/R. Returns time (s) and pressure (mmHg) arrays.

    R in mmHg s/mL, C in mL/mmHg. p0 defaults to the mean-flow pressure R * mean(Q_in).
    """
    if R <= 0 or C <= 0:
        raise ValueError("R and C must be positive")
    period = 60.0 / hr
    dt = period / n
    if p0 is None:
        p0 = R * sv * hr / 60.0
    f = lambda t, y: np.array([(inflow(t, hr, sv, frac) - y[0] / R) / C])
    y = np.array([float(p0)])
    t = np.arange(beats * n + 1) * dt
    P = np.empty(beats * n + 1)
    P[0] = y[0]
    for k in range(beats * n):
        y = rk4_step(f, t[k], y, dt)
        P[k + 1] = y[0]
    return t, P


def last_beat(R, C, hr=HR0, sv=SV0, beats=30, n=N_STEPS, frac=SYSTOLE_FRACTION):
    """Time (from 0) and pressure over the final beat, after the start-up has died away."""
    t, P = windkessel(R, C, hr, sv, beats, n, frac)
    return t[:n + 1] - t[0], P[-(n + 1):]


# %% [markdown]
# ## Step 3: read the waveform
# Systolic = highest pressure, diastolic = lowest, pulse pressure = their difference, mean =
# time average over one beat (the last point repeats the first, so it is left out).

# %%
def bp_stats(P):
    """(systolic, diastolic, pulse pressure, mean) in mmHg from one periodic beat."""
    body = np.asarray(P)[:-1]
    return float(body.max()), float(body.min()), float(body.max() - body.min()), float(body.mean())


def diastolic_decay(P0, R, C, t):
    """Exact solution of C dP/dt = -P/R with P(0) = P0, for t seconds after systole ends."""
    return P0 * np.exp(-np.asarray(t) / (R * C))


def mean_inflow(hr=HR0, sv=SV0):
    return sv * hr / 60.0          # mL/s


# %% [markdown]
# ## Step 4: validate
# Two independent checks. (a) In diastole there is no inflow, so the exact solution is
# P = P0 exp(-t / (R C)); the numerical curve must lie on it. (b) Averaged over a periodic
# beat the stored blood does not change, so mean(P) / R = mean(Q_in): mean P = R x mean Q.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    R, C = 1.214, 1.251                       # tuned in the mini-project to give about 120/80
    tt, P = last_beat(R, C)
    period = 60.0 / HR0
    ts = SYSTOLE_FRACTION * period
    s, d, pp, m = bp_stats(P)
    print(f"R = {R}, C = {C}: systolic {s:.1f}, diastolic {d:.1f}, pulse {pp:.1f}, mean {m:.1f} mmHg")
    print(f"mean P / R = {m / R:.2f} mL/s, mean inflow = {mean_inflow():.2f} mL/s")
    i0 = int(round(SYSTOLE_FRACTION * N_STEPS))
    exact = diastolic_decay(P[i0], R, C, tt[i0:] - ts)
    print(f"largest gap between RK4 and the exact diastolic decay: {np.abs(P[i0:] - exact).max():.2e} mmHg")

    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(tt, P, lw=2, label="RK4 solution")
    ax.plot(tt[i0:], exact, "k--", lw=1, label="exact decay in diastole")
    ax.axhline(m, color="gray", ls=":", label=f"mean {m:.0f} mmHg")
    ax.axvspan(0, ts, color="tab:red", alpha=0.08, label="systole (ejection)")
    ax.set_xlabel("time within the beat (s)")
    ax.set_ylabel("arterial pressure (mmHg)")
    ax.set_title("Windkessel pressure wave, R = 1.214, C = 1.251")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "windkessel_wave.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    for c_val, col in ((2.5, "tab:green"), (1.251, "tab:blue"), (0.626, "tab:red")):
        t2, P2 = last_beat(R, c_val)
        s2, d2, pp2, m2 = bp_stats(P2)
        ax2.plot(t2, P2, color=col, label=f"C = {c_val}: pulse {pp2:.0f}, mean {m2:.0f} mmHg")
        print(f"C = {c_val}: systolic {s2:.1f}, diastolic {d2:.1f}, pulse {pp2:.1f}, mean {m2:.1f}")
    ax2.set_xlabel("time within the beat (s)")
    ax2.set_ylabel("arterial pressure (mmHg)")
    ax2.set_title("Stiffer arteries (smaller C): same mean, bigger swing")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "stiffness_effect.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Where the model stops
# The ventricle here forces its flow whatever the pressure; a real heart ejects only while
# its pressure exceeds the arterial pressure and the aortic valve closes afterwards. There is
# no wave travelling along the arteries, no change of C with pressure, and one lump stands
# for the whole arterial tree. Very small C gives absurd pressure swings (see the checkpoint).
