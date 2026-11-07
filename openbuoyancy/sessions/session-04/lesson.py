"""Session 4 (Level 3): a liquid with a free surface in a tank takes away stability.

Educational 2D model only: not a naval architecture tool.
Run:  python start.py 4
"""
# %% [markdown]
# # Session 4: sloshing liquid and the lost metacentric height
# **A. Real-world problem.** In Session 3 the 180 t barge (60 t empty, 120 t of cargo with its centre
# 2.5 m above the keel) had a healthy GM of 0.75 m. Now the 120 t is a liquid in a tank 10 m long and
# 5 m wide. When the barge heels, a solid cargo stays where it is, but a liquid with a free surface
# flows to the low side, and the barge feels it. How much GM does the tank take away, why does a
# *wider* tank hurt so much more, and how does a divider help?
#
# **Plan.** (1) the free-surface correction by formula, (2) check it against the exact geometry of the
# heeled tank, (3) what a tank divider does (longitudinal and transverse), (4) the full GZ curve and the
# angle of loll, (5) the widest tank that keeps a safe GM.
#
# *Educational 2D model: still water, slow heel, a rectangular tank on the centre line. Never use it for a real vessel.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
RHO = 1000.0            # fresh water, kg/m^3 (the water the barge floats in)
LEN, BEAM, DEPTH = 20.0, 6.0, 2.5      # barge length, beam and hull depth, m
LIGHT, KG_LIGHT = 60000.0, 1.0         # empty barge: mass kg, centre of gravity above keel m


# %% [markdown]
# ## Step 0: the barge from Session 3
# Copied unchanged from Session 3 so that this file runs on its own: the box formulas, the exact
# wet-section geometry (`wet_polygon`: clip the heeled hull at the water line that keeps the
# submerged area) and `righting_arm`.

# %%
def draft_for(mass, beam=BEAM, length=LEN, rho=RHO):
    return mass / (rho * length * beam)


# %%
def kb_box(draft):
    return draft / 2.0


# %%
def bm_box(draft, beam=BEAM):
    return beam ** 2 / (12.0 * draft)


# %%
def kg_loaded(cargo, cargo_h, light=LIGHT, kg_light=KG_LIGHT):
    """Centre of gravity (m above keel) of barge plus cargo (kg) whose own centre is at height cargo_h."""
    return (light * kg_light + cargo * cargo_h) / (light + cargo)


# %%
def gm_loaded(cargo, cargo_h, beam=BEAM, length=LEN, light=LIGHT, kg_light=KG_LIGHT):
    d = draft_for(light + cargo, beam, length)
    return kb_box(d) + bm_box(d, beam) - kg_loaded(cargo, cargo_h, light, kg_light)


# %%
def clip_below(poly, level):
    """Part of a polygon (list of (y, z) points) with z <= level (Sutherland-Hodgman)."""
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        pin, qin = p[1] <= level, q[1] <= level
        if pin:
            out.append(p)
        if pin != qin:
            t = (level - p[1]) / (q[1] - p[1])
            out.append((p[0] + t * (q[0] - p[0]), level))
    return out


# %%
def area_centroid(poly):
    if len(poly) < 3:
        return 0.0, 0.0, 0.0
    y = np.array([p[0] for p in poly])
    z = np.array([p[1] for p in poly])
    y2, z2 = np.roll(y, -1), np.roll(z, -1)
    cr = y * z2 - y2 * z
    a = cr.sum() / 2.0
    if abs(a) < 1e-14:
        return 0.0, 0.0, 0.0
    return a, ((y + y2) * cr).sum() / (6 * a), ((z + z2) * cr).sum() / (6 * a)


# %%
def wet_polygon(phi, area, hull):
    """Any hull: heel angle phi (radians), wet area (m^2) -> (waterline height, y_B, z_B).

    `hull` is the upright cross-section as a list of (y, z) corners (y sideways, z up, keel at
    z = 0). The hull is turned about the origin, the water line is found by bisection so the wet
    part has the wanted area, and the centroid of the wet part is the centre of buoyancy B.
    Coordinates are in the water frame."""
    total = abs(area_centroid(list(hull))[0])
    if area >= total:
        raise ValueError("the hull would be fully submerged")
    c, s = np.cos(phi), np.sin(phi)
    world = [(y * c - z * s, y * s + z * c) for y, z in hull]
    lo = min(p[1] for p in world)
    hi = max(p[1] for p in world)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        a = area_centroid(clip_below(world, mid))[0]
        if a < area:
            lo = mid
        else:
            hi = mid
    level = 0.5 * (lo + hi)
    a, yb, zb = area_centroid(clip_below(world, level))
    return level, yb, zb


# %%
def rectangle_hull(beam=BEAM, depth=DEPTH):
    """Box section, keel in the middle at z = 0 (counter-clockwise)."""
    return [(-beam / 2, 0.0), (beam / 2, 0.0), (beam / 2, depth), (-beam / 2, depth)]


# %%
def wet_section(phi, area, beam=BEAM, depth=DEPTH):
    """Heel angle phi (radians), wet cross-section area (m^2) -> (waterline height, y_B, z_B).
    The box is the special case of `wet_polygon` with a rectangle."""
    if area >= beam * depth:
        raise ValueError("the box would be fully submerged")
    return wet_polygon(phi, area, rectangle_hull(beam, depth))


# %%
def righting_arm(phi, mass, kg, beam=BEAM, length=LEN, depth=DEPTH, rho=RHO, shift=0.0):
    """GZ (m) at heel angle phi (radians). `shift` moves G sideways in the hull by that many metres (cargo shift)."""
    area = mass / (rho * length)
    level, yb, zb = wet_section(phi, area, beam, depth)
    yg = -kg * np.sin(phi) + shift * np.cos(phi)
    return yg - yb


# %% [markdown]
# ## Step 1: the tank and the free-surface correction
# A tank is a box of length l (along the barge), width w (across it) and height H, on the centre line,
# with its floor at height z0 above the keel. It holds a liquid of mass m_l and density rho_l, so the
# liquid is h = m_l / (rho_l l w) deep and its centre of gravity is at z0 + h/2.
#
# When the barge heels by a small angle phi the liquid surface stays level, so the liquid wedge moves to
# the low side: the liquid's centre of gravity shifts sideways by i phi / v, where i = l w^3 / 12 is the
# second moment of the free surface and v the liquid volume. That shifts the barge's weight sideways
# exactly as if G had risen by
#
#     FSC = rho_l i / m = rho_l l w^3 / (12 m)       (m = total mass of the barge, m = rho V)
#
# and the effective metacentric height is **GM_eff = GM_solid - FSC**. Two things to notice: FSC does not
# depend on how full the tank is (as long as the surface does not touch the roof or floor), and it grows
# with the cube of the width. A full tank has no free surface: FSC = 0.

# %%
def make_tank(length, width, liquid_mass, cg, rho_l=RHO, height=4.0, n_long=1, n_trans=1):
    """A rectangular tank on the centre line, filled with liquid_mass (kg) so that the liquid's own centre of
    gravity is `cg` m above the keel. n_long longitudinal dividers split the width, n_trans transverse
    bulkheads split the length (each compartment gets an equal share of the liquid)."""
    if min(length, width, liquid_mass, rho_l, height) <= 0 or n_long < 1 or n_trans < 1:
        raise ValueError("lengths, mass, density and the number of compartments must be positive")
    depth = liquid_mass / (rho_l * length * width)
    if depth > height + 1e-12:
        raise ValueError("the liquid does not fit in the tank")
    return {"length": length, "width": width, "mass": liquid_mass, "cg": cg, "rho": rho_l, "height": height,
            "depth": depth, "z0": cg - depth / 2.0, "n_long": int(n_long), "n_trans": int(n_trans)}


def is_full(tank):
    return tank["depth"] >= tank["height"] - 1e-9


def tank_inertia(tank):
    """Total second moment of the free surface(s), m^4: n_long * n_trans compartments of l/n_trans by w/n_long."""
    nl, nt = tank["n_long"], tank["n_trans"]
    return nl * nt * (tank["length"] / nt) * (tank["width"] / nl) ** 3 / 12.0


def free_surface_correction(tank, total_mass):
    """FSC = rho_l i / m (m): the loss of metacentric height. Zero for a full tank."""
    return 0.0 if is_full(tank) else tank["rho"] * tank_inertia(tank) / total_mass


def gm_effective(tank, light=LIGHT, kg_light=KG_LIGHT):
    """GM with the liquid treated as a solid cargo, minus the free-surface correction. The liquid is the whole cargo."""
    solid = gm_loaded(tank["mass"], tank["cg"], light=light, kg_light=kg_light)
    return solid - free_surface_correction(tank, light + tank["mass"])


# %% [markdown]
# ## Step 2: the exact geometry of the heeled tank
# Check the formula the same way as in Session 3. Turn the tank rectangle by the heel angle, find the level
# water line that keeps the liquid's area, and take the centroid of the liquid: that is the liquid's centre of
# gravity (a free surface in a *tank* behaves exactly like the water around a hull). The tank is fixed in the
# hull, so its floor centre sits at height z0 on the hull's centre line. Then
#
#     y_G = [ m_dry y_dry + m_liquid y_liquid ] / m_total,      GZ = y_G - y_B,
#
# with the barge's own wet section for y_B. `frozen=True` keeps the liquid as a solid lump at its centre of
# gravity, which is what Session 3 assumed.

# %%
def liquid_centroid(phi, tank):
    """Sideways position y (m, water frame) and height of the liquid's centre of gravity at heel phi, all compartments."""
    nl, nt = tank["n_long"], tank["n_trans"]
    wc = tank["width"] / nl
    area = tank["mass"] / (tank["rho"] * tank["length"])        # liquid cross-section of the whole tank, m^2
    area_c = area / nl                                           # one compartment (each gets an equal share)
    c, s = np.cos(phi), np.sin(phi)
    ys, zs = [], []
    for j in range(nl):
        y_c = -tank["width"] / 2 + wc * (j + 0.5)               # compartment centre in the hull
        if is_full(tank):
            yl, zl = -tank["height"] / 2.0 * s, tank["height"] / 2.0 * c        # a full tank: the centre of the box, turned with it
        else:
            _, yl, zl = wet_polygon(phi, area_c, rectangle_hull(wc, tank["height"]))
        ys.append(y_c * c - tank["z0"] * s + yl)
        zs.append(y_c * s + tank["z0"] * c + zl)
    return float(np.mean(ys)), float(np.mean(zs))


def righting_arm_tank(phi, tank, light=LIGHT, kg_light=KG_LIGHT, frozen=False, beam=BEAM, length=LEN, depth=DEPTH, rho=RHO):
    """GZ (m) of the barge carrying the tank at heel phi; `frozen` treats the liquid as a solid lump."""
    m_tot = light + tank["mass"]
    level, yb, zb = wet_section(phi, m_tot / (rho * length), beam, depth)
    y_dry = -kg_light * np.sin(phi)
    y_liq = -tank["cg"] * np.sin(phi) if frozen else liquid_centroid(phi, tank)[0]
    yg = (light * y_dry + tank["mass"] * y_liq) / m_tot
    return yg - yb


def effective_gm_exact(tank, phi=np.radians(0.5), **kw):
    """GM_eff from the exact geometry: GZ / sin(phi) at a small heel angle."""
    return righting_arm_tank(phi, tank, **kw) / np.sin(phi)


def free_surface_moment_exact(tank, phi=np.radians(0.5)):
    """Free-surface moment (kg m) from the exact geometry: m_l (y_frozen - y_free) / sin(phi), the sideways shift of the
    liquid's weight caused by the free surface. Theory says rho_l i."""
    y_free = liquid_centroid(phi, tank)[0]
    y_frozen = -tank["cg"] * np.sin(phi)
    return tank["mass"] * (y_frozen - y_free) / np.sin(phi)


# %% [markdown]
# ## Step 3: dividers
# A longitudinal divider (along the barge) splits the width. With n equal longitudinal compartments each has
# width w / n, so each has i = l (w/n)^3 / 12 and together i / n^2: **two compartments cut the loss to a quarter,
# three to a ninth**. A transverse bulkhead (across the barge) splits the length instead; the compartments
# are shorter but each is still w wide, and the sum of the l_j w^3 / 12 is unchanged: **a transverse bulkhead
# does not help**.

# %%
def divided_inertia(length, width, n_long=1, n_trans=1):
    """Total i for a tank split by n_long longitudinal dividers and n_trans transverse bulkheads."""
    return n_long * n_trans * (length / n_trans) * (width / n_long) ** 3 / 12.0


# %% [markdown]
# ## Step 4: the GZ curve and the angle of loll
# For a negative GM_eff the upright barge is unstable: it lolls over to the angle at which GZ returns to zero,
# as in Session 3. With a free surface the exact curve is not the straight line GM_eff sin(phi): for the
# 10 x 5 m tank the exact GZ is 0.0336 m at 10 degrees against 0.0297 m from the line, and the loss gets worse at
# large angles. The formula is a small-angle result: it is exact in the limit of zero heel, and the liquid is a clean wedge
# only up to the angle where the surface reaches the roof or the floor (tan phi = 2 (H - h) / w or 2 h / w).

# %%
def gz_curve_tank(phis, tank, frozen=False, **kw):
    return np.array([righting_arm_tank(p, tank, frozen=frozen, **kw) for p in phis])


def angle_of_loll_tank(tank, max_deg=60.0, **kw):
    """Smallest positive heel angle (radians) where GZ returns to zero from below (GM_eff < 0), or nan."""
    grid = np.linspace(np.radians(0.5), np.radians(max_deg), 120)
    vals = [righting_arm_tank(p, tank, **kw) for p in grid]
    for a, b, fa, fb in zip(grid[:-1], grid[1:], vals[:-1], vals[1:]):
        if fa < 0 <= fb:
            lo, hi = a, b
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                if righting_arm_tank(mid, tank, **kw) < 0:
                    lo = mid
                else:
                    hi = mid
            return 0.5 * (lo + hi)
    return float("nan")


def vanishing_angle_deg(tank, max_deg=80.0, frozen=False, **kw):
    """First heel angle (degrees) above 1 degree where GZ falls to zero (the end of the range of stability), or nan."""
    grid = np.radians(np.arange(1.0, max_deg + 0.5, 1.0))
    vals = [righting_arm_tank(p, tank, frozen=frozen, **kw) for p in grid]
    for a, b, fa, fb in zip(grid[:-1], grid[1:], vals[:-1], vals[1:]):
        if fa > 0 >= fb:
            lo, hi = a, b
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                if righting_arm_tank(mid, tank, frozen=frozen, **kw) > 0:
                    lo = mid
                else:
                    hi = mid
            return float(np.degrees(0.5 * (lo + hi)))
    return float("nan")


def surface_touches_deg(tank):
    """Heel angle (degrees) at which the liquid surface first reaches the roof or the floor of the tank at a wall:
    below it the liquid is a clean wedge of angle phi, above it the shape of the liquid changes."""
    wc = tank["width"] / tank["n_long"]
    return float(np.degrees(np.arctan(2.0 * min(tank["depth"], tank["height"] - tank["depth"]) / wc)))


# %% [markdown]
# ## Step 5: design: the widest tank
# The barge is 6 m wide. Rearranged, the correction formula gives the largest tank width that still leaves a
# chosen GM_min: i_max = (GM_solid - GM_min) m / rho_l and, for n longitudinal compartments of width w / n,
# w = n (12 i_max / (n l))^(1/3). The function below returns that width for one tank
# with n_long compartments (length l, no transverse bulkheads).

# %%
def max_tank_width(length, liquid_mass, cg, gm_min=0.15, n_long=1, rho_l=RHO, light=LIGHT, kg_light=KG_LIGHT):
    """Widest tank (m) whose effective GM stays at or above gm_min, with n_long equal longitudinal compartments."""
    solid = gm_loaded(liquid_mass, cg, light=light, kg_light=kg_light)
    i_max = (solid - gm_min) * (light + liquid_mass) / rho_l
    if i_max <= 0:
        return 0.0
    return n_long * (12.0 * i_max / (n_long * length)) ** (1.0 / 3.0)


# %% [markdown]
# ## See it
# Figure 1: the heeled section with the liquid surface level and the frozen liquid for comparison. Figure 2: the
# GZ curve with the tank (free surface), with the liquid frozen, and the small-angle line GM_eff sin(phi).
# Figure 3: effective GM against tank width for one, two and three compartments, and the free-surface moment
# against fill (theory against exact geometry).

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    BLUE, ORANGE, MAGENTA = "#0072b2", "#c86a00", "#d81b60"
    tank = make_tank(10.0, 5.0, 120000.0, 2.5)
    m_tot = LIGHT + tank["mass"]
    solid = gm_loaded(tank["mass"], tank["cg"])
    fsc = free_surface_correction(tank, m_tot)
    print(f"solid cargo: GM {solid:.4f} m;  tank 10 x 5 m: i = {tank_inertia(tank):.2f} m^4, FSC = {fsc:.4f} m, GM_eff = {gm_effective(tank):.4f} m")
    print(f"exact geometry: GM_eff = {effective_gm_exact(tank):.4f} m;  liquid depth {tank['depth']:.2f} m, the liquid stays a clean wedge up to {surface_touches_deg(tank):.1f} deg")
    for deg in (5, 10, 20, 30):
        p = np.radians(deg)
        print(f"heel {deg:2d} deg: GZ solid {righting_arm_tank(p, tank, frozen=True):.4f}, free surface {righting_arm_tank(p, tank):.4f}, GM_eff sin(phi) {gm_effective(tank) * np.sin(p):.4f}")
    for nl in (1, 2, 3):
        tk = make_tank(10.0, 5.0, 120000.0, 2.5, n_long=nl)
        print(f"{nl} longitudinal compartment(s): i = {tank_inertia(tk):.2f}, GM_eff = {gm_effective(tk):.4f}, exact {effective_gm_exact(tk):.4f}")
    tk = make_tank(10.0, 5.0, 120000.0, 2.5, n_trans=2)
    print(f"2 transverse bulkheads: i = {tank_inertia(tk):.2f}, GM_eff = {gm_effective(tk):.4f}")
    wide = make_tank(10.0, 5.8, 120000.0, 2.5)
    print(f"wide tank 10 x 5.8: GM_eff = {gm_effective(wide):+.4f}, angle of loll {np.degrees(angle_of_loll_tank(wide)):.1f} deg")
    for nl in (1, 2, 3, 4):
        print(f"  {nl} compartments: GM_eff = {gm_effective(make_tank(10.0, 5.8, 120000.0, 2.5, n_long=nl)):+.3f}")
    print("widest tank (10 m long) for GM >= 0.15:", [round(max_tank_width(10.0, 120000.0, 2.5, 0.15, n), 3) for n in (1, 2, 3)])

    # figure 1: heeled sections, free versus frozen liquid
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.3))
    phi = np.radians(10)
    c, s = np.cos(phi), np.sin(phi)
    level, yb, zb = wet_section(phi, m_tot / (RHO * LEN))
    for ax, tk, title in ((axs[0], tank, "tank 10 x 5 m, 10 degrees"), (axs[1], wide, "tank 10 x 5.8 m (no divider)")):
        hull = np.array(rectangle_hull() + [rectangle_hull()[0]])
        ax.plot(hull[:, 0] * c - hull[:, 1] * s, hull[:, 0] * s + hull[:, 1] * c - level, "k-")
        tkr = np.array(rectangle_hull(tk["width"], tk["height"]) + [rectangle_hull(tk["width"], tk["height"])[0]])
        tkr_w = np.c_[tkr[:, 0] * c - (tkr[:, 1] + tk["z0"]) * s, tkr[:, 0] * s + (tkr[:, 1] + tk["z0"]) * c - level]
        ax.plot(tkr_w[:, 0], tkr_w[:, 1], color="0.4")
        area = tk["mass"] / (tk["rho"] * tk["length"])
        lv, _, _ = wet_polygon(phi, area, rectangle_hull(tk["width"], tk["height"]))
        z_surf = lv + tk["z0"] * c - level                      # tank frame water line, shifted to the barge water frame
        y_l, z_l = liquid_centroid(phi, tk)
        ax.axhline(0, color=BLUE, lw=1)
        liq = clip_below([(y * c - z * s, y * s + z * c) for y, z in rectangle_hull(tk["width"], tk["height"])], lv)
        ax.fill([q[0] - tk["z0"] * s for q in liq], [q[1] + tk["z0"] * c - level for q in liq], color=BLUE, alpha=0.3, lw=0)
        ax.plot(-tk["cg"] * s, tk["cg"] * c - level, "o", color=ORANGE, label="liquid as a solid lump")
        ax.plot(y_l, z_l - level, "o", color=MAGENTA, label="liquid with a free surface")
        ax.set_title(title, fontsize=10)
        ax.set_aspect("equal")
        ax.set_xlabel("sideways position (m)")
        ax.legend(fontsize=8, loc="upper left")
    axs[0].set_ylabel("height above the water line (m)")
    fig.tight_layout()
    fig.savefig(OUT / "heeled_tank.png", dpi=120)

    # figure 2: GZ curves
    phis = np.radians(np.arange(0, 41, 1.0))
    fig2, ax2 = plt.subplots(figsize=(6.6, 4.2))
    ax2.plot(np.degrees(phis), gz_curve_tank(phis, tank, frozen=True), color=ORANGE, label="liquid as a solid (GM 0.75 m)")
    ax2.plot(np.degrees(phis), gz_curve_tank(phis, tank), color=MAGENTA, lw=2, label="free surface, tank 10 x 5 m")
    ax2.plot(np.degrees(phis), gm_effective(tank) * np.sin(phis), "--", color="0.4", label="small angle: GM_eff sin(phi)")
    ax2.plot(np.degrees(phis), gz_curve_tank(phis, wide), color=BLUE, label="free surface, tank 10 x 5.8 m")
    ax2.axhline(0, color="k", lw=0.8)
    ax2.set_xlabel("heel angle (degrees)")
    ax2.set_ylabel("righting arm GZ (m)")
    ax2.set_title("A free surface eats the righting arm", fontsize=10)
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "gz_free_surface.png", dpi=120)

    # figure 3: design curves and the fill check
    fig3, axs3 = plt.subplots(1, 2, figsize=(10, 4.0))
    ws = np.linspace(2.0, 5.8, 39)
    for nl, col in ((1, MAGENTA), (2, ORANGE), (3, BLUE)):
        axs3[0].plot(ws, [gm_effective(make_tank(10.0, w, 120000.0, 2.5, height=8.0, n_long=nl)) for w in ws], color=col, label=f"{nl} compartment{'s' if nl > 1 else ''}")
    axs3[0].axhline(0.15, color="0.4", ls=":", label="GM = 0.15 m margin")
    axs3[0].axhline(0, color="k", lw=0.8)
    axs3[0].set_xlabel("tank width (m)")
    axs3[0].set_ylabel("effective GM (m)")
    axs3[0].set_title("Width costs stability; dividers buy it back", fontsize=10)
    axs3[0].grid(alpha=0.3)
    axs3[0].legend(fontsize=8)
    fills = np.array([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
    mom = [free_surface_moment_exact(make_tank(10.0, 5.0, f * RHO * 10.0 * 5.0 * 4.0, 2.0)) / 1e3 for f in fills]
    axs3[1].plot(100 * fills, [tank_inertia(tank) * RHO / 1e3] * len(fills), "-", color=MAGENTA, label="theory: rho_l i")
    axs3[1].plot(100 * fills, mom, "o", color=BLUE, label="exact geometry at 0.5 degrees")
    axs3[1].set_ylim(0, 150)
    axs3[1].set_xlabel("tank fill (percent of its height)")
    axs3[1].set_ylabel("free-surface moment (tonne m)")
    axs3[1].set_title("It does not depend on how full the tank is", fontsize=10)
    axs3[1].grid(alpha=0.3)
    axs3[1].legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "design_and_fill.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Where this stops
# A real tank has a roof, baffles, several tanks at once, waves that make the liquid slosh dynamically and
# rules that set the limits. This model is a still-water, slow-heel, centre-line tank: use it to understand why
# a sloshing liquid is dangerous, never to load a vessel.
