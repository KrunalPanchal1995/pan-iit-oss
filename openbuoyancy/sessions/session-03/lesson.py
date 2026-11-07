"""Session 3 (Level 3): does the floating box stay upright? Metacentric height and the GZ curve.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: floating is not enough, it must also right itself
# **A. Real-world problem.** A barge can float with plenty of freeboard and still roll over
# when the cargo is stacked too high. Stability asks a different question from buoyancy:
# when the barge is pushed over by a small angle, does the water push it back? The answer
# is the metacentric height GM. We compute it by formula, then check it against an exact
# numerical calculation of the heeled cross-section.
# *Educational 2D model only: not a naval architecture tool; it ignores waves, wind,
# flooding, free liquid surfaces and the rules that govern real ships.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
RHO = 1000.0            # fresh water, kg/m^3
LEN, BEAM, DEPTH = 20.0, 6.0, 2.5      # barge length, beam and hull depth, m
LIGHT, KG_LIGHT = 60000.0, 1.0         # empty barge: mass kg, centre of gravity above keel m


# %% [markdown]
# ## Step 1: the small-angle formulas
# Heights are measured up from the keel (the bottom): K is the keel, B the centre of
# buoyancy (centre of the displaced water), G the centre of gravity, M the metacentre.
# For a box floating at draft d:  KB = d / 2,  BM = I / V with I = L B^3 / 12 (waterplane)
# and V = L B d, so BM = B^2 / (12 d). Then KM = KB + BM and  GM = KM - KG.
# **GM > 0: the box rights itself. GM < 0: it heels over.**

# %%
def draft_for(mass, beam=BEAM, length=LEN, rho=RHO):
    return mass / (rho * length * beam)


def kb_box(draft):
    return draft / 2.0


def bm_box(draft, beam=BEAM):
    return beam ** 2 / (12.0 * draft)


def kg_loaded(cargo, cargo_h, light=LIGHT, kg_light=KG_LIGHT):
    """Centre of gravity (m above keel) of barge plus cargo (kg) whose own centre is at height cargo_h."""
    return (light * kg_light + cargo * cargo_h) / (light + cargo)


def gm_loaded(cargo, cargo_h, beam=BEAM, length=LEN, light=LIGHT, kg_light=KG_LIGHT):
    d = draft_for(light + cargo, beam, length)
    return kb_box(d) + bm_box(d, beam) - kg_loaded(cargo, cargo_h, light, kg_light)


# %% [markdown]
# ## Step 2: exact geometry when the box is heeled
# Rotate the rectangle by the heel angle phi, find the horizontal water line that leaves the
# same submerged area (same weight of water displaced), and take the centroid of the wet part:
# that is the heeled centre of buoyancy B. The righting arm GZ is the horizontal distance
# between the upward buoyant force (through B) and the downward weight (through G):
# **GZ = y_G - y_B** with y measured sideways in the water frame. Righting moment = weight * GZ.

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


def rectangle_hull(beam=BEAM, depth=DEPTH):
    """Box section, keel in the middle at z = 0 (counter-clockwise)."""
    return [(-beam / 2, 0.0), (beam / 2, 0.0), (beam / 2, depth), (-beam / 2, depth)]


def v_hull(beam=BEAM, depth=DEPTH):
    """V-shaped section: keel at the bottom, straight sides up to the deck edges."""
    return [(0.0, 0.0), (beam / 2, depth), (-beam / 2, depth)]


def round_bilge_hull(beam=BEAM, depth=DEPTH, n=48):
    """Half-ellipse section (a round-bilge hull) with `n` straight pieces on each side."""
    th = np.linspace(np.pi, 2 * np.pi, n + 1)
    pts = [(beam / 2 * np.cos(t), depth + depth * np.sin(t)) for t in th]
    return pts + [(beam / 2, depth), (-beam / 2, depth)]


def wet_section(phi, area, beam=BEAM, depth=DEPTH):
    """Heel angle phi (radians), wet cross-section area (m^2) -> (waterline height, y_B, z_B).
    The box is the special case of `wet_polygon` with a rectangle."""
    if area >= beam * depth:
        raise ValueError("the box would be fully submerged")
    return wet_polygon(phi, area, rectangle_hull(beam, depth))


def righting_arm_hull(phi, mass, kg, hull, length=LEN, rho=RHO, shift=0.0):
    """GZ (m) at heel angle phi for any hull section (see `wet_polygon`)."""
    area = mass / (rho * length)
    level, yb, zb = wet_polygon(phi, area, hull)
    return (-kg * np.sin(phi) + shift * np.cos(phi)) - yb


def righting_arm(phi, mass, kg, beam=BEAM, length=LEN, depth=DEPTH, rho=RHO, shift=0.0):
    """GZ (m) at heel angle phi (radians). `shift` moves G sideways in the hull by that many metres (cargo shift)."""
    area = mass / (rho * length)
    level, yb, zb = wet_section(phi, area, beam, depth)
    yg = -kg * np.sin(phi) + shift * np.cos(phi)
    return yg - yb


def gz_curve(phis, mass, kg, **kw):
    return np.array([righting_arm(p, mass, kg, **kw) for p in phis])


def wall_sided_gz(phi, gm, bm):
    """Analytic GZ for a box while the deck edge is dry and the bilge stays wet."""
    return np.sin(phi) * (gm + 0.5 * bm * np.tan(phi) ** 2)


# %% [markdown]
# ## Step 3: cargo shift and a failure case
# A cargo moved sideways by s moves G sideways by gs = cargo * s / mass. The barge then heels
# to the angle where the righting arm equals the offset, GZ(phi) = gs * cos(phi). With a
# negative GM the upright position is unstable: the barge settles at an "angle of loll"
# where GZ is zero again (or capsizes).

# %%
def heel_after_shift(cargo, cargo_h, s, light=LIGHT, **kw):
    """Equilibrium heel angle (radians) after moving the cargo sideways by s metres (scan, then bisection on the exact GZ)."""
    mass = light + cargo
    kg = kg_loaded(cargo, cargo_h, light)
    gs = cargo * s / mass
    f = lambda p: righting_arm(p, mass, kg, **kw) - gs * np.cos(p)
    grid = np.linspace(0.0, np.radians(80.0), 161)
    vals = [f(p) for p in grid]
    if gs == 0 or vals[0] > 0:
        return 0.0
    for a, b, fa, fb in zip(grid[:-1], grid[1:], vals[:-1], vals[1:]):
        if fa <= 0 < fb:
            lo, hi = a, b
            break
    else:
        return float("nan")      # no equilibrium: it capsizes
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if f(mid) <= 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def angle_of_loll(mass, kg, **kw):
    """Smallest positive heel angle (radians) where GZ returns to zero (for GM < 0), by exact geometry."""
    grid = np.linspace(np.radians(0.5), np.radians(60.0), 120)
    vals = [righting_arm(p, mass, kg, **kw) for p in grid]
    for a, b, fa, fb in zip(grid[:-1], grid[1:], vals[:-1], vals[1:]):
        if fa < 0 <= fb:
            lo, hi = a, b
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                if righting_arm(mid, mass, kg, **kw) < 0:
                    lo = mid
                else:
                    hi = mid
            return 0.5 * (lo + hi)
    return float("nan")


def max_cargo_height(cargo, gm_min=0.15):
    """Highest cargo centre of gravity (m above keel) that keeps GM >= gm_min (closed form from GM = KM - KG)."""
    mass = LIGHT + cargo
    d = draft_for(mass)
    km = kb_box(d) + bm_box(d)
    kg_max = km - gm_min
    return (kg_max * mass - LIGHT * KG_LIGHT) / cargo


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    cargo, h = 120000.0, 2.5
    mass = LIGHT + cargo
    d = draft_for(mass)
    kg = kg_loaded(cargo, h)
    gm = gm_loaded(cargo, h)
    bm = bm_box(d)
    print(f"draft {d:.3f} m  KB {kb_box(d):.3f}  BM {bm:.3f}  KM {kb_box(d) + bm:.3f}  KG {kg:.3f}  GM {gm:.3f} m")
    phis = np.radians(np.arange(0, 81, 1.0))
    gz = gz_curve(phis, mass, kg)
    for deg in (1, 5, 10, 20):
        p = np.radians(deg)
        print(f"heel {deg:2d} deg: exact GZ {righting_arm(p, mass, kg):.4f}  GM sin(phi) {gm * np.sin(p):.4f}  wall-sided {wall_sided_gz(p, gm, bm):.4f}")
    p1 = np.radians(0.5)
    print(f"GZ / sin(phi) at 0.5 deg: {righting_arm(p1, mass, kg) / np.sin(p1):.4f}  (GM = {gm:.4f})")
    print(f"deck edge goes under at {np.degrees(np.arctan(2 * (DEPTH - d) / BEAM)):.1f} deg, bilge lifts at {np.degrees(np.arctan(2 * d / BEAM)):.1f} deg")

    for hc in (2.0, 2.5, 3.0, 3.4, 3.8):
        print(f"cargo centre at {hc:.1f} m: KG {kg_loaded(cargo, hc):.3f}, GM {gm_loaded(cargo, hc):+.3f}")
    kg_bad = kg_loaded(cargo, 3.8)
    loll = angle_of_loll(mass, kg_bad)
    print(f"failure case h=3.8 m: GM {gm_loaded(cargo, 3.8):+.3f} m, angle of loll {np.degrees(loll):.1f} deg"
          f" (analytic tan^2 = -2 GM / BM -> {np.degrees(np.arctan(np.sqrt(-2 * gm_loaded(cargo, 3.8) / bm))):.1f} deg)")
    print(f"max cargo height for GM >= 0.15 m with 120 t: {max_cargo_height(cargo):.2f} m")
    for s in (0.1, 0.2, 0.3):
        print(f"cargo shifted {s} m: heel {np.degrees(heel_after_shift(cargo, h, s)):.1f} deg  (small-angle estimate {np.degrees(np.arctan(cargo * s / mass / gm)):.1f} deg)")

    # figure 1: GZ curve versus small-angle line
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.plot(np.degrees(phis), gz, label="exact geometry (loaded, cargo at 2.5 m)")
    ax.plot(np.degrees(phis), gm * np.sin(phis), "--", label="small angle: GM sin(phi)")
    ax.plot(np.degrees(phis), wall_sided_gz(phis, gm, bm), ":", label="wall-sided formula")
    gz_bad = gz_curve(phis, mass, kg_bad)
    ax.plot(np.degrees(phis), gz_bad, label="cargo at 3.8 m (GM negative)")
    ax.axhline(0, color="gray", lw=0.8)
    ax.set_ylim(-0.4, 1.0)
    ax.set_xlabel("heel angle (degrees)")
    ax.set_ylabel("righting arm GZ (m)")
    ax.set_title("Righting arm of the loaded barge")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "gz_curve.png", dpi=120)

    # figure 2: section pictures at 20 deg for stable and unstable
    fig2, axs = plt.subplots(1, 2, figsize=(9, 3.8))
    for axp, hc, title in zip(axs, (2.5, 3.8), ("cargo low (2.5 m): GM > 0", "cargo high (3.8 m): GM < 0")):
        kgx = kg_loaded(cargo, hc)
        phi = np.radians(20)
        level, yb, zb = wet_section(phi, mass / (RHO * LEN))
        c, s = np.cos(phi), np.sin(phi)
        corners = np.array([(-BEAM / 2, 0), (BEAM / 2, 0), (BEAM / 2, DEPTH), (-BEAM / 2, DEPTH), (-BEAM / 2, 0)])
        wy = corners[:, 0] * c - corners[:, 1] * s
        wz = corners[:, 0] * s + corners[:, 1] * c - level
        axp.plot(wy, wz, "k-")
        axp.axhline(0, color="tab:blue")
        axp.plot(-kgx * s, kgx * c - level, "ro", label="G")
        axp.plot(yb, zb - level, "go", label="B")
        km = kb_box(d) + bm
        axp.plot(-km * s, km * c - level, "b^", label="M (initial)")
        axp.set_title(title)
        axp.set_aspect("equal")
        axp.set_xlabel("sideways position (m)")
        axp.legend(fontsize=8, loc="upper left")
    axs[0].set_ylabel("height above the water line (m)")
    fig2.tight_layout()
    fig2.savefig(OUT / "heeled_sections.png", dpi=120)

    # figure 3: GM versus cargo height
    hh = np.linspace(1.0, 5.0, 81)
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    ax3.plot(hh, [gm_loaded(cargo, x) for x in hh])
    ax3.axhline(0, color="red", ls="--", label="GM = 0 (neutral)")
    ax3.axhline(0.15, color="orange", ls=":", label="GM = 0.15 m (design margin)")
    ax3.set_xlabel("height of the cargo's centre of gravity above the keel (m)")
    ax3.set_ylabel("metacentric height GM (m)")
    ax3.set_title("Loading high eats the stability (120 t cargo)")
    ax3.grid(alpha=0.3)
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "gm_vs_height.png", dpi=120)

    # figure 4: other hull shapes (same mass and the same KG)
    fig4, ax4 = plt.subplots(1, 2, figsize=(10, 4))
    mass4, kg4 = 80000.0, 1.2     # 80 t with G 1.2 m above the keel: every hull below floats
    hulls = {"box (barge)": (rectangle_hull(), "#003f7f"), "V hull": (v_hull(), "#c86a00"),
             "round bilge": (round_bilge_hull(), "#555555")}
    ph20 = np.radians(20)
    for name, (hl, col) in hulls.items():
        a_w = mass4 / (RHO * LEN)
        lv, yb, zb = wet_polygon(ph20, a_w, hl)
        c20, s20 = np.cos(ph20), np.sin(ph20)
        wpoly = [(y * c20 - z * s20, y * s20 + z * c20) for y, z in hl]
        ax4[0].plot([q[0] for q in wpoly] + [wpoly[0][0]], [q[1] for q in wpoly] + [wpoly[0][1]], color=col, label=name)
        ax4[0].plot([yb], [zb], "o", color=col)
        ax4[0].axhline(lv, color=col, ls=":", lw=1)
        ax4[1].plot(np.degrees(phis[:61]), [righting_arm_hull(q, mass4, kg4, hl) for q in phis[:61]], color=col, label=name)
    ax4[0].set_aspect("equal")
    ax4[0].set_xlabel("y (m)")
    ax4[0].set_ylabel("z (m)")
    ax4[0].set_title("Heeled 20 degrees (dots: B; dotted: water lines)", fontsize=10)
    ax4[0].legend(fontsize=8)
    ax4[1].axhline(0, color="k", lw=0.8)
    ax4[1].set_xlabel("heel angle (degrees)")
    ax4[1].set_ylabel("righting arm GZ (m)")
    ax4[1].set_title("Same mass and KG, different hulls")
    ax4[1].grid(alpha=0.3)
    ax4[1].legend(fontsize=8)
    fig4.tight_layout()
    fig4.savefig(OUT / "hull_shapes.png", dpi=120)
    for name, (hl, col) in hulls.items():
        print(f"{name}: GZ at 20 degrees {righting_arm_hull(ph20, mass4, kg4, hl):.3f} m")


# %% [markdown]
# ## Where this stops
# Real ships have curved hulls, free-surface liquids, waves and wind, and are judged by rules
# that look at the whole GZ curve. See `promo/roadmap.md` for the road to the Target.
