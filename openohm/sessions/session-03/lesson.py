"""Session 3 (Level 3): a non-ohmic part (an LED) solved numerically and validated.

Run:  python start.py 3
Low-voltage educational circuits only (never mains). A simplified LED model, not a datasheet.
"""
# %% [markdown]
# # Session 3: when Ohm's law is not enough
# **A. Real-world problem.** An LED does not obey V = I R. Connect it straight to a battery and
# it burns out. A series resistor limits the current, but what current actually flows, and how
# much does it change if the supply is 10 percent off?
#
# **Plan.** (1) an LED model, (2) solve supply = I R + V_led by Newton's method, (3) validate
# against bisection and the ohmic limit, (4) measure the sensitivity to the supply voltage.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

N_VT = 0.05                              # ideality factor times thermal voltage (volts)
I_REF, V_REF = 0.020, 2.0               # model is tuned so that 20 mA gives 2.0 V
I_S = I_REF / np.expm1(V_REF / N_VT)    # saturation current (amperes)


# %% [markdown]
# ## Step 1: the LED model (Shockley form)
# I = I_s * (exp(V / N_VT) - 1). Below about 1.5 V almost nothing flows; near 2 V the current
# climbs steeply. Inverse: V = N_VT * ln(I / I_s + 1).

# %%
def led_current(vd):
    return I_S * np.expm1(vd / N_VT)


def led_voltage(i):
    return N_VT * np.log1p(i / I_S)


# %% [markdown]
# ## Step 2: the circuit equation and Newton's method
# Kirchhoff's voltage law around the loop: Vs = I R + Vd with I = led_current(Vd). Define
# f(Vd) = led_current(Vd) - (Vs - Vd) / R. We want f = 0. Newton's method repeats
# Vd <- Vd - f / f', with f' = I_s/N_VT * exp(Vd/N_VT) + 1/R.
# Graphically this is the *load line* (the straight line I = (Vs - Vd)/R) crossing the LED curve.

# %%
def solve_newton(vs, r, tol=1e-12, max_iter=200):
    """Return (Vd, I, iterations). Vd is clipped to [0, Vs] to keep exp() in range."""
    if r <= 0 or vs <= 0:
        raise ValueError("supply and resistance must be positive")
    vd = min(vs, 2.5)             # start where f > 0: for a convex f, Newton then only moves down
    for k in range(1, max_iter + 1):
        f = led_current(vd) - (vs - vd) / r
        fp = I_S / N_VT * np.exp(vd / N_VT) + 1.0 / r
        new = min(max(vd - f / fp, 0.0), vs)
        if abs(new - vd) < tol:
            vd = new
            return float(vd), float((vs - vd) / r), k
        vd = new
    raise RuntimeError("Newton did not converge")


def solve_bisection(vs, r, tol=1e-13):
    """Slow but safe reference: the root of f(Vd) lies between 0 and Vs."""
    lo, hi = 0.0, vs
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if led_current(mid) - (vs - mid) / r > 0:
            hi = mid
        else:
            lo = mid
    vd = 0.5 * (lo + hi)
    return float(vd), float((vs - vd) / r)


# %% [markdown]
# ## Step 3: validation and sensitivity
# (a) Newton must agree with bisection. (b) Ohmic limit: if the "part" were an ordinary resistor
# Rx, the answer is a voltage divider; the same Newton step must reproduce it (one iteration for
# a linear problem). (c) The ohmic shortcut I = Vs / R (ignore the LED) is wrong. (d) Sensitivity:
# dI/dVs = 1 / (R + r_d), with the LED's dynamic resistance r_d = N_VT / I.

# %%
def newton_linear(vs, r, rx):
    """Same Newton update for a linear part Rx (ohmic limit). Returns (V across part, iterations)."""
    v, k = 0.0, 0
    for k in range(1, 10):
        f = v / rx - (vs - v) / r
        new = v - f / (1.0 / rx + 1.0 / r)
        if abs(new - v) < 1e-14:
            return float(new), k
        v = new
    return float(v), k


def sensitivity(vs, r, dv=1e-3):
    """dI/dVs (A per V) by central difference, and the formula 1 / (R + N_VT / I)."""
    fd = (solve_newton(vs + dv, r)[1] - solve_newton(vs - dv, r)[1]) / (2 * dv)
    i = solve_newton(vs, r)[1]
    return fd, 1.0 / (r + N_VT / i)


def current_range(vs_nominal, tol_frac, r):
    """(I at the lowest supply, I at the highest supply) for a supply tolerance."""
    lo = solve_newton(vs_nominal * (1 - tol_frac), r)[1]
    hi = solve_newton(vs_nominal * (1 + tol_frac), r)[1]
    return lo, hi


E12 = (1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2)


def pick_resistor(vs, tol_frac, i_min, i_max, p_max):
    """E12 resistors (ohms) that keep the LED current in [i_min, i_max] over the supply
    tolerance and the total power at the highest supply below p_max (watts)."""
    ok = []
    for r in [round(v * 10 ** d, 6) for d in range(1, 4) for v in E12]:
        lo, hi = current_range(vs, tol_frac, r)
        _, i_top, _ = solve_newton(vs * (1 + tol_frac), r)
        if lo >= i_min and hi <= i_max and vs * (1 + tol_frac) * i_top <= p_max:
            ok.append(r)
    return ok


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    vd, i, k = solve_newton(5.0, 150.0)
    print(f"5 V and 150 ohm: LED {vd:.3f} V, I = {1000 * i:.2f} mA, {k} Newton steps")
    print(f"ohmic shortcut 5/150 = {1000 * 5 / 150:.2f} mA (wrong)")
    print("bisection:", [round(x, 6) for x in solve_bisection(5.0, 150.0)])
    print("sensitivity (finite difference, formula) mA/V:", [round(1000 * x, 3) for x in sensitivity(5.0, 150.0)])
    lo, hi = current_range(5.0, 0.10, 150.0)
    print(f"supply 4.5 to 5.5 V: I from {1000 * lo:.2f} to {1000 * hi:.2f} mA")
    print("safe E12 choices (5 V +-10 %, 10-25 mA, 0.12 W):", pick_resistor(5.0, 0.10, 0.010, 0.025, 0.12))
    print("power in resistor, LED (mW):", round(1000 * i * i * 150, 1), round(1000 * i * vd, 1))

    vds = np.linspace(0, 2.4, 300)
    fig, ax = plt.subplots(figsize=(6.5, 4.3))
    ax.plot(vds, 1000 * led_current(vds), label="LED curve")
    for vs, r in ((5.0, 150.0), (4.5, 150.0), (5.5, 150.0)):
        ax.plot(vds, 1000 * (vs - vds) / r, "--", label=f"load line {vs:g} V, {r:g} ohm")
        vd_, i_, _ = solve_newton(vs, r)
        ax.plot([vd_], [1000 * i_], "ko")
    ax.set_ylim(0, 40)
    ax.set_xlabel("LED voltage Vd (volts)")
    ax.set_ylabel("current I (milliamperes)")
    ax.set_title("Load line meets the LED curve")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "load_line.png", dpi=120)

    rs = np.linspace(60, 600, 120)
    fig2, ax2 = plt.subplots(figsize=(6.5, 4.3))
    ax2.plot(rs, [1000 * solve_newton(5.0, r)[1] for r in rs], label="Newton with LED")
    ax2.plot(rs, 1000 * 5.0 / rs, "--", label="ohmic shortcut Vs / R")
    ax2.plot(rs, 1000 * (5.0 - V_REF) / rs, ":", label="constant 2 V drop (Vs - 2) / R")
    ax2.set_ylim(0, 60)
    ax2.set_xlabel("series resistor R (ohms)")
    ax2.set_ylabel("current I (milliamperes)")
    ax2.set_title("Ignoring the LED overestimates the current")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "led_current_vs_r.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
