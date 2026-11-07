"""Session 3 (Level 3): tilt to move. A planar quadrotor with a cascaded PID, motor lag and validation.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: attitude control, cascaded loops and motor lag
# **A. Real-world problem.** A drone has no sideways propeller. To move 1 m to the right it must
# tilt, so part of its thrust points sideways; then it must tilt back to stop. The tilt itself is
# controlled by spinning the right rotors slower than the left ones. And the rotors cannot change
# speed instantly. How do we build a controller that flies the drone 1 m sideways, keeps the
# height, and stays stable when the motors are slow?
#
# **Plan.** (1) the planar quadrotor equations, (2) the inner attitude loop (PD on roll angle)
# and its formulas, (3) the outer position loop that asks for a tilt, (4) tilt compensation of
# the thrust, (5) motor lag and the stability limit, (6) validation, (7) a tuning mini-project.
#
# **Model.** We look at the drone from behind: sideways position y, height z, roll angle phi.
# The left pair and the right pair of rotors each give one force. A simplified teaching model,
# not a flight-controller design tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

G = 9.81
MASS = 1.2          # kg
ARM = 0.2           # distance from the centre to each rotor pair (m)
INERTIA = 0.012     # roll moment of inertia (kg m^2)
F_SIDE_MAX = 20.0   # largest force of one rotor pair (N); two pairs give 40 N as in Session 1


# %% [markdown]
# ## Step 1: the planar quadrotor
# Let F_r and F_l be the forces of the right and left rotor pairs. Total thrust T = F_r + F_l
# points along the drone's "up" axis. Tilting by phi (positive = leaning right) gives
#
#     m y'' = T sin(phi)          m z'' = T cos(phi) - m g          I phi'' = tau = (F_l - F_r) L
#
# Spinning the left rotors harder (F_l > F_r) rolls the drone to the right. Given a wanted T and
# torque tau, the **mixer** solves for the two forces: F_l = T/2 + tau/(2L), F_r = T/2 - tau/(2L).

# %%
def mixer(thrust, torque, arm=ARM, f_max=F_SIDE_MAX):
    """Rotor-pair forces (F_left, F_right) in N for a total thrust (N) and roll torque (N m), clamped."""
    f_l = thrust / 2.0 + torque / (2.0 * arm)
    f_r = thrust / 2.0 - torque / (2.0 * arm)
    return float(np.clip(f_l, 0.0, f_max)), float(np.clip(f_r, 0.0, f_max))


def derivatives(state, f_l, f_r, mass=MASS, inertia=INERTIA, arm=ARM, g=G):
    """Time derivative of state [y, z, phi, vy, vz, p] for given rotor-pair forces."""
    y, z, phi, vy, vz, p = state
    thrust, torque = f_l + f_r, (f_l - f_r) * arm
    return np.array([vy, vz, p, thrust * np.sin(phi) / mass, thrust * np.cos(phi) / mass - g, torque / inertia])


# %% [markdown]
# ## Step 2: the inner loop, attitude
# The roll angle obeys I phi'' = tau, the same "push a mass" problem as the height in Session 2,
# only rotating. A PD law tau = Kp_att (phi_des - phi) - Kd_att p (p = roll rate, rad/s) gives
#
#     wn_att = sqrt(Kp_att / I)        zeta_att = Kd_att / (2 sqrt(Kp_att I))
#
# With Kp_att = 1.2 N m/rad and Kd_att = 0.17 N m s/rad: wn = 10 rad/s, zeta = 0.71.

# %%
def attitude_wn_zeta(kp_att, kd_att, inertia=INERTIA):
    """Natural frequency (rad/s) and damping ratio of the PD attitude loop with ideal motors."""
    return float(np.sqrt(kp_att / inertia)), float(kd_att / (2.0 * np.sqrt(kp_att * inertia)))


def overshoot_formula(zeta):
    """Fractional overshoot of a second-order step response."""
    return 0.0 if zeta >= 1.0 else float(np.exp(-zeta * np.pi / np.sqrt(1.0 - zeta ** 2)))


# %% [markdown]
# ## Step 3: the motors are not instant, and that sets a limit
# A rotor needs time to spin up. A simple model is a first-order lag with time constant tau_m:
# dF/dt = (F_cmd - F) / tau_m. With the lag the attitude loop becomes third order,
#
#     I tau_m s^3 + I s^2 + Kd_att s + Kp_att = 0
#
# and the Routh test says it is stable only if tau_m < Kd_att / Kp_att. For our gains this is
# 0.17 / 1.2 = 0.142 s. Slower motors, or a bigger Kp_att with the same Kd_att, shake the drone.

# %%
def lag_limit(kp_att, kd_att):
    """Largest motor time constant (s) for which the PD attitude loop stays stable."""
    if kp_att <= 0 or kd_att <= 0:
        raise ValueError("attitude gains must be positive")
    return kd_att / kp_att


# %% [markdown]
# ## Step 4: the outer loop, position, and tilt compensation
# To move sideways we want an acceleration a_y = Kp_y (y_ref - y) - Kd_y vy. Since y'' ~ g phi
# for small angles, the outer loop asks the inner loop for phi_des = a_y / g, limited to a safe
# tilt. The height loop is Session 2's PID, now written per unit mass, and we divide the thrust
# by cos(phi) so the vertical part stays m (g + a_z) while tilted (**tilt compensation**).
# With Kp_y = 2.25 1/s^2 and Kd_y = 2.1 1/s the outer loop has wn = 1.5 rad/s and zeta = 0.7.
# Rule of thumb: the inner loop should be about 5 to 10 times faster than the outer loop
# (here 10 rad/s against 1.5 rad/s), so the outer loop can treat the tilt as instant.

# %%
DEFAULT_GAINS = dict(kp_y=2.25, kd_y=2.1, kp_z=4.0, ki_z=1.0, kd_z=3.0, kp_att=1.2, kd_att=0.17)


def simulate(y_ref=1.0, z_ref=0.0, t_end=8.0, dt=0.001, tau_m=0.02, mass=MASS, gains=None, tilt_comp=True,
             max_tilt_deg=30.0, phi0=0.0, outer=True, phi_ref=0.0, f_max=F_SIDE_MAX, m_nominal=MASS):
    """Fly the planar quadrotor with the cascaded PID. Starts hovering at y = z = 0.

    Returns a dict of arrays: t, y, z, phi, f_l, f_r, phi_des."""
    if dt <= 0 or t_end <= 0 or tau_m < 0:
        raise ValueError("dt and t_end must be positive and tau_m not negative")
    k = dict(DEFAULT_GAINS, **(gains or {}))
    n = int(round(t_end / dt))
    s = np.array([0.0, 0.0, phi0, 0.0, 0.0, 0.0])
    f_l = f_r = m_nominal * G / 2.0            # rotors start at the hover force
    z_int = 0.0
    out = {key: np.zeros(n + 1) for key in ("t", "y", "z", "phi", "f_l", "f_r", "phi_des")}
    lim = np.radians(max_tilt_deg)
    for i in range(n + 1):
        y, z, phi, vy, vz, p = s
        # outer loop: position -> wanted tilt
        phi_des = float(np.clip((k["kp_y"] * (y_ref - y) - k["kd_y"] * vy) / G, -lim, lim)) if outer else phi_ref
        # height loop (Session 2, per unit mass) with tilt compensation
        z_int += (z_ref - z) * dt
        a_z = k["kp_z"] * (z_ref - z) + k["ki_z"] * z_int - k["kd_z"] * vz
        thrust = m_nominal * (G + a_z) / (np.cos(phi) if tilt_comp else 1.0)
        # inner loop: tilt -> torque
        torque = k["kp_att"] * (phi_des - phi) - k["kd_att"] * p
        fl_cmd, fr_cmd = mixer(thrust, torque, f_max=f_max)
        for key, val in zip(out, (i * dt, y, z, phi, f_l, f_r, phi_des)):
            out[key][i] = val
        if i == n:
            break
        # motor lag (exact discrete first-order update), then semi-implicit Euler for the body
        alpha = 1.0 if tau_m == 0 else 1.0 - np.exp(-dt / tau_m)
        f_l += alpha * (fl_cmd - f_l)
        f_r += alpha * (fr_cmd - f_r)
        d = derivatives(s, f_l, f_r, mass=mass)
        s[3:] += d[3:] * dt
        s[:3] += s[3:] * dt
    return out


def metrics(r, y_ref=1.0, tol=0.02):
    """Settling time (2 percent band), overshoot (m), largest height dip (m) and largest tilt (degrees)."""
    t, y = r["t"], r["y"]
    outside = np.where(np.abs(y - y_ref) > tol * abs(y_ref))[0]
    settle = 0.0 if len(outside) == 0 else float(t[min(outside[-1] + 1, len(t) - 1)])
    return {"settling": settle, "overshoot": float(max(0.0, np.max(y) - y_ref)),
            "dip": float(max(0.0, -np.min(r["z"]))), "max_tilt": float(np.degrees(np.max(np.abs(r["phi"])))),
            "final_y": float(y[-1]), "final_phi": float(r["phi"][-1])}


def attitude_step(phi_ref_deg=5.0, tau_m=0.0, kp_att=1.2, kd_att=0.17, t_end=2.0, dt=0.0005):
    """Inner loop alone: step the wanted roll angle with the position loop switched off."""
    r = simulate(t_end=t_end, dt=dt, tau_m=tau_m, outer=False, phi_ref=np.radians(phi_ref_deg),
                 gains=dict(kp_att=kp_att, kd_att=kd_att), f_max=1e6)
    return r["t"], np.degrees(r["phi"])


# %% [markdown]
# ## Step 5: choosing gains (used by the mini-project)
# A camera drone must move 1 m sideways and settle within 4 s, dip less than 1 cm and never
# tilt more than 15 degrees (so the camera gimbal can cope). Its motors have tau_m = 0.06 s, and the designer wants a safety
# factor of 2 on the lag limit: tau_m <= Kd_att / (2 Kp_att).

# %%
CANDIDATES = [("A soft", 0.192, 0.0672), ("B medium", 0.432, 0.1008), ("C default", 1.2, 0.17), ("D stiff", 4.8, 0.336)]


def check_design(kp_att, kd_att, tau_m=0.06, safety=2.0, settle_max=4.0, dip_max=0.01, tilt_max=15.0):
    """Fly the design and report whether every requirement is met."""
    r = simulate(tau_m=tau_m, t_end=10.0, gains=dict(kp_att=kp_att, kd_att=kd_att))
    m = metrics(r)
    margin_ok = tau_m * safety <= lag_limit(kp_att, kd_att)
    ok = margin_ok and m["settling"] <= settle_max and m["dip"] <= dip_max and m["max_tilt"] <= tilt_max
    return dict(m, margin_ok=margin_ok, ok=ok, wn=attitude_wn_zeta(kp_att, kd_att)[0])


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    wn, zeta = attitude_wn_zeta(1.2, 0.17)
    print(f"attitude loop: wn = {wn:.2f} rad/s, zeta = {zeta:.3f}, overshoot formula {overshoot_formula(zeta):.3f}")
    print(f"motor-lag limit Kd/Kp = {lag_limit(1.2, 0.17):.3f} s")

    # Figure 1: the sideways move, with drone outlines along the path
    r = simulate(t_end=8.0)
    m = metrics(r)
    print(f"1 m sideways move: settles in {m['settling']:.2f} s, overshoot {100 * m['overshoot']:.1f} cm, "
          f"height dip {100 * m['dip']:.2f} cm, largest tilt {m['max_tilt']:.1f} degrees")
    fig, axes = plt.subplots(2, 1, figsize=(9, 6.6), gridspec_kw=dict(height_ratios=[1, 1.4]))
    ax = axes[0]
    ax.plot(r["y"], r["z"], color="#1f6feb", lw=1.5, label="path of the centre")
    for tk in np.arange(0.0, 3.21, 0.4):
        i = int(round(tk / 0.001))
        y0, z0, ph = r["y"][i], r["z"][i], r["phi"][i]
        c = 0.07                               # half-width of the drawn drone (m)
        ax.plot([y0 - c * np.cos(ph), y0 + c * np.cos(ph)], [z0 + c * np.sin(ph), z0 - c * np.sin(ph)], color="k", lw=2.5)
        ax.annotate("", xy=(y0 + 0.12 * np.sin(ph), z0 + 0.12 * np.cos(ph)), xytext=(y0, z0),
                    arrowprops=dict(arrowstyle="->", color="#d9534f"))
    ax.set_aspect("equal")
    ax.set_xlim(-0.15, 1.25)
    ax.set_ylim(-0.08, 0.18)
    ax.set_xlabel("sideways position y (m)")
    ax.set_ylabel("height change z (m)")
    ax.set_title("Every 0.4 s: tilt to go, tilt back to stop")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="lower right")
    ax2 = axes[1]
    ax2.plot(r["t"], r["y"], color="#1f6feb", lw=2, label="y (m)")
    ax2.plot(r["t"], np.degrees(r["phi"]) / 10, color="#d9534f", lw=2, label="tilt phi (degrees / 10)")
    ax2.plot(r["t"], np.degrees(r["phi_des"]) / 10, color="#d9534f", lw=1, ls="--", label="wanted tilt (degrees / 10)")
    ax2.axhline(1.0, color="k", ls=":", lw=1)
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("value")
    ax2.set_title(f"Settles in {m['settling']:.1f} s, largest tilt {m['max_tilt']:.0f} degrees")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "sideways_move.png", dpi=120)

    # Figure 2: motor lag, attitude step responses and the stability limit
    fig2, axes2 = plt.subplots(1, 2, figsize=(10.5, 4.2))
    for tm, col in [(0.0, "k"), (0.03, "#2a9d8f"), (0.08, "#e9a23b"), (0.13, "#d9534f")]:
        t, ph = attitude_step(5.0, tm)
        axes2[0].plot(t, ph, color=col, lw=2, label=f"tau_m = {tm:.2f} s")
    axes2[0].axhline(5.0, color="k", ls=":", lw=1)
    axes2[0].set_xlabel("time (s)")
    axes2[0].set_ylabel("roll angle (degrees)")
    axes2[0].set_title(f"5 degree tilt step; limit tau_m = {lag_limit(1.2, 0.17):.3f} s")
    axes2[0].grid(alpha=0.3)
    axes2[0].legend(fontsize=8)
    kps = np.linspace(0.4, 4.0, 60)
    axes2[1].plot(kps, 0.17 / kps, "k-", lw=2, label="limit tau_m = Kd / Kp (Kd = 0.17)")
    axes2[1].fill_between(kps, 0.17 / kps, 0.5, color="#d9534f", alpha=0.2, label="unstable")
    axes2[1].plot([1.2], [0.06], "o", color="#1f6feb", label="camera drone motors, Kp = 1.2")
    axes2[1].set_ylim(0, 0.4)
    axes2[1].set_xlabel("attitude gain Kp_att (N m/rad)")
    axes2[1].set_ylabel("motor time constant tau_m (s)")
    axes2[1].set_title("Faster attitude gains need faster motors")
    axes2[1].grid(alpha=0.3)
    axes2[1].legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "motor_lag.png", dpi=120)

    # Figure 3: tilt compensation keeps the height
    fig3, ax3 = plt.subplots(figsize=(6.4, 4.0))
    for tc, col, lab in [(False, "#d9534f", "no tilt compensation"), (True, "#2a9d8f", "thrust / cos(phi)")]:
        rr = simulate(y_ref=3.0, t_end=8.0, tilt_comp=tc)
        ax3.plot(rr["t"], 100 * rr["z"], color=col, lw=2, label=f"{lab}: dip {100 * metrics(rr, 3.0)['dip']:.1f} cm")
    ax3.set_xlabel("time (s)")
    ax3.set_ylabel("height change z (cm)")
    ax3.set_title("3 m sideways move: height while tilting")
    ax3.grid(alpha=0.3)
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "tilt_compensation.png", dpi=120)

    # Mini-project: three candidate attitude tunings for the camera drone
    print("Mini-project (tau_m = 0.06 s, safety factor 2):")
    for name, kp, kd in CANDIDATES:
        d = check_design(kp, kd)
        print(f"  {name}: Kp = {kp}, Kd = {kd}, lag limit {lag_limit(kp, kd):.3f} s, settling {d['settling']:.2f} s, "
              f"dip {100 * d['dip']:.2f} cm, tilt {d['max_tilt']:.1f} deg, meets all: {d['ok']}")

# %% [markdown]
# ## Where this stops
# We flew in a flat world with one tilt angle, perfect sensors and still air. A real quadrotor
# has roll, pitch and yaw, four motors, noisy gyroscopes and gusts. The roadmap shows the path.
