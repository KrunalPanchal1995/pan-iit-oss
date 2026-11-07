"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    n = len(L.SEQ)

    # worked example / hand calculation of the radius of gyration
    rg = L.radius_of_gyration(L.extended_chain(n))
    checks.append((f"worked example: straight chain of 12 beads has Rg = sqrt(143/12) = 3.452 (got {rg:.3f})",
                   abs(rg - np.sqrt(143 / 12)) < 1e-9))
    square = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    checks.append(("hand calculation: four beads on a unit square have Rg = sqrt(1/2)",
                   abs(L.radius_of_gyration(square) - np.sqrt(0.5)) < 1e-12))
    checks.append(("Rg does not change if the whole chain is shifted", abs(L.radius_of_gyration(square + 5.0) - L.radius_of_gyration(square)) < 1e-12))

    # forces: minus the gradient, zero total force, bonds at rest length cost nothing
    pairs = L.make_pairs(L.SEQ)
    rng = np.random.default_rng(5)
    x = np.cumsum(rng.normal(size=(n, 2)) * 0.25 + [0.9, 0.0], axis=0)
    f, u = L.forces(x, pairs)
    checks.append(("internal forces add up to zero", float(np.abs(f.sum(axis=0)).max()) < 1e-8))
    h, worst = 1e-6, 0.0
    for i in range(n):
        for k in range(2):
            xp, xm = x.copy(), x.copy()
            xp[i, k] += h
            xm[i, k] -= h
            worst = max(worst, abs(f[i, k] + (L.forces(xp, pairs)[1] - L.forces(xm, pairs)[1]) / (2 * h)))
    checks.append((f"force equals minus the numerical gradient of U (worst error {worst:.1e})", worst < 1e-3))
    f0, u0 = L.forces(L.extended_chain(n), pairs)
    checks.append(("a straight chain with bond length 1: bonds at rest, only the H-H attraction remains (U < 0)", u0 < 0))

    # H-H attraction: two H beads at the LJ minimum have energy -1; repulsive pairs cost zero beyond 2^(1/6)
    s_hh, s_hp = L.make_pairs("HHH"), L.make_pairs("HHP")
    far = np.array([[0.0, 0.0], [0.5, 0.0], [2.0 ** (1 / 6), 0.0]])
    # bead 0 and bead 2 are the only non-neighbour pair; remove the bond energy by subtracting it
    bond = 0.5 * L.K_BOND * ((0.5 - 1.0) ** 2 + (2.0 ** (1 / 6) - 0.5 - 1.0) ** 2)
    checks.append(("H-H pair at the LJ minimum contributes -1 epsilon", abs(L.forces(far, s_hh)[1] - bond + 1.0) < 1e-9))
    checks.append(("H-P pair beyond 2^(1/6) contributes zero (purely repulsive)", abs(L.forces(far, s_hp)[1] - bond) < 1e-9))
    checks.append(("a non-H sequence has no H-H contacts", L.hh_contacts(L.extended_chain(n), "P" * n) == 0))

    # NVE validation
    ke, pe, _, _ = L.run_nve(steps=2000)
    e = ke + pe
    checks.append((f"NVE: total energy spread is below 3 percent of the mean KE over 20 tau ({(e.max() - e.min()) / ke.mean():.3f})",
                   (e.max() - e.min()) / ke.mean() < 0.03))
    checks.append(("NVE: a smaller time step gives a smaller energy spread", L.nve_energy_spread(0.005, total_time=10.0) < L.nve_energy_spread(0.02, total_time=10.0)))

    # Langevin validation: equipartition
    mid = L.run_langevin(temp=0.5, steps=20000, seed=2)
    tk = L.kinetic_temperature(mid)
    checks.append((f"equipartition: kinetic temperature equals the set temperature within 5 percent (0.5 -> {tk:.3f})", abs(tk / 0.5 - 1) < 0.05))

    ke_mean = mid["ke_mean"]
    checks.append((f"worked example: at T = 0.5 equipartition gives mean KE = (1/2) * 24 * 0.5 = 6.0 (got {ke_mean:.2f})", abs(ke_mean - 6.0) < 0.3))

    # folding behaviour
    cold = L.run_langevin(temp=0.2, steps=20000, seed=1)
    hot = L.run_langevin(temp=0.8, steps=20000, seed=1)
    rc, rh = L.mean_after_burn_in(cold["rg"]), L.mean_after_burn_in(hot["rg"])
    checks.append((f"cold chain (T=0.2) is folded: mean Rg {rc:.2f} below {L.RG_FOLDED}", rc < L.RG_FOLDED))
    checks.append((f"hot chain (T=0.8) is not folded: mean Rg {rh:.2f} above {L.RG_FOLDED}", rh > L.RG_FOLDED))
    checks.append(("cold chain has more H-H contacts than hot chain", L.mean_after_burn_in(cold["contacts"]) > L.mean_after_burn_in(hot["contacts"]) + 2))
    pp = L.run_langevin("P" * n, temp=0.2, steps=20000, seed=1)
    checks.append(("control: a chain with no H beads does not fold even when cold (Rg > 2.0)", L.mean_after_burn_in(pp["rg"]) > 2.0))
    checks.append(("the cold run shrank from the straight chain (Rg 3.45) to a compact shape", cold["rg"][-1] < 2.0 and cold["rg"][0] > 2.5))

    # failure case
    bad = L.run_langevin(temp=0.5, dt=0.15, steps=2000, seed=3)
    checks.append(("failure case: a time step of 0.15 makes the simulation blow up (detected)", bad["ok"] is False))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson3", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
