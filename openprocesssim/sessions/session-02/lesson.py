"""Session 2 (Level 2): streams, unit blocks, Raoult's law, bubble and dew points, the flash.

Run:  python start.py 2
Educational model only: ideal liquids and ideal gases, constant heat capacities, rounded
textbook constants. Not a design tool, and not compatible with any commercial package.
"""
# %% [markdown]
# # Session 2: the numbers inside the boxes
# **A. Real-world problem.** A liquid mixture of benzene and toluene is heated until it
# just starts to boil, then a little more. Part of it turns to vapour, which is richer in the
# more volatile benzene. At what temperature does it start to boil, and how much vapour do we
# get at a chosen temperature? A flowsheet program answers this thousands of times inside its
# boxes; today you write that box.
#
# Symbols: n_i = molar flow of component i (mol/s); z_i, x_i, y_i = mole fractions in the
# feed, liquid and vapour; P = pressure (kPa); T = temperature (K); V = vapour fraction
# (moles of vapour per mole of feed).

# %%
import pathlib
from dataclasses import dataclass

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

NAMES = ["benzene", "toluene", "ethanol"]
# Antoine: log10(P/mmHg) = A - B / (C + T/degC). Rounded textbook values, valid roughly 10-100 degC.
ANTOINE = np.array([[6.90565, 1211.033, 220.790],
                    [6.95464, 1344.800, 219.482],
                    [8.20417, 1642.890, 230.300]])
CP = np.array([136.0, 157.0, 112.0])          # liquid heat capacity, J/(mol K), approximate
DHVAP = np.array([30800.0, 33200.0, 38600.0])  # heat of vaporisation, J/mol, approximate
T_REF = 298.15                                 # enthalpy reference, K
P_ATM = 101.325                                # kPa
MMHG_TO_KPA = 0.1333224


# %% [markdown]
# ## Step 1: a stream object
# A stream is "what flows in a pipe": molar flow of each component, a temperature, a
# pressure and a phase tag ("L" liquid or "V" vapour). Enthalpy uses a constant Cp:
# H = sum n_i * (Cp_i * (T - T_ref)), plus n_i * dHvap_i if the stream is vapour.

# %%
@dataclass
class Stream:
    n: np.ndarray          # component molar flows, mol/s
    T: float               # K
    P: float               # kPa
    phase: str = "L"

    def total(self):
        return float(np.sum(self.n))

    def z(self):
        return self.n / self.total()

    def enthalpy(self):
        """Enthalpy flow in W (J/s) relative to the pure liquids at T_REF."""
        h = CP * (self.T - T_REF) + (DHVAP if self.phase == "V" else 0.0)
        return float(np.sum(self.n * h))


# %% [markdown]
# ## Step 2: unit blocks are functions
# Each block takes streams in and returns streams out (and a heat or work duty, in W).

# %%
def mixer(streams):
    """Adiabatic mixer of liquid streams; outlet pressure = lowest inlet pressure."""
    if any(s.phase != "L" for s in streams):
        raise ValueError("mixer: this teaching model mixes liquid streams only")
    n = sum(s.n for s in streams)
    hsum = sum(float(np.sum(s.n * CP)) * (s.T - T_REF) for s in streams)
    T = T_REF + hsum / float(np.sum(n * CP))
    return Stream(n, T, min(s.P for s in streams), "L")


def splitter(s, fractions):
    """Split one stream into several of identical composition. Fractions must sum to 1."""
    if abs(sum(fractions) - 1.0) > 1e-12 or min(fractions) < 0:
        raise ValueError("splitter: fractions must be >= 0 and sum to 1")
    return [Stream(f * s.n, s.T, s.P, s.phase) for f in fractions]


def heater(s, T_out):
    """Change temperature at constant pressure. Returns (stream, duty in W); negative duty = cooling."""
    out = Stream(s.n.copy(), T_out, s.P, s.phase)
    return out, out.enthalpy() - s.enthalpy()


def pump(s, P_out, eta=0.7, vm=1.0e-4):
    """Raise the pressure of a liquid. vm = molar volume (m3/mol, about 1e-4 for these liquids).
    Returns (stream, shaft power in W). Temperature rise is ignored."""
    w = s.total() * vm * (P_out - s.P) * 1000.0 / eta
    return Stream(s.n.copy(), s.T, P_out, s.phase), w


def valve(s, P_out):
    """Pressure drop with no work and no heat; a liquid keeps its temperature in this model."""
    if P_out > s.P:
        raise ValueError("valve: outlet pressure must not exceed inlet pressure")
    return Stream(s.n.copy(), s.T, P_out, s.phase)


# %% [markdown]
# ## Step 3: vapour pressure and Raoult's law
# The Antoine equation gives the vapour pressure P_sat(T) of a pure liquid. For an ideal
# mixture Raoult's law says the partial pressure of i is x_i * P_sat_i(T), so the
# K-value (K_i = y_i / x_i) is K_i = P_sat_i / P. At the bubble point the liquid first
# boils: sum x_i P_sat_i(T) = P. At the dew point the vapour first condenses: sum y_i / K_i = 1.

# %%
def psat(T, idx=None):
    """Vapour pressure in kPa at T (K). All components if idx is None."""
    a = ANTOINE if idx is None else ANTOINE[idx]
    return MMHG_TO_KPA * 10.0 ** (a[..., 0] - a[..., 1] / (a[..., 2] + T - 273.15))


def k_values(T, P):
    return psat(T) / P


def _bisect(f, lo, hi, tol=1e-10, maxit=200):
    """Root of f in [lo, hi] by bisection; returns (root, iterations). f(lo) and f(hi) must differ in sign."""
    flo = f(lo)
    for it in range(1, maxit + 1):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if flo * fm <= 0:
            hi = mid
        else:
            lo, flo = mid, fm
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi), it


def bubble_T(x, P):
    """Bubble-point temperature (K) of liquid x at pressure P (kPa), ideal. Returns (T, y)."""
    x = np.asarray(x, dtype=float)
    mask = x > 0
    f = lambda T: float(np.sum(x[mask] * psat(T)[mask])) / P - 1.0
    T, _ = _bisect(f, 200.0, 500.0)
    y = x * k_values(T, P)
    return T, y / y.sum()


def dew_T(y, P):
    """Dew-point temperature (K) of vapour y at pressure P (kPa), ideal. Returns (T, x)."""
    y = np.asarray(y, dtype=float)
    mask = y > 0
    f = lambda T: float(np.sum(y[mask] / k_values(T, P)[mask])) - 1.0
    T, _ = _bisect(f, 200.0, 500.0)
    x = y / k_values(T, P)
    return T, x / x.sum()


# %% [markdown]
# ## Step 4: the Rachford-Rice flash
# Feed z (1 mole), split into vapour V and liquid 1 - V. Component balance z_i = V y_i + (1-V) x_i
# with y_i = K_i x_i gives x_i = z_i / (1 + V (K_i - 1)). Because the mole fractions of the
# liquid must sum to 1 as well as those of the vapour, we need
#
#     f(V) = sum_i z_i (K_i - 1) / (1 + V (K_i - 1)) = 0.
#
# f falls as V grows, so there is one root between 0 and 1 (if the feed is two-phase).
# f(0) <= 0 means the feed is liquid below its bubble point (V = 0). f(1) >= 0 means it is all vapour.

# %%
def rr_f(V, z, K):
    return float(np.sum(z * (K - 1.0) / (1.0 + V * (K - 1.0))))


def rr_bisection(z, K, tol=1e-12):
    """Vapour fraction by bisection. Returns (V, iterations). V is clipped to 0 or 1 outside the two-phase region."""
    if rr_f(0.0, z, K) <= 0:
        return 0.0, 0
    if rr_f(1.0, z, K) >= 0:
        return 1.0, 0
    lo, hi = 0.0, 1.0
    for it in range(1, 200):
        mid = 0.5 * (lo + hi)
        if rr_f(mid, z, K) > 0:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi), it


def rr_newton(z, K, tol=1e-12):
    """Vapour fraction by Newton's method with a bisection safety net. Returns (V, iterations)."""
    if rr_f(0.0, z, K) <= 0:
        return 0.0, 0
    if rr_f(1.0, z, K) >= 0:
        return 1.0, 0
    lo, hi, V = 0.0, 1.0, 0.5
    for it in range(1, 100):
        f = rr_f(V, z, K)
        if f > 0:
            lo = V
        else:
            hi = V
        df = -float(np.sum(z * (K - 1.0) ** 2 / (1.0 + V * (K - 1.0)) ** 2))
        Vn = V - f / df
        if not (lo < Vn < hi):
            Vn = 0.5 * (lo + hi)
        if abs(Vn - V) < tol:
            return Vn, it
        V = Vn
    return V, it


def flash_TP(feed, T, P):
    """Isothermal flash of a stream at T, P. Returns (vapour stream, liquid stream, V, duty W).
    Duty = enthalpy out - enthalpy in (what the heater inside the box must supply)."""
    z = feed.z()
    K = k_values(T, P)
    V, _ = rr_newton(z, K)
    x = z / (1.0 + V * (K - 1.0))
    y = K * x
    x, y = x / x.sum(), y / y.sum()
    F = feed.total()
    vap = Stream(V * F * y, T, P, "V") if V > 0 else Stream(np.zeros(3), T, P, "V")
    liq = Stream((1.0 - V) * F * x, T, P, "L") if V < 1 else Stream(np.zeros(3), T, P, "L")
    return vap, liq, V, vap.enthalpy() + liq.enthalpy() - feed.enthalpy()


# %% [markdown]
# ## Step 5: a design problem (inverse)
# Instead of "given T find V", ask "given V find T": the flash temperature for 50 percent
# vapour. V rises with T, so bisection on T works.

# %%
def flash_T_for_vapour_fraction(z, P, V_target, lo=300.0, hi=450.0):
    """Temperature (K) at which the flash of feed z gives vapour fraction V_target (0 < V_target < 1)."""
    z = np.asarray(z, dtype=float)
    f = lambda T: rr_newton(z, k_values(T, P))[0] - V_target
    T, _ = _bisect(f, lo, hi)
    return T


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    z = np.array([0.5, 0.5, 0.0])
    Tb, yb = bubble_T(z, P_ATM)
    Td, xd = dew_T(z, P_ATM)
    print(f"equimolar benzene-toluene at 1 atm: bubble {Tb:.2f} K, dew {Td:.2f} K")
    print(f"first vapour y = {yb[:2].round(3)}")
    Th = flash_T_for_vapour_fraction(z, P_ATM, 0.5)
    print(f"flash T for 50 percent vapour: {Th:.2f} K")

    # figure 1: T-x-y diagram of benzene-toluene at 1 atm
    xb = np.linspace(0, 1, 101)
    bub = [bubble_T(np.array([x, 1 - x, 0.0]), P_ATM)[0] for x in xb]
    dew = [dew_T(np.array([x, 1 - x, 0.0]), P_ATM)[0] for x in xb]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(xb, bub, label="bubble curve (liquid x)")
    ax.plot(xb, dew, label="dew curve (vapour y)")
    ax.plot([0.5], [Tb], "ko")
    ax.plot([0.5], [Td], "ks")
    ax.set_xlabel("benzene mole fraction (liquid x or vapour y)")
    ax.set_ylabel("temperature T (K)")
    ax.set_title("Benzene-toluene at 1 atm (Raoult's law)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "txy.png", dpi=120)

    # figure 2: vapour fraction against flash temperature
    Ts = np.linspace(Tb - 3, Td + 3, 200)
    Vs = [rr_newton(z, k_values(T, P_ATM))[0] for T in Ts]
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.plot(Ts, Vs)
    ax2.axhline(0.5, color="gray", ls=":")
    ax2.plot([Th], [0.5], "ro")
    ax2.set_xlabel("flash temperature T (K)")
    ax2.set_ylabel("vapour fraction V (mol vapour / mol feed)")
    ax2.set_title("Flash curve of an equimolar feed at 1 atm")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "flash_curve.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Real liquids are not ideal (Session 3 shows an ethanol-benzene mixture where Raoult's law
# fails), and the flash here is a single box. Session 3 joins boxes into a flowsheet.
