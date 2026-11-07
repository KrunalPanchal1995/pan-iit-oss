"""Session 2 (Level 3): sketch profiles: area, centroid and second moment of area, then extrusion and mass.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: from an outline to the properties of a solid
# **A. Real-world problem.** A shelf bracket is cut from an L-shaped steel section. Two sections with the
# same mass can bend very differently under the same load. Which numbers of the outline decide how stiff it is, and
# how do we compute them from the corner points of a sketch?
#
# Educational model: a flat outline (a sketch) described by straight edges and round holes, extruded to a
# prism. Section properties follow from exact formulas. Not a structural design tool.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
RHO = 7850.0   # density of steel (kg/m^3)


# %% [markdown]
# ## Step 1: area, centroid and second moments of a polygon
# For corner points (x_i, y_i) listed counter-clockwise, with cross_i = x_i y_{i+1} - x_{i+1} y_i and the
# last point joined to the first:
#
#     A  = 1/2 sum cross_i
#     Cx = 1/(6 A) sum (x_i + x_{i+1}) cross_i       Cy = 1/(6 A) sum (y_i + y_{i+1}) cross_i
#     Ix0 = 1/12 sum (y_i^2 + y_i y_{i+1} + y_{i+1}^2) cross_i      (about the x axis through the origin)
#     Iy0 = 1/12 sum (x_i^2 + x_i x_{i+1} + x_{i+1}^2) cross_i
#
# A clockwise list gives negative values, which is exactly what a hole needs.

# %%
def polygon_moments(points):
    """Return (A, A*Cx, A*Cy, Ix0, Iy0) of a polygon about the origin. The sign follows the orientation."""
    pts = np.asarray(points, dtype=float)
    if pts.ndim != 2 or pts.shape[1] != 2 or len(pts) < 3:
        raise ValueError("a polygon needs at least three (x, y) points")
    x, y = pts[:, 0], pts[:, 1]
    x2, y2 = np.roll(x, -1), np.roll(y, -1)
    cross = x * y2 - x2 * y
    a = cross.sum() / 2
    return (a, ((x + x2) * cross).sum() / 6, ((y + y2) * cross).sum() / 6,
            ((y ** 2 + y * y2 + y2 ** 2) * cross).sum() / 12, ((x ** 2 + x * x2 + x2 ** 2) * cross).sum() / 12)


def circle_moments(cx, cy, r):
    """The same five numbers for a full disc, so round holes are exact (no polygon approximation)."""
    if r <= 0:
        raise ValueError("the radius must be positive")
    a = math.pi * r ** 2
    return (a, a * cx, a * cy, a * r ** 2 / 4 + a * cy ** 2, a * r ** 2 / 4 + a * cx ** 2)


# %% [markdown]
# ## Step 2: a section made of several shapes
# A sketch is a list of shapes, each added (+1) or removed (-1). Sum the moments about the origin, then
# move to the centroid with the parallel-axis rule:
#
#     Ixx = Ix0 - A Cy^2         Iyy = Iy0 - A Cx^2

# %%
def section_properties(shapes):
    """shapes: list of (sign, 'poly', points) or (sign, 'circle', (cx, cy, r)). Returns a dictionary."""
    tot = np.zeros(5)
    for sign, kind, data in shapes:
        if sign not in (1, -1):
            raise ValueError("the sign must be +1 (add) or -1 (remove)")
        if kind == "poly":
            m = np.array(polygon_moments(data))
            if m[0] < 0:
                m = -m                                  # accept either orientation; the sign argument decides add or remove
        elif kind == "circle":
            m = np.array(circle_moments(*data))
        else:
            raise ValueError("a shape is 'poly' or 'circle'")
        tot += sign * m
    a = tot[0]
    if a <= 0:
        raise ValueError("the section has no material: the removed area is not smaller than the added area")
    cx, cy = tot[1] / a, tot[2] / a
    return {"area": a, "cx": cx, "cy": cy, "ixx": tot[3] - a * cy ** 2, "iyy": tot[4] - a * cx ** 2}


def l_section(b, h, t):
    """Outline of an L with horizontal leg b, vertical leg h and thickness t (mm), counter-clockwise."""
    if not (0 < t < min(b, h)):
        raise ValueError("need 0 < t < min(b, h)")
    return [(0, 0), (b, 0), (b, t), (t, t), (t, h), (0, h)]


def rectangle(w, h, x0=0.0, y0=0.0):
    return [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)]


# %% [markdown]
# ## Step 3: extrude and weigh
# A prism of length ell has volume A ell and mass rho A ell. For bending about the horizontal axis the
# stiffness is proportional to Ixx, so a good section has a large Ixx for a given area (a large
# Ixx / A).

# %%
def extrude(props, length_mm):
    volume = props["area"] * length_mm
    return {"volume_mm3": volume, "mass_kg": RHO * volume * 1e-9}


def bending_stress(moment_nmm, c_mm, ixx_mm4):
    """Maximum bending stress (MPa = N/mm^2) at distance c from the neutral axis for a moment in N mm."""
    return moment_nmm * c_mm / ixx_mm4


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    pr = section_properties([(1, "poly", l_section(50, 50, 5))])
    print(f"L 50 x 50 x 5: A = {pr['area']:.1f} mm2, centroid = ({pr['cx']:.3f}, {pr['cy']:.3f}) mm, Ixx = {pr['ixx']:.0f} mm4, Iyy = {pr['iyy']:.0f} mm4")
    e = extrude(pr, 200)
    print(f"200 mm long: volume {e['volume_mm3'] / 1000:.1f} cm3, mass {e['mass_kg']:.3f} kg")
    plate = section_properties([(1, "poly", rectangle(100, 20)), (-1, "circle", (50, 10, 5))])
    print(f"100 x 20 plate with a 10 mm hole at the centre: A = {plate['area']:.1f} mm2, Ixx = {plate['ixx']:.0f} mm4")

    ts = np.linspace(2, 15, 66)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(ts, [section_properties([(1, "poly", l_section(50, 50, t))])["ixx"] / 1e4 for t in ts], color="tab:blue", label="Ixx")
    ax.plot(ts, [section_properties([(1, "poly", l_section(50, 50, t))])["iyy"] / 1e4 for t in ts], "--", color="tab:orange", label="Iyy (same by symmetry)")
    ax.set_xlabel("thickness t (mm)")
    ax.set_ylabel("second moment of area (cm^4)")
    ax.set_title("Stiffness of a 50 x 50 mm L-section against its thickness")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "ixx_vs_thickness.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    for hh, col in ((30, "tab:green"), (50, "tab:blue"), (80, "tab:red")):
        a_ = [section_properties([(1, "poly", l_section(50, hh, t))])["area"] for t in ts]
        i_ = [section_properties([(1, "poly", l_section(50, hh, t))])["ixx"] for t in ts]
        ax2.plot(a_, [i / 1e4 for i in i_], color=col, label=f"vertical leg h = {hh} mm")
    ax2.set_xlabel("section area (mm^2), proportional to mass")
    ax2.set_ylabel("Ixx (cm^4)")
    ax2.set_title("The same material gives more stiffness with a taller leg")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "ixx_vs_area.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The outline is fixed here: you type the corner points. A parametric CAD program keeps the corners
# consistent while you change dimensions. Session 3 builds that: a small solver for sketch constraints.
