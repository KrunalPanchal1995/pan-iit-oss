"""Session 3 (Level 3): search a design space, add losses and backlash, check against exact laws.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: search, losses, backlash and a planetary set
# **A. Real-world problem.** A real gearbox must hit its ratio, fit a box (input and output
# shafts in line), survive being started with a torque pulse, and waste as little power as
# possible. Session 2 gave the smallest 1:20 design (17-68, 17-85) but its centre distances
# differ, so the shafts cannot be in line. We search all tooth combinations for one that fits.
#
# **Plan.** (1) a brute-force numpy search with a ratio tolerance and an in-line constraint,
# (2) mesh efficiency, (3) a lumped-inertia simulation with backlash, checked against exact
# laws, (4) the planetary (Willis) relation, (5) a checker for failing designs, (6) the winch.
# Everything here is a simplified educational model, not a validated gearbox design tool.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: brute-force search
# Two stages, four gears N1..N4 (N1 drives N2; N3 sits on the N2 shaft and drives N4). The
# ratio is `N2 N4 / (N1 N3)`. With one module for both stages, input and output shafts are in
# line when the centre distances are equal, i.e. `N1 + N2 = N3 + N4`. We let numpy test every
# (N2, N3, N4) for each N1 at once.

# %%
def search_trains(target, tol, n_min=17, n_max=90, inline=True, sum_max=None):
    """All (N1, N2, N3, N4) with |ratio / target - 1| <= tol, every count in [n_min, n_max].

    inline=True also demands N1 + N2 == N3 + N4. sum_max limits N1 + N2 and N3 + N4.
    Returns an integer array of shape (count, 4).
    """
    n = np.arange(n_min, n_max + 1)
    n2, n3, n4 = np.meshgrid(n, n, n, indexing="ij")
    rows = []
    for n1 in n:
        ok = np.abs(n2 * n4 / (n1 * n3) / target - 1.0) <= tol
        if inline:
            ok &= (n1 + n2) == (n3 + n4)
        if sum_max is not None:
            ok &= ((n1 + n2) <= sum_max) & ((n3 + n4) <= sum_max)
        for i, j, k in np.argwhere(ok):
            rows.append((n1, n[i], n[j], n[k]))
    return np.array(rows, dtype=int).reshape(-1, 4)


def train_ratio(row):
    n1, n2, n3, n4 = row
    return n2 * n4 / (n1 * n3)


# %% [markdown]
# ## Step 2: losses
# Each mesh transmits about 98 percent of the power (a typical figure; real values depend on the
# gears, the lubricant and the load). So a train with n meshes has efficiency `0.98^n`: six
# meshes keep 0.98^6. Power in = power out + loss, always.

# %%
def train_efficiency(n_meshes, eta_mesh=0.98):
    return eta_mesh ** n_meshes


def power_balance(p_in, n_meshes, eta_mesh=0.98):
    """(p_out, p_loss) with p_in = p_out + p_loss."""
    p_out = p_in * train_efficiency(n_meshes, eta_mesh)
    return p_out, p_in - p_out


# %% [markdown]
# ## Step 3: inertia, backlash and a torque pulse
# Refer every shaft to the input: the angle of shaft i divided by its ideal ratio rho_i gives
# phi_i, and its inertia counts as J_i rho_i^2. A tooth mesh is a spring (stiffness k) with a
# dead zone of width b (backlash) and some damping c while the teeth touch. When all teeth are
# in contact the whole train acts as one inertia `J_eff = sum J_i rho_i^2`; for one stage this
# is `J1 + J2 (N1 / N2)^2`. Two exact checks: the momentum `sum J_i rho_i^2 phi_i'` grows by
# exactly the torque impulse (internal mesh forces cancel), and input work = kinetic energy +
# spring energy + energy lost in damping.

# %%
def shaft_ratios(stages):
    """Ideal speed of each shaft divided by the input speed (magnitudes)."""
    rho = [1.0]
    for n_driver, n_driven in stages:
        rho.append(rho[-1] * n_driver / n_driven)
    return np.array(rho)


def reflected_inertia(inertias, stages):
    """J_eff seen at the input shaft."""
    return float(np.sum(np.asarray(inertias) * shaft_ratios(stages) ** 2))


def _contact(delta, b):
    """Dead-zone deflection: zero inside the backlash gap, shifted outside it."""
    return np.where(delta > b / 2, delta - b / 2, np.where(delta < -b / 2, delta + b / 2, 0.0))


def simulate_train(stages, inertias, k, c, backlash, torque, t_pulse, t_end, dt=1e-4):
    """Torque pulse (constant `torque` N m for t_pulse s) on the input of a train, RK4 steps.

    Returns a dict with time t, input-referred speeds w (rows = shafts), mesh torques,
    and the energy terms (input work, kinetic, spring, dissipated).
    """
    jr = np.asarray(inertias, float) * shaft_ratios(stages) ** 2
    n = len(jr)

    def mesh_torque(phi, w):
        d = phi[:-1] - phi[1:]
        f = _contact(d, backlash)
        touching = f != 0.0
        return k * f + c * (w[:-1] - w[1:]) * touching, touching

    def deriv(t, y):
        phi, w = y[:n], y[n:2 * n]
        tau, touching = mesh_torque(phi, w)
        acc = np.zeros(n)
        acc[0] += torque if t < t_pulse else 0.0
        acc[:-1] -= tau
        acc[1:] += tau
        dv = (w[:-1] - w[1:])
        d_diss = np.sum(c * dv ** 2 * touching)
        work = (torque if t < t_pulse else 0.0) * w[0]
        return np.concatenate([w, acc / jr, [d_diss, work]])

    y = np.zeros(2 * n + 2)
    steps = int(round(t_end / dt))
    keep = max(1, steps // 600)
    ts, ys, taus = [0.0], [y.copy()], [0.0]
    peak = 0.0
    for s in range(steps):
        t = s * dt
        k1 = deriv(t, y)
        k2 = deriv(t + dt / 2, y + dt / 2 * k1)
        k3 = deriv(t + dt / 2, y + dt / 2 * k2)
        k4 = deriv(t + dt, y + dt * k3)
        y = y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        tau_now = float(np.max(np.abs(mesh_torque(y[:n], y[n:2 * n])[0])))
        peak = max(peak, tau_now)
        if (s + 1) % keep == 0:
            ts.append((s + 1) * dt)
            ys.append(y.copy())
            taus.append(tau_now)
    ys = np.array(ys)
    phi, w = ys[:, :n], ys[:, n:2 * n]
    spring = 0.5 * k * np.sum(_contact(phi[:, :-1] - phi[:, 1:], backlash) ** 2, axis=1)
    kinetic = 0.5 * np.sum(jr * w ** 2, axis=1)
    return {"t": np.array(ts), "phi": phi, "w": w, "diss": ys[:, 2 * n], "work": ys[:, 2 * n + 1],
            "spring": spring, "kinetic": kinetic, "momentum": w @ jr, "peak_torque": peak,
            "mesh_torque": np.array(taus), "jr": jr}


# %% [markdown]
# ## Step 4: a planetary gear set
# A sun gear (Ns teeth) in the middle, a ring gear (Nr teeth, internal teeth) outside, and
# planet gears on a carrier between them (Np = (Nr - Ns) / 2 teeth). The Willis relation links
# the three speeds: `w_sun Ns + w_ring Nr = w_carrier (Ns + Nr)`. With the ring fixed and the
# sun as input, the carrier is the output and the ratio is `1 + Nr / Ns`. We also derive it
# a second way, from the velocity of the contact points, as a check.

# %%
def willis_carrier(w_sun, w_ring, ns, nr):
    return (w_sun * ns + w_ring * nr) / (ns + nr)


def planet_kinematics(w_sun, w_ring, ns, nr):
    """Carrier and planet speeds from rolling contact (pitch radii proportional to teeth).

    Sun contact point: w_c Rc - w_p rp = w_sun rs.  Ring contact point: w_c Rc + w_p rp = w_ring rr.
    """
    rs, rr = ns / 2.0, nr / 2.0
    rp = (rr - rs) / 2.0
    rc = rs + rp
    a = np.array([[rc, -rp], [rc, rp]])
    w_c, w_p = np.linalg.solve(a, np.array([w_sun * rs, w_ring * rr]))
    return float(w_c), float(w_p)


def planetary_ratio_fixed_ring(ns, nr):
    return 1.0 + nr / ns


def planets_fit(ns, nr, n_planets):
    """Planet teeth must be a whole number, and the planets must space evenly round the sun."""
    return (nr - ns) % 2 == 0 and (ns + nr) % n_planets == 0


# %% [markdown]
# ## Step 5: when a design does not work
# A design can fail for simple reasons: a tooth count is not a whole number, a pinion is below
# the minimum (undercut), the two stages do not have equal centre distances, the gear is too
# big for the box, or the ratio is off target.

# %%
def check_design(teeth, module_mm, target, tol, n_min=17, a_max_mm=None, inline=True):
    """List of problems found with a two-stage design (empty list = it works)."""
    problems = []
    n = list(teeth)
    for i, v in enumerate(n, 1):
        if abs(v - round(v)) > 1e-9:
            problems.append(f"N{i} = {v:g} is not a whole number")
    if problems:
        return problems
    n = [int(round(v)) for v in n]
    for i in (0, 2):
        if n[i] < n_min:
            problems.append(f"pinion N{i + 1} = {n[i]} is below {n_min}: the tooth root would be undercut")
    a12 = module_mm * (n[0] + n[1]) / 2
    a34 = module_mm * (n[2] + n[3]) / 2
    if inline and abs(a12 - a34) > 1e-9:
        problems.append(f"centre distances differ ({a12:g} mm and {a34:g} mm): shafts are not in line")
    if a_max_mm is not None and max(a12, a34) > a_max_mm:
        problems.append(f"centre distance {max(a12, a34):g} mm is more than {a_max_mm:g} mm")
    ratio = n[1] * n[3] / (n[0] * n[2])
    if abs(ratio / target - 1) > tol:
        problems.append(f"ratio {ratio:.3f} is off target {target:g} by more than {100 * tol:g} percent")
    return problems


# %% [markdown]
# ## Step 6: mini-project numbers (hand-crank winch, illustrative)
# A 50 kg load on a rope drum of radius 0.12 m, a crank of radius 0.15 m, at most 100 N of hand
# force, module 2 mm gears, and a gearbox where each mesh stays within 80 mm centre distance
# (so N + N is at most 80). Rope speed must reach 0.10 m/s with the crank at 40 rpm.

# %%
WINCH = dict(mass=50.0, g=9.81, r_drum=0.12, r_crank=0.15, f_max=100.0, module=2.0, a_max_mm=80.0,
             crank_rpm=40.0, v_min=0.10, eta=0.98, n_min=17)


def crank_force(ratio, n_meshes, w=WINCH):
    """Hand force (N) to hold the load steadily: m g r_drum / (ratio eta^n r_crank)."""
    return w["mass"] * w["g"] * w["r_drum"] / (ratio * train_efficiency(n_meshes, w["eta"]) * w["r_crank"])


def rope_speed(ratio, w=WINCH):
    """Rope speed (m/s) at the crank speed in the table."""
    return w["crank_rpm"] * 2 * np.pi / 60 * w["r_drum"] / ratio


def winch_candidates(stages_count, w=WINCH):
    """All designs with `stages_count` (1 or 2) stages meeting the force, speed and size limits."""
    s_max = int(2 * w["a_max_mm"] / w["module"])
    pairs = [(a, b) for a in range(w["n_min"], s_max) for b in range(a, s_max - a + 1)]
    out = []
    if stages_count == 1:
        combos = [(p,) for p in pairs]
    else:
        combos = [(p, q) for p in pairs for q in pairs]
    for stage in combos:
        ratio = 1.0
        for a, b in stage:
            ratio *= b / a
        if crank_force(ratio, len(stage), w) <= w["f_max"] and rope_speed(ratio, w) >= w["v_min"]:
            out.append((sum(a + b for a, b in stage), stage, float(ratio)))
    out.sort()
    return out


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    exact = search_trains(20, 0.0, inline=True)
    tight = search_trains(20, 0.01, inline=True)
    loose = search_trains(20, 0.01, inline=False)
    print("in-line, exact 20:", len(exact), " in-line within 1 percent:", len(tight), " no in-line limit:", len(loose))
    best = tight[np.argmin(tight.sum(axis=1))]
    print("fewest teeth, in line:", best, "ratio", round(train_ratio(best), 4))
    print("efficiency 0.98^6 =", round(train_efficiency(6), 4), " 0.98^2 =", round(train_efficiency(2), 4))

    stages = [(int(best[0]), int(best[1])), (int(best[2]), int(best[3]))]
    J = [1.0e-4, 2.0e-4, 0.05]
    jeff = reflected_inertia(J, stages)
    print("J_eff =", jeff)
    runs = {}
    for name, bk in (("no backlash", 0.0), ("backlash 0.02 rad", 0.02)):
        runs[name] = simulate_train(stages, J, k=100.0, c=0.05, backlash=bk, torque=0.2, t_pulse=0.05, t_end=0.3)
        r = runs[name]
        print(name, "final input speed", round(r["w"][-1, 0], 3), "rad/s; ideal", round(0.2 * 0.05 / jeff, 3),
              "; peak mesh torque", round(r["peak_torque"], 3))

    # figure 1: feasible combinations near the target
    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    ax.plot(loose[:, 1] / loose[:, 0], loose[:, 3] / loose[:, 2], ".", color="lightgray", ms=2, label="within 1 percent")
    ax.plot(tight[:, 1] / tight[:, 0], tight[:, 3] / tight[:, 2], "o", color="tab:red", ms=5, label="and shafts in line")
    r1 = np.linspace(1.0, 5.3, 200)
    ax.plot(r1, 20 / r1, "k-", lw=0.8)
    ax.set_xlabel("stage 1 ratio N2 / N1")
    ax.set_ylabel("stage 2 ratio N4 / N3")
    ax.set_title("Tooth combinations near a 1:20 reduction")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "feasible_map.png", dpi=120)

    # figure 2: speeds, energy and backlash
    fig2, axs = plt.subplots(1, 3, figsize=(11, 3.6))
    for name, r in runs.items():
        axs[0].plot(r["t"] * 1000, r["w"][:, 2], label=name)
    axs[0].set_xlabel("time (ms)")
    axs[0].set_ylabel("load speed referred to input (rad/s)")
    axs[0].set_title("Load speed after a torque pulse")
    axs[0].legend(fontsize=8)
    r = runs["backlash 0.02 rad"]
    axs[1].plot(r["t"] * 1000, r["work"], label="input work")
    axs[1].plot(r["t"] * 1000, r["kinetic"] + r["spring"] + r["diss"], "--", label="kinetic + spring + lost")
    axs[1].set_xlabel("time (ms)")
    axs[1].set_ylabel("energy (J)")
    axs[1].set_title("Energy balance")
    axs[1].legend(fontsize=8)
    bs = np.array([0.0, 0.005, 0.01, 0.02, 0.04])
    pk = [simulate_train(stages, J, 100.0, 0.05, b, 0.2, 0.05, 0.3)["peak_torque"] for b in bs]
    axs[2].plot(bs, pk, "o-")
    axs[2].set_xlabel("backlash b (rad at the input)")
    axs[2].set_ylabel("peak mesh torque (N m)")
    axs[2].set_title("Backlash makes the start-up impact harder")
    for a in axs:
        a.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "dynamics.png", dpi=120)

    print("Willis ring fixed 20/60:", planetary_ratio_fixed_ring(20, 60))
    one = winch_candidates(1)
    two = winch_candidates(2)
    print("winch: one-stage designs", len(one), " two-stage designs", len(two), " first:", two[0])
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Change the target, the tolerance or the backlash, predict what happens, then run it. Answer the
# four questions in the README (section F), then run the checkpoint.
