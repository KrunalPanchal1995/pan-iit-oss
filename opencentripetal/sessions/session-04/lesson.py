"""Session 4 (Level 3): a transition spiral (clothoid) between a straight road and a circular curve.

Run:  python start.py 4
"""
# %% [markdown]
# # Session 4: the transition spiral
# **A. Real-world problem.** In Session 3 the car met the curve with a step: on the straight the
# sideways acceleration is 0, one metre later on a curve of radius 100 m at 20 m/s it must be
# v^2 / R = 4 m/s^2. Real roads and railways never do that. They insert a **transition spiral**
# (a *clothoid*) whose curvature grows in proportion to the distance, so the sideways
# acceleration, and the force on the passengers, builds up smoothly. How long must the spiral be?
# How much does it shift the curve? And how much better does a car with slightly slow tyres and
# steering follow the road? Today you build the path, measure the rate of change of the sideways
# acceleration (the **lateral jerk**), and test it with a car that follows the path.
#
# *Simplified educational model: not a road design tool. Real design uses the national standard.*

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81            # m/s^2
TAU = 0.25          # s: how quickly sideways force builds up (tyres and steering); a made-up value
KP, KD = 1.0, 1.4   # the driver's steering feedback gains (1/s^2 and 1/s), as in Session 3


# %% [markdown]
# ## Step 1: the clothoid
# Curvature kappa is 1 / (radius of the bend). On a straight it is 0; on the circle it is 1 / R.
# On the spiral of length L we let it grow linearly: kappa(s) = s / (R L), so it reaches 1 / R
# exactly at the end. The direction of the road (the heading) is the integral of kappa:
# theta(s) = s^2 / (2 R L). The position follows from x = integral of cos(theta) ds and
# y = integral of sin(theta) ds (the *Fresnel integrals*), which we sum as a fast series in
# u = s^2 / (2 R L).

# %%
def _check(R, L):
    if R <= 0:
        raise ValueError("the radius R must be positive")
    if L <= 0:
        raise ValueError("the spiral length L must be positive")
    if L > 2.0 * R:
        raise ValueError("the spiral must not turn the road by more than 1 radian: L <= 2 R")


def clothoid_curvature(s, R, L):
    """Curvature (1/m) at distance s along a spiral of length L that ends at radius R."""
    _check(R, L)
    return np.clip(np.asarray(s, dtype=float), 0.0, L) / (R * L)


def clothoid_heading(s, R, L):
    """Heading angle (rad) at distance s along the spiral: s^2 / (2 R L)."""
    _check(R, L)
    s = np.asarray(s, dtype=float)
    return s * s / (2.0 * R * L)


def clothoid_xy(s, R, L):
    """Position (x, y) in metres at distance s along the spiral, starting at the origin heading along +x."""
    _check(R, L)
    s = np.asarray(s, dtype=float)
    u = s * s / (2.0 * R * L)
    x = np.zeros_like(u)
    y = np.zeros_like(u)
    for k in range(14):
        x = x + (-1) ** k * u ** (2 * k) / ((4 * k + 1) * math.factorial(2 * k))
        y = y + (-1) ** k * u ** (2 * k + 1) / ((4 * k + 3) * math.factorial(2 * k + 1))
    return s * x, s * y


# %% [markdown]
# ## Step 2: a path made of a straight, a spiral and an arc
# The path starts on a straight of length `straight`, then the spiral (length L, or none if L = 0:
# the step of Session 3), then a circular arc of radius R. We store points every `ds` metres with
# the distance s, the position, the heading and the curvature. The spiral pulls the circle
# inwards by the **shift** p: the circle's distance from the original straight line. For
# a short spiral p is about L^2 / (24 R).

# %%
def build_path(R, L, straight=60.0, arc=80.0, ds=0.05):
    """Left-turning path. Returns a dict with arrays s, x, y, theta, kappa and the numbers
    s_spiral (start of the spiral), s_arc (start of the circle), shift (m)."""
    if R <= 0:
        raise ValueError("the radius R must be positive")
    if L < 0:
        raise ValueError("the spiral length L must not be negative")
    if straight < 0 or arc <= 0 or ds <= 0:
        raise ValueError("lengths must be positive")
    n0 = int(round(straight / ds))
    s0 = n0 * ds
    s_list = [np.arange(n0) * ds]
    x_list, y_list = [np.arange(n0) * ds], [np.zeros(n0)]
    th_list, k_list = [np.zeros(n0)], [np.zeros(n0)]
    if L > 0:
        n1 = int(round(L / ds))
        q = np.arange(n1) * ds
        sx, sy = clothoid_xy(q, R, L)
        s_list.append(s0 + q)
        x_list.append(s0 + sx)
        y_list.append(sy)
        th_list.append(clothoid_heading(q, R, L))
        k_list.append(clothoid_curvature(q, R, L))
        ex, ey = clothoid_xy(L, R, L)
        theta_e, x_e, y_e = L / (2.0 * R), s0 + float(ex), float(ey)
        s_arc = s0 + n1 * ds
    else:
        theta_e, x_e, y_e, s_arc = 0.0, s0, 0.0, s0
    cx, cy = x_e - R * math.sin(theta_e), y_e + R * math.cos(theta_e)      # centre of the circle
    m = int(round(arc / ds)) + 1
    phi = theta_e + np.arange(m) * ds / R
    s_list.append(s_arc + np.arange(m) * ds)
    x_list.append(cx + R * np.sin(phi))
    y_list.append(cy - R * np.cos(phi))
    th_list.append(phi)
    k_list.append(np.full(m, 1.0 / R))
    return {"s": np.concatenate(s_list), "x": np.concatenate(x_list), "y": np.concatenate(y_list),
            "theta": np.concatenate(th_list), "kappa": np.concatenate(k_list),
            "s_spiral": s0, "s_arc": s_arc, "shift": cy - R, "centre": (cx, cy), "R": R, "L": L}


def spiral_shift_formula(R, L):
    """Approximate shift of the circle caused by the spiral: L^2 / (24 R)."""
    if R <= 0 or L < 0:
        raise ValueError("R must be positive and L not negative")
    return L * L / (24.0 * R)


# %% [markdown]
# ## Step 3: lateral acceleration and jerk
# At speed v the sideways acceleration is a = v^2 kappa. On the spiral kappa grows with s = v t, so
# a grows in proportion to time. Its rate of change, the lateral jerk, is constant:
#
#     j = d(a)/dt = v^3 / (R L)
#
# Solving for L gives the shortest spiral for a jerk limit: L = v^3 / (R j_max). The spiral takes
# L / v seconds to drive. With L = 0 (a step) the jerk is infinite in this model.

# %%
def lateral_acceleration(v, kappa):
    """Sideways acceleration (m/s^2) of a car at speed v on a path of curvature kappa."""
    return v * v * np.asarray(kappa, dtype=float)


def lateral_jerk(v, R, L):
    """Rate of change of the sideways acceleration on the spiral, v^3 / (R L), in m/s^3."""
    _check(R, L)
    if v < 0:
        raise ValueError("the speed must not be negative")
    return v ** 3 / (R * L)


def min_spiral_length(v, R, jerk_max):
    """Shortest spiral (m) that keeps the lateral jerk at or below jerk_max (m/s^3)."""
    if v < 0 or R <= 0 or jerk_max <= 0:
        raise ValueError("v must not be negative, R and the jerk limit must be positive")
    return v ** 3 / (R * jerk_max)


def spiral_time(v, L):
    """Seconds needed to drive a spiral of length L at speed v."""
    if v <= 0 or L < 0:
        raise ValueError("v must be positive and L not negative")
    return L / v


def round_up(x, step=5.0):
    """Round x up to a multiple of step (spirals are specified in whole 5 m)."""
    return step * math.ceil(x / step - 1e-9)


# %% [markdown]
# ## Step 4: a car that follows the path (the Session 3 car with slow tyres)
# The car of Session 3 is a point mass at constant speed v. Its sideways acceleration a is
# demanded by the driver: a_cmd = v^2 kappa(path here) - KP d - KD d' , where d is the distance
# to the left of the path and d' its rate. The new ingredient: the tyres and steering need a
# moment to build the force, so a follows a_cmd with a lag, da/dt = (a_cmd - a) / TAU, and the
# force can never exceed the friction limit mu g. State: x, y, heading psi, and a.
# We step it in time with the 4th-order Runge-Kutta method as in Session 3.

# %%
def follow_path(path, v, tau=TAU, mu=0.8, kp=KP, kd=KD, dt=0.01, T=None):
    """Drive the path at constant speed v from its start. Returns a dict of arrays:
    t, x, y, a (actual sideways acceleration), a_cmd, d (distance left of the path), ratio (|a_cmd| / (mu g))."""
    if v <= 0 or tau <= 0 or mu <= 0 or dt <= 0:
        raise ValueError("v, tau, mu and dt must be positive")
    xs, ys, th, ka = path["x"], path["y"], path["theta"], path["kappa"]
    total = path["s"][-1]
    T = (total - 15.0) / v if T is None else T
    cap = mu * G

    def deriv(st):
        x, y, psi, a = st
        i = int(np.argmin((xs - x) ** 2 + (ys - y) ** 2))
        d = -(x - xs[i]) * math.sin(th[i]) + (y - ys[i]) * math.cos(th[i])
        ddot = v * math.sin(psi - th[i])
        a_cmd = v * v * ka[i] - kp * d - kd * ddot
        a_lim = max(-cap, min(cap, a_cmd))
        return np.array([v * math.cos(psi), v * math.sin(psi), a / v, (a_lim - a) / tau]), d, a_cmd

    st = np.array([0.0, 0.0, 0.0, 0.0])
    n = int(round(T / dt))
    keys = ("t", "x", "y", "a", "a_cmd", "d", "ratio")
    rec = {k: [] for k in keys}
    for i in range(n + 1):
        k1, d, a_cmd = deriv(st)
        for k, val in zip(keys, (i * dt, st[0], st[1], st[3], a_cmd, d, abs(a_cmd) / cap)):
            rec[k].append(val)
        if i == n:
            break
        k2 = deriv(st + 0.5 * dt * k1)[0]
        k3 = deriv(st + 0.5 * dt * k2)[0]
        k4 = deriv(st + dt * k3)[0]
        st = st + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return {k: np.array(val) for k, val in rec.items()}


def entry_metrics(R, L, v, tau=TAU, mu=0.8, dt=0.01):
    """Follow a path with spiral length L (0 = step) and report the largest distance from the
    path, the peak sideways acceleration and the peak lateral jerk (finite differences)."""
    path = build_path(R, L)
    out = follow_path(path, v, tau, mu, dt=dt)
    jerk = np.abs(np.diff(out["a"]) / dt)
    return {"max_dev": float(np.abs(out["d"]).max()), "peak_a": float(out["a"].max()),
            "peak_jerk": float(jerk.max()), "steady_a": v * v / R, "peak_ratio": float(out["a"].max() / (mu * G))}


# %% [markdown]
# ## Step 5: a spiral for a road curve (used by the mini-project)
# Pick a curve radius, the design speeds and a jerk limit. For each speed the shortest spiral is
# v^3 / (R j_max), rounded up to a multiple of 5 m; report its shift and the time it takes.

# %%
def design_spiral(v_kmh, R, jerk_max, step=5.0):
    """Shortest spiral for a design speed (km/h): returns L (m, rounded up), exact minimum, jerk achieved, shift, time."""
    v = v_kmh / 3.6
    exact = min_spiral_length(v, R, jerk_max)
    L = round_up(exact, step)
    return {"v": v, "L_min": exact, "L": L, "jerk": lateral_jerk(v, R, L), "shift": spiral_shift_formula(R, L),
            "time": spiral_time(v, L), "a_steady": v * v / R}


# %% [markdown]
# ## See it
# Figure 1: the three-part path and the curvature along it, with a step and with a spiral. Figure 2: the
# sideways acceleration and the car's distance from the path while it enters the curve, for a
# step and for spirals of 20, 40 and 80 m. Figure 3: peak jerk and largest distance from the path
# against the spiral length.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    BLUE, ORANGE, MAGENTA = "#0072b2", "#c86a00", "#d81b60"
    R, v = 100.0, 20.0
    print(f"R = {R:.0f} m, v = {v:.0f} m/s: steady sideways acceleration {v * v / R:.1f} m/s^2")
    for L in (0, 10, 20, 40, 80):
        m = entry_metrics(R, L, v)
        sh = build_path(R, L)["shift"]
        jerk_ideal = lateral_jerk(v, R, L) if L else math.inf
        print(f"L = {L:3d} m: ideal jerk {jerk_ideal:6.2f} m/s^3, shift {sh:.3f} m (formula {spiral_shift_formula(R, L):.3f}), "
              f"car: max distance from path {m['max_dev']:.2f} m, peak a {m['peak_a']:.2f}, peak jerk {m['peak_jerk']:.2f}")
    for kmh in (50, 70, 90):
        d = design_spiral(kmh, 150.0, 2.0)
        print(f"design {kmh} km/h on R = 150 m, jerk limit 2.0: L_min {d['L_min']:.1f} -> {d['L']:.0f} m, jerk {d['jerk']:.2f}, shift {d['shift']:.2f} m, {d['time']:.1f} s")

    # figure 1
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 4.0))
    for L, col, ls in ((0, MAGENTA, "--"), (40, BLUE, "-")):
        p = build_path(R, L, straight=40.0, arc=70.0)
        axs[0].plot(p["x"], p["y"], color=col, ls=ls, lw=2, label="step (no spiral)" if L == 0 else f"spiral L = {L} m")
        axs[1].plot(p["s"], p["kappa"] * 1000, color=col, ls=ls, lw=2)
    axs[0].set_aspect("equal")
    axs[0].set_xlabel("x (m)")
    axs[0].set_ylabel("y (m)")
    axs[0].set_title("The path: straight, spiral, circle of radius 100 m", fontsize=10)
    axs[0].legend(fontsize=8)
    axs[1].set_xlabel("distance along the road (m)")
    axs[1].set_ylabel("curvature (1/km)")
    axs[1].set_title("Curvature: a jump, or a ramp", fontsize=10)
    for ax in axs:
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "path_curvature.png", dpi=120)

    # figure 2
    fig2, axs2 = plt.subplots(1, 2, figsize=(10.5, 4.0))
    cols = {0: MAGENTA, 20: ORANGE, 40: BLUE, 80: "#444444"}
    for L, col in cols.items():
        out = follow_path(build_path(R, L), v)
        lab = "step" if L == 0 else f"spiral {L} m"
        axs2[0].plot(out["t"], out["a"], color=col, lw=2, label=lab)
        axs2[1].plot(out["t"], out["d"], color=col, lw=2, label=lab)
    axs2[0].axhline(4.0, color="#666666", ls=":", lw=1)
    axs2[0].set_xlabel("time (s)")
    axs2[0].set_ylabel("sideways acceleration (m/s^2)")
    axs2[0].set_title("Entering the curve at 20 m/s", fontsize=10)
    axs2[1].set_xlabel("time (s)")
    axs2[1].set_ylabel("distance left of the path (m)")
    axs2[1].set_title("How far the car strays from the road", fontsize=10)
    for ax in axs2:
        ax.set_xlim(0, 8)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "entry_response.png", dpi=120)

    # figure 3
    Ls = [10, 20, 30, 40, 60, 80, 120]
    ms = [entry_metrics(R, L, v) for L in Ls]
    fig3, axs3 = plt.subplots(1, 2, figsize=(10.5, 4.0))
    axs3[0].plot(Ls, [lateral_jerk(v, R, L) for L in Ls], "o-", color=BLUE, label="ideal v^3 / (R L)")
    axs3[0].plot(Ls, [m["peak_jerk"] for m in ms], "s-", color=ORANGE, label="car with slow tyres (peak)")
    axs3[0].set_xlabel("spiral length L (m)")
    axs3[0].set_ylabel("lateral jerk (m/s^3)")
    axs3[0].set_title("Longer spiral, gentler build-up", fontsize=10)
    axs3[0].legend(fontsize=8)
    axs3[1].plot(Ls, [m["max_dev"] for m in ms], "o-", color=MAGENTA)
    axs3[1].axhline(entry_metrics(R, 0, v)["max_dev"], color="#666666", ls=":", lw=1)
    axs3[1].text(60, entry_metrics(R, 0, v)["max_dev"] - 0.15, "no spiral", fontsize=9)
    axs3[1].set_xlabel("spiral length L (m)")
    axs3[1].set_ylabel("largest distance from the path (m)")
    axs3[1].set_title("The car stays closer to the road", fontsize=10)
    for ax in axs3:
        ax.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "jerk_and_deviation.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint. The mini-project (README) designs a spiral for a road curve.
