"""Session 3 (Level 3): a whole year, hour by hour: daylight, heat and the best window.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: simulate a year of daylight and heat, validate it, choose the window
# **A. Real-world problem.** A bigger window gives more daylight, so the lights stay off longer,
# but it also lets in more solar heat that the air conditioner must remove. Somewhere between a
# slit and a glass wall is the window size that uses the least electricity in a year. Can we
# simulate a study room in Chennai hour by hour for a whole year, check the simulation, and
# choose the window size, the orientation and the overhang?
#
# **Plan.** (1) check the overhang formula with an independent 3D ray test, (2) the average
# daylight factor, (3) an hour-by-hour simulation of one year (daylight, lights, solar heat,
# cooling), (4) validation, (5) the best window-to-wall ratio for each orientation,
# (6) a failure case: a west window without shading.
#
# **Model.** Clear sky every day (no monsoon clouds), solar time, a room 4 m wide, 5 m deep
# and 3 m high with one window wall. Illustrative values for glass, lights and air conditioner.
# A simplified teaching model, not a design tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
TILT, SOLAR_CONST, DIFFUSE_C = 23.45, 1353.0, 0.10


def declination(n):
    """Solar declination (degrees), Cooper's formula (Session 1)."""
    return TILT * np.sin(np.radians(360.0 * (284.0 + np.asarray(n, float)) / 365.0))


def sun_vector(lat, decl, hour):
    """Unit vector towards the sun as (east, north, up) components (Session 1)."""
    phi, d = np.radians(lat), np.radians(decl)
    h = np.radians(15.0 * (np.asarray(hour, float) - 12.0))
    up = np.sin(d) * np.sin(phi) + np.cos(d) * np.cos(phi) * np.cos(h)
    east = -np.cos(d) * np.sin(h)
    north = np.sin(d) * np.cos(phi) - np.cos(d) * np.sin(phi) * np.cos(h)
    return east, north, up


def sun_position(lat, decl, hour):
    """(altitude, azimuth) in degrees, azimuth clockwise from north (Session 1)."""
    e, n, u = sun_vector(lat, decl, hour)
    return np.degrees(np.arcsin(np.clip(u, -1, 1))), np.degrees(np.arctan2(e, n)) % 360.0


def dni(alt):
    """Clear-sky direct normal irradiance (W/m2), Meinel model (Session 2)."""
    alt = np.asarray(alt, float)
    s = np.sin(np.radians(np.maximum(alt, 1e-6)))
    return np.where(alt > 0, SOLAR_CONST * 0.7 ** ((1.0 / s) ** 0.678), 0.0)


def sunlit_fraction(alt, az, facing, depth, height, gap=0.0):
    """Share of the window height in direct sun below an overhang (Session 2 formula)."""
    g = np.radians((np.asarray(az, float) - facing + 180.0) % 360.0 - 180.0)
    c = np.cos(g)
    front = (np.asarray(alt) > 0) & (c > 1e-9)
    tan_vsa = np.tan(np.radians(np.clip(alt, 0, 89.999))) / np.where(front, c, 1.0)
    shaded = np.clip(depth * tan_vsa - gap, 0.0, height)
    return np.where(front, 1.0 - shaded / height, 0.0)


# %% [markdown]
# ## Step 1: check the overhang formula with a 3D ray test
# Session 2 used the vertical shadow angle. Here we test it without using that angle at all.
# Take 2000 points up the window. From each point, follow a straight ray towards the sun in 3D:
# the sun vector s has an up part s_up and an outward part s_out = s . (wall normal). The ray
# rises by d (to the overhang height) after travelling d x s_out / s_up away from the wall.
# If that is less than the overhang depth, the ray hits the overhang and the point is in shade.

# %%
def sunlit_fraction_raytrace(lat, decl, hour, facing, depth, height, gap=0.0, n=2000):
    """Independent check: share of points up the window whose ray to the sun misses the overhang."""
    e, nn, u = sun_vector(lat, decl, hour)
    out = e * np.sin(np.radians(facing)) + nn * np.cos(np.radians(facing))
    if u <= 0 or out <= 0:
        return 0.0
    z = (np.arange(n) + 0.5) / n * height                 # height of each point above the sill (m)
    rise = gap + (height - z)                             # how far the ray must rise to reach the overhang
    reach = rise * out / u                                # distance from the wall at that height (m)
    return float(np.mean(reach >= depth))


# %% [markdown]
# ## Step 2: how much daylight reaches the room? The average daylight factor
# The **daylight factor** DF is the indoor illuminance as a percentage of the outdoor
# illuminance under an unobstructed sky. The average daylight factor formula (Littlefair, BRE)
# is
#
#     DF = T Aw theta / ( A (1 - R**2) )      (percent)
#
# T = visible transmittance of the glass, Aw = glass area (m2), theta = visible sky angle in
# degrees (90 for an open window wall), A = area of all room surfaces (floor, ceiling, walls,
# windows) and R = their average reflectance. An overhang hides part of the sky: seen from the
# window centre the sky starts above the angle atan((gap + H/2) / depth) from horizontal.

# %%
ROOM_W, ROOM_D, ROOM_H = 4.0, 5.0, 3.0            # facade width, depth, height (m)
WIN_H, SILL = 1.5, 0.9                            # window height and sill height (m)
A_TOTAL = 2 * (ROOM_W * ROOM_D + ROOM_W * ROOM_H + ROOM_D * ROOM_H)   # 94 m2
T_VIS, R_MEAN, SHGC = 0.7, 0.5, 0.6
LUX_PER_W = 120.0      # luminous efficacy of diffuse daylight (lm/W)
E_TARGET = 300.0       # lux on the desk for study (a typical recommended value)
LPD = 8.0              # lighting power density (W/m2 of floor)
U_GLASS, U_WALL, DT_MEAN = 5.8, 2.0, 4.0           # W/(m2 K), W/(m2 K), K (outdoor mean - indoor)
COP = 3.0              # air conditioner: heat removed per unit of electricity
OCC = (9.0, 17.0)      # occupied hours, solar time


def visible_sky_angle(depth, gap=0.3, height=WIN_H):
    """Visible sky angle theta (degrees) at the window centre below an overhang."""
    if depth <= 0:
        return 90.0
    return float(np.degrees(np.arctan((gap + height / 2.0) / depth)))


def average_daylight_factor(glass_area, theta=90.0, t_vis=T_VIS, a_total=A_TOTAL, refl=R_MEAN):
    """Average daylight factor (percent), Littlefair formula."""
    if glass_area < 0 or not (0 <= refl < 1):
        raise ValueError("need glass_area >= 0 and 0 <= R < 1")
    return t_vis * glass_area * theta / (a_total * (1.0 - refl ** 2))


# %% [markdown]
# ## Step 3: one year, hour by hour
# For every time step of every day of the year:
#
# * **sun**: altitude and azimuth (Session 1), DNI (Session 2)
# * **solar heat in** = SHGC x Aw x [DNI cos(theta_i) x sunlit + 0.05 DNI]   (W)
# * **daylight indoors** = DF / 100 x outdoor diffuse illuminance, with the outdoor diffuse
#   illuminance = 120 lm/W x 0.1 DNI   (lux)
# * **lights** (only 9:00 to 17:00): dimmed to top up the daylight to 300 lux:
#   P = LPD x floor area x max(0, 1 - E_in / 300)
#
# The air conditioner runs only while the room is used (9:00 to 17:00); heat that enters at
# other hours is assumed to leave by ventilation at night. Over the year we add up:
#
#     cooling heat = [solar heat + window conduction (U_glass - U_wall) Aw dT + lights] in use hours
#     electricity  = lights + cooling heat / COP
#
# The window is 1.5 m tall and as wide as needed for a chosen **window-to-wall ratio** WWR
# (glass area / 12 m2 of facade): width = WWR x 12 / 1.5, so WWR 0.25 is 2 m wide.

# %%
def simulate_year(lat, facing, wwr, depth=0.0, gap=0.3, shgc=SHGC, step=0.25, days=None):
    """Hour-by-hour year of a one-window room. Returns a dict of yearly totals (kWh) and monthly solar."""
    if not (0 < wwr <= ROOM_W * WIN_H / (ROOM_W * ROOM_H)):
        raise ValueError("need 0 < WWR <= 0.5 for a 1.5 m tall window in a 4 m x 3 m wall")
    area = wwr * ROOM_W * ROOM_H
    df = average_daylight_factor(area, visible_sky_angle(depth, gap))
    days = np.arange(1, 366) if days is None else np.asarray(days)
    hours = np.arange(step / 2.0, 24.0, step)
    nn, hh = np.meshgrid(days, hours, indexing="ij")
    alt, az = sun_position(lat, declination(nn), hh)
    beam = dni(alt)
    g = np.radians((az - facing + 180.0) % 360.0 - 180.0)
    cos_i = np.where(alt > 0, np.maximum(np.cos(np.radians(alt)) * np.cos(g), 0.0), 0.0)
    lit = sunlit_fraction(alt, az, facing, depth, WIN_H, gap)
    q_solar = shgc * area * (beam * cos_i * lit + 0.5 * DIFFUSE_C * beam)          # W
    e_in = df / 100.0 * LUX_PER_W * DIFFUSE_C * beam                                 # lux
    occ = (hh >= OCC[0]) & (hh < OCC[1])
    p_light = np.where(occ, LPD * ROOM_W * ROOM_D * np.clip(1.0 - e_in / E_TARGET, 0.0, 1.0), 0.0)
    q_cond = (U_GLASS - U_WALL) * area * DT_MEAN * np.ones_like(hh)
    to_kwh = step / 1000.0
    solar = float((q_solar * occ).sum() * to_kwh)
    light = float(p_light.sum() * to_kwh)
    cond = float((q_cond * occ).sum() * to_kwh)
    cooling = (solar + cond + light) / COP
    month = np.minimum((days - 1) * 12 // 365, 11)
    monthly = np.array([q_solar[month == m].sum() * to_kwh for m in range(12)])
    return {"area": area, "df": df, "solar_kwh": solar, "solar_all_kwh": float(q_solar.sum() * to_kwh), "cond_kwh": cond, "light_kwh": light,
            "cool_kwh": cooling, "total_kwh": light + cooling, "monthly_solar": monthly,
            "daylit_hours": float((occ & (e_in >= E_TARGET)).sum() * step)}


def best_wwr(lat, facing, depth=0.0, gap=0.3, wwrs=None):
    """(best WWR, its total kWh, all totals) from a sweep of window-to-wall ratios."""
    wwrs = np.round(np.arange(0.05, 0.501, 0.05), 2) if wwrs is None else np.asarray(wwrs)
    tot = np.array([simulate_year(lat, facing, w, depth, gap)["total_kwh"] for w in wwrs])
    k = int(np.argmin(tot))
    return float(wwrs[k]), float(tot[k]), tot


def plan_window(lat, facings=(0, 90, 180, 270), depths=(0.0, 0.3, 0.6, 0.9), min_df=2.0):
    """Search orientation, overhang depth and WWR for the lowest yearly electricity with an
    average daylight factor of at least `min_df` percent. Returns (facing, depth, wwr, total kWh)."""
    wwrs = np.round(np.arange(0.05, 0.501, 0.05), 2)
    best = None
    for f in facings:
        for d in depths:
            for w in wwrs:
                r = simulate_year(lat, f, float(w), d)
                if r["df"] >= min_df and (best is None or r["total_kwh"] < best[3] - 1e-9):
                    best = (f, d, float(w), r["total_kwh"])
    return best


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    CHENNAI = 13.0

    # validation 1: ray test against the formula
    for n, hr, f in ((355, 12.0, 180), (172, 15.0, 270), (80, 9.0, 90), (300, 10.5, 150)):
        d = float(declination(n))
        a, z = sun_position(CHENNAI, d, hr)
        print(f"n {n}, {hr} h, facing {f}: formula {float(sunlit_fraction(a, z, f, 0.6, 1.5, 0.3)):.4f}, "
              f"ray test {sunlit_fraction_raytrace(CHENNAI, d, hr, f, 0.6, 1.5, 0.3):.4f}")

    # worked example: south, WWR 0.25, 0.6 m overhang
    r = simulate_year(CHENNAI, 180, 0.25, 0.6)
    print(f"south WWR 0.25 overhang 0.6 m: DF {r['df']:.2f}%, solar {r['solar_kwh']:.0f}, cond {r['cond_kwh']:.0f}, "
          f"lights {r['light_kwh']:.0f}, cooling elec {r['cool_kwh']:.0f}, total {r['total_kwh']:.0f} kWh/yr")

    # Figure 1: the energy balance against window size (south, 0.6 m overhang)
    wwrs = np.round(np.arange(0.05, 0.501, 0.05), 2)
    res = [simulate_year(CHENNAI, 180, w, 0.6) for w in wwrs]
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    ax.plot(wwrs, [x["light_kwh"] for x in res], "o-", color="#e9a23b", label="lights")
    ax.plot(wwrs, [x["cool_kwh"] for x in res], "o-", color="#4ea8de", label="cooling (solar + conduction + lights) / COP")
    ax.plot(wwrs, [x["total_kwh"] for x in res], "o-", color="#264653", lw=2.5, label="total electricity")
    k = int(np.argmin([x["total_kwh"] for x in res]))
    ax.plot(wwrs[k], res[k]["total_kwh"], "*", color="#d9534f", ms=16, label=f"best WWR {wwrs[k]:.2f}")
    ax.set_xlabel("window-to-wall ratio WWR (no unit)")
    ax.set_ylabel("electricity per year (kWh)")
    ax.set_title("Chennai study room, south window, 0.6 m overhang")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "energy_vs_wwr.png", dpi=120)
    for x, w in zip(res, wwrs):
        print(f"WWR {w:.2f}: DF {x['df']:.2f}%  lights {x['light_kwh']:6.1f}  cooling {x['cool_kwh']:6.1f}  total {x['total_kwh']:6.1f}")

    # Figure 2: orientation and overhang, best WWR and its total
    faces = [("N", 0), ("E", 90), ("S", 180), ("W", 270)]
    fig2, ax2 = plt.subplots(figsize=(6.6, 4.2))
    x = np.arange(4)
    for j, (dep, col) in enumerate(((0.0, "#d9534f"), (0.6, "#2a9d8f"))):
        tots, bests = [], []
        for name, f in faces:
            bw, bt, _ = best_wwr(CHENNAI, f, dep)
            tots.append(bt)
            bests.append(bw)
            print(f"facing {name}, overhang {dep} m: best WWR {bw:.2f}, total {bt:.1f} kWh/yr")
        ax2.bar(x + (j - 0.5) * 0.36, tots, 0.36, color=col, label=f"overhang {dep} m")
        for xi, t, b in zip(x, tots, bests):
            ax2.text(xi + (j - 0.5) * 0.36, t + 4, f"{b:.2f}", ha="center", fontsize=8)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{n}-facing" for n, _ in faces])
    ax2.set_ylabel("lowest electricity per year (kWh)")
    ax2.set_title("Best window per orientation (number = best WWR)")
    ax2.set_ylim(0, None)
    ax2.legend(fontsize=8, loc="lower right")
    ax2.grid(alpha=0.3, axis="y")
    fig2.tight_layout()
    fig2.savefig(OUT / "best_by_orientation.png", dpi=120)

    # Figure 3: the window planner (sun path + shading mask, monthly solar heat)
    fig3, (p1, p2) = plt.subplots(1, 2, figsize=(11, 4.3))
    for n, col, lab in ((172, "#d9534f", "21 June"), (81, "#e9a23b", "22 March"), (355, "#2a9d8f", "21 December")):
        hrs = np.linspace(5, 19, 400)
        a, z = sun_position(CHENNAI, declination(n), hrs)
        a = np.where(a > 0, a, np.nan)
        z = np.where(np.abs(np.diff(z, prepend=z[0])) > 180, np.nan, z)    # break the line where it wraps past north
        p1.plot(z, a, color=col, label=lab)
    az_grid = np.linspace(90, 270, 181)
    tan_cut = (0.3 + 1.5) / 0.6                     # full shade when tan(VSA) >= (gap + H) / depth
    alt_cut = np.degrees(np.arctan(tan_cut * np.cos(np.radians(az_grid - 180))))
    p1.fill_between(az_grid, alt_cut, 90, color="#555", alpha=0.18, label="0.6 m overhang: window fully shaded")
    p1.axvspan(0, 90, color="#555", alpha=0.08)
    p1.axvspan(270, 360, color="#555", alpha=0.08, label="sun behind the wall")
    p1.set_xlim(0, 360)
    p1.set_ylim(0, 90)
    p1.set_xticks([0, 45, 90, 135, 180, 225, 270, 315, 360])
    p1.set_xticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"])
    p1.set_xlabel("sun azimuth")
    p1.set_ylabel("sun altitude (degrees)")
    p1.set_title("Chennai sun path and the shading mask of a south window")
    p1.legend(fontsize=7, loc="upper left")
    p1.grid(alpha=0.3)
    months = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    for f, col, lab in ((180, "#2a9d8f", "south"), (270, "#d9534f", "west"), (0, "#264653", "north")):
        for dep, ls in ((0.0, "--"), (0.6, "-")):
            ms = simulate_year(CHENNAI, f, 0.25, dep)["monthly_solar"]
            p2.plot(range(12), ms, ls, color=col, label=f"{lab}, overhang {dep} m")
    p2.set_xticks(range(12))
    p2.set_xticklabels(months)
    p2.set_ylabel("solar heat through the window (kWh per month)")
    p2.set_title("2 m x 1.5 m window (WWR 0.25)")
    p2.legend(fontsize=7, ncol=2)
    p2.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "window_planner.png", dpi=120)

    # failure case: an unshaded west window that is too big
    w_big = simulate_year(CHENNAI, 270, 0.5, 0.0)
    s_best = simulate_year(CHENNAI, 180, 0.25, 0.6)
    print(f"failure case, west WWR 0.5 no overhang: total {w_big['total_kwh']:.0f} kWh/yr against {s_best['total_kwh']:.0f} for the planned south window")
    print("convergence (south, 0.25, 0.6 m), step 0.25 h vs 0.05 h:",
          round(r["total_kwh"], 2), round(simulate_year(CHENNAI, 180, 0.25, 0.6, step=0.05)["total_kwh"], 2))

# %% [markdown]
# ## Where this stops
# Real skies have clouds and monsoon months, the daylight is not the same everywhere in the
# room, and the room's walls store heat. The roadmap (Session 4 and up) adds weather data,
# a point-by-point daylight map, glare and side fins.
