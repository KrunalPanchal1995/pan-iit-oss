"""Session 1 (Level 1): a rain cell drifts with the wind - when will it reach us?

Educational only. This is NOT a weather warning system: always follow official forecasts.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a rain cell drifts with the wind
# **A. Real-world problem.** A weather radar sends out a picture of rain every 5 minutes.
# A rain cell (a blob of heavy rain) in one picture is in a new place in the next picture.
# If we measure how far it moved, we know the wind that is carrying it. Then we can say when
# it will reach a town in the next hour. This is called a *nowcast* (a forecast for the next
# hour or two). Safety note: this is a teaching model, not a warning system.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
PX_KM = 1.0          # one radar pixel is 1 km wide
DT_MIN = 5.0         # a new radar picture every 5 minutes
N = 100              # the picture is 100 x 100 pixels (100 km x 100 km)


# %% [markdown]
# ## Step 1: a radar picture is a grid of numbers
# Each pixel holds a rain rate in mm/h (millimetres of rain per hour). One rain cell is
# a smooth hill of rain: strongest at the centre, weaker outside. We model it as a Gaussian
# bell with width `sigma` (km) and centre rain rate `peak` (mm/h).

# %%
def gauss_cell(cx, cy, sigma, peak, n=N):
    """A rain cell centred at pixel (cx, cy). Returns an n x n array (rows = y, columns = x) in mm/h."""
    y, x = np.mgrid[0:n, 0:n]
    return peak * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * sigma ** 2))


def centroid(field):
    """Rain-weighted centre (cx, cy) of a picture, in pixels."""
    y, x = np.mgrid[0:field.shape[0], 0:field.shape[1]]
    total = field.sum()
    return float((field * x).sum() / total), float((field * y).sum() / total)


# %% [markdown]
# ## Step 2: how fast is the cell moving?
# Compare two pictures taken 5 minutes apart. If the centre moved `dx` pixels east and `dy`
# pixels north, then 1 pixel = 1 km and 5 minutes = 1/12 hour give
#     wind = pixels moved * 1 km / (1/12 h) = 12 * pixels moved   (km/h).

# %%
def wind_from_shift(dx_px, dy_px, px_km=PX_KM, dt_min=DT_MIN):
    """Wind components (u east, v north) in km/h, speed in km/h and direction in degrees (0 = east, 90 = north)."""
    hours = dt_min / 60.0
    u, v = dx_px * px_km / hours, dy_px * px_km / hours
    return u, v, float(np.hypot(u, v)), float(np.degrees(np.arctan2(v, u)))


# %% [markdown]
# ## Step 3: when will it reach the town?
# Assume the wind stays the same (the key assumption of this whole repo). The cell centre then
# moves in a straight line at constant speed. The closest the centre comes to the town, and
# when, follow from simple geometry. Rain at the town is the bell evaluated at the distance
# from the centre.

# %%
def cell_position(c0, wind, t_min):
    """Centre (x, y) in km after t_min minutes. c0 = (x, y) now, wind = (u, v) in km/h."""
    return c0[0] + wind[0] * t_min / 60.0, c0[1] + wind[1] * t_min / 60.0


def closest_approach(c0, wind, town):
    """(time in minutes, distance in km) of the closest approach of the cell centre to the town."""
    rx, ry = town[0] - c0[0], town[1] - c0[1]
    sp2 = wind[0] ** 2 + wind[1] ** 2
    if sp2 == 0:
        return float("inf"), float(np.hypot(rx, ry))
    t_h = max(0.0, (rx * wind[0] + ry * wind[1]) / sp2)      # no negative times: the cell moves forward only
    cx, cy = cell_position(c0, wind, t_h * 60.0)
    return t_h * 60.0, float(np.hypot(town[0] - cx, town[1] - cy))


def rain_at(point, centre, sigma, peak):
    """Rain rate (mm/h) at a point, from a Gaussian cell."""
    return peak * np.exp(-((point[0] - centre[0]) ** 2 + (point[1] - centre[1]) ** 2) / (2 * sigma ** 2))


def rain_edge_radius(sigma, peak, threshold):
    """Distance (km) from the centre at which the rain falls to `threshold` mm/h; 0 if the peak is below it."""
    return 0.0 if peak <= threshold else float(sigma * np.sqrt(2 * np.log(peak / threshold)))


def first_rain_time(c0, wind, town, sigma, peak, threshold):
    """First time (minutes) at which the town gets at least `threshold` mm/h, or None if it never does."""
    r = rain_edge_radius(sigma, peak, threshold)
    if r == 0.0:
        return None
    ax, ay = c0[0] - town[0], c0[1] - town[1]
    a = (wind[0] ** 2 + wind[1] ** 2) / 3600.0                 # per minute squared
    b = 2 * (ax * wind[0] + ay * wind[1]) / 60.0
    c = ax ** 2 + ay ** 2 - r ** 2
    if c <= 0:
        return 0.0                                             # already raining at the town
    if a == 0:
        return None
    disc = b * b - 4 * a * c
    if disc < 0:
        return None                                            # the edge of the cell never reaches the town
    t = (-b - np.sqrt(disc)) / (2 * a)
    return float(t) if t >= 0 else None


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    c0, sigma, peak, thr = (20.0, 50.0), 6.0, 40.0, 5.0
    town = (56.0, 50.0)
    u, v, sp, ang = wind_from_shift(3, 0)
    print(f"cell moved 3 px in 5 min -> wind {u:.0f} km/h east (speed {sp:.0f} km/h, direction {ang:.0f} deg)")
    t_c, miss = closest_approach(c0, (u, v), town)
    print(f"centre is closest at {t_c:.0f} min, miss distance {miss:.1f} km")
    print(f"first rain >= {thr:.0f} mm/h at the town after {first_rain_time(c0, (u, v), town, sigma, peak, thr):.1f} min")
    tilt = np.radians(20)
    w2 = (sp * np.cos(tilt), sp * np.sin(tilt))
    t2, miss2 = closest_approach(c0, w2, town)
    print(f"wind turned by 20 deg: closest at {t2:.1f} min, miss {miss2:.1f} km, "
          f"peak rain at town {rain_at(town, cell_position(c0, w2, t2), sigma, peak):.2f} mm/h")

    fig, axs = plt.subplots(1, 4, figsize=(11, 3.2))
    for ax, t in zip(axs, (0, 20, 40, 60)):
        cx, cy = cell_position(c0, (u, v), t)
        ax.imshow(gauss_cell(cx, cy, sigma, peak), origin="lower", cmap="Blues", vmin=0, vmax=40)
        ax.plot(*town, "r*", ms=12)
        ax.set_title(f"t = +{t} min")
        ax.set_xlabel("x (km)")
    axs[0].set_ylabel("y (km)")
    fig.suptitle("A rain cell drifts east at 36 km/h; red star = town")
    fig.tight_layout()
    fig.savefig(OUT / "drifting_cell.png", dpi=110)

    ts = np.linspace(0, 120, 241)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for wind, lab in (((u, v), "wind straight at the town"), (w2, "wind turned by 20 degrees")):
        ax2.plot(ts, [rain_at(town, cell_position(c0, wind, t), sigma, peak) for t in ts], label=lab)
    ax2.axhline(thr, color="gray", ls=":")
    ax2.set_xlabel("time from now (min)")
    ax2.set_ylabel("rain rate at the town (mm/h)")
    ax2.set_title("Forecast rain at the town")
    ax2.legend()
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "rain_at_town.png", dpi=120)

# %% [markdown]
# ## Try it
# Do the coding tasks, the README questions (F), then the checkpoint.
