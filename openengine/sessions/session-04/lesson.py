"""Session 4 (Level 2): air whose cp and cv grow with temperature.

Run:  python start.py 4
"""
# %% [markdown]
# # Session 4: temperature-dependent gas properties
# **A. Real-world problem.** Session 2 promised an ideal Otto efficiency of 0.585 at r = 9, but
# real petrol engines reach only about 0.25 to 0.35. Part of the gap is burn time, heat loss and
# friction (Session 3). Another part hides in one number: gamma = 1.4. Hot air stores more
# energy per kelvin than cold air, so gamma falls as the gas heats up. How much efficiency does
# that cost, even in a perfect engine?
#
# **Plan.** (1) cp(T) of air from a published polynomial, (2) internal energy u(T) and an
# entropy-like function for isentropes, (3) the Otto cycle with variable properties, (4) check it
# against Session 2 when the properties are held constant, (5) measure how efficiency falls with
# the heat added.
#
# **Model.** Air-standard cycle as in Session 2 (ideal gas, heat from outside, no friction, no
# heat loss) but cp and cv depend on temperature. No dissociation of the hot gas. This is a
# simplified teaching model, not a design tool.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
R_AIR = 0.287          # gas constant of air, kJ/(kg K), as in Session 2
GAMMA = 1.4            # Session 2's constant gamma, kept for comparison


# %% [markdown]
# ## Step 1: cp(T) of air from the NASA polynomials
# Tables such as JANAF and the NASA thermodynamic database fit the heat capacity of each gas with
# a polynomial in T, in two temperature ranges (200 to 1000 K and 1000 to 6000 K):
#
#     cp / R = a1 + a2 T + a3 T**2 + a4 T**3 + a5 T**4
#
# The same seven coefficients also give enthalpy and entropy (a6 and a7 are integration
# constants). Air is about 79 percent N2 and 21 percent O2 by moles (argon counted as N2), and
# for an ideal-gas mixture the molar coefficients simply mix in that ratio. Multiplying by
# R = 0.287 kJ/(kg K) gives values per kg of air.
#
# Coefficients for N2 and O2 below are the widely used NASA 7-coefficient fits (as published
# in the GRI-Mech 3.0 thermodynamic data).

# %%
NASA = {   # species: (coefficients for 1000-6000 K, coefficients for 200-1000 K)
    "N2": ([2.92664000e+00, 1.48797680e-03, -5.68476000e-07, 1.00970380e-10, -6.75335100e-15, -9.22797700e+02, 5.98052800e+00],
           [3.29867700e+00, 1.40824040e-03, -3.96322200e-06, 5.64151500e-09, -2.44485400e-12, -1.02089990e+03, 3.95037200e+00]),
    "O2": ([3.28253784e+00, 1.48308754e-03, -7.57966669e-07, 2.09470555e-10, -2.16717794e-14, -1.08845772e+03, 5.45323129e+00],
           [3.78245636e+00, -2.99673416e-03, 9.84730201e-06, -9.68129509e-09, 3.24372837e-12, -1.06394356e+03, 3.65767573e+00]),
}
AIR = {"N2": 0.79, "O2": 0.21}
T_MID = 1000.0
A_HIGH = np.sum([x * np.array(NASA[s][0]) for s, x in AIR.items()], axis=0)
A_LOW = np.sum([x * np.array(NASA[s][1]) for s, x in AIR.items()], axis=0)


def _coeffs(t):
    if not 200.0 <= t <= 6000.0:
        raise ValueError("the polynomials are valid from 200 K to 6000 K")
    return A_LOW if t < T_MID else A_HIGH


def cp_air(t):
    """Specific heat at constant pressure of air, kJ/(kg K), at temperature t (K)."""
    a = _coeffs(t)
    return R_AIR * (a[0] + t * (a[1] + t * (a[2] + t * (a[3] + t * a[4]))))


def cv_air(t):
    """Specific heat at constant volume, kJ/(kg K): cv = cp - R for an ideal gas."""
    return cp_air(t) - R_AIR


def gamma_air(t):
    """Local ratio of specific heats cp / cv at temperature t."""
    return cp_air(t) / cv_air(t)


# %% [markdown]
# ## Step 2: energy and an isentrope with variable cv
# Integrating the polynomial gives the enthalpy h(T) (the NASA a6 term fixes h at 298 K) and
# u(T) = h(T) - R T. Heat added at constant volume raises u: `q = u(T3) - u(T2)`.
#
# For an isentrope Session 2 used `T V**(gamma-1) = const`. With variable cv we go back one
# step: for a small reversible step with no heat, `cv(T) dT / T = -R dv / v`. Integrating from
# state 1 to state 2 gives
#
#     phi(T2) - phi(T1) = R ln(v1 / v2) = R ln r,      phi(T) = s0(T) - R ln T
#
# where s0(T) is the tabulated entropy at 1 bar (its derivative is cp / T, so phi has derivative
# cv / T). phi only grows with T, so we can find T2 from phi(T2) by bisection.

# %%
def h_air(t):
    """Specific enthalpy of air, kJ/kg (zero point from the NASA tables)."""
    a = _coeffs(t)
    return R_AIR * t * (a[0] + t * (a[1] / 2 + t * (a[2] / 3 + t * (a[3] / 4 + t * a[4] / 5)))) + R_AIR * a[5]


def u_air(t):
    """Specific internal energy of air, kJ/kg: u = h - R T."""
    return h_air(t) - R_AIR * t


def s0_air(t):
    """Standard entropy of air at 1 bar (pure-species value, no mixing term), kJ/(kg K)."""
    a = _coeffs(t)
    return R_AIR * (a[0] * math.log(t) + t * (a[1] + t * (a[2] / 2 + t * (a[3] / 3 + t * a[4] / 4))) + a[6])


def phi_air(t):
    """s0(T) - R ln T, kJ/(kg K); it changes by R ln(v1 / v2) along an isentrope."""
    return s0_air(t) - R_AIR * math.log(t)


def solve_t(f, target, lo=200.0, hi=6000.0):
    """Temperature (K) where the increasing function f equals target, found by bisection."""
    if not f(lo) <= target <= f(hi):
        raise ValueError("no temperature between 200 K and 6000 K gives this value")
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if f(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# %% [markdown]
# ## Step 3: a gas object, so one cycle code serves both models
# A gas here is anything with `u(T)`, `h(T)`, `phi(T)` and `cp(T)`. `NasaAir` uses the
# polynomials. `ConstantGas` uses Session 2's constant gamma, for which `u = cv T` and
# `phi = cv ln T`. Running the same cycle code with `ConstantGas` must give back the Session 2
# formula exactly; that is our validation.

# %%
class NasaAir:
    """Air with cp(T) from the NASA polynomials."""
    name = "variable cp(T)"
    u = staticmethod(u_air)
    h = staticmethod(h_air)
    phi = staticmethod(phi_air)
    cp = staticmethod(cp_air)


class ConstantGas:
    """Ideal gas with constant gamma (Session 2)."""

    def __init__(self, gamma=GAMMA):
        self.gamma = gamma
        self.cv = R_AIR / (gamma - 1.0)
        self.name = f"constant gamma = {gamma}"

    def u(self, t):
        return self.cv * t

    def h(self, t):
        return (self.cv + R_AIR) * t

    def phi(self, t):
        return self.cv * math.log(t)

    def cp(self, t):
        return self.cv + R_AIR


def isentrope_t(gas, t_start, v_ratio):
    """Temperature after an isentropic change of volume by v_ratio = v_start / v_end."""
    return solve_t(gas.phi, gas.phi(t_start) + R_AIR * math.log(v_ratio))


# %% [markdown]
# ## Step 4: the Otto cycle with any gas
# 1 to 2: isentropic compression by r. 2 to 3: heat q_in at constant volume, u(T3) = u(T2) + q_in.
# 3 to 4: isentropic expansion by r. 4 to 1: heat rejected at constant volume,
# q_out = u(T4) - u(T1). Efficiency = 1 - q_out / q_in.
#
# The **effective gamma** is the constant gamma that would give the same efficiency in the
# Session 2 formula: `gamma_eff = 1 + ln(1 / (1 - eta)) / ln r`.

# %%
def otto_cycle(r, q_in, gas=None, t1=300.0):
    """Ideal Otto cycle. Returns a dict with T1..T4 (K), q_out (kJ/kg), eta and gamma_eff."""
    gas = gas or NasaAir
    if r <= 1:
        raise ValueError("compression ratio must be above 1")
    if q_in <= 0:
        raise ValueError("heat input must be positive")
    t2 = isentrope_t(gas, t1, r)
    t3 = solve_t(gas.u, gas.u(t2) + q_in)
    t4 = isentrope_t(gas, t3, 1.0 / r)
    q_out = gas.u(t4) - gas.u(t1)
    eta = 1.0 - q_out / q_in
    return {"T": (t1, t2, t3, t4), "q_out": q_out, "eta": eta, "gamma_eff": 1.0 + math.log(1.0 / (1.0 - eta)) / math.log(r)}


def diesel_cycle(r, q_in, gas=None, t1=300.0):
    """Ideal Diesel cycle: heat at constant pressure, h(T3) = h(T2) + q_in. Also returns rho."""
    gas = gas or NasaAir
    if r <= 1:
        raise ValueError("compression ratio must be above 1")
    t2 = isentrope_t(gas, t1, r)
    t3 = solve_t(gas.h, gas.h(t2) + q_in)
    rho = t3 / t2                                   # constant pressure: v grows with T
    t4 = isentrope_t(gas, t3, rho / r)              # expand from rho v2 to v1 = r v2
    q_out = gas.u(t4) - gas.u(t1)
    return {"T": (t1, t2, t3, t4), "rho": rho, "q_out": q_out, "eta": 1.0 - q_out / q_in}


# %% [markdown]
# ## Step 5: an independent check with P dv
# The heats above come from u(T). As a check that does not use u at all, trace the loop in small
# steps: along the isentropes solve `dT/dv = -R T / (cv(T) v)` with Runge-Kutta 4, then sum
# P dv around the loop as in Session 3. The area must equal q_in - q_out.

# %%
def otto_path(r, q_in, gas=None, t1=300.0, p1=100.0, n=400):
    """(v, P) arrays of the Otto loop, v in m3/kg and P in kPa, isentropes by RK4 on T(v)."""
    gas = gas or NasaAir
    cyc = otto_cycle(r, q_in, gas, t1)
    cv = lambda t: gas.cp(t) - R_AIR
    v1 = R_AIR * t1 / p1
    v2 = v1 / r

    def isentrope(t0, va, vb):
        vs = np.geomspace(va, vb, n + 1)
        ts = [t0]
        f = lambda v, t: -R_AIR * t / (cv(t) * v)
        for a, b in zip(vs[:-1], vs[1:]):
            dv, t = b - a, ts[-1]
            k1 = f(a, t)
            k2 = f(a + dv / 2, t + dv / 2 * k1)
            k3 = f(a + dv / 2, t + dv / 2 * k2)
            k4 = f(b, t + dv * k3)
            ts.append(t + dv * (k1 + 2 * k2 + 2 * k3 + k4) / 6)
        return vs, np.array(ts)

    vc, tc = isentrope(t1, v1, v2)
    ve, te = isentrope(cyc["T"][2], v2, v1)
    v = np.concatenate([vc, ve])
    p = R_AIR * np.concatenate([tc, te]) / v
    return v, p


def loop_work(v, p):
    """Sum of P dv around the closed loop (trapezoid rule), kJ/kg."""
    v2, p2 = np.roll(v, -1), np.roll(p, -1)
    return float(np.sum(0.5 * (p + p2) * (v2 - v)))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    for t in (300, 1000, 2000):
        print(f"T = {t} K: cp = {cp_air(t):.3f} kJ/(kg K), gamma = {gamma_air(t):.3f}")
    var, const = otto_cycle(9, 1100), otto_cycle(9, 1100, ConstantGas())
    print("Otto r = 9, q_in = 1100 kJ/kg:")
    print(f"  constant gamma: T = {[round(x, 1) for x in const['T']]}, eta = {const['eta']:.4f}")
    print(f"  variable cp(T): T = {[round(x, 1) for x in var['T']]}, eta = {var['eta']:.4f}, gamma_eff = {var['gamma_eff']:.3f}")
    v, p = otto_path(9, 1100)
    print(f"  P dv check: loop work {loop_work(v, p):.1f} kJ/kg against q_in - q_out = {1100 - var['q_out']:.1f} kJ/kg")
    d = diesel_cycle(18, 1100)
    print(f"Diesel r = 18, q_in = 1100: rho = {d['rho']:.3f}, eta = {d['eta']:.4f} "
          f"(constant gamma {diesel_cycle(18, 1100, ConstantGas())['eta']:.4f})")

    # colour-blind-safe colours (Okabe-Ito) and a line style per model
    C_CONST, C_VAR = "#0072B2", "#D55E00"

    # Figure 1: cp and gamma against temperature
    ts = np.linspace(250, 3000, 300)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 4))
    a1.plot(ts, [cp_air(t) for t in ts], color=C_VAR, label="air, NASA polynomial")
    a1.axhline(GAMMA * R_AIR / (GAMMA - 1), color=C_CONST, ls="--", label="constant (gamma = 1.4)")
    a1.set_xlabel("temperature T (K)")
    a1.set_ylabel("cp (kJ/(kg K))")
    a1.set_title("cp grows with temperature")
    a2.plot(ts, [gamma_air(t) for t in ts], color=C_VAR, label="air, NASA polynomial")
    a2.axhline(GAMMA, color=C_CONST, ls="--", label="Session 2: 1.4")
    a2.set_xlabel("temperature T (K)")
    a2.set_ylabel("gamma = cp / cv (no unit)")
    a2.set_title("so gamma falls")
    for a in (a1, a2):
        a.grid(alpha=0.3)
        a.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "cp_gamma.png", dpi=120)

    # Figure 2: efficiency against heat input and against compression ratio
    qs = np.linspace(100, 2500, 60)
    rs = np.linspace(4, 20, 60)
    fig2, (b1, b2) = plt.subplots(1, 2, figsize=(9.6, 4))
    b1.plot(qs, [otto_cycle(9, q, ConstantGas())["eta"] for q in qs], color=C_CONST, ls="--", label="constant gamma = 1.4")
    b1.plot(qs, [otto_cycle(9, q)["eta"] for q in qs], color=C_VAR, label="variable cp(T)")
    b1.plot([1100], [var["eta"]], "o", color=C_VAR)
    b1.annotate(f"{var['eta']:.3f}", (1100, var["eta"]), textcoords="offset points", xytext=(6, -14))
    b1.axhline(0.56, color="k", ls=":", lw=1, label="roadmap checkpoint 0.56")
    b1.set_xlabel("heat added q_in (kJ/kg)")
    b1.set_ylabel("ideal Otto efficiency (no unit)")
    b1.set_title("r = 9: more heat, hotter gas, lower efficiency")
    b2.plot(rs, [otto_cycle(r, 1100, ConstantGas())["eta"] for r in rs], color=C_CONST, ls="--", label="constant gamma = 1.4")
    b2.plot(rs, [otto_cycle(r, 1100)["eta"] for r in rs], color=C_VAR, label="variable cp(T)")
    b2.set_xlabel("compression ratio r")
    b2.set_ylabel("ideal Otto efficiency (no unit)")
    b2.set_title("q_in = 1100 kJ/kg: the gap at every r")
    for b in (b1, b2):
        b.grid(alpha=0.3)
        b.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "eta_variable_cp.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The gas still never changes its chemistry: at 2000 K and above real combustion products
# dissociate, which lowers the peak temperature further. The cycle is still instant and lossless.
# Session 5 keeps the ideal model and splits the heat between constant volume and constant
# pressure, as real diesels do.
