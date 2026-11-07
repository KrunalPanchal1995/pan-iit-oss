"""Session 3 (Level 3): rebuild a 3D flame from many photos and validate the result.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: from many photos to one 3D flame
# **A. Real-world problem.** A flame bent by a breeze is not round and not symmetric. One
# stereo pair sees only its front. If we put several stereo pairs around it, match thousands
# of small windows (Session 2) and triangulate each match (Session 1), we get a cloud of 3D
# points on the flame surface. Can we turn that cloud into the flame's shape and volume, and
# show, with numbers, how close we are to the truth and how many camera pairs we need?
#
# **Plan.** (1) a synthetic flame whose shape and volume we know exactly, (2) render what
# each camera sees, (3) match and triangulate every window into 3D points, (4) slice the
# cloud by height and measure each slice's area, (5) add the slices up to a volume,
# (6) validate: point residuals, volume error, and the error against the number of pairs.
#
# **Model.** The flame is treated as an opaque glowing surface with a fixed texture (as if
# speckles were painted on the flame front). Real flames are partly transparent and flicker;
# see the roadmap. A simplified teaching model, not a measurement tool.

# %%
import pathlib

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# The test flame (metres): a sheared elliptic paraboloid. Its cross-section at height z is an
# ellipse with semi-axes a(z) = A0 sqrt(1 - z/H) and b(z) = B0 sqrt(1 - z/H), centred at x = LEAN z.
FLAME = dict(a0=0.015, b0=0.010, H=0.060, lean=0.15)
F_PX, BASE, DIST, Z_CAM = 1000.0, 0.03, 0.30, 0.030       # focal length px, baseline m, distance m, camera height m
SHAPE = (240, 240)                                       # image rows, columns


# %% [markdown]
# ## Step 1: a flame whose answer we know
# A slice at height z is an ellipse of area pi a(z) b(z) = pi A0 B0 (1 - z/H). Adding thin
# slices (Cavalieri's principle) gives the exact volume
#
#     V = integral from 0 to H of pi A0 B0 (1 - z/H) dz = pi A0 B0 H / 2
#
# The lean moves each slice sideways but does not change its area, so it does not change V.

# %%
def true_area(z, flame=FLAME):
    """Exact cross-section area (m^2) of the test flame at height z (m)."""
    z = np.asarray(z, float)
    return np.where((z >= 0) & (z <= flame["H"]), np.pi * flame["a0"] * flame["b0"] * (1 - z / flame["H"]), 0.0)


def true_volume(flame=FLAME):
    """Exact volume (m^3) of the test flame: pi A0 B0 H / 2."""
    return np.pi * flame["a0"] * flame["b0"] * flame["H"] / 2


def texture_dots(n=1400, flame=FLAME, seed=5):
    """Random points on the flame surface that carry the glowing texture (n x 3 array, m)."""
    rng = np.random.default_rng(seed)
    z = flame["H"] * (1 - np.sqrt(rng.uniform(0, 1, n)))    # more dots low down, where the surface is wide
    t = rng.uniform(0, 2 * np.pi, n)
    s = np.sqrt(1 - z / flame["H"])
    return np.c_[flame["lean"] * z + flame["a0"] * s * np.cos(t), flame["b0"] * s * np.sin(t), z]


# %% [markdown]
# ## Step 2: the cameras and what they see
# Stereo pair k sits at distance D from the flame axis, at angle phi_k = 360 k / n degrees,
# looking at the axis. Its two cameras are side by side, B apart, with parallel axes (a
# rectified pair, as in Session 1). Every pixel sends a ray into the scene; where the ray first
# meets the flame surface we read the texture. Background pixels stay dark.

# %%
def stereo_pair(phi_deg, dist=DIST, base=BASE, z_cam=Z_CAM):
    """Left and right camera centres (m) and the shared rotation R (rows: right, up, forward)."""
    p = np.radians(phi_deg)
    fwd = np.array([-np.cos(p), -np.sin(p), 0.0])
    right = np.array([-np.sin(p), np.cos(p), 0.0])
    up = np.array([0.0, 0.0, 1.0])
    centre = np.array([dist * np.cos(p), dist * np.sin(p), z_cam])
    return centre - 0.5 * base * right, centre + 0.5 * base * right, np.vstack([right, up, fwd])


def ray_hits(cam, R, f=F_PX, shape=SHAPE, flame=FLAME):
    """First hit point (rows x cols x 3, m) of every pixel ray with the flame; NaN where it misses."""
    rows, cols = shape
    cy, cx = (rows - 1) / 2, (cols - 1) / 2
    rr, cc = np.mgrid[0:rows, 0:cols].astype(float)
    d = np.stack([(cc - cx) / f, -(rr - cy) / f, np.ones_like(cc)], -1) @ R     # world ray directions
    a0, b0, H, s = flame["a0"], flame["b0"], flame["H"], flame["lean"]
    u0, du = cam[0] - s * cam[2], d[..., 0] - s * d[..., 2]
    qa = du ** 2 / a0 ** 2 + d[..., 1] ** 2 / b0 ** 2
    qb = 2 * u0 * du / a0 ** 2 + 2 * cam[1] * d[..., 1] / b0 ** 2 + d[..., 2] / H
    qc = u0 ** 2 / a0 ** 2 + cam[1] ** 2 / b0 ** 2 + cam[2] / H - 1
    disc = qb ** 2 - 4 * qa * qc
    t = np.where(disc >= 0, (-qb - np.sqrt(np.abs(disc))) / (2 * qa), np.nan)
    pts = cam + t[..., None] * d
    pts[(pts[..., 2] < 0) | (t <= 0)] = np.nan          # below the burner rim: hidden
    return pts


def render(cam, R, dots, sigma=0.0006, noise=0.01, seed=0, **kw):
    """Grey image (0..1) of the textured flame seen by one camera, plus camera noise."""
    pts = ray_hits(cam, R, **kw)
    hit = ~np.isnan(pts[..., 0])
    img = np.zeros(hit.shape)
    p = pts[hit]
    tex = np.zeros(len(p))
    for i in range(0, len(p), 2000):                    # in chunks, to keep memory small
        q = p[i:i + 2000]
        d2 = np.sum(q * q, 1)[:, None] + np.sum(dots * dots, 1)[None, :] - 2 * q @ dots.T
        tex[i:i + 2000] = np.exp(-np.clip(d2, 0, None) / (2 * sigma ** 2)).sum(1)
    img[hit] = 0.3 + 0.7 * (1 - np.exp(-tex))
    return img + np.random.default_rng(seed).normal(0, noise, img.shape)


# %% [markdown]
# ## Step 3: match every window and triangulate it
# On a grid of points in the left image (every `step` pixels) we take a (2h+1) x (2h+1) window
# that lies fully on the flame, slide it along the same row of the right image over the
# disparities the working distance allows, keep the best ZNCC score, refine it with the
# parabola, and keep the match only if the score is above `min_score`. Then (Session 1)
#
#     Z = f B / d,   X = (col - cx) Z / f,   Y = (cy - row) Z / f    (left-camera frame)
#
# and we rotate and move the point into the world frame: P = C_left + R^T (X, Y, Z).

# %%
def match_pair(left, right, d_range, half=5, step=5, min_score=0.9, bright=0.15):
    """Match a grid of left windows along rows. Returns arrays (row, col, disparity, score)."""
    lo, hi = d_range
    w = 2 * half + 1
    rows, cols = left.shape
    out = []
    for r in range(half, rows - half, step):
        for c in range(half + hi, cols - half, step):
            win = left[r - half:r + half + 1, c - half:c + half + 1]
            if win.min() < bright:
                continue                                   # window touches the dark background
            strip = right[r - half:r + half + 1, c - hi - half:c - lo + half + 1]
            cand = sliding_window_view(strip, (w, w))[0][::-1]     # candidate k has disparity lo + k
            f0 = win - win.mean()
            g0 = cand - cand.mean(axis=(1, 2), keepdims=True)
            den = np.sqrt(np.sum(f0 * f0) * np.sum(g0 * g0, axis=(1, 2)))
            sc = np.where(den > 0, np.sum(f0 * g0, axis=(1, 2)) / np.where(den > 0, den, 1), -1)
            k = int(np.argmax(sc))
            if sc[k] < min_score or k == 0 or k == len(sc) - 1:
                continue
            cm, c0, cp = sc[k - 1], sc[k], sc[k + 1]
            delta = (cm - cp) / (2 * (cm - 2 * c0 + cp))
            out.append((r, c, lo + k + delta, c0))
    return np.array(out).reshape(-1, 4)


def triangulate_world(matches, cam_left, R, f=F_PX, base=BASE, shape=SHAPE):
    """World points (n x 3, m) from matches (row, col, disparity, score) of a rectified pair."""
    rows, cols = shape
    cy, cx = (rows - 1) / 2, (cols - 1) / 2
    r, c, d = matches[:, 0], matches[:, 1], matches[:, 2]
    Z = f * base / d
    cam_pts = np.c_[(c - cx) * Z / f, (cy - r) * Z / f, Z]
    return cam_left + cam_pts @ R


def reconstruct(n_pairs, flame=FLAME, noise=0.01, half=5, step=5, seed=0):
    """Point cloud (n x 3, m) of the flame surface from n_pairs stereo pairs spaced evenly around it."""
    dots = texture_dots(flame=flame)
    d_lo = int(np.floor(F_PX * BASE / (DIST + 0.03)))       # flame lies within 3 cm of the axis
    d_hi = int(np.ceil(F_PX * BASE / (DIST - 0.03)))
    clouds = []
    for k in range(n_pairs):
        cl, cr, R = stereo_pair(360.0 * k / n_pairs)
        left = render(cl, R, dots, noise=noise, seed=seed + 2 * k, flame=flame)
        right = render(cr, R, dots, noise=noise, seed=seed + 2 * k + 1, flame=flame)
        m = match_pair(left, right, (d_lo, d_hi), half=half, step=step)
        clouds.append(triangulate_world(m, cl, R))
    return np.vstack(clouds)


# %% [markdown]
# ## Step 4: slice the cloud and measure each slice
# Cut the cloud into horizontal slices of thickness dz. In each slice, sort the points by
# their angle around the slice's centre point (the mean of x and y) and join them into a
# polygon. Its area comes from the **shoelace formula**
#
#     A = 1/2 | sum (x_i y_(i+1) - x_(i+1) y_i) |
#
# Where no camera saw the surface, the polygon cuts straight across, so missing views make the
# area too small: a **bias**, not just noise.

# %%
def shoelace(x, y):
    """Area of a polygon with vertices (x_i, y_i) in order (same units squared)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    return 0.5 * abs(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def slice_areas(points, H, n_slices, n_sectors=24):
    """Area (m^2) of each of n_slices horizontal slices of the cloud between 0 and H.

    In each slice the points are grouped into n_sectors equal angle sectors around the slice
    centre; the median radius of each sector is one corner of the polygon."""
    edges = np.linspace(0, H, n_slices + 1)
    areas = np.zeros(n_slices)
    for i in range(n_slices):
        p = points[(points[:, 2] >= edges[i]) & (points[:, 2] < edges[i + 1])]
        if len(p) < 3:
            continue
        x, y = p[:, 0] - p[:, 0].mean(), p[:, 1] - p[:, 1].mean()
        ang, rad = np.arctan2(y, x), np.hypot(x, y)
        sector = np.floor((ang + np.pi) / (2 * np.pi) * n_sectors).astype(int) % n_sectors
        keep = [k for k in range(n_sectors) if np.any(sector == k)]
        if len(keep) < 3:
            continue
        a_mid = -np.pi + (np.array(keep) + 0.5) * 2 * np.pi / n_sectors
        r_med = np.array([np.median(rad[sector == k]) for k in keep])
        areas[i] = shoelace(r_med * np.cos(a_mid), r_med * np.sin(a_mid))
    return areas


def volume_from_areas(areas, dz):
    """Volume (m^3) as the sum of slice area times slice thickness (midpoint rule)."""
    return float(np.sum(areas) * dz)


# %% [markdown]
# ## Step 5: validate
# Two independent checks. (a) **Point residual**: for each reconstructed point, the
# normalised radius rho = sqrt(((x - lean z)/a(z))^2 + (y/b(z))^2) is exactly 1 on the true
# surface; the spread of rho - 1 is the shape error. (b) **Volume error**: compare the sliced
# volume with pi A0 B0 H / 2, and see how it changes with the number of pairs.

# %%
def normalised_radius(points, flame=FLAME):
    """rho for each point (1 on the true surface). Points above the tip give NaN."""
    x, y, z = points.T
    s = np.sqrt(np.clip(1 - z / flame["H"], 0, None))
    with np.errstate(divide="ignore", invalid="ignore"):
        rho = np.sqrt(((x - flame["lean"] * z) / flame["a0"]) ** 2 + (y / flame["b0"]) ** 2) / s
    return np.where(s > 0, rho, np.nan)


def volume_study(n_pairs, n_slices=12, flame=FLAME, half=5):
    """Reconstruct with n_pairs and return (volume m^3, relative error, number of points)."""
    pts = reconstruct(n_pairs, flame=flame, half=half)
    v = volume_from_areas(slice_areas(pts, flame["H"], n_slices), flame["H"] / n_slices)
    return v, v / true_volume(flame) - 1, len(pts)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    H, n_sl = FLAME["H"], 12
    zm = (np.arange(n_sl) + 0.5) * H / n_sl
    print(f"True volume pi x 15 x 10 x 60 / 2 = {true_volume() * 1e6:.3f} cm^3")
    print(f"Sum of exact slice areas x 5 mm = {volume_from_areas(true_area(zm), H / n_sl) * 1e6:.3f} cm^3")

    # Figure 1: what one stereo pair sees and the matched disparities
    dots = texture_dots()
    cl, cr, R = stereo_pair(0.0)
    left, right = render(cl, R, dots, seed=0), render(cr, R, dots, seed=1)
    d_lo, d_hi = int(np.floor(F_PX * BASE / 0.33)), int(np.ceil(F_PX * BASE / 0.27))
    m = match_pair(left, right, (d_lo, d_hi))
    print(f"Pair 1: {len(m)} matches, disparities {m[:, 2].min():.1f} to {m[:, 2].max():.1f} px, median score {np.median(m[:, 3]):.3f}")
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))
    axes[0].imshow(left, cmap="inferno", vmin=0, vmax=1)
    axes[0].set_title("left camera, pair 1")
    axes[1].imshow(right, cmap="inferno", vmin=0, vmax=1)
    axes[1].set_title("right camera, pair 1")
    sc = axes[2].scatter(m[:, 1], m[:, 0], c=m[:, 2], cmap="viridis", s=14)
    axes[2].set_xlim(0, SHAPE[1])
    axes[2].set_ylim(SHAPE[0], 0)
    axes[2].set_aspect("equal")
    axes[2].set_title("matched windows (colour = disparity)")
    fig.colorbar(sc, ax=axes[2], label="disparity d (px)")
    for ax in axes:
        ax.set_xlabel("column (px)")
        ax.set_ylabel("row (px)")
    fig.tight_layout()
    fig.savefig(OUT / "stereo_views.png", dpi=120)

    # Figure 2: the 3D cloud from four pairs and the slice areas
    pts = reconstruct(4)
    rho = normalised_radius(pts)
    rho = rho[np.isfinite(rho)]
    print(f"Four pairs: {len(pts)} points, median |rho - 1| = {np.median(np.abs(rho - 1)):.4f}, "
          f"95th percentile {np.percentile(np.abs(rho - 1), 95):.4f}")
    areas = slice_areas(pts, H, n_sl)
    v4 = volume_from_areas(areas, H / n_sl)
    print(f"Four pairs: volume {v4 * 1e6:.3f} cm^3, error {100 * (v4 / true_volume() - 1):+.1f} percent")
    fig2 = plt.figure(figsize=(12, 4.6))
    ax = fig2.add_subplot(1, 3, 1, projection="3d")
    ax.scatter(pts[:, 0] * 1000, pts[:, 1] * 1000, pts[:, 2] * 1000, c=pts[:, 2] * 1000, cmap="plasma", s=3)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_zlabel("height z (mm)")
    ax.set_title(f"{len(pts)} points from 4 stereo pairs")
    ax.set_box_aspect((1, 0.8, 1.6))
    ax = fig2.add_subplot(1, 3, 2)
    for zc, col in [(7.5, "#d9534f"), (27.5, "#2a9d8f"), (47.5, "#1f6feb")]:
        sel = np.abs(pts[:, 2] * 1000 - zc) < 2.5
        ax.plot(pts[sel, 0] * 1000, pts[sel, 1] * 1000, ".", color=col, ms=4, label=f"slice at {zc} mm")
        t = np.linspace(0, 2 * np.pi, 200)
        s = np.sqrt(1 - zc / 60)
        ax.plot(FLAME["lean"] * zc + 15 * s * np.cos(t), 10 * s * np.sin(t), "-", color=col, lw=1)
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title("Slices: points and true ellipses")
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)
    ax = fig2.add_subplot(1, 3, 3)
    zz = np.linspace(0, 60, 100)
    ax.plot(true_area(zz / 1000) * 1e6, zz, "k-", label="true area")
    ax.plot(areas * 1e6, zm * 1000, "o", color="#d9534f", label="from the cloud")
    ax.set_xlabel("slice area (mm^2)")
    ax.set_ylabel("height z (mm)")
    ax.set_title(f"V = {v4 * 1e6:.2f} cm^3 (true {true_volume() * 1e6:.2f})")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "flame_cloud.png", dpi=120)

    # Figure 3: volume error against the number of stereo pairs, with the slicing-only floor
    ideal = texture_dots(n=20000, seed=1)                  # perfect points on the true surface
    v_ideal = volume_from_areas(slice_areas(ideal, H, n_sl), H / n_sl)
    e_ideal = 100 * (v_ideal / true_volume() - 1)
    print(f"Perfect surface points, same slicing: volume {v_ideal * 1e6:.3f} cm^3, error {e_ideal:+.1f} percent")
    ns = [1, 2, 3, 4, 6]
    errs = []
    for n in ns:
        v, e, npts = volume_study(n)
        errs.append(100 * e)
        print(f"{n} pair(s): {npts} points, volume {v * 1e6:.3f} cm^3, error {100 * e:+.1f} percent")
    fig3, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(ns, errs, "o-", color="#1f6feb", label="stereo reconstruction")
    ax.axhline(e_ideal, color="#2a9d8f", ls="--", label=f"perfect points, slicing only ({e_ideal:+.1f} %)")
    ax.axhline(0, color="k", lw=1)
    for n, e in zip(ns, errs):
        ax.annotate(f"{e:+.0f} %", (n, e), textcoords="offset points", xytext=(6, -12), fontsize=8)
    ax.set_xlabel("number of stereo pairs around the flame")
    ax.set_ylabel("volume error (percent)")
    ax.set_title("More views remove the bias from unseen sides")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="lower right")
    fig3.tight_layout()
    fig3.savefig(OUT / "volume_vs_pairs.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The flame here is an opaque, steady surface with a painted texture. A real flame is a
# translucent glowing gas that flickers. Rebuilding its inside needs emission tomography,
# time-synchronised cameras and a calibration target. That is the road to the Target: see
# `promo/roadmap.md`.
