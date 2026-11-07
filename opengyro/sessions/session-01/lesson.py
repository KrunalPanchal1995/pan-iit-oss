"""Session 1 (Level 1): a spinning wheel resists falling and slowly circles (precession).

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: why a spinning wheel does not fall
# **A. Real-world problem.** Hold a bicycle wheel by one end of its axle. Not spinning, it
# flops down. Spinning fast, the axle stays up and slowly swings round in a circle. This
# slow circling is called *precession*. A top does the same thing.
#
# **The idea.** A spinning wheel carries *angular momentum* `L`, an arrow along its axle. A
# push that tries to turn the wheel is a *torque* `tau`, another arrow. The rule is
#
#     change of L in a short time dt  =  torque * dt
#
# Gravity pulls down at the wheel's centre, which is `r` away from the support. That gives a
# *sideways* torque. A sideways change of `L` turns the arrow sideways, so the axle circles
# instead of falling.
#
# **Plan.** (1) compute `L`, (2) compute the gravity torque, (3) move `L` in small steps and
# watch the axle circle, (4) see that a faster spin gives a slower circle.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

G = 9.81          # m/s^2
M = 0.5           # kg, mass of the wheel (a solid disc)
RAD = 0.05        # m, radius
LEN = 0.04        # m, distance from the support to the wheel centre
I3 = M * RAD ** 2 / 2          # moment of inertia about the axle, kg m^2


# %% [markdown]
# ## Step 1: angular momentum and gravity torque
# For a wheel spinning at `w` radians per second, the size of the angular momentum is
# `L = I w`, where `I` is the moment of inertia (how hard the wheel is to spin up). Its
# direction is along the axle (right-hand rule).
#
# The gravity torque is `tau = (distance r) * (weight m g)` for a horizontal axle. Its
# direction is horizontal and at right angles to the axle.

# %%
def angular_momentum(w):
    """Size of L in kg m^2/s for spin w in rad/s."""
    return I3 * w


def gravity_torque():
    """Size of the torque of the weight about the support (horizontal axle), N m."""
    return M * G * LEN


# %% [markdown]
# ## Step 2: move the L arrow in small steps
# Start with the axle pointing along x. In each small time step the arrow `L` changes by
# `tau * dt`, where `tau` is the weight torque (horizontal, perpendicular to the axle).
# We keep a 3D arrow `[x, y, z]`; gravity pulls along `-z`.

# %%
def torque_vector(L):
    """tau = r x F for the centre of the wheel at LEN along L and the weight pointing down."""
    n = L / np.linalg.norm(L)
    weight = np.array([0.0, 0.0, -M * G])
    return np.cross(LEN * n, weight)


def step_L(L, dt):
    """One RK4 step of dL/dt = tau(L)."""
    k1 = torque_vector(L)
    k2 = torque_vector(L + 0.5 * dt * k1)
    k3 = torque_vector(L + 0.5 * dt * k2)
    k4 = torque_vector(L + dt * k3)
    return L + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def precess(w, t_end=3.0, dt=0.002):
    """Follow the axle for t_end seconds. Returns times and the L arrows (rows)."""
    L = np.array([angular_momentum(w), 0.0, 0.0])
    n = int(round(t_end / dt))
    t = np.arange(n + 1) * dt
    out = np.empty((n + 1, 3))
    out[0] = L
    for k in range(n):
        L = step_L(L, dt)
        out[k + 1] = L
    return t, out


def circling_rate(t, Ls):
    """Rate (rad/s) at which the axle turns round the vertical, from the heading angle."""
    heading = np.unwrap(np.arctan2(Ls[:, 1], Ls[:, 0]))
    return float((heading[-1] - heading[0]) / (t[-1] - t[0]))


def predicted_rate(w):
    """The rule 'torque / L' gives the circling rate: Omega = tau / (I w)."""
    return gravity_torque() / angular_momentum(w)


# %% [markdown]
# ## Step 3: and without the spin?
# With no spin there is no `L` to steer: gravity simply makes the wheel tilt faster and
# faster. Here is the time for the same wheel, not spinning, to fall from 10 degrees away from straight up to the horizontal.

# %%
def fall_time_no_spin(start_deg=10.0, dt=1e-4):
    """Seconds for a non-spinning wheel to drop from `start_deg` away from vertical to horizontal."""
    i1 = M * RAD ** 2 / 4 + M * LEN ** 2
    th, om, t = np.radians(start_deg), 0.0, 0.0
    while th < np.pi / 2:
        om += (gravity_torque() / i1) * np.sin(th) * dt
        th += om * dt
        t += dt
    return t


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    for w in (50, 100, 200):
        t, Ls = precess(w)
        print(f"spin {w:3d} rad/s: L = {angular_momentum(w):.4f} kg m^2/s, circling {circling_rate(t, Ls):.3f} rad/s "
              f"(torque / L = {predicted_rate(w):.3f} rad/s), one circle in {2 * np.pi / circling_rate(t, Ls):.2f} s")
    print(f"weight torque = {gravity_torque():.4f} N m")
    print(f"no spin: falls in {fall_time_no_spin():.2f} s")

    # figure 1: view from above, L and tau arrows
    w = 100
    t, Ls = precess(w, 3.0)
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.3))
    ax[0].plot(np.cos(np.linspace(0, 6.3, 100)), np.sin(np.linspace(0, 6.3, 100)), ":", color="gray")
    ax[0].annotate("", xy=(1, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.5, color="tab:blue"))
    ax[0].annotate("", xy=(0, 0.6), xytext=(1, 0), arrowprops=dict(arrowstyle="->", lw=2.5, color="tab:red"))
    ax[0].text(0.45, -0.12, "L (along the axle)", color="tab:blue")
    ax[0].text(1.03, 0.3, "torque", color="tab:red")
    ax[0].text(-0.1, 0.05, "support")
    ax[0].set_aspect("equal")
    ax[0].set_xlim(-1.3, 1.7)
    ax[0].set_ylim(-1.3, 1.3)
    ax[0].set_xlabel("x, horizontal (relative length)")
    ax[0].set_ylabel("y, horizontal (relative length)")
    ax[0].set_title("From above: torque pushes the tip of L sideways")
    for w2, c in ((50, "tab:red"), (100, "tab:blue"), (200, "tab:green")):
        t2, L2 = precess(w2)
        ax[1].plot(t2, np.degrees(np.unwrap(np.arctan2(L2[:, 1], L2[:, 0]))), color=c, label=f"spin {w2} rad/s")
    ax[1].set_xlabel("time (s)")
    ax[1].set_ylabel("heading of the axle (degrees)")
    ax[1].set_title("Faster spin, slower circling")
    ax[1].legend()
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "torque_and_L.png", dpi=120)

# %% [markdown]
# ## Where this stops
# We assumed the axle stays horizontal and that the wheel spins very fast compared with its
# circling. Session 2 turns the same idea into a formula, and Session 3 simulates a real top
# that also tilts and wobbles.
