"""Session 3 (Level 3): simulate a hot day hour by hour, validate the model, and choose a passive design.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a whole day in the room, step by step
# **A. Real-world problem.** Session 1 gave one steady temperature for fixed conditions.
# Session 2 gave the sun and the air flow at one moment. But the sun moves, the outdoor
# temperature swings from 27 C at dawn to 35 C in the afternoon, and the floor slab soaks
# up heat by day and gives it back at night. Can we step through a whole day, check the
# simulation against Session 1 and the energy balance, and then choose the cheapest set of
# passive measures (sunshade, white roof, night ventilation) that keeps a top-floor room in
# Chennai comfortable?
#
# **Plan.** (1) a hot-day weather model, (2) a two-part room model: air plus thermal mass,
# (3) validation, (4) ventilation strategies, (5) a comfort limit, (6) design choice.
#
# **Model.** Clear-sky sun, sinusoidal outdoor temperature, one lumped thermal mass, roof
# without its own heat storage. A simplified teaching model, not a design tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
RHO_CP = 1200.0            # J/(m3 K) for air
LAT, DAY = 13.08, 105      # Chennai, 15 April
WEST = 270.0               # azimuth the window wall faces (degrees)


# %% [markdown]
# ## Step 1: sun and weather for a hot day (from Session 2)
# The sun functions are copied from Session 2 so this file runs on its own. The outdoor air
# temperature follows a daily wave: mean 31 C, swing +/- 4.5 K, hottest at 15:00.
#
#     T_out(t) = T_mean + T_amp cos(2 pi (t - 15) / 24)

# %%
def sun_position(lat, day, hour):
    """(altitude, azimuth) in degrees for solar time `hour`; azimuth clockwise from north."""
    d = np.radians(23.45 * np.sin(np.radians(360.0 * (284 + day) / 365.0)))
    phi, w = np.radians(lat), np.radians(15.0 * (np.asarray(hour, float) - 12.0))
    alt = np.arcsin(np.clip(np.sin(phi) * np.sin(d) + np.cos(phi) * np.cos(d) * np.cos(w), -1, 1))
    east, north = -np.cos(d) * np.sin(w), np.cos(phi) * np.sin(d) - np.sin(phi) * np.cos(d) * np.cos(w)
    return np.degrees(alt), np.degrees(np.arctan2(east, north)) % 360.0


def beam_normal(alt):
    """Clear-sky beam irradiance (W/m2) with A = 1100 W/m2, B = 0.18."""
    s = np.sin(np.radians(alt))
    return np.where(s > 0.01, 1100.0 * np.exp(-0.18 / np.maximum(s, 0.01)), 0.0)


def window_sun(hour, depth, gap=0.3, height=1.5, wall_az=WEST):
    """Sun on the window glass (W/m2) under an overhang of `depth` m (beam shaded, diffuse not)."""
    alt, az = sun_position(LAT, DAY, hour)
    g = np.radians((az - wall_az + 180.0) % 360.0 - 180.0)
    cos_t = np.cos(np.radians(alt)) * np.cos(g)
    tan_om = np.tan(np.radians(np.clip(alt, 0, 89.9))) / np.maximum(np.cos(g), 1e-9)
    f = np.where(cos_t > 0, np.clip((depth * tan_om - gap) / height, 0, 1), 1.0)
    idn = beam_normal(alt)
    diffuse = 0.5 * idn * (0.12 + 0.2 * (np.maximum(np.sin(np.radians(alt)), 0) + 0.12))
    return np.where(alt > 0, idn * np.maximum(cos_t, 0) * (1 - f) + diffuse, 0.0)


def roof_sun(hour):
    """Sun on a flat roof (W/m2): beam times sin(altitude) plus sky diffuse 0.12 x beam."""
    alt, _ = sun_position(LAT, DAY, hour)
    idn = beam_normal(alt)
    return np.where(alt > 0, idn * (np.sin(np.radians(alt)) + 0.12), 0.0)


def outdoor_temperature(hour, t_mean=31.0, t_amp=4.5, t_peak=15.0):
    """Outdoor air temperature (C) on the design day."""
    return t_mean + t_amp * np.cos(2 * np.pi * (np.asarray(hour, float) - t_peak) / 24.0)


# %% [markdown]
# ## Step 2: the sol-air temperature of the roof
# A sunlit roof gets much hotter than the air. Its effect on the room is as if the outdoor air
# above it were at the **sol-air temperature**
#
#     T_sa = T_out + a I_roof / h_o - dR
#
# a = solar absorptance of the roof surface (about 0.8 for dark concrete, 0.3 for white lime
# or reflective paint), h_o = 20 W/(m2 K) outside surface coefficient, and dR = 3.9 K for
# the heat a flat roof radiates to the cold sky. A white roof is "shading" for the roof.

# %%
def sol_air(t_out, i_roof, absorptance, h_o=20.0, sky=3.9):
    """Sol-air temperature (C) of a flat roof."""
    if not (0 <= absorptance <= 1):
        raise ValueError("absorptance must be between 0 and 1")
    return t_out + absorptance * i_roof / h_o - sky


# %% [markdown]
# ## Step 3: a room with thermal mass
# The room has two parts:
#
# * **air** (small heat capacity, treated as always in balance), temperature T_a
# * **mass** (floor slab and inner walls, heat capacity C_m in J/K), temperature T_m,
#   linked to the air by a conductance hA (W/K)
#
# Air balance (no storage):
#
#     0 = UA_w (T_out - T_a) + UA_r (T_sa - T_a) + H_v (T_out - T_a) + hA (T_m - T_a) + Q_int + (1 - f) Q_sun
#
# so T_a is a weighted average of T_out, T_sa and T_m plus the heat gains. Mass balance:
#
#     C_m dT_m/dt = hA (T_a - T_m) + f Q_sun
#
# f = share of the window sun that lands on the floor (0.7). We step the mass equation with
# Runge-Kutta 4 every 5 minutes. We want the day that repeats itself (a "periodic steady
# state"): the mass ends the day at the temperature it started with.

# %%
ROOM = {
    "volume": 48.0, "ua_wall": 30.0,  # brick wall 10 m2 x 2 + glass 2 m2 x 5 (W/K)
    "ua_roof": 40.0,                  # concrete roof 16 m2 x 2.5 (W/K)
    "window_area": 2.0, "shgc": 0.8, "f_mass": 0.7,
    "c_mass": 6.0e6,                  # J/K: about 16 m2 of 150 mm slab plus inner walls
    "ha_mass": 400.0,                 # W/K: about 50 m2 of surface at 8 W/(m2 K)
    "q_int": 250.0,                   # W: two people and lamps
    "ach_closed": 0.5, "ach_open": 20.0,
}


def air_temperature(t_m, t_out, t_sa, h_v, q_sun, room=ROOM):
    """Indoor air temperature (C) from the air heat balance (no air storage)."""
    uw, ur, ha, f = room["ua_wall"], room["ua_roof"], room["ha_mass"], room["f_mass"]
    num = (uw + h_v) * t_out + ur * t_sa + ha * t_m + room["q_int"] + (1 - f) * q_sun
    return num / (uw + ur + h_v + ha)


def ach_schedule(strategy, hour, room=ROOM):
    """Air changes per hour for a ventilation strategy at solar time `hour`.

    'closed' : windows shut all day (infiltration only)
    'open'   : windows open all day
    'night'  : night flushing, open 19:00 to 07:00, shut by day"""
    h = np.asarray(hour, float) % 24.0
    if strategy == "closed":
        return np.full_like(h, room["ach_closed"])
    if strategy == "open":
        return np.full_like(h, room["ach_open"])
    if strategy == "night":
        return np.where((h >= 19.0) | (h < 7.0), room["ach_open"], room["ach_closed"])
    raise ValueError("strategy must be 'closed', 'open' or 'night'")


def simulate_day(depth=0.0, absorptance=0.8, strategy="closed", room=ROOM, dt_min=5.0, forcing=None,
                 t_mean=31.0, t_amp=4.5):
    """Step the room through one day and return its periodic steady state.

    The model is linear in T_m, so one day maps the start temperature T0 to an end
    temperature A T0 + B. Two trial days (T0 = 0 and T0 = 1) give A and B, and the day that
    repeats itself starts at T0 = B / (1 - A). `forcing`, if given, is a function
    hour -> (t_out, t_sa, q_sun, ach) that replaces the weather (used for validation)."""
    if dt_min <= 0 or 1440.0 % dt_min:
        raise ValueError("dt_min must divide 1440 minutes")
    dt = 60.0 * dt_min
    n = int(round(24 * 60 / dt_min))
    vol, c, ha, f = room["volume"], room["c_mass"], room["ha_mass"], room["f_mass"]
    half = dt_min / 120.0 * np.arange(2 * n + 1)            # forcing on a half-step grid (h)
    if forcing is not None:
        t_o, t_sa, q_sun, ach = (np.asarray(x, float) * np.ones_like(half) for x in forcing(half))
    else:
        t_o = outdoor_temperature(half, t_mean, t_amp)
        t_sa = sol_air(t_o, roof_sun(half), absorptance)
        q_sun = room["shgc"] * room["window_area"] * window_sun(half, depth)
        ach = ach_schedule(strategy, half, room)
    h_v = RHO_CP * ach * vol / 3600.0
    # T_a = a0 + a1 T_m on every grid point, so dT_m/dt = k0 + k1 T_m
    den = room["ua_wall"] + room["ua_roof"] + h_v + ha
    a0 = ((room["ua_wall"] + h_v) * t_o + room["ua_roof"] * t_sa + room["q_int"] + (1 - f) * q_sun) / den
    a1 = ha / den
    k0, k1 = (ha * a0 + f * q_sun) / c, ha * (a1 - 1.0) / c

    def one_day(t0):
        tm = np.empty(n + 1)
        tm[0] = t0
        for i in range(n):
            j = 2 * i
            r = lambda jj, t: k0[jj] + k1[jj] * t
            q1 = r(j, tm[i])
            q2 = r(j + 1, tm[i] + dt / 2 * q1)
            q3 = r(j + 1, tm[i] + dt / 2 * q2)
            q4 = r(j + 2, tm[i] + dt * q3)
            tm[i + 1] = tm[i] + dt * (q1 + 2 * q2 + 2 * q3 + q4) / 6.0
        return tm

    e0, e1 = one_day(0.0)[-1], one_day(1.0)[-1]
    tm = one_day(e0 / (1.0 - (e1 - e0)))
    g = slice(0, 2 * n + 1, 2)                               # whole-step points
    hours = half[g]
    t_a = a0[g] + a1[g] * tm
    gains = (room["ua_wall"] + h_v[g]) * (t_o[g] - t_a) + room["ua_roof"] * (t_sa[g] - t_a) + room["q_int"] + q_sun[g]
    stored = c * (tm[-1] - tm[0])
    gain_int = float(np.sum(0.5 * (gains[1:] + gains[:-1])) * dt)
    return {"hour": hours, "t_air": t_a, "t_mass": tm, "t_out": t_o[g], "t_sa": t_sa[g], "q_sun": q_sun[g], "ach": ach[g],
            "peak": float(t_a.max()), "mean": float(t_a[:-1].mean()),
            "energy_residual": gain_int - stored, "energy_scale": float(np.sum(np.abs(gains[1:])) * dt),
            "periodic_error": float(abs(tm[-1] - tm[0]))}


# %% [markdown]
# ## Step 4: when is the room comfortable?
# People in naturally ventilated buildings adapt to the climate. The adaptive comfort model
# of ASHRAE Standard 55 sets a neutral temperature `T_n = 0.31 T_pma + 17.8` from the
# prevailing mean outdoor temperature T_pma, with an 80 percent acceptability band of
# +/- 3.5 K. For T_pma = 31 C the upper limit is 30.9 C. Moving air from a ceiling fan
# (about 0.9 m/s) raises the limit by 1.8 K, to 32.7 C; we use that, because almost every
# room in India has a fan. We use the indoor air temperature as a stand-in for the
# operative temperature people feel, and count **discomfort degree-hours**: how many kelvin
# above the limit, summed over the hours of the day.

# %%
def comfort_upper_limit(t_pma, band=3.5, fan_bonus=0.0):
    """Upper limit (C) of the adaptive comfort band for naturally ventilated rooms.

    `fan_bonus` (K) is the extra allowance for air movement from a ceiling fan."""
    if not (10.0 <= t_pma <= 33.5):
        raise ValueError("the adaptive model applies for prevailing mean outdoor 10 to 33.5 C")
    if fan_bonus < 0:
        raise ValueError("fan bonus must not be negative")
    return 0.31 * t_pma + 17.8 + band + fan_bonus


def degree_hours(hours, temps, limit):
    """Kelvin-hours above `limit` (trapezoid rule over the hours given)."""
    excess = np.maximum(np.asarray(temps, float) - limit, 0.0)
    return float(np.sum(0.5 * (excess[1:] + excess[:-1]) * np.diff(hours)))


# %% [markdown]
# ## Step 5: choosing a design (the mini-project)
# Each measure has a rough cost (illustrative rupees, not quotations). We try every
# combination and keep the cheapest that keeps discomfort below a target.

# %%
OPTIONS = {
    "depth": {0.0: 0, 0.6: 6000, 1.2: 12000},     # overhang depth (m): cost in rupees
    "absorptance": {0.8: 0, 0.3: 8000},           # roof: plain concrete or white-coated
    "strategy": {"closed": 0, "open": 0, "night": 1500},   # night: insect mesh and secure grille
}


def choose_design(max_degree_hours, limit, options=OPTIONS):
    """Cheapest (cost, depth, absorptance, strategy, degree_hours, peak) with discomfort <= the target."""
    best = None
    for d, cd in options["depth"].items():
        for a, ca in options["absorptance"].items():
            for s, cs in options["strategy"].items():
                r = simulate_day(d, a, s)
                dh = degree_hours(r["hour"], r["t_air"], limit)
                cand = (cd + ca + cs, d, a, s, dh, r["peak"])
                if dh <= max_degree_hours and (best is None or cand[0] < best[0] or (cand[0] == best[0] and dh < best[4])):
                    best = cand
    return best


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    limit = comfort_upper_limit(31.0, fan_bonus=1.8)
    print(f"adaptive comfort upper limit for prevailing mean 31 C: {comfort_upper_limit(31.0):.2f} C, with a ceiling fan {limit:.2f} C")

    # validation 1: constant weather must reproduce the Session 1 steady formula
    const = lambda h: (34.0, 34.0, 160.0, 10.0)
    v = simulate_day(forcing=const)
    h_v = RHO_CP * 10.0 * 48.0 / 3600.0
    t_s1 = 34.0 + (160.0 + 250.0) / (70.0 + h_v)
    print(f"validation: constant inputs give {v['t_air'][-1]:.4f} C, Session 1 formula {t_s1:.4f} C")

    # Figure 1: four designs through the day (this is also the promo Target figure)
    designs = [("as built: no shade, dark roof, closed", 0.0, 0.8, "closed", "#d9534f"),
               ("0.6 m overhang + white roof, closed", 0.6, 0.3, "closed", "#e9a23b"),
               ("as built, windows open all day", 0.0, 0.8, "open", "#90a4ae"),
               ("0.6 m overhang + white roof, open all day", 0.6, 0.3, "open", "#264653"),
               ("0.6 m overhang + white roof + night flush", 0.6, 0.3, "night", "#2a9d8f")]
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    res = {}
    for name, d, a, s, col in designs:
        r = simulate_day(d, a, s)
        res[name] = r
        dh = degree_hours(r["hour"], r["t_air"], limit)
        ax.plot(r["hour"], r["t_air"], color=col, lw=2.2, label=f"{name}: peak {r['peak']:.1f} C, {dh:.0f} K h")
        print(f"{name:44s} peak {r['peak']:.2f} C  mean {r['mean']:.2f} C  discomfort {dh:6.1f} K h  "
              f"energy residual {r['energy_residual'] / r['energy_scale']:.1e}  periodic error {r['periodic_error']:.1e} K")
    r0 = res[designs[0][0]]
    ax.plot(r0["hour"], r0["t_out"], "k--", lw=1.2, label="outdoor air")
    ax.axhspan(limit - 8.8, limit, color="#2a9d8f", alpha=0.08)
    ax.axhline(limit, color="#2a9d8f", lw=1, ls=":")
    ax.text(0.3, limit + 0.25, f"comfort upper limit with a fan {limit:.1f} C", fontsize=8, color="#2a9d8f")
    for x0, x1 in ((0, 7), (19, 24)):
        ax.axvspan(x0, x1, color="#264653", alpha=0.06)
    ax.set_xlim(0, 24)
    ax.set_xticks(range(0, 25, 3))
    ax.set_xlabel("solar time (h); shaded bands = night-flush hours")
    ax.set_ylabel("indoor air temperature (C)")
    ax.set_title("Top-floor room in Chennai on 15 April: shading and ventilation, hour by hour")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "day_designs.png", dpi=120)

    # Figure 2: where the heat comes from in the as-built room, and the role of thermal mass
    fig2, (axa, axb) = plt.subplots(1, 2, figsize=(10.5, 4.2))
    r = res[designs[0][0]]
    hv = RHO_CP * r["ach"] * 48.0 / 3600.0
    axa.plot(r["hour"], ROOM["ua_roof"] * (r["t_sa"] - r["t_air"]), color="#8d6e63", lw=2, label="through the roof")
    axa.plot(r["hour"], r["q_sun"], color="#e9a23b", lw=2, label="sun through the west window")
    axa.plot(r["hour"], (ROOM["ua_wall"] + hv) * (r["t_out"] - r["t_air"]), color="#264653", lw=2, label="walls, glass and air leaks")
    axa.axhline(ROOM["q_int"], color="#d9534f", lw=2, label="people and lamps")
    axa.axhline(0, color="k", lw=0.8)
    axa.set_xlim(0, 24)
    axa.set_xticks(range(0, 25, 3))
    axa.set_xlabel("solar time (h)")
    axa.set_ylabel("heat flow into the room (W)")
    axa.set_title("As built: the roof and the west sun dominate")
    axa.grid(alpha=0.3)
    axa.legend(fontsize=8)
    for cm, col in ((1.0e6, "#d9534f"), (6.0e6, "#2a9d8f"), (20.0e6, "#264653")):
        room = dict(ROOM, c_mass=cm)
        rr = simulate_day(0.6, 0.3, "night", room=room)
        axb.plot(rr["hour"], rr["t_air"], color=col, lw=2, label=f"C_m = {cm / 1e6:.0f} MJ/K: peak {rr['peak']:.1f} C")
        print(f"night flush design with C_m = {cm / 1e6:4.0f} MJ/K: peak {rr['peak']:.2f} C, swing {rr['t_air'].max() - rr['t_air'].min():.2f} K")
    axb.plot(r["hour"], r["t_out"], "k--", lw=1.2, label="outdoor air")
    axb.set_xlim(0, 24)
    axb.set_xticks(range(0, 25, 3))
    axb.set_xlabel("solar time (h)")
    axb.set_ylabel("indoor air temperature (C)")
    axb.set_title("Night flush works best with heavy mass")
    axb.grid(alpha=0.3)
    axb.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "heat_paths_mass.png", dpi=120)

    # sensitivity
    print("peak vs overhang depth (white roof, night flush):", [round(simulate_day(d, 0.3, "night")["peak"], 2) for d in (0.0, 0.3, 0.6, 0.9, 1.2)])
    print("peak vs roof absorptance (0.6 m, night flush):", [round(simulate_day(0.6, a, "night")["peak"], 2) for a in (0.2, 0.4, 0.6, 0.8)])
    print("peak vs open-window ACH (0.6 m, white roof, night):",
          [round(simulate_day(0.6, 0.3, "night", room=dict(ROOM, ach_open=x))["peak"], 2) for x in (5, 10, 20, 30)])
    print("time-step check (night design): 5 min", round(simulate_day(0.6, 0.3, "night")["peak"], 4),
          " 15 min", round(simulate_day(0.6, 0.3, "night", dt_min=15)["peak"], 4))

    # climate check: night flushing pays off when nights are much cooler than days
    for tm_, amp_ in ((31.0, 4.5), (28.0, 9.0)):
        pk = {s_: simulate_day(0.6, 0.3, s_, t_mean=tm_, t_amp=amp_)["peak"] for s_ in ("open", "night")}
        print(f"outdoor {tm_:.0f} +/- {amp_:.1f} C: peak with windows open all day {pk['open']:.2f} C, with night flush {pk['night']:.2f} C")

    # mini-project
    for target in (25.0, 20.0):
        print(f"cheapest design with at most {target:.0f} K h of discomfort:", choose_design(target, limit))

# %% [markdown]
# ## Where this stops
# The roof has no heat storage of its own, walls in the sun are treated as if in shade, the
# wind is steady, and comfort uses air temperature only. Each is a road to the Target: see
# the roadmap.
