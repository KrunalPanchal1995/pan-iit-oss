"""Session 2 (Level 2): the one-step Arrhenius model and the ignition-delay law.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the one-step model and the ignition-delay law
# **A. Real-world problem.** An engine designer asks: how hot must the charge be so that it ignites
# within 1 millisecond, and what happens to that delay if the charge is 50 K cooler? We turn the
# story of Session 1 into equations we can solve and invert.
#
# **Still a toy.** One made-up reaction (fuel -> products, heat released) with toy numbers. Real
# hydrogen-oxygen ignition has chain branching and explosion limits; this model only keeps the
# part that is common to all thermal ignition: heat feedback on an Arrhenius rate.
#
# **Plan.** (1) the equations, (2) an exact shortcut: temperature and fuel are tied together,
# (3) the delay as an integral, (4) the straight-line law ln(tau) against 1000/T0, (5) design.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

A_PRE = 2.5e9      # pre-exponential factor, 1/s (toy)
EA = 150e3         # activation energy, J/mol (toy)
R_GAS = 8.314      # gas constant, J/(mol K)
DT_AD = 1500.0     # Q/cp: adiabatic temperature rise when all fuel burns, K
RISE = 400.0       # ignition criterion: T has risen by this much, K


# %% [markdown]
# ## Step 1: the equations
# With `c` the fuel left (0 to 1), `Q` the heat per unit fuel burnt (J/kg) and `cp` the specific
# heat (J/(kg K)), so that `DT_AD = Q / cp`:
#
#     dc/dt = -k(T) c        dT/dt = DT_AD * k(T) c        k(T) = A exp(-Ea / (R T))
#
# (A lumped, insulated box at constant pressure with constant cp; Q/cp is a single toy number.)

# %%
def rate_const(T, A=A_PRE, Ea=EA):
    """Arrhenius rate constant, 1/s (T in kelvin, Ea in J/mol)."""
    return A * np.exp(-Ea / (R_GAS * np.asarray(T, dtype=float)))


# %% [markdown]
# ## Step 2: an exact shortcut
# Divide the two equations: `dT/dc = -DT_AD`. So `T = T0 + DT_AD * (1 - c)` at all times.
# Temperature and fuel are not independent: every unit of fuel burnt adds the same heat.
# The two equations collapse to one, `dc/dt = -k(T0 + DT_AD (1 - c)) c`, and time becomes an integral:
#
#     t(c) = integral from c to 1 of dc' / ( k(T(c')) c' )

# %%
def temperature_from_fuel(c, T0, dT_ad=DT_AD):
    return T0 + dT_ad * (1.0 - np.asarray(c, dtype=float))


def history(T0, dT_ad=DT_AD, Ea=EA, A=A_PRE, c_end=0.01, n=4000):
    """Exact curve: arrays t (s), T (K), c, obtained by integrating dc / (k c) with the trapezoid rule."""
    c = np.linspace(1.0, c_end, n)
    f = 1.0 / (rate_const(temperature_from_fuel(c, T0, dT_ad), A, Ea) * c)
    t = np.concatenate([[0.0], np.cumsum(0.5 * (f[1:] + f[:-1]) * (c[:-1] - c[1:]))])
    return t, temperature_from_fuel(c, T0, dT_ad), c


# %% [markdown]
# ## Step 3: the ignition delay as one integral
# Ignition = T has risen by RISE = 400 K, which happens when `c = 1 - RISE / DT_AD`. So
# `tau = integral from c* to 1 of dc / (k c)`. We evaluate it with Gauss-Legendre quadrature
# (a few hundred smart sample points), no time-stepping at all.

# %%
_X, _W = np.polynomial.legendre.leggauss(200)


def ignition_delay(T0, Ea=EA, dT_ad=DT_AD, A=A_PRE, rise=RISE):
    """Time (s) for T to rise by `rise` kelvin. Returns None if dT_ad <= rise (never reached)."""
    if dT_ad <= rise:
        return None
    cs = 1.0 - rise / dT_ad
    c = 0.5 * (1 - cs) * _X + 0.5 * (1 + cs)
    f = 1.0 / (rate_const(temperature_from_fuel(c, T0, dT_ad), A, Ea) * c)
    return float(0.5 * (1 - cs) * np.sum(_W * f))


def max_rate_delay(T0, Ea=EA, dT_ad=DT_AD, A=A_PRE):
    """Second definition: the time when dT/dt is largest. dT/dt = DT_AD k c as a function of c."""
    c = np.linspace(1.0, 1e-3, 200001)
    rate = dT_ad * rate_const(temperature_from_fuel(c, T0, dT_ad), A, Ea) * c
    cm = c[int(np.argmax(rate))]
    cx = 0.5 * (1 - cm) * _X + 0.5 * (1 + cm)
    f = 1.0 / (rate_const(temperature_from_fuel(cx, T0, dT_ad), A, Ea) * cx)
    return float(0.5 * (1 - cm) * np.sum(_W * f)), float(temperature_from_fuel(cm, T0, dT_ad))


def frank_kamenetskii(T0, Ea=EA, dT_ad=DT_AD, A=A_PRE):
    """Textbook estimate of the delay: tau = R T0^2 / (Ea DT_AD k(T0)).
    It replaces k(T) by k(T0) exp(Ea (T - T0) / (R T0^2)), which is good only for small T - T0."""
    return float(R_GAS * T0 ** 2 / (Ea * dT_ad * rate_const(T0, A, Ea)))


# %% [markdown]
# ## Step 4: the straight line of ln(tau) against 1000/T0
# If `tau` were proportional to `exp(E / (R T0))`, a plot of `ln tau` against `1000/T0` would be a
# straight line with slope `E / (1000 R)`. The ignition delay almost is such a line. We fit it by
# least squares and compare the slope with the activation energy that we put in.

# %%
def arrhenius_fit(T0s, **kw):
    """Fit ln(tau in s) = a + b * (1000 / T0). Returns slope b, intercept a, and R^2."""
    x = 1000.0 / np.asarray(T0s, dtype=float)
    y = np.log([ignition_delay(T, **kw) for T in T0s])
    b, a = np.polyfit(x, y, 1)
    resid = y - (a + b * x)
    return float(b), float(a), float(1 - np.sum(resid ** 2) / np.sum((y - y.mean()) ** 2))


# %% [markdown]
# ## Step 5: the design problem
# The delay falls steadily as T0 rises, so a target delay can be inverted by bisection.

# %%
def design_T0(tau_target, lo=700.0, hi=1500.0, **kw):
    """Starting temperature (K) whose ignition delay equals tau_target (s)."""
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if ignition_delay(mid, **kw) > tau_target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    T0s = np.arange(800.0, 1201.0, 50.0)
    print("  T0 (K)   delay +400K (ms)   max-rate delay (ms)   Frank-Kamenetskii (ms)   FK/exact")
    for T in T0s:
        d1 = ignition_delay(T)
        d2, Tm = max_rate_delay(T)
        d3 = frank_kamenetskii(T)
        print(f"  {T:6.0f}   {d1 * 1e3:15.4f}   {d2 * 1e3:18.4f}   {d3 * 1e3:20.4f}   {d3 / d1:8.3f}")
    b, a, r2 = arrhenius_fit(T0s)
    print(f"fit: slope = {b:.2f} per (1000/K), intercept = {a:.2f}, R^2 = {r2:.5f}; Ea/(1000 R) = {EA / (1000 * R_GAS):.2f}")
    print(f"effective activation energy from the fit = {b * 1000 * R_GAS / 1000:.1f} kJ/mol (input 150)")
    Td = design_T0(1.0e-3)
    print(f"design: T0 = {Td:.1f} K gives a 1.000 ms delay; at {Td - 50:.1f} K the delay is {ignition_delay(Td - 50) * 1e3:.2f} ms")

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for T in (900.0, 1000.0, 1100.0):
        t, Tt, c = history(T)
        tau = ignition_delay(T)
        ax.plot(t / tau, Tt, label=f"T0 = {T:.0f} K  (delay {tau * 1e3:.2f} ms)")
    ax.axvline(1.0, color="k", ls=":")
    ax.set_xlim(0, 1.5)
    ax.set_xlabel("time divided by the ignition delay (-)")
    ax.set_ylabel("temperature (K)")
    ax.set_title("Same shape, different clock")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "curves_scaled.png", dpi=120)

    xs = 1000.0 / T0s
    ys = np.log([ignition_delay(T) for T in T0s])
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.plot(xs, ys, "o", color="#1f6feb", label="model")
    xx = np.linspace(xs.min(), xs.max(), 50)
    ax2.plot(xx, a + b * xx, "-", color="#d9534f", label=f"fit, slope {b:.2f}")
    ax2.axhline(np.log(1e-3), color="gray", ls=":")
    ax2.text(xs.min() + 0.02, np.log(1e-3) + 0.15, "1 ms", fontsize=9)
    ax2.set_xlabel("1000 / T0  (1/K)")
    ax2.set_ylabel("ln( delay / 1 s )")
    ax2.set_title("The ignition-delay law is nearly a straight line")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "ln_tau_vs_1000_over_T0.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
