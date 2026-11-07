"""Session 2 (Level 2): the single-storey model, resonance and a stiffness design problem.

Educational model only. Never use it for real seismic design.
Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: one storey, shaken at the base
# **A. Real-world problem.** A one-storey building has a roof mass m on columns of total
# sideways stiffness k. The ground moves with acceleration a_g(t). Typical dominant ground
# shaking in a soft-soil city is around 1 s per cycle. How big does the sway get, and how stiff
# must the columns be so that the building is not at the mercy of that rhythm?
#
# **Plan.** (1) equation of motion and natural period, (2) the amplification factor,
# (3) check it against a step-by-step numerical solution, (4) solve a design problem.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
ZETA = 0.05          # typical damping ratio of a building (about 5 percent of critical)


# %% [markdown]
# ## Step 1: equation of motion
# Let u be the roof displacement *relative to the ground*. Newton's law on the roof gives
#
#     m u'' + c u' + k u = -m a_g(t)
#
# Divide by m, with w = sqrt(k/m) and damping ratio zeta = c / (2 m w):
#
#     u'' + 2 zeta w u' + w^2 u = -a_g(t)
#
# Period T = 2 pi / w. For N storeys of a typical frame building a rough *empirical* guide is
# T about 0.1 N seconds (not a law).

# %%
def omega(k, m):
    """Natural angular frequency w = sqrt(k / m) in rad/s."""
    return float(np.sqrt(k / m))


def period(k, m):
    """Natural period T = 2 pi / w in seconds."""
    return float(2 * np.pi / omega(k, m))


def rule_of_thumb_period(storeys):
    """T = 0.1 N seconds: rough empirical guide for typical frame buildings."""
    return 0.1 * storeys


# %% [markdown]
# ## Step 2: harmonic ground motion and the amplification factor
# Let the ground accelerate as a_g = a0 sin(W t) with forcing frequency W, and let r = W / w be
# the *frequency ratio*. After the start-up transient dies, the building sways with amplitude
#
#     u_max = (a0 / w^2) D(r),     D(r) = 1 / sqrt((1 - r^2)^2 + (2 zeta r)^2)
#
# a0 / w^2 is the sway if the acceleration were applied as a constant push. D is the
# *amplification factor*. Its maximum is near r = 1 and equals about 1 / (2 zeta).

# %%
def amplification(r, zeta=ZETA):
    """D(r), the dynamic amplification factor (no unit)."""
    r = np.asarray(r, float)
    return 1.0 / np.sqrt((1 - r ** 2) ** 2 + (2 * zeta * r) ** 2)


def peak_amplification(zeta=ZETA):
    """Exact maximum of D (at r = sqrt(1 - 2 zeta^2), needs zeta < 0.7071) and where it occurs."""
    r = np.sqrt(1 - 2 * zeta ** 2)
    return float(amplification(r, zeta)), float(r)


def sway_amplitude(a0, k, m, t_ground, zeta=ZETA):
    """Steady sway amplitude (m) of the roof relative to the ground for ground acceleration amplitude a0 (m/s^2)."""
    w = omega(k, m)
    r = (2 * np.pi / t_ground) / w
    return float(a0 / w ** 2 * amplification(r, zeta))


# %% [markdown]
# ## Step 3: check it by brute force
# Step u'' + 2 zeta w u' + w^2 u = -a0 sin(W t) forward with the 4th-order Runge-Kutta
# method until the transient has died, then read off the amplitude. It should match the formula.

# %%
def sway_amplitude_numeric(a0, k, m, t_ground, zeta=ZETA, steps_per_period=200):
    w = omega(k, m)
    W = 2 * np.pi / t_ground
    h = min(t_ground, 2 * np.pi / w) / steps_per_period
    t_end = 12.0 / (zeta * w) + 20 * t_ground
    n = int(t_end / h)

    def f(t, y):
        return np.array([y[1], -a0 * np.sin(W * t) - 2 * zeta * w * y[1] - w * w * y[0]])

    y = np.zeros(2)
    t = 0.0
    peak = 0.0
    last = n - int(3 * max(t_ground, 2 * np.pi / w) / h)
    for i in range(n):
        k1 = f(t, y); k2 = f(t + h / 2, y + h / 2 * k1); k3 = f(t + h / 2, y + h / 2 * k2); k4 = f(t + h, y + h * k3)
        y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        t += h
        if i >= last:
            peak = max(peak, abs(y[0]))
    return float(peak)


# %% [markdown]
# ## Step 4: a design problem
# The ground has a dominant period T_g = 1 s. We want the amplification factor to stay at or
# below D_max = 2. There are two ways to get there: make the building *stiffer* (r below 1,
# short period) or *much more flexible* (r above 1, long period, as with base isolation).
# Solve D(r) = D_max for r by bisection on each side of the resonance, then turn r into a
# stiffness with  T = r T_g  and  k = m (2 pi / T)^2.

# %%
def stiffness_for_period(m, t):
    """k (N/m) that gives period t (s) for mass m (kg)."""
    return float(m * (2 * np.pi / t) ** 2)


def r_for_amplification(dmax, zeta=ZETA, side="stiff"):
    """The frequency ratio r where D(r) = dmax: below the resonance ('stiff') or above it ('flexible')."""
    rp = peak_amplification(zeta)[1]
    if dmax >= peak_amplification(zeta)[0]:
        raise ValueError("dmax must be below the resonance peak")
    lo, hi = (0.0, rp) if side == "stiff" else (rp, 20.0)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        above = amplification(mid, zeta) > dmax
        if side == "stiff":
            lo, hi = (mid, hi) if not above else (lo, mid)
        else:
            lo, hi = (lo, mid) if not above else (mid, hi)
    return 0.5 * (lo + hi)


def design_stiffness(m, t_ground, dmax, zeta=ZETA, side="stiff"):
    """Stiffness (N/m) keeping the amplification factor at dmax for a ground period t_ground.
    r = (W / w) = T / t_ground, so the building period is T = r t_ground."""
    r = r_for_amplification(dmax, zeta, side)
    return stiffness_for_period(m, r * t_ground)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    m = 2.0e5
    k0 = stiffness_for_period(m, 1.0)
    print(f"m = {m:.0f} kg, k0 = {k0:.4g} N/m gives T = {period(k0, m):.4f} s (resonant with a 1 s ground)")
    print("peak amplification at 5%:", peak_amplification(0.05), " 1/(2 zeta) =", 1 / 0.1)
    ks = design_stiffness(m, 1.0, 2.0)
    kf = design_stiffness(m, 1.0, 2.0, side="flexible")
    print(f"stiffer design: k = {ks:.4g} N/m (x{ks / k0:.3f}), T = {period(ks, m):.4f} s")
    print(f"flexible design: k = {kf:.4g} N/m (x{kf / k0:.3f}), T = {period(kf, m):.4f} s")
    r = np.linspace(0, 3, 601)
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    for z in (0.02, 0.05, 0.10, 0.20):
        ax[0].plot(r, amplification(r, z), label=f"zeta = {z}")
    ax[0].axhline(2, color="red", ls="--", lw=0.8)
    ax[0].set_ylim(0, 12)
    ax[0].set_xlabel("frequency ratio r = W / w (no unit)")
    ax[0].set_ylabel("amplification factor D (no unit)")
    ax[0].set_title("Resonance curves")
    ax[0].grid(alpha=0.3)
    ax[0].legend(fontsize=8)
    # numerical dots on the formula
    for rr in (0.5, 1.0, 1.5):
        tg = 1.0
        w_target = 2 * np.pi / tg / rr
        kk = m * w_target ** 2
        num = sway_amplitude_numeric(1.0, kk, m, tg)
        ax[0].plot(rr, num / (1.0 / w_target ** 2), "ko", ms=5)
        print(f"r = {rr}: numeric D = {num * w_target ** 2:.4f}, formula {amplification(rr):.4f}")
    kk = np.linspace(2e6, 4e7, 200)
    ax[1].plot(kk / 1e6, [sway_amplitude(2.0, x, m, 1.0) * 1000 for x in kk])
    ax[1].axvline(k0 / 1e6, color="gray", ls=":", label="k giving T = 1 s")
    ax[1].axvline(ks / 1e6, color="green", ls="--", label="stiffer design (D = 2)")
    ax[1].axvline(kf / 1e6, color="purple", ls="--", label="flexible design (D = 2)")
    ax[1].set_xlabel("storey stiffness k (MN/m)")
    ax[1].set_ylabel("steady sway amplitude (mm)")
    ax[1].set_title("Ground: a0 = 2 m/s^2, period 1 s")
    ax[1].set_yscale("log")
    ax[1].grid(alpha=0.3, which="both")
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "resonance_and_design.png", dpi=120)

# %% [markdown]
# ## Where this stops
# One lump cannot show how floors bend over each other; Session 3 gives each floor its own mass.
# Steady harmonic shaking is also kinder than a real record, which has many frequencies at once.
