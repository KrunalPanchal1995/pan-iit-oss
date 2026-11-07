"""Session 2 (Level 2): signed distance functions as CAD operations, and a parametric mug cross-section.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: building a part from distance functions
# **A. Real-world problem.** A designer wants a mug that holds 300 mL. The wall thickness and the
# radius are free; the height is fixed by the shelf. How do we build the mug from simple shapes,
# let a program change its size, and compute the volume? Lengths are in cm, so 1 cm^3 = 1 mL.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
HANDLE_R, HANDLE_T = 2.0, 0.45     # handle ring: centre-line radius and tube radius (cm)


# %% [markdown]
# ## Step 1: shapes and the CAD operations
# With signed distances `a` and `b` of two shapes:
#
# | operation | formula |
# |---|---|
# | union | `min(a, b)` |
# | intersection | `max(a, b)` |
# | subtraction (a minus b) | `max(a, -b)` |
# | offset (grow by t) | `a - t` |
# | shell (a wall of thickness t on each side of the surface) | `abs(a) - t` |

# %%
def sd_circle(p, c, r):
    return np.linalg.norm(np.asarray(p, float) - np.asarray(c, float), axis=-1) - r


def sd_box(p, c, half):
    q = np.abs(np.asarray(p, float) - np.asarray(c, float)) - np.asarray(half, float)
    return np.linalg.norm(np.maximum(q, 0.0), axis=-1) + np.minimum(np.max(q, axis=-1), 0.0)


def op_union(a, b):
    return np.minimum(a, b)


def op_intersect(a, b):
    return np.maximum(a, b)


def op_subtract(a, b):
    """a minus b: keep the points that are in a and not in b."""
    return np.maximum(a, -b)


def op_shell(a, t):
    return np.abs(a) - t


# %% [markdown]
# ## Step 2: smooth union
# `min` leaves a sharp crease where two shapes meet. A *smooth minimum* rounds it with a blend
# radius `k` (cm). We use the quadratic polynomial version:
#
#     h = max(k - |a - b|, 0) / k
#     smin(a, b, k) = min(a, b) - h * h * k / 4
#
# When the shapes are far apart (`|a - b| >= k`), `h = 0` and `smin` is exactly `min`. When the
# two distances are equal, the surface is pulled outward by the largest amount, `k / 4`.

# %%
def smin(a, b, k):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if k <= 0:
        return np.minimum(a, b)
    h = np.maximum(k - np.abs(a - b), 0.0) / k
    return np.minimum(a, b) - h * h * k / 4.0


# %% [markdown]
# ## Step 3: a parametric mug cross-section
# We cut the mug in half along its axis and look at the plane `(x, z)`: `x` is across the mug and `z`
# is up. The outer wall is a box of half-width `R` from `z = 0` to `z = H`. The cavity is a box of
# half-width `R - t` that starts at the floor `z = t` and reaches above the rim (open top). The
# handle is a ring (a torus cut open by the plane) found as `|circle| - tube radius`, kept only
# outside the wall, and blended to the body with radius `k`.

# %%
def body2d(p, R, H, t):
    """Mug body without the handle: outer box minus the cavity box."""
    p = np.asarray(p, float)
    outer = sd_box(p, (0.0, H / 2.0), (R, H / 2.0))
    cavity = sd_box(p, (0.0, (t + H + 1.0) / 2.0), (R - t, (H + 1.0 - t) / 2.0))
    return op_subtract(outer, cavity)


def handle2d(p, R, H, t):
    """Handle ring attached to the +x side of the wall, clipped so it never enters the cavity."""
    p = np.asarray(p, float)
    ring = np.abs(sd_circle(p, (R + 1.0, 0.55 * H), HANDLE_R)) - HANDLE_T
    return op_intersect(ring, (R - t / 2.0) - p[..., 0])


def mug2d(p, R, H, t, k=0.0):
    return smin(body2d(p, R, H, t), handle2d(p, R, H, t), k)


def area_by_cells(f, lo, hi, n):
    """Area of {f < 0} inside the box lo..hi, by counting n by n cell centres."""
    x = lo[0] + (np.arange(n) + 0.5) * (hi[0] - lo[0]) / n
    z = lo[1] + (np.arange(n) + 0.5) * (hi[1] - lo[1]) / n
    X, Z = np.meshgrid(x, z)
    inside = f(np.stack([X, Z], axis=-1)) < 0
    return float(inside.mean() * (hi[0] - lo[0]) * (hi[1] - lo[1]))


def body_area(R, H, t):
    """Analytic cross-section area of the body: outer box minus the cavity box."""
    return 2 * R * H - 2 * (R - t) * (H - t)


# %% [markdown]
# ## Step 4: volume of revolution and the 300 mL design problem
# The body is a solid of revolution about the z axis, so it has simple volumes:
#
#     cavity (capacity)  V_c = pi (R - t)^2 (H - t)
#     material           V_m = pi R^2 H - V_c
#
# For a wanted capacity V, height H and wall t, solve for the outer radius:
# `R = t + sqrt(V / (pi (H - t)))`. Another route: sum `2 pi x dx dz` over the inside cells of the
# half cross-section `x >= 0` (a slice rotated about the axis), which we use as a check.

# %%
def capacity(R, H, t):
    return float(np.pi * (R - t) ** 2 * (H - t))


def material_volume(R, H, t):
    return float(np.pi * R ** 2 * H - capacity(R, H, t))


def radius_for_capacity(V, H, t):
    if t <= 0 or t >= H:
        raise ValueError("wall thickness must satisfy 0 < t < H")
    return float(t + np.sqrt(V / (np.pi * (H - t))))


def revolve_volume(f, R, H, n):
    """Volume of the solid made by rotating the half cross-section {f < 0, x >= 0} about the z axis."""
    dx, dz = (R + 0.5) / n, (H + 1.0) / n
    x = (np.arange(n) + 0.5) * dx
    z = -0.5 + (np.arange(n) + 0.5) * dz
    X, Z = np.meshgrid(x, z)
    inside = f(np.stack([X, Z], axis=-1)) < 0
    return float(np.sum(inside * 2 * np.pi * X * dx * dz))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    R, H, t = radius_for_capacity(300.0, 9.0, 0.5), 9.0, 0.5
    print(f"design: H = 9 cm, t = 0.5 cm, capacity 300 mL needs R = {R:.3f} cm")
    print(f"check: capacity({R:.3f}) = {capacity(R, H, t):.2f} mL, material = {material_volume(R, H, t):.1f} cm^3")

    lo, hi = (-R - 1.0, -0.8), (R + 5.0, H + 1.0)
    n = 500
    xs = np.linspace(lo[0], hi[0], n)
    zs = np.linspace(lo[1], hi[1], n)
    X, Z = np.meshgrid(xs, zs)
    P = np.stack([X, Z], axis=-1)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), sharey=True)
    for ax, k, name in zip(axes, [0.0, 1.0], ["sharp union (k = 0)", "smooth union (k = 1 cm)"]):
        d = mug2d(P, R, H, t, k)
        ax.imshow(d, extent=[lo[0], hi[0], lo[1], hi[1]], origin="lower", cmap="RdBu", vmin=-3, vmax=3)
        ax.contour(X, Z, d, levels=[0.0], colors="k", linewidths=2)
        ax.set_aspect("equal")
        ax.set_title(name)
        ax.set_xlabel("x across the mug (cm)")
    axes[0].set_ylabel("z up (cm)")
    fig.tight_layout()
    fig.savefig(OUT / "mug_section.png", dpi=110)

    a = np.linspace(-3, 3, 400)
    fig2, ax2 = plt.subplots(figsize=(6.2, 3.8))
    ax2.plot(a, np.minimum(a, 0.0), "k--", label="min(a, 0)")
    for k in (0.5, 1.0, 2.0):
        ax2.plot(a, smin(a, 0.0, k), label=f"smin, k = {k} cm")
    ax2.set_xlabel("distance a to shape 1 (cm), shape 2 at distance 0")
    ax2.set_ylabel("blended distance (cm)")
    ax2.set_title("Smooth minimum equals min when |a - b| >= k")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "smooth_min.png", dpi=120)

    for nn in (50, 100, 200, 400):
        A = area_by_cells(lambda q: body2d(q, R, H, t), (-R - 0.5, -0.5), (R + 0.5, H + 0.5), nn)
        print(f"n = {nn:4d}: body cross-section area by counting {A:7.3f}  analytic {body_area(R, H, t):7.3f}")
    V = revolve_volume(lambda q: body2d(q, R, H, t), R, H, 400)
    print(f"material by revolving the counted slice: {V:.1f}  analytic {material_volume(R, H, t):.1f}")
    print("handle ring area by counting:", round(area_by_cells(lambda q: np.abs(sd_circle(q, (0, 0), 2.0)) - 0.45,
                                                                 (-3, -3), (3, 3), 600), 3),
          " analytic 4 pi Rh r =", round(4 * np.pi * 2.0 * 0.45, 3))
