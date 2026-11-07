"""Session 2 (Level 2): the projectile equations, the range formula and a design problem.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the equations of projectile motion
# **A. Real-world problem.** A batter wants the ball to clear a boundary 70 m away, or a
# fielder wants to hit the stumps from 30 m. Guessing is slow; the equations tell us exactly
# which speed and angle will do it, and how many different ways there are to do it.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81   # m/s^2


# %% [markdown]
# ## Step 1: position and velocity as functions of time
# Launch from height h0 at speed v and angle a (degrees above horizontal):
#
#     x = v cos(a) t          y = h0 + v sin(a) t - g t^2 / 2
#     vx = v cos(a)           vy = v sin(a) - g t
#
# Remove t between the two position formulas and you get the path in terms of x:
#
#     y = h0 + x tan(a) - g x^2 / (2 v^2 cos^2(a))      (a parabola)

# %%
def trajectory(t, v, angle_deg, h0=0.0):
    """Return (x, y, vx, vy) at time t for a launch from height h0."""
    a = np.radians(angle_deg)
    t = np.asarray(t, dtype=float)
    return (v * np.cos(a) * t, h0 + v * np.sin(a) * t - 0.5 * G * t ** 2,
            v * np.cos(a) + 0 * t, v * np.sin(a) - G * t)


def height_at(x, v, angle_deg, h0=0.0):
    """Height (m) of the ball when it is x metres away horizontally."""
    a = np.radians(angle_deg)
    x = np.asarray(x, dtype=float)
    return h0 + x * np.tan(a) - G * x ** 2 / (2 * v ** 2 * np.cos(a) ** 2)


# %% [markdown]
# ## Step 2: time of flight, peak height and range
# Landing means y = 0, a quadratic in t. Its positive root is
#
#     T = (v sin(a) + sqrt(v^2 sin^2(a) + 2 g h0)) / g
#
# The peak is where vy = 0, at t = v sin(a) / g, so  H = h0 + v^2 sin^2(a) / (2 g).
# The range is R = v cos(a) T. On level ground (h0 = 0) this simplifies to
#
#     R = v^2 sin(2a) / g
#
# using sin(2a) = 2 sin(a) cos(a). sin(2a) is largest (equal to 1) when 2a = 90 degrees,
# so the best angle on level ground is 45 degrees.

# %%
def time_of_flight(v, angle_deg, h0=0.0):
    a = np.radians(angle_deg)
    vy = v * np.sin(a)
    return float((vy + np.sqrt(vy ** 2 + 2 * G * h0)) / G)


def peak_height(v, angle_deg, h0=0.0):
    a = np.radians(angle_deg)
    return float(h0 + (v * np.sin(a)) ** 2 / (2 * G))


def range_from(v, angle_deg, h0=0.0):
    a = np.radians(angle_deg)
    return float(v * np.cos(a) * time_of_flight(v, angle_deg, h0))


def best_angle_with_height(v, h0=0.0):
    """Angle (degrees) for the longest range when launching from height h0:
    tan(a) = v / sqrt(v^2 + 2 g h0). It is 45 degrees at h0 = 0 and gets smaller as h0 grows."""
    return float(np.degrees(np.arctan(v / np.sqrt(v ** 2 + 2 * G * h0))))


# %% [markdown]
# ## Step 3: two angles for one range
# On level ground sin(2a) = g R / v^2. If that number is between 0 and 1 there are two angles,
# a and 90 - a (a low flat shot and a high lofted one). At exactly 1 they merge into 45
# degrees; above 1 the target is out of reach.

# %%
def angles_for_range(v, target_range):
    """Launch angles (degrees, level ground) that land at target_range (m). 0, 1 or 2 values."""
    s = G * target_range / v ** 2
    if s > 1 + 1e-12:
        return []
    if s >= 1 - 1e-12:
        return [45.0]
    a1 = 0.5 * np.degrees(np.arcsin(s))
    return [float(a1), float(90.0 - a1)]


# %% [markdown]
# ## Step 4: the design problem, lowest speed to hit a target
# The target is d metres away and h metres above the launch point (use h < 0 for below).
# Put x = d, y = h in the path equation and treat u = tan(a) as the unknown:
#
#     (g d^2 / (2 v^2)) u^2 - d u + (h + g d^2 / (2 v^2)) = 0
#
# It has real solutions only if the discriminant is not negative. The edge case gives the
# lowest possible speed:
#
#     v_min^2 = g (h + sqrt(d^2 + h^2)),     tan(a) = (h + sqrt(d^2 + h^2)) / d

# %%
def angles_to_hit(d, h, v):
    """Angles (degrees) that pass through (d, h) at launch speed v (from the origin)."""
    c = G * d ** 2 / (2 * v ** 2)
    disc = d ** 2 - 4 * c * (h + c)
    if disc < -1e-9:
        return []
    signs = (0,) if disc <= 1e-12 else (-1, 1)     # one double root at the lowest speed
    roots = [float(np.degrees(np.arctan((d + s * np.sqrt(max(disc, 0.0))) / (2 * c)))) for s in signs]
    return sorted(r for r in roots if r > 0.0)


def min_speed_to_hit(d, h):
    """Lowest launch speed (m/s) and its angle (degrees) to pass through (d, h)."""
    root = np.sqrt(d ** 2 + h ** 2)
    return float(np.sqrt(G * (h + root))), float(np.degrees(np.arctan((h + root) / d)))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    v = 30.0
    print(f"level ground, v = {v} m/s: R(45) = {range_from(v, 45):.2f} m, v^2/g = {v ** 2 / G:.2f} m")
    for h0 in (0.0, 1.0, 2.0):
        ba = best_angle_with_height(v, h0)
        print(f"h0 = {h0} m: best angle {ba:.2f} degrees, range {range_from(v, ba, h0):.2f} m")
    print("angles for R = 80 m at 30 m/s:", [round(a, 1) for a in angles_for_range(30.0, 80.0)])
    vm, am = min_speed_to_hit(50.0, 10.0)
    print(f"target (50 m, 10 m): lowest speed {vm:.2f} m/s at {am:.2f} degrees")
    print("at 26 m/s the angles are", [round(a, 2) for a in angles_to_hit(50.0, 10.0, 26.0)])

    # figure 1: range versus angle for several launch heights
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    angs = np.linspace(1, 89, 177)
    for h0 in (0.0, 1.0, 2.0):
        ax.plot(angs, [range_from(v, a, h0) for a in angs], label=f"launch height {h0:.0f} m")
        ba = best_angle_with_height(v, h0)
        ax.plot([ba], [range_from(v, ba, h0)], "ko", ms=4)
    ax.axhline(80, color="gray", ls=":")
    ax.text(2, 82, "R = 80 m: two angles", fontsize=8)
    ax.set_xlabel("launch angle (degrees)")
    ax.set_ylabel("range (m)")
    ax.set_title("Range versus angle at 30 m/s (dots: best angle)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "range_vs_angle.png", dpi=120)

    # figure 2: hitting a target at the lowest speed
    fig2, ax2 = plt.subplots(figsize=(7, 4.2))
    x = np.linspace(0, 55, 200)
    ax2.plot(x, height_at(x, vm, am), color="tab:red", label=f"lowest speed {vm:.1f} m/s at {am:.1f} deg")
    for ang in angles_to_hit(50.0, 10.0, 26.0):
        ax2.plot(x, height_at(x, 26.0, ang), "--", label=f"26 m/s at {ang:.1f} deg")
    ax2.plot([50], [10], "k*", ms=12)
    ax2.set_ylim(0, 60)
    ax2.set_xlabel("horizontal distance x (m)")
    ax2.set_ylabel("height y (m)")
    ax2.set_title("Reaching the target (50 m, 10 m)")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "hit_target.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Still no air, so every range here is too long for a real cricket ball. Session 3 measures by how much.
