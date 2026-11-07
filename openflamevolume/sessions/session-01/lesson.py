"""Session 1 (Level 1): two cameras see depth. The pinhole camera and stereo triangulation.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: two eyes see depth
# **A. Real-world problem.** A photo of a flame is flat: every point on it has only two
# numbers, a column and a row. Yet you can reach out and touch a candle without missing it,
# because your two eyes see it from slightly different places. How can two cameras do the
# same: turn two flat photos into the 3D position of the flame tip, in metres? And how sure
# can we be of that number?
#
# **Plan.** (1) the pinhole camera: where a 3D point lands in a photo, (2) two cameras side
# by side and the disparity, (3) triangulation: depth from disparity, (4) how a small pixel
# error becomes a depth error, checked with a Monte Carlo experiment.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the pinhole camera
# A camera is a dark box with a tiny hole. A point at (X, Y, Z) in metres, with Z the
# distance straight ahead, lands on the image at
#
#     x = f X / Z        y = f Y / Z
#
# measured in pixels from the image centre. f is the focal length **in pixels** (the lens
# focal length divided by the pixel size). Doubling Z halves x: far things look small.
# Notice what is lost: every point on the same ray (X, Y, Z), (2X, 2Y, 2Z), ... lands on the
# same pixel. One photo cannot tell depth.

# %%
def project(point, f, cam_x=0.0):
    """Pixel position (x, y) of a 3D point (X, Y, Z) in metres seen by a pinhole camera.

    The camera sits at (cam_x, 0, 0) and looks along +Z. f is the focal length in pixels."""
    X, Y, Z = (float(c) for c in point)
    if Z <= 0:
        raise ValueError("the point must be in front of the camera (Z > 0)")
    return f * (X - cam_x) / Z, f * Y / Z


# %% [markdown]
# ## Step 2: two cameras and the disparity
# Put a second camera a distance B (the **baseline**, in metres) to the right of the first,
# looking the same way. The same point lands at x_L in the left image and x_R in the right
# image, on the same row. The shift between them is the **disparity**
#
#     d = x_L - x_R = f B / Z
#
# Near things shift a lot, far things hardly at all. Hold a finger in front of your nose and
# blink left eye, right eye: the finger jumps, the far wall does not.

# %%
def disparity(point, f, baseline):
    """Disparity x_L - x_R in pixels of a 3D point seen by a rectified stereo pair."""
    xl, _ = project(point, f, 0.0)
    xr, _ = project(point, f, baseline)
    return xl - xr


# %% [markdown]
# ## Step 3: triangulation, depth from disparity
# Turn the formula round. If we measure d in the photos, the depth is
#
#     Z = f B / d,        X = x_L Z / f,        Y = y Z / f
#
# Geometrically: the two rays from the two cameras through the matched pixels meet at the
# point. That is **triangulation**, the same idea a surveyor uses.

# %%
def triangulate(x_left, x_right, y, f, baseline):
    """3D point (X, Y, Z) in metres from matched pixel positions in a rectified stereo pair."""
    d = x_left - x_right
    if d <= 0:
        raise ValueError("disparity must be positive (the point must be in front of both cameras)")
    Z = f * baseline / d
    return np.array([x_left * Z / f, y * Z / f, Z])


# %% [markdown]
# ## Step 4: how sure are we? Error propagation
# A match is never perfect: d has a small error, with standard deviation sigma_d (pixels).
# Differentiate Z = f B / d: dZ/dd = -f B / d^2 = -Z^2 / (f B), so
#
#     sigma_Z ~= Z^2 / (f B) * sigma_d
#
# The depth error grows with the **square** of the distance and shrinks with a longer
# baseline or a longer focal length. We check this formula with a Monte Carlo experiment:
# add random noise to d many times, triangulate each time and measure the spread.

# %%
def depth_sigma(Z, f, baseline, sigma_d):
    """First-order standard deviation of depth (m) for a disparity error sigma_d (px)."""
    return Z ** 2 / (f * baseline) * sigma_d


def monte_carlo_depth(Z, f, baseline, sigma_d, n=20000, seed=1):
    """Simulate n noisy disparity measurements; return the array of triangulated depths (m)."""
    rng = np.random.default_rng(seed)
    d_true = f * baseline / Z
    d = d_true + rng.normal(0.0, sigma_d, n)
    return f * baseline / d


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    f, B = 800.0, 0.10

    # worked example: a flame tip seen at x_L = 120 px, x_R = 80 px, row y = 60 px
    P = triangulate(120.0, 80.0, 60.0, f, B)
    print(f"Worked example: d = 40 px, flame tip at X = {P[0]:.3f} m, Y = {P[1]:.3f} m, Z = {P[2]:.3f} m")
    print(f"Depth uncertainty for sigma_d = 0.5 px: {depth_sigma(P[2], f, B, 0.5) * 100:.2f} cm")

    # Figure 1: top view of the stereo geometry for a near and a far flame
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.2))
    ax = axes[0]
    for Z, col in [(1.0, "#d9534f"), (2.0, "#2a9d8f")]:
        Pt = np.array([0.15, 0.0, Z])
        d = disparity(Pt, f, B)
        for cx, ls in [(0.0, "-"), (B, "--")]:
            ax.plot([cx, Pt[0]], [0, Z], ls, color=col, lw=1.5)
        ax.plot(Pt[0], Z, "o", color=col, ms=9)
        ax.annotate(f"flame at Z = {Z:.0f} m\nd = {d:.0f} px", (Pt[0], Z), textcoords="offset points",
                    xytext=(10, -6), fontsize=9)
    ax.plot([0, B], [0, 0], "ks", ms=8)
    ax.annotate("left camera", (0, 0), textcoords="offset points", xytext=(-70, 4), fontsize=9)
    ax.annotate("right camera", (B, 0), textcoords="offset points", xytext=(8, 4), fontsize=9)
    ax.annotate("", xy=(B, -0.1), xytext=(0, -0.1), arrowprops=dict(arrowstyle="<->"))
    ax.text(B + 0.03, -0.12, "B = 0.10 m", ha="left", va="center", fontsize=9)
    ax.set_xlim(-0.3, 0.55)
    ax.set_ylim(-0.25, 2.3)
    ax.set_xlabel("sideways position X (m)")
    ax.set_ylabel("depth Z (m)")
    ax.set_title("Top view: two rays meet at the flame")
    ax.grid(alpha=0.3)
    ax = axes[1]
    Zs = np.linspace(0.5, 5.0, 200)
    ax.plot(Zs, f * B / Zs, color="#1f6feb", lw=2)
    for Z in (1.0, 2.0, 4.0):
        ax.plot(Z, f * B / Z, "o", color="#14181f")
        ax.annotate(f"{f * B / Z:.0f} px", (Z, f * B / Z), textcoords="offset points", xytext=(6, 6), fontsize=9)
    ax.set_xlabel("depth Z (m)")
    ax.set_ylabel("disparity d (px)")
    ax.set_title("d = f B / Z  (f = 800 px, B = 0.10 m)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "stereo_geometry.png", dpi=120)

    # Figure 2: depth error against depth, formula and Monte Carlo
    fig2, ax = plt.subplots(figsize=(6.4, 4.2))
    sigma_d = 0.5
    for Bb, col in [(0.10, "#d9534f"), (0.20, "#2a9d8f")]:
        ax.plot(Zs, 100 * depth_sigma(Zs, f, Bb, sigma_d), color=col, lw=2, label=f"formula, B = {Bb:.2f} m")
        Zp = np.array([1.0, 2.0, 3.0, 4.0])
        mc = [100 * np.std(monte_carlo_depth(Z, f, Bb, sigma_d)) for Z in Zp]
        ax.plot(Zp, mc, "o", color=col, mfc="none", ms=8, label=f"Monte Carlo, B = {Bb:.2f} m")
        for Z, s in zip(Zp, mc):
            print(f"B = {Bb:.2f} m, Z = {Z:.0f} m: formula {100 * depth_sigma(Z, f, Bb, sigma_d):.2f} cm, Monte Carlo {s:.2f} cm")
    ax.set_xlabel("depth Z (m)")
    ax.set_ylabel("depth uncertainty sigma_Z (cm)")
    ax.set_title("sigma_Z = Z^2 sigma_d / (f B),  sigma_d = 0.5 px")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "depth_error.png", dpi=120)

# %% [markdown]
# ## Where this stops
# We assumed we already know which pixel in the right photo matches the flame tip in the left
# photo. Finding that match automatically, to a fraction of a pixel, is Session 2.
