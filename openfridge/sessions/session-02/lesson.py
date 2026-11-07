"""Session 2 (Level 2): COP, the Carnot limit and sizing a fridge for a heat leak.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: COP, the Carnot limit and sizing a fridge
# **A. Real-world problem.** A kitchen fridge holds 4 C inside while the kitchen is 25 C.
# Heat leaks in through the walls all day. How much electric power must the compressor
# use, and why does the same fridge use more power in a hot summer kitchen? Is there a
# best possible fridge?
#
# Educational model: ideal temperatures, steady state, one "fraction of Carnot" number
# for all real losses. Not a design tool for real appliances.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
ZERO_C = 273.15   # 0 degrees Celsius in kelvin


# %% [markdown]
# ## Step 1: kelvin, COP and the best possible COP
# Temperature ratios must use kelvin: T(K) = T(C) + 273.15.
#
#     COP = Q_cold / W                       (heat removed per unit of work)
#     COP_Carnot = T_c / (T_h - T_c)         (no fridge can beat this)
#
# `T_c` is the cold temperature and `T_h` the warm one, both in kelvin. A real fridge reaches
# only a fraction `eta2` of the Carnot value: COP = eta2 x COP_Carnot.

# %%
def kelvin(t_celsius):
    return t_celsius + ZERO_C


def cop_carnot(t_cold_c, t_hot_c):
    """Best possible COP between a cold space and a warm room (temperatures in Celsius)."""
    tc, th = kelvin(t_cold_c), kelvin(t_hot_c)
    if th <= tc:
        raise ValueError("the room must be warmer than the cold space")
    return tc / (th - tc)


def cop_real(t_cold_c, t_hot_c, eta2):
    """Real COP as a fraction eta2 (0 to 1) of the Carnot COP."""
    if not 0 < eta2 <= 1:
        raise ValueError("eta2 must be above 0 and at most 1")
    return eta2 * cop_carnot(t_cold_c, t_hot_c)


# %% [markdown]
# ## Step 2: size the compressor for a heat leak
# Steady state: heat removed Q_cold (per second) equals the leak. Then
#
#     W = Q_cold / COP        (electric power, W)
#     Q_hot = Q_cold + W      (heat given to the kitchen, W)

# %%
def electric_power(leak_w, t_cold_c, t_hot_c, eta2):
    return leak_w / cop_real(t_cold_c, t_hot_c, eta2)


def room_heating(leak_w, t_cold_c, t_hot_c, eta2):
    """Q_hot = Q_cold + W, in watts."""
    return leak_w + electric_power(leak_w, t_cold_c, t_hot_c, eta2)


# %% [markdown]
# ## Step 3: the design problem (inverse)
# Given a power limit, how hot may the kitchen be? Solve W = Q_cold (T_h - T_c) / (eta2 T_c)
# for the warm temperature:
#
#     T_h = T_c + eta2 x T_c x W / Q_cold

# %%
def max_room_temp_c(leak_w, t_cold_c, eta2, power_limit_w):
    """Warmest room (Celsius) for which the compressor power stays at or below the limit."""
    tc = kelvin(t_cold_c)
    return tc + eta2 * tc * power_limit_w / leak_w - ZERO_C


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    c = cop_carnot(4, 25)
    cr = cop_real(4, 25, 0.25)
    w = electric_power(60, 4, 25, 0.25)
    print(f"Carnot COP 4 C / 25 C = {c:.2f};  real COP (eta2 = 0.25) = {cr:.2f}")
    print(f"leak 60 W -> compressor {w:.1f} W, heat to kitchen {room_heating(60, 4, 25, 0.25):.1f} W")
    print(f"warmest room for 15 W limit (leak 60 W, eta2 0.30): {max_room_temp_c(60, 4, 0.30, 15):.1f} C")

    room = np.linspace(10, 45, 141)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for t_in, col in ((-18, "tab:purple"), (4, "tab:blue"), (10, "tab:green")):
        mask = room > t_in + 1
        ax.plot(room[mask], [cop_carnot(t_in, r) for r in room[mask]], color=col, label=f"inside {t_in} C")
    ax.plot(room, [cop_real(4, r, 0.25) for r in room], "k--", label="real fridge, 4 C, eta2 = 0.25")
    ax.set_ylim(0, 25)
    ax.set_xlabel("room temperature (C)")
    ax.set_ylabel("COP (no unit)")
    ax.set_title("Carnot COP falls as the room gets hotter")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "cop_vs_room.png", dpi=120)

    leak = np.linspace(10, 120, 56)
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    for th, col in ((20, "tab:green"), (25, "tab:blue"), (32, "tab:red")):
        ax2.plot(leak, [electric_power(q, 4, th, 0.25) for q in leak], color=col, label=f"room {th} C")
    ax2.axhline(15, color="gray", ls=":", label="15 W limit")
    ax2.set_xlabel("heat leak Q_cold (W)")
    ax2.set_ylabel("compressor power W (W)")
    ax2.set_title("Compressor power for a 4 C fridge, eta2 = 0.25")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "power_vs_leak.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The Carnot limit uses the room and inside temperatures. In a real fridge the refrigerant must
# be colder than the inside and hotter than the room, and that is why eta2 is small.
# Session 3 builds a cycle and measures eta2 instead of assuming it.
