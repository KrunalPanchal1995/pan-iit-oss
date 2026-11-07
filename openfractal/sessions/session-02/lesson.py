"""Session 2 (Level 2): modulus and argument, the escape-time algorithm, Mandelbrot and Julia sets.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the mathematics of "does it escape?"
# **A. Real-world problem.** To draw the picture we must decide, for hundreds of thousands of
# numbers, whether an orbit escapes - and decide it with a computer that cannot iterate forever.
# How far must we iterate? Why is 2 the magic distance? And what is the difference between the
# Mandelbrot picture and a Julia picture?
#
# **Plan.** (1) modulus and argument, (2) the escape-time function, (3) the Mandelbrot set and
# the Julia set as two views of the same rule, (4) a design problem: how many iterations do we need?

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
SEAHORSE = complex(-0.7436, 0.1318)       # a point on the "seahorse valley" part of the boundary


# %% [markdown]
# ## Step 1: modulus and argument
# A point z = a + b i can be described by its **modulus** |z| = sqrt(a^2 + b^2) (distance from 0)
# and its **argument** arg z = atan2(b, a) (angle from the real axis). Then z = |z| (cos t + i sin t).
#
# Multiplying two numbers **multiplies the moduli and adds the arguments**:
# |z w| = |z| |w| and arg(z w) = arg z + arg w. Multiplying by i (modulus 1, argument 90 degrees)
# therefore turns by 90 degrees - Session 1's rule. Squaring squares the modulus and doubles
# the angle, so the rule z -> z^2 + c first squares and doubles, then slides by c.

# %%
def modulus(z):
    return float(abs(z))


def argument_deg(z):
    """Angle of z from the positive real axis, in degrees, in (-180, 180]."""
    return float(np.degrees(np.angle(z)))


# %% [markdown]
# ## Step 2: the escape-time algorithm
# For one starting value z0 and one constant c, iterate z -> z^2 + c until |z| > 2 (escaped) or
# until we run out of patience (`max_iter` steps). The answer is the number of steps used.
# A result equal to `max_iter` means "never escaped (as far as we looked)".
#
# **Why 2?** Suppose |z| > 2 and |c| <= 2. Then |z^2 + c| >= |z|^2 - |c| >= |z|^2 - 2
# = |z| + (|z| - 2)(|z| + 1) > |z| + 3 (|z| - 2). The distance grows by at least 3 (|z| - 2) every
# step, so it can never return: the orbit escapes to infinity for sure. And every c with |c| > 2
# is already outside, because z1 = c has |z1| > 2 and |c| is the largest allowed. So the whole
# Mandelbrot set lies inside the disc |c| <= 2, and radius 2 is a safe "point of no return".

# %%
def escape_time(c, max_iter=100, z0=0j):
    """Number of steps until |z| > 2 for z -> z*z + c starting at z0 (max_iter if it never does)."""
    z = z0
    for k in range(max_iter):
        if abs(z) > 2:
            return k
        z = z * z + c
    return max_iter


# %% [markdown]
# ## Step 3: two sets from one rule
# * **Mandelbrot set M**: all c whose orbit of z0 = 0 stays bounded. We vary c, start fixed.
# * **Julia set J(c) (filled)**: all starting values z0 whose orbit stays bounded for one fixed c.
#   We vary the start, c fixed.
#
# A known fact (not proved here): the Julia set of c is in one connected piece exactly when c is in M.
# Check c = 0: the rule is z -> z^2, so the orbit stays when |z0| <= 1 and escapes when |z0| > 1;
# the filled Julia set is the unit disc.

# %%
def grid_points(centre, width, nx, ny):
    """Complex numbers on an nx-by-ny grid centred on `centre`, `width` wide (pixels are square)."""
    height = width * ny / nx
    xs = centre.real + (np.arange(nx) + 0.5 - nx / 2) * width / nx
    ys = centre.imag + (ny / 2 - 0.5 - np.arange(ny)) * height / ny
    return xs, ys


def mandelbrot_image(centre, width, nx, ny, max_iter):
    xs, ys = grid_points(centre, width, nx, ny)
    return np.array([[escape_time(complex(x, y), max_iter) for x in xs] for y in ys])


def julia_image(c, width, nx, ny, max_iter, centre=0j):
    xs, ys = grid_points(centre, width, nx, ny)
    return np.array([[escape_time(c, max_iter, complex(x, y)) for x in xs] for y in ys])


# %% [markdown]
# ## Step 4: design problem - how many iterations?
# Pixels near the boundary of M take a long time to escape. If `max_iter` is too small they are
# wrongly painted "inside" and the boundary looks fat and smeared. We measure this error against
# a patient reference run (`REF_ITER` steps):
# error = fraction of pixels painted inside by `max_iter` that the reference shows escaping.

# %%
REF_ITER = 1500


def wrongly_inside(centre, width, max_iter, nx=40, ny=30, ref=None):
    """Fraction of pixels (nx by ny window) that look inside at max_iter but escape within the reference."""
    ref = mandelbrot_image(centre, width, nx, ny, REF_ITER) if ref is None else ref
    low = mandelbrot_image(centre, width, nx, ny, max_iter)
    return float(np.mean((low >= max_iter) & (ref < REF_ITER)))


def smallest_enough(centre, width, ladder=(25, 50, 100, 200, 400, 800), limit=0.01, nx=40, ny=30):
    """Smallest max_iter on the ladder whose error is at most `limit`; None if none is enough."""
    ref = mandelbrot_image(centre, width, nx, ny, REF_ITER)
    for m in ladder:
        if wrongly_inside(centre, width, m, nx, ny, ref) <= limit:
            return m
    return None


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    z = 3 + 4j
    print(f"z = 3+4i: modulus {modulus(z):.3f}, argument {argument_deg(z):.2f} degrees")
    w = 1 + 1j
    print(f"|z w| = {modulus(z * w):.4f} = |z||w| = {modulus(z) * modulus(w):.4f};  arg z + arg w = {argument_deg(z) + argument_deg(w):.2f}, arg(zw) = {argument_deg(z * w):.2f}")
    for c in (0, 1, -1, -2, 0.3):
        print(f"c = {c:5}: escape_time(c, 100) = {escape_time(c, 100)}")

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))
    M = mandelbrot_image(complex(-0.5, 0), 3.4, 120, 80, 60)
    axes[0].imshow(M, extent=(-2.2, 1.2, -1.133, 1.133), cmap="magma", origin="upper")
    axes[0].set_title("Mandelbrot set: vary c, start at 0")
    axes[0].set_xlabel("Re c")
    axes[0].set_ylabel("Im c")
    for ax, c in zip(axes[1:], (complex(-0.8, 0.156), complex(0.285, 0.01))):
        J = julia_image(c, 3.0, 120, 80, 60)
        ax.imshow(J, extent=(-1.5, 1.5, -1.0, 1.0), cmap="magma", origin="upper")
        ax.set_title(f"Julia set, c = {c.real}{c.imag:+}i: vary the start")
        ax.set_xlabel("Re z0")
        ax.set_ylabel("Im z0")
    fig.tight_layout()
    fig.savefig(OUT / "mandelbrot_and_julia.png", dpi=110)

    widths = [0.5, 0.05, 0.005]
    ladder = [25, 50, 100, 200, 400, 800]
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for wd in widths:
        ref = mandelbrot_image(SEAHORSE, wd, 40, 30, REF_ITER)
        errs = [wrongly_inside(SEAHORSE, wd, m, 40, 30, ref) for m in ladder]
        print(f"window width {wd}: wrongly-inside fraction for {ladder} = {[round(e, 3) for e in errs]}  -> smallest enough {smallest_enough(SEAHORSE, wd)}")
        ax2.semilogx(ladder, [100 * e for e in errs], "o-", label=f"window width {wd}")
    ax2.axhline(1.0, color="red", ls="--", label="1% limit")
    ax2.set_xlabel("max_iter (steps)")
    ax2.set_ylabel("pixels wrongly painted inside (%)")
    ax2.set_title("Deeper zoom needs more iterations")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "iterations_needed.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
