"""Session 3 (Level 3): a coarse-grained bead-chain "peptide" collapses into a fold under a Langevin thermostat.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: can a chain of beads fold?
# **A. Real-world problem.** In water, the greasy (hydrophobic) parts of a protein hide together
# in the middle while the water-loving (polar) parts stay outside. That crowding is one of the
# main reasons a chain collapses into a compact shape. Here we build the simplest possible
# cartoon of that idea, the **HP model** (H = hydrophobic bead, P = polar bead), and run a real
# molecular dynamics simulation with a thermostat. We then *validate* it and ask at which
# temperature the chain stays folded.
#
# **Honest limits.** This is a 12-bead toy in 2D with made-up reduced units. Real peptides have
# 3D backbones, side chains, water, charges and folding times millions of times longer than
# anything here. Nothing in this repo predicts a real protein, and nothing here is medical or
# drug-design advice. General education only.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
SEQ = "HPHPPHHPHPPH"       # the 12-bead sequence of the mini-project
K_BOND = 100.0              # bond spring constant (epsilon / sigma^2)
R_BOND = 1.0                # bond length (sigma)
RC2 = 2.0 ** (1.0 / 3.0)    # (2^(1/6))^2: where the purely repulsive WCA force stops
DT = 0.01                   # default time step (tau); Session 2 showed the energy error is then about 1 percent
RG_FOLDED = 1.8             # we call the chain "folded" when its mean radius of gyration is below this


# %% [markdown]
# ## Step 1: the model
# * Every bead: mass 1, bonded to its neighbours by a spring (length 1, constant K = 100).
# * Two **H** beads that are not neighbours attract: full Lennard-Jones, well depth 1 (Session 1).
# * Every other non-neighbour pair only repels (the LJ curve cut at its minimum and shifted up
#   by 1 so that it is zero beyond r = 2^(1/6)). This keeps beads from overlapping.
# * Temperature T is in units of epsilon / k_B. There is no solvent: the "water effect" is
#   hidden inside the H-H attraction.

# %%
def make_pairs(seq):
    """Non-neighbour bead pairs (i < j), a flag saying whether the pair attracts (H-H), and the
    matrices that add pair forces / bond forces onto the beads (+1 on bead i, -1 on bead j)."""
    n = len(seq)
    ii, jj = np.triu_indices(n, k=2)
    attract = np.array([seq[a] == "H" and seq[b] == "H" for a, b in zip(ii, jj)])
    m = len(ii)
    pair_sum = np.zeros((n, m))
    pair_sum[ii, np.arange(m)] = 1.0
    pair_sum[jj, np.arange(m)] = -1.0
    bond_sum = np.zeros((n, n - 1))                    # a bond force acts +f on bead k+1 and -f on bead k
    bond_sum[np.arange(n - 1), np.arange(n - 1)] = -1.0
    bond_sum[np.arange(1, n), np.arange(n - 1)] = 1.0
    return ii, jj, attract, pair_sum, bond_sum


def forces(x, pairs):
    """Force on every bead (N, 2) and the potential energy of the bead chain."""
    ii, jj, attract, pair_sum, bond_sum = pairs
    d = x[ii] - x[jj]
    r2 = np.sum(d * d, axis=1)
    s6 = 1.0 / (r2 * r2 * r2)
    active = attract | (r2 < RC2)
    shift = np.where(attract, 0.0, 1.0)                # repulsive pairs are lifted by +1 (WCA)
    u_pair = np.where(active, 4.0 * (s6 * s6 - s6) + shift, 0.0)
    coef = np.where(active, 24.0 * (2.0 * s6 * s6 - s6) / r2, 0.0)
    f = pair_sum @ (coef[:, None] * d)
    b = x[1:] - x[:-1]
    length = np.sqrt(np.sum(b * b, axis=1))
    f += bond_sum @ ((-K_BOND * (length - R_BOND) / length)[:, None] * b)
    return f, float(u_pair.sum() + 0.5 * K_BOND * np.sum((length - R_BOND) ** 2))


def extended_chain(n):
    """A straight chain along x: the unfolded starting shape."""
    x = np.zeros((n, 2))
    x[:, 0] = np.arange(n) * R_BOND
    return x


def radius_of_gyration(x):
    """Root-mean-square distance of the beads from their centre: the size of the chain."""
    return float(np.sqrt(np.mean(np.sum((x - x.mean(axis=0)) ** 2, axis=1))))


def hh_contacts(x, seq, cutoff=1.5):
    """Number of non-neighbour H-H pairs closer than `cutoff` sigma."""
    ii, jj, attract = make_pairs(seq)[:3]
    r = np.linalg.norm(x[ii] - x[jj], axis=1)
    return int(np.sum(attract & (r < cutoff)))


def kinetic_energy(v):
    return 0.5 * float(np.sum(v * v))


# %% [markdown]
# ## Step 2: two kinds of dynamics
# **NVE** (constant energy): plain velocity Verlet from Session 2. Used to *validate* the force
# code: if the total energy is not conserved, the forces are wrong.
#
# **Langevin** (constant temperature): each step is the symmetric "BAOAB" recipe
#
#     B: v += (dt/2) F        A: x += (dt/2) v        O: v = c1 v + c2 * (random normal)
#     A: x += (dt/2) v        B: v += (dt/2) F(new x)
#
# with c1 = exp(-gamma dt) and c2 = sqrt(T (1 - c1^2)). The O step is friction plus random
# kicks, the "heat bath". The kicks are balanced against friction so that the average kinetic
# energy per degree of freedom is T/2 (the **equipartition theorem**), i.e. the kinetic
# temperature T_kin = 2 KE / (d N) equals T. (A Langevin bath does not conserve total momentum,
# so all d N = 24 degrees of freedom count here, unlike the d (N - 1) of Session 2.)

# %%
def run_nve(seq=SEQ, temp=0.3, dt=DT, steps=2000, seed=1):
    """Constant-energy run from the straight chain. Returns arrays of KE and U and the end state."""
    rng = np.random.default_rng(seed)
    pairs = make_pairs(seq)
    x = extended_chain(len(seq))
    v = rng.normal(0.0, np.sqrt(temp), x.shape)
    v -= v.mean(axis=0)
    f, u = forces(x, pairs)
    ke, pe = [kinetic_energy(v)], [u]
    for _ in range(steps):
        v += 0.5 * dt * f
        x += dt * v
        f, u = forces(x, pairs)
        v += 0.5 * dt * f
        ke.append(kinetic_energy(v))
        pe.append(u)
    return np.array(ke), np.array(pe), x, v


def run_langevin(seq=SEQ, temp=0.3, dt=DT, steps=20000, gamma=1.0, seed=1, every=100, x0=None):
    """Langevin (BAOAB) run. Returns a dict of time series sampled every `every` steps
    (keys t, rg, u, ke, contacts), the final positions 'x' and 'ke_mean'. If the run blows up
    (non-finite numbers) it stops early and sets 'ok' to False."""
    rng = np.random.default_rng(seed)
    pairs = make_pairs(seq)
    n = len(seq)
    x = extended_chain(n) if x0 is None else np.array(x0, dtype=float)
    v = rng.normal(0.0, np.sqrt(temp), x.shape)
    f, u = forces(x, pairs)
    c1 = np.exp(-gamma * dt)
    c2 = np.sqrt(temp * (1.0 - c1 * c1))
    out = {"t": [], "rg": [], "u": [], "ke": [], "contacts": []}
    ok = True
    ke_sum, ke_count, burn = 0.0, 0, steps // 4
    np.seterr(all="ignore")           # a too-large time step may overflow: we detect that below
    for i in range(steps):
        v += 0.5 * dt * f
        x += 0.5 * dt * v
        v = c1 * v + c2 * rng.normal(size=v.shape)
        x += 0.5 * dt * v
        f, u = forces(x, pairs)
        v += 0.5 * dt * f
        if i >= burn:
            ke_sum += 0.5 * float(np.sum(v * v))
            ke_count += 1
        if i % every == 0:
            if not (np.isfinite(u) and np.isfinite(v).all()):
                ok = False
                break
            out["t"].append((i + 1) * dt)
            out["rg"].append(radius_of_gyration(x))
            out["u"].append(u)
            out["ke"].append(kinetic_energy(v))
            out["contacts"].append(hh_contacts(x, seq))
    res = {k: np.array(val) for k, val in out.items()}
    res["x"] = x
    res["ok"] = ok
    res["ke_mean"] = ke_sum / max(ke_count, 1)      # average kinetic energy over every step after burn-in
    return res


def mean_after_burn_in(series, fraction=0.25):
    """Average of a time series, ignoring the first `fraction` (the chain is still relaxing)."""
    k = int(len(series) * fraction)
    return float(np.mean(series[k:]))


def kinetic_temperature(run, n=len(SEQ), d=2):
    """Equipartition thermometer for a Langevin run: 2 <KE> / (d N)."""
    return 2.0 * run["ke_mean"] / (d * n)


def mean_rg(seq=SEQ, temp=0.3, seeds=(1, 2, 3, 4), steps=20000, dt=DT):
    """Mean radius of gyration (after burn-in), averaged over several independent runs."""
    return float(np.mean([mean_after_burn_in(run_langevin(seq, temp, dt, steps, seed=s)["rg"]) for s in seeds]))


def nve_energy_spread(dt, total_time=20.0, **kw):
    """(max E - min E) / mean KE for a constant-energy run lasting `total_time` (tau)."""
    ke, pe, _, _ = run_nve(dt=dt, steps=int(round(total_time / dt)), **kw)
    e = ke + pe
    return float((e.max() - e.min()) / ke.mean())


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    cold = run_langevin(temp=0.2, steps=20000, seed=1)
    hot = run_langevin(temp=0.8, steps=20000, seed=1)
    print("extended chain Rg = %.2f sigma (theory sqrt((N^2-1)/12) = %.2f)" % (radius_of_gyration(extended_chain(12)), np.sqrt(143 / 12)))
    for name, r in (("T=0.2", cold), ("T=0.8", hot)):
        print("%s: mean Rg %.2f, mean U %.2f, mean H-H contacts %.1f, T_kin %.3f" % (
            name, mean_after_burn_in(r["rg"]), mean_after_burn_in(r["u"]), mean_after_burn_in(r["contacts"]), kinetic_temperature(r)))

    fig, axs = plt.subplots(1, 3, figsize=(13, 4))
    for ax, (name, r) in zip(axs[:2], (("T = 0.2 (cold)", cold), ("T = 0.8 (hot)", hot))):
        x = r["x"]
        ax.plot(x[:, 0], x[:, 1], "-", color="0.5", lw=2, zorder=1)
        ax.scatter(x[:, 0], x[:, 1], s=260, c=["tab:red" if c == "H" else "tab:blue" for c in SEQ], edgecolor="k", zorder=2)
        for i, c in enumerate(SEQ):
            ax.text(x[i, 0], x[i, 1], c, ha="center", va="center", color="w", fontsize=8, zorder=3)
        ax.set_aspect("equal")
        ax.set_xlabel("x (sigma)")
        ax.set_ylabel("y (sigma)")
        ax.set_title("%s: Rg = %.2f sigma" % (name, radius_of_gyration(x)))
        ax.grid(alpha=0.3)
    axs[2].plot(cold["t"], cold["rg"], label="T = 0.2")
    axs[2].plot(hot["t"], hot["rg"], label="T = 0.8")
    axs[2].axhline(RG_FOLDED, color="k", ls=":", label="folded below %.1f" % RG_FOLDED)
    axs[2].set_xlabel("time t (tau)")
    axs[2].set_ylabel("radius of gyration Rg (sigma)")
    axs[2].set_title("The cold chain collapses; the hot one stays loose")
    axs[2].legend(fontsize=8)
    axs[2].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "collapse.png", dpi=120)

    # validation 1: NVE energy conservation
    ke, pe, _, _ = run_nve(steps=4000)
    e = ke + pe
    print("NVE, dt=0.01, 40 tau: E0 = %.3f, drift (E_end - E0)/|E0| = %.1e, spread (max-min)/mean KE = %.1e" % (
        e[0], (e[-1] - e[0]) / abs(e[0]), (e.max() - e.min()) / ke.mean()))

    # validation 2: equipartition at several set temperatures
    temps = [0.2, 0.5, 1.0]
    tk = [kinetic_temperature(run_langevin(temp=t, steps=20000, seed=2)) for t in temps]
    for t, k in zip(temps, tk):
        print("set T = %.2f -> kinetic temperature %.3f" % (t, k))

    # sensitivity to temperature (two runs per temperature)
    scan_t = [0.2, 0.3, 0.4, 0.5, 0.8]
    scan_rg = [mean_rg(temp=t, seeds=(1, 2)) for t in scan_t]
    for t, g in zip(scan_t, scan_rg):
        print("T = %.2f: mean Rg %.2f" % (t, g))

    # sensitivity to the time step (constant-energy runs of the same length, 20 tau)
    dts = [0.005, 0.01, 0.02, 0.04, 0.08]
    spreads = [nve_energy_spread(dt) for dt in dts]
    for dt, sp in zip(dts, spreads):
        print("dt = %.3f: NVE energy spread / mean KE = %.2e" % (dt, sp))
    print("Langevin with dt = 0.15 stays finite:", run_langevin(temp=0.5, dt=0.15, steps=2000, seed=3)["ok"])

    fig2, axs2 = plt.subplots(1, 2, figsize=(10, 4))
    axs2[0].plot(scan_t, scan_rg, "o-")
    axs2[0].axhline(RG_FOLDED, color="k", ls=":", label="folded below %.1f" % RG_FOLDED)
    axs2[0].set_xlabel("temperature T (epsilon / k_B)")
    axs2[0].set_ylabel("mean radius of gyration (sigma)")
    axs2[0].set_title("Compact when cold, loose when hot")
    axs2[0].legend(fontsize=8)
    axs2[0].grid(alpha=0.3)
    axs2[1].plot([0, 1.1], [0, 1.1], "k:", label="perfect thermostat")
    axs2[1].plot(temps, tk, "o", label="measured kinetic temperature")
    axs2[1].set_xlabel("set temperature T")
    axs2[1].set_ylabel("measured 2<KE>/(d N)")
    axs2[1].set_title("Equipartition check")
    axs2[1].legend(fontsize=8)
    axs2[1].grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "validation.png", dpi=120)

# %% [markdown]
# ## Where this stops
# A flexible 2D chain with one kind of sticky bead is only a cartoon of folding. The Target
# in `promo/` adds more physics; see `promo/roadmap.md`.
