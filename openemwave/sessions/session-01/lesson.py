"""Session 1 (Level 1): electric charges, field lines, and a wave as a travelling disturbance.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: charges, fields and waves
# **A. Real-world problem.** Rub a balloon on your hair and it sticks to the wall; the same
# invisible push that does this also carries your FM radio and wifi through the air. What is
# that push, what does it look like, and why do light and radio turn out to be the same thing?
#
# **Plan.** (1) charges push or pull, (2) draw the push as arrows (the *electric field*) for
# like charges and for a dipole, (3) a wave is a disturbance that travels, (4) speed =
# frequency x wavelength, (5) light and radio travel at the same speed.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
C = 299792458.0            # speed of light in vacuum, metres per second (about 3e8)


# %% [markdown]
# ## Step 1: like charges repel, opposite charges attract
# A charge is positive or negative. Two charges of the *same* sign push apart; *opposite* signs
# pull together. Write a charge as a signed number: +1, -1, +2 ...

# %%
def force_direction(q1, q2):
    """'repel', 'attract' or 'none' for two charges (signed numbers)."""
    if q1 == 0 or q2 == 0:
        return "none"
    return "repel" if q1 * q2 > 0 else "attract"


# %% [markdown]
# ## Step 2: the field is "the push a tiny test charge would feel"
# Put a tiny positive test charge at a point. Each charge pushes it: away from positive charges,
# towards negative ones, and the push is weaker far away. Add up the pushes as arrows. The
# result is the *electric field* at that point. Here we draw it in simple units (the number
# is the strength of a push, the exact scale comes in Session 2).
#
# Two equal positive charges: the pushes cancel exactly in the middle. A dipole (one positive,
# one negative of equal size): in the middle both pushes point the same way, from + towards -.

# %%
def field_at(point, charges):
    """Field vector (Ex, Ey) at `point` in simple units. charges = [(q, x, y), ...].
    Each charge adds q * (point - charge position) / distance^3."""
    ex = ey = 0.0
    for q, x, y in charges:
        dx, dy = point[0] - x, point[1] - y
        r = np.hypot(dx, dy)
        if r == 0:
            continue
        ex += q * dx / r ** 3
        ey += q * dy / r ** 3
    return np.array([ex, ey])


def field_grid(charges, xs, ys):
    """Field on a grid. Returns Ex, Ey arrays of shape (len(ys), len(xs))."""
    X, Y = np.meshgrid(xs, ys)
    Ex = np.zeros_like(X)
    Ey = np.zeros_like(X)
    for q, x, y in charges:
        dx, dy = X - x, Y - y
        r3 = np.maximum(np.hypot(dx, dy), 1e-9) ** 3
        Ex += q * dx / r3
        Ey += q * dy / r3
    return Ex, Ey


LIKE = [(1.0, -1.0, 0.0), (1.0, 1.0, 0.0)]          # two positive charges
DIPOLE = [(1.0, -1.0, 0.0), (-1.0, 1.0, 0.0)]       # one positive, one negative


# %% [markdown]
# ## Step 3: a wave is a disturbance that travels
# Shake the end of a rope: a bump runs along it. The rope itself only moves up and down; what
# *travels* is the bump. In radio and light, what travels is a changing electric and magnetic
# field. A bump at position x and time t, moving right at speed v, is simply a bump that was
# at x - v t at time 0.

# %%
def pulse(x, t, v, width=1.0):
    """A bump (height 1) that started at x = 0 and moves right at speed v."""
    return np.exp(-(((np.asarray(x) - v * t) / width) ** 2))


def peak_position(x, t, v, width=1.0):
    """Where the highest point of the bump is at time t (read from the sampled curve)."""
    y = pulse(x, t, v, width)
    return float(np.asarray(x)[np.argmax(y)])


# %% [markdown]
# ## Step 4: speed = frequency x wavelength
# A repeating wave has a *wavelength* (distance between neighbouring crests, in metres) and a
# *frequency* (crests passing a point per second, in hertz). If f crests pass each second and
# each is lambda metres long, the wave moves f * lambda metres each second:  v = f * lambda.

# %%
def wavelength(f, v=C):
    """Wavelength in metres for frequency f (Hz) and wave speed v (m/s)."""
    return v / f


def frequency(lam, v=C):
    """Frequency in Hz for wavelength lam (m)."""
    return v / lam


# %% [markdown]
# ## Step 5: light and radio are the same kind of wave
# In empty space every electromagnetic wave travels at c, about 3e8 m/s (300 million metres per
# second), whatever its frequency. Radio, wifi, visible light and X-rays differ only in
# frequency and wavelength.

# %%
EXAMPLES = {
    "FM radio, 100 MHz": 100e6,
    "wifi, 2.4 GHz": 2.4e9,
    "green light, 600 THz": 600e12,
}

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("two positive charges:", force_direction(1, 1), "| a positive and a negative charge:", force_direction(1, -1))
    print("field in the middle, like charges :", field_at((0.0, 0.0), LIKE).round(3))
    print("field in the middle, dipole       :", field_at((0.0, 0.0), DIPOLE).round(3), "(points from + towards -)")
    for name, f in EXAMPLES.items():
        print(f"{name}: wavelength = {wavelength(f):.4g} m")
    print(f"a sound wave at 440 Hz in air (343 m/s): wavelength = {wavelength(440, 343.0):.3f} m")
    x = np.linspace(-2, 12, 1401)
    for t in (0.0, 2.0, 5.0):
        print(f"pulse at t = {t}: peak at x = {peak_position(x, t, 2.0):.2f} (v t = {2.0 * t:.1f})")

    xs = np.linspace(-3, 3, 121)
    fig, axs = plt.subplots(1, 2, figsize=(9, 4.2))
    for ax, ch, title in ((axs[0], LIKE, "Two like charges: they repel"), (axs[1], DIPOLE, "A dipole: lines run from + to -")):
        Ex, Ey = field_grid(ch, xs, xs)
        mag = np.hypot(Ex, Ey)
        ax.streamplot(xs, xs, Ex, Ey, color=np.log10(mag + 1e-3), cmap="viridis", density=1.4, linewidth=0.9)
        for q, cx, cy in ch:
            ax.plot(cx, cy, "o", ms=14, color="tab:red" if q > 0 else "tab:blue")
            ax.text(cx, cy, "+" if q > 0 else "-", ha="center", va="center", color="white", fontsize=12)
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.set_aspect("equal")
        ax.set_xlabel("x (arbitrary length unit)")
        ax.set_ylabel("y (arbitrary length unit)")
        ax.set_title(title)
    fig.tight_layout()
    fig.savefig(OUT / "field_lines.png", dpi=110)

    fig2, axs2 = plt.subplots(1, 2, figsize=(10, 4))
    for t, col in ((0.0, "tab:blue"), (2.0, "tab:orange"), (5.0, "tab:green")):
        axs2[0].plot(x, pulse(x, t, 2.0), color=col, label=f"t = {t:.0f} s")
    axs2[0].set_xlabel("position x (m)")
    axs2[0].set_ylabel("disturbance (relative)")
    axs2[0].set_title("A bump travelling at v = 2 m/s")
    axs2[0].legend()
    axs2[0].grid(alpha=0.3)
    f = np.logspace(5, 16, 200)
    axs2[1].loglog(f, wavelength(f), color="black")
    for name, fv in EXAMPLES.items():
        axs2[1].plot(fv, wavelength(fv), "o", label=name)
    axs2[1].set_xlabel("frequency (Hz)")
    axs2[1].set_ylabel("wavelength (m)")
    axs2[1].set_title("lambda = c / f: one line for all light and radio")
    axs2[1].legend(fontsize=7)
    axs2[1].grid(alpha=0.3, which="both")
    fig2.tight_layout()
    fig2.savefig(OUT / "wave_basics.png", dpi=110)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
