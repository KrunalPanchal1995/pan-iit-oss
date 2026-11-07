"""Session 2 (Level 2): airfoil shape, thin-airfoil theory and the drag polar.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: shape sets the lift, lift costs drag
# **A. Real-world problem.** Session 1 said a 1000 kg aeroplane at 50 m/s needs CL = 0.40.
# Which wing section gives that, at what angle? And once we know the lift, how big is the
# drag, and what is the best lift-to-drag ratio the aircraft can reach?
#
# **Plan.** (1) the NACA 4-digit airfoil: camber line plus thickness, (2) thin-airfoil
# theory: CL = 2 pi (alpha - alpha_L0), with alpha_L0 from the camber line, (3) the drag
# polar of a whole aircraft, CD = CD0 + CL^2 / (pi e AR), and the best L/D.
#
# **Model.** Low speed (no compressibility), attached flow (well below stall). A simplified
# teaching model, not a design tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the NACA 4-digit airfoil
# "NACA 2412" means: maximum camber m = 2 % of the chord, at p = 4 tenths of the chord from
# the nose, maximum thickness t = 12 % of the chord. x runs from 0 (leading edge) to 1
# (trailing edge) in units of the chord c.
#
# * camber line: yc = m/p^2 (2 p x - x^2) for x < p, and m/(1-p)^2 ((1 - 2p) + 2 p x - x^2) after
# * thickness: yt = 5 t (0.2969 sqrt(x) - 0.1260 x - 0.3516 x^2 + 0.2843 x^3 - 0.1036 x^4)
# * the surfaces are the camber line plus and minus yt, measured at right angles to it.

# %%
def parse_naca(code):
    """'2412' -> (m, p, t) as fractions of the chord."""
    if len(code) != 4 or not code.isdigit():
        raise ValueError("a NACA 4-digit code has exactly four digits, e.g. '2412'")
    m, p, t = int(code[0]) / 100, int(code[1]) / 10, int(code[2:]) / 100
    if m > 0 and not 0 < p < 1:
        raise ValueError("a cambered airfoil needs 1 <= second digit <= 9")
    if t <= 0:
        raise ValueError("thickness must be positive")
    return m, p, t


def camber_line(x, m, p):
    """Camber height yc(x) and slope dyc/dx for a NACA 4-digit camber line."""
    x = np.asarray(x, float)
    if m == 0:
        return np.zeros_like(x), np.zeros_like(x)
    front = x < p
    yc = np.where(front, m / p**2 * (2 * p * x - x**2), m / (1 - p) ** 2 * ((1 - 2 * p) + 2 * p * x - x**2))
    dyc = np.where(front, 2 * m / p**2 * (p - x), 2 * m / (1 - p) ** 2 * (p - x))
    return yc, dyc


def thickness(x, t):
    """Half-thickness yt(x) of the NACA 4-digit family (trailing edge slightly open)."""
    x = np.asarray(x, float)
    return 5 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1036 * x**4)


def naca4(code, n=80):
    """Airfoil outline as (X, Y): from the trailing edge along the lower surface to the nose
    and back along the upper surface (clockwise), with points packed near both edges."""
    m, p, t = parse_naca(code)
    x = 0.5 * (1 - np.cos(np.linspace(0.0, np.pi, n + 1)))   # cosine spacing
    yc, dyc = camber_line(x, m, p)
    yt, th = thickness(x, t), np.arctan(dyc)
    xu, yu = x - yt * np.sin(th), yc + yt * np.cos(th)
    xl, yl = x + yt * np.sin(th), yc - yt * np.cos(th)
    return np.r_[xl[::-1], xu[1:]], np.r_[yl[::-1], yu[1:]]


# %% [markdown]
# ## Step 2: thin-airfoil theory
# Squash the airfoil to its camber line and replace it by a sheet of tiny whirls (vortices).
# Requiring the flow to slide along the camber line and to leave the trailing edge smoothly
# (the Kutta condition) gives a famous result:
#
#     CL = 2 pi (alpha - alpha_L0)          (alpha in radians)
#
# The slope 2 pi per radian (0.110 per degree) is the same for every thin airfoil. Only the
# camber matters for alpha_L0, the angle at which the lift is zero:
#
#     alpha_L0 = -(1/pi) * integral from 0 to pi of dyc/dx (cos theta - 1) d theta,
#     with x = (1 - cos theta) / 2
#
# A symmetric airfoil has alpha_L0 = 0. Camber makes alpha_L0 negative, so the wing lifts
# even at zero angle. Thickness does not appear at all; Session 3 checks how good that is.

# %%
def alpha_zero_lift(m, p, n=2000):
    """Zero-lift angle in degrees from thin-airfoil theory (midpoint rule in theta)."""
    theta = (np.arange(n) + 0.5) * np.pi / n
    x = 0.5 * (1 - np.cos(theta))
    _, dyc = camber_line(x, m, p)
    return float(np.degrees(-np.sum(dyc * (np.cos(theta) - 1.0)) * (np.pi / n) / np.pi))


def cl_thin(alpha_deg, code):
    """Lift coefficient from thin-airfoil theory for a NACA 4-digit code."""
    m, p, _ = parse_naca(code)
    return 2 * np.pi * np.radians(np.asarray(alpha_deg, float) - alpha_zero_lift(m, p))


def alpha_for_cl(cl, code):
    """Angle of attack in degrees that gives this CL (thin-airfoil theory)."""
    m, p, _ = parse_naca(code)
    return float(np.degrees(cl / (2 * np.pi)) + alpha_zero_lift(m, p))


# %% [markdown]
# ## Step 3: the drag polar of a whole aircraft
# A finite wing leaks air round its tips. The tip vortices tilt the lift backwards a little,
# which is a drag that grows with the square of the lift: the induced drag. With aspect
# ratio AR = span^2 / S and span efficiency e (about 0.7 to 0.9):
#
#     CD = CD0 + k CL^2,     k = 1 / (pi e AR)
#
# CD0 is the "parasite" drag of the whole aircraft at zero lift (skin friction, fuselage,
# wheels). L/D = CL / CD is largest where the two parts are equal, CD0 = k CL^2, so
#
#     CL* = sqrt(CD0 / k)        (L/D)max = 1 / (2 sqrt(CD0 k))

# %%
def induced_factor(aspect_ratio, e=0.8):
    """k = 1 / (pi e AR) of the drag polar."""
    if aspect_ratio <= 0 or not 0 < e <= 1:
        raise ValueError("need AR > 0 and 0 < e <= 1")
    return 1.0 / (np.pi * e * aspect_ratio)


def cd_polar(cl, cd0, aspect_ratio, e=0.8):
    """Total drag coefficient of the aircraft at lift coefficient cl."""
    return cd0 + induced_factor(aspect_ratio, e) * np.asarray(cl, float) ** 2


def best_glide(cd0, aspect_ratio, e=0.8):
    """(CL*, best L/D) of the parabolic drag polar."""
    k = induced_factor(aspect_ratio, e)
    return float(np.sqrt(cd0 / k)), float(1.0 / (2.0 * np.sqrt(cd0 * k)))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    for code in ("0012", "2412", "4412"):
        m, p, _ = parse_naca(code)
        print(f"NACA {code}: alpha_L0 = {alpha_zero_lift(m, p):.3f} deg, CL(4 deg) = {cl_thin(4, code):.4f}, "
              f"alpha for CL 0.40 = {alpha_for_cl(0.40, code):.2f} deg")
    k = induced_factor(8, 0.8)
    cls, ld = best_glide(0.025, 8, 0.8)
    print(f"AR 8, e 0.8: k = {k:.5f}; CD0 0.025 -> CL* = {cls:.4f}, best L/D = {ld:.2f}")
    cd = cd_polar(0.40, 0.025, 8, 0.8)
    print(f"at CL 0.40: CD = {cd:.5f}, L/D = {0.40 / cd:.2f}")

    # Figure 1: three NACA airfoils, shape and camber line
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for code, col, off in (("0012", "#1f6feb", 0.0), ("2412", "#2a9d8f", -0.22), ("4412", "#d9534f", -0.44)):
        X, Y = naca4(code, 80)
        m, p, _ = parse_naca(code)
        xc = np.linspace(0, 1, 200)
        ax.fill(X, Y + off, color=col, alpha=0.25)
        ax.plot(X, Y + off, color=col, lw=1.5, label=f"NACA {code}")
        ax.plot(xc, camber_line(xc, m, p)[0] + off, "k--", lw=0.8)
    ax.set_aspect("equal")
    ax.set_xlabel("x / c (fraction of the chord)")
    ax.set_ylabel("y / c (shifted for clarity)")
    ax.set_title("NACA 4-digit airfoils: thickness wrapped round a camber line (dashed)")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "naca_shapes.png", dpi=120)

    # Figure 2: (left) thin-airfoil lift lines; (right) drag polar and L/D
    fig2, axes = plt.subplots(1, 2, figsize=(10, 4))
    al = np.linspace(-6, 10, 100)
    for code, col in (("0012", "#1f6feb"), ("2412", "#2a9d8f"), ("4412", "#d9534f")):
        axes[0].plot(al, cl_thin(al, code), color=col, label=f"NACA {code}")
        a0 = alpha_zero_lift(*parse_naca(code)[:2])
        axes[0].plot(a0, 0, "o", color=col)
    axes[0].axhline(0, color="k", lw=0.8)
    axes[0].axhline(0.40, color="k", ls=":", lw=1)
    axes[0].text(-5.8, 0.45, "CL = 0.40 (cruise, Session 1)", fontsize=8)
    axes[0].set_xlabel("angle of attack alpha (degrees)")
    axes[0].set_ylabel("lift coefficient CL (no unit)")
    axes[0].set_title("Thin-airfoil theory: same slope, camber shifts the line")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)
    cl = np.linspace(0.0, 1.4, 200)
    for ar, col in ((6, "#d9534f"), (8, "#2a9d8f"), (12, "#1f6feb")):
        axes[1].plot(cl, cl / cd_polar(cl, 0.025, ar, 0.8), color=col, label=f"AR = {ar}")
        c_s, ld_s = best_glide(0.025, ar, 0.8)
        axes[1].plot(c_s, ld_s, "o", color=col)
        axes[1].annotate(f"{ld_s:.1f}", (c_s, ld_s), xytext=(4, 4), textcoords="offset points", fontsize=8)
    axes[1].set_xlabel("lift coefficient CL (no unit)")
    axes[1].set_ylabel("lift-to-drag ratio L/D (no unit)")
    axes[1].set_title("CD = 0.025 + CL^2 / (pi 0.8 AR)")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.3)
    axes[1].set_ylim(0, 20)
    fig2.tight_layout()
    fig2.savefig(OUT / "lift_line_and_polar.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Thin-airfoil theory ignores thickness and gives no pressure along the surface. Session 3
# builds a panel method that computes the real speed and pressure all round any airfoil,
# validates it, and adds a skin-friction estimate to get the airfoil's own lift and drag.
