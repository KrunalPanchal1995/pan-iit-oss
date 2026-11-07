"""Session 2 (Level 2): Coulomb's law, superposition, the wave equation and antenna length.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the numbers behind fields and waves
# **A. Real-world problem.** How long should the antenna of an FM radio be, and why does a
# wifi router use a stubby antenna a few centimetres long? The answer is a wavelength, and a
# wavelength comes from a frequency and the speed of light. Before that, we put numbers on the
# electric field of charges: Coulomb's law and superposition.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
K = 8.99e9                  # Coulomb constant, N m^2 / C^2
C = 299792458.0             # speed of light, m/s


# %% [markdown]
# ## Step 1: Coulomb's law for the field of a point charge
# (K is the Coulomb constant.) A point charge q (coulombs) makes an electric field of size  E = K |q| / r^2  (volts per
# metre, V/m) at distance r (metres). It points away from a positive charge, towards a
# negative one.

# %%
def coulomb_field(q, r):
    """Size of the field (V/m) of a point charge q (C) at distance r (m)."""
    return K * abs(q) / r ** 2


def point_field(q, pos, X, Y):
    """Field vector (Ex, Ey) of one charge q at pos = (x, y) metres, on the grid X, Y."""
    dx, dy = X - pos[0], Y - pos[1]
    r3 = np.maximum(np.hypot(dx, dy), 1e-9) ** 3
    return K * q * dx / r3, K * q * dy / r3


# %% [markdown]
# ## Step 2: superposition and the dipole
# Fields from several charges simply *add* as vectors. A dipole is +q and -q a small distance
# d apart. Far away on its axis the two fields almost cancel, leaving  E = 2 K q d / r^3,
# which falls faster (1/r^3) than the 1/r^2 of a single charge.

# %%
def dipole_grid(q, d, xs, ys):
    """Dipole field on a grid: +q at (-d/2, 0) and -q at (+d/2, 0). Returns Ex, Ey."""
    X, Y = np.meshgrid(xs, ys)
    e1 = point_field(q, (-d / 2, 0.0), X, Y)
    e2 = point_field(-q, (d / 2, 0.0), X, Y)
    return e1[0] + e2[0], e1[1] + e2[1]


def dipole_axis_exact(q, d, r):
    """Exact field on the axis (x = r > d/2), pointing from + towards -: sum of two Coulomb fields."""
    return K * q * (1 / (r - d / 2) ** 2 - 1 / (r + d / 2) ** 2)


def dipole_axis_far(q, d, r):
    """Far-field formula 2 K q d / r^3 (valid for r much larger than d)."""
    return 2 * K * q * d / r ** 3


# %% [markdown]
# ## Step 3: the wave equation y = A sin(k x - w t)
# A wave of amplitude A travelling in +x:  y(x, t) = A sin(k x - w t). Here k = 2 pi / lambda
# is the *wavenumber* (rad/m) and w = 2 pi f the *angular frequency* (rad/s). A crest is where
# k x - w t stays constant, so it moves at v = w / k = f lambda. For light and radio v = c.

# %%
def wavenumber(lam):
    return 2 * np.pi / lam


def angular_frequency(f):
    return 2 * np.pi * f


def wave_y(x, t, A, k, w):
    """Displacement of a wave travelling to +x."""
    return A * np.sin(k * np.asarray(x) - w * t)


def phase_speed(w, k):
    return w / k


def wavelength(f, v=C):
    return v / f


# %% [markdown]
# ## Step 4: antenna length and polarisation
# A half-wave dipole antenna is a straight conductor whose length is half a wavelength,
# L = lambda / 2 = c / (2 f): the electrons slosh back and forth along it in step with the
# wave. (A real wire is cut a few percent shorter because of its thickness; here we use
# the ideal value.) The electric field of the wave points along the wire: that direction is
# the wave's *polarisation*. A receiver that is tilted by an angle theta from it collects
# a fraction cos^2(theta) of the power.

# %%
def half_wave_length(f):
    """Ideal half-wave dipole length in metres for frequency f (Hz)."""
    return C / (2.0 * f)


def received_fraction(theta_deg):
    """Fraction of power received by an antenna (or polariser) tilted by theta from the E field."""
    return float(np.cos(np.radians(theta_deg)) ** 2)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print(f"1 nC at 0.5 m: E = {coulomb_field(1e-9, 0.5):.2f} V/m;  at 1.0 m: {coulomb_field(1e-9, 1.0):.2f} V/m (4 times weaker)")
    for r in (0.5, 1.0, 2.0):
        print(f"dipole q = 1 nC, d = 0.1 m, axis r = {r} m: exact {dipole_axis_exact(1e-9, 0.1, r):.4f} V/m, far formula {dipole_axis_far(1e-9, 0.1, r):.4f} V/m")
    lam = wavelength(2.4e9)
    print(f"wifi 2.4 GHz: lambda = {lam * 100:.2f} cm, k = {wavenumber(lam):.1f} rad/m, w = {angular_frequency(2.4e9):.3e} rad/s, "
          f"w/k = {phase_speed(angular_frequency(2.4e9), wavenumber(lam)):.4e} m/s")
    print(f"wifi half-wave dipole: {half_wave_length(2.4e9) * 100:.2f} cm;  FM 100 MHz: {half_wave_length(100e6):.3f} m")
    print("received fraction at 0, 45, 90 degrees:", [round(received_fraction(a), 3) for a in (0, 45, 90)])

    xs = np.linspace(-1.5, 1.5, 121)
    Ex, Ey = dipole_grid(1e-9, 0.6, xs, xs)
    mag = np.hypot(Ex, Ey)
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.2))
    st = axs[0].streamplot(xs, xs, Ex, Ey, color=np.log10(mag + 1e-3), cmap="viridis", density=1.5, linewidth=0.9)
    axs[0].plot([-0.3], [0], "o", ms=12, color="tab:red")
    axs[0].plot([0.3], [0], "o", ms=12, color="tab:blue")
    fig.colorbar(st.lines, ax=axs[0], label="log10 of |E| (V/m)")
    axs[0].set_xlabel("x (m)")
    axs[0].set_ylabel("y (m)")
    axs[0].set_title("Dipole field on a grid (+1 nC, -1 nC, 0.6 m apart)")
    axs[0].set_aspect("equal")
    r = np.linspace(0.5, 6, 200)
    axs[1].loglog(r, dipole_axis_exact(1e-9, 0.6, r), label="exact (two charges added)")
    axs[1].loglog(r, dipole_axis_far(1e-9, 0.6, r), "--", label="2 K q d / r^3")
    axs[1].loglog(r, coulomb_field(1e-9, r), ":", label="single charge K q / r^2")
    axs[1].set_xlabel("distance r along the axis (m)")
    axs[1].set_ylabel("field E (V/m)")
    axs[1].set_title("A dipole fades faster than one charge")
    axs[1].legend()
    axs[1].grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "dipole_field.png", dpi=110)

    fig2, axs2 = plt.subplots(1, 2, figsize=(10, 4))
    xw = np.linspace(0, 0.5, 600)
    f = 2.4e9
    T = 1 / f
    for t, col in ((0, "tab:blue"), (T / 4, "tab:orange"), (T / 2, "tab:green")):
        axs2[0].plot(xw * 100, wave_y(xw, t, 1.0, wavenumber(lam), angular_frequency(f)), color=col, label=f"t = {t * 1e12:.0f} ps")
    axs2[0].annotate("", xy=(lam * 100, 1.15), xytext=(0, 1.15), arrowprops=dict(arrowstyle="<->"))
    axs2[0].text(lam * 50, 1.2, f"lambda = {lam * 100:.1f} cm", ha="center")
    axs2[0].set_ylim(-1.2, 1.5)
    axs2[0].set_xlabel("position x (cm)")
    axs2[0].set_ylabel("field y (relative to A)")
    axs2[0].set_title("2.4 GHz wifi wave at three instants")
    axs2[0].legend(loc="lower right", fontsize=7)
    axs2[0].grid(alpha=0.3)
    fr = np.logspace(7, 10, 200)
    axs2[1].loglog(fr / 1e6, half_wave_length(fr), color="black")
    for name, fv in (("FM 100 MHz", 100e6), ("wifi 2.4 GHz", 2.4e9)):
        axs2[1].plot(fv / 1e6, half_wave_length(fv), "o", label=f"{name}: {half_wave_length(fv):.3g} m")
    axs2[1].set_xlabel("frequency (MHz)")
    axs2[1].set_ylabel("half-wave dipole length (m)")
    axs2[1].set_title("Higher frequency, shorter antenna")
    axs2[1].legend()
    axs2[1].grid(alpha=0.3, which="both")
    fig2.tight_layout()
    fig2.savefig(OUT / "wave_antenna.png", dpi=110)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
