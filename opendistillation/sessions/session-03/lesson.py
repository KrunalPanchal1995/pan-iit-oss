"""Session 3 (Level 3): design an ethanol-water column with McCabe-Thiele and validate it.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: design the column, then check it
# **A. Real-world problem.** A small distillery has 100 kmol/h of fermented wash with 10 mol
# percent ethanol (about 22 percent by mass). It wants a top product of 80 mol percent ethanol and
# wants to throw away a bottom stream with only 2 mol percent. How many stages does the column
# need, on which stage should the feed enter, how much liquid must be sent back down (reflux),
# and how much steam does the reboiler use? Which reflux ratio is cheapest overall?
#
# **Plan.** (1) the real equilibrium curve from Session 2, (2) operating lines and the q-line,
# (3) step off stages (McCabe-Thiele), (4) validate against Fenske and the material balance,
# (5) minimum reflux and the pinch, (6) energy and cost: choosing the reflux ratio,
# (7) the failure case: trying to pass the azeotrope.
#
# **Model.** Equilibrium stages, constant molar overflow (equal molar latent heats), total
# condenser, partial reboiler counted as a stage, pressure 1 atm. A simplified teaching model.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
P_ATM = 760.0                                                    # mmHg
ANTOINE = {"ethanol": (8.20417, 1642.89, 230.300), "water": (8.07131, 1730.63, 233.426)}
VAN_LAAR = (1.6798, 0.9227)
LATENT = 40.0                                                    # kJ/mol, average molar latent heat


# %% [markdown]
# ## Step 1: the real equilibrium curve (from Session 2, vectorised)
# Same Antoine + van Laar model as Session 2. We tabulate y(x) and T(x) once on a fine grid, then
# interpolate. The inverse x(y) is needed for stepping; it is only defined below the azeotrope,
# where y > x.

# %%
def _psat(t, c):
    a, b, cc = ANTOINE[c]
    return 10.0 ** (a - b / (t + cc))


def bubble_curve(x, p=P_ATM):
    """Vectorised bubble point: arrays (T in degrees C, y) for an array of liquid fractions x."""
    x = np.atleast_1d(np.asarray(x, float))
    a12, a21 = VAN_LAAR
    x2 = 1.0 - x
    d = a12 * x + a21 * x2
    g1, g2 = np.exp(a12 * (a21 * x2 / d) ** 2), np.exp(a21 * (a12 * x / d) ** 2)
    lo, hi = np.full_like(x, 0.0), np.full_like(x, 150.0)
    for _ in range(60):
        t = 0.5 * (lo + hi)
        high = x * g1 * _psat(t, "ethanol") + x2 * g2 * _psat(t, "water") > p
        hi = np.where(high, t, hi)
        lo = np.where(high, lo, t)
    t = 0.5 * (lo + hi)
    return t, x * g1 * _psat(t, "ethanol") / p


_XG = np.linspace(0.0, 1.0, 4001)
_TG, _YG = bubble_curve(_XG)
X_AZEO = float(_XG[1:][np.argmax(_YG[1:] - _XG[1:] <= 0)])      # first grid point where y <= x


def y_eq(x):
    """Real ethanol-water vapour fraction in equilibrium with liquid x (1 atm)."""
    return np.interp(x, _XG, _YG)


def x_eq(y):
    """Liquid in equilibrium with vapour y, valid below the azeotrope."""
    m = _XG < X_AZEO
    return np.interp(y, _YG[m], _XG[m])


def t_bubble(x):
    """Bubble temperature (degrees C) of liquid x."""
    return np.interp(x, _XG, _TG)


def alpha_curve(alpha):
    """Equilibrium pair (y(x), x(y)) for a constant relative volatility, for validation."""
    return (lambda x: alpha * x / (1 + (alpha - 1) * x)), (lambda y: y / (alpha - (alpha - 1) * y))


# %% [markdown]
# ## Step 2: operating lines and the q-line
# With constant molar overflow the liquid L and vapour V flows are the same on every stage of a
# section. A balance around the top of the column (above stage n) gives the **rectifying line**
#
#     y = R/(R+1) x + xD/(R+1)          (R = L/D, the reflux ratio)
#
# and around the bottom the **stripping line** y = (L'/V') x - (B/V') xB with L' = L + qF and
# V' = V - (1-q)F. q is the liquid fraction of the feed (q = 1 for liquid at its boiling point).
# The two lines cross on the **q-line** y = q/(q-1) x - zF/(q-1) (a vertical line x = zF if q = 1).

# %%
def column_flows(z_feed, x_top, x_bottom, reflux, feed=100.0, q=1.0):
    """Flows (same unit as feed, e.g. kmol/h) for a column with constant molar overflow."""
    if not (0 < x_bottom < z_feed < x_top < 1):
        raise ValueError("need 0 < xB < zF < xD < 1")
    if reflux <= 0:
        raise ValueError("reflux ratio must be positive")
    d = feed * (z_feed - x_bottom) / (x_top - x_bottom)
    b = feed - d
    l = reflux * d
    v = l + d
    lb = l + q * feed
    vb = v - (1.0 - q) * feed
    return {"D": d, "B": b, "L": l, "V": v, "Lb": lb, "Vb": vb}


def feed_intersection(z_feed, x_top, reflux, q=1.0):
    """x where the rectifying line meets the q-line."""
    if abs(q - 1.0) < 1e-12:
        return z_feed
    return (z_feed / (q - 1.0) + x_top / (reflux + 1.0)) / (q / (q - 1.0) - reflux / (reflux + 1.0))


# %% [markdown]
# ## Step 3: step off the stages (McCabe-Thiele)
# Start at the top: the vapour leaving stage 1 is condensed totally, so y1 = xD.
# Then repeat: the liquid on the stage is in equilibrium with its vapour, x = x_eq(y) (a
# horizontal step on the x-y diagram); the vapour from the stage below follows from the operating
# line (a vertical step). Switch to the stripping line once x passes the feed intersection: that
# stage is the **feed stage**. Stop when x <= xB; the last stage is the reboiler.

# %%
def mccabe_thiele(z_feed, x_top, x_bottom, reflux, q=1.0, eq=None, max_stages=200):
    """Step off stages from the top. Returns dict with lists x, y, the number of stages,
    the feed stage and the flows. eq = (y_of_x, x_of_y); default is the real curve."""
    yf, xf = eq if eq is not None else (y_eq, x_eq)
    if eq is None and x_top >= X_AZEO:
        raise ValueError(f"xD = {x_top} is at or beyond the azeotrope (x = {X_AZEO:.3f}); no column can reach it")
    fl = column_flows(z_feed, x_top, x_bottom, reflux, 100.0, q)
    xi = feed_intersection(z_feed, x_top, reflux, q)
    yi = reflux / (reflux + 1) * xi + x_top / (reflux + 1)
    if yi >= yf(xi) - 1e-12:
        raise ValueError("reflux is at or below the minimum: the operating lines touch the equilibrium curve")
    xs, ys = [], []
    y = x_top
    feed_stage = None
    for n in range(1, max_stages + 1):
        x = float(xf(y))
        xs.append(x)
        ys.append(float(y))
        if x <= x_bottom:
            break
        if feed_stage is None and x <= xi:
            feed_stage = n + 1                 # the next stage down uses the stripping line
        if feed_stage is None:
            y_next = reflux / (reflux + 1) * x + x_top / (reflux + 1)
        else:
            y_next = fl["Lb"] / fl["Vb"] * x - fl["B"] * x_bottom / fl["Vb"]
        y = y_next
    else:
        raise ValueError("did not reach xB: pinched (too little reflux or too pure a target)")
    if feed_stage is None or feed_stage > len(xs):
        feed_stage = len(xs)
    return {"x": np.array(xs), "y": np.array(ys), "stages": len(xs), "feed_stage": feed_stage,
            "flows": fl, "x_feed": xi}


def total_reflux_stages(x_top, x_bottom, eq=None):
    """Stages at total reflux (operating line y = x), stepping from the top."""
    yf, xf = eq if eq is not None else (y_eq, x_eq)
    y, n = x_top, 0
    while n < 500:
        x = float(xf(y))
        n += 1
        if x <= x_bottom:
            return n
        y = x
    raise ValueError("no convergence")


def fenske(x_top, x_bottom, alpha):
    """Fenske minimum stages for constant alpha (Session 1)."""
    return np.log((x_top / (1 - x_top)) / (x_bottom / (1 - x_bottom))) / np.log(alpha)


# %% [markdown]
# ## Step 4: minimum reflux and the pinch
# Lower the reflux and the rectifying line swings up towards the equilibrium curve. When it
# first touches it, the steps become infinitely small there: a **pinch**, infinite stages. For a
# saturated-liquid feed, the touching point is often the feed point (x = zF, y = y_eq(zF)), which
# gives the hand formula Rmin = (xD - y*) / (y* - zF). For ethanol-water the curve bulges
# towards y = x near the top, so for high xD the line touches tangentially above the feed: a
# **tangent pinch** with a higher Rmin. We take the largest slope (xD - y)/(xD - x) over all x
# between zF and xD, which covers both cases.

# %%
def min_reflux(z_feed, x_top, q=1.0):
    """Minimum reflux ratio and the pinch point x (saturated liquid feed, q = 1, assumed)."""
    if abs(q - 1.0) > 1e-12:
        raise ValueError("this teaching version handles q = 1 only")
    if x_top >= X_AZEO:
        raise ValueError("xD beyond the azeotrope")
    xs = np.linspace(z_feed, x_top - 1e-4, 20001)
    slope = (x_top - y_eq(xs)) / (x_top - xs)
    k = int(np.argmax(slope))
    s = slope[k]
    return float(s / (1.0 - s)), float(xs[k])


# %% [markdown]
# ## Step 5: energy and cost
# The reboiler must boil V' mol of vapour per hour: duty Q_R = V' x latent heat (about 40 kJ/mol
# for both ethanol and water, which is why constant molar overflow works). More reflux means
# fewer stages (cheaper column) but more vapour (dearer steam). Illustrative costs:
# one real tray costs 2.0 lakh rupees per year (annualised build cost) and one kW of reboiler
# heat costs 0.24 lakh rupees per year (about 2.7 rupees per kWh of steam heat, 8760 hours).

# %%
def reboiler_duty_kw(flows):
    """Reboiler duty in kW for flows in kmol/h: V' (kmol/h) x 40 kJ/mol x 1000 mol/kmol / 3600 s/h."""
    return flows["Vb"] * LATENT * 1000.0 / 3600.0


def annual_cost(stages, duty_kw, tray_efficiency=0.6, c_tray=2.0, c_kw=0.24):
    """Illustrative annual cost in lakh rupees: real trays x c_tray + duty (kW) x c_kw.
    The reboiler is an equilibrium stage but not a tray."""
    trays = int(np.ceil((stages - 1) / tray_efficiency))
    return trays * c_tray + duty_kw * c_kw, trays


def design(z_feed, x_top, x_bottom, factor, feed=100.0, tray_efficiency=0.6):
    """Design at R = factor x Rmin: stages, feed stage, trays, duty and cost."""
    rmin, _ = min_reflux(z_feed, x_top)
    r = factor * rmin
    mt = mccabe_thiele(z_feed, x_top, x_bottom, r)
    fl = column_flows(z_feed, x_top, x_bottom, r, feed)
    duty = reboiler_duty_kw(fl)
    cost, trays = annual_cost(mt["stages"], duty, tray_efficiency)
    return {"R": r, "Rmin": rmin, "stages": mt["stages"], "feed_stage": mt["feed_stage"],
            "trays": trays, "duty_kw": duty, "cost": cost, "flows": fl}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    zF, xD, xB = 0.10, 0.80, 0.02
    print(f"model azeotrope at x = {X_AZEO:.3f}")

    # validation 1: constant alpha, total reflux stepping against Fenske
    for a in (2.5, 4.0):
        n = total_reflux_stages(xD, xB, alpha_curve(a))
        print(f"alpha = {a}: stepped stages at total reflux {n}, Fenske {fenske(xD, xB, a):.2f}")

    rmin, xp = min_reflux(zF, xD)
    ystar = float(y_eq(zF))
    print(f"Rmin = {rmin:.3f} (pinch at x = {xp:.3f}); hand: (0.80 - {ystar:.3f}) / ({ystar:.3f} - 0.10) = {(xD - ystar) / (ystar - zF):.3f}")
    nmin = total_reflux_stages(xD, xB)
    print(f"minimum stages at total reflux (real curve): {nmin}")
    d = design(zF, xD, xB, 1.5)
    print(f"design R = 1.5 Rmin = {d['R']:.3f}: {d['stages']} stages incl. reboiler, feed on stage {d['feed_stage']},"
          f" {d['trays']} real trays at 60 %, D = {d['flows']['D']:.2f} kmol/h, V' = {d['flows']['Vb']:.2f} kmol/h,"
          f" reboiler {d['duty_kw']:.0f} kW")
    try:
        mccabe_thiele(zF, 0.92, xB, 5.0)
    except ValueError as e:
        print("failure case xD = 0.92:", e)
    rmin_hi, xp_hi = min_reflux(zF, 0.86)
    ys_hi = float(y_eq(zF))
    print(f"xD = 0.86: Rmin = {rmin_hi:.3f} at x = {xp_hi:.3f} (tangent pinch); feed-pinch formula would give {(0.86 - ys_hi) / (ys_hi - zF):.3f}")

    # Figure 1: the McCabe-Thiele diagram for the design
    mt = mccabe_thiele(zF, xD, xB, d["R"])
    fl = mt["flows"]
    x = np.linspace(0, 1, 401)
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    ax.plot(x, y_eq(x), color="#2a9d8f", label="equilibrium (van Laar, 1 atm)")
    ax.plot([0, 1], [0, 1], "k", lw=1)
    xr = np.linspace(mt["x_feed"], xD, 50)
    ax.plot(xr, d["R"] / (d["R"] + 1) * xr + xD / (d["R"] + 1), color="#264653", label=f"rectifying line, R = {d['R']:.2f}")
    xs_ = np.linspace(xB, mt["x_feed"], 50)
    ax.plot(xs_, fl["Lb"] / fl["Vb"] * xs_ - fl["B"] * xB / fl["Vb"], color="#e9a23b", label="stripping line")
    ax.axvline(zF, color="#888888", ls=":", lw=1, label="q-line (saturated liquid feed)")
    px, py = [xD], [xD]
    for i in range(mt["stages"]):
        px += [mt["x"][i]]
        py += [mt["y"][i]]
        if i + 1 < mt["stages"]:
            px += [mt["x"][i]]
            py += [mt["y"][i + 1]]
    ax.plot(px, py, color="#d9534f", lw=1.2, label=f"{mt['stages']} stages, feed on stage {mt['feed_stage']}")
    ax.set_xlabel("ethanol in liquid, x (mole fraction)")
    ax.set_ylabel("ethanol in vapour, y (mole fraction)")
    ax.set_title("McCabe-Thiele: 10 % wash to 80 % ethanol")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "mccabe_thiele.png", dpi=120)

    # Figure 2: stages and energy against reflux, and the cost optimum
    factors = np.round(np.arange(1.05, 3.01, 0.05), 2)
    rows = [design(zF, xD, xB, f) for f in factors]
    best = min(rows, key=lambda r: r["cost"])
    print(f"cheapest: R = {best['R']:.3f} ({best['R'] / rmin:.2f} x Rmin), {best['stages']} stages, {best['trays']} trays,"
          f" {best['duty_kw']:.0f} kW, cost {best['cost']:.1f} lakh rupees per year")
    fig2, (axl, axr) = plt.subplots(1, 2, figsize=(10, 4.2))
    rs = [r["R"] for r in rows]
    axl.step(rs, [r["stages"] for r in rows], where="mid", color="#264653", label="theoretical stages")
    axl.axhline(nmin, color="#264653", ls=":", lw=1)
    axl.axvline(rmin, color="#d9534f", ls="--", lw=1)
    axl.text(rmin * 1.02, max(r["stages"] for r in rows) * 0.9, f"Rmin = {rmin:.2f}", color="#d9534f", fontsize=8)
    axl.text(rs[-1], nmin + 0.4, f"N_min = {nmin}", ha="right", fontsize=8)
    axl.set_xlabel("reflux ratio R = L/D (no unit)")
    axl.set_ylabel("theoretical stages")
    axl2 = axl.twinx()
    axl2.plot(rs, [r["duty_kw"] for r in rows], color="#e9a23b", label="reboiler duty")
    axl2.set_ylabel("reboiler duty (kW)", color="#e9a23b")
    axl.set_title("More reflux: fewer stages, more steam")
    axr.plot(rs, [r["cost"] for r in rows], color="#2a9d8f")
    axr.plot([best["R"]], [best["cost"]], "o", color="#d9534f")
    axr.annotate(f"cheapest R = {best['R']:.2f}", (best["R"], best["cost"]), textcoords="offset points", xytext=(8, 10), fontsize=8)
    axr.set_xlabel("reflux ratio R = L/D (no unit)")
    axr.set_ylabel("annual cost (lakh rupees, illustrative)")
    axr.set_title("Trays + steam: an optimum reflux")
    axr.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "reflux_tradeoff.png", dpi=120)

    # Figure 3 (Target figure): column picture with tray temperatures and compositions
    temps = t_bubble(mt["x"])
    fig3, (axc, axp) = plt.subplots(1, 2, figsize=(10, 5.6), gridspec_kw={"width_ratios": [1, 1.6]})
    n = mt["stages"]
    cmap = plt.get_cmap("coolwarm")
    for i in range(n):
        frac = (temps[i] - 78) / (100 - 78)
        axc.add_patch(plt.Rectangle((0.3, n - 1 - i), 0.4, 0.85, color=cmap(frac)))
        axc.text(0.75, n - 1 - i + 0.4, f"{i + 1}: x = {mt['x'][i]:.3f}, {temps[i]:.1f} C", va="center", fontsize=7)
    axc.annotate("feed 100 kmol/h\nzF = 0.10", xy=(0.3, n - mt["feed_stage"] + 0.4), xytext=(-0.55, n - mt["feed_stage"] + 0.4),
                 arrowprops=dict(arrowstyle="->"), fontsize=8, va="center")
    axc.text(0.5, n + 0.3, f"distillate D = {fl['D']:.1f} kmol/h, xD = 0.80", ha="center", fontsize=8)
    axc.text(0.5, -0.7, f"bottoms B = {fl['B']:.1f} kmol/h, xB = 0.02 (reboiler {d['duty_kw']:.0f} kW)", ha="center", fontsize=8)
    axc.set_xlim(-0.6, 1.6)
    axc.set_ylim(-1.2, n + 0.9)
    axc.axis("off")
    axc.set_title("The designed column (stage 1 = top)")
    st = np.arange(1, n + 1)
    axp.plot(temps, st, "o-", color="#d9534f", label="temperature")
    axp.invert_yaxis()
    axp.set_xlabel("tray temperature (degrees C)", color="#d9534f")
    axp.set_ylabel("stage number (1 = top)")
    axp.axhline(mt["feed_stage"], color="#888888", ls=":", lw=1)
    axp2 = axp.twiny()
    axp2.plot(mt["x"], st, "s-", color="#264653", label="liquid x")
    axp2.plot(mt["y"], st, "^-", color="#2a9d8f", label="vapour y")
    axp2.set_xlabel("ethanol mole fraction")
    axp2.legend(fontsize=8, loc="lower right")
    axp.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "column_profile.png", dpi=120)

    print("sensitivity of stages to xB (R = 1.5 Rmin):", [design(zF, xD, b, 1.5)["stages"] for b in (0.05, 0.02, 0.01, 0.005)])
    print("sensitivity of stages to xD (R = 1.5 Rmin):", [design(zF, t, xB, 1.5)["stages"] for t in (0.70, 0.75, 0.80, 0.85)])
    print("Rmin against feed composition:", [round(min_reflux(z, xD)[0], 3) for z in (0.05, 0.10, 0.20)])

# %% [markdown]
# ## Where this stops
# Constant molar overflow, ideal stages, a fixed tray efficiency and a steady state are strong
# assumptions. Real columns need energy balances on each tray, tray hydraulics and a start-up
# that takes time. That is the road to the Target: see `promo/roadmap.md`.
