"""Session 1 (Level 1): complex numbers are points that move, and one rule decides who escapes.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: complex numbers as moves, and the escape question
# **A. Real-world problem.** A fractal picture is made by asking one yes/no question for
# every pixel: "if I keep applying the same rule, does the number run away?" To ask it we need
# numbers that live on a *plane*, not just on a line. That is what complex numbers are.
#
# **Plan.** (1) treat a complex number as a point, (2) see addition and multiplication as moves,
# (3) repeat the rule z -> z*z + c and watch the orbit, (4) decide "escapes" or "stays".

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: a complex number is a point
# Write z = a + b i. The pair (a, b) is a point: a goes along, b goes up. The special number
# i is the point (0, 1) with the property i * i = -1. Python writes it as `1j`.
#
# **Adding** is a slide: (1 + 2i) + (3 - 1i) = 4 + 1i. Add the along parts, add the up parts.
#
# **Multiplying by i** is a quarter turn: 1 -> i -> -1 -> -i -> 1. Check: (a + b i) * i = a i + b i*i = -b + a i,
# so the point (a, b) moves to (-b, a), which is the same point turned 90 degrees counter-clockwise.

# %%
def add(z, w):
    """Add two complex numbers (a slide of the point z by the vector w)."""
    return z + w


def times_i(z):
    """Multiply by i: turn the point z by 90 degrees about 0."""
    return z * 1j


# %% [markdown]
# ## Step 2: the rule z -> z*z + c
# Pick a fixed number c. Start at z = 0 and apply the rule again and again:
# z1 = 0*0 + c = c, z2 = c*c + c, z3 = z2*z2 + c, ... The list z0, z1, z2, ... is the **orbit** of c.
#
# Two things can happen: the points stay in a bounded region, or they run off to infinity.
# We shall use this test: **if the distance from 0 ever exceeds 2, we call it "escaped"**
# (Session 2 explains why 2 is the right number).

# %%
def orbit(c, n):
    """Return [z0, z1, ..., zn] for z -> z*z + c starting at z0 = 0."""
    z = 0j
    out = [z]
    for _ in range(n):
        z = z * z + c
        out.append(z)
        if abs(z) > 1e6:        # far past escaping: stop before numbers overflow
            break
    return out


def escape_step(c, n=50):
    """First step k at which |z_k| > 2, or None if the orbit stays within 2 for n steps."""
    z = 0j
    for k in range(1, n + 1):
        z = z * z + c
        if abs(z) > 2:
            return k
    return None


def escapes(c, n=50):
    return escape_step(c, n) is not None


# %% [markdown]
# ## Step 3: see it
# Left: the points 1 + 2i and 3 - 1i, their sum, and 1 + 2i turned by i. Right: the distance
# |z_k| against the step k for four values of c: one settles, one cycles, two escape (one slowly).

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    z, w = 1 + 2j, 3 - 1j
    pts = {"z = 1+2i": z, "w = 3-1i": w, "z+w": add(z, w), "i*z": times_i(z)}
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    for name, q in pts.items():
        ax.plot(q.real, q.imag, "o")
        ax.annotate(name, (q.real, q.imag), textcoords="offset points", xytext=(6, 6))
    ax.annotate("", xy=(z.real, z.imag), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color="gray"))
    ax.annotate("", xy=(times_i(z).real, times_i(z).imag), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color="gray"))
    ax.set_aspect("equal")
    ax.set_xlim(-3, 5)
    ax.set_ylim(-2, 4)
    ax.grid(alpha=0.3)
    ax.set_xlabel("real part (a)")
    ax.set_ylabel("imaginary part (b)")
    ax.set_title("Adding slides, multiplying by i turns 90 degrees")
    fig.savefig(OUT / "plane_moves.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for c, label in ((0.2, "c = 0.2 (stays, settles)"), (0.3, "c = 0.3 (escapes, but slowly)"), (-1.0, "c = -1 (stays, cycles 0, -1, 0, ...)"), (1.0, "c = 1 (escapes)")):
        o = orbit(c, 14)
        ax2.plot(range(len(o)), [abs(q) for q in o], "o-", label=label)
        print(f"c = {c:5}: |z_k| = {[round(abs(q), 3) for q in o]}  escape step = {escape_step(c)}")
    ax2.axhline(2, color="red", ls="--", label="escape line |z| = 2")
    ax2.set_ylim(0, 4)
    ax2.set_xlabel("step k")
    ax2.set_ylabel("distance |z_k| from 0 (units)")
    ax2.set_title("Three orbits of z -> z*z + c")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "three_orbits.png", dpi=120)
    c = 0.5 + 0.5j
    print("worked example c = 0.5+0.5i:", [complex(round(q.real, 4), round(q.imag, 4)) for q in orbit(c, 5)], "escape step", escape_step(c))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
