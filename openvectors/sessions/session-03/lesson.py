"""Session 3 (Level 3): simulate a boat in a river with a changing current, wind and feedback.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a river that changes, and a boat that corrects itself
# **A. Real-world problem.** Real rivers flow fastest in the middle and slowly near the banks,
# and wind pushes the boat as well. A fixed heading that is perfect for a uniform current
# misses the landing. A ferry pilot looks at where the boat is drifting and steers back
# towards the landing line: that is *feedback*. Today you simulate it in small time steps and
# check the simulation against the exact results of Session 2.
#
# This is a simplified educational model (flat 2D water, no waves, no boat inertia): it is not
# a navigation tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
WIDTH = 60.0                       # river width (m)
MAX_HEADING = np.radians(60.0)     # the rudder limit: the boat never points more than 60 degrees off


# %% [markdown]
# ## Step 1: the model
# State: x (downstream, m) and y (across, m), starting at (0, 0). The landing target is the
# point (0, W) straight opposite. The boat has speed v through the water and heading theta
# (radians, positive = leaning upstream). Then
#
#     dx/dt = u(y) + wind - v sin(theta)      dy/dt = v cos(theta)
#
# * `u(y)` is the current. *Uniform*: u = umax. *Parabolic*: u(y) = 4 umax (y/W)(1 - y/W),
#   zero at both banks and umax in the middle; its average across the river is (2/3) umax.
# * `wind` is a steady sideways push in m/s, positive downstream.

# %%
def current_profile(y, umax, profile="parabolic"):
    if profile == "uniform":
        return umax
    s = y / WIDTH
    return 4.0 * umax * s * (1.0 - s)


# %% [markdown]
# ## Step 2: the heading controller
# *Naive*: keep one fixed heading (`heading0_deg`) all the way. *Feedback*: every step look at
# the cross-track error x (how far downstream of the target line we are) and steer upstream:
#
#     theta = heading0 + K x + Ki * (sum of x dt),   limited to +-60 degrees
#
# K is in degrees per metre of error; the second (integral) term has Ki = K / 20 and removes
# the leftover error that a steady wind or current would otherwise cause. With K = 0 the
# boat is naive.

# %%
def simulate(v, umax, wind=0.0, K=0.0, heading0_deg=0.0, profile="parabolic", dt=0.05, method="rk4"):
    """Time-step the boat until it reaches y = WIDTH.
    Returns a dict with t, x, y, heading_deg (arrays) and landing_x (m), time (s)."""
    ki = K / 20.0
    h0 = np.radians(heading0_deg)

    def rate(x, y, th):
        return np.array([current_profile(y, umax, profile) + wind - v * np.sin(th), v * np.cos(th)])

    x = y = t = integ = 0.0
    T, X, Y, H = [0.0], [0.0], [0.0], []
    for _ in range(int(2000 / dt)):
        th = float(np.clip(h0 + np.radians(K) * x + np.radians(ki) * integ, -MAX_HEADING, MAX_HEADING))
        if method == "euler":
            nxt = np.array([x, y]) + dt * rate(x, y, th)
        else:
            s = np.array([x, y])
            k1 = rate(*s, th)
            k2 = rate(*(s + dt / 2 * k1), th)
            k3 = rate(*(s + dt / 2 * k2), th)
            k4 = rate(*(s + dt * k3), th)
            nxt = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        H.append(np.degrees(th))
        if nxt[1] >= WIDTH:                      # crossed the far bank inside this step
            f = (WIDTH - y) / (nxt[1] - y)
            x, t, y = x + f * (nxt[0] - x), t + f * dt, WIDTH
            T.append(t); X.append(x); Y.append(y)
            break
        x, y = nxt
        t += dt
        integ += x * dt
        T.append(t); X.append(x); Y.append(y)
    else:
        raise RuntimeError("the boat did not reach the far bank")
    H.append(H[-1])
    return {"t": np.array(T), "x": np.array(X), "y": np.array(Y), "heading_deg": np.array(H),
            "landing_x": float(X[-1]), "time": float(T[-1])}


# %% [markdown]
# ## Step 3: the exact answers to compare with
# For a *fixed* heading the boat moves along a straight line in the uniform case, and in the
# parabolic case the across motion is still uniform (dy/dt = v cos theta), so the time is
# W / (v cos theta) and the drift is the average current times the time:
#
#     drift = (u_avg + wind - v sin theta) W / (v cos theta),   u_avg = umax or (2/3) umax.

# %%
def analytic_fixed(v, umax, wind=0.0, heading0_deg=0.0, profile="parabolic"):
    """(landing_x, time) for a fixed heading, from the formulas above."""
    th = np.radians(heading0_deg)
    u_avg = umax if profile == "uniform" else 2.0 * umax / 3.0
    t = WIDTH / (v * np.cos(th))
    return float((u_avg + wind - v * np.sin(th)) * t), float(t)


def best_possible_drift(v, u):
    """Smallest |drift| (m) with a fixed heading in a uniform current u (exact, Session 2)."""
    return 0.0 if u < v else float(WIDTH * np.sqrt(u * u - v * v) / v)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    v, umax, wind = 4.0, 3.0, 0.5
    naive = simulate(v, umax, wind, K=0.0)
    open_loop = simulate(v, umax, wind, K=0.0, heading0_deg=float(np.degrees(np.arcsin(2.0 / 4.0))))
    fb = simulate(v, umax, wind, K=4.0)
    for name, r in [("naive straight", naive), ("fixed 30 deg", open_loop), ("feedback K=4", fb)]:
        print(f"{name:15s} lands {r['landing_x']:7.2f} m downstream after {r['time']:5.2f} s")
    ex, et = analytic_fixed(4.0, 3.0, 0.5, 0.0)
    print(f"analytic straight heading: {ex:.2f} m after {et:.2f} s (simulation {naive['landing_x']:.2f} m)")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for name, r, col in [("naive: straight across", naive, "tab:red"), ("fixed 30 degrees upstream", open_loop, "tab:orange"),
                         ("feedback, K = 4 deg/m", fb, "tab:green")]:
        ax.plot(r["x"], r["y"], color=col, lw=2.5, label=f"{name}: lands {r['landing_x']:.1f} m")
    ax.axvline(0, color="k", ls=":", label="target line")
    ax.axhline(0, color="k")
    ax.axhline(WIDTH, color="k")
    ax.set_xlabel("distance downstream (m)")
    ax.set_ylabel("distance across the river (m)")
    ax.set_title("Boat 4 m/s, parabolic current (peak 3 m/s), wind 0.5 m/s")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "paths_compared.png", dpi=120)

    # validation: simulation against the exact formulas over many headings
    heads = np.arange(-40, 61, 5)
    err = [abs(simulate(v, umax, wind, heading0_deg=h)["landing_x"] - analytic_fixed(v, umax, wind, h)[0]) for h in heads]
    print(f"largest |simulation - exact| over {len(heads)} headings: {max(err):.2e} m")
    # sensitivity to the current
    peaks = np.linspace(0, 6, 25)
    naive_drift = [simulate(v, p, 0.0)["landing_x"] for p in peaks]
    fb_err = [simulate(v, p, 0.0, K=4.0)["landing_x"] for p in peaks]
    fig2, ax2 = plt.subplots(figsize=(6.5, 4.2))
    ax2.plot(peaks, naive_drift, lw=2, color="tab:red", label="naive straight heading")
    ax2.plot(peaks, fb_err, lw=2, color="tab:green", label="feedback, K = 4 deg/m")
    ax2.set_xlabel("peak current (m/s)")
    ax2.set_ylabel("landing point, downstream (m)")
    ax2.set_title("Sensitivity to the current (boat 4 m/s, no wind)")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "sensitivity.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint. Mini-project: plan a ferry route.
