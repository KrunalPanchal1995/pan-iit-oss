"""Session 3 (Level 3): the Hodgkin-Huxley nerve cell, integrated with your own RK4.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: the Hodgkin-Huxley model
# **A. Real-world problem.** The leaky integrate-and-fire neuron of Session 2 *draws* a spike
# by hand. A real nerve cell makes its spike from the physics of ion channels: sodium rushes
# in, potassium flows out. Hodgkin and Huxley (squid giant axon, 1952) wrote four coupled
# equations that reproduce the spike, the threshold, the refractory period and repetitive
# firing. Today you integrate them yourself and validate the result.
#
# **Plan.** (1) write the equations, (2) integrate with RK4, (3) check the resting state,
# the gating variables and the charge balance, (4) find the threshold and the firing
# onset, (5) test temperature, g_Na, axon diameter and a time step that is too large.
#
# *General education only. This is a simplified textbook model of one axon, not a medical tool.*

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# Classic squid-axon parameters, MODERN convention: V = inside minus outside, rest near -65 mV.
C_M = 1.0          # membrane capacitance, uF/cm^2
G_NA = 120.0       # maximum sodium conductance, mS/cm^2
G_K = 36.0         # maximum potassium conductance, mS/cm^2
G_L = 0.3          # leak conductance, mS/cm^2
E_NA = 50.0        # sodium reversal potential, mV
E_K = -77.0        # potassium reversal potential, mV
E_L = -54.387      # leak reversal potential, mV (chosen so that rest is -65 mV)
T_REF = 6.3        # temperature of the original rate functions, degrees C
Q10 = 3.0          # rate multiplier per 10 degrees C (the Q10 idea)


# %% [markdown]
# ## Step 1: the equations
# The membrane voltage V obeys a current balance (units: uA/cm^2 = mS/cm^2 x mV):
#
#     C dV/dt = I_ext - g_Na m^3 h (V - E_Na) - g_K n^4 (V - E_K) - g_L (V - E_L)
#
# Each gate x in {m, n, h} is a probability between 0 and 1 that relaxes towards a value set
# by the voltage:  dx/dt = alpha_x(V) (1 - x) - beta_x(V) x.  The rates alpha, beta
# (in 1/ms) are the standard empirical fits of Hodgkin and Huxley.

# %%
def vtrap(x, y):
    """x / (1 - exp(-x / y)), safe at x = 0 where the limit is y."""
    z = x / y
    if abs(z) < 1e-7:
        return y * (1.0 - z / 2.0)
    return x / (1.0 - math.exp(-z))


def rates(V):
    """Return (alpha_m, beta_m, alpha_h, beta_h, alpha_n, beta_n) in 1/ms at 6.3 C."""
    am = 0.1 * vtrap(V + 40.0, 10.0)
    bm = 4.0 * math.exp(-(V + 65.0) / 18.0)
    ah = 0.07 * math.exp(-(V + 65.0) / 20.0)
    bh = 1.0 / (1.0 + math.exp(-(V + 35.0) / 10.0))
    an = 0.01 * vtrap(V + 55.0, 10.0)
    bn = 0.125 * math.exp(-(V + 65.0) / 80.0)
    return am, bm, ah, bh, an, bn


def gate_steady(V):
    """Steady-state values (m_inf, h_inf, n_inf) of the gates at a fixed voltage."""
    am, bm, ah, bh, an, bn = rates(V)
    return am / (am + bm), ah / (ah + bh), an / (an + bn)


def ion_currents(V, m, h, n, gna=G_NA):
    """Sodium, potassium and leak currents (uA/cm^2); positive means outward."""
    return gna * m ** 3 * h * (V - E_NA), G_K * n ** 4 * (V - E_K), G_L * (V - E_L)


def hh_rhs(y, i_ext, phi=1.0, gna=G_NA):
    """Right-hand side of the four equations. y = (V, m, h, n); phi multiplies the gate rates."""
    V, m, h, n = y
    am, bm, ah, bh, an, bn = rates(V)
    i_na, i_k, i_l = ion_currents(V, m, h, n, gna)
    return (
        (i_ext - i_na - i_k - i_l) / C_M,
        phi * (am * (1.0 - m) - bm * m),
        phi * (ah * (1.0 - h) - bh * h),
        phi * (an * (1.0 - n) - bn * n),
    )


# %% [markdown]
# ## Step 2: RK4, written by hand
# Runge-Kutta 4 takes four slope estimates per step and combines them. The stimulus
# `stim(t)` is a function of time (uA/cm^2), so we can use pulses, steps and ramps.

# %%
def rk4_step(y, t, dt, stim, phi=1.0, gna=G_NA):
    k1 = hh_rhs(y, stim(t), phi, gna)
    y2 = tuple(a + 0.5 * dt * b for a, b in zip(y, k1))
    k2 = hh_rhs(y2, stim(t + 0.5 * dt), phi, gna)
    y3 = tuple(a + 0.5 * dt * b for a, b in zip(y, k2))
    k3 = hh_rhs(y3, stim(t + 0.5 * dt), phi, gna)
    y4 = tuple(a + dt * b for a, b in zip(y, k3))
    k4 = hh_rhs(y4, stim(t + dt), phi, gna)
    return tuple(a + dt / 6.0 * (b + 2 * c + 2 * d + e) for a, b, c, d, e in zip(y, k1, k2, k3, k4))


def find_rest(gna=G_NA):
    """Resting voltage: where the steady-state net ion current is zero (bisection)."""
    def net(V):
        m, h, n = gate_steady(V)
        return sum(ion_currents(V, m, h, n, gna))
    lo, hi = -80.0, -50.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if net(lo) * net(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


V_REST = find_rest()


def rest_state(gna=G_NA):
    v = V_REST if gna == G_NA else find_rest(gna)
    m, h, n = gate_steady(v)
    return (v, m, h, n)


def simulate(stim, t_end, dt=0.01, temp=T_REF, gna=G_NA, y0=None):
    """Integrate with RK4 from rest. Returns arrays t, V, m, h, n (ms, mV, then 0..1)."""
    phi = Q10 ** ((temp - T_REF) / 10.0)
    steps = int(round(t_end / dt))
    y = rest_state(gna) if y0 is None else tuple(y0)
    out = np.empty((steps + 1, 4))
    out[0] = y
    for i in range(steps):
        try:
            y = rk4_step(y, i * dt, dt, stim, phi, gna)
        except OverflowError:               # exp() overflowed: the solution has blown up
            out[i + 1:] = np.nan
            break
        out[i + 1] = y
        if not (abs(y[0]) < 1e4):          # blown up: stop and keep what we have
            out[i + 2:] = np.nan
            break
    t = np.arange(steps + 1) * dt
    return t, out[:, 0], out[:, 1], out[:, 2], out[:, 3]


def pulse(amp, start=1.0, dur=1.0):
    return lambda t: amp if start <= t < start + dur else 0.0


def step_current(amp, start=1.0):
    return lambda t: amp if t >= start else 0.0


# %% [markdown]
# ## Step 3: spikes, thresholds and firing rate
# A *spike* is counted each time V crosses 0 mV going upwards. The *threshold* is found by
# bisection: the smallest pulse that still produces a spike.

# %%
def spike_times(t, V, level=0.0):
    up = np.where((V[:-1] < level) & (V[1:] >= level))[0]
    return t[up] + (level - V[up]) / (V[up + 1] - V[up]) * (t[up + 1] - t[up])


def fires(amp, dur=1.0, dt=0.02, temp=T_REF, gna=G_NA):
    t, V, *_ = simulate(pulse(amp, 1.0, dur), 30.0 + dur, dt, temp, gna)
    return len(spike_times(t, V)) > 0


def threshold_pulse(dur=1.0, dt=0.02, temp=T_REF, gna=G_NA, hi=400.0):
    """Smallest pulse amplitude (uA/cm^2, to 0.01) of duration `dur` ms that fires a spike."""
    lo = 0.0
    if not fires(hi, dur, dt, temp, gna):
        return float("nan")
    while hi - lo > 0.01:
        mid = 0.5 * (lo + hi)
        if fires(mid, dur, dt, temp, gna):
            hi = mid
        else:
            lo = mid
    return hi


def firing_rate(i_amp, t_end=400.0, dt=0.05, temp=T_REF, gna=G_NA):
    """Steady rate (Hz) for a constant current: from the last inter-spike interval."""
    t, V, *_ = simulate(step_current(i_amp, 1.0), t_end, dt, temp, gna)
    st = spike_times(t, V)
    if len(st) < 3:
        return 0.0
    return 1000.0 / float(st[-1] - st[-2])


def strength_duration(durations=(0.2, 0.5, 1.0, 2.0, 5.0, 20.0)):
    """Mini-project helper: threshold amplitude (uA/cm^2) and charge (nC/cm^2) for each pulse length."""
    return [(d, threshold_pulse(d), d * threshold_pulse(d)) for d in durations]


def max_rate_scan(currents):
    """Mini-project helper: (best rate in Hz, current) over a list of constant currents."""
    best = (0.0, None)
    for i in currents:
        r = firing_rate(float(i))
        if r > best[0]:
            best = (r, float(i))
    return best


def onset_current(lo=2.0, hi=12.0, t_end=1000.0, dt=0.05):
    """Smallest constant current (to 0.01 uA/cm^2) with sustained firing: a spike still occurs in
    the last fifth of a `t_end` ms run (a few transient spikes at the start do not count)."""
    def sustained(i):
        t, V, *_ = simulate(step_current(i, 1.0), t_end, dt)
        return bool(np.any(spike_times(t, V) > 0.8 * t_end))
    while hi - lo > 0.01:
        mid = 0.5 * (lo + hi)
        if sustained(mid):
            hi = mid
        else:
            lo = mid
    return hi


# %% [markdown]
# ## Step 4: validation against a reference
# For a tiny current the gates barely move in the first millisecond, so the membrane acts
# as one leaky capacitor with a fixed conductance g0 = g_Na m^3 h + g_K n^4 + g_L. That is
# the leaky integrate-and-fire closed form of Session 2:
# V(t) = V_rest + (I / g0) (1 - exp(-g0 t / C)).

# %%
def instant_conductance():
    m, h, n = gate_steady(V_REST)
    return G_NA * m ** 3 * h + G_K * n ** 4 + G_L


def lif_subthreshold(t, i_amp, g0=None):
    g0 = instant_conductance() if g0 is None else g0
    return V_REST + (i_amp / g0) * (1.0 - np.exp(-g0 * t / C_M))


def charge_balance(amp=10.0, dur=1.0, t_end=40.0, dt=0.01):
    """Charges (uA/cm^2 x ms = nC/cm^2) carried by each ion current during one spike.
    Returns (q_na, q_k, q_l, q_stim, delta_v). The stimulus charge must equal the net ion
    charge plus C x change in V."""
    t, V, m, h, n = simulate(pulse(amp, 1.0, dur), t_end, dt)
    i_na = G_NA * m ** 3 * h * (V - E_NA)
    i_k = G_K * n ** 4 * (V - E_K)
    i_l = G_L * (V - E_L)
    q = [float(np.sum(0.5 * (x[1:] + x[:-1]) * np.diff(t))) for x in (i_na, i_k, i_l)]
    return q[0], q[1], q[2], amp * dur, float(V[-1] - V[0])


# %% [markdown]
# ## Step 5: temperature, g_Na, a refractory period and a step that is too large

# %%
def spike_width(t, V):
    """Width (ms) of the first spike at half of its height above rest."""
    k = int(np.argmax(V))
    half = V_REST + 0.5 * (V[k] - V_REST)
    a = k
    while a > 0 and V[a] > half:
        a -= 1
    b = k
    while b < len(V) - 1 and V[b] > half:
        b += 1
    ta = t[a] + (half - V[a]) / (V[a + 1] - V[a]) * (t[a + 1] - t[a])
    tb = t[b - 1] + (half - V[b - 1]) / (V[b] - V[b - 1]) * (t[b] - t[b - 1])
    return float(tb - ta)


def second_pulse_threshold(gap, first=20.0, dur=1.0, dt=0.02):
    """Smallest amplitude of a second 1 ms pulse that fires a second spike `gap` ms after the
    start of the first pulse (which is 1 ms long and strong enough to fire). nan if none."""
    def stim_of(a):
        return lambda t: first if 1.0 <= t < 1.0 + dur else (a if 1.0 + gap <= t < 1.0 + gap + dur else 0.0)

    def n_spikes(a):
        t, V, *_ = simulate(stim_of(a), 40.0, dt)
        return len(spike_times(t, V))

    hi = 400.0
    if n_spikes(hi) < 2:
        return float("nan")
    lo = 0.0
    while hi - lo > 0.05:
        mid = 0.5 * (lo + hi)
        if n_spikes(mid) >= 2:
            hi = mid
        else:
            lo = mid
    return hi


def blows_up(dt, i_amp=10.0, t_end=20.0):
    """True if RK4 with this time step leaves the physical range (V beyond +-200 mV or gate outside 0..1)."""
    t, V, m, h, n = simulate(pulse(i_amp, 1.0, 1.0), t_end, dt)
    bad = ~np.isfinite(V) | (np.abs(V) > 200.0)
    for g in (m, h, n):
        bad = bad | ~np.isfinite(g) | (g < -1e-9) | (g > 1 + 1e-9)
    return bool(bad.any())


# %% [markdown]
# ## Step 6: how fast does the spike travel?
# Cable theory: a spike spreads along the axon by current flowing through the inside (axial
# resistance r_i per length) and leaking out through the membrane (r_m x length). The length
# constant is lambda = sqrt(r_m / r_i). For an axon of radius a, r_i is proportional to
# 1/a^2 and r_m to 1/a, so lambda is proportional to sqrt(a). The membrane time constant does
# not depend on a, so the speed (about lambda / time) scales as **sqrt(a)**. We test this
# scaling with a discretised HH cable.

# %%
RI = 35.4          # axoplasm resistivity, ohm cm (classic squid value)


def cable_speed(radius_cm, length_cm=6.0, dx=0.02, dt=0.0005, t_max=40.0):
    """Speed (cm/ms) of a spike travelling on an HH cable of the given radius (explicit scheme)."""
    with np.errstate(all="ignore"):
        return _cable_speed(radius_cm, length_cm, dx, dt, t_max)


def _cable_speed(radius_cm, length_cm, dx, dt, t_max):
    n = int(round(length_cm / dx)) + 1
    v0, m0, h0, n0 = rest_state()
    V = np.full(n, v0)
    m = np.full(n, m0)
    h = np.full(n, h0)
    g = np.full(n, n0)
    d = 1000.0 * radius_cm / (2.0 * RI * C_M)     # cm^2/ms (the factor 1000 converts mA to uA)
    x = np.arange(n) * dx
    t_a = t_b = None
    xa, xb = 1.5, 4.0
    ia, ib = int(round(xa / dx)), int(round(xb / dx))
    for step in range(int(t_max / dt)):
        t = step * dt
        lap = np.empty(n)
        lap[1:-1] = (V[2:] - 2 * V[1:-1] + V[:-2]) / dx ** 2
        lap[0] = 2 * (V[1] - V[0]) / dx ** 2
        lap[-1] = 2 * (V[-2] - V[-1]) / dx ** 2
        am = 0.1 * (V + 40.0) / (1.0 - np.exp(-(V + 40.0) / 10.0))
        bm = 4.0 * np.exp(-(V + 65.0) / 18.0)
        ah = 0.07 * np.exp(-(V + 65.0) / 20.0)
        bh = 1.0 / (1.0 + np.exp(-(V + 35.0) / 10.0))
        an = 0.01 * (V + 55.0) / (1.0 - np.exp(-(V + 55.0) / 10.0))
        bn = 0.125 * np.exp(-(V + 65.0) / 80.0)
        i_ion = G_NA * m ** 3 * h * (V - E_NA) + G_K * g ** 4 * (V - E_K) + G_L * (V - E_L)
        i_inj = np.where((x < 0.2) & (t < 1.0), 40.0, 0.0)
        dV = d * lap + (i_inj - i_ion) / C_M
        m += dt * (am * (1 - m) - bm * m)
        h += dt * (ah * (1 - h) - bh * h)
        g += dt * (an * (1 - g) - bn * g)
        V += dt * dV
        if t_a is None and V[ia] > 0.0:
            t_a = t
        if t_b is None and V[ib] > 0.0:
            t_b = t
            break
    if t_a is None or t_b is None:
        return float("nan")
    return (xb - xa) / (t_b - t_a)


def velocity_scaling(a, a0, v0):
    """Scaling argument: v is proportional to sqrt(radius). Returns v at radius a given v0 at a0."""
    return v0 * math.sqrt(a / a0)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print(f"resting potential {V_REST:.3f} mV; gates at rest m,h,n = "
          + ", ".join(f"{g:.4f}" for g in gate_steady(V_REST)))

    t, V, m, h, n = simulate(pulse(10.0, 1.0, 1.0), 30.0, 0.01)
    st = spike_times(t, V)
    print(f"10 uA/cm2 for 1 ms: peak {V.max():.1f} mV at {t[V.argmax()]:.2f} ms, "
          f"width {spike_width(t, V):.2f} ms, undershoot {V[t > 5].min():.1f} mV, spikes {len(st)}")
    fig, ax = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    ax[0].plot(t, V, color="#1f6feb")
    ax[0].axhline(V_REST, color="gray", ls=":")
    ax[0].set_ylabel("membrane voltage V (mV)")
    ax[0].set_title("One action potential from a 1 ms, 10 uA/cm^2 pulse")
    ax[1].plot(t, m, label="m (Na activation)")
    ax[1].plot(t, h, label="h (Na inactivation)")
    ax[1].plot(t, n, label="n (K activation)")
    ax[1].set_xlabel("time (ms)")
    ax[1].set_ylabel("gate value (0 to 1)")
    ax[1].legend(fontsize=8)
    for a in ax:
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "action_potential.png", dpi=120)

    # threshold behaviour
    thr = threshold_pulse(1.0)
    print(f"threshold for a 1 ms pulse: {thr:.2f} uA/cm2")
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    for amp in (0.8 * thr, 0.95 * thr, 1.05 * thr, 2 * thr):
        tt, VV, *_ = simulate(pulse(amp, 1.0, 1.0), 20.0, 0.02)
        ax2.plot(tt, VV, label=f"{amp:.1f} uA/cm2")
        print(f"  pulse {amp:6.2f}: peak {VV.max():6.1f} mV")
    ax2.set_xlabel("time (ms)")
    ax2.set_ylabel("membrane voltage V (mV)")
    ax2.set_title("All or nothing: weak pulses fade, strong ones give the same spike")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "threshold.png", dpi=120)

    # repetitive firing and f-I curve
    cur = [2, 4, 6, 8, 10, 15, 20, 30, 50, 100]
    rates_hz = [firing_rate(i) for i in cur]
    onset = onset_current()
    print(f"onset of sustained firing: {onset:.2f} uA/cm2")
    for i, r in zip(cur, rates_hz):
        print(f"  I = {i:4d} uA/cm2 -> {r:6.1f} Hz")
    fig3, ax3 = plt.subplots(figsize=(7, 4))
    ax3.plot(cur, rates_hz, "o-")
    ax3.axvline(onset, color="red", ls="--", label=f"measured onset {onset:.1f}")
    ax3.set_xlabel("constant current I (uA/cm^2)")
    ax3.set_ylabel("firing rate (spikes per second)")
    ax3.set_title("Hodgkin-Huxley f-I curve")
    ax3.legend(fontsize=8)
    ax3.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "fi_curve.png", dpi=120)

    # validation
    tt = np.arange(0, 1.001, 0.01)
    t2, V2, *_ = simulate(step_current(0.1, 0.0), 1.0, 0.01)
    print(f"LIF check at 1 ms for 0.1 uA/cm2: HH {V2[-1] - V_REST:.5f} mV, LIF {lif_subthreshold(tt, 0.1)[-1] - V_REST:.5f} mV")
    print("charge balance (na, k, leak, stim, dV):", [round(x, 4) for x in charge_balance()])

    # a time step that is too large
    for dt in (0.01, 0.1, 0.5, 1.0, 2.0, 3.0):
        print(f"  dt = {dt}: blows up = {blows_up(dt)}")
