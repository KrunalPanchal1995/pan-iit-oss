"""Session 1 (Level 1): a lift going up and down, and why you feel heavier.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a lift goes up and down
# **A. Real-world problem.** You step into a lift and the floor seems to push harder on your feet for a
# moment as it starts to rise, and less hard when it starts to go down. Your mass did not change and
# gravity did not change. What did?
#
# **Plan.** (1) draw the speed-time graph of a ride, (2) find the acceleration from its slope and the
# distance from its area, (3) work out the force of the floor on your feet (the "apparent weight").

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

G = 9.81   # m/s^2, acceleration of gravity


# %% [markdown]
# ## Step 1: the speed-time graph of a ride
# A simple ride has three parts: **accelerate** (speed rises in a straight line), **cruise** (speed is
# constant), **decelerate** (speed falls to zero). The graph is a trapezoid.
# - The **slope** of the graph is the acceleration a (m/s^2).
# - The **area** under the graph is the distance travelled (m).
#
# With cruise speed v and acceleration a, speeding up takes v / a seconds and covers v^2 / (2a) metres.
# Speeding up and slowing down together use v^2 / a metres, so for a total distance d (if the lift
# reaches the cruise speed) the cruise distance is d - v^2 / a and the cruise time is that divided by v.

# %%
def ride_times(d, v, a):
    """Times (accelerate, cruise, decelerate) in seconds for distance d (m), top speed v (m/s), acceleration a (m/s^2).

    If the distance is too short to reach v, the lift speeds up and then at once slows down (cruise time 0)
    and the top speed is smaller than v.
    """
    if d >= v ** 2 / a:
        t_acc = v / a
        return t_acc, (d - v ** 2 / a) / v, t_acc
    # half the distance speeding up: d / 2 = a t^2 / 2, so t = sqrt(d / a)
    t_acc = np.sqrt(d / a)
    return t_acc, 0.0, t_acc


def speed_at(t, d, v, a):
    """Speed (m/s) at time t (s) during a ride going up."""
    t_acc, t_cruise, t_dec = ride_times(d, v, a)
    top = a * t_acc
    total = t_acc + t_cruise + t_dec
    if t < 0 or t > total:
        return 0.0
    if t < t_acc:
        return a * t
    if t < t_acc + t_cruise:
        return top
    return top - a * (t - t_acc - t_cruise)


def travel_time(d, v, a):
    """Total ride time (s): accelerate + cruise + decelerate."""
    return sum(ride_times(d, v, a))


# %% [markdown]
# ## Step 2: why you feel heavier
# You feel the force of the floor on you. When the lift is not accelerating that force equals your
# weight m g. When the lift accelerates upward with a, the floor must push you up with more force so
# that you accelerate too (Newton's second law: net force = m a):
#
#     N - m g = m a        so        N = m (g + a)
#
# Going up and speeding up: a > 0, you feel heavier. Going up and slowing down: the acceleration points
# down (a < 0), you feel lighter. A lift in free fall (a = -g) would give N = 0.

# %%
def apparent_weight(m, a):
    """Force of the floor on a person of mass m (kg) when the lift has acceleration a (m/s^2, up positive), in newtons."""
    return m * (G + a)


def feel_ratio(a):
    """Apparent weight divided by true weight: 1 + a / g (no unit)."""
    return 1.0 + a / G


# %% [markdown]
# ## Step 3: see it
# Left: speed against time (a trapezoid). Right: the floor force on a 60 kg person during the same ride.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    d, v, a, m = 21.0, 2.0, 1.0, 60.0
    T = travel_time(d, v, a)
    t = np.linspace(0, T, 400)
    speed = np.array([speed_at(x, d, v, a) for x in t])
    t_acc, t_cr, t_dec = ride_times(d, v, a)
    # acceleration during each part: +a while speeding up, 0 while cruising, -a while slowing down
    acc = np.where(t < t_acc, a, np.where(t < t_acc + t_cr, 0.0, -a))
    print(f"ride of {d} m at {v} m/s: accelerate {t_acc:.1f} s, cruise {t_cr:.1f} s, decelerate {t_dec:.1f} s, total {T:.1f} s")
    print(f"weight at rest {m * G:.0f} N, while speeding up {apparent_weight(m, a):.0f} N, "
          f"while slowing down {apparent_weight(m, -a):.0f} N")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(t, speed, color="tab:blue")
    ax.fill_between(t, speed, alpha=0.15)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("speed (m/s)")
    ax.set_title("Speed-time graph: area = distance (21 m)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "speed_time.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(t, [apparent_weight(m, x) for x in acc], color="tab:red")
    ax2.axhline(m * G, color="gray", ls=":", label=f"true weight {m * G:.0f} N")
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("floor force on a 60 kg person (N)")
    ax2.set_title("Heavier when speeding up, lighter when slowing down")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "apparent_weight.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
