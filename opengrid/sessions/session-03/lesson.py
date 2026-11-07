"""Session 3 (Level 3): a toy frequency model, inertia, droop, and a three-bus DC power flow.

Run:  python start.py 3
Educational toy model only. One aggregate generator stands for a whole grid; real grids have
protection, load shedding, many machine types and far richer dynamics. NEVER use for grid operation.
"""
# %% [markdown]
# # Session 3: what happens in the seconds after a power station trips
# **A. Real-world problem.** A large generator suddenly disconnects. Demand has not changed, so
# the grid is short of power. The rotating machines give up some of their stored kinetic energy,
# the frequency falls, the governors open the steam or water valves, and the frequency recovers
# to a value slightly below 50 Hz. With wind and solar (little rotating mass) the fall is faster.
#
# **Plan.** (1) write the swing equation in per unit, (2) solve it with our own RK4, (3) check the
# start slope and the final value against hand formulas, (4) compare with and without governor,
# (5) vary inertia and droop, (6) a three-bus DC power flow, (7) a failure case and a mini-project.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

F0 = 50.0   # nominal frequency (Hz)


# %% [markdown]
# ## Step 1: the swing equation in per unit
# Let dw = (f - f0) / f0 be the per-unit frequency deviation. For one aggregate generator
# with inertia constant H (seconds of stored energy at rated power), damping D (the load falls
# a little as frequency falls), mechanical power change Pm and a sudden loss dP (all per unit
# on the generation base):
#     2 H d(dw)/dt = Pm - dP - D dw          (same as 2H/f0 d(df)/dt = ...)
# The governor with droop R and a combined turbine/governor lag Tg:
#     Tg dPm/dt = -dw / R - Pm
# An optional fast battery adds power Pb = clip(-dw / Rb, 0, B), reached with lag Tb:
#     Tb dPb/dt = clip(-dw / Rb, 0, B) - Pb;     it enters the swing equation as + Pb.
# Hand formulas to test the solver:
#     initial rate of change   RoCoF = -f0 dP / (2 H)       (the governor has not moved yet)
#     final deviation          df = -f0 dP / (1/R + D)      (Pm settles at -dw/R)

# %%
def simulate_frequency(h_s=5.0, dp=0.05, droop=0.05, damp=1.0, tg=5.0, governor=True,
                       batt_pu=0.0, rb=0.02, tb=0.5, t_end=100.0, dt=0.02):
    """RK4 solution of the toy frequency model after a sudden loss dp (per unit).

    Returns (time in s, frequency in Hz, governor power Pm in pu, battery power Pb in pu).
    """
    def f(y):
        dw, pm, pb = y
        gov_cmd = -dw / droop if governor else 0.0
        bat_cmd = min(max(-dw / rb, 0.0), batt_pu)
        return np.array([(pm + pb - dp - damp * dw) / (2.0 * h_s),
                         (gov_cmd - pm) / tg,
                         (bat_cmd - pb) / tb])

    n = int(round(t_end / dt))
    y = np.zeros(3)
    out = np.zeros((n + 1, 3))
    for i in range(n):
        k1 = f(y)
        k2 = f(y + dt / 2 * k1)
        k3 = f(y + dt / 2 * k2)
        k4 = f(y + dt * k3)
        y = y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out[i + 1] = y
    t = np.arange(n + 1) * dt
    return t, F0 * (1.0 + out[:, 0]), out[:, 1], out[:, 2]


def rocof_analytic(dp, h_s):
    """Initial rate of change of frequency (Hz/s): -f0 dP / (2 H)."""
    return -F0 * dp / (2.0 * h_s)


def steady_deviation(dp, droop, damp=1.0):
    """Final frequency change (Hz) with governor droop: -f0 dP / (1/R + D)."""
    return -F0 * dp / (1.0 / droop + damp)


def nadir(freq):
    """Lowest frequency (Hz) reached."""
    return float(np.min(freq))


# %% [markdown]
# ## Step 2: compare, then vary inertia and droop
# Without a governor the frequency only stops falling because the load itself relaxes (damping D):
# the final value is -f0 dP / D. With the governor the fall is stopped much earlier.

# %%
def nadir_for(h_s, dp=0.05, droop=0.05, **kw):
    """Convenience: nadir (Hz) of one run."""
    return nadir(simulate_frequency(h_s=h_s, dp=dp, droop=droop, **kw)[1])


def trips_under_frequency(freq, limit=49.0):
    """True if the frequency ever goes below the under-frequency trip limit (Hz)."""
    return bool(np.min(freq) < limit)


# %% [markdown]
# ## Step 3: a three-bus DC power flow (stretch)
# The "DC" approximation of AC load flow: lines are reactances x (per unit), voltages are 1 pu, angle
# differences are small, and real power in a line from i to j is (theta_i - theta_j) / x.
# For the whole network B theta = P, with B built from 1/x. Bus 1 is the slack (angle 0).

# %%
LINES = [(0, 1, 0.10), (0, 2, 0.20), (1, 2, 0.25)]   # (from bus, to bus, reactance in pu)


def dc_power_flow(p_inject, lines=LINES):
    """Solve B theta = P with bus 0 as slack. p_inject: net power at each bus (pu); the slack takes the rest.

    Returns (angles in radians, list of line flows in pu, slack power).
    """
    n = len(p_inject)
    b = np.zeros((n, n))
    for i, j, x in lines:
        b[i, i] += 1.0 / x
        b[j, j] += 1.0 / x
        b[i, j] -= 1.0 / x
        b[j, i] -= 1.0 / x
    p = np.asarray(p_inject, dtype=float).copy()
    theta = np.zeros(n)
    theta[1:] = np.linalg.solve(b[1:, 1:], p[1:])
    flows = [(theta[i] - theta[j]) / x for i, j, x in lines]
    return theta, flows, float(b[0] @ theta)


# %% [markdown]
# ## Step 4: see it, then the mini-project
# Mini-project: the smallest fast battery that keeps the nadir at or above 49.5 Hz after an 8 percent
# loss on a low-inertia grid (H = 3 s).

# %%
def smallest_battery(dp, h_s, target=49.5, step=0.005, max_pu=0.5, **kw):
    """Smallest battery size (pu, multiples of step) that keeps the nadir >= target Hz, or None."""
    k = 0
    while k * step <= max_pu + 1e-12:
        if nadir_for(h_s, dp=dp, batt_pu=k * step, **kw) >= target:
            return round(k * step, 6)
        k += 1
    return None


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t, f_gov, pm, _ = simulate_frequency()
    _, f_free, _, _ = simulate_frequency(governor=False)
    print(f"5% loss, H = 5 s: RoCoF analytic {rocof_analytic(0.05, 5.0):.3f} Hz/s, "
          f"numeric {(f_gov[5] - f_gov[0]) / t[5]:.3f} Hz/s")
    print(f"with governor: nadir {nadir(f_gov):.3f} Hz at t = {t[np.argmin(f_gov)]:.1f} s, "
          f"final {f_gov[-1]:.3f} Hz (analytic {F0 + steady_deviation(0.05, 0.05):.3f} Hz)")
    print(f"without governor: nadir {nadir(f_free):.3f} Hz, final {f_free[-1]:.3f} Hz "
          f"(analytic {F0 + -F0 * 0.05 / 1.0:.3f} Hz)")

    for h in (2.0, 3.0, 5.0, 8.0):
        print(f"H = {h:.0f} s: nadir {nadir_for(h):.3f} Hz")
    for r in (0.03, 0.05, 0.08):
        print(f"droop {r * 100:.0f}%: nadir {nadir_for(5.0, droop=r):.3f} Hz, final {F0 + steady_deviation(0.05, r):.3f} Hz")
    f_low = simulate_frequency(h_s=2.0, dp=0.10)[1]
    f_high = simulate_frequency(h_s=5.0, dp=0.10)[1]
    print(f"failure case, 10% loss: H = 2 s nadir {nadir(f_low):.3f} Hz (trip below 49 Hz: {trips_under_frequency(f_low)}); "
          f"H = 5 s nadir {nadir(f_high):.3f} Hz (trip: {trips_under_frequency(f_high)})")

    th, fl, ps = dc_power_flow([0.0, 0.5, -1.0])
    print("DC flow angles (rad):", np.round(th, 4), " flows 1-2, 1-3, 2-3 (pu):", np.round(fl, 4), " slack:", round(ps, 4))

    best = smallest_battery(0.08, 3.0)
    print(f"mini-project: 8% loss, H = 3 s, no battery nadir {nadir_for(3.0, dp=0.08):.3f} Hz; "
          f"smallest battery {best} pu gives {nadir_for(3.0, dp=0.08, batt_pu=best):.3f} Hz")

    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(t, f_gov, label="with governor (droop 5%)")
    ax.plot(t, f_free, "--", label="without governor")
    ax.axhline(49.0, color="r", ls=":", label="49 Hz trip level (toy)")
    ax.set_xlim(0, 60)
    ax.set_xlabel("time after the loss (s)")
    ax.set_ylabel("frequency (Hz)")
    ax.set_title("5 percent generation loss, H = 5 s")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "frequency_response.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(7, 4.2))
    for h in (2.0, 3.0, 5.0, 8.0):
        tt, ff, _, _ = simulate_frequency(h_s=h, dp=0.10)
        ax2.plot(tt, ff, label=f"H = {h:.0f} s")
    ax2.axhline(49.0, color="r", ls=":", label="49 Hz trip level (toy)")
    ax2.set_xlim(0, 40)
    ax2.set_xlabel("time after the loss (s)")
    ax2.set_ylabel("frequency (Hz)")
    ax2.set_title("Less inertia: faster and deeper fall (10 percent loss)")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "inertia_effect.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Change the loss to 12 percent, the droop to 3 percent and the battery size, and watch the nadir.
# Then answer the four questions in the README (section F) and run the checkpoint.
