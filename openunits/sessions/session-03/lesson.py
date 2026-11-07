"""Session 3 (Level 3): a units-checked wrapper and a toy trajectory-correction simulation.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: catch the Mars Climate Orbiter bug before it flies
# **A. Real-world problem.** In 1999 NASA's Mars Climate Orbiter was lost at Mars. The
# investigation found that thruster impulse data were produced in pound-force seconds (lbf*s)
# while the navigation software expected newton seconds (N*s). One lbf*s is about 4.45 N*s, so
# the effect of the small thruster firings was misjudged by that factor and the spacecraft
# came in lower than planned.
#
# Today you (1) build a tiny units-checked wrapper in plain numpy that refuses bare numbers and
# mismatched dimensions, (2) simulate a **toy** trajectory correction to see how a factor of
# 4.45 grows into a miss distance, and (3) compare the simulation with a formula.
# The spacecraft numbers below are illustrative, NOT mission data.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
LBF_S_TO_NS = 4.448222        # newton seconds in one pound-force second
DAY = 86400.0                 # seconds in a day


# %% [markdown]
# ## Step 1: a quantity that remembers its dimension
# We store the value in SI units and the dimension as a vector of exponents [M, L, T]
# (Session 2). Adding quantities of different dimension raises an error. Note the limit:
# lbf*s and N*s have the SAME dimension, so the check cannot catch a lbf*s number read as N*s.
# What catches it is that a `Quantity` never exists without its unit, and converts itself.

# %%
UNITS = {      # unit: (size in SI, dimension [M, L, T])
    "kg": (1.0, (1, 0, 0)), "g": (1e-3, (1, 0, 0)), "lb": (0.45359237, (1, 0, 0)),
    "m": (1.0, (0, 1, 0)), "km": (1000.0, (0, 1, 0)), "ft": (0.3048, (0, 1, 0)),
    "s": (1.0, (0, 0, 1)), "h": (3600.0, (0, 0, 1)), "day": (DAY, (0, 0, 1)),
    "m/s": (1.0, (0, 1, -1)), "km/h": (1000.0 / 3600.0, (0, 1, -1)), "ft/s": (0.3048, (0, 1, -1)),
    "N": (1.0, (1, 1, -2)), "lbf": (4.4482216152605, (1, 1, -2)),
    "N*s": (1.0, (1, 1, -1)), "lbf*s": (4.4482216152605, (1, 1, -1)),
}


class DimensionError(Exception):
    """Raised when quantities with different dimensions are combined or compared."""


class Quantity:
    def __init__(self, value, unit):
        if unit not in UNITS:
            raise DimensionError(f"unknown unit {unit!r}")
        size, d = UNITS[unit]
        self.si = float(value) * size
        self.dim = np.array(d, dtype=int)

    @classmethod
    def _raw(cls, si, dim):
        q = cls.__new__(cls)
        q.si, q.dim = float(si), np.array(dim, dtype=int)
        return q

    def _need_same(self, other, op):
        if not isinstance(other, Quantity):
            raise DimensionError(f"cannot {op} a bare number and a quantity: attach a unit")
        if not np.array_equal(self.dim, other.dim):
            raise DimensionError(f"cannot {op} dimensions {self.dim.tolist()} and {other.dim.tolist()}")

    def __add__(self, other):
        self._need_same(other, "add")
        return Quantity._raw(self.si + other.si, self.dim)

    def __sub__(self, other):
        self._need_same(other, "subtract")
        return Quantity._raw(self.si - other.si, self.dim)

    def __mul__(self, other):
        if isinstance(other, Quantity):
            return Quantity._raw(self.si * other.si, self.dim + other.dim)
        return Quantity._raw(self.si * other, self.dim)        # a bare number is a pure scale factor

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Quantity):
            return Quantity._raw(self.si / other.si, self.dim - other.dim)
        return Quantity._raw(self.si / other, self.dim)

    def __pow__(self, n):
        return Quantity._raw(self.si ** n, self.dim * n)

    def to(self, unit):
        """The number that goes in front of `unit`. Raises if the dimension is wrong."""
        size, d = UNITS[unit]
        if not np.array_equal(self.dim, np.array(d)):
            raise DimensionError(f"{self.dim.tolist()} is not convertible to {unit} {list(d)}")
        return self.si / size

    def __repr__(self):
        return f"Quantity({self.si:.6g} SI, dim [M, L, T] = {self.dim.tolist()})"


def require(q, unit):
    """The gate at a software boundary: accept only a Quantity of the right dimension, return its number."""
    if not isinstance(q, Quantity):
        raise DimensionError("a bare number is not an answer: it has no unit")
    return q.to(unit)


# %% [markdown]
# ## Step 2: a toy trajectory correction
# A spacecraft of mass m makes n small thruster firings. Each firing gives a sideways velocity
# change dv = impulse / m. The ground file lists each impulse as a number in lbf*s. Navigators
# use it to predict the path. If the number is read as N*s, the predicted push is too small by
# the factor 4.448222, and the real path drifts away from the predicted one.
# Sideways offset y after time t:  y = sum over firings of dv * (t - t_k).

# %%
MASS = 600.0                           # kg, an illustrative value
T_END = 180 * DAY                      # toy cruise duration, seconds


def firing_times(n, first_day=10, last_day=150):
    """n evenly spaced firing times in seconds (whole days)."""
    if n == 1:
        return np.array([first_day * DAY])
    return np.floor(np.linspace(first_day, last_day, n) + 0.5) * DAY


def offset_analytic(t, dv, times):
    """Sideways offset (m) at times t from firings dv (m/s) made at `times` (s). Pure formula."""
    t = np.atleast_1d(np.asarray(t, dtype=float))
    out = np.zeros_like(t)
    for tk in times:
        out += dv * np.clip(t - tk, 0.0, None)
    return out


def offset_simulated(dv, times, t_end=T_END, dt=3600.0):
    """Step the sideways motion hour by hour: apply each kick, then move. Returns (t, y)."""
    n = int(round(t_end / dt))
    t = np.arange(n + 1) * dt
    kick_steps = [int(round(tk / dt)) for tk in times]
    y = np.zeros(n + 1)
    v = 0.0
    for i in range(n):
        v += dv * kick_steps.count(i)
        y[i + 1] = y[i] + v * dt
    return t, y


def dv_from_file(number, factor, mass=MASS):
    """Velocity change (m/s) for a file number when the reader uses `factor` newton seconds per unit."""
    return number * factor / mass


def miss_distance(number, n, mass=MASS, factor_used=1.0, factor_true=LBF_S_TO_NS):
    """Gap (m) at the end between the real path and the predicted path.

    factor_used = 1 reads lbf*s as N*s (the bug); factor_true is the right conversion.
    """
    times = firing_times(n)
    real = offset_analytic(T_END, dv_from_file(number, factor_true, mass), times)[0]
    predicted = offset_analytic(T_END, dv_from_file(number, factor_used, mass), times)[0]
    return float(real - predicted)


# %% [markdown]
# ## Step 3: the audit helper (the wrapper at work)
# The same calculation, written with `Quantity`, cannot confuse the units.

# %%
def delta_v(impulse, mass):
    """Velocity change from an impulse and a mass, both Quantities. Returns a Quantity."""
    return impulse / mass


def total_miss(impulse_per_firing, n, mass):
    """Miss distance as a Quantity (metres) if the unit is dropped, for n firings of the given impulse."""
    times = firing_times(n)
    dv = require(delta_v(impulse_per_firing, mass), "m/s")
    dv_bug = dv / LBF_S_TO_NS               # what a reader sees when the unit is dropped
    real = offset_analytic(T_END, dv, times)[0]
    wrong = offset_analytic(T_END, dv_bug, times)[0]
    return Quantity(real - wrong, "m")


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    n, number = 12, 0.2
    times = firing_times(n)
    dv_true = dv_from_file(number, LBF_S_TO_NS)
    dv_bug = dv_from_file(number, 1.0)
    t_sim, y_true_sim = offset_simulated(dv_true, times)
    _, y_bug_sim = offset_simulated(dv_bug, times)
    y_true_f = offset_analytic(t_sim, dv_true, times)
    print(f"firings: {n} x {number} lbf*s, mass {MASS:g} kg, cruise {T_END / DAY:g} days (toy numbers)")
    print(f"real sideways offset at the end      {y_true_sim[-1] / 1000:9.2f} km (simulation)")
    print(f"predicted (lbf*s read as N*s)        {y_bug_sim[-1] / 1000:9.2f} km (simulation)")
    print(f"miss distance                        {(y_true_sim[-1] - y_bug_sim[-1]) / 1000:9.2f} km")
    print(f"formula miss_distance()              {miss_distance(number, n) / 1000:9.2f} km")
    print(f"largest gap simulation - formula     {np.abs(y_true_sim - y_true_f).max():9.4f} m")
    print(f"ratio real / predicted               {y_true_sim[-1] / y_bug_sim[-1]:9.4f}")
    q = total_miss(Quantity(number, "lbf*s"), n, Quantity(MASS, "kg"))
    print(f"wrapper: miss = {q.to('km'):.2f} km")
    for label, thing in (("bare number", lambda: require(0.2, "N*s")),
                         ("force + impulse", lambda: Quantity(5, "N") + Quantity(5, "N*s"))):
        try:
            thing()
        except DimensionError as err:
            print(f"caught {label}: {err}")

    days = t_sim / DAY
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(days, y_bug_sim / 1000, label="predicted path (lbf*s read as N*s)")
    ax.plot(days, y_true_sim / 1000, label="actual path (correct conversion)")
    ax.plot(days, y_true_f / 1000, "k:", label="formula for the actual path")
    ax.fill_between(days, y_bug_sim / 1000, y_true_sim / 1000, alpha=0.2, color="#d9534f", label="miss")
    ax.set_xlabel("time since start of cruise (days)")
    ax.set_ylabel("sideways offset (km)")
    ax.set_title("Toy model: the unit mistake grows into a miss")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "toy_trajectory.png", dpi=120)

    ns = np.arange(1, 21)
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.plot(ns, [miss_distance(number, k) / 1000 for k in ns], "o-", label="miss, mass 600 kg")
    ax2.plot(ns, [miss_distance(number, k, mass=1200.0) / 1000 for k in ns], "s--", label="miss, mass 1200 kg")
    ax2.set_xlabel("number of firings")
    ax2.set_ylabel("miss distance (km)")
    ax2.set_title("Miss grows with the number of firings and shrinks with mass")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "miss_sensitivity.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Where this stops
# A real navigation team models gravity of the Sun and planets, thruster directions and
# measurements of the spacecraft's position. This toy has straight-line drift only. It shows
# the scaling, not the mission.
