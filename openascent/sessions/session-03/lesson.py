"""Session 3 (Level 3): fly a two-stage rocket to orbit with a gravity turn, and validate it.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: fly to orbit with a gravity turn and staging
# **A. Real-world problem.** Session 2 showed that a rocket going straight up comes back down.
# To stay in orbit it must end up moving sideways at about 7.8 km/s, above the air. So the
# rocket must turn over on the way up, but not too early (it would plough through thick air)
# and not too late (it would waste propellant fighting gravity). Can we fly a two-stage
# rocket to a 200 km orbit, check the simulation against the laws it must obey, and find
# the largest payload it can carry?
#
# **Plan.** (1) equations of motion in 2D around a round Earth, (2) the guidance: vertical
# rise, pitch kick, gravity turn, then an altitude-holding upper stage, (3) staging,
# (4) orbit from position and velocity, (5) validation: the delta-v budget closes, energy is
# conserved in a coast, the rocket equation is recovered, (6) the pitch-kick window and the
# payload mini-project.
#
# **Model.** A point mass in a plane through Earth's centre. Inverse-square gravity, a
# non-rotating spherical Earth, an exponential atmosphere, constant thrust and Isp per stage
# (no change of thrust with altitude). A simplified teaching model, not a mission design tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G0 = 9.80665          # m/s2, defines Isp
MU = 3.986004418e14   # m3/s2, G M of the Earth
R_EARTH = 6.371e6     # m
RHO0, H_SCALE = 1.225, 8500.0       # sea-level air density (kg/m3) and scale height (m)
H_TARGET = 200e3      # target circular orbit altitude, m
MIN_PERIGEE = 150e3   # we call it "in orbit" if the lowest point is above 150 km

# Teaching launcher (illustrative, not a real vehicle). F: thrust (N), isp (s), masses in kg.
LAUNCHER = [dict(prop=90000.0, dry=7000.0, isp=290.0, F=1.6e6),
            dict(prop=15000.0, dry=1500.0, isp=340.0, F=150e3)]
PAYLOAD = 1000.0
CD_A = 2.5            # drag coefficient times frontal area, m2 (Cd 0.4 on a 2.8 m wide body)


# %% [markdown]
# ## Step 1: forces and the equations of motion
# Put the Earth's centre at the origin and launch from the top of the circle, (0, R).
# The state is position (x, y), velocity (vx, vy) and mass m. Three forces act:
#
# * thrust F along the pointing direction d (a unit vector chosen by the guidance),
# * gravity  -G M m r_hat / r**2  (it weakens with height),
# * drag  D = 0.5 rho(h) v**2 Cd A  against the velocity, with rho(h) = rho0 exp(-h / H).
#
# So  a = F d / m - D v_hat / m - G M r_hat / r**2  and  dm/dt = -F / (Isp g0).
# We step it forward with Runge-Kutta 4 (four slope estimates per step, as in Session 2).

# %%
def density(h):
    """Exponential model of air density (kg/m3) at height h (m)."""
    return RHO0 * np.exp(-max(h, 0.0) / H_SCALE)


def orbit_elements(x, y, vx, vy):
    """Orbit through position (x, y) with velocity (vx, vy), all in m and m/s.

    Returns dict with specific energy eps (J/kg), eccentricity e, semi-major axis a (m) and
    perigee and apogee ALTITUDES hp, ha (m). From eps = v**2 / 2 - mu / r and h = r x v."""
    r = np.hypot(x, y)
    eps = 0.5 * (vx * vx + vy * vy) - MU / r
    h = x * vy - y * vx
    e = float(np.sqrt(max(0.0, 1.0 + 2.0 * eps * h * h / MU ** 2)))
    if eps >= 0:
        return dict(eps=eps, e=e, a=np.inf, hp=h * h / MU / (1 + e) - R_EARTH, ha=np.inf)
    a = -MU / (2.0 * eps)
    return dict(eps=eps, e=e, a=a, hp=a * (1 - e) - R_EARTH, ha=a * (1 + e) - R_EARTH)


# %% [markdown]
# ## Step 2: the guidance (where does the nose point?)
# * **Vertical rise** for `t_vert` seconds to clear the pad.
# * **Pitch kick**: tilt the thrust `kick` degrees east of vertical for `t_kick` seconds.
# * **Gravity turn**: point the thrust along the velocity. Gravity bends the path over by
#   itself, so the rocket turns without pushing sideways (no steering loss, low sideways load
#   in the thick lower air).
# * **Upper stage (altitude hold)**: after staging the rocket is high but slow. Stage 2
#   points mostly sideways and tilts up just enough to stop the climb near 200 km. The
#   vertical acceleration it asks for is a damped spring  a_cmd = w**2 (h_target - h) - 2 w v_r,
#   and the upward thrust share is sin(pitch) = (g - v_h**2 / r + a_cmd) m / F.
# * **Cut-off** when the orbit's energy equals that of a 200 km circular orbit
#   (semi-major axis a = R + 200 km).

# %%
def launch(stages=None, payload=PAYLOAD, kick=3.0, t_vert=10.0, t_kick=10.0, dt=0.2,
           gravity=True, drag=True, drop_stages=True, cutoff=True, upper="hold",
           h_target=H_TARGET, omega=0.04, cd_a=CD_A, tmax=2000.0):
    """Fly the launcher. Returns a dict with the time history and the final orbit.

    Keys: status ('orbit' or 'suborbital' or 'crashed'), t, x, y, vx, vy, m, stage (arrays),
    events (list of (name, time s, altitude m, speed m/s)), budget (ideal, gravity, drag,
    steering delta-v in m/s), orbit (dict from orbit_elements), max_q (Pa), max_q_time (s),
    prop_left (kg of stage-2 propellant left)."""
    stages = LAUNCHER if stages is None else stages
    if payload < 0 or kick < 0 or dt <= 0:
        raise ValueError("need payload >= 0, kick >= 0 and dt > 0")
    mu = MU if gravity else 0.0
    prop = [s["prop"] for s in stages]
    m = payload + sum(s["dry"] + s["prop"] for s in stages)
    x, y, vx, vy = 0.0, R_EARTH, 0.0, 0.0
    t, k = 0.0, 0
    budget = np.zeros(4)
    hist = [(t, x, y, vx, vy, m, k)]
    events, max_q, max_q_t = [], 0.0, 0.0
    kk = np.radians(kick)

    def accel(st, thrust, mode):
        x, y, vx, vy, m = st[:5]
        r = np.hypot(x, y)
        ux, uy = x / r, y / r                     # up
        ex, ey = uy, -ux                          # east (direction of launch)
        v = np.hypot(vx, vy)
        g = mu / r ** 2
        if mode == "vertical":
            dx, dy = ux, uy
        elif mode == "kick":
            dx, dy = np.cos(kk) * ux + np.sin(kk) * ex, np.cos(kk) * uy + np.sin(kk) * ey
        elif mode == "prograde":
            dx, dy = (vx / v, vy / v) if v > 1.0 else (ux, uy)
        else:                                     # altitude hold
            vr, vh = vx * ux + vy * uy, vx * ex + vy * ey
            a_cmd = omega ** 2 * (h_target - (r - R_EARTH)) - 2.0 * omega * vr
            s = np.clip((g - vh * vh / r + a_cmd) * m / thrust, -0.5, 0.95) if thrust > 0 else 0.0
            c = np.sqrt(1.0 - s * s)
            dx, dy = s * ux + c * ex, s * uy + c * ey
        dens = density(r - R_EARTH) if drag else 0.0
        D = 0.5 * dens * v * v * cd_a
        hx, hy = (vx / v, vy / v) if v > 1e-9 else (dx, dy)
        ax = thrust * dx / m - D * hx / m - g * ux
        ay = thrust * dy / m - D * hy / m - g * uy
        aT = thrust / m
        # rates of the four delta-v budget terms (their sum explains the speed change)
        rates = np.array([aT, g * (ux * hx + uy * hy), D / m, aT * (1.0 - (dx * hx + dy * hy))])
        return ax, ay, rates

    while t < tmax:
        if k < len(stages):
            thrust = stages[k]["F"]
            mdot = thrust / (stages[k]["isp"] * G0)
        else:
            thrust = mdot = 0.0
        if k == 0 or upper == "prograde":
            mode = "vertical" if t < t_vert else ("kick" if t < t_vert + t_kick else "prograde")
            if kick == 0:
                mode = "vertical" if mode == "kick" else mode
        else:
            mode = "hold"
        h = dt if mdot == 0 or prop[k] >= mdot * dt else prop[k] / mdot   # land exactly on burnout

        def f(st):
            ax, ay, rates = accel(st, thrust, mode)
            return np.r_[st[2], st[3], ax, ay, -mdot, rates]

        def rk4(st0, hh):
            k1 = f(st0)
            k2 = f(st0 + 0.5 * hh * k1)
            k3 = f(st0 + 0.5 * hh * k2)
            k4 = f(st0 + hh * k3)
            return st0 + hh * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0

        st0 = np.r_[x, y, vx, vy, m, budget]
        st = rk4(st0, h)
        a_goal = R_EARTH + h_target
        if cutoff and gravity and k == len(stages) - 1 and orbit_elements(*st[:4])["a"] >= a_goal:
            lo, hi = 0.0, h                       # cut-off falls inside this step: find it by bisection
            for _ in range(40):
                mid = 0.5 * (lo + hi)
                if orbit_elements(*rk4(st0, mid)[:4])["a"] >= a_goal:
                    hi = mid
                else:
                    lo = mid
            h = hi
            st = rk4(st0, h)
        x, y, vx, vy, m = st[:5]
        budget = st[5:]
        t += h
        if mdot > 0:
            prop[k] -= mdot * h
        r, v = np.hypot(x, y), np.hypot(vx, vy)
        q = 0.5 * (density(r - R_EARTH) if drag else 0.0) * v * v
        if q > max_q:
            max_q, max_q_t = q, t
        hist.append((t, x, y, vx, vy, m, k))
        if r < R_EARTH:
            events.append(("hit the ground", t, 0.0, v))
            break
        if k < len(stages) and prop[k] <= 1e-6:
            events.append((f"stage {k + 1} burnout", t, r - R_EARTH, v))
            if k == len(stages) - 1:
                break
            if drop_stages:
                m -= stages[k]["dry"]
                events.append((f"stage {k + 1} dropped", t, r - R_EARTH, v))
            k += 1
        if cutoff and k == len(stages) - 1 and gravity:
            if orbit_elements(x, y, vx, vy)["a"] >= R_EARTH + h_target - 1.0:
                events.append(("engine cut-off: in orbit", t, r - R_EARTH, v))
                break
    arr = np.array(hist)
    el = orbit_elements(x, y, vx, vy)
    if events and events[-1][0] == "hit the ground":
        status = "crashed"
    else:
        status = "orbit" if el["hp"] >= MIN_PERIGEE else "suborbital"
    return dict(status=status, t=arr[:, 0], x=arr[:, 1], y=arr[:, 2], vx=arr[:, 3], vy=arr[:, 4],
                m=arr[:, 5], stage=arr[:, 6], events=events, budget=budget, orbit=el,
                max_q=max_q, max_q_time=max_q_t, prop_left=prop[-1])


# %% [markdown]
# ## Step 3: validation tools
# * The **delta-v budget** must close: final speed = ideal - gravity loss - drag loss -
#   steering loss, because each term is the integral of one part of a . v_hat.
# * The **ideal** term must equal the rocket equation of Session 1 for the propellant used.
# * In a **coast** above the air the orbital energy v**2 / 2 - mu / r must stay constant.

# %%
def rocket_equation_dv(stages, payload, burnt=None):
    """Sum of ve ln(m0 / mf) for the stages; burnt gives the propellant used per stage (kg)."""
    burnt = [s["prop"] for s in stages] if burnt is None else burnt
    total = 0.0
    for i, s in enumerate(stages):
        above = payload + sum(t["prop"] + t["dry"] for t in stages[i + 1:])
        m0 = above + s["dry"] + s["prop"]
        total += s["isp"] * G0 * np.log(m0 / (m0 - burnt[i]))
    return float(total)


def coast(x, y, vx, vy, duration, dt=1.0):
    """Coast with gravity only (no thrust, no drag) using RK4. Returns arrays x, y, vx, vy."""
    n = int(round(duration / dt))
    s = np.array([x, y, vx, vy], float)
    out = np.empty((n + 1, 4))
    out[0] = s

    def f(s):
        r3 = np.hypot(s[0], s[1]) ** 3
        return np.array([s[2], s[3], -MU * s[0] / r3, -MU * s[1] / r3])

    for i in range(n):
        k1 = f(s)
        k2 = f(s + 0.5 * dt * k1)
        k3 = f(s + 0.5 * dt * k2)
        k4 = f(s + dt * k3)
        s = s + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        out[i + 1] = s
    return out.T


def altitude(res):
    """Altitude history (m) of a launch result."""
    return np.hypot(res["x"], res["y"]) - R_EARTH


def downrange(res):
    """Ground distance (m) along the Earth's surface under the rocket."""
    return R_EARTH * np.arctan2(res["x"], res["y"])


# %% [markdown]
# ## Step 4: the pitch-kick window and the payload mini-project

# %%
def kick_scan(kicks, payload=PAYLOAD, stages=None):
    """List of (kick, status, perigee km, propellant left kg) for each kick angle (degrees)."""
    rows = []
    for k in kicks:
        r = launch(stages, payload, kick=k)
        rows.append((float(k), r["status"], r["orbit"]["hp"] / 1000.0, r["prop_left"]))
    return rows


def max_payload(kicks=(2.0, 2.5, 3.0), step=250.0, stages=None, start=0.0):
    """Largest payload (kg, in multiples of step) that reaches orbit with the best of the kicks.

    Returns (payload, kick). Starts at `start` and goes up until no kick reaches orbit."""
    best = (None, None)
    p = start
    while p < 10000.0:
        ok = [k for k in kicks if launch(stages, p, kick=k)["status"] == "orbit"]
        if not ok:
            break
        best = (p, ok[0])
        p += step
    return best


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    # the reference flight
    res = launch()
    el, b = res["orbit"], res["budget"]
    v_end = np.hypot(res["vx"][-1], res["vy"][-1])
    print(f"status: {res['status']}, perigee {el['hp'] / 1000:.1f} km, apogee {el['ha'] / 1000:.1f} km, e = {el['e']:.4f}")
    for name, t, h, v in res["events"]:
        print(f"  t = {t:6.1f} s  {name:28s} altitude {h / 1000:6.1f} km  speed {v:6.0f} m/s")
    print(f"max dynamic pressure {res['max_q'] / 1000:.1f} kPa at t = {res['max_q_time']:.0f} s")
    print(f"delta-v budget: ideal {b[0]:.0f}, gravity {b[1]:.0f}, drag {b[2]:.0f}, steering {b[3]:.0f} m/s;"
          f" ideal - losses = {b[0] - b[1:].sum():.1f}, final speed {v_end:.1f} m/s")
    print(f"stage-2 propellant left {res['prop_left']:.0f} kg")

    # validation
    burnt = [LAUNCHER[0]["prop"], LAUNCHER[1]["prop"] - res["prop_left"]]
    print(f"rocket equation for the propellant used: {rocket_equation_dv(LAUNCHER, PAYLOAD, burnt):.1f} m/s (budget ideal {b[0]:.1f})")
    xs, ys, vxs, vys = coast(res["x"][-1], res["y"][-1], res["vx"][-1], res["vy"][-1], 3000.0)
    eps = 0.5 * (vxs ** 2 + vys ** 2) - MU / np.hypot(xs, ys)
    print(f"coast 3000 s: energy drift {abs(eps[-1] - eps[0]) / abs(eps[0]):.2e} (relative), lowest altitude {(np.hypot(xs, ys).min() - R_EARTH) / 1000:.1f} km")
    vert = launch(kick=0.0)
    nodrop = launch(drop_stages=False)
    print(f"no pitch kick: {vert['status']}, peak altitude {altitude(vert).max() / 1000:.0f} km")
    print(f"keep the empty stage 1: {nodrop['status']}, perigee {nodrop['orbit']['hp'] / 1000:.0f} km")

    # the pitch-kick window
    kicks = np.arange(1.0, 5.01, 0.5)
    scan = kick_scan(kicks)
    for k, s, hp, left in scan:
        print(f"kick {k:3.1f} deg: {s:10s} perigee {hp:8.1f} km  propellant left {left:6.0f} kg")

    # mini-project
    pmax, kbest = max_payload(start=1000.0)
    print(f"mini-project: largest payload in 250 kg steps = {pmax:.0f} kg (kick {kbest} deg)")

    # Figure 1: the trajectory, seen from the side, with the stage events
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))
    dr, al = downrange(res) / 1000, altitude(res) / 1000
    for st, colour, lab in ((0, "#264653", "stage 1"), (1, "#2a9d8f", "stage 2")):
        sel = res["stage"] == st
        ax1.plot(dr[sel], al[sel], color=colour, lw=2.2, label=lab)
    ax1.plot(downrange(vert) / 1000, altitude(vert) / 1000, color="#d9534f", ls="--", label="no pitch kick (falls back)")
    for name, t, h, v in res["events"]:
        if "dropped" in name or "cut-off" in name:
            i = np.searchsorted(res["t"], t)
            ax1.plot(dr[i], al[i], "ko", ms=5)
            ax1.annotate(name.replace(": in orbit", ""), (dr[i], al[i]), textcoords="offset points", xytext=(6, -14), fontsize=8)
    ax1.set_xlabel("downrange distance (km)")
    ax1.set_ylabel("altitude (km)")
    ax1.set_title("Climb, turn, stage, insert")
    ax1.set_ylim(0, 300)
    ax1.legend(fontsize=8, loc="upper right")
    ax1.grid(alpha=0.3)
    th = np.linspace(0, 2 * np.pi, 400)
    ax2.fill(R_EARTH / 1e3 * np.cos(th), R_EARTH / 1e3 * np.sin(th), color="#9ec5e8", alpha=0.6)
    ax2.plot(xs / 1e3, ys / 1e3, color="#2a9d8f", lw=1, ls=":", label="coast after cut-off")
    ax2.plot(res["x"] / 1e3, res["y"] / 1e3, color="#264653", lw=2, label="powered ascent")
    ax2.set_aspect("equal")
    ax2.set_xlabel("x (km)")
    ax2.set_ylabel("y (km)")
    ax2.set_title(f"Orbit {el['hp'] / 1000:.0f} km x {el['ha'] / 1000:.0f} km")
    ax2.legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(OUT / "ascent.png", dpi=120)

    # Figure 2: the delta-v budget and the kick window
    fig2, (axb, axk) = plt.subplots(1, 2, figsize=(10, 4.2))
    names = ["ideal\n(rocket eq.)", "gravity\nloss", "drag\nloss", "steering\nloss", "final\nspeed"]
    vals = [b[0], -b[1], -b[2], -b[3], v_end]
    cols = ["#264653", "#d9534f", "#e9a23b", "#8e6c8a", "#2a9d8f"]
    axb.bar(range(5), np.abs(vals), color=cols)
    for i, v in enumerate(vals):
        axb.text(i, abs(v) + 150, f"{v:+.0f}" if 0 < i < 4 else f"{v:.0f}", ha="center", fontsize=9)
    axb.set_xticks(range(5))
    axb.set_xticklabels(names, fontsize=8)
    axb.set_ylabel("delta-v (m/s)")
    axb.set_ylim(0, 11500)
    axb.set_title("Where the delta-v went (kick 3 degrees)")
    hp = [min(max(r[2], -100.0), 300.0) for r in scan]
    colours = ["#2a9d8f" if r[1] == "orbit" else "#d9534f" for r in scan]
    axk.bar(kicks, hp, width=0.35, color=colours)
    axk.axhline(MIN_PERIGEE / 1000, color="k", ls="--", lw=1)
    axk.text(1.0, MIN_PERIGEE / 1000 + 8, "orbit if perigee above 150 km", fontsize=8)
    axk.set_xlabel("pitch kick (degrees from vertical)")
    axk.set_ylabel("perigee altitude (km, clipped at -100)")
    axk.set_title("Too little or too much kick fails")
    axk.set_ylim(-110, 320)
    fig2.tight_layout()
    fig2.savefig(OUT / "budget_and_window.png", dpi=120)

    # Figure 3: speed, altitude and acceleration against time
    fig3, axs = plt.subplots(1, 3, figsize=(11, 3.6))
    v = np.hypot(res["vx"], res["vy"])
    acc = np.gradient(v, res["t"])
    axs[0].plot(res["t"], al, color="#264653")
    axs[0].set_ylabel("altitude (km)")
    axs[1].plot(res["t"], v / 1000, color="#2a9d8f")
    axs[1].set_ylabel("speed (km/s)")
    axs[2].plot(res["t"], acc / G0, color="#d9534f")
    axs[2].set_ylabel("speed gain rate (g)")
    for a in axs:
        a.set_xlabel("time (s)")
        a.axvline(res["events"][0][1], color="grey", ls=":", lw=1)
        a.grid(alpha=0.3)
    axs[1].text(res["events"][0][1] + 5, 0.3, "staging", fontsize=8, color="grey")
    fig3.suptitle("The reference flight: acceleration jumps down at staging, then climbs as stage 2 empties", fontsize=10)
    fig3.tight_layout()
    fig3.savefig(OUT / "time_histories.png", dpi=120)

    up = OUT.resolve().parents
    docs = up[2] / "docs" / "figures" if len(up) > 2 else OUT    # repo/docs/figures, when run from the repo
    if docs != OUT and docs.exists() and (docs.parent.parent / "start.py").exists():
        fig.savefig(docs / "s03_ascent.png", dpi=120)
        fig2.savefig(docs / "s03_budget_and_window.png", dpi=120)
        fig3.savefig(docs / "s03_time_histories.png", dpi=120)

# %% [markdown]
# ## Where this stops
# A flat, non-rotating Earth, constant thrust and a fixed pitch program are still crude.
# Real launches use Earth's spin, thrust that changes with altitude, optimal (not just
# reasonable) steering and limits on loads. That is the road to the Target: see
# `promo/roadmap.md`.
