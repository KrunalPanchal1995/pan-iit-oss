"""Session 2 (Level 2): speed = slope, units, the structure tensor, and a design problem.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: from slope to metres per second
# **A. Real-world problem.** A stripe slope in "pixels per frame" is not yet a speed you can
# tell an engineer. We need (1) the pixel size and the frame rate to convert units, (2) a
# measurement of the slope that uses every pixel, not two hand-picked points, and (3) a rule
# for choosing the camera settings so that the measurement works at all.
#
# **Plan.** (1) model a stripe, (2) measure its slope with image gradients (the structure
# tensor), (3) convert to m/s, (4) solve the design problem: which frame rate?

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: a stripe as a formula
# A pattern that moves rigidly at speed v has brightness K(x, t) = f(x - v t). Our `f` is a
# Gaussian blob of width sigma (pixels). Rows of the array are time (frames), columns are
# position (pixels).

# %%
def stripe_image(v, x0=10.0, n_t=40, n_x=64, sigma=2.0):
    """Kymograph of one blob moving at v pixels per frame. Shape (n_t, n_x)."""
    t = np.arange(n_t)[:, None]
    x = np.arange(n_x)[None, :]
    return np.exp(-((x - (x0 + v * t)) ** 2) / (2 * sigma ** 2))


# %% [markdown]
# ## Step 2: the slope from gradients
# Along a stripe the brightness does not change, so K(x - v t) obeys
# `Kt + v * Kx = 0`, where Kx is the change of brightness per pixel and Kt per frame.
# Every pixel gives one such equation. The *structure tensor* collects them:
#
#     J = [[sum Kx*Kx, sum Kx*Kt],
#          [sum Kx*Kt, sum Kt*Kt]]
#
# Its main eigenvector points across the stripes (the direction in which brightness changes
# fastest). The stripes run perpendicular to it, so v = -nt / nx.
# *Coherence* = (big - small) / (big + small) eigenvalue: 1 for clean parallel stripes, 0 for no
# preferred direction.

# %%
def gradients(K):
    """Brightness change per pixel (Kx) and per frame (Kt), central differences, edges cropped."""
    Kt, Kx = np.gradient(K)           # axis 0 = time, axis 1 = position
    return Kx[1:-1, 1:-1], Kt[1:-1, 1:-1]


def structure_tensor(K):
    """The 2x2 matrix J summed over the image: [[Jxx, Jxt], [Jxt, Jtt]]."""
    Kx, Kt = gradients(K)
    return np.array([[np.sum(Kx * Kx), np.sum(Kx * Kt)],
                     [np.sum(Kx * Kt), np.sum(Kt * Kt)]])


def stripe_speed(K):
    """Return (v, coherence): v in pixels per frame. (nan, 0) if the image has no structure."""
    J = structure_tensor(K)
    if np.trace(J) < 1e-12:
        return float("nan"), 0.0
    w, V = np.linalg.eigh(J)          # ascending eigenvalues
    nx, nt = V[:, 1]                  # eigenvector of the larger one: across the stripes
    if abs(nx) < 1e-12:
        return float("inf"), float((w[1] - w[0]) / (w[1] + w[0]))   # stripes along x: not a speed
    return float(-nt / nx), float((w[1] - w[0]) / (w[1] + w[0]))


def stripe_angle_deg(v):
    """Angle between the stripe and the time axis: 0 degrees = standing still. tan(angle) = v."""
    return float(np.degrees(np.arctan(v)))


# %% [markdown]
# ## Step 3: units
# `v_px` pixels per frame. One pixel is `mm_per_px` millimetres wide; there are `fps` frames
# per second. So speed in m/s = v_px * (mm_per_px / 1000) * fps.

# %%
def speed_mps(v_px, mm_per_px, fps):
    """Convert pixels per frame to metres per second."""
    return v_px * (mm_per_px / 1000.0) * fps


def shift_per_frame(v_mps, mm_per_px, fps):
    """How many pixels the object moves between two frames (the inverse of the above)."""
    return v_mps / ((mm_per_px / 1000.0) * fps)


# %% [markdown]
# ## Step 4: the design problem
# The gradient method assumes the pattern moves only a *small* part of its own width between
# frames. A safe rule for a blob is: shift per frame <= 0.5 pixel (never above 1 pixel). Then
# the slowest allowed frame rate is fps_min = v / (shift_max * pixel size). The stripe must also
# last long enough to measure: the line needs at least `shift * n_frames` pixels.

# %%
def min_fps(v_mps, mm_per_px, shift_max=0.5):
    """Smallest frame rate (frames per second) that keeps the shift per frame <= shift_max."""
    return v_mps / (shift_max * (mm_per_px / 1000.0))


def min_line_pixels(shift, n_frames):
    """Shortest line (pixels) that holds a stripe for n_frames frames."""
    return int(np.ceil(abs(shift) * n_frames))


def min_pixel_mm(v_mps, fps, shift_max=0.5):
    """With a fixed camera frame rate, the smallest pixel size (mm) that still obeys the rule: coarser pixels are safer."""
    return 1000.0 * v_mps / (shift_max * fps)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    for v in (-1.0, 0.3, 0.8):
        v_est, coh = stripe_speed(stripe_image(v, x0=30.0 if v < 0 else 10.0))
        print(f"true {v:+.2f} px/frame -> structure tensor {v_est:+.3f}, coherence {coh:.3f}, angle {stripe_angle_deg(v_est):+.1f} deg")
    print("0.8 px/frame at 1.5 mm/px and 200 fps =", round(speed_mps(0.8, 1.5, 200), 3), "m/s")
    print("fps needed for 0.5 m/s at 2 mm/px (0.5 px/frame):", min_fps(0.5, 2.0))
    print("pixel size for 0.8 m/s at 240 fps:", round(min_pixel_mm(0.8, 240), 2), "mm")

    # figure 1: two stripes with different slopes
    fig, axs = plt.subplots(1, 2, figsize=(7, 3.6))
    for ax, v, name in zip(axs, (0.3, 0.8), ("slow", "fast")):
        ax.imshow(stripe_image(v), cmap="gray", aspect="auto")
        ax.set_title(f"{name}: dx/dt = {v} px/frame")
        ax.set_xlabel("position x (pixels)")
        ax.set_ylabel("time t (frames)")
    fig.tight_layout()
    fig.savefig(OUT / "two_slopes.png", dpi=120)

    # figure 2: shift per frame against frame rate, with the rule
    fps = np.linspace(20, 600, 300)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for mm in (1.0, 2.0, 4.0):
        ax2.plot(fps, shift_per_frame(0.5, mm, fps), label=f"{mm} mm/px")
    ax2.axhline(0.5, color="k", ls="--", label="design limit 0.5 px/frame")
    ax2.set_ylim(0, 6)
    ax2.set_xlabel("frame rate (frames per second)")
    ax2.set_ylabel("shift per frame (pixels)")
    ax2.set_title("Object at 0.5 m/s: shift per frame")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "shift_vs_fps.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
