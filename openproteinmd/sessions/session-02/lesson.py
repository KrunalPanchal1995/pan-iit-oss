"""Session 2 (Level 2): velocity Verlet, a small chain, energy conservation, temperature and the time step.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: stepping a chain forward without cheating
# **A. Real-world problem.** To follow atoms we must take small time steps. If the step rule is
# poor, the computer atoms gain energy out of nothing and the simulation "explodes". If the
# steps are too small, the run takes forever. How accurate must the step rule be, how big can
# the step be, and how do we know the simulation is behaving? (Toy model in reduced units,
# general education only: sigma = epsilon = m = 1, time unit tau, temperature in epsilon / k_B.)

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
K_BOND = 100.0     # bond spring constant (epsilon / sigma^2)
R_BOND = 1.0       # bond rest length (sigma)


# %% [markdown]
# ## Step 1: the stepping rule, tested on one spring
# A single ball on a spring has an exact answer, so it is the perfect test bench. The ball has
# mass 1, spring constant k, so omega = sqrt(k) and the exact energy is constant.
#
# Velocity Verlet (one step of length dt):
#
#     v_half = v + (dt/2) a(x)            half kick
#     x_new  = x + dt v_half              drift
#     v_new  = v_half + (dt/2) a(x_new)   half kick with the new force
#
# For comparison, the naive "explicit Euler" rule is x_new = x + dt v, v_new = v + dt a(x).

# %%
def oscillator_energy_trace(omega, dt, steps, method="verlet"):
    """Energy E/E0 after each step for x'' = -omega^2 x, started at x=1, v=0."""
    x, v = 1.0, 0.0
    e0 = 0.5 * omega ** 2
    out = [1.0]
    for _ in range(steps):
        if method == "verlet":
            v += 0.5 * dt * (-omega ** 2 * x)
            x += dt * v
            v += 0.5 * dt * (-omega ** 2 * x)
        else:  # explicit Euler
            x, v = x + dt * v, v + dt * (-omega ** 2 * x)
        out.append((0.5 * v * v + 0.5 * omega ** 2 * x * x) / e0)
        if out[-1] > 1e6:        # blown up: stop
            break
    return np.array(out)


def verlet_energy_error(omega, dt, periods=20):
    """Largest relative energy error |E/E0 - 1| over a number of oscillation periods."""
    steps = int(np.ceil(periods * 2 * np.pi / (omega * dt)))
    tr = oscillator_energy_trace(omega, dt, steps)
    return float(np.max(np.abs(tr - 1.0)))


# %% [markdown]
# ## Step 2: a chain of beads
# N beads in a plane, neighbours joined by springs (bonds), every pair that is not a
# neighbour interacts through Lennard-Jones (Session 1). Forces from the potential energy:
#
#     U = sum over bonds of (1/2) K (l - R)^2  +  sum over non-neighbour pairs of LJ(r)

# %%
def chain_forces(x, k=K_BOND, r0=R_BOND):
    """Forces (N, d) and potential energy U of a bead chain."""
    n = len(x)
    d = x[:, None, :] - x[None, :, :]
    r2 = np.sum(d * d, axis=-1) + np.eye(n)
    s6 = 1.0 / r2 ** 3
    nonnb = np.abs(np.subtract.outer(np.arange(n), np.arange(n))) >= 2
    coef = np.where(nonnb, 24.0 * (2.0 * s6 * s6 - s6) / r2, 0.0)
    f = np.sum(coef[:, :, None] * d, axis=1)
    u = 0.5 * np.sum(np.where(nonnb, 4.0 * (s6 * s6 - s6), 0.0))
    b = x[1:] - x[:-1]
    length = np.linalg.norm(b, axis=1)
    fb = (-k * (length - r0) / length)[:, None] * b
    f[1:] += fb
    f[:-1] -= fb
    return f, u + 0.5 * k * np.sum((length - r0) ** 2)


def verlet_step(x, v, f, dt):
    """One velocity-Verlet step. Returns the new x, v, f and the potential energy."""
    v = v + 0.5 * dt * f
    x = x + dt * v
    f, u = chain_forces(x)
    v = v + 0.5 * dt * f
    return x, v, f, u


def kinetic_energy(v):
    return 0.5 * float(np.sum(v * v))


def temperature(v):
    """Kinetic temperature: 2 KE / (number of degrees of freedom). With the centre-of-mass
    motion removed there are d (N - 1) degrees of freedom (d = 2 here)."""
    n, d = v.shape
    return 2.0 * kinetic_energy(v) / (d * (n - 1))


def initial_state(n=6, temp=0.5, seed=1):
    """Straight chain in the x direction; random velocities with zero total momentum scaled
    to exactly the requested kinetic temperature."""
    rng = np.random.default_rng(seed)
    x = np.zeros((n, 2))
    x[:, 0] = np.arange(n) * R_BOND
    v = rng.normal(size=(n, 2))
    v -= v.mean(axis=0)
    v *= np.sqrt(temp / temperature(v))
    return x, v


def run_nve(n=6, temp=0.5, dt=0.005, steps=4000, seed=1):
    """Run constant-energy dynamics. Returns time, KE, U arrays and the final x, v."""
    x, v = initial_state(n, temp, seed)
    f, u = chain_forces(x)
    ke = [kinetic_energy(v)]
    pe = [u]
    for _ in range(steps):
        x, v, f, u = verlet_step(x, v, f, dt)
        ke.append(kinetic_energy(v))
        pe.append(u)
    return np.arange(steps + 1) * dt, np.array(ke), np.array(pe), x, v


def energy_fluctuation(dt, total_time=20.0, **kw):
    """(max E - min E) divided by the mean kinetic energy, over a run of fixed length."""
    steps = int(round(total_time / dt))
    _, ke, pe, _, _ = run_nve(dt=dt, steps=steps, **kw)
    e = ke + pe
    return float((e.max() - e.min()) / ke.mean())


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t, ke, pe, _, _ = run_nve()
    e = ke + pe
    print("chain of 6 beads, dt = 0.005, 20 tau: E0 = %.4f, relative drift (E_end - E0)/E0 = %.2e" % (e[0], (e[-1] - e[0]) / abs(e[0])))
    print("temperature at start %.3f; time-average of kinetic temperature %.3f" % (2 * ke[0] / 10, 2 * ke.mean() / 10))

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    axs[0].plot(t, ke, label="kinetic")
    axs[0].plot(t, pe - pe[0], label="potential (relative to start)")
    axs[0].plot(t, e - e[0], "k", label="total minus start")
    axs[0].set_xlabel("time t (tau)")
    axs[0].set_ylabel("energy (epsilon)")
    axs[0].set_title("Energy flows between KE and U; the total stays flat")
    axs[0].legend(fontsize=8)
    axs[0].grid(alpha=0.3)
    dts = [0.001, 0.002, 0.005, 0.01, 0.02]
    fl = [energy_fluctuation(d) for d in dts]
    for d, f_ in zip(dts, fl):
        print("dt = %.3f  energy fluctuation / mean KE = %.2e" % (d, f_))
    axs[1].loglog(dts, fl, "o-", label="measured")
    axs[1].loglog(dts, fl[0] * (np.array(dts) / dts[0]) ** 2, "k:", label="slope 2, for comparison")
    axs[1].set_xlabel("time step dt (tau)")
    axs[1].set_ylabel("(max E - min E) / mean KE")
    axs[1].set_title("Energy error falls steeply as dt shrinks")
    axs[1].legend(fontsize=8)
    axs[1].grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "chain_energy.png", dpi=120)

    omega = 10.0
    fig2, ax2 = plt.subplots(figsize=(6.5, 3.8))
    for name, method, dt in (("Verlet dt=0.05", "verlet", 0.05), ("Euler dt=0.002", "euler", 0.002)):
        tr = oscillator_energy_trace(omega, dt, 3000, method)
        ax2.plot(np.arange(len(tr)) * dt, tr, label=name)
    ax2.set_ylim(0, 4)
    ax2.set_xlabel("time t (tau)")
    ax2.set_ylabel("E / E0")
    ax2.set_title("One spring (omega = 10): Verlet wobbles, Euler climbs")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "verlet_vs_euler.png", dpi=120)
    for dt in (0.01, 0.05, 0.1, 0.19, 0.21):
        print("omega=10, dt=%.2f (omega*dt=%.1f): max energy error %.3g" % (dt, omega * dt, verlet_energy_error(omega, dt)))
    print("Euler, omega=10, dt=0.002, 3000 steps: E/E0 = %.2f" % oscillator_energy_trace(omega, 0.002, 3000, "euler")[-1])

# %% [markdown]
# ## Where this stops
# We now have a trustworthy stepping rule and a thermometer. Session 3 adds a thermostat and
# makes some beads sticky, so that the chain can collapse into a fold.
