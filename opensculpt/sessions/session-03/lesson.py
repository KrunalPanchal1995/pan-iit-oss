"""Session 3 (Level 3): a 3D mug from distance functions, measured and validated.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: sample the mug, measure it, check it
# **A. Real-world problem.** A manufacturer wants a mug that holds 300 mL and weighs under a limit.
# We build the 3D mug from signed distance functions, sample it on a grid of small cubes (voxels),
# estimate the volume by counting, and compare with exact formulas. We also pull a contour out of a
# field (marching squares), compute the surface normal from the field, and see how things fail.
# Lengths are in cm, volumes in cm^3 = mL, density in g/cm^3.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
HANDLE_R, HANDLE_T = 2.0, 0.45     # handle ring: centre-line radius and tube radius (cm)


# %% [markdown]
# ## Step 1: the 3D mug
# The mug stands on `z = 0` with its axis along `z`. Primitives:
# * finite cylinder (exact): `d = (rho - R, |z - zc| - half-height)` with `rho = sqrt(x^2 + y^2)`;
#   the distance is `min(max(d), 0) + |max(d, 0)|`.
# * torus for the handle: ring of radius `Rh` in the `(x, z)` plane, tube radius `r`:
#   `sqrt((sqrt((x - xc)^2 + (z - zc)^2) - Rh)^2 + y^2) - r`.
# * body = outer cylinder minus the cavity cylinder; handle = torus clipped to `x >= R - t/2`;
#   mug = smooth union of body and handle with blend radius `k`.

# %%
def sd_cylinder(x, y, z, R, z0, z1):
    d1 = np.hypot(x, y) - R
    d2 = np.abs(z - (z0 + z1) / 2.0) - (z1 - z0) / 2.0
    return np.minimum(np.maximum(d1, d2), 0.0) + np.hypot(np.maximum(d1, 0.0), np.maximum(d2, 0.0))


def sd_torus(x, y, z, xc, zc, Rh, r):
    return np.hypot(np.hypot(x - xc, z - zc) - Rh, y) - r


def smin(a, b, k):
    if k <= 0:
        return np.minimum(a, b)
    h = np.maximum(k - np.abs(a - b), 0.0) / k
    return np.minimum(a, b) - h * h * k / 4.0


def body3d(x, y, z, R, H, t):
    outer = sd_cylinder(x, y, z, R, 0.0, H)
    cavity = sd_cylinder(x, y, z, R - t, t, H + 1.0)
    return np.maximum(outer, -cavity)


def handle3d(x, y, z, R, H, t):
    ring = sd_torus(x, y, z, R + 1.0, 0.55 * H, HANDLE_R, HANDLE_T)
    return np.maximum(ring, (R - t / 2.0) - x)


def mug3d(x, y, z, R, H, t, k=0.0):
    return smin(body3d(x, y, z, R, H, t), handle3d(x, y, z, R, H, t), k)


# exact (analytic) volumes
def body_volume(R, H, t):
    return float(np.pi * R ** 2 * H - np.pi * (R - t) ** 2 * (H - t))


def torus_volume(Rh, r):
    return float(2 * np.pi ** 2 * Rh * r ** 2)


def cavity_surface_area(R, H, t):
    """Inner wall plus floor of the cavity: d(body volume)/dt."""
    return float(2 * np.pi * (R - t) * (H - t) + np.pi * (R - t) ** 2)


# %% [markdown]
# ## Step 2: volume by counting voxels
# Fill a box with cubes of side `h`. Evaluate the field at each cube centre; the volume is
# (number of cubes with field < 0) * h^3. This is the fraction of inside voxels times the box volume.

# %%
def voxel_volume(f, lo, hi, h, shift=(0.0, 0.0, 0.0)):
    n = [int(np.ceil((hi[i] - lo[i]) / h)) for i in range(3)]
    ax = [lo[i] + shift[i] + (np.arange(n[i]) + 0.5) * h for i in range(3)]
    Y, Z = np.meshgrid(ax[1], ax[2], indexing="ij")
    count = 0
    for xv in ax[0]:
        count += int(np.count_nonzero(f(np.full_like(Y, xv), Y, Z) < 0))
    return count * h ** 3


def mug_box(R, H):
    return (-R - 0.6, -R - 0.6, -0.6), (R + 5.0, R + 0.6, H + 0.6)


def voxel_size(N, R):
    """Voxel side when N voxels span the mug diameter plus margins."""
    return (2 * R + 1.2) / N


def body_volume_rms_error(N, R, H, t, shifts=12, seed=1):
    """RMS relative error of the voxel volume of the body over random shifts of the grid."""
    rng = np.random.default_rng(seed)
    h = voxel_size(N, R)
    lo, hi = mug_box(R, H)
    exact = body_volume(R, H, t)
    errs = []
    for _ in range(shifts):
        s = rng.uniform(-0.5, 0.5, 3) * h
        v = voxel_volume(lambda x, y, z: body3d(x, y, z, R, H, t), lo, hi, h, s)
        errs.append((v - exact) / exact)
    return float(np.sqrt(np.mean(np.square(errs))))


def convergence_slope(Ns, errors):
    """Slope of log(error) against log(N): -1 means error falls like 1/N."""
    return float(np.polyfit(np.log(Ns), np.log(errors), 1)[0])


# %% [markdown]
# ## Step 3: marching squares (a contour from a field)
# Look at the field on a grid. In each square of four corners, mark the corners with field < 0.
# The contour crosses the square edges where the sign changes; put the crossing point by linear
# interpolation, and join the crossings with a segment. Total length of the segments approximates
# the length of the curve.

# %%
# corner order: 0 bottom-left, 1 bottom-right, 2 top-right, 3 top-left;
# edges: 0 bottom, 1 right, 2 top, 3 left
_CASES = {1: [(3, 0)], 2: [(0, 1)], 3: [(3, 1)], 4: [(1, 2)], 5: [(3, 0), (1, 2)], 6: [(0, 2)], 7: [(3, 2)],
          8: [(2, 3)], 9: [(0, 2)], 10: [(0, 1), (2, 3)], 11: [(1, 2)], 12: [(1, 3)], 13: [(0, 1)], 14: [(3, 0)]}


def marching_squares(F, x, y):
    """Contour F = 0 of F[j, i] (rows follow y, columns follow x). Returns segments, shape (m, 2, 2)."""
    neg = F < 0
    code = neg[:-1, :-1] * 1 + neg[:-1, 1:] * 2 + neg[1:, 1:] * 4 + neg[1:, :-1] * 8
    segs = []
    for j, i in zip(*np.nonzero((code > 0) & (code < 15))):
        c = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
        v = [F[q[1], q[0]] for q in c]

        def cross(e):
            a, b = e, (e + 1) % 4
            s = v[a] / (v[a] - v[b])
            pa, pb = np.array([x[c[a][0]], y[c[a][1]]]), np.array([x[c[b][0]], y[c[b][1]]])
            return pa + s * (pb - pa)

        for e1, e2 in _CASES[int(code[j, i])]:
            segs.append([cross(e1), cross(e2)])
    return np.array(segs)


def contour_length(F, x, y):
    s = marching_squares(F, x, y)
    return float(np.sum(np.linalg.norm(s[:, 1] - s[:, 0], axis=1))) if len(s) else 0.0


def circle_contour_length(r, n):
    x = np.linspace(-1.3 * r, 1.3 * r, n)
    X, Y = np.meshgrid(x, x)
    return contour_length(np.hypot(X, Y) - r, x, x)


# %% [markdown]
# ## Step 4: the gradient is the surface normal
# For an exact distance field, `|grad d| = 1` everywhere and `grad d / |grad d|` points straight out
# of the surface. We take it by central differences: `(d(x + e) - d(x - e)) / (2 e)` for each axis.
# Combining fields with min/max keeps `|grad| = 1` but the values near sharp corners are no longer
# exact distances, and the smooth union has `|grad| < 1` inside the blend.

# %%
def gradient(f, p, eps=1e-4):
    p = np.asarray(p, float)
    g = np.zeros_like(p)
    for i in range(p.shape[-1]):
        e = np.zeros(p.shape[-1])
        e[i] = eps
        g[..., i] = (f(p + e) - f(p - e)) / (2 * eps)
    return g


def sphere_f(p, c=(0.0, 0.0, 0.0), r=1.0):
    return np.linalg.norm(p - np.asarray(c), axis=-1) - r


def two_spheres(p, k=0.0):
    """Two unit spheres 1.6 apart on the x axis, joined with blend radius k (k = 0 is the plain union)."""
    return smin(sphere_f(p, (0, 0, 0), 1.0), sphere_f(p, (1.6, 0, 0), 1.0), k)


def surface_gradient_norm(f, x=0.9):
    """|grad f| at the point of the surface above the neck (x fixed, y found by bisection, z = 0)."""
    a, b = 0.0, 3.0
    for _ in range(60):
        m = 0.5 * (a + b)
        if f(np.array([x, m, 0.0])) < 0:
            a = m
        else:
            b = m
    return float(np.linalg.norm(gradient(f, np.array([x, 0.5 * (a + b), 0.0]))))


# %% [markdown]
# ## Step 5: render with a ray march
# For each pixel send a ray along the view direction `d` (orthographic: all rays parallel). Step by
# the field value (it is the distance to the surface, so the step is safe) until the field is
# below a small number: a hit. Shade with the normal. A cut-away drops the half `y > 0`.

# %%
def render_cutaway(R, H, t, k=0.0, size=(220, 240), view=(0.45, -1.0, -0.55)):
    d = np.array(view, float)
    d /= np.linalg.norm(d)
    right = np.cross(d, [0.0, 0.0, 1.0])
    right /= np.linalg.norm(right)
    up = np.cross(right, d)
    h, w = size
    u = np.linspace(-6.5, 8.5, w)
    v = np.linspace(-6.5, 6.5, h)
    U, V = np.meshgrid(u, v)
    centre = np.array([1.0, 0.0, H / 2.0])
    o = centre + U[..., None] * right + V[..., None] * up - 40.0 * d

    def f(p):
        m = mug3d(p[..., 0], p[..., 1], p[..., 2], R, H, t, k)
        return np.maximum(m, p[..., 1])          # remove the half y > 0

    pos = o.copy()
    hit = np.zeros((h, w), bool)
    for _ in range(140):
        dist = f(pos)
        hit |= dist < 1e-3
        pos = pos + np.where(hit[..., None], 0.0, 0.9 * np.maximum(dist, 1e-4)[..., None] * d)
    g = gradient(f, pos, 1e-3)
    g /= np.linalg.norm(g, axis=-1, keepdims=True) + 1e-12
    light = -d + 0.4 * up
    light /= np.linalg.norm(light)
    shade = 0.25 + 0.75 * np.clip(g @ light, 0.0, 1.0)
    img = np.where(hit, shade, np.nan)
    return np.flipud(img)


# %% [markdown]
# ## Step 6: how things fail
# * A wall thinner than a voxel is hit by a sample line only some of the time.
# * A large blend radius adds material everywhere the two distances are within `k`, even inside the cavity.

# %%
def wall_hit_probability(t, h, trials=2000, seed=2):
    """Chance that a line of samples spaced h apart lands at least once inside a wall of thickness t."""
    rng = np.random.default_rng(seed)
    hits = 0
    for off in rng.uniform(0.0, h, trials):
        xs = off + np.arange(-1, int(np.ceil(1.0 / h)) + 2) * h
        hits += bool(np.any((xs >= 0.5) & (xs < 0.5 + t)))
    return hits / trials


def cavity_capacity(R, H, t, k, N=100):
    """Empty volume inside the cavity cylinder, counted with voxels (the blend can fill it)."""
    h = (H - t) / N
    n = int(np.ceil(2 * (R - t) / h))
    xs = -(R - t) + (np.arange(n) + 0.5) * h
    zs = t + (np.arange(N) + 0.5) * h
    X, Y, Z = np.meshgrid(xs, xs, zs, indexing="ij")
    free = (np.hypot(X, Y) < R - t) & (mug3d(X, Y, Z, R, H, t, k) > 0)
    return float(np.count_nonzero(free) * h ** 3)


def mug_mass(R, H, t, k=0.5, rho=2.4, N=140):
    """Mass in grams of a mug of density rho g/cm^3, from the voxel volume of body plus handle."""
    lo, hi = mug_box(R, H)
    h = voxel_size(N, R)
    return rho * voxel_volume(lambda x, y, z: mug3d(x, y, z, R, H, t, k), lo, hi, h)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    R, H, t = 3.852, 9.0, 0.5
    lo, hi = mug_box(R, H)

    print("exact body volume:", round(body_volume(R, H, t), 2), "cm^3; torus alone:", round(torus_volume(HANDLE_R, HANDLE_T), 2))
    for N in (16, 32, 64, 128):
        h = voxel_size(N, R)
        v = voxel_volume(lambda x, y, z: body3d(x, y, z, R, H, t), lo, hi, h)
        print(f"N = {N:3d}: voxel volume {v:7.2f}  error {100 * (v / body_volume(R, H, t) - 1):6.2f} %")
    Ns = np.array([16, 24, 32, 48, 64, 96, 128])
    errs = np.array([body_volume_rms_error(int(N), R, H, t) for N in Ns])
    print("rms error", np.round(100 * errs, 2), "%  slope", round(convergence_slope(Ns, errs), 2))

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.loglog(Ns, 100 * errs, "o-", label="rms error of the voxel volume")
    ax.loglog(Ns, 100 * errs[0] * Ns[0] / Ns, "k--", label="1/N")
    ax.set_xlabel("voxels across the mug, N")
    ax.set_ylabel("relative volume error (%)")
    ax.set_title("Volume error falls about like 1/N")
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "volume_error.png", dpi=120)

    for n in (16, 32, 64, 128):
        print(f"marching squares, circle r = 1, n = {n}: length {circle_contour_length(1.0, n):.5f}  (2 pi = {2 * np.pi:.5f})")
    x = np.linspace(-1.3, 1.3, 40)
    X, Y = np.meshgrid(x, x)
    segs = marching_squares(np.hypot(X, Y) - 1.0, x, x)
    fig2, ax2 = plt.subplots(figsize=(4.6, 4.4))
    for s in segs:
        ax2.plot(s[:, 0], s[:, 1], "k-")
    ax2.plot(np.cos(np.linspace(0, 6.3, 200)), np.sin(np.linspace(0, 6.3, 200)), "r:", lw=1, label="true circle")
    ax2.set_aspect("equal")
    ax2.set_xlabel("x (units)")
    ax2.set_ylabel("y (units)")
    ax2.set_title("Marching squares contour, 40 x 40 grid")
    ax2.legend(loc="upper right", fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "marching_squares.png", dpi=120)

    img = render_cutaway(R, H, t, 0.5)
    fig3, ax3 = plt.subplots(figsize=(5, 4.6))
    ax3.imshow(img, cmap="copper", vmin=0, vmax=1, extent=[-6.5, 8.5, -6.5, 6.5])
    ax3.set_title("Cut-away ray march of the 300 mL mug")
    ax3.set_xlabel("screen x (cm)")
    ax3.set_ylabel("screen y (cm)")
    fig3.tight_layout()
    fig3.savefig(OUT / "mug_render.png", dpi=120)

    yy = np.linspace(0.0, 2.5, 300)
    q = np.stack([np.full(300, 0.9), yy, np.zeros(300)], axis=-1)
    fig4, ax4 = plt.subplots(figsize=(6.2, 3.8))
    for f, name in ((lambda p: sphere_f(p, (0, 0, 0), 1.0), "one sphere (exact)"),
                    (lambda p: two_spheres(p, 0.0), "union: min of two spheres"),
                    (lambda p: two_spheres(p, 1.0), "smooth union, k = 1")):
        ax4.plot(yy, np.linalg.norm(gradient(f, q), axis=-1), label=name)
    ax4.set_ylim(0.5, 1.2)
    ax4.set_xlabel("y along a line above the neck, x = 0.9 (cm)")
    ax4.set_ylabel("|grad d| (no unit)")
    ax4.set_title("Gradient length: 1 for exact fields, below 1 in a blend")
    ax4.grid(alpha=0.3)
    ax4.legend(fontsize=8)
    fig4.tight_layout()
    fig4.savefig(OUT / "gradient_norm.png", dpi=120)

    print("|grad| on the surface above the neck: union", round(surface_gradient_norm(lambda p: two_spheres(p, 0.0)), 3),
          " smooth union k = 1:", round(surface_gradient_norm(lambda p: two_spheres(p, 1.0)), 3))
    c = np.array([2.0, 1.0, 0.5])
    print("single sphere |grad| at a random point:", round(float(np.linalg.norm(gradient(lambda p: sphere_f(p), c))), 6))
    corner = np.array([1.0, 1.0])
    print("intersection of two half-spaces at (1, 1): value", float(np.max(corner)), " true distance to the corner", round(float(np.sqrt(2.0)), 3))
    print("analytic dV/dt = cavity surface area =", round(cavity_surface_area(R, H, t), 1), "cm^2")
    dt = 0.1
    h = voxel_size(200, R)
    vp = voxel_volume(lambda x, y, z: body3d(x, y, z, R, H, t + dt), lo, hi, h)
    vm = voxel_volume(lambda x, y, z: body3d(x, y, z, R, H, t - dt), lo, hi, h)
    print("voxel (V(t+dt) - V(t-dt)) / 2dt =", round((vp - vm) / (2 * dt), 1), "cm^2")
    for tt in (0.3, 0.5):
        print(f"wall {tt} cm, voxel 0.5 cm: a sample line hits the wall {100 * wall_hit_probability(tt, 0.5):.0f} % of the time")
    for k in (0, 2, 8, 16):
        print(f"blend radius k = {k:2d} cm: capacity {cavity_capacity(R, H, t, k):6.1f} mL")
    print(f"mass of the mug (2.4 g/cm^3): {mug_mass(R, H, t):.0f} g")
