"""Session 2 (Level 2): hold the height with feedback, using a PID controller.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: altitude hold with P, PD and PID control
# **A. Real-world problem.** In Session 1 a fixed throttle made the drone sink as soon as a
# 0.2 kg parcel was added. A flight controller instead measures the height many times per
# second and corrects the thrust. How should the correction depend on the error so that the
# drone climbs to 2 m quickly, without big overshoot, and ends up exactly at 2 m even though
# the controller believes the drone weighs 1.2 kg when it really weighs 1.4 kg?
#
# **Plan.** (1) the error and the feedback loop, (2) P control and its steady-state error,
# (3) adding D for damping, with the second-order formulas, (4) adding I to remove the error,
# (5) a step-by-step simulation that we check against the formulas.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

G = 9.81            # m/s^2
M_NOMINAL = 1.2     # the mass the controller believes (kg)
T_MAX = 40.0        # largest total thrust of the four rotors (N), from Session 1 at 1000 rad/s


# %% [markdown]
# ## Step 1: the feedback loop
# Every time step the controller computes the **error** e = z_ref - z (wanted height minus
# measured height, in m) and sets the total thrust
#
#     T = m_nom g + u,      u = Kp e + Ki (integral of e dt) - Kd (dz/dt)
#
# m_nom g is the **feed-forward** guess of the hover thrust. u is the **feedback** correction
# in newtons. Kp is in N/m, Ki in N/(m s), Kd in N s/m. We use the measured climb rate dz/dt
# instead of de/dt ("derivative on measurement"), so a sudden change of z_ref does not kick
# the thrust. Thrust is limited to 0..T_MAX: rotors cannot push down or spin forever.

# %%
class PID:
    """A discrete PID controller with derivative on measurement and a clamped integral."""

    def __init__(self, kp, ki=0.0, kd=0.0, i_limit=np.inf):
        if kp < 0 or ki < 0 or kd < 0:
            raise ValueError("gains must not be negative")
        self.kp, self.ki, self.kd, self.i_limit = kp, ki, kd, i_limit
        self.integral = 0.0

    def update(self, error, rate, dt):
        """Return the correction u. error = ref - measured, rate = d(measured)/dt."""
        self.integral = float(np.clip(self.integral + error * dt, -self.i_limit, self.i_limit))
        return self.kp * error + self.ki * self.integral - self.kd * rate


# %% [markdown]
# ## Step 2: what the formulas predict
# With m z'' = T - m g and T = m_nom g + Kp e - Kd z', the height obeys a mass-spring-damper
# equation. Kp acts as a spring, Kd as a damper:
#
#     natural frequency  wn = sqrt(Kp / m)          damping ratio  zeta = Kd / (2 sqrt(Kp m))
#     overshoot (0 < zeta < 1) = exp(-zeta pi / sqrt(1 - zeta^2))
#     settling time (2 percent) ~ 4 / (zeta wn)
#
# If the real mass differs from m_nom, gravity is not fully cancelled. At rest the spring must
# carry the rest, so P or PD control leaves a **steady-state error**
#
#     e_ss = (m - m_nom) g / Kp
#
# The integral term keeps growing while any error remains, so with Ki > 0 the error goes to
# zero. Adding Ki makes the loop third order; it stays stable only if Kd Kp > m Ki (the Routh
# test for m s^3 + Kd s^2 + Kp s + Ki).

# %%
def natural_frequency(kp, mass):
    """wn in rad/s of the PD altitude loop."""
    return float(np.sqrt(kp / mass))


def damping_ratio(kp, kd, mass):
    """zeta (no unit) of the PD altitude loop."""
    return float(kd / (2.0 * np.sqrt(kp * mass)))


def overshoot_formula(zeta):
    """Fractional overshoot of a second-order step response (0 if zeta >= 1)."""
    if zeta >= 1.0:
        return 0.0
    return float(np.exp(-zeta * np.pi / np.sqrt(1.0 - zeta ** 2)))


def steady_state_error(kp, mass, m_nominal=M_NOMINAL, g=G):
    """Height error (m) left by P or PD control when the mass is wrong."""
    if kp <= 0:
        raise ValueError("Kp must be positive")
    return (mass - m_nominal) * g / kp


def pid_is_stable(kp, ki, kd, mass):
    """Routh test for m s^3 + Kd s^2 + Kp s + Ki: all gains positive and Kd Kp > m Ki."""
    if ki == 0:
        return kp > 0 and kd > 0
    return kp > 0 and kd > 0 and ki > 0 and kd * kp > mass * ki


# %% [markdown]
# ## Step 3: simulate it step by step
# Every dt = 0.01 s: measure z and v, ask the PID for u, limit the thrust, then update with
# the semi-implicit Euler method: a = T / m - g, v = v + a dt, z = z + v dt.

# %%
def simulate_altitude(kp, ki, kd, mass=1.4, z_ref=2.0, t_end=10.0, dt=0.01,
                      m_nominal=M_NOMINAL, t_max=T_MAX, z0=0.0, i_limit=np.inf):
    """Fly the 1-D altitude loop. Returns a dict of arrays t, z, v, thrust."""
    if dt <= 0 or t_end <= 0:
        raise ValueError("dt and t_end must be positive")
    pid = PID(kp, ki, kd, i_limit)
    n = int(round(t_end / dt))
    t = np.arange(n + 1) * dt
    z, v, thrust = np.zeros(n + 1), np.zeros(n + 1), np.zeros(n + 1)
    z[0] = z0
    for k in range(n):
        u = pid.update(z_ref - z[k], v[k], dt)
        thrust[k] = float(np.clip(m_nominal * G + u, 0.0, t_max))
        a = thrust[k] / mass - G
        v[k + 1] = v[k] + a * dt
        z[k + 1] = z[k] + v[k + 1] * dt
    thrust[-1] = thrust[-2]
    return {"t": t, "z": z, "v": v, "thrust": thrust}


def step_metrics(t, z, z_start, tol=0.02):
    """Final value, fractional overshoot and 2 percent settling time of a step response."""
    final = float(np.mean(z[-max(2, len(z) // 20):]))
    span = final - z_start
    if abs(span) < 1e-12:
        return {"final": final, "overshoot": 0.0, "settling": 0.0}
    over = max(0.0, (np.max(z) - final) / span) if span > 0 else max(0.0, (final - np.min(z)) / -span)
    outside = np.where(np.abs(z - final) > tol * abs(span))[0]
    settle = 0.0 if len(outside) == 0 else float(t[min(outside[-1] + 1, len(t) - 1)])
    return {"final": final, "overshoot": float(over), "settling": settle}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    m = 1.4
    kp, kd, ki = 4.0, 3.0, 1.5
    print(f"wn = {natural_frequency(kp, m):.3f} rad/s, zeta = {damping_ratio(kp, kd, m):.3f}, "
          f"overshoot formula = {overshoot_formula(damping_ratio(kp, kd, m)):.3f}")
    print(f"steady-state error of PD = {steady_state_error(kp, m):.3f} m, PID stable: {pid_is_stable(kp, ki, kd, m)}")

    # Figure 1: P, PD and PID flying the heavier drone to 2 m
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    for (gains, lab, col) in [((kp, 0, 0), "P (Kp = 4)", "#d9534f"), ((kp, 0, kd), "PD (Kp = 4, Kd = 3)", "#1f6feb"),
                              ((kp, ki, kd), "PID (Kp = 4, Ki = 1.5, Kd = 3)", "#2a9d8f")]:
        r = simulate_altitude(*gains, mass=m, t_end=15.0)
        met = step_metrics(r["t"], r["z"], 0.0)
        ax.plot(r["t"], r["z"], color=col, lw=2, label=lab)
        if gains[2] == 0:
            print(f"{lab}: no damping, keeps oscillating between {r['z'].min():.2f} m and {r['z'].max():.2f} m")
        else:
            print(f"{lab}: final {met['final']:.3f} m, overshoot {met['overshoot']:.3f}, settling {met['settling']:.2f} s")
    ax.axhline(2.0, color="k", ls="--", lw=1)
    ax.text(14.8, 2.04, "target 2 m", ha="right", fontsize=8)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("height z (m)")
    ax.set_title("1.4 kg drone, controller assumes 1.2 kg")
    ax.set_ylim(0, 3.2)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "p_pd_pid.png", dpi=120)

    # Figure 2: effect of Kd on the PD response, compared with the formula
    fig2, axes = plt.subplots(1, 2, figsize=(10, 4))
    kds = [0.8, 1.5, 3.0, 6.0]
    for kdi, col in zip(kds, ["#d9534f", "#e9a23b", "#1f6feb", "#6f42c1"]):
        r = simulate_altitude(kp, 0.0, kdi, mass=m, t_end=12.0)
        axes[0].plot(r["t"], r["z"], color=col, lw=2, label=f"Kd = {kdi} (zeta = {damping_ratio(kp, kdi, m):.2f})")
    axes[0].set_xlabel("time (s)")
    axes[0].set_ylabel("height z (m)")
    axes[0].set_title("More Kd = more damping")
    axes[0].grid(alpha=0.3)
    axes[0].legend(fontsize=8)
    zetas = np.linspace(0.05, 1.0, 60)
    axes[1].plot(zetas, [100 * overshoot_formula(zz) for zz in zetas], "k-", label="formula")
    for kdi in np.linspace(0.4, 7.0, 12):
        r = simulate_altitude(kp, 0.0, kdi, mass=m, t_end=40.0)
        axes[1].plot(damping_ratio(kp, kdi, m), 100 * step_metrics(r["t"], r["z"], 0.0)["overshoot"], "o", color="#2a9d8f",
                     label="simulation" if kdi == 0.4 else None)
    axes[1].set_xlabel("damping ratio zeta (no unit)")
    axes[1].set_ylabel("overshoot (%)")
    axes[1].set_title("Simulation agrees with the formula")
    axes[1].grid(alpha=0.3)
    axes[1].legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "damping_overshoot.png", dpi=120)

# %% [markdown]
# ## Where this stops
# A real drone cannot push its thrust straight down whenever it likes: it has to tilt to move
# sideways, the rotors take time to speed up, and if it tilts the thrust no longer points up.
# Session 3 adds the roll angle, a second (inner) PID loop and the motor lag.
