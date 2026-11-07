"""Session 2 (Level 2): derivative as a limit of slopes, integral as a sum of rectangles, the fundamental theorem.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the derivative and the integral as limits
# **A. Real-world problem.** A car's position is x(t) = 3 t^2 + 2 t metres. What are its
# velocity and acceleration, and how far does a car travel while it brakes to a stop?
#
# **Plan.** (1) slope between two moments (a secant), (2) shrink the gap to get the derivative,
# (3) rules and a numerical check, (4) add thin rectangles to get the integral, (5) see that
# the two undo each other, (6) design a braking distance.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: secant slope, then tangent slope
# The slope of the straight line through (t, x(t)) and (t + h, x(t + h)) is
# (x(t + h) - x(t)) / h. Make h smaller and smaller: the numbers settle on one value, the
# *derivative* x'(t), the slope of the tangent line.

# %%
def x_car(t):
    """Position (m) of the example car: 3 t^2 + 2 t, with t in seconds."""
    return 3.0 * np.asarray(t, dtype=float) ** 2 + 2.0 * np.asarray(t, dtype=float)


def secant_slope(f, t, h):
    return (f(t + h) - f(t)) / h


# %% [markdown]
# ## Step 2: rules, and a check by finite differences
# For a polynomial c * t^n the rule is c * n * t^(n-1). Also (sin t)' = cos t and (e^t)' = e^t.
# We store a polynomial as its coefficients [c0, c1, c2, ...] meaning c0 + c1 t + c2 t^2 + ...

# %%
def poly_value(coef, t):
    return sum(c * np.asarray(t, dtype=float) ** k for k, c in enumerate(coef))


def poly_derivative(coef):
    """Coefficients of the derivative: the term c t^k becomes k c t^(k-1)."""
    return [k * c for k, c in enumerate(coef)][1:] or [0.0]


def central_slope(f, t, h=1e-5):
    """Check tool: slope from one step each side."""
    return (f(t + h) - f(t - h)) / (2 * h)


# %% [markdown]
# ## Step 3: the integral as a sum of thin rectangles
# Cut [a, b] into n slices of width dt = (b - a) / n. Each slice is a rectangle of height
# f(somewhere in the slice). Heights are m/s, widths are s, so every area is metres.

# %%
def riemann_sum(f, a, b, n, rule="left"):
    dt = (b - a) / n
    k = np.arange(n)
    shift = {"left": 0.0, "mid": 0.5, "right": 1.0}[rule]
    return float(np.sum(f(a + (k + shift) * dt)) * dt)


def poly_antiderivative(coef, constant=0.0):
    """Coefficients of an antiderivative: c t^k becomes c t^(k+1) / (k+1)."""
    return [constant] + [c / (k + 1) for k, c in enumerate(coef)]


# %% [markdown]
# ## Step 4: the fundamental theorem
# If v(t) = x'(t) then the integral of v from a to b is x(b) - x(a). Adding up thin rectangles
# of speed gives the change in position: derivative and integral undo each other.

# %%
def v_car(t):
    """Velocity (m/s) of the example car: 6 t + 2."""
    return 6.0 * np.asarray(t, dtype=float) + 2.0


A_CAR = 6.0   # acceleration (m/s^2): the derivative of 6 t + 2


# %% [markdown]
# ## Step 5: design problem, braking to a stop
# Brake with a steady slowdown a (m/s^2): the speed drops in a straight line from v0 to 0 in
# T = v0 / a seconds. Distance = area of the triangle = v0 T / 2 = v0^2 / (2 a). A driver also
# travels at v0 during a reaction time tr before braking starts.

# %%
def stopping_distance(v0, a, t_react=0.0):
    """Distance (m) to stop from speed v0 (m/s) with steady slowdown a (m/s^2)."""
    return v0 * t_react + v0 ** 2 / (2.0 * a)


def max_speed_for(distance_m, a, t_react=0.0):
    """Largest speed (m/s) that still stops within distance_m: solves v tr + v^2/(2a) = d."""
    return float(-a * t_react + np.sqrt((a * t_react) ** 2 + 2.0 * a * distance_m))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t0 = 2.0
    print(f"x({t0}) = {float(x_car(t0)):.1f} m, v({t0}) = {float(v_car(t0)):.1f} m/s, a = {A_CAR} m/s^2")
    for h in (1.0, 0.1, 0.01, 0.001):
        print(f"  secant slope at t = 2 with h = {h:<6}: {float(secant_slope(x_car, t0, h)):.4f} m/s")
    print("poly derivative of [0, 2, 3]:", poly_derivative([0.0, 2.0, 3.0]))
    print(f"check d/dt sin at 1: rule {np.cos(1.0):.6f}, finite difference {central_slope(np.sin, 1.0):.6f}")
    print(f"check d/dt exp at 1: rule {np.exp(1.0):.6f}, finite difference {central_slope(np.exp, 1.0):.6f}")
    for n in (4, 16, 64):
        print(f"  left sum of v on [0, 2] with n = {n:<3}: {riemann_sum(v_car, 0, 2, n):.4f} m (exact {float(x_car(2) - x_car(0)):.1f})")
    print(f"mid sum n = 4: {riemann_sum(v_car, 0, 2, 4, 'mid'):.4f} m")
    print(f"stopping from 20 m/s at 5 m/s^2: {stopping_distance(20, 5):.1f} m")
    print(f"stopping from 25 m/s with 0.75 s reaction at 6 m/s^2: {stopping_distance(25, 6, 0.75):.1f} m")
    print(f"max speed to stop within 40 m (a = 6, reaction 0.75 s): {max_speed_for(40, 6, 0.75):.2f} m/s")

    t = np.linspace(0, 3, 301)
    fig, axs = plt.subplots(3, 1, figsize=(6, 7), sharex=True)
    axs[0].plot(t, x_car(t), color="#d62728")
    axs[0].plot([t0], [x_car(t0)], "ko")
    s = float(v_car(t0))
    axs[0].plot([1, 3], [float(x_car(t0)) + s * (1 - t0), float(x_car(t0)) + s * (3 - t0)], "k--", label="tangent, slope 14 m/s")
    axs[0].set_ylabel("position x (m)")
    axs[0].legend()
    axs[1].plot(t, v_car(t), color="#1f77b4")
    axs[1].set_ylabel("velocity v (m/s)")
    axs[2].plot(t, np.full_like(t, A_CAR), color="#2ca02c")
    axs[2].set_ylabel("acceleration a (m/s^2)")
    axs[2].set_xlabel("time t (s)")
    axs[2].set_ylim(0, 10)
    axs[0].set_title("x(t) = 3 t^2 + 2 t, its derivative and second derivative")
    for ax in axs:
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "x_v_a.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    tt = np.linspace(0, 2, 201)
    ax2.plot(tt, v_car(tt), color="#1f77b4", label="v(t) = 6 t + 2")
    n = 4
    dt = 2.0 / n
    ax2.bar(np.arange(n) * dt, v_car(np.arange(n) * dt), width=dt, align="edge", alpha=0.35, edgecolor="k",
            label=f"4 left rectangles: {riemann_sum(v_car, 0, 2, n):.0f} m")
    ax2.set_xlabel("time t (s)")
    ax2.set_ylabel("velocity v (m/s)")
    ax2.set_title("Thin rectangles add up to distance (exact 16 m)")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "riemann_rectangles.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
