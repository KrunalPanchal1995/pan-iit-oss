"""Session 3 (Level 3): a eutectic alloy, a cooling simulation, and Scheil versus equilibrium.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: cooling a eutectic alloy, and when equilibrium fails
# **A. Real-world problem.** Electronics solder melts at a low temperature because tin and lead
# (the classic recipe) form a *eutectic*: a mixture that melts lower than either metal. When a
# solder joint cools in a factory it may freeze in a fraction of a second, far too fast for the atoms to
# reach the equilibrium that the lever rule assumes. The joint then contains a different structure than the diagram
# predicts. Here we (1) build a eutectic diagram, (2) simulate the cooling curve with latent heat,
# (3) compare equilibrium with fast (Scheil) freezing, and (4) find where the equilibrium assumption fails.
#
# **Illustrative numbers.** The diagram is *Pb-Sn-like*, with rounded round-number values (lead side
# 327 C, tin side 232 C, eutectic 183 C at 62 wt% Sn, solubility limits 19 and 97 wt% Sn) and straight lines.
# The heat capacity, latent heat and diffusion data are illustrative, not measured design data.
# Composition x is weight percent Sn. Temperatures in C, time in s, heat in J/g.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

T_PB, T_SN, T_E = 327.0, 232.0, 183.0       # melting points of the pure metals and the eutectic, C
C_ALPHA, C_E, C_BETA = 19.0, 62.0, 97.0     # alpha solubility limit, eutectic point, beta limit (wt% Sn)
M_L = (T_PB - T_E) / C_E                     # liquidus slope on the lead side, C per wt% Sn
M_S = (T_PB - T_E) / C_ALPHA                 # solidus slope on the lead side, C per wt% Sn
K = C_ALPHA / C_E                            # partition coefficient C_solid / C_liquid (constant here)

C_HEAT = 0.2          # specific heat, J/(g K), same in every phase (simplification)
L_HEAT = 50.0         # latent heat of freezing, J/g (illustrative)
D_SOLID = 1.0e-12     # diffusion coefficient of Sn in solid alpha, m^2/s (illustrative)
LAMBDA = 20.0e-6      # half the dendrite arm spacing, m (illustrative; really depends on cooling rate)


# %% [markdown]
# ## Step 1: the eutectic diagram (lead-rich side)
# Liquidus: T_L(x) = 327 - M_L x.  Solidus of the alpha solid: T_S(x) = 327 - M_S x for x <= 19.
# Both lines start at the same point (pure Pb), so the ratio of the compositions on a tie line is
# *constant*: C_solid / C_liquid = M_L / M_S = 19/62 = K (about 0.31). Below 183 C the liquid left
# (62 wt% Sn) freezes all at once into a fine eutectic mixture of alpha and beta.

# %%
def t_liquidus(x):
    return T_PB - M_L * x


def t_solidus(x):
    """Equilibrium end of freezing: the alpha solidus, or the eutectic line when x > 19."""
    return max(T_PB - M_S * x, T_E) if x < C_E else T_E


def eq_solid_fraction(T, x):
    """Equilibrium (lever rule) solid fraction at T for a lead-rich alloy x <= 62 wt% Sn.
    Above the liquidus: 0. Just above 183 C for x > 19 it is (62 - x)/(62 - 19); at or below
    the end of freezing it is 1 (the eutectic freezes at 183 C)."""
    tl, ts = t_liquidus(x), t_solidus(x)
    if tl - ts < 1e-9:                     # pure Pb or the eutectic composition
        return 0.0 if T > tl + 1e-9 else 1.0
    if T >= tl:
        return 0.0
    if T <= ts:
        return 1.0
    c_l = (T_PB - T) / M_L
    c_s = (T_PB - T) / M_S
    return (c_l - x) / (c_l - c_s)


def pro_eutectic_fraction(x):
    """Fraction of primary alpha (grown before the eutectic) just above 183 C, for 19 <= x <= 62."""
    return (C_E - x) / (C_E - C_ALPHA)


def eutectic_mixture_fraction(x):
    return 1.0 - pro_eutectic_fraction(x)


def liquid_fraction_eq(x, T):
    return 1.0 - eq_solid_fraction(T, x)


# %% [markdown]
# ## Step 2: a cooling simulation with latent heat (the enthalpy method)
# Heat content per gram: H(T) = c T + L (1 - f_s(T)).  While heat leaves at rate q (W/g),
#
#     dH/dt = -q      so      H_(n+1) = H_n - q dt,   then find T with H(T) = H_(n+1).
#
# f_s(T) is the lever-rule solid fraction. Where f_s changes quickly with T the temperature falls
# slowly (the *effective* heat capacity is c + L |d f_s / dT|); where f_s jumps (the eutectic) the
# temperature stops: a flat arrest. This is energy conservation applied step by step.

# %%
def temperature_from_enthalpy(H, fs_fun, lo=0.0, hi=700.0):
    """Invert H(T) = c T + L (1 - fs_fun(T)) by bisection. Works across jumps (arrests)."""
    a, b = lo, hi
    for _ in range(55):
        m = 0.5 * (a + b)
        if C_HEAT * m + L_HEAT * (1.0 - fs_fun(m)) >= H:
            b = m
        else:
            a = m
    return 0.5 * (a + b)


def simulate_cooling(fs_fun, q_fun, T0, T_end, n_steps=3000, max_steps=200000):
    """March the enthalpy forward in time. q_fun(T) is the heat loss rate (W/g) at temperature T.
    Returns arrays t (s), T (C) and the frozen fraction f (from f = 1 - (H - cT)/L)."""
    H = C_HEAT * T0 + L_HEAT * (1.0 - fs_fun(T0))
    H_end = C_HEAT * T_end + L_HEAT
    dt = (H - H_end) / q_fun(T0) / n_steps
    ts, Ts, fs = [0.0], [T0], [fs_fun(T0)]
    T = T0
    while T > T_end and len(ts) < max_steps:
        H -= q_fun(T) * dt
        T = temperature_from_enthalpy(H, fs_fun)
        ts.append(ts[-1] + dt)
        Ts.append(T)
        fs.append(min(1.0, max(0.0, 1.0 - (H - C_HEAT * T) / L_HEAT)))
    return np.array(ts), np.array(Ts), np.array(fs)


def constant_q(q):
    return lambda T: q


def newtonian_q(h, T_amb=25.0):
    """Heat loss q = h (T - T_amb) with h in W/(g K)."""
    return lambda T: h * (T - T_amb)


def arrest_duration(t, T, T_level, tol=1e-6):
    """Time the temperature sits within tol of T_level (flat arrest)."""
    dt = t[1] - t[0]
    return float(np.sum(np.abs(T - T_level) < tol) * dt)


def time_to_reach(t, T, T_target):
    """First time the falling curve reaches T_target (linear interpolation)."""
    i = int(np.argmax(T <= T_target))
    if i == 0:
        return float(t[0])
    f = (T[i - 1] - T_target) / (T[i - 1] - T[i])
    return float(t[i - 1] + f * (t[i] - t[i - 1]))


# %% [markdown]
# ## Step 3: Scheil (no diffusion in the solid) versus equilibrium
# At the other extreme from the lever rule, assume the solid does not change after it forms
# and the liquid stays perfectly mixed. A thin slice dfs of solid has composition k C_L. Sn leaving
# the liquid: (1 - f_s) dC_L = (C_L - k C_L) d f_s, which integrates to the **Scheil equation**
#
#     C_L = C0 f_L^(k-1),     C_S = k C_L = k C0 f_L^(k-1),     f_L = 1 - f_s.
#
# The liquid keeps getting richer in Sn until it reaches the eutectic 62 wt% Sn, even for alloys
# the equilibrium diagram says are fully solid before that.

# %%
def scheil_liquid_composition(fl, x, k=K):
    return x * np.asarray(fl, dtype=float) ** (k - 1.0)


def scheil_solid_composition(fl, x, k=K):
    return k * scheil_liquid_composition(fl, x, k)


def scheil_eutectic_fraction(x, k=K):
    """Liquid fraction left when C_L reaches the eutectic 62 wt% Sn (it then freezes as eutectic)."""
    return min(1.0, (C_E / x) ** (1.0 / (k - 1.0)))


def scheil_solid_fraction(T, x, k=K):
    """Scheil f_s at temperature T (C) for x < 62: the eutectic arrest takes all liquid left at 183 C."""
    if T >= t_liquidus(x):
        return 0.0
    if T <= T_E:
        return 1.0
    fl = ((T_PB - T) / (M_L * x)) ** (1.0 / (k - 1.0))
    return 1.0 - fl


def scheil_by_integration(x, fs_end, k=K, n=20000):
    """Integrate the mass-balance equation dC_L/d f_s = (1 - k) C_L / (1 - f_s) with RK4."""
    h = fs_end / n
    c, f = x, 0.0

    for _ in range(n):
        k1 = (1.0 - k) * c / (1.0 - f)
        k2 = (1.0 - k) * (c + 0.5 * h * k1) / (1.0 - f - 0.5 * h)
        k3 = (1.0 - k) * (c + 0.5 * h * k2) / (1.0 - f - 0.5 * h)
        k4 = (1.0 - k) * (c + h * k3) / (1.0 - f - h)
        c += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        f += h
    return c


def scheil_mass_balance(x, fs_end, k=K, n=200001):
    """Total Sn found in the solid made so far plus the Sn left in the liquid, divided by x.
    Must equal 1 (conservation of Sn)."""
    fs = np.linspace(0.0, fs_end, n)
    cs = scheil_solid_composition(1.0 - fs, x, k)
    sn_solid = float(np.sum(0.5 * (cs[1:] + cs[:-1]) * np.diff(fs)))
    sn_liquid = (1.0 - fs_end) * float(scheil_liquid_composition(1.0 - fs_end, x, k))
    return (sn_solid + sn_liquid) / x


# %% [markdown]
# ## Step 4: in between (Clyne-Kurz back-diffusion) and the effect of cooling rate
# Real freezing lies between the two extremes. The Clyne-Kurz model adds limited diffusion in the solid
# through one number, alpha = D t_f / lambda^2 (diffusion distance squared over the arm size squared,
# with t_f the local freezing time). Slow cooling = long t_f = large alpha = lever rule.
# Fast cooling = tiny alpha = Scheil. The model uses
#
#     a' = alpha (1 - exp(-1/alpha)) - 0.5 exp(-1/(2 alpha)),     C_L = C0 [1 - (1 - 2 a' k) f_s]^((k-1)/(1 - 2 a' k)).
#
# a' = 0 gives Scheil and a' = 0.5 gives the lever rule exactly.

# %%
def alpha_prime(alpha):
    if alpha <= 0.0:
        return 0.0
    if alpha > 1e3:
        return 0.5                      # lever-rule limit (avoids round-off for huge alpha)
    return alpha * (1.0 - math.exp(-1.0 / alpha)) - 0.5 * math.exp(-1.0 / (2.0 * alpha))


def clyne_kurz_liquid_composition(fs, x, ap, k=K):
    s = 1.0 - 2.0 * ap * k
    return x * (1.0 - s * np.asarray(fs, dtype=float)) ** ((k - 1.0) / s)


def clyne_kurz_eutectic_fraction(x, ap, k=K):
    """Fraction of the casting that freezes as eutectic when back-diffusion strength is a'."""
    s = 1.0 - 2.0 * ap * k
    fs_at_e = (1.0 - (C_E / x) ** (s / (k - 1.0))) / s
    return max(0.0, 1.0 - fs_at_e)


def back_diffusion_alpha(t_freeze):
    return D_SOLID * t_freeze / LAMBDA ** 2


def freezing_time(x, q):
    """Time (s) to cross the freezing range at constant heat loss q (W/g), equilibrium freezing, from the simulation."""
    tl = t_liquidus(x)
    ts = t_solidus(x)
    t, T, _ = simulate_cooling(lambda T_: eq_solid_fraction(T_, x), constant_q(q), tl + 20.0, ts - 20.0, n_steps=4000)
    return time_to_reach(t, T, ts + 1e-9) - time_to_reach(t, T, tl - 1e-9)


# %% [markdown]
# ## Step 5: a design question for the mini-project
# Which alloy, and which temperature, gives a wanted liquid fraction (a pasty solder)?
# For 19 < x < 62 the liquid fraction between 183 C and the liquidus follows the lever rule.

# %%
def temperature_for_liquid_fraction(x, target):
    """Temperature (C) in the alpha + liquid band where alloy x (19 < x < 62) has liquid fraction `target`.
    If the target is below the liquid fraction available just above 183 C, that fraction is only
    reached during the eutectic arrest, so 183 C is returned."""
    lo, hi = T_E + 1e-9, t_liquidus(x)
    if liquid_fraction_eq(x, lo) >= target:
        return T_E
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if liquid_fraction_eq(x, mid) > target:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    # --- figure 1: the diagram with two alloys
    xa = np.linspace(0, C_E, 100)
    xb = np.linspace(C_E, 100, 100)
    fig, ax = plt.subplots(figsize=(6.6, 4.8))
    ax.plot(xa, T_PB - M_L * xa, "r-", label="liquidus")
    ax.plot(xb, T_SN + (T_E - T_SN) * (100 - xb) / (100 - C_E), "r-")
    ax.plot(np.linspace(0, C_ALPHA, 30), T_PB - M_S * np.linspace(0, C_ALPHA, 30), "b-", label="solidus")
    ax.plot([C_BETA, 100], [T_E, T_SN], "b-")
    ax.plot([0, 100], [T_E, T_E], "b-")
    for xx, lab in ((10, "10"), (40, "40")):
        ax.axvline(xx, color="gray", ls=":")
        ax.text(xx + 1, 345, lab + " wt% Sn", fontsize=8)
    ax.set_xlabel("composition (weight percent Sn)")
    ax.set_ylabel("temperature (C)")
    ax.set_title("Illustrative Pb-Sn-like eutectic diagram")
    ax.set_ylim(120, 360)
    ax.legend(loc="lower center")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "eutectic_diagram.png", dpi=120)

    # --- figure 2: cooling curves for 40 wt% Sn and 10 wt% Sn
    q = 0.5
    fig2, axs = plt.subplots(1, 2, figsize=(9.6, 4.4))
    for x, ax_ in zip((40.0, 10.0), axs):
        t, T, f = simulate_cooling(lambda T_: eq_solid_fraction(T_, x), constant_q(q), t_liquidus(x) + 40.0, 120.0)
        ax_.plot(t, T, "k-", label="equilibrium (lever rule)")
        ts_, Ts_, _ = simulate_cooling(lambda T_: scheil_solid_fraction(T_, x), constant_q(q), t_liquidus(x) + 40.0, 120.0)
        ax_.plot(ts_, Ts_, "r--", label="Scheil")
        ax_.set_xlabel("time (s)")
        ax_.set_ylabel("temperature (C)")
        ax_.set_title(f"{x:.0f} wt% Sn, heat loss {q} W/g")
        ax_.grid(alpha=0.3)
        ax_.legend(fontsize=8)
        print(f"{x:.0f} wt% Sn: liquidus {t_liquidus(x):.1f} C, eutectic arrest (equilibrium) {arrest_duration(t, T, T_E):.1f} s, "
              f"(Scheil) {arrest_duration(ts_, Ts_, T_E):.1f} s")
    fig2.tight_layout()
    fig2.savefig(OUT / "cooling_curves.png", dpi=120)

    # --- figure 3: coring (Scheil solid composition) and cooling-rate sensitivity
    x0 = 10.0
    fe_scheil = scheil_eutectic_fraction(x0)
    print(f"x0 = {x0:.0f}: Scheil eutectic fraction {100 * fe_scheil:.1f} %, equilibrium 0 %; core {K * x0:.2f}, rim up to {C_ALPHA:.0f} wt% Sn")
    fig3, axs3 = plt.subplots(1, 2, figsize=(9.6, 4.4))
    fs = np.linspace(0, 1.0 - fe_scheil, 200)
    axs3[0].plot(fs, scheil_solid_composition(1 - fs, x0), "r-", label="Scheil (fast)")
    axs3[0].axhline(x0, color="k", label="equilibrium (slow, after full diffusion)")
    axs3[0].set_xlabel("fraction solid when this layer formed (centre to edge)")
    axs3[0].set_ylabel("Sn in the solid layer (wt%)")
    axs3[0].set_title("Coring: the dendrite centre is Sn-poor")
    axs3[0].legend(fontsize=8)
    axs3[0].grid(alpha=0.3)
    qs = np.logspace(-2.5, 1.5, 17)
    fes = []
    for qq in qs:
        tf = freezing_time(x0, qq)
        fes.append(100 * clyne_kurz_eutectic_fraction(x0, alpha_prime(back_diffusion_alpha(tf))))
    axs3[1].semilogx(qs / C_HEAT, fes, "o-")
    axs3[1].axhline(100 * fe_scheil, color="r", ls="--", label="Scheil limit")
    axs3[1].set_xlabel("cooling rate of the liquid, q/c (K/s)")
    axs3[1].set_ylabel("eutectic in a 10 wt% Sn alloy (%)")
    axs3[1].set_title("Equilibrium predicts 0 %; fast cooling creates eutectic")
    axs3[1].legend(fontsize=8)
    axs3[1].grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "scheil_and_rate.png", dpi=120)
    for qq, fe in zip(qs[::4], fes[::4]):
        print(f"  q = {qq:.4g} W/g (liquid rate {qq / C_HEAT:.3g} K/s): eutectic {fe:.2f} %")

# %% [markdown]
# ## Where this stops
# A lumped model has one temperature for the whole casting; real castings freeze from the wall inwards.
# Constant k, straight lines and no undercooling are simplifications. Treat every number here as
# a teaching illustration, never as design data for a real solder or casting.
