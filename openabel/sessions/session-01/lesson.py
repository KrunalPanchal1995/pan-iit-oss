"""Session 1 (Level 1): a glowing round object seen from the side adds up everything along each line of sight.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: what a camera really sees in a glowing ball
# **A. Real-world problem.** A photo of a candle flame is flat, but the flame is a 3D glowing
# blob. Each pixel does not record one point of the flame: it records the *total* light
# along the whole line of sight through it. Today you learn that one rule (a line integral,
# which for us is just a sum along a line) and see why a hollow glowing shell looks brightest
# at its edge, not in the middle.
#
# **Plan.** (1) chord length through a ball, (2) brightness profile of a solid glowing ball,
# (3) check it by brute-force adding up light along a ray, (4) make the ball hollow.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the chord
# Look at a ball of radius R from the side. The line of sight at height y above the middle
# enters and leaves the ball, travelling a straight distance called the *chord*. Pythagoras
# on the right triangle (half chord, y, R) gives
#
#     chord(y) = 2 * sqrt(R^2 - y^2)      for |y| < R, and 0 outside the ball.
#
# Check by hand with R = 3 cm and y = 1.8 cm: sqrt(9 - 3.24) = sqrt(5.76) = 2.4, so the
# chord is 4.8 cm.

# %%
def chord_length(y, R):
    """Length (cm) of the line of sight at offset y through a ball of radius R (same units)."""
    y = np.abs(np.asarray(y, dtype=float))
    inside = np.clip(R * R - y * y, 0.0, None)
    return 2.0 * np.sqrt(inside)


# %% [markdown]
# ## Step 2: brightness of a glowing ball
# If every point of the ball glows equally, with emission `eps0` (arbitrary units of light per
# cm of path), the camera adds up eps0 over the chord:  I(y) = eps0 * chord(y).
# A hollow shell (empty inside radius `r_in`) loses the chord through the empty hole:
#
#     I(y) = eps0 * ( chord(y, R) - chord(y, r_in) )

# %%
def ball_profile(y, R, eps0=1.0, r_in=0.0):
    """Brightness (a.u.) at offset y for a ball (or shell if r_in > 0) of uniform emission eps0 (a.u. per cm)."""
    return eps0 * (chord_length(y, R) - chord_length(y, r_in))


# %% [markdown]
# ## Step 3: check it by brute force
# Walk along the line of sight in tiny steps ds, find the distance from the ball's centre at
# each step, and add up the emission there times ds. This is a numerical *line integral*,
# and it knows nothing about Pythagoras, so it is an honest check.

# %%
def ray_sum(emission, y, half_length=6.0, n=6001):
    """Add up emission(r) * ds along a straight line at offset y (r = distance from the centre)."""
    s = np.linspace(-half_length, half_length, n)
    ds = s[1] - s[0]
    r = np.sqrt(s * s + y * y)
    return float(np.sum(emission(r)) * ds)


def uniform_ball(R, eps0=1.0, r_in=0.0):
    """Emission as a function of the distance r from the centre."""
    return lambda r: np.where((r <= R) & (r >= r_in), eps0, 0.0)


# %% [markdown]
# ## Optional: a second shape, a glowing cylinder seen from the side
# Stand a glowing cylinder (a candle flame, a tube light) upright: radius `R`, length `length`,
# axis along y. A line of sight at height y and sideways offset x from the axis travels a
# chord of length 2 sqrt(R^2 - x^2) through the cylinder, but only if |y| <= length / 2. So
# along the axis the brightness is *flat* (the chord does not change with y) and drops to zero
# at the ends, while across the cylinder (changing x) it is round, just like the ball:
#
#     I(x, y) = eps0 * ( chord(x, R) - chord(x, r_in) )   if |y| <= length / 2, else 0

# %%
def cylinder_profile(y, R, length, eps0=1.0, r_in=0.0, x=0.0):
    """Brightness (a.u.) of an upright glowing cylinder at height y and sideways offset x from its axis."""
    path = chord_length(x, R) - chord_length(x, r_in)
    return np.where(np.abs(np.asarray(y, dtype=float)) <= length / 2, eps0 * path, 0.0)


def ray_sum_3d(emission, x, y, half_length=6.0, n=6001):
    """Add up emission(X, Y, Z) * ds along the line of sight (the z direction) at the pixel (x, y)."""
    z = np.linspace(-half_length, half_length, n)
    ds = z[1] - z[0]
    return float(np.sum(emission(x + 0.0 * z, y + 0.0 * z, z)) * ds)


def uniform_cylinder(R, length, eps0=1.0, r_in=0.0):
    """Emission as a function of the position (X, Y, Z); the cylinder axis is the Y axis."""
    def emission(X, Y, Z):
        r = np.hypot(X, Z)
        return np.where((r <= R) & (r >= r_in) & (np.abs(Y) <= length / 2), eps0, 0.0)
    return emission


# %% [markdown]
# ## Step 4: a picture of the ball
# The 2D "photo" of a round object: the pixel at (x, y) sees the same profile as the pixel at
# distance sqrt(x^2 + y^2) from the middle, because the ball is round in every direction.

# %%
def photo(R, r_in=0.0, n=161, half=4.0):
    xs = np.linspace(-half, half, n)
    X, Y = np.meshgrid(xs, xs)
    return xs, ball_profile(np.sqrt(X * X + Y * Y), R, 1.0, r_in)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    R, r_in = 3.0, 2.0
    print(f"worked example: chord at y=1.8 cm in a ball of radius 3 cm = {chord_length(1.8, R):.3f} cm")
    print(f"solid ball: centre brightness {ball_profile(0.0, R):.3f} a.u., near the edge y=2.9 -> {ball_profile(2.9, R):.3f} a.u.")
    print(f"shell (inner radius {r_in} cm): centre {ball_profile(0.0, R, 1.0, r_in):.3f} a.u., "
          f"brightest at y=inner radius: {ball_profile(r_in, R, 1.0, r_in):.3f} a.u.")
    print(f"brute-force ray sum at y=1.8 cm: {ray_sum(uniform_ball(R), 1.8):.3f} (formula {ball_profile(1.8, R):.3f})")

    fig, axes = plt.subplots(2, 2, figsize=(8, 7), gridspec_kw={"height_ratios": [1.2, 1]})
    y = np.linspace(-4, 4, 401)
    for col, (name, ri) in enumerate([("solid ball", 0.0), ("hollow shell", r_in)]):
        xs, img = photo(R, ri)
        im = axes[0, col].imshow(img, extent=[-4, 4, -4, 4], cmap="inferno", vmin=0, vmax=6, origin="lower")
        axes[0, col].set_title(f"{name}: what the camera records")
        axes[0, col].set_xlabel("x (cm)")
        axes[0, col].set_ylabel("y (cm)")
        axes[1, col].plot(y, ball_profile(y, R, 1.0, ri), lw=2, label="formula")
        yy = np.linspace(-2.9, 2.9, 15)
        axes[1, col].plot(yy, [ray_sum(uniform_ball(R, 1.0, ri), v) for v in yy], "o", ms=4, label="ray sum")
        axes[1, col].set_ylim(0, 6.5)
        axes[1, col].set_xlabel("height y of the line of sight (cm)")
        axes[1, col].set_ylabel("brightness I (a.u.)")
        axes[1, col].grid(alpha=0.3)
        axes[1, col].legend()
    fig.colorbar(im, ax=axes[0, :], shrink=0.8, label="brightness (a.u.)")
    fig.savefig(OUT / "ball_photos.png", dpi=110)

    fig2, ax2 = plt.subplots(figsize=(5, 5))
    th = np.linspace(0, 2 * np.pi, 200)
    ax2.plot(R * np.cos(th), R * np.sin(th), "k")
    ax2.plot(r_in * np.cos(th), r_in * np.sin(th), "k--")
    for yv in (0.0, 1.0, 1.8, 2.6):
        h = chord_length(yv, R) / 2
        ax2.plot([-4, 4], [yv, yv], color="gray", lw=0.8)
        ax2.plot([-h, h], [yv, yv], color="tab:red", lw=3)
        ax2.text(4.05, yv, f"{2 * h:.2f} cm", va="center", fontsize=8)
    ax2.set_xlim(-4, 5.2)
    ax2.set_ylim(-3.5, 3.5)
    ax2.set_aspect("equal")
    ax2.set_xlabel("x (cm)")
    ax2.set_ylabel("y (cm)")
    ax2.set_title("Lines of sight and their chords (red)")
    fig2.tight_layout()
    fig2.savefig(OUT / "chords.png", dpi=110)

    # figure 3: a second shape, the cylinder
    fig3, ax3 = plt.subplots(1, 2, figsize=(9, 3.8))
    yy = np.linspace(-4, 4, 801)
    ax3[0].plot(yy, ball_profile(yy, 3.0), color="#003f7f", lw=2, label="ball (R = 3 cm)")
    ax3[0].plot(yy, cylinder_profile(yy, 3.0, 5.0), color="#c86a00", lw=2, label="cylinder (R = 3 cm, length 5 cm)")
    ys = np.array([-3.5, -2.0, -1.0, 0.0, 1.0, 2.0, 3.5])
    ax3[0].plot(ys, [ray_sum_3d(uniform_cylinder(3.0, 5.0), 0.0, v) for v in ys], "ko", ms=4, label="ray sum (cylinder)")
    ax3[0].set_xlabel("height y of the line of sight (cm)")
    ax3[0].set_ylabel("brightness I (a.u.)")
    ax3[0].set_title("Along the axis: the cylinder is flat")
    ax3[0].grid(alpha=0.3)
    ax3[0].legend(fontsize=7)
    xx = np.linspace(-3.5, 3.5, 701)
    ax3[1].plot(xx, cylinder_profile(0.0, 3.0, 5.0, x=xx), color="#c86a00", lw=2, label="formula, y = 0")
    xs2 = np.linspace(-2.9, 2.9, 13)
    ax3[1].plot(xs2, [ray_sum_3d(uniform_cylinder(3.0, 5.0), v, 0.0) for v in xs2], "ko", ms=4, label="ray sum")
    ax3[1].set_xlabel("sideways offset x from the axis (cm)")
    ax3[1].set_ylabel("brightness I (a.u.)")
    ax3[1].set_title("Across the axis: round, like the ball")
    ax3[1].grid(alpha=0.3)
    ax3[1].legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "cylinder.png", dpi=110)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint. Next session turns this into a general formula: the Abel transform.
