"""Session 3 (Level 3): add air drag, solve by RK4, and validate against exact results.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a cricket ball with air drag
# **A. Real-world problem.** In Sessions 1 and 2 the ball flew in a perfect parabola and 45
# degrees gave the longest hit. A real cricket ball is slowed by the air, so the parabola is
# lopsided and the best angle is lower. There is no neat formula any more, so we solve the motion
# step by step on the computer (RK4), and we prove the solver right before trusting it:
# switch drag off and it must match Session 2 exactly; switch it on and the energy books must
# balance.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81            # m/s^2
RHO = 1.2           # air density, kg/m^3 (approximate, sea level)
MASS, DIAM, CD = 0.16, 0.07, 0.4   # cricket ball: approximate typical values (real balls vary)


# %% [markdown]
# ## Step 1: the drag force
# Quadratic drag points against the velocity *relative to the air* and grows with its square:
#
#     F = - k |v_rel| v_rel,      k = 0.5 * rho * Cd * A,      A = pi d^2 / 4
#
# So the acceleration is a = -(k/m) |v_rel| v_rel + (0, -g). With wind speed `wind` (m/s, along
# +x, positive = tailwind), v_rel = (vx - wind, vy). For the cricket ball k = 9.2e-4 kg/m and
# k/m = 0.0058 per metre.

# %%
def drag_k(cd=CD, diam=DIAM, rho=RHO):
    """Drag constant k = 0.5 rho Cd A in kg/m."""
    return 0.5 * rho * cd * np.pi * diam ** 2 / 4.0


def terminal_speed(mass=MASS, cd=CD, diam=DIAM, rho=RHO):
    """Speed at which drag balances weight: v_t = sqrt(2 m g / (rho Cd A)) in m/s."""
    area = np.pi * diam ** 2 / 4.0
    return float(np.sqrt(2 * mass * G / (rho * cd * area)))


def deriv(s, kom, wind=0.0):
    """Time derivative of the state s = [x, y, vx, vy, W].
    W is the work done against the ball by drag, per unit mass (J/kg); it is multiplied by the
    mass later. Wind (m/s, +x) only changes the velocity relative to the air."""
    x, y, vx, vy, w = s
    rx, ry = vx - wind, vy
    sp = np.hypot(rx, ry)
    ax, ay = -kom * sp * rx, -G - kom * sp * ry
    dw = kom * sp * (rx * vx + ry * vy)      # minus (drag force . velocity) per unit mass
    return np.array([vx, vy, ax, ay, dw])


# %% [markdown]
# ## Step 2: RK4 and (for the failure case) explicit Euler
# One step of size dt. Euler uses only the slope at the start. RK4 samples the slope four
# times (start, two middles, end) and blends them; its error shrinks like dt^4, Euler's only
# like dt.

# %%
def step_euler(s, dt, kom, wind):
    return s + dt * deriv(s, kom, wind)


def step_rk4(s, dt, kom, wind):
    k1 = deriv(s, kom, wind)
    k2 = deriv(s + 0.5 * dt * k1, kom, wind)
    k3 = deriv(s + 0.5 * dt * k2, kom, wind)
    k4 = deriv(s + dt * k3, kom, wind)
    return s + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


# %% [markdown]
# ## Step 3: fly the ball until it lands
# The state starts at (0, h0) with the launch velocity. We step until y would go below 0,
# then find the exact landing moment inside the last step by bisection (a shorter step of the
# same method), so the landing is not rounded to a multiple of dt.

# %%
def simulate(v0, angle_deg, h0=0.0, cd=CD, wind=0.0, dt=0.01, method="rk4", mass=MASS, t_max=60.0):
    """Fly the ball. Returns a dict with arrays t, x, y, vx, vy, work and the numbers
    range (m), flight (s), peak (m). cd = 0 switches drag off."""
    kom = drag_k(cd) / mass
    step = step_rk4 if method == "rk4" else step_euler
    a = np.radians(angle_deg)
    s = np.array([0.0, h0, v0 * np.cos(a), v0 * np.sin(a), 0.0])
    rows, t = [(0.0, *s)], 0.0
    while t < t_max:
        s_new = step(s, dt, kom, wind)
        if s_new[1] < 0.0:                       # crossed the ground inside this step
            lo, hi = 0.0, 1.0
            for _ in range(50):
                mid = 0.5 * (lo + hi)
                if step(s, mid * dt, kom, wind)[1] < 0.0:
                    hi = mid
                else:
                    lo = mid
            s = step(s, hi * dt, kom, wind)
            t += hi * dt
            rows.append((t, *s))
            break
        s = s_new
        t += dt
        rows.append((t, *s))
    r = np.array(rows)
    return {"t": r[:, 0], "x": r[:, 1], "y": r[:, 2], "vx": r[:, 3], "vy": r[:, 4], "work": r[:, 5] * mass,
            "range": float(r[-1, 1]), "flight": float(r[-1, 0]), "peak": float(r[:, 2].max()), "mass": mass}


# %% [markdown]
# ## Step 4: validation 1, drag off must equal Session 2
# With cd = 0 the exact answers are R = v cos(a) (v sin(a) + sqrt(v^2 sin^2(a) + 2 g h0)) / g and
# T = R / (v cos(a)). If the solver cannot reproduce these, it cannot be trusted with drag.

# %%
def exact_range(v0, angle_deg, h0=0.0):
    a = np.radians(angle_deg)
    return float(v0 * np.cos(a) * (v0 * np.sin(a) + np.sqrt((v0 * np.sin(a)) ** 2 + 2 * G * h0)) / G)


def exact_flight(v0, angle_deg, h0=0.0):
    a = np.radians(angle_deg)
    return float((v0 * np.sin(a) + np.sqrt((v0 * np.sin(a)) ** 2 + 2 * G * h0)) / G)


# %% [markdown]
# ## Step 5: validation 2, the energy books
# Mechanical energy E = m g y + m v^2 / 2 changes only because of drag. So
# E(t) + (work done against the ball by drag up to t) must stay equal to E(0). The solver
# integrates that work as an extra variable, so this is an independent check on the motion.

# %%
def energy_error(sim):
    """Largest |E + W - E0| / E0 along the flight (should be tiny for a good solver)."""
    m = sim["mass"]
    e = m * G * sim["y"] + 0.5 * m * (sim["vx"] ** 2 + sim["vy"] ** 2)
    return float(np.max(np.abs(e + sim["work"] - e[0])) / e[0])


# %% [markdown]
# ## Step 6: the best angle, found numerically
# Range as a function of angle has one peak. Scan 5 to 85 degrees in 5 degree steps, then
# squeeze the peak with a golden-section search around the best scan point.

# %%
def best_angle(v0, h0=0.0, cd=CD, wind=0.0, dt=0.01):
    """Launch angle (degrees) that gives the longest range, and that range (m)."""
    def rng(ang):
        return simulate(v0, ang, h0, cd, wind, dt)["range"]
    grid = np.arange(5.0, 90.0, 5.0)
    vals = [rng(a) for a in grid]
    k = int(np.argmax(vals))
    lo, hi = grid[max(k - 1, 0)], grid[min(k + 1, len(grid) - 1)]
    phi = (np.sqrt(5) - 1) / 2
    c, d = hi - phi * (hi - lo), lo + phi * (hi - lo)
    fc, fd = rng(c), rng(d)
    for _ in range(24):
        if fc > fd:
            hi, d, fd = d, c, fc
            c = hi - phi * (hi - lo)
            fc = rng(c)
        else:
            lo, c, fc = c, d, fd
            d = lo + phi * (hi - lo)
            fd = rng(d)
    a = 0.5 * (lo + hi)
    return float(a), float(rng(a))


def min_speed_for_range(target, h0=0.0, cd=CD, wind=0.0, dt=0.02):
    """Lowest launch speed (m/s) that can reach `target` metres with the best angle. Bisection:
    the best range grows with speed, so halve the bracket until it is 0.001 m/s wide."""
    lo, hi = 1.0, 100.0
    while hi - lo > 1e-3:
        mid = 0.5 * (lo + hi)
        if best_angle(mid, h0, cd, wind, dt)[1] >= target:
            hi = mid
        else:
            lo = mid
    return float(hi)


def angle_window(v0, target, h0=0.0, cd=CD, wind=0.0, dt=0.02):
    """Smallest and largest whole-degree launch angles whose range is at least `target` (or None)."""
    ok = [a for a in range(5, 90) if simulate(v0, float(a), h0, cd, wind, dt)["range"] >= target]
    return (ok[0], ok[-1]) if ok else None


def fall_speed(t_end, cd=CD, mass=MASS, dt=0.01):
    """Speed of a ball dropped from rest after t_end seconds of falling (RK4). It approaches v_t."""
    kom = drag_k(cd) / mass
    s = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
    for _ in range(int(round(t_end / dt))):
        s = step_rk4(s, dt, kom, 0.0)
    return float(abs(s[3]))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    v0, h0 = 35.0, 1.0
    print(f"k = {drag_k():.3e} kg/m, k/m = {drag_k() / MASS:.5f} 1/m, terminal speed = {terminal_speed():.1f} m/s")

    # validation 1: drag off versus exact formulas
    s0 = simulate(v0, 40.0, h0, cd=0.0)
    print(f"drag off: RK4 range {s0['range']:.4f} m, exact {exact_range(v0, 40.0, h0):.4f} m")
    # validation 2: energy
    s1 = simulate(v0, 40.0, h0)
    print(f"drag on : range {s1['range']:.2f} m, flight {s1['flight']:.2f} s, peak {s1['peak']:.2f} m,"
          f" energy error {energy_error(s1):.1e}")

    # figure 1: drag versus no drag for several angles
    fig, ax = plt.subplots(figsize=(8, 4.2))
    for ang, col in ((20, "tab:green"), (30, "tab:orange"), (45, "tab:blue"), (60, "tab:red")):
        a = simulate(v0, ang, h0)
        b = simulate(v0, ang, h0, cd=0.0)
        ax.plot(a["x"], a["y"], color=col, label=f"{ang} deg with drag (range {a['range']:.0f} m)")
        ax.plot(b["x"], b["y"], color=col, ls="--", lw=1)
    ax.set_xlabel("horizontal distance x (m)")
    ax.set_ylabel("height y (m)")
    ax.set_title("Solid: with drag. Dashed: no drag (same colour = same launch). v = 35 m/s, h0 = 1 m")
    ax.set_ylim(0, None)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "drag_vs_vacuum.png", dpi=120)

    # figure 2: range versus angle with and without drag, best angles marked
    angs = np.arange(5, 86, 2.5)
    r_drag = [simulate(v0, a, h0)["range"] for a in angs]
    r_free = [exact_range(v0, a, h0) for a in angs]
    ba, br = best_angle(v0, h0)
    bf, bfr = best_angle(v0, h0, cd=0.0)
    fig2, ax2 = plt.subplots(figsize=(6.5, 4.2))
    ax2.plot(angs, r_free, "--", color="gray", label=f"no drag (best {bf:.1f} deg, {bfr:.0f} m)")
    ax2.plot(angs, r_drag, color="tab:blue", label=f"with drag (best {ba:.1f} deg, {br:.0f} m)")
    ax2.plot([ba], [br], "o", color="tab:blue")
    ax2.plot([bf], [bfr], "o", color="gray")
    ax2.set_xlabel("launch angle (degrees)")
    ax2.set_ylabel("range (m)")
    ax2.set_title("Drag shortens the range and lowers the best angle")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "range_vs_angle.png", dpi=120)
    print(f"best angle with drag {ba:.2f} deg ({br:.1f} m); without drag {bf:.2f} deg ({bfr:.1f} m)")

    # best angle and range loss as the launch speed rises (level ground)
    for vv in (15.0, 25.0, 35.0, 45.0, 60.0):
        ba_v, br_v = best_angle(vv)
        print(f"v = {vv:4.0f} m/s: best angle {ba_v:.1f} deg, range {br_v:6.1f} m, no-drag {vv ** 2 / G:6.1f} m,"
              f" loss {100 * (1 - br_v / (vv ** 2 / G)):.1f} percent")

    # failure case: explicit Euler with big steps
    fig3, ax3 = plt.subplots(figsize=(6.5, 4.2))
    ref = simulate(v0, 40.0, h0)
    ax3.plot(ref["x"], ref["y"], "k", lw=2, label=f"RK4 dt 0.01 ({ref['range']:.1f} m)")
    for dt, col in ((0.05, "tab:green"), (0.2, "tab:orange"), (0.5, "tab:red")):
        e = simulate(v0, 40.0, h0, dt=dt, method="euler")
        ax3.plot(e["x"], e["y"], color=col, label=f"Euler dt {dt} ({e['range']:.1f} m)")
        print(f"Euler dt {dt}: range {e['range']:.1f} m, energy error {energy_error(e):.2f}")
    r4 = simulate(v0, 40.0, h0, dt=0.5)
    ax3.plot(r4["x"], r4["y"], "k:", label=f"RK4 dt 0.5 ({r4['range']:.1f} m)")
    ax3.set_xlabel("horizontal distance x (m)")
    ax3.set_ylabel("height y (m)")
    ax3.set_title("Explicit Euler drifts as dt grows; RK4 survives")
    ax3.set_ylim(0, None)
    ax3.grid(alpha=0.3)
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "euler_failure.png", dpi=120)

    # sensitivity
    for cdv in (0.3, 0.4, 0.5):
        print(f"Cd {cdv}: range {simulate(v0, 40.0, h0, cd=cdv)['range']:.1f} m")
    for wv in (-5.0, 0.0, 5.0):
        print(f"wind {wv:+.0f} m/s: range {simulate(v0, 40.0, h0, wind=wv)['range']:.1f} m")

# %% [markdown]
# ## Where this stops
# The ball is a point with a constant drag coefficient, in still or steady-wind air, with no
# spin, swing, bounce or Magnus force. Real cricket balls swing and dip. This is a teaching
# model, not a coaching tool.
