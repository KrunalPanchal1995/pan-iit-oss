"""Session 2 (Level 2): one atmospheric layer that absorbs infrared warms the surface.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the one-layer greenhouse model
# **A. Real-world problem.** Session 1 found that a bare Earth would sit at about 255 K
# (-18 C), but the real surface averages about 288 K (15 C). Air is almost transparent to
# sunlight, yet water vapour and carbon dioxide absorb the infrared that the warm ground
# sends up. How much infrared must the air absorb to explain the missing 33 K, and how
# warm would the surface get if the air absorbed all of it?
#
# **Plan.** (1) a single atmospheric layer with infrared absorptivity epsilon, (2) three
# energy balances (top of atmosphere, layer, surface) solved by hand, (3) find epsilon for
# today's Earth, (4) stacks of N opaque layers and Venus, (5) what a small rise in epsilon
# does: radiative forcing.
#
# **Model.** Averages over the whole globe and a whole year, per square metre. Sunlight
# passes the layer untouched; the layer absorbs a share epsilon of the infrared from the
# ground and, by Kirchhoff's law, emits epsilon sigma Ta^4 both upward and downward.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
SIGMA = 5.670374419e-8      # W/(m2 K4)
S_EARTH, ALBEDO_EARTH, T_OBS = 1361.0, 0.30, 288.0


def absorbed_solar(s=S_EARTH, albedo=ALBEDO_EARTH):
    """Sunlight absorbed per square metre, averaged over the sphere (W/m2)."""
    if s <= 0 or not 0.0 <= albedo <= 1.0:
        raise ValueError("need S > 0 and 0 <= albedo <= 1")
    return s * (1.0 - albedo) / 4.0


def bare_temperature(s=S_EARTH, albedo=ALBEDO_EARTH):
    """Session 1: the bare-planet (effective) temperature in K."""
    return (absorbed_solar(s, albedo) / SIGMA) ** 0.25


# %% [markdown]
# ## Step 1: three balances, solved by hand
# Write G = sigma Ts^4 (ground emission) and A = sigma Ta^4 (layer emission per face).
#
# * **Layer:** absorbs eps G, emits eps A up and eps A down, so eps G = 2 eps A, i.e. A = G / 2.
# * **Top of atmosphere:** sunlight absorbed = what escapes = (1 - eps) G + eps A.
# * Putting A = G / 2 in: absorbed = G (1 - eps / 2), so
#
#       Ts = Te [ 2 / (2 - eps) ]^(1/4)        Ta = Ts / 2^(1/4)
#
# * **Surface check:** absorbed sunlight + eps A (back-radiation) = G. It holds automatically.

# %%
def surface_temperature(eps, s=S_EARTH, albedo=ALBEDO_EARTH):
    """Surface temperature (K) under one layer with infrared absorptivity eps (0 to 1)."""
    if not 0.0 <= eps <= 1.0:
        raise ValueError("eps must lie between 0 and 1")
    return bare_temperature(s, albedo) * (2.0 / (2.0 - eps)) ** 0.25


def layer_temperature(eps, s=S_EARTH, albedo=ALBEDO_EARTH):
    """Temperature of the absorbing layer (K): Ts / 2^(1/4), whatever eps is."""
    return surface_temperature(eps, s, albedo) / 2.0 ** 0.25


def fluxes(eps, s=S_EARTH, albedo=ALBEDO_EARTH):
    """All energy flows of the one-layer model (W/m2) and the three balance residuals."""
    asr = absorbed_solar(s, albedo)
    g = SIGMA * surface_temperature(eps, s, albedo) ** 4
    a = SIGMA * layer_temperature(eps, s, albedo) ** 4
    f = {"solar_absorbed": asr, "ground": g, "through_window": (1.0 - eps) * g,
         "layer_up": eps * a, "back_radiation": eps * a}
    f["olr"] = f["through_window"] + f["layer_up"]                    # outgoing longwave radiation
    f["toa_residual"] = asr - f["olr"]
    f["layer_residual"] = eps * g - f["layer_up"] - f["back_radiation"]
    f["surface_residual"] = asr + f["back_radiation"] - g
    return f


def eps_for_surface(t_surface, s=S_EARTH, albedo=ALBEDO_EARTH):
    """Invert: the eps that gives the requested surface temperature (K)."""
    ratio = (bare_temperature(s, albedo) / t_surface) ** 4
    eps = 2.0 * (1.0 - ratio)
    if not 0.0 <= eps <= 1.0:
        raise ValueError("one layer cannot give this temperature (needs 0 <= eps <= 1)")
    return eps


# %% [markdown]
# ## Step 2: N opaque layers
# Stack N layers that each absorb all infrared (eps = 1). Each layer is warmer than the one
# above it, and the same bookkeeping gives Ts = Te (N + 1)^(1/4). Venus, with a thick CO2
# atmosphere, behaves like many such layers.

# %%
def n_layer_surface_temperature(n, s=S_EARTH, albedo=ALBEDO_EARTH):
    """Surface temperature (K) under n fully absorbing layers."""
    if n < 0 or int(n) != n:
        raise ValueError("n must be a whole number >= 0")
    return bare_temperature(s, albedo) * (n + 1) ** 0.25


def layers_needed(t_surface, s, albedo):
    """How many opaque layers (not rounded) give this surface temperature."""
    return (t_surface / bare_temperature(s, albedo)) ** 4 - 1.0


# %% [markdown]
# ## Step 3: radiative forcing
# Add a little more CO2 and eps rises. Before anything warms, less infrared escapes: the
# outgoing longwave radiation (OLR) at fixed temperatures falls. That deficit is the
# **radiative forcing** F (W/m2). In this model OLR = G (1 - eps / 2) at the old Ta = Ts / 2^(1/4),
# so F = G d(eps) / 2. Doubling CO2 gives about 3.7 W/m2 (IPCC estimate).

# %%
def instant_forcing(eps_old, eps_new, s=S_EARTH, albedo=ALBEDO_EARTH):
    """Drop in OLR (W/m2) right after eps changes, with the old temperatures held fixed."""
    g = SIGMA * surface_temperature(eps_old, s, albedo) ** 4
    return g * (eps_new - eps_old) / 2.0


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    eps_now = eps_for_surface(T_OBS)
    f = fluxes(eps_now)
    print(f"eps for 288 K = {eps_now:.3f}; layer temperature {layer_temperature(eps_now):.1f} K")
    for k in ("solar_absorbed", "ground", "through_window", "layer_up", "back_radiation", "olr"):
        print(f"  {k:15s} {f[k]:7.1f} W/m2")
    print(f"residuals: top {f['toa_residual']:.2e}, layer {f['layer_residual']:.2e}, surface {f['surface_residual']:.2e}")
    print(f"eps = 0: {surface_temperature(0):.1f} K;  eps = 1: {surface_temperature(1):.1f} K")
    d_eps = 3.7 / (f["ground"] / 2.0)
    print(f"a forcing of 3.7 W/m2 needs d(eps) = {d_eps:.4f}; new equilibrium {surface_temperature(eps_now + d_eps):.2f} K")
    print(f"Venus needs about {layers_needed(737.0, 2601.0, 0.77):.0f} opaque layers")

    # Figure 1: the energy flows of the one-layer model for today's Earth
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.3, 0.3), 9.4, 1.2, color="#8d6e63", alpha=0.6))
    ax.text(5, 0.75, f"surface  Ts = {surface_temperature(eps_now):.0f} K", ha="center", fontsize=10, color="white")
    ax.add_patch(plt.Rectangle((0.3, 5.0), 9.4, 1.0, color="#90caf9", alpha=0.7))
    ax.text(5.35, 5.5, f"atmosphere layer  eps = {eps_now:.2f},  Ta = {layer_temperature(eps_now):.0f} K", ha="left", va="center", fontsize=9.5)

    def arrow(x, y0, y1, colour, text, ty):
        ax.annotate("", xy=(x, y1), xytext=(x, y0), arrowprops=dict(arrowstyle="-|>", lw=2.2, color=colour))
        ax.text(x + 0.15, ty, text, fontsize=8.5, color=colour, ha="left", va="center")

    arrow(1.2, 9.3, 1.6, "#e9a23b", f"sunlight\nabsorbed\n{f['solar_absorbed']:.0f}", 7.8)
    arrow(3.2, 1.6, 4.9, "#d9534f", f"ground\n{f['ground']:.0f}", 3.2)
    arrow(5.0, 1.6, 9.3, "#d9534f", f"through the\nwindow\n{f['through_window']:.0f}", 7.8)
    arrow(7.0, 6.1, 9.3, "#1f6feb", f"layer up\n{f['layer_up']:.0f}", 7.8)
    arrow(8.4, 4.9, 1.6, "#1f6feb", f"back-\nradiation\n{f['back_radiation']:.0f}", 3.2)
    ax.text(5, 9.75, f"top of atmosphere: in {f['solar_absorbed']:.0f} = out {f['olr']:.0f} W/m2", ha="center", fontsize=10, weight="bold")
    ax.set_title("One-layer greenhouse model (W/m2, global average)", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "layer_fluxes.png", dpi=120)

    # Figure 2: surface temperature against eps, and against the number of opaque layers
    fig2, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.2))
    e = np.linspace(0, 1, 201)
    a1.plot(e, [surface_temperature(x) for x in e], color="#d9534f", lw=2.2, label="surface Ts")
    a1.plot(e, [layer_temperature(x) for x in e], color="#1f6feb", lw=2.2, label="layer Ta")
    a1.axhline(bare_temperature(), color="#e9a23b", ls="--", label=f"bare planet {bare_temperature():.0f} K")
    a1.plot([eps_now], [T_OBS], "ko")
    a1.annotate(f"today: eps = {eps_now:.2f}, 288 K", (eps_now, T_OBS), textcoords="offset points", xytext=(-150, 10))
    a1.set_xlabel("infrared absorptivity eps (no unit)")
    a1.set_ylabel("temperature (K)")
    a1.set_title("More infrared absorbed, warmer surface")
    a1.legend(fontsize=8, loc="lower right")
    a1.grid(alpha=0.3)
    n = np.arange(0, 9)
    a2.plot(n, [n_layer_surface_temperature(k) for k in n], "o-", color="#264653")
    for k in (0, 1, 4, 8):
        a2.annotate(f"{n_layer_surface_temperature(k):.0f} K", (k, n_layer_surface_temperature(k)), textcoords="offset points", xytext=(4, -14), fontsize=8)
    a2.set_xlabel("number of opaque layers N")
    a2.set_ylabel("surface temperature (K)")
    a2.set_title("Ts = Te (N + 1)^(1/4)")
    a2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "ts_vs_eps.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The one-layer model explains the 33 K and shows that more absorbing gas means a warmer
# surface. It says nothing about **how fast** the warming happens or about feedbacks such
# as water vapour. Session 3 steps the temperature forward in time with the ocean's heat
# capacity and a CO2 forcing.
