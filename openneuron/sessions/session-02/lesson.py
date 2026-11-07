"""Session 2 (Level 2): the membrane as an RC circuit - the leaky integrate-and-fire neuron.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the membrane is an RC circuit
# **A. Real-world problem.** A cell membrane keeps charge apart, so it stores energy like a
# capacitor C; ion channels let charge leak through, like a resistor R. Inject a current I
# and the voltage obeys  C dV/dt = -(V - V_rest)/R + I.  Add a rule "when V reaches the
# threshold, record a spike, reset V, and wait a refractory time" and you have the *leaky
# integrate-and-fire* (LIF) neuron. How fast does it fire for a given current, and what current
# do we need to make it fire 20 times a second?
#
# *General education only. All numbers labelled typical are textbook-style round values,
# not measurements of a particular cell.*

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

V_REST = -70.0     # mV, typical
V_TH = -55.0       # mV, typical threshold
V_RESET = -70.0    # mV, typical reset value
R_DEFAULT = 100.0  # megaohm (typical order of magnitude for a small neuron)
C_DEFAULT = 100.0  # picofarad  -> tau = R C = 10 ms (typical)
T_REF = 2.0        # ms, typical refractory period


# %% [markdown]
# ## Step 1: units and the time constant
# Units: 1 megaohm x 1 nanoamp = 1 mV, and 1 megaohm x 1 picofarad = 1 microsecond, so
# tau (ms) = R (megaohm) x C (pF) / 1000. With R = 100 and C = 100 this gives 10 ms.
#
# For a constant current the equation has the exact solution
#
#     V(t) = V_rest + R I (1 - exp(-t / tau))
#
# which climbs towards the level V_rest + R I. It can only reach the threshold if
# R I > V_th - V_rest (15 mV here): the *rheobase* current is I = (V_th - V_rest) / R.

# %%
def tau_ms(R=R_DEFAULT, C=C_DEFAULT):
    return R * C / 1000.0


def rheobase_nA(R=R_DEFAULT):
    """Smallest constant current (nA) that can ever reach the threshold."""
    return (V_TH - V_REST) / R


def v_subthreshold(t, I_nA, R=R_DEFAULT, C=C_DEFAULT):
    """Exact V(t) for a constant current switched on at t = 0 (valid until the threshold)."""
    return V_REST + R * I_nA * (1.0 - np.exp(-np.asarray(t, dtype=float) / tau_ms(R, C)))


# %% [markdown]
# ## Step 2: the firing rate, derived
# Solve V(T) = V_th for the time T to climb from reset to threshold. With the reset equal to
# the rest value:
#
#     V_rest + R I (1 - exp(-T/tau)) = V_th   =>   exp(-T/tau) = 1 - (V_th - V_rest)/(R I)
#     T = tau ln( R I / (R I - (V_th - V_rest)) )
#
# After a spike the cell is also silent for t_ref, so one full cycle lasts T + t_ref and
# the rate is  f = 1 / (t_ref + tau ln(R I / (R I - (V_th - V_rest)))).
# With t_ref = 0 this is the closed form  f = 1 / (tau ln(...)).  Below the rheobase f = 0.

# %%
def climb_time_ms(I_nA, R=R_DEFAULT, C=C_DEFAULT):
    """Time (ms) to climb from reset to threshold; inf if the current is too small."""
    ri = R * I_nA
    dv = V_TH - V_RESET
    if ri <= dv:
        return math.inf
    return tau_ms(R, C) * math.log(ri / (ri - dv))


def rate_hz(I_nA, R=R_DEFAULT, C=C_DEFAULT, t_ref=T_REF):
    """Closed-form firing rate (spikes per second)."""
    T = climb_time_ms(I_nA, R, C)
    return 0.0 if math.isinf(T) else 1000.0 / (t_ref + T)


def current_for_rate(f_hz, R=R_DEFAULT, C=C_DEFAULT, t_ref=T_REF):
    """Design problem, inverted: the constant current (nA) that gives f_hz spikes per second.
    From T = 1000/f - t_ref:  R I = (V_th - V_reset) / (1 - exp(-T/tau))."""
    T = 1000.0 / f_hz - t_ref
    if T <= 0:
        return math.inf
    return (V_TH - V_RESET) / (R * (1.0 - math.exp(-T / tau_ms(R, C))))


# %% [markdown]
# ## Step 3: simulate it numerically
# Between spikes we can step the equation exactly (constant current in a step), or with
# the simple Euler rule  V += dt * (-(V - V_rest)/tau + R I / tau).  Comparing them with the
# closed form shows how good each is.

# %%
def simulate_lif(I_nA, t_end=500.0, dt=0.01, R=R_DEFAULT, C=C_DEFAULT, t_ref=T_REF, method="exact"):
    """Returns (t, V, spike_times). I_nA may be a number or a function of time (ms)."""
    tau = tau_ms(R, C)
    cur = I_nA if callable(I_nA) else (lambda t, a=I_nA: a)
    n = int(round(t_end / dt))
    t = np.arange(n + 1) * dt
    V = np.empty(n + 1)
    V[0] = V_REST
    spikes = []
    wait = 0.0
    a = 1.0 - math.exp(-dt / tau)
    for i in range(n):
        v = V[i]
        if wait > 1e-12:
            wait -= dt
            V[i + 1] = V_RESET
            continue
        vinf = V_REST + R * cur(t[i])
        if method == "exact":
            v = v + (vinf - v) * a
        else:
            v = v + dt * (vinf - v) / tau
        if v >= V_TH:
            spikes.append(t[i + 1])
            v = V_RESET
            wait = t_ref
        V[i + 1] = v
    return t, V, np.array(spikes)


def measured_rate(spikes):
    """Rate from the last inter-spike interval (spikes per second)."""
    if len(spikes) < 2:
        return 0.0
    return 1000.0 / float(spikes[-1] - spikes[-2])


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print(f"tau = {tau_ms():.1f} ms, rheobase = {rheobase_nA():.3f} nA")
    I20 = current_for_rate(20.0)
    print(f"current for 20 spikes per second (t_ref {T_REF} ms): {I20:.4f} nA")
    for I in (0.15, 0.16, 0.2, 0.3, 0.5, 1.0):
        t, V, sp = simulate_lif(I, 1000.0, 0.01)
        print(f"I = {I:5.2f} nA: closed form {rate_hz(I):7.2f} Hz   simulation {measured_rate(sp):7.2f} Hz   "
              f"(without refractory {rate_hz(I, t_ref=0.0):7.2f} Hz)")

    fig, ax = plt.subplots(2, 1, figsize=(7, 6))
    for I, col in ((0.12, "gray"), (0.2, "#1f6feb"), (0.4, "#d9534f")):
        t, V, sp = simulate_lif(I, 150.0, 0.01)
        trace = V.copy()
        for s in sp:
            trace[int(round(s / 0.01))] = 20.0
        ax[0].plot(t, trace, color=col, label=f"I = {I} nA")
    ax[0].axhline(V_TH, color="k", ls="--", lw=1)
    ax[0].set_xlabel("time (ms)")
    ax[0].set_ylabel("membrane voltage (mV)")
    ax[0].set_title("Leaky integrate-and-fire neuron (spikes drawn to +20 mV)")
    ax[0].legend(fontsize=8)
    ax[0].grid(alpha=0.3)
    cur = np.linspace(0.0, 1.0, 400)
    ax[1].plot(cur, [rate_hz(c) for c in cur], label="closed form, t_ref 2 ms")
    ax[1].plot(cur, [rate_hz(c, t_ref=0.0) for c in cur], "--", label="closed form, t_ref 0")
    cs = np.linspace(0.05, 1.0, 12)
    ax[1].plot(cs, [measured_rate(simulate_lif(c, 1000.0, 0.01)[2]) for c in cs], "ko", ms=4, label="simulation")
    ax[1].axvline(rheobase_nA(), color="gray", ls=":")
    ax[1].set_xlabel("input current (nA)")
    ax[1].set_ylabel("firing rate (spikes per second)")
    ax[1].set_title("The f-I curve")
    ax[1].legend(fontsize=8)
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "lif_and_fi.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    t = np.linspace(0, 60, 300)
    ax2.plot(t, v_subthreshold(t, 0.1), label="exact V(t), I = 0.1 nA")
    for dt, st in ((5.0, "s"), (1.0, "o")):
        tt, VV, _ = simulate_lif(0.1, 60.0, dt, method="euler")
        ax2.plot(tt, VV, st, ms=3, label=f"Euler, dt = {dt} ms")
    ax2.set_xlabel("time (ms)")
    ax2.set_ylabel("membrane voltage (mV)")
    ax2.set_title("Subthreshold response: exact versus Euler")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "subthreshold.png", dpi=120)
