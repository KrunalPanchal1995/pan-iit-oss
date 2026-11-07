"""Session 1 (Level 1): why a triangle is rigid, and what a truss bar carries.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a triangle is rigid, a rectangle is not
# **A. Real-world problem.** Look under a railway bridge or at a crane arm: you see
# triangles made of straight bars. Why triangles, and not rectangles? And when a heavy
# lorry stands in the middle, which bars are being *pulled* and which are being *squashed*?
#
# **Plan.** (1) show that four bars joined by pins can lean over but three cannot,
# (2) count the bars a rigid frame needs, (3) find the forces in the simplest bridge
# truss, (4) draw it with tension in blue and compression in red.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: a rectangle of pinned bars can lean, a triangle cannot
# Take a 4 m by 3 m rectangle of four bars joined by pins. Push its top sideways: the bar
# lengths stay the same but the corner angle changes (the frame "racks"). Now add a
# diagonal bar. The diagonal of a parallelogram with sides a and b and corner angle phi has
# length d = sqrt(a^2 + b^2 - 2 a b cos(phi)). A diagonal of fixed length therefore allows
# only one angle: the frame can no longer lean.

# %%
def diagonal_length(a, b, phi_deg):
    """Length of the diagonal opposite the corner angle phi of a pinned parallelogram."""
    phi = np.radians(phi_deg)
    return float(np.sqrt(a * a + b * b - 2 * a * b * np.cos(phi)))


def corner_angle_for_diagonal(a, b, d):
    """The single corner angle (degrees) that a fixed diagonal d allows (law of cosines)."""
    c = (a * a + b * b - d * d) / (2 * a * b)
    return float(np.degrees(np.arccos(np.clip(c, -1.0, 1.0))))


# %% [markdown]
# ## Step 2: how many bars make a rigid frame?
# A frame with j pins in a plane needs at least 2 j - 3 bars to be rigid. A triangle:
# j = 3, so 3 bars. A rectangle: j = 4, so 5 bars, but it has only 4.

# %%
def bars_needed(joints):
    """Smallest number of bars that can make a plane pin-jointed frame rigid."""
    return 2 * joints - 3


def is_rigid_by_count(joints, bars):
    """Necessary condition only: enough bars. (Bars must also be placed sensibly.)"""
    return bars >= bars_needed(joints)


# %% [markdown]
# ## Step 3: the simplest bridge truss
# Two equal sloping bars meet at the middle (the apex, where the load P hangs). A bottom
# bar joins the two feet. Span L, height h. The supports hold up P/2 each. At the apex,
# the two sloping bars share the load: 2 F sin(theta) = P, where theta is the slope angle.
# The sloping bars are squashed (compression), the bottom bar is stretched (tension).
# We write tension as positive and compression as negative.

# %%
def slope_angle(span, height):
    """Angle (radians) of the sloping bars above the horizontal."""
    return float(np.arctan2(height, span / 2.0))


def triangle_truss_forces(load, span, height):
    """Return (F_top, F_bottom) in the units of load. F_top < 0 is compression, F_bottom > 0 tension."""
    th = slope_angle(span, height)
    f_top = -load / (2.0 * np.sin(th))
    f_bottom = load / (2.0 * np.tan(th))
    return float(f_top), float(f_bottom)


def force_colour(force, tol=1e-9):
    """blue for tension, red for compression, grey for a zero-force bar."""
    if force > tol:
        return "tab:blue"
    if force < -tol:
        return "tab:red"
    return "0.6"


# %% [markdown]
# ## Step 4: see it
# Left: the rectangle, the leaning rectangle and the braced triangle frame. Right: the
# bridge with a load in the middle; line width shows the size of the force.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    a, b = 4.0, 3.0
    print("rectangle 4 x 3: diagonal at 90 degrees =", round(diagonal_length(a, b, 90), 3), "m")
    print("leaning to 60 degrees: diagonal =", round(diagonal_length(a, b, 60), 3), "m")
    print("a fixed 5 m diagonal allows only", round(corner_angle_for_diagonal(a, b, 5.0), 1), "degrees")
    print("bars needed: triangle", bars_needed(3), "rectangle", bars_needed(4))

    fig, axs = plt.subplots(1, 3, figsize=(9, 3))
    for ax, phi, title, diag in ((axs[0], 90, "rectangle: 4 bars", False),
                                 (axs[1], 60, "leaning: same 4 bars", False),
                                 (axs[2], 90, "with a diagonal: rigid", True)):
        p = np.radians(phi)
        pts = np.array([[0, 0], [a, 0], [a + b * np.cos(p), b * np.sin(p)], [b * np.cos(p), b * np.sin(p)]])
        ax.fill(pts[:, 0], pts[:, 1], alpha=0.2)
        ax.plot(*np.vstack([pts, pts[0]]).T, "o-", color="k")
        if diag:
            ax.plot([pts[0, 0], pts[2, 0]], [pts[0, 1], pts[2, 1]], "-", color="tab:red", lw=3)
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("x (m)")
        ax.set_xlim(-1, 9)
        ax.set_ylim(-0.5, 3.5)
    axs[0].set_ylabel("y (m)")
    fig.tight_layout()
    fig.savefig(OUT / "rigid_vs_rectangle.png", dpi=120)

    span, load = 6.0, 10.0
    fig2, (axb, axf) = plt.subplots(1, 2, figsize=(10, 3.8))
    height = 3.0
    ft, fb = triangle_truss_forces(load, span, height)
    print(f"span 6 m, height 3 m, load 10 kN: top bars {ft:.2f} kN, bottom bar {fb:.2f} kN")
    nodes = np.array([[0, 0], [span, 0], [span / 2, height]])
    for (i, j), f in (((0, 2), ft), ((2, 1), ft), ((0, 1), fb)):
        axb.plot(nodes[[i, j], 0], nodes[[i, j], 1], color=force_colour(f), lw=1 + 5 * abs(f) / 10)
    axb.annotate("", xy=(span / 2, height), xytext=(span / 2, height + 1.2),
                 arrowprops=dict(arrowstyle="->", lw=2))
    axb.text(span / 2 + 0.2, height + 0.7, "10 kN")
    axb.text(0.1, -0.7, "blue: tension +5.00 kN, red: compression -7.07 kN", fontsize=8)
    axb.set_aspect("equal")
    axb.set_xlabel("x (m)")
    axb.set_ylabel("y (m)")
    axb.set_ylim(-1.0, 5.2)
    axb.set_title("Simple bridge truss, load in the middle")
    hs = np.linspace(0.5, 4.0, 60)
    res = np.array([triangle_truss_forces(load, span, h) for h in hs])
    axf.plot(hs, res[:, 0], color="tab:red", label="sloping bars (compression)")
    axf.plot(hs, res[:, 1], color="tab:blue", label="bottom bar (tension)")
    axf.axhline(0, color="gray", lw=0.8)
    axf.set_xlabel("truss height h (m)")
    axf.set_ylabel("bar force (kN, tension positive)")
    axf.set_title("A taller truss carries the load with smaller forces")
    axf.grid(alpha=0.3)
    axf.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "simple_truss.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
