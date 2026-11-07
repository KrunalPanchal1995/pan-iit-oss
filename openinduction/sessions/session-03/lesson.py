"""Session 3 (Level 3): simulate a loaded generator, count the losses in a transformer, break the core.

Run:  python start.py 3
Low-voltage educational model only (never mains). All loss numbers are illustrative, not
measurements of any real machine, and this is not a design tool for real generators or transformers.
"""
# %% [markdown]
# # Session 3: a loaded generator, transformer losses, and saturation
# **A. Real-world problem.** A bicycle dynamo lights a 3 W lamp. The coil has resistance and
# inductance, so the lamp never gets the full EMF. Real transformers run warm because their
# wire has resistance and their iron wastes energy. And if you push too much flux into the
# iron, the output waveform is no longer a clean sine.
#
# **Plan.** (1) solve the generator circuit in time (RK4) and compare with the exact steady
# state, (2) check energy conservation and Lenz's law, (3) a transformer with losses, (4) a
# core that saturates, (5) the mini-project: size a dynamo.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the generator circuit
# A coil with armature resistance Ra and inductance L drives a resistive load RL. The coil EMF is
# e(t) = k w sin(w t) with k = N B A. Kirchhoff's voltage law:  L di/dt = e - (Ra + RL) i.
# We integrate it with the classical 4th-order Runge-Kutta method (RK4). We also integrate
# three energies at the same time: into the load, into the coil resistance, and the mechanical
# work needed to turn the coil. The torque of the magnetic field on the coil is
# tau = -k i sin(w t) (negative = it opposes the rotation, which is Lenz's law), so the
# mechanical power we must supply is -tau * w = k w i sin(w t) = e i.
#
# Exact steady state (hand calculation): impedance Z = sqrt((Ra + RL)^2 + (w L)^2), peak current
# Em / Z, RMS current Em / (Z sqrt 2), load power Irms^2 RL.

# %%
def steady_state(turns, b_field, area, freq, ra, rl, ind):
    """Exact sinusoidal steady state of the generator circuit."""
    w = 2 * np.pi * freq
    em = turns * b_field * area * w
    z = float(np.hypot(ra + rl, w * ind))
    irms = em / z / np.sqrt(2.0)
    return {"em": em, "z": z, "i_peak": em / z, "i_rms": irms, "p_load": irms ** 2 * rl,
            "p_arm": irms ** 2 * ra, "phase_deg": float(np.degrees(np.arctan2(w * ind, ra + rl))),
            "v_load_rms": irms * rl}


def simulate_generator(turns, b_field, area, freq, ra, rl, ind, periods=24, steps=400, window=4):
    """RK4 time simulation. Returns a dict with time, current, torque and measured results.

    Measurements use the last `window` whole periods, after the start-up transient has died away.
    """
    w = 2 * np.pi * freq
    k = turns * b_field * area
    h = 1.0 / freq / steps
    n = periods * steps

    def f(t, y):
        s = np.sin(w * t)
        i = y[0]
        e = k * w * s
        return np.array([(e - (ra + rl) * i) / ind,      # coil current
                         rl * i * i,                      # energy into the load
                         ra * i * i,                      # energy into the coil resistance
                         k * w * s * i])                  # mechanical work: -torque * w

    y = np.zeros(4)
    ts = np.arange(n + 1) * h
    ys = np.zeros((n + 1, 4))
    for j in range(n):
        t = ts[j]
        k1 = f(t, y)
        k2 = f(t + h / 2, y + h / 2 * k1)
        k3 = f(t + h / 2, y + h / 2 * k2)
        k4 = f(t + h, y + h * k3)
        y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        ys[j + 1] = y
    torque = -k * ys[:, 0] * np.sin(w * ts)          # magnetic torque on the coil (N m)
    j0 = n - window * steps
    span = ts[n] - ts[j0]
    return {"t": ts, "i": ys[:, 0], "torque": torque, "omega": w,
            "i_rms": float(np.sqrt((ys[n, 1] - ys[j0, 1]) / rl / span)),
            "p_load": float((ys[n, 1] - ys[j0, 1]) / span),
            "p_arm": float((ys[n, 2] - ys[j0, 2]) / span),
            "p_mech": float((ys[n, 3] - ys[j0, 3]) / span),
            "stored": float(0.5 * ind * ys[n, 0] ** 2 - 0.5 * ind * ys[j0, 0] ** 2),
            "w_mech": float(ys[n, 3] - ys[j0, 3]), "e_load": float(ys[n, 1] - ys[j0, 1]),
            "e_arm": float(ys[n, 2] - ys[j0, 2]), "span": float(span)}


def energy_balance(sim, ind=None):
    """Mechanical work in minus (load energy + coil heat + change in stored magnetic energy), in joules."""
    return sim["w_mech"] - sim["e_load"] - sim["e_arm"] - sim["stored"]


# %% [markdown]
# ## Step 2: a transformer with losses (illustrative numbers)
# Real transformer, referred to the primary side. Turns ratio a = N1/N2.
# * copper loss: the winding resistances, Req = R1 + a^2 R2, carry the load current;
# * leakage: a series reactance Xeq (flux that links only one winding) causes a voltage drop;
# * core loss: a resistor Rc across the primary, P_core = V1^2 / Rc, present even with no load.
# Efficiency = P_out / P_in. Voltage regulation = (V2 no load - V2 full load) / V2 no load.
# Values below are illustrative for a small 230 V : 12 V transformer.

# %%
XFMR = {"n1": 460, "n2": 24, "r1": 30.0, "r2": 0.08, "x_eq": 40.0, "rc": 35000.0}


def transformer_load(r_load, v1=230.0, p=None):
    """Phasor solution of the equivalent circuit with a resistive load r_load (ohm) on the secondary."""
    p = XFMR if p is None else p
    a = p["n1"] / p["n2"]
    req = p["r1"] + a * a * p["r2"]
    zs = complex(req, p["x_eq"])
    rl_ref = a * a * r_load
    i_ref = v1 / (zs + rl_ref)                       # load current referred to the primary (A)
    i_core = v1 / p["rc"]
    p_out = abs(i_ref) ** 2 * rl_ref
    p_cu = abs(i_ref) ** 2 * req
    p_core = v1 ** 2 / p["rc"]
    p_in = (v1 * np.conj(i_ref + i_core)).real
    v2 = abs(i_ref) * rl_ref / a
    return {"v2": float(v2), "i2": float(abs(i_ref) * a), "i1": float(abs(i_ref + i_core)),
            "p_out": float(p_out), "p_cu": float(p_cu), "p_core": float(p_core), "p_in": float(p_in),
            "eff": float(p_out / p_in), "v2_noload": float(v1 / a),
            "regulation": float((v1 / a - v2) / (v1 / a))}


# %% [markdown]
# ## Step 3: a core that saturates (the failure case, illustrative)
# Iron cannot carry unlimited flux. We model the winding flux linkage as
# lambda = lambda_s tanh(i / i_s): proportional to current for small currents, but never above
# lambda_s. A source of peak voltage vp with series resistance rs gives d(lambda)/dt = v - rs i.
# This equation is *stiff* near saturation (the incremental inductance collapses), so we use
# the implicit backward-Euler method, solving for i with bisection at every step. The voltage
# on the secondary (open circuit) is d(lambda)/dt / a. This is a teaching model with made-up
# numbers, not a model of a real core.

# %%
def saturating_core(drive, freq=50.0, v_rated_peak=12 * np.sqrt(2), lam_s=0.108, i_s=0.05, rs=4.0,
                    periods=8, steps=2000):
    """Drive the saturating core with `drive` times the rated voltage. Returns time, current, winding voltage."""
    w = 2 * np.pi * freq
    h = 1.0 / freq / steps
    vp = drive * v_rated_peak
    n = periods * steps
    ts = np.arange(n + 1) * h
    cur = np.zeros(n + 1)
    lam = 0.0
    for j in range(1, n + 1):
        v = vp * np.cos(w * ts[j])
        lo, hi = -50.0, 50.0                          # residual g(i) = lam_s tanh(i/i_s) - lam - h (v - rs i)
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            g = lam_s * np.tanh(mid / i_s) - lam - h * (v - rs * mid)
            if g > 0:
                hi = mid
            else:
                lo = mid
        cur[j] = 0.5 * (lo + hi)
        lam = lam_s * np.tanh(cur[j] / i_s)
    v_wind = vp * np.cos(w * ts) - rs * cur
    return {"t": ts, "i": cur, "v_wind": v_wind, "steps": steps, "periods": periods}


def thd(wave, steps, periods, skip=2):
    """Total harmonic distortion of a waveform: sqrt(sum of harmonics 2.. squared) / fundamental.

    Uses whole periods after the first `skip` periods.
    """
    x = np.asarray(wave[skip * steps: periods * steps], dtype=float)
    spec = np.abs(np.fft.rfft(x))
    m = periods - skip                                 # fundamental sits in bin m
    fund = spec[m]
    harm = np.sqrt(np.sum(spec[2 * m::m][:20] ** 2))
    return float(harm / fund)


# %% [markdown]
# ## Step 4: mini-project - a bicycle dynamo for a 3 W lamp
# A roller of radius 0.01 m runs on the tyre; the bike speed v gives w = v / 0.01 (rad/s) and the
# electrical frequency f = w / (2 pi). The lamp is 6 V, 3 W: RL = 6^2 / 3 = 12 ohm. The coil has
# B = 0.3 T, A = 4e-4 m^2, Ra = 1.5 ohm and L = 40 mH (illustrative; in reality L grows with N^2,
# which this simple model ignores).

# %%
DYNAMO = {"b": 0.3, "area": 4e-4, "ra": 1.5, "ind": 0.040, "rl": 12.0, "roller": 0.01}


def dynamo_power(turns, speed_kmh, d=None):
    """Lamp power (W) at a bike speed (km/h), from the exact steady state."""
    d = DYNAMO if d is None else d
    f = (speed_kmh / 3.6) / d["roller"] / (2 * np.pi)
    return steady_state(turns, d["b"], d["area"], f, d["ra"], d["rl"], d["ind"])["p_load"]


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    GEN = dict(turns=250, b_field=0.2, area=0.0016, freq=50.0, ra=2.0, rl=10.0, ind=0.03)
    ss = steady_state(**GEN)
    sim = simulate_generator(**GEN)
    print(f"generator: peak EMF {ss['em']:.2f} V, Z {ss['z']:.2f} ohm, phase lag {ss['phase_deg']:.1f} deg")
    print(f"  steady-state I_rms {ss['i_rms']:.4f} A, load power {ss['p_load']:.3f} W")
    print(f"  RK4 measured  I_rms {sim['i_rms']:.4f} A, load power {sim['p_load']:.3f} W, error {abs(sim['p_load'] / ss['p_load'] - 1):.2e}")
    print(f"  mechanical power {sim['p_mech']:.3f} W = load {sim['p_load']:.3f} + coil heat {sim['p_arm']:.3f} (+ stored change {sim['stored']:.1e} J)")
    print(f"  energy balance residual {energy_balance(sim):.2e} J of {sim['w_mech']:.4f} J")
    print(f"  mean torque {sim['torque'][-4 * 400:].mean() * 1000:.2f} mN m (negative = opposes rotation)")

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7, 6))
    tm = sim["t"]
    em_t = ss["em"] * np.sin(sim["omega"] * tm)
    a1.plot(tm[:1200] * 1000, em_t[:1200] / ss["z"], color="tab:gray", label="EMF / Z (no inductance lag)")
    a1.plot(tm[:1200] * 1000, sim["i"][:1200], color="tab:blue", label="RK4 current")
    ia = ss["i_peak"] * np.sin(sim["omega"] * tm - np.radians(ss["phase_deg"]))
    a1.plot(tm[:1200:15] * 1000, ia[:1200:15], "k.", ms=3, label="exact steady state")
    a1.set_xlabel("time (ms)")
    a1.set_ylabel("current (A)")
    a1.set_title("Loaded generator: start-up and steady state")
    a1.grid(alpha=0.3)
    a1.legend(fontsize=8)
    ln = slice(-1600, None)
    a2.plot((tm[ln] - tm[ln][0]) * 1000, sim["torque"][ln] * sim["omega"], color="tab:red", label="magnetic power on the coil = torque x w")
    a2.plot((tm[ln] - tm[ln][0]) * 1000, em_t[ln] * sim["i"][ln], color="tab:green", ls="--", label="e i (power we supply)")
    a2.axhline(0, color="k", lw=0.5)
    a2.set_xlabel("time over four periods (ms)")
    a2.set_ylabel("power (W)")
    a2.set_title("Lenz's law: the field takes power from the shaft")
    a2.grid(alpha=0.3)
    a2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "generator_rk4.png", dpi=120)

    rls = np.logspace(np.log10(0.7), np.log10(500), 80)
    rows = [transformer_load(r) for r in rls]
    pout = np.array([r["p_out"] for r in rows])
    eff = np.array([r["eff"] for r in rows])
    reg = np.array([r["regulation"] for r in rows])
    rated = transformer_load(6.0)
    print(f"transformer at 6 ohm: V2 {rated['v2']:.2f} V, I2 {rated['i2']:.2f} A, P_out {rated['p_out']:.2f} W, "
          f"copper {rated['p_cu']:.2f} W, core {rated['p_core']:.2f} W, efficiency {rated['eff']:.1%}, regulation {rated['regulation']:.1%}")
    ib = int(np.argmax(eff))
    print(f"  best efficiency {eff[ib]:.1%} at P_out {pout[ib]:.1f} W; copper = core loss when I1 = {np.sqrt(rated['p_core'] / (XFMR['r1'] + (XFMR['n1'] / XFMR['n2']) ** 2 * XFMR['r2'])):.3f} A")
    fig2, (b1, b2) = plt.subplots(1, 2, figsize=(9, 4))
    b1.semilogx(pout, eff * 100, color="tab:blue")
    b1.plot(pout[ib], eff[ib] * 100, "ro")
    b1.set_xlabel("output power (W)")
    b1.set_ylabel("efficiency (%)")
    b1.set_title("Efficiency against load (illustrative)")
    b1.grid(alpha=0.3)
    b2.plot(pout, reg * 100, color="tab:red")
    b2.set_xlabel("output power (W)")
    b2.set_ylabel("voltage regulation (%)")
    b2.set_title("Output voltage drops as load rises")
    b2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "transformer_losses.png", dpi=120)

    fig3, ax = plt.subplots(1, 3, figsize=(10, 3.6), sharey=False)
    for axx, drive in zip(ax, (1.0, 2.0, 3.0)):
        r = saturating_core(drive)
        s0 = 5 * r["steps"]
        sl = slice(s0, s0 + r["steps"] + 1)
        tt = (r["t"][sl] - r["t"][s0]) * 1000
        axx.plot(tt, r["v_wind"][sl] * 24 / 460, color="tab:red", label="secondary voltage (V)")
        axx.set_xlabel("time (ms)")
        axx.set_title(f"drive {drive} x rated\nTHD {thd(r['v_wind'], r['steps'], r['periods']):.1%}", fontsize=9)
        axx.grid(alpha=0.3)
        ax2 = axx.twinx()
        ax2.plot(tt, r["i"][sl], color="tab:blue", lw=0.8)
        ax2.set_ylabel("magnetising current (A)", color="tab:blue", fontsize=8)
    ax[0].set_ylabel("secondary open-circuit voltage (V)")
    fig3.tight_layout()
    fig3.savefig(OUT / "core_saturation.png", dpi=120)
    for drive in (1.0, 2.0, 2.5, 3.0):
        r = saturating_core(drive)
        print(f"core drive {drive}: peak magnetising current {abs(r['i']).max():.3f} A, secondary THD {thd(r['v_wind'], r['steps'], r['periods']):.2%}")

    for n in (300, 310, 320, 330):
        print(f"dynamo N={n}: lamp power at 8/15/25 km/h = {dynamo_power(n, 8):.2f} / {dynamo_power(n, 15):.2f} / {dynamo_power(n, 25):.2f} W")

# %% [markdown]
# ## Where this stops
# The generator is a single coil with a fixed inductance, the transformer is a linear circuit
# with made-up loss values, and the saturation curve is a tanh. They show the right trends and
# let you test energy conservation, but they are not models for designing real machines.
