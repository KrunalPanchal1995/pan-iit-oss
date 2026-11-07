"""Session 3 (Level 3): a hydraulic lift circuit in time: pump, cylinder, relief valve, leakage, friction, compressible oil.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: simulate a hydraulic lift
# **A. Real-world problem.** A garage lift is not a jack with two pistons: an electric pump
# pushes oil at a steady flow Q into a big cylinder under the car. A relief valve protects the
# system from too much pressure. Oil leaks past seals, seals rub, and oil can be squashed a
# tiny bit, which makes the car bounce slightly on its hydraulic "spring". How fast does the
# car rise, where does the energy go, and what happens when the load is too heavy?
#
# **Plan.** (1) write the model, (2) step it in time, (3) check it against exact results
# (lift speed v = Q / A, energy balance, plateau pressure), (4) change leakage and oil
# temperature, (5) trigger the relief valve. This is a simplified educational model, not a
# design tool: real lifts need certified design, check valves and mechanical safety locks.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81                          # m/s^2
D_CYL = 0.050                     # m, cylinder (ram) diameter
A_CYL = np.pi * D_CYL ** 2 / 4.0  # m^2, ram area
BASE = {
    "mass": 1200.0,       # kg, load
    "d": D_CYL,           # m, ram diameter
    "Q": 1.0e-4,          # m^3/s, pump flow (6 L/min)
    "p_relief": 8.0e6,    # Pa, relief valve setting (80 bar)
    "B": 1.5e9,           # Pa, bulk modulus of the oil
    "V0": 1.5e-3,         # m^3, oil volume at zero lift (cylinder, hose, pump)
    "c_leak40": 3.0e-13,  # m^3/s per Pa, leakage coefficient at 40 C
    "wear": 1.0,          # leakage multiplier (1 = new seals)
    "T": 40.0,            # C, oil temperature
    "c_f": 10000.0,       # N s/m, viscous friction of the seals
}


# %% [markdown]
# ## Step 1: the model
# Unknowns: ram position x, speed v, oil pressure p. Pump flow Q goes three ways: it moves the
# piston (A v), it leaks (c p) and it may escape through the relief valve (k_r (p - p_set) when
# p > p_set). Oil is slightly compressible with bulk modulus B, so
#
#     dp/dt = (B / V) (Q - A v - c p - Q_relief),      V = V0 + A x
#     m dv/dt = p A - m g - c_f v                       (the floor holds the load at x = 0)
#
# Together these are a spring-mass-damper: the oil acts as a spring of stiffness
# k = B A^2 / V, friction as the damper. Viscosity of oil falls steeply as it warms
# (rough fit: halves every 22 C), and laminar leakage is inversely proportional to viscosity,
# so hot oil leaks more: c = c40 * wear * exp(0.0318 (T - 40)).

# %%
def leak_coefficient(c_leak40, wear, T):
    """Leakage coefficient (m^3/s per Pa) at oil temperature T (C)."""
    return c_leak40 * wear * np.exp(0.0318 * (T - 40.0))


def stiffness(B, area, volume):
    """Hydraulic spring stiffness k = B A^2 / V in N/m."""
    return B * area ** 2 / volume


def relief_gain(Q, p_relief):
    """Relief valve flow per excess pressure (m^3/s per Pa): full pump flow at 10 percent over the setting."""
    return Q / (0.1 * p_relief)


# %% [markdown]
# ## Step 2: step it in time
# Semi-implicit Euler with a small step dt = 0.2 ms: update the pressure, then the speed, then
# the position. We also accumulate energies: the pump's hydraulic work W_in = integral of p Q dt,
# the energy lost in friction, leakage and the relief valve, and the energy stored by squeezing
# the oil.

# %%
def simulate(t_end=6.0, dt=2.0e-4, **kw):
    """Lift a load for t_end seconds. kw overrides BASE. Returns a dict of numpy arrays (SI units)."""
    q = dict(BASE)
    q.update(kw)
    m, Q, B, V0, c_f = q["mass"], q["Q"], q["B"], q["V0"], q["c_f"]
    area = np.pi * q["d"] ** 2 / 4.0            # ram area (m^2)
    c = leak_coefficient(q["c_leak40"], q["wear"], q["T"])
    kr = relief_gain(Q, q["p_relief"])
    n = int(round(t_end / dt))
    keep = 25                                   # store every 25th step
    t_s, x_s, v_s, p_s, qr_s = [], [], [], [], []
    x = v = p = 0.0
    w_in = w_fric = w_leak = w_rel = e_fluid = 0.0
    for i in range(n + 1):
        V = V0 + area * x
        q_rel = kr * max(0.0, p - q["p_relief"])
        q_leak = c * p
        if i % keep == 0:
            t_s.append(i * dt); x_s.append(x); v_s.append(v); p_s.append(p); qr_s.append(q_rel)
        dp = B / V * (Q - area * v - q_leak - q_rel) * dt
        acc = (p * area - m * G - c_f * v) / m
        if x <= 0.0 and v <= 0.0 and acc < 0.0:     # the floor carries the load
            v, acc = 0.0, 0.0
        w_in += p * Q * dt
        w_leak += p * q_leak * dt
        w_rel += p * q_rel * dt
        w_fric += c_f * v * v * dt
        e_fluid += p * V / B * dp                   # energy stored by compressing the oil
        p += dp
        v += acc * dt
        x = max(0.0, x + v * dt)
    t = np.array(t_s)
    return {"t": t, "x": np.array(x_s), "v": np.array(v_s), "p": np.array(p_s), "q_relief": np.array(qr_s),
            "W_in": w_in, "W_friction": w_fric, "W_leak": w_leak, "W_relief": w_rel, "E_fluid": e_fluid,
            "PE": m * G * x, "KE": 0.5 * m * v * v, "c": c, "kr": kr, "params": q}


# %% [markdown]
# ## Step 3: check against exact results
# (a) Without leakage the steady lift speed is exactly v = Q / A. With leakage and friction a
# short algebra gives v = (Q - c m g / A) / (A + c c_f / A). (b) Energy: W_in = lifted potential
# energy + kinetic energy + friction + leakage + relief + stored oil energy. (c) If the load is
# too heavy the piston stays down and the pressure sits on a plateau
# p = (Q + k_r p_set) / (c + k_r). (d) The oil spring rings at f = sqrt(k / m) / (2 pi).

# %%
def lift_speed(Q=BASE["Q"], area=A_CYL, mass=BASE["mass"], c=0.0, c_f=BASE["c_f"]):
    """Steady lift speed (m/s). With no leakage (c = 0) this is exactly Q / A, whatever the friction."""
    return (Q - c * mass * G / area) / (area + c * c_f / area)


def energy_residual(s):
    """Input work minus everything accounted for (J)."""
    out = s["PE"] + s["KE"] + s["W_friction"] + s["W_leak"] + s["W_relief"] + s["E_fluid"]
    return s["W_in"] - out


def plateau_pressure(Q, kr, p_relief, c):
    """Pressure when the whole pump flow goes over the relief valve and through leakage."""
    return (Q + kr * p_relief) / (c + kr)


def mean_speed(s, t_from):
    """Average lift speed (m/s) from t_from to the end (smooths out the ringing)."""
    i = int(np.searchsorted(s["t"], t_from))
    return float((s["x"][-1] - s["x"][i]) / (s["t"][-1] - s["t"][i]))


def critical_leak(Q, area, mass):
    """Leakage coefficient at which leakage swallows the whole pump flow at the load pressure (no lift)."""
    return Q * area / (mass * G)


def ring_frequency(t, p):
    """Dominant frequency (Hz) of the pressure ripple, after removing the slow trend (FFT, zero padded)."""
    r = (p - np.polyval(np.polyfit(t, p, 4), t)) * np.hanning(len(p))
    spec = np.abs(np.fft.rfft(r, 16 * len(r)))
    f = np.fft.rfftfreq(16 * len(r), t[1] - t[0])
    return float(f[3:][np.argmax(spec[3:])])


# %% [markdown]
# ## Step 4: sensitivity and the failure case
# `lift_after(...)` returns the height lifted in 6 s. We vary seal wear and temperature, then
# put a 1800 kg load on a lift whose relief valve is set to 70 bar.

# %%
def lift_after(**kw):
    """Height (m) after the simulated time."""
    return float(simulate(**kw)["x"][-1])


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    s = simulate()
    v_end = mean_speed(s, 3.0)
    print(f"area {A_CYL * 1e4:.2f} cm^2; load pressure {BASE['mass'] * G / A_CYL / 1e5:.1f} bar")
    print(f"steady speed: simulated {v_end * 1000:.2f} mm/s, ideal Q/A {BASE['Q'] / A_CYL * 1000:.2f} mm/s, "
          f"with leakage and friction {lift_speed(c=s['c']) * 1000:.2f} mm/s")
    s0 = simulate(c_leak40=0.0)
    print(f"no leakage: mean speed {mean_speed(s0, 3.0) * 1000:.3f} mm/s, ideal Q/A {BASE['Q'] / A_CYL * 1000:.3f} mm/s; "
          f"lift {s0['x'][-1] * 1000:.1f} mm, Q t / A = {BASE['Q'] * 6.0 / A_CYL * 1000:.1f} mm, "
          f"oil squeeze {s0['p'][-1] * (BASE['V0'] + A_CYL * s0['x'][-1]) / BASE['B'] / A_CYL * 1000:.1f} mm")
    print(f"lifted {s['x'][-1] * 100:.1f} cm; energy in {s['W_in']:.0f} J = lift {s['PE']:.0f} + friction {s['W_friction']:.1f} "
          f"+ leakage {s['W_leak']:.1f} + oil {s['E_fluid']:.1f} + kinetic {s['KE']:.2f} J; residual {energy_residual(s):.3f} J")
    r = simulate(t_end=3.0, Q=3.0e-5, c_f=1000.0)
    sl = slice(int(np.searchsorted(r["t"], 0.2)), None)
    k = stiffness(BASE["B"], A_CYL, BASE["V0"] + A_CYL * r["x"][sl].mean())
    print(f"oil spring k = {k / 1e6:.2f} MN/m; predicted ring {np.sqrt(k / BASE['mass']) / (2 * np.pi):.2f} Hz; "
          f"measured {ring_frequency(r['t'][sl], r['p'][sl]):.2f} Hz")
    print(f"critical leakage {critical_leak(BASE['Q'], A_CYL, BASE['mass']):.2e}; at wear x30, 80 C the coefficient is "
          f"{leak_coefficient(BASE['c_leak40'], 30.0, 80.0):.2e}")
    print("sensitivity (lift in 6 s):")
    for label, kw in (("new seals, 40 C", {}), ("wear x10, 40 C", {"wear": 10.0}), ("wear x10, 80 C", {"wear": 10.0, "T": 80.0}),
                      ("wear x30, 80 C", {"wear": 30.0, "T": 80.0}), ("new seals, 20 C", {"T": 20.0})):
        print(f"  {label:16s} {lift_after(**kw) * 100:6.2f} cm")
    f = simulate(mass=1800.0, p_relief=7.0e6)
    pp = plateau_pressure(BASE["Q"], f["kr"], 7.0e6, f["c"])
    print(f"failure: 1800 kg needs {1800 * G / A_CYL / 1e5:.0f} bar > relief 70 bar: lift {f['x'][-1] * 100:.1f} cm, "
          f"plateau {f['p'][-1] / 1e5:.1f} bar (formula {pp / 1e5:.1f} bar)")

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(s["t"], s["x"] * 100, label="new seals, 40 C")
    sw = simulate(wear=10.0, T=80.0)
    ax[0].plot(sw["t"], sw["x"] * 100, label="worn seals x10, 80 C")
    ax[0].plot(s["t"], BASE["Q"] / A_CYL * s["t"] * 100, "k:", label="ideal Q/A")
    ax[0].set_xlabel("time (s)")
    ax[0].set_ylabel("lift height (cm)")
    ax[0].set_title("Lift height: leakage slows the car")
    ax[0].grid(alpha=0.3)
    ax[0].legend()
    ax[1].plot(s["t"], s["p"] / 1e5, label="1200 kg")
    ax[1].plot(f["t"], f["p"] / 1e5, label="1800 kg, relief at 70 bar")
    ax[1].axhline(70, color="C3", ls="--", lw=1)
    ax[1].set_xlabel("time (s)")
    ax[1].set_ylabel("oil pressure (bar)")
    ax[1].set_title("Pressure rises, then relief valve caps it")
    ax[1].grid(alpha=0.3)
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(OUT / "lift_and_pressure.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    names = ["lifted (PE)", "friction", "leakage", "oil squeeze"]
    vals = [s["PE"], s["W_friction"], s["W_leak"], s["E_fluid"]]
    ax2.bar(names, vals, color=["C2", "C1", "C3", "C0"])
    ax2.set_ylabel("energy over 6 s (J)")
    ax2.set_title(f"Where the pump's {s['W_in']:.0f} J goes")
    ax2.set_yscale("log")
    ax2.grid(alpha=0.3, axis="y")
    fig2.tight_layout()
    fig2.savefig(OUT / "energy_budget.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), run the checkpoint,
# then start the mini-project.
