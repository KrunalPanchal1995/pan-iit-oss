"""Session 2 (Level 2): fly straight up and measure what gravity and air cost.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: straight up, against gravity and air
# **A. Real-world problem.** Session 1 said our two-stage rocket has about 10.9 km/s of ideal
# delta-v. But the rocket equation assumed empty space. On the launch pad gravity pulls down
# all the time the engines burn, and air pushes back while the rocket is low and fast. How
# much speed do these really cost, why must a rocket's thrust be bigger than its weight, and
# what happens if the rocket simply flies straight up?
#
# **Plan.** (1) thrust-to-weight ratio, (2) a vertical flight stepped in time (Euler, then
# Runge-Kutta 4), (3) check it against the exact answer for constant gravity and no air,
# (4) gravity loss = g x burn time, (5) add drag and inverse-square gravity, (6) straight up
# never gives orbit.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G0 = 9.80665
MU = 3.986004418e14
R_EARTH = 6.371e6
RHO0, H_SCALE = 1.225, 8500.0       # sea-level density (kg/m3) and scale height (m)

LAUNCHER = [dict(prop=90000.0, dry=7000.0, isp=290.0, F=1.6e6),
            dict(prop=15000.0, dry=1500.0, isp=340.0, F=150e3)]
PAYLOAD = 1000.0
CD_A = 2.5            # drag coefficient x frontal area (m2)


# %% [markdown]
# ## Step 1: thrust-to-weight ratio
# On the pad the engine must lift the rocket's weight before it can speed it up:
#
#     TWR = F / (m g0)        net upward acceleration = (TWR - 1) g0
#
# A rocket with TWR below 1 does not leave the pad. Real launchers lift off with TWR about
# 1.2 to 1.6.

# %%
def thrust_to_weight(thrust, mass):
    """Thrust-to-weight ratio F / (m g0) (no unit)."""
    if mass <= 0:
        raise ValueError("mass must be positive")
    return thrust / (mass * G0)


def mass_flow(thrust, isp):
    """Propellant mass flow rate F / (Isp g0) in kg/s."""
    if isp <= 0:
        raise ValueError("specific impulse must be positive")
    return thrust / (isp * G0)


# %% [markdown]
# ## Step 2: the exact answer for constant gravity and no air
# With constant g, the speed after time t is the rocket equation minus what gravity took:
#
#     v(t) = ve ln(m0 / m) - g t,       m = m0 - mdot t
#
# Integrating once more gives the height
#
#     h(t) = ve t - ve (m / mdot) ln(m0 / m) - g t**2 / 2
#
# At burnout t_b = m_prop / mdot. The term g t_b is the **gravity loss**: the longer the burn,
# the more speed gravity takes. After burnout the rocket coasts up a further v_b**2 / (2 g).

# %%
def analytic_burn(isp, thrust, m0, m_prop, g=G0):
    """Exact burnout (time s, speed m/s, height m) for a vertical burn, constant g, no air."""
    if not 0 < m_prop < m0:
        raise ValueError("need 0 < m_prop < m0")
    ve, mdot = isp * G0, mass_flow(thrust, isp)
    tb = m_prop / mdot
    mf = m0 - m_prop
    vb = ve * np.log(m0 / mf) - g * tb
    hb = ve * tb - ve * (mf / mdot) * np.log(m0 / mf) - 0.5 * g * tb * tb
    return tb, vb, hb


def coast_height(h_burnout, v_burnout, g=G0):
    """Highest point (m) after burnout for constant g, no air: h_b + v_b**2 / (2 g)."""
    return h_burnout + max(v_burnout, 0.0) ** 2 / (2.0 * g)


# %% [markdown]
# ## Step 3: stepping the flight in time
# The computer does not need the formula. It takes small time steps dt and updates
#
#     a = F / m - g(h) - D / m,     D = 0.5 rho(h) v |v| Cd A,     dm/dt = -F / (Isp g0)
#
# **Euler** uses the slope at the start of each step. **Runge-Kutta 4 (RK4)** takes four
# slopes per step and averages them; it is far more accurate for the same dt. Gravity is
# either constant g0 or the inverse-square law g = G M / (R + h)**2. Air density falls with
# height: rho = rho0 exp(-h / 8500 m). Stages are dropped when they are empty.

# %%
def density(h):
    """Exponential air density (kg/m3) at height h (m)."""
    return RHO0 * np.exp(-max(h, 0.0) / H_SCALE)


def vertical_flight(stages=None, payload=PAYLOAD, dt=0.1, method="rk4", gravity="inverse",
                    drag=True, t_end=None, cd_a=CD_A):
    """Fly straight up. Returns dict with arrays t, h, v, m and the list of staging events.

    gravity: 'constant' (g0) or 'inverse' (inverse-square). drag: True or False.
    Stops at t_end, or when the rocket falls back to the ground after burnout."""
    stages = LAUNCHER if stages is None else stages
    if dt <= 0 or method not in ("euler", "rk4") or gravity not in ("constant", "inverse"):
        raise ValueError("need dt > 0, method euler or rk4, gravity constant or inverse")
    prop = [s["prop"] for s in stages]
    m = payload + sum(s["prop"] + s["dry"] for s in stages)
    if thrust_to_weight(stages[0]["F"], m) <= 1.0:
        raise ValueError("thrust-to-weight below 1: the rocket cannot lift off")
    h, v, t, k = 0.0, 0.0, 0.0, 0
    T, Hs, Vs, Ms, events = [t], [h], [v], [m], []

    def rates(h, v, m, thrust, mdot):
        g = G0 if gravity == "constant" else MU / (R_EARTH + h) ** 2
        D = 0.5 * density(h) * v * abs(v) * cd_a if drag else 0.0
        return np.array([v, thrust / m - g - D / m, -mdot])

    while True:
        if k < len(stages):
            thrust = stages[k]["F"]
            mdot = mass_flow(thrust, stages[k]["isp"])
        else:
            thrust = mdot = 0.0
        step = dt if mdot == 0 or prop[k] >= mdot * dt else prop[k] / mdot
        if t_end is not None:
            step = min(step, t_end - t)
        s = np.array([h, v, m])
        if method == "euler":
            s = s + step * rates(*s, thrust, mdot)
        else:
            k1 = rates(*s, thrust, mdot)
            k2 = rates(*(s + 0.5 * step * k1), thrust, mdot)
            k3 = rates(*(s + 0.5 * step * k2), thrust, mdot)
            k4 = rates(*(s + step * k3), thrust, mdot)
            s = s + step * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        h, v, m = s
        t += step
        if mdot > 0:
            prop[k] -= mdot * step
        if k < len(stages) and prop[k] <= 1e-6:
            events.append((f"stage {k + 1} burnout", t, h, v))
            if k < len(stages) - 1:
                m -= stages[k]["dry"]
            k += 1
        T.append(t)
        Hs.append(h)
        Vs.append(v)
        Ms.append(m)
        if (t_end is not None and t >= t_end - 1e-9) or h < 0 or t > 5000:
            break
    return dict(t=np.array(T), h=np.array(Hs), v=np.array(Vs), m=np.array(Ms), events=events)


# %% [markdown]
# ## Step 4: the gravity-loss trade-off
# For the same propellant, a bigger engine (higher TWR) burns it faster, so gravity has less
# time to pull: gravity loss g t_b falls as TWR rises. But bigger engines weigh more and the
# rocket goes faster in thick air, so real rockets pick a middle value.

# %%
def gravity_loss_vs_twr(twrs, isp=300.0, m0=100e3, m_prop=75e3):
    """Gravity loss g0 t_b (m/s) for a single stage with lift-off TWR values (constant g)."""
    out = []
    for n in twrs:
        tb = m_prop / mass_flow(n * m0 * G0, isp)
        out.append(G0 * tb)
    return np.array(out)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    # worked example: single stage, 100 t, 75 t propellant, Isp 300 s, thrust 1.5 MN
    single = [dict(prop=75e3, dry=25e3, isp=300.0, F=1.5e6)]
    tb, vb, hb = analytic_burn(300.0, 1.5e6, 100e3, 75e3)
    print(f"TWR at lift-off = {thrust_to_weight(1.5e6, 100e3):.3f}")
    print(f"mass flow = {mass_flow(1.5e6, 300.0):.1f} kg/s, burn time = {tb:.1f} s")
    print(f"exact burnout: v = {vb:.1f} m/s, h = {hb / 1000:.2f} km, gravity loss = {G0 * tb:.0f} m/s, top = {coast_height(hb, vb) / 1000:.1f} km")
    for meth, d in (("euler", 1.0), ("euler", 0.1), ("rk4", 1.0)):
        r = vertical_flight(single, 0.0, dt=d, method=meth, gravity="constant", drag=False, t_end=tb)
        print(f"{meth:5s} dt = {d:3.1f} s: v = {r['v'][-1]:.2f} m/s (error {r['v'][-1] - vb:+.3f}), h = {r['h'][-1] / 1000:.4f} km")

    # the teaching launcher, straight up
    full = vertical_flight()
    nodrag = vertical_flight(drag=False)
    for name, r in (("with drag", full), ("no drag", nodrag)):
        i = np.argmax(r["h"])
        print(f"launcher straight up ({name}): top {r['h'][i] / 1000:.0f} km at t = {r['t'][i]:.0f} s, "
              f"fastest {r['v'].max():.0f} m/s, back on the ground after {r['t'][-1]:.0f} s")

    # Figure 1: the worked example, exact against numerical, plus the launcher straight up
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))
    tt = np.linspace(0.0, tb, 200)
    m_t = 100e3 - mass_flow(1.5e6, 300.0) * tt
    ve = 300.0 * G0
    ax1.plot(tt, (ve * np.log(100e3 / m_t) - G0 * tt) / 1000, "k-", lw=3, alpha=0.35, label="exact formula")
    e1 = vertical_flight(single, 0.0, dt=10.0, method="euler", gravity="constant", drag=False, t_end=tb)
    r1 = vertical_flight(single, 0.0, dt=10.0, method="rk4", gravity="constant", drag=False, t_end=tb)
    ax1.plot(e1["t"], e1["v"] / 1000, "o--", color="#d9534f", ms=4, label="Euler, dt = 10 s")
    ax1.plot(r1["t"], r1["v"] / 1000, "s:", color="#2a9d8f", ms=4, label="RK4, dt = 10 s")
    ax1.plot(tt, ve * np.log(100e3 / m_t) / 1000, color="#264653", ls="-.", lw=1, label="no gravity (rocket equation)")
    ax1.set_xlabel("time (s)")
    ax1.set_ylabel("speed (km/s)")
    ax1.set_title(f"Gravity loss = g t_b = {G0 * tb:.0f} m/s")
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.3)
    for name, r, st in (("with drag", full, "-"), ("no drag", nodrag, "--")):
        ax2.plot(r["t"], r["h"] / 1000, st, color="#264653", label=name)
    for name, t, h, v in full["events"]:
        ax2.plot(t, h / 1000, "o", color="#e9a23b")
        ax2.annotate(name, (t, h / 1000), textcoords="offset points", xytext=(6, -10), fontsize=8)
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("altitude (km)")
    ax2.set_title("Teaching launcher flown straight up: it falls back")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "vertical_flight.png", dpi=120)

    # Figure 2: gravity loss against TWR
    twrs = np.linspace(1.1, 4.0, 60)
    fig2, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(twrs, gravity_loss_vs_twr(twrs), color="#d9534f")
    ax.axvspan(1.2, 1.6, color="#2a9d8f", alpha=0.15)
    ax.text(1.4, 500, "typical\nlift-off TWR", ha="center", fontsize=9)
    ax.set_xlabel("thrust-to-weight ratio at lift-off (no unit)")
    ax.set_ylabel("gravity loss g0 t_b (m/s)")
    ax.set_title("Faster burn, less gravity loss (Isp 300 s, 75% propellant)")
    ax.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "gravity_loss_twr.png", dpi=120)

    up = OUT.resolve().parents
    docs = up[2] / "docs" / "figures" if len(up) > 2 else OUT    # repo/docs/figures, when run from the repo
    if docs != OUT and docs.exists() and (docs.parent.parent / "start.py").exists():
        fig.savefig(docs / "s02_vertical_flight.png", dpi=120)
        fig2.savefig(docs / "s02_gravity_loss_twr.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Straight up, the rocket reaches hundreds of kilometres but has no sideways speed, so it
# falls back. Session 3 turns the rocket over (a gravity turn) and flies it into orbit.
