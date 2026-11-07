"""Session 2 (Level 2): levelling books, slope distances, total-station coordinates, error growth.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the mathematics of levelling and of the total station
# **A. Real-world problem.** A real levelling run is written in a *levelling book*, a table of
# readings. A mistake in the table ruins every level after it, so surveyors use two methods and
# an arithmetic check. A *total station* adds the second half of surveying: it measures a slope
# distance and angles, and the computer turns them into easting and northing. Finally, how far
# apart should the staff positions be, so that small reading errors do not pile up over 1 km?
#
# **Plan.** (1) reduce a levelling book two ways, (2) the arithmetic check, (3) horizontal
# distance from a slope distance, (4) easting and northing from bearing and distance,
# (5) the square-root law for accumulated error.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# A levelling book: each row is (kind, reading in metres). BS = backsight, IS = intermediate
# sight, FS = foresight. A foresight followed by a backsight is the same point (a change point).
BOOK = [("BS", 1.425), ("IS", 1.870), ("IS", 2.315), ("FS", 2.905),
        ("BS", 1.150), ("IS", 0.980), ("FS", 0.640)]
RL_BM = 100.000   # reduced level of the first point (a benchmark)


# %% [markdown]
# ## Step 1: height of instrument (collimation) method
# At each set-up, the height of instrument is HI = RL of the backsight point + backsight.
# Every other point seen from that set-up has RL = HI - reading.

# %%
def hi_method(rows, rl0=RL_BM):
    """Reduced level for every row. Returns (rls, hi_values)."""
    rls, his, hi = [], [], None
    for kind, r in rows:
        if kind == "BS":
            rl = rl0 if not rls else rls[-1]     # first point, or the change point just left
            hi = rl + r
            his.append(hi)
        else:
            rl = hi - r
            his.append(None)
        rls.append(rl)
    return rls, his


# %% [markdown]
# ## Step 2: rise-and-fall method, and the arithmetic check
# Compare each reading with the one before it in the same set-up: rise = previous - current
# (positive is a rise, negative a fall), RL = previous RL + rise.
#
# **Arithmetic check:** sum of backsights - sum of foresights = last RL - first RL.
# Warning: the check only proves the arithmetic along the chain of backsights and foresights.
# It cannot find a wrong intermediate sight, because no later level uses it.

# %%
def rise_fall(rows, rl0=RL_BM):
    """Reduced level for every row by rise and fall. Returns (rls, rises); rises[0 or CP] is None."""
    rls, rises, prev = [], [], None
    for kind, r in rows:
        if kind == "BS":
            rl = rl0 if not rls else rls[-1]
            rises.append(None)
        else:
            rise = prev - r
            rl = rls[-1] + rise
            rises.append(rise)
        rls.append(rl)
        prev = r
    return rls, rises


def arithmetic_check(rows, rls):
    """Returns (sum_bs, sum_fs, last_rl - first_rl). The first two differ by the third if all is well."""
    sb = sum(r for k, r in rows if k == "BS")
    sf = sum(r for k, r in rows if k == "FS")
    return sb, sf, rls[-1] - rls[0]


# %% [markdown]
# ## Step 3: slope distance to horizontal distance
# A tape or total station measures along the slope: S. A map needs the horizontal distance.
# With elevation angle a (above horizontal): D = S cos(a) and height change V = S sin(a).

# %%
def horizontal_distance(S, a_deg):
    return S * np.cos(np.radians(a_deg))


def vertical_component(S, a_deg):
    return S * np.sin(np.radians(a_deg))


# %% [markdown]
# ## Step 4: easting and northing from bearing and distance
# A bearing is an angle measured clockwise from grid north. East is E, north is N:
#
#     E = E0 + D sin(bearing)        N = N0 + D cos(bearing)
#
# (sin goes with east because bearing 90 degrees points east.) The reverse problem, the
# *inverse*, gives bearing = atan2(dE, dN) and distance = sqrt(dE^2 + dN^2).

# %%
def total_station_point(E0, N0, rl0, ih, th, S, a_deg, bearing_deg):
    """One shot: station at (E0, N0, rl0), instrument height ih, prism height th, slope distance S,
    elevation angle a_deg, bearing bearing_deg. Returns dict with D, E, N and RL of the ground point."""
    D = float(horizontal_distance(S, a_deg))
    b = np.radians(bearing_deg)
    return {"D": D, "E": E0 + D * np.sin(b), "N": N0 + D * np.cos(b),
            "RL": rl0 + ih + float(vertical_component(S, a_deg)) - th}


def inverse(E1, N1, E2, N2):
    """Bearing (degrees, 0 to 360) and distance from point 1 to point 2."""
    dE, dN = E2 - E1, N2 - N1
    return float(np.degrees(np.arctan2(dE, dN)) % 360.0), float(np.hypot(dE, dN))


# %% [markdown]
# ## Step 5: the square-root law for levelling error
# Suppose each set-up adds an independent random error with standard deviation s (here 2 mm).
# After n set-ups the errors add like the sides of a random walk, not like a plain sum:
#
#     error(n) = s sqrt(n)
#
# For a line of length L with the staffs spaced d apart (one set-up per d), n = L / d.

# %%
def levelling_error(n, s):
    return s * np.sqrt(n)


def max_setups(s, limit):
    """Largest whole number of set-ups with s sqrt(n) strictly below limit."""
    n = int(np.floor((limit / s) ** 2))
    return n - 1 if abs(levelling_error(n, s) - limit) < 1e-12 else n


def min_spacing(total_length, s, limit):
    """Smallest staff spacing (same unit as total_length) that keeps the error below the limit."""
    return total_length / max_setups(s, limit)


def simulate_levelling(n, s, trials=20000, seed=1):
    """Monte Carlo: standard deviation of the accumulated error of n set-ups."""
    rng = np.random.default_rng(seed)
    return float(rng.normal(0.0, s, size=(trials, n)).sum(axis=1).std())


# %% [markdown]
# ## Step 6: see it
# Left: the error grows slowly (square root) while a one-sided systematic error would grow
# straight. Right: the slope distance versus the horizontal distance.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    rls_h, his = hi_method(BOOK)
    rls_r, rises = rise_fall(BOOK)
    for (k, r), a, b in zip(BOOK, rls_h, rls_r):
        print(f"{k}  {r:6.3f}   RL (HI) {a:8.3f}   RL (rise/fall) {b:8.3f}")
    sb, sf, dr = arithmetic_check(BOOK, rls_h)
    print(f"sum BS {sb:.3f} - sum FS {sf:.3f} = {sb - sf:.3f}; last RL - first RL = {dr:.3f}")

    p = total_station_point(1000.0, 5000.0, 50.0, 1.55, 1.80, 85.340, 7.5, 63.5)
    print("total station point:", {k: round(v, 3) for k, v in p.items()})

    n = np.arange(1, 61)
    fig, ax = plt.subplots(figsize=(6.4, 4))
    ax.plot(n, levelling_error(n, 2.0), label="random errors: 2 mm x sqrt(n)")
    ax.plot(n, 1.0 * n, label="systematic 1 mm per set-up: 1 mm x n")
    ax.axhline(10, color="red", ls="--", label="10 mm limit")
    ax.axvline(24, color="gray", ls=":")
    ax.set_xlabel("number of set-ups n")
    ax.set_ylabel("accumulated error (mm)")
    ax.set_title("Random error grows like sqrt(n): 24 set-ups give 9.8 mm")
    ax.set_ylim(0, 40)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "error_growth.png", dpi=120)

    a = np.linspace(-30, 30, 121)
    fig2, ax2 = plt.subplots(figsize=(6.4, 4))
    ax2.plot(a, horizontal_distance(100.0, a), label="horizontal D = S cos(a)")
    ax2.plot(a, vertical_component(100.0, a), label="vertical V = S sin(a)")
    ax2.axhline(100.0, color="gray", ls=":")
    ax2.set_xlabel("elevation angle a (degrees)")
    ax2.set_ylabel("distance for S = 100 m (m)")
    ax2.set_title("Slope distance 100 m split into D and V")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "slope_split.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
