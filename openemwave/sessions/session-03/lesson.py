"""Session 3 (Level 3): simulate electromagnetic waves with FDTD and check them against theory.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a wave simulator, and how to trust it
# **A. Real-world problem.** Nobody solves Maxwell's equations by hand for a phone antenna.
# Engineers march the fields forward in time on a grid: the FDTD method (finite-difference
# time-domain). A simulator is only useful if you can show that it gets known answers right
# and that you know when it breaks. Today you build one in about 60 lines and test it.
#
# **Units.** We use *normalised units*: the grid spacing is 1 (one "cell"), the speed of light
# is 1, and time is measured in cell-crossing times. So `S = c dt / dx` (the Courant number)
# is the fraction of a cell a wave travels in one time step. Distances are in cells.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the 1D Yee grid
# In 1D the electric field Ez lives on whole cells and the magnetic field Hy sits half a cell
# to the right. The two update each other in turn (leapfrog):
#
#     Hy[i] += S * (Ez[i+1] - Ez[i])        (a changing E makes H)
#     Ez[i] += S * (Hy[i] - Hy[i-1])        (a changing H makes E)
#
# The ends are handled by a simple absorbing rule (Mur) or by a perfect conductor, where Ez
# is forced to 0.

# %%
def gaussian(n, centre=60.0, width=15.0):
    """A smooth pulse in time step n (dimensionless), peak 1 at n = centre."""
    return float(np.exp(-(((n - centre) / width) ** 2)))


def fdtd_1d(n_cells, steps, S, src_cell, waveform, probes=(), right="mur"):
    """March Ez, Hy for `steps` steps. Returns (Ez, history of Ez at the probe cells).

    waveform(n) is added to Ez[src_cell] each step (a soft source).
    right = "mur" (absorbing) or "pec" (perfect conductor wall at the last cell).
    """
    ez = np.zeros(n_cells)
    hy = np.zeros(n_cells - 1)
    hist = np.zeros((len(probes), steps))
    k = (S - 1.0) / (S + 1.0)
    for n in range(steps):
        hy += S * (ez[1:] - ez[:-1])
        old0, old1, oldm1, oldm2 = ez[0], ez[1], ez[-1], ez[-2]
        ez[1:-1] += S * (hy[1:] - hy[:-1])
        ez[src_cell] += waveform(n)
        ez[0] = old1 + k * (ez[1] - old0)                      # Mur on the left
        ez[-1] = 0.0 if right == "pec" else oldm2 + k * (ez[-2] - oldm1)
        for m, p in enumerate(probes):
            hist[m, n] = ez[p]
    return ez, hist


def peak_time(series):
    """Time of the maximum of a sampled pulse, refined by a parabola through 3 points."""
    i = int(np.argmax(series))
    a, b, c = series[i - 1], series[i], series[i + 1]
    return i + 0.5 * (a - c) / (a - 2 * b + c)


def measured_speed_1d(S=0.5, gap=100):
    """Wave speed (cells per unit time, c = 1) from the arrival of a pulse peak at two probes."""
    p1, p2 = 150, 150 + gap
    _, h = fdtd_1d(500, 500, S, 100, gaussian, probes=(p1, p2))
    dt_steps = peak_time(h[1]) - peak_time(h[0])
    return gap / (dt_steps * S)


# %% [markdown]
# ## Step 2: a standing wave in front of a conductor
# A continuous sine source and a metal wall at the right end. The incoming and reflected
# waves add. Where they cancel the field is always 0 (a node). Nodes are half a wavelength
# apart. We find them from the envelope: the largest |Ez| each cell reaches in the last periods.

# %%
def sine_wave(ppw, S, phase=0.0, ramp_periods=3.0):
    """Returns f(n): a sine of wavelength `ppw` cells, switched on smoothly (soft start)."""
    period = ppw / S                                           # time steps per period
    def f(n):
        r = min(1.0, n / (ramp_periods * period))
        return (r * r * (3 - 2 * r)) * np.sin(2 * np.pi * n / period - phase)
    return f


def standing_wave_nodes(ppw=20, S=0.5, n_cells=300, src_cell=50):
    """Positions (cells) of the field nodes in front of a conductor at the last cell."""
    period = ppw / S
    steps = int(2.5 * (n_cells - src_cell) / S) + int(4 * period)     # long enough for the echo to return
    ez = np.zeros(n_cells)
    hy = np.zeros(n_cells - 1)
    k = (S - 1.0) / (S + 1.0)
    f = sine_wave(ppw, S)
    env = np.zeros(n_cells)
    for n in range(steps):
        hy += S * (ez[1:] - ez[:-1])
        o0, o1 = ez[0], ez[1]
        ez[1:-1] += S * (hy[1:] - hy[:-1])
        ez[src_cell] += f(n)
        ez[0] = o1 + k * (ez[1] - o0)
        ez[-1] = 0.0
        if n >= steps - int(period) - 1:
            env = np.maximum(env, np.abs(ez))
    # nodes = local minima of the envelope in the region between the source and the wall
    lo, hi = src_cell + ppw, n_cells - 1
    seg = env[lo:hi + 1]
    nodes = []
    for i in range(1, len(seg) - 1):
        if seg[i] <= seg[i - 1] and seg[i] < seg[i + 1] and seg[i] < 0.5 * seg.max():
            a, b, c = seg[i - 1], seg[i], seg[i + 1]
            nodes.append(lo + i + 0.5 * (a - c) / (a - 2 * b + c))
    return np.array(nodes), env


# %% [markdown]
# ## Step 3: the 2D grid (TMz mode)
# In 2D we follow Ez and the two in-plane magnetic components Hx, Hy:
#
#     Hx -= S * dEz/dy      Hy += S * dEz/dx      Ez += S * (dHy/dx - dHx/dy)
#
# Think of Ez as the electric field pointing out of the page, a wave spreading in the page.
# The class below keeps the three arrays and can report the total energy.

# %%
class Yee2D:
    """2D FDTD, normalised units (dx = 1, c = 1, eps = mu = 1)."""

    def __init__(self, nx, ny, S=0.5, boundary="mur"):
        self.nx, self.ny, self.S, self.boundary = nx, ny, S, boundary
        self.ez = np.zeros((nx, ny))
        self.hx = np.zeros((nx, ny - 1))
        self.hy = np.zeros((nx - 1, ny))
        self.n = 0
        self.k = (S - 1.0) / (S + 1.0)
        self.ez_prev = self.ez.copy()

    def step(self, sources=()):
        """One time step. sources = iterable of (i, j, value) added to Ez (soft sources)."""
        S, ez = self.S, self.ez
        self.ez_prev = ez.copy()
        self.hx -= S * (ez[:, 1:] - ez[:, :-1])
        self.hy += S * (ez[1:, :] - ez[:-1, :])
        if self.boundary == "mur":
            e0, e1 = ez[0, :].copy(), ez[1, :].copy()
            em, em2 = ez[-1, :].copy(), ez[-2, :].copy()
            f0, f1 = ez[:, 0].copy(), ez[:, 1].copy()
            fm, fm2 = ez[:, -1].copy(), ez[:, -2].copy()
        ez[1:-1, 1:-1] += S * ((self.hy[1:, 1:-1] - self.hy[:-1, 1:-1]) - (self.hx[1:-1, 1:] - self.hx[1:-1, :-1]))
        for i, j, v in sources:
            ez[i, j] += v
        if self.boundary == "mur":
            k = self.k
            ez[0, :] = e1 + k * (ez[1, :] - e0)
            ez[-1, :] = em2 + k * (ez[-2, :] - em)
            ez[:, 0] = f1 + k * (ez[:, 1] - f0)
            ez[:, -1] = fm2 + k * (ez[:, -2] - fm)
        self.n += 1

    def energy(self):
        """Total field energy 0.5*sum(E^n E^(n+1) + H^2). Exactly conserved in a closed box."""
        return float(0.5 * (np.sum(self.ez_prev * self.ez) + np.sum(self.hx ** 2) + np.sum(self.hy ** 2)))


COURANT_LIMIT_2D = 1.0 / np.sqrt(2.0)       # S must stay below this in 2D


def courant_dt(dx, c=299792458.0, dim=2):
    """Largest stable time step (seconds) for cell size dx (metres): dx / (c sqrt(dim))."""
    return dx / (c * np.sqrt(dim))


# %% [markdown]
# ## Step 4: tests of the 2D solver
# (a) energy in a closed metal box stays constant, (b) a time step above the Courant limit
# blows up, (c) the cylindrical wave from a point source weakens as 1/sqrt(r).

# %%
def box_energy_history(S=0.5, size=81, steps=400):
    """Closed PEC box, a short pulse in the middle at the start, then nothing."""
    g = Yee2D(size, size, S, boundary="pec")
    c = size // 2
    e = []
    for n in range(steps):
        src = [(c, c, gaussian(n, 20.0, 6.0))] if n < 60 else []
        g.step(src)
        if n >= 60:
            e.append(g.energy())
    return np.array(e)


def growth_test(S, size=61, steps=300):
    """Largest |Ez| after `steps` steps of a tiny pulse in a closed box."""
    g = Yee2D(size, size, S, boundary="pec")
    c = size // 2
    peak = 0.0
    for n in range(steps):
        g.step([(c, c, gaussian(n, 15.0, 4.0))])
        peak = max(peak, float(np.abs(g.ez).max()))
        if not np.isfinite(peak) or peak > 1e12:
            break
    return peak


def run_sources(sources, ppw=10, S=0.5, size=301, steps=None, boundary="mur"):
    """Continuous sine sources [(i, j, amplitude, phase_rad)]. Returns the envelope max|Ez|
    over the last period (the steady amplitude at every cell) and the grid."""
    g = Yee2D(size, size, S, boundary)
    period = ppw / S
    if steps is None:
        steps = int(0.8 * size / S)
    waves = [(i, j, a, sine_wave(ppw, S, ph)) for i, j, a, ph in sources]
    env = np.zeros((size, size))
    for n in range(steps):
        g.step([(i, j, a * w(n)) for i, j, a, w in waves])
        if n >= steps - int(period) - 1:
            env = np.maximum(env, np.abs(g.ez))
    return env, g


def boundary_echo(small=121, big=601, steps=500):
    """Size of the spurious echo from the Mur edge, as a fraction of the pulse seen at a probe:
    the same pulse in a small box and in a box so large that no echo can return in time."""
    def run(size):
        c = size // 2
        g = Yee2D(size, size, 0.5, "mur")
        rec = np.zeros(steps)
        for n in range(steps):
            g.step([(c, c, gaussian(n, 40.0, 10.0))])
            rec[n] = g.ez[c + 30, c + 25]
        return rec
    ref = run(big)
    return float(np.abs(run(small) - ref).max() / np.abs(ref).max())


def falloff_exponent(ppw=10, size=401, r_min=20, r_max=70):
    """Fit amplitude ~ r^p along the x axis from a single point source. Expect p about -0.5."""
    c = size // 2
    env, _ = run_sources([(c, c, 1.0, 0.0)], ppw=ppw, size=size, steps=300)
    r = np.arange(r_min, r_max + 1)
    amp = 0.5 * (env[c + r, c] + env[c, c + r])
    return float(np.polyfit(np.log(r), np.log(amp), 1)[0]), r, amp


# %% [markdown]
# ## Step 5: numerical dispersion, the failure case
# A grid cannot carry a wave exactly: on a coarse grid short waves travel a little too slowly.
# Theory for the 1D scheme: sin(w dt / 2) = S sin(k dx / 2), so the phase speed is below c
# by about (k dx)^2 (1 - S^2) / 24. With `ppw` = points per wavelength, k dx = 2 pi / ppw.

# %%
def phase_speed_theory(ppw, S):
    """Numerical phase speed / c of the 1D (and axis-aligned 2D) scheme."""
    kdx = 2 * np.pi / ppw
    return float(2 * np.arcsin(S * np.sin(kdx / 2)) / (S * kdx))


def phase_speed_measured(ppw, S=0.5):
    """Phase speed / c measured from the phase lag of a steady sine between two probes."""
    n_cells, src = 500, 60
    period = ppw / S
    p1, p2 = 200, 200 + 2 * ppw
    steps = int(2 * (p2 - src) / S) + int(8 * period)     # slow short waves need extra time to arrive
    _, h = fdtd_1d(n_cells, steps, S, src, sine_wave(ppw, S), probes=(p1, p2))
    m = steps - int(4 * period)                               # use only the last 4 periods
    t = np.arange(steps)[m:]
    w = 2 * np.pi / period
    ph = [np.angle(np.sum(h[q, m:] * np.exp(-1j * w * t))) for q in (0, 1)]
    dphi = (ph[0] - ph[1]) % (2 * np.pi)                      # lag from probe 1 to probe 2
    dphi += 2 * np.pi * round((2 * np.pi * (p2 - p1) / ppw - dphi) / (2 * np.pi))
    return float((2 * np.pi * (p2 - p1) / ppw) / dphi)


# %% [markdown]
# ## Step 6: two sources make a radiation pattern, and a phase shift steers it
# Two line sources a distance d apart, with phase difference delta, give far-field amplitude
# |cos((k d cos(theta) + delta) / 2)|, with theta measured from the line joining them and
# k = 2 pi / wavelength. Opposite phases (delta = 180 degrees) with d = wavelength / 2 form a
# "dipole-like" figure eight: strongest along the axis, with a null at 90 degrees.
# We measure the pattern on a ring of radius R in the simulation.

# %%
def array_factor(theta, d_over_lambda, delta):
    """Two-element pattern |cos((k d cos(theta) + delta)/2)|; delta in radians."""
    return np.abs(np.cos((2 * np.pi * d_over_lambda * np.cos(theta) + delta) / 2))


def ring_pattern(ppw=10, d_cells=5, delta=np.pi, size=301, R=60, n_angles=72):
    """Pattern measured in FDTD. Source 1 at the left of centre, source 2 (phase LEAD delta) at the right.
    Returns (angles from the line joining the sources, normalised amplitude on the ring)."""
    c = size // 2
    s = [(c - d_cells // 2 - d_cells % 2, c, 1.0, 0.0), (c + d_cells // 2, c, 1.0, -delta)]
    env, _ = run_sources(s, ppw=ppw, size=size, steps=int(1.5 * R / 0.5) + 100)
    # the sources are d_cells apart: the midpoint is the ring centre
    mx = 0.5 * (s[0][0] + s[1][0])
    th = np.linspace(0, 2 * np.pi, n_angles, endpoint=False)
    amp = np.zeros(n_angles)
    for m, a in enumerate(th):
        x, y = mx + R * np.cos(a), c + R * np.sin(a)
        i0, j0 = int(np.floor(x)), int(np.floor(y))
        fx, fy = x - i0, y - j0                                # bilinear interpolation
        amp[m] = ((1 - fx) * (1 - fy) * env[i0, j0] + fx * (1 - fy) * env[i0 + 1, j0]
                  + (1 - fx) * fy * env[i0, j0 + 1] + fx * fy * env[i0 + 1, j0 + 1])
    return th, amp / amp.max()


def beam_phase(theta0_deg, d_over_lambda):
    """Phase difference delta (radians) that points the main beam at theta0 from the pair axis."""
    return -2 * np.pi * d_over_lambda * np.cos(np.radians(theta0_deg))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    v = measured_speed_1d()
    print(f"1D pulse: measured wave speed = {v:.4f} c (theory 1)")

    nodes, env = standing_wave_nodes()
    print(f"standing wave: {len(nodes)} nodes, spacing = {np.diff(nodes).mean():.2f} cells (lambda/2 = 10)")

    e = box_energy_history()
    print(f"closed box: energy from {e.min():.6e} to {e.max():.6e} (relative spread {(e.max() - e.min()) / e.mean():.2e})")
    for S in (0.5, 0.70, 0.72, 0.75):
        print(f"Courant S = {S}: largest |Ez| reached = {growth_test(S):.3g}")

    p, r, amp = falloff_exponent()
    print(f"Mur boundary echo = {100 * boundary_echo():.2f} percent of the pulse (point source, oblique incidence)")
    dx = (299792458.0 / 2.4e9) / 20
    print(f"2.4 GHz, 20 cells per wavelength: dx = {dx * 1000:.2f} mm, largest dt = {courant_dt(dx) * 1e12:.2f} ps, "
          f"steps per period = {1 / 2.4e9 / courant_dt(dx):.1f}")
    print(f"point source in 2D: amplitude ~ r^{p:.3f} (theory -0.5)")

    for ppw in (4, 6, 10, 20):
        print(f"ppw {ppw:2d}: phase speed theory {phase_speed_theory(ppw, 0.5):.4f}, measured {phase_speed_measured(ppw):.4f}")

    th, A = ring_pattern(delta=np.pi)
    ref = array_factor(th, 0.5, np.pi)
    print(f"opposite-phase pair: pattern error (rms) vs theory = {np.sqrt(np.mean((A - ref / ref.max()) ** 2)):.3f}")
    th2, A2 = ring_pattern(delta=beam_phase(60, 0.5))
    side = A2[(th2 > 0) & (th2 < np.pi)]
    print(f"steered pair: strongest direction on the upper half-plane = {np.degrees(th2[(th2 > 0) & (th2 < np.pi)][side.argmax()]):.0f} degrees (aim 60)")

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(np.arange(len(env)), env, color="tab:blue")
    ax[0].plot(nodes, np.zeros_like(nodes), "ro", label="nodes")
    ax[0].set_xlabel("position (cells)")
    ax[0].set_ylabel("envelope of Ez (normalised units)")
    ax[0].set_title("Standing wave in front of a conductor")
    ax[0].legend()
    ax[0].grid(alpha=0.3)
    ppws = np.linspace(3, 30, 100)
    ax[1].plot(ppws, [phase_speed_theory(q, 0.5) for q in ppws], label="theory, S = 0.5")
    ax[1].plot([4, 6, 10, 20], [phase_speed_measured(q) for q in (4, 6, 10, 20)], "ro", label="FDTD measurement")
    ax[1].axvline(10, color="gray", ls=":")
    ax[1].set_xlabel("points per wavelength")
    ax[1].set_ylabel("phase speed / c")
    ax[1].set_title("Numerical dispersion: coarse grids are slow")
    ax[1].legend()
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "validation.png", dpi=110)

    fig2 = plt.figure(figsize=(9, 4))
    a1 = fig2.add_subplot(1, 2, 1)
    env2, _ = run_sources([(150, 150, 1.0, 0.0)], size=301)
    a1.imshow(env2.T, origin="lower", cmap="magma")
    a1.set_title("Point source: amplitude spreads out")
    a1.set_xlabel("x (cells)")
    a1.set_ylabel("y (cells)")
    a2 = fig2.add_subplot(1, 2, 2, projection="polar")
    t_fine = np.linspace(0, 2 * np.pi, 361)
    a2.plot(t_fine, array_factor(t_fine, 0.5, np.pi), label="theory: opposite phases")
    a2.plot(th, A, "o", ms=3, label="FDTD")
    a2.plot(t_fine, array_factor(t_fine, 0.5, beam_phase(60, 0.5)), label="steered to 60 deg")
    a2.plot(th2, A2, "s", ms=3)
    a2.set_title("Two sources: pattern vs angle from their axis", va="bottom")
    a2.legend(loc="lower left", fontsize=7)
    fig2.tight_layout()
    fig2.savefig(OUT / "pattern.png", dpi=110)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint. Then try the mini-project: steer the beam.
