"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # hand calculation of a temperature: v = (1,0), (0,1), (-1,-1): KE = 2, dof = 2*(3-1) = 4, T = 2*2/4 = 1
    v = np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, -1.0]])
    checks.append(("hand calculation: temperature of three beads is 1.0", abs(L.temperature(v) - 1.0) < 1e-12))

    # worked example: omega = 10, 1 percent energy error needs dt < 0.02 (error = (omega dt)^2 / 4)
    e_ok, e_bad = L.verlet_energy_error(10.0, 0.019), L.verlet_energy_error(10.0, 0.021)
    checks.append((f"worked example: omega=10 keeps the energy error under 1 percent for dt=0.019 but not dt=0.021 ({e_ok:.4f}, {e_bad:.4f})",
                   e_ok < 0.01 < e_bad))
    checks.append(("small-step rule: error is close to (omega dt)^2 / 4",
                   abs(L.verlet_energy_error(10.0, 0.01) - 0.0025) < 2e-4))

    # explicit Euler multiplies the energy by exactly (1 + omega^2 dt^2) each step
    tr = L.oscillator_energy_trace(10.0, 0.002, 500, "euler")
    checks.append(("Euler energy grows by exactly (1 + (omega dt)^2) per step", abs(tr[-1] - (1 + (10 * 0.002) ** 2) ** 500) < 1e-6 * tr[-1]))
    checks.append(("Verlet keeps the energy bounded where Euler does not",
                   L.verlet_energy_error(10.0, 0.002, periods=60) < 0.001 and L.oscillator_energy_trace(10.0, 0.002, 6000, "euler")[-1] > 10))
    # limit: omega dt > 2 is unstable
    checks.append(("limit: omega dt = 2.1 blows up, omega dt = 1.9 does not", L.verlet_energy_error(10.0, 0.21) > 1e3 and L.verlet_energy_error(10.0, 0.19) < 1.5))

    # chain: forces are minus the gradient of U, and add up to zero
    rng = np.random.default_rng(3)
    x = np.cumsum(rng.normal(size=(5, 2)) * 0.3 + [1.0, 0.0], axis=0)
    f, u = L.chain_forces(x)
    checks.append(("internal forces add up to zero (Newton's third law)", float(np.abs(f.sum(axis=0)).max()) < 1e-9))
    h, ok = 1e-6, True
    for i in range(5):
        for k in range(2):
            xp, xm = x.copy(), x.copy()
            xp[i, k] += h
            xm[i, k] -= h
            ok &= abs(f[i, k] + (L.chain_forces(xp)[1] - L.chain_forces(xm)[1]) / (2 * h)) < 1e-3
    checks.append(("chain force equals minus the numerical gradient of U", bool(ok)))

    # initial state has the requested temperature and zero momentum
    x0, v0 = L.initial_state(6, 0.5, 1)
    checks.append(("initial temperature is exactly 0.5 and momentum is zero", abs(L.temperature(v0) - 0.5) < 1e-12 and float(np.abs(v0.sum(axis=0)).max()) < 1e-12))

    # NVE run: energy conserved, momentum conserved
    t, ke, pe, xf, vf = L.run_nve()
    e = ke + pe
    checks.append((f"NVE: total energy drifts by less than 0.1 percent over 4000 steps ({abs(e[-1] - e[0]) / abs(e[0]):.1e})", abs(e[-1] - e[0]) / abs(e[0]) < 1e-3))
    checks.append(("NVE: total momentum stays zero", float(np.abs(vf.sum(axis=0)).max()) < 1e-9))

    # time reversibility: go forward, flip the velocities, come back
    x, v = L.initial_state()
    f, _ = L.chain_forces(x)
    xs, vs = x.copy(), v.copy()
    for _ in range(500):
        xs, vs, f, _ = L.verlet_step(xs, vs, f, 0.005)
    vs = -vs
    for _ in range(500):
        xs, vs, f, _ = L.verlet_step(xs, vs, f, 0.005)
    checks.append(("Verlet is time-reversible: 500 steps forward then back returns to the start", float(np.abs(xs - x).max()) < 1e-6))

    # smaller time step, smaller energy fluctuation
    checks.append(("a smaller time step gives a smaller energy fluctuation", L.energy_fluctuation(0.002, total_time=10.0) < L.energy_fluctuation(0.01, total_time=10.0)))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson2", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
