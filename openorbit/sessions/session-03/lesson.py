"""Session 3 (Level 3): plan a transfer orbit, then check it by integrating the trajectory.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: Hohmann transfers, and checking them numerically
# **A. Real-world problem.** A satellite is released in a low circular orbit and must reach a
# higher one. Fuel is the scarcest thing on board, so every m/s of speed change (delta-v) counts.
# Today you plan the cheapest simple transfer (the Hohmann transfer), compare it with a
# three-burn alternative (bi-elliptic), price a plane change, catch a target by phasing, and
# then check every claim by integrating the real motion step by step.
# The model: instant burns ("impulses"), two bodies only (point-mass Earth and satellite),
# circular coplanar orbits. This is a teaching model, not a mission design tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
MU = 3.986004418e14      # m^3/s^2
R_EARTH = 6.371e6        # m


# %% [markdown]
# ## Step 1: the Hohmann transfer
# The transfer ellipse touches the inner circle (radius r1) at perigee and the outer circle
# (radius r2) at apogee, so its semi-major axis is a_t = (r1 + r2) / 2. Use vis-viva:
# burn 1 raises speed at r1 from the circular speed to the perigee speed of the ellipse;
# burn 2 raises it at r2 from the ellipse's apogee speed to the circular speed. The flight takes
# half of the ellipse's period.

# %%
def circular_speed(r):
    return np.sqrt(MU / r)


def vis_viva(r, a):
    return np.sqrt(MU * (2 / r - 1 / a))


def period(a):
    return 2 * np.pi * np.sqrt(a**3 / MU)


def hohmann(r1, r2):
    """Hohmann transfer between circular orbits of radii r1 and r2 (m). Speeds in m/s, time in s."""
    a_t = 0.5 * (r1 + r2)
    dv1 = vis_viva(r1, a_t) - circular_speed(r1)
    dv2 = circular_speed(r2) - vis_viva(r2, a_t)
    return {"dv1": dv1, "dv2": dv2, "total": abs(dv1) + abs(dv2), "time": 0.5 * period(a_t), "a_t": a_t}


# %% [markdown]
# ## Step 2: check it by integrating the motion
# We do not just trust the formula. Start on the inner circle, add dv1 along the velocity, and
# integrate the two-body equations (RK4, small steps) for the predicted time. If the plan is right
# we arrive at radius r2, on the opposite side of the Earth, moving at the apogee speed.

# %%
def accel(r):
    return -MU * r / np.linalg.norm(r) ** 3


def rk4_step(r, v, dt, thrust=None):
    """One RK4 step. thrust: optional function (r, v) -> extra acceleration (m/s^2)."""
    def f(rr, vv):
        a = accel(rr)
        if thrust is not None:
            a = a + thrust(rr, vv)
        return a
    k1v = f(r, v); k1r = v
    k2v = f(r + 0.5 * dt * k1r, v + 0.5 * dt * k1v); k2r = v + 0.5 * dt * k1v
    k3v = f(r + 0.5 * dt * k2r, v + 0.5 * dt * k2v); k3r = v + 0.5 * dt * k2v
    k4v = f(r + dt * k3r, v + dt * k3v); k4r = v + dt * k3v
    return r + dt / 6 * (k1r + 2 * k2r + 2 * k3r + k4r), v + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)


def integrate(r0, v0, t_end, dt=5.0, thrust=None):
    """Integrate from t = 0 to t_end. Returns (times, positions, velocities)."""
    n = int(np.ceil(t_end / dt))
    h = t_end / n
    r, v = np.array(r0, float), np.array(v0, float)
    ts, rs, vs = [0.0], [r.copy()], [v.copy()]
    for i in range(n):
        r, v = rk4_step(r, v, h, thrust)
        ts.append((i + 1) * h); rs.append(r.copy()); vs.append(v.copy())
    return np.array(ts), np.array(rs), np.array(vs)


def check_hohmann(r1, r2, dt=5.0):
    """Fly the Hohmann transfer numerically. Returns arrival radius, arrival speed, arrival angle and the later circle error."""
    h = hohmann(r1, r2)
    r0 = np.array([r1, 0.0])
    v0 = np.array([0.0, circular_speed(r1) + h["dv1"]])
    ts, rs, vs = integrate(r0, v0, h["time"], dt)
    r_end, v_end = rs[-1], vs[-1]
    angle = np.degrees(np.arctan2(r_end[1], r_end[0])) % 360
    # second burn: add dv2 along the velocity, then fly one full lap of the outer circle
    v_new = v_end + h["dv2"] * v_end / np.linalg.norm(v_end)
    lap = 2 * np.pi * r2 / circular_speed(r2)
    _, rs2, _ = integrate(r_end, v_new, lap, dt)
    err = np.max(np.abs(np.linalg.norm(rs2, axis=1) - r2))
    return {"r_end": np.linalg.norm(r_end), "v_end": np.linalg.norm(v_end), "angle": angle, "circle_err": err}


# %% [markdown]
# ## Step 3: bi-elliptic transfer, a plane change, Oberth, phasing
# *Bi-elliptic*: go out to a far radius rb, then to r2, then back to circular: three burns. For
# a big enough ratio r2 / r1 it costs less delta-v than Hohmann, but takes much longer.
# *Plane change*: turning the velocity direction by an angle di costs 2 v sin(di / 2).
# *Oberth*: the energy a burn adds is v dv + dv^2 / 2, so the same dv gives more energy when v is high.

# %%
def bielliptic(r1, r2, rb):
    a1, a2 = 0.5 * (r1 + rb), 0.5 * (rb + r2)
    dv1 = vis_viva(r1, a1) - circular_speed(r1)
    dv2 = vis_viva(rb, a2) - vis_viva(rb, a1)
    dv3 = abs(circular_speed(r2) - vis_viva(r2, a2))
    return {"dv1": dv1, "dv2": dv2, "dv3": dv3, "total": dv1 + dv2 + dv3, "time": 0.5 * period(a1) + 0.5 * period(a2)}


def cost_ratio(ratio, rb_over_r1=1e6):
    """Bi-elliptic total delta-v divided by Hohmann total delta-v, for r2 / r1 = ratio (very far rb)."""
    r1 = 1.0e7
    return bielliptic(r1, ratio * r1, rb_over_r1 * r1)["total"] / hohmann(r1, ratio * r1)["total"]


def crossover_ratio(lo=8.0, hi=16.0):
    """Radius ratio where bi-elliptic (rb very far) starts to beat Hohmann, by bisection."""
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if cost_ratio(mid) > 1:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def plane_change_dv(v, di_deg):
    """Delta-v (m/s) to rotate a velocity of size v (m/s) by di_deg degrees, speed unchanged."""
    return 2 * v * np.sin(np.radians(di_deg) / 2)


def combined_burn_dv(v1, v2, di_deg):
    """Delta-v (m/s) to change speed from v1 to v2 and turn the direction by di_deg in one burn."""
    return np.sqrt(v1**2 + v2**2 - 2 * v1 * v2 * np.cos(np.radians(di_deg)))


def energy_gain(v, dv):
    """Energy per kg (J/kg) gained by adding dv to speed v: change in 0.5 v^2."""
    return 0.5 * (v + dv) ** 2 - 0.5 * v**2


# %% [markdown]
# ## Step 4: phasing, and why impulses are only a model
# *Phasing*: a chaser in a lower orbit has a higher angular rate and gains on a target that is
# ahead. We find the catch-up time numerically from simulated angles. And a real engine does
# not push for an instant: a long, weak burn wastes some of its push fighting gravity.

# %%
def phasing_time(r_chaser, r_target, lead_deg, dt=10.0):
    """Time (s) until a chaser in the lower orbit reaches the target, which starts lead_deg ahead.

    Both circular orbits are flown with RK4; the time is found where the angle gap first changes sign.
    """
    t_max = 2 * np.pi / (np.sqrt(MU / r_chaser**3) - np.sqrt(MU / r_target**3)) * 1.1
    out = []
    for r, ang in ((r_chaser, 0.0), (r_target, np.radians(lead_deg))):
        pos = np.array([r * np.cos(ang), r * np.sin(ang)])
        vel = circular_speed(r) * np.array([-np.sin(ang), np.cos(ang)])
        ts, rs, _ = integrate(pos, vel, t_max, dt)
        out.append(np.unwrap(np.arctan2(rs[:, 1], rs[:, 0])))
    gap = out[1] - out[0]
    k = int(np.argmax(gap <= 0))
    return float(ts[k - 1] + (ts[k] - ts[k - 1]) * gap[k - 1] / (gap[k - 1] - gap[k]))


def phasing_formula(r_chaser, r_target, lead_deg):
    n1, n2 = np.sqrt(MU / r_chaser**3), np.sqrt(MU / r_target**3)
    return np.radians(lead_deg) / (n1 - n2)


def orbit_apogee(r, v):
    """Apogee radius (m) of the Kepler orbit through position r and velocity v (2D arrays)."""
    rn = np.linalg.norm(r)
    energy = 0.5 * np.dot(v, v) - MU / rn
    a = -MU / (2 * energy)
    evec = ((np.dot(v, v) - MU / rn) * r - np.dot(r, v) * v) / MU
    if energy >= 0:
        return np.inf
    return a * (1 + np.linalg.norm(evec))


def finite_burn(r1, burn_time, accel_ms2, dt=2.0):
    """Burn along the velocity with constant acceleration, starting from the circular orbit of radius r1.
    Returns the apogee radius (m) of the orbit the satellite is left in (inf if it escapes)."""
    r0, v0 = np.array([r1, 0.0]), np.array([0.0, circular_speed(r1)])
    thrust = lambda rr, vv: accel_ms2 * vv / np.linalg.norm(vv)
    _, rs, vs = integrate(r0, v0, burn_time, dt, thrust)
    return orbit_apogee(rs[-1], vs[-1])


def finite_burn_cost(r1, r2, accel_ms2, dt=2.0):
    """Delta-v (m/s) a constant-acceleration burn really needs to reach apogee r2, found by bisection on burn time.
    Compare with the impulsive hohmann(r1, r2)['dv1']; the difference is the gravity loss."""
    lo, hi = 0.0, 3.0 * hohmann(r1, r2)["dv1"] / accel_ms2
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if finite_burn(r1, mid, accel_ms2, dt) < r2:
            lo = mid
        else:
            hi = mid
    return accel_ms2 * 0.5 * (lo + hi)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    r1, r2 = 6778e3, 42164e3
    h = hohmann(r1, r2)
    print(f"LEO 6778 km -> GEO 42164 km: dv1 {h['dv1'] / 1e3:.3f}, dv2 {h['dv2'] / 1e3:.3f}, total {h['total'] / 1e3:.3f} km/s, time {h['time'] / 3600:.3f} h, a_t {h['a_t'] / 1e3:.0f} km")
    c = check_hohmann(r1, r2)
    print(f"integrated: arrival radius {c['r_end'] / 1e3:.1f} km, speed {c['v_end']:.1f} m/s (apogee speed {vis_viva(r2, h['a_t']):.1f}), angle {c['angle']:.2f} deg, later circle error {c['circle_err']:.1f} m")

    for ratio in (5, 10, 11.94, 15, 20, 50):
        print(f"ratio {ratio:5}: bi-elliptic / Hohmann = {cost_ratio(ratio):.4f}")
    print(f"crossover ratio {crossover_ratio():.3f}")
    b = bielliptic(r1, r2, 20 * r2)
    print(f"LEO->GEO bi-elliptic rb = 20 r2: total {b['total'] / 1e3:.3f} km/s, time {b['time'] / 86400:.1f} days")
    r_a, r_b = 6778e3, 6778e3 * 20
    print("ratio 20, rb=100 r1: hohmann", hohmann(r_a, 20 * r_a)["total"], "bielliptic", bielliptic(r_a, 20 * r_a, 100 * r_a)["total"])

    di = 28.5
    vleo, vgeo = circular_speed(r1), circular_speed(r2)
    vapo = vis_viva(r2, h["a_t"])
    print(f"plane change {di} deg: at LEO {plane_change_dv(vleo, di) / 1e3:.3f}, at GEO {plane_change_dv(vgeo, di) / 1e3:.3f}, at transfer apogee {plane_change_dv(vapo, di) / 1e3:.3f} km/s")
    print(f"apogee speed {vapo / 1e3:.3f}, combined apogee burn {combined_burn_dv(vapo, vgeo, di) / 1e3:.3f} vs separate {(abs(vgeo - vapo) + plane_change_dv(vgeo, di)) / 1e3:.3f} km/s")
    print(f"Oberth: 1000 m/s at {vleo:.0f} m/s adds {energy_gain(vleo, 1000) / 1e6:.3f} MJ/kg, at 1000 m/s adds {energy_gain(1000, 1000) / 1e6:.3f} MJ/kg")

    rl, rt = 6778e3, 7178e3
    print(f"phasing: numeric {phasing_time(rl, rt, 30):.1f} s, formula {phasing_formula(rl, rt, 30):.1f} s")

    for acc in (20.0, 2.0, 0.5):
        tb = h["dv1"] / acc
        ra = finite_burn(r1, tb, acc)
        need = finite_burn_cost(r1, r2, acc)
        print(f"finite burn {acc} m/s^2: burn {tb:.0f} s ({tb / period(r1):.2f} LEO laps), apogee {ra / 1e3:.0f} km (impulsive 42164), real dv needed {need:.0f} m/s, extra {need - h['dv1']:.0f} m/s ({(need - h['dv1']) / h['dv1']:.1%})")

    # Figure 1: delta-v ratio vs radius ratio
    rr = np.linspace(2, 40, 200)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(rr, [cost_ratio(x) for x in rr], label="bi-elliptic (far apogee) / Hohmann")
    ax.axhline(1, color="gray", ls=":")
    ax.axvline(crossover_ratio(), color="red", ls="--", label=f"crossover {crossover_ratio():.2f}")
    ax.set_xlabel("radius ratio r2 / r1 (no unit)"); ax.set_ylabel("delta-v ratio (no unit)")
    ax.set_title("When is three burns cheaper than two?"); ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(OUT / "bielliptic_vs_hohmann.png", dpi=120)

    # Figure 2: the integrated transfer
    h2 = hohmann(r1, r2)
    ts, rs, vs = integrate([r1, 0], [0, circular_speed(r1) + h2["dv1"]], h2["time"], 10.0)
    th = np.linspace(0, 2 * np.pi, 300)
    fig2, ax2 = plt.subplots(figsize=(5.5, 5.5))
    ax2.fill(R_EARTH / 1e3 * np.cos(th), R_EARTH / 1e3 * np.sin(th), color="#9ecae1")
    ax2.plot(r1 / 1e3 * np.cos(th), r1 / 1e3 * np.sin(th), "k--", lw=0.8)
    ax2.plot(r2 / 1e3 * np.cos(th), r2 / 1e3 * np.sin(th), "k--", lw=0.8)
    ax2.plot(rs[:, 0] / 1e3, rs[:, 1] / 1e3, "r-", label="integrated transfer")
    ax2.plot([r1 / 1e3], [0], "go", label="burn 1"); ax2.plot([-r2 / 1e3], [0], "bo", label="burn 2")
    ax2.set_aspect("equal"); ax2.set_xlabel("x (km)"); ax2.set_ylabel("y (km)")
    ax2.set_title("LEO to GEO Hohmann transfer"); ax2.legend(loc="upper right", fontsize=8); ax2.grid(alpha=0.3)
    fig2.tight_layout(); fig2.savefig(OUT / "hohmann_integrated.png", dpi=120)

    # Figure 3: plane change cost against speed
    ang = np.linspace(0, 60, 100)
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    for name, v in (("LEO", vleo), ("GEO", vgeo), ("transfer apogee", vapo)):
        ax3.plot(ang, plane_change_dv(v, ang) / 1e3, label=f"{name}, v = {v / 1e3:.2f} km/s")
    ax3.set_xlabel("plane change (degrees)"); ax3.set_ylabel("delta-v (km/s)")
    ax3.set_title("Plane changes are cheap where you are slow"); ax3.legend(); ax3.grid(alpha=0.3)
    fig3.tight_layout(); fig3.savefig(OUT / "plane_change.png", dpi=120)

    # Mini-project
    m1, m2 = R_EARTH + 500e3, R_EARTH + 20200e3
    hm = hohmann(m1, m2)
    cm = check_hohmann(m1, m2)
    print(f"mini-project: r1 {m1 / 1e3:.0f}, r2 {m2 / 1e3:.0f}: dv1 {hm['dv1']:.1f}, dv2 {hm['dv2']:.1f}, total {hm['total']:.1f} m/s, time {hm['time'] / 3600:.3f} h; arrival r {cm['r_end'] / 1e3:.2f} km, angle {cm['angle']:.2f}, circle err {cm['circle_err']:.1f} m")
    print("ratio r2/r1", m2 / m1)
