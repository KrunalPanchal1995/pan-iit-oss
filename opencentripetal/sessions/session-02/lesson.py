"""Session 2 (Level 2): friction and banking supply the inward force.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: friction and banking supply the inward force
# **A. Real-world problem.** On a flat road the only thing that can push a car sideways is friction
# between tyres and road. That has a limit, and the limit drops when the road is wet. Engineers
# therefore *bank* (tilt) fast curves so that the road itself helps to push the car inward.
# How fast can a car go round a flat curve? What bank angle suits 80 km/h on a curve of radius
# 100 m? And what is the safe speed range on a wet road?
#
# **Plan.** (1) flat curve limit, (2) the ideal bank angle, (3) the safe speed range of a banked
# curve with friction, derived and then checked in three independent ways, (4) the design problem.
#
# *Educational model of a car as a point mass. Not a road design tool.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81  # gravitational acceleration, m/s^2


# %% [markdown]
# ## Step 1: the flat curve
# Friction must supply F = m v**2 / r. The most friction can give is mu * N = mu * m * g
# (N = m g on a flat road). So m v**2 / r <= mu m g, and the mass cancels:
#
#     v_max = sqrt(mu * g * r)

# %%
def flat_max_speed(mu, r):
    """Highest speed (m/s) on a flat curve of radius r (m) with friction coefficient mu."""
    return float(np.sqrt(mu * G * r))


# %% [markdown]
# ## Step 2: the ideal banked curve
# Tilt the road inward by angle theta. The normal force N (perpendicular to the road) now has an
# inward horizontal part N sin(theta). With no friction at all:
#
#     vertical:    N cos(theta) = m g
#     horizontal:  N sin(theta) = m v**2 / r       ->     tan(theta) = v**2 / (g r)

# %%
def ideal_bank_angle(v, r):
    """Bank angle (radians) for which no friction is needed at speed v (m/s), radius r (m)."""
    return float(np.arctan(v * v / (G * r)))


def ideal_speed(theta, r):
    """Speed (m/s) at which a frictionless banked curve of angle theta (radians) works."""
    return float(np.sqrt(G * r * np.tan(theta)))


# %% [markdown]
# ## Step 3: banked curve with friction - the safe speed range
# Let friction f act along the road surface. At the *top* speed the car is about to slide up and
# outward, so friction points down the slope, f = mu N. At the *lowest* speed it is about to slide
# down and inward, so friction points up the slope. With s = +1 (top speed) or s = -1 (lowest):
#
#     vertical:    N cos(theta) - s mu N sin(theta) = m g
#     horizontal:  N sin(theta) + s mu N cos(theta) = m v**2 / r
#
# Divide the second by the first: v**2 = g r (tan(theta) + s mu) / (1 - s mu tan(theta)).

# %%
def bank_speed_limits(theta, mu, r):
    """(v_min, v_max) in m/s for a banked curve. v_min is 0 when friction alone can hold a car at rest
    (mu >= tan theta); v_max is infinity when mu * tan(theta) >= 1 (no speed can make it slide out)."""
    t = np.tan(theta)
    vmax2 = G * r * (t + mu) / (1 - mu * t) if mu * t < 1 else np.inf
    vmin2 = G * r * (t - mu) / (1 + mu * t)
    return float(np.sqrt(max(vmin2, 0.0))), float(np.sqrt(vmax2))


# Check 1: solve the two force equations with numpy instead of using the formula.
def limit_speed_by_solving(theta, mu, r, s):
    """s = +1 for the top speed, -1 for the lowest. Unknowns: N and A = m v**2 / r (take m = 1)."""
    c, sn = np.cos(theta), np.sin(theta)
    # rows:  N (c - s mu sn) + 0 A = g        N (sn + s mu c) - A = 0
    M = np.array([[c - s * mu * sn, 0.0], [sn + s * mu * c, -1.0]])
    N, A = np.linalg.solve(M, np.array([G, 0.0]))
    return float(np.sqrt(max(A * r, 0.0))), float(N)      # A < 0 means no lowest speed (friction holds the car at rest)


# Check 2: scan the speed and test the grip condition |f| <= mu N directly.
def grips(v, theta, mu, r):
    """True if friction needed (along the slope) is within mu N at speed v (per unit mass)."""
    N = G * np.cos(theta) + v * v / r * np.sin(theta)          # normal force / m
    f = v * v / r * np.cos(theta) - G * np.sin(theta)           # friction along slope (down +) / m
    return abs(f) <= mu * N + 1e-12


def limits_by_scan(theta, mu, r, vtop=120.0, n=120001):
    vs = np.linspace(0.0, vtop, n)
    ok = np.array([grips(v, theta, mu, r) for v in vs[::40]])    # coarse scan, 40 steps apart
    vv = vs[::40][ok]
    return float(vv.min()), float(vv.max())


# %% [markdown]
# ## Step 4: the design problem
# Choose the bank angle for a curve of radius 100 m for a design speed of 80 km/h, then see how
# a wet road changes the maximum speed.

# %%
def kmh(v_ms):
    return v_ms * 3.6


def ms(v_kmh):
    return v_kmh / 3.6


def design_angle_deg(v_kmh, r):
    return float(np.degrees(ideal_bank_angle(ms(v_kmh), r)))


# %% [markdown]
# Inverse question: the *smallest* bank that still lets a car at speed v stay on the road on a
# surface with friction mu. Put v = v_max in the formula and solve for tan(theta):
#
#     tan(theta) = (k - mu) / (1 + mu k)        with k = v**2 / (g r)

# %%
def min_bank_for_speed(v, mu, r):
    """Smallest bank angle (radians) for which speed v (m/s) is still inside the safe range."""
    k = v * v / (G * r)
    if k <= mu:
        return 0.0          # friction alone is enough on the flat
    return float(np.arctan((k - mu) / (1 + mu * k)))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    r, vd = 100.0, 80.0
    mu_dry, mu_wet = 0.7, 0.4
    print(f"flat curve r = {r:.0f} m: v_max dry = {kmh(flat_max_speed(mu_dry, r)):.1f} km/h, "
          f"wet = {kmh(flat_max_speed(mu_wet, r)):.1f} km/h")
    th = ideal_bank_angle(ms(vd), r)
    print(f"ideal bank angle for {vd:.0f} km/h at r = {r:.0f} m: {np.degrees(th):.2f} degrees (tan = {np.tan(th):.4f})")
    for name, mu in (("dry", mu_dry), ("wet", mu_wet), ("ice", 0.1)):
        lo, hi = bank_speed_limits(th, mu, r)
        print(f"  banked {np.degrees(th):.1f} deg, {name} mu = {mu}: safe {kmh(lo):.1f} to {kmh(hi):.1f} km/h")
    print("verification of the formula at theta = 30 deg, mu = 0.3, r = 100 m:")
    th30 = np.radians(30)
    f_lo, f_hi = bank_speed_limits(th30, 0.3, r)
    s_hi, s_lo = limit_speed_by_solving(th30, 0.3, r, +1)[0], limit_speed_by_solving(th30, 0.3, r, -1)[0]
    c_lo, c_hi = limits_by_scan(th30, 0.3, r)
    print(f"  formula  v_min = {f_lo:.3f}  v_max = {f_hi:.3f} m/s")
    print(f"  solving  v_min = {s_lo:.3f}  v_max = {s_hi:.3f} m/s")
    print(f"  scan     v_min = {c_lo:.3f}  v_max = {c_hi:.3f} m/s (step 0.04 m/s)")
    # design with a margin: pick a bank angle so that 80 km/h is safe even at mu = 0.3 (wet)
    print(f"smallest bank for 80 km/h at mu = 0.3: {np.degrees(min_bank_for_speed(ms(vd), 0.3, r)):.2f} degrees")
    for deg in (6, 10, 12, 15):
        lo, hi = bank_speed_limits(np.radians(deg), 0.3, r)
        print(f"  mu = 0.3, bank {deg:2d} deg: safe {kmh(lo):.1f} to {kmh(hi):.1f} km/h -> 80 km/h {'safe' if kmh(lo) <= 80 <= kmh(hi) else 'NOT safe'}")

    # Figure 1: safe speed window versus bank angle
    angles = np.linspace(0, 40, 161)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for mu, col in ((mu_dry, "tab:green"), (mu_wet, "tab:blue")):
        lims = np.array([bank_speed_limits(np.radians(a), mu, r) for a in angles])
        ax.plot(angles, kmh(lims[:, 1]), color=col, label=f"top speed, mu = {mu}")
        ax.plot(angles, kmh(lims[:, 0]), color=col, ls="--", label=f"lowest speed, mu = {mu}")
    ax.plot(angles, [kmh(ideal_speed(np.radians(a), r)) if a > 0 else 0 for a in angles], "k:", label="ideal speed (no friction)")
    ax.axhline(vd, color="tab:red", lw=1)
    ax.text(1, vd + 3, "design speed 80 km/h", color="tab:red", fontsize=8)
    ax.set_xlabel("bank angle theta (degrees)")
    ax.set_ylabel("speed (km/h)")
    ax.set_title(f"Safe speed window of a banked curve, r = {r:.0f} m")
    ax.set_ylim(0, 260)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "safe_speed_window.png", dpi=120)

    # Figure 2: flat curve limit versus friction for three radii
    mus = np.linspace(0.05, 1.0, 100)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for rr in (50, 100, 200):
        ax2.plot(mus, kmh(np.sqrt(mus * G * rr)), label=f"r = {rr} m")
    ax2.set_xlabel("friction coefficient mu")
    ax2.set_ylabel("top speed on a flat curve (km/h)")
    ax2.set_title("Flat curve: v_max = sqrt(mu g r)")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "flat_limit.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Where this stops
# A real car is not a point: it can tip over, its weight shifts between wheels, and tyres do not
# have one friction number. Session 3 lets a simulated car drive the curve and checks it against
# these formulas.
