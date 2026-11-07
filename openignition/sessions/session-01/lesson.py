"""Session 1 (Level 1): why a mixture waits, then suddenly ignites.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: why a mixture waits, then suddenly ignites
# **A. Real-world problem.** Squeeze a fuel-air mixture in an engine and nothing seems to happen
# for a short while. Then, within a tiny fraction of that waiting time, the temperature explodes.
# That waiting time is the *ignition delay*. We build the smallest model that shows it.
#
# **Important.** This is a one-step *toy*. Real hydrogen-oxygen ignition is a network of
# chain-branching reactions with explosion limits; here one made-up reaction stands in for all of it.
#
# **Plan.** (1) a reaction rate that grows steeply with temperature, (2) a closed box where the
# reaction heats the gas, (3) step through time and watch the flat-then-jump curve, (4) read off
# the ignition delay.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

A_PRE = 2.5e9      # pre-exponential factor, 1/s (toy value)
EA = 150e3         # activation energy, J/mol (toy value)
R_GAS = 8.314      # gas constant, J/(mol K)
DT_AD = 1500.0     # temperature rise if ALL the fuel burns (adiabatic), K
RISE = 400.0       # we call the mixture "ignited" when T has risen by this much, K


# %% [markdown]
# ## Step 1: a rate that explodes with temperature
# The reaction rate constant is `k = A * exp(-Ea / (R * T))` (Arrhenius). Only the few molecules
# that collide hard enough react, and the fraction that can grows very fast with T.
# Check by hand: at T = 1000 K, `Ea/(R T) = 150000 / (8.314 * 1000) = 18.04`, so
# `k = 2.5e9 * exp(-18.04)`, about 36.5 per second. At 1400 K it is about 6300 per second.

# %%
def rate_const(T):
    """Arrhenius rate constant k(T) in 1/s for a temperature T in kelvin."""
    return A_PRE * np.exp(-EA / (R_GAS * T))


# %% [markdown]
# ## Step 2: the closed box that heats itself
# Let `c` be the fuel left (1 = all of it, 0 = none) and `T` the gas temperature.
#
#     dc/dt = -k(T) * c                 fuel is used up at rate k c
#     dT/dt = DT_AD * k(T) * c          each bit of fuel burnt heats the gas
#
# No heat escapes (an insulated box). Burning all the fuel would add DT_AD = 1500 K.
# *Feedback:* hotter gas gives a bigger k, which burns fuel faster, which heats the gas more.
# Take `heat=False` to switch the feedback off and compare.

# %%
def euler_run(T0, t_end, dt, dT_ad=DT_AD, heat=True):
    """Step the box forward with the simplest rule (Euler): new = old + dt * rate.
    Returns arrays t (s), T (K), c (fuel left, 0 to 1)."""
    n = int(round(t_end / dt))
    t = np.arange(n + 1) * dt
    T = np.empty(n + 1)
    c = np.empty(n + 1)
    T[0], c[0] = T0, 1.0
    for i in range(n):
        burn = rate_const(T[i]) * c[i]
        c[i + 1] = c[i] - dt * burn
        T[i + 1] = T[i] + (dt * dT_ad * burn if heat else 0.0)
    return t, T, c


# %% [markdown]
# ## Step 3: read off the ignition delay
# We define the ignition delay `tau` as the time when the temperature has risen by 400 K.
# We find it by walking along the curve and interpolating between the two steps that straddle it.

# %%
def ignition_delay(t, T, rise=RISE):
    """Time (s) at which T first reaches T[0] + rise, or None if it never does."""
    hit = np.nonzero(T >= T[0] + rise)[0]
    if len(hit) == 0:
        return None
    j = int(hit[0])
    f = (T[0] + rise - T[j - 1]) / (T[j] - T[j - 1])
    return float(t[j - 1] + f * (t[j] - t[j - 1]))


def euler_delay(T0, dT_ad=DT_AD):
    """Ignition delay (s) from an Euler run that stops at the event. The step is a small
    fraction of the reaction time 1/k at the ignition temperature."""
    if dT_ad <= RISE:          # even burning every drop of fuel cannot raise T by 400 K
        return None
    dt = 0.01 / rate_const(T0 + RISE)
    T, c, t = T0, 1.0, 0.0
    while T < T0 + RISE and t < 100.0:
        burn = rate_const(T) * c
        Tn = T + dt * dT_ad * burn
        if Tn >= T0 + RISE:
            return t + dt * (T0 + RISE - T) / (Tn - T)
        c -= dt * burn
        T = Tn
        t += dt
    return None


# %% [markdown]
# ## Step 4: see it
# Left: temperature against time, with and without the heat feedback. Right: the delay against the
# starting temperature (a log scale, because it changes by a factor of more than 100).

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t, T, c = euler_run(1000.0, 2.0e-3, 0.5e-6)
    t2, T2, c2 = euler_run(1000.0, 2.0e-3, 0.5e-6, heat=False)
    tau = ignition_delay(t, T)
    print(f"T0 = 1000 K: ignition delay = {tau * 1e3:.3f} ms")
    for ms in (0.0, 0.5, 1.0, 1.1, 1.2, 1.3, 1.5):
        i = int(round(ms * 1e-3 / 0.5e-6))
        print(f"  t = {ms:3.1f} ms  T = {T[i]:7.1f} K  fuel left = {c[i]:.3f}")
    print(f"without feedback, T stays at {T2.max():.0f} K and fuel left at 2 ms = {c2[-1]:.3f}")

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(t * 1e3, T, color="#d9534f", lw=2, label="with heat feedback")
    ax.plot(t2 * 1e3, T2, color="gray", ls="--", label="heat feedback off")
    ax.axvline(tau * 1e3, color="k", ls=":")
    ax.text(tau * 1e3 + 0.03, 1100, f"delay {tau * 1e3:.2f} ms", fontsize=9)
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("temperature (K)")
    ax.set_title("A closed box: flat, then a sudden jump")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "temperature_vs_time.png", dpi=120)

    T0s = np.array([850, 900, 950, 1000, 1050, 1100, 1150, 1200.0])
    taus = np.array([euler_delay(x) for x in T0s])
    for x, y in zip(T0s, taus):
        print(f"  T0 = {x:6.0f} K  delay = {y * 1e3:9.4f} ms")
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.semilogy(T0s, taus * 1e3, "o-", color="#1f6feb")
    ax2.set_xlabel("starting temperature T0 (K)")
    ax2.set_ylabel("ignition delay (ms)")
    ax2.set_title("A hotter start ignites much sooner")
    ax2.grid(alpha=0.3, which="both")
    fig2.tight_layout()
    fig2.savefig(OUT / "delay_vs_start.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
