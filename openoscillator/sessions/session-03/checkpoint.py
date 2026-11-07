"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    T0 = L.small_angle_period()
    checks.append(("small-angle period of a 1 m pendulum is 2.0061 s", abs(T0 - 2.0061) < 1e-3))
    checks.append(("the AGM is right: agm(1, sqrt 2) = 1.198140", abs(L.agm(1.0, np.sqrt(2.0)) - 1.1981402347) < 1e-9))
    checks.append(("exact period at 0 degrees equals the small-angle period", abs(L.exact_period(0.0) - T0) < 1e-12))
    t, th, om = L.simulate_pendulum(40.0, dt=0.005, t_end=30.0)
    Tm = L.measure_period(t, th)
    checks.append(("worked example: at 40 degrees the exact period is 2.0689 s and RK4 agrees within 0.0002 s",
                   abs(L.exact_period(40.0) - 2.0689) < 1e-3 and abs(Tm - L.exact_period(40.0)) < 2e-4))
    checks.append(("worked example: the small-angle formula is 3.04 percent low at 40 degrees", abs(100 * L.small_angle_error(40.0) - 3.04) < 0.02))
    a5 = L.angle_for_error(0.05)
    checks.append(("worked example: the small-angle formula is 5 percent low at 51.3 degrees",
                   abs(a5 - 51.35) < 0.05 and abs(L.small_angle_error(a5) - 0.05) < 1e-9))
    checks.append(("the two-term series beats the one-term series at 40 degrees",
                   abs(L.series_period(40.0) - L.exact_period(40.0)) < abs(L.series_period(40.0, terms=1) - L.exact_period(40.0))))
    checks.append(("the small-angle formula is 1 percent low at 22.9 degrees", abs(L.angle_for_error(0.01) - 22.93) < 0.02))
    loss = 86400 * (1 - L.small_angle_period() / L.exact_period(30.0))
    checks.append(("question B: a clock swinging 30 degrees loses 1.711 percent, 1478 s per day",
                   abs(L.small_angle_error(30.0) - 0.01711) < 1e-5 and abs(loss - 1478.4) < 0.5))
    t, th, om = L.simulate_pendulum(0.5, dt=0.005, t_end=10.0)
    checks.append(("validation 1: a 0.5 degree swing matches theta0 cos(w t) within 1e-5 rad",
                   np.max(np.abs(th - L.small_angle_solution(t, 0.5))) < 1e-5))
    checks.append(("validation 2: RK4 keeps the energy to 1e-6 over 20 s (60 degrees, dt = 0.01)", abs(L.energy_drift(60.0, 0.01, "rk4")) < 1e-6))
    c = 0.4
    t, th, om = L.simulate_pendulum(3.0, c=c, dt=0.005, t_end=20.0)
    tp, vp = L.peaks(t, th)
    pred = np.exp(-c / 2 * 2 * np.pi / np.sqrt(L.G - (c / 2) ** 2))
    checks.append(("validation 3: successive maxima shrink by exp(-c Td / 2) within 0.1 percent",
                   len(vp) > 5 and np.allclose(vp[1:6] / vp[:5], pred, rtol=1e-3)))
    checks.append(("failure case: explicit Euler more than doubles the energy over 20 s at dt = 0.005", L.energy_drift(60.0, 0.005, "euler") > 1.0))
    # a linear oscillator under Euler follows (1 + (w dt)^2) per step exactly
    w, dt, n = 3.0, 0.01, 500
    y = np.array([1.0, 0.0])
    for _ in range(n):
        y = np.array([y[0] + dt * y[1], y[1] - dt * w * w * y[0]])
    e_ratio = (0.5 * y[1] ** 2 + 0.5 * w * w * y[0] ** 2) / (0.5 * w * w)
    checks.append(("Euler on a linear oscillator grows the energy by (1 + (w dt)^2) each step", abs(e_ratio / L.euler_growth_factor(w, dt, n) - 1) < 1e-9))
    w0, zeta = 2 * np.pi, 0.05
    Om = np.linspace(0.5, 1.5, 101) * w0
    sim = L.driven_amplitude_simulated(Om, w0, zeta)
    ex = L.driven_amplitude_exact(Om, w0, zeta)
    checks.append(("driven RK4 amplitude matches the resonance formula within 1 percent of the static displacement", np.max(np.abs(sim - ex)) < 1e-3 / w0 ** 2 * 10))
    checks.append(("quality factor: peak / static = 10 for zeta = 0.05", abs(sim.max() * w0 ** 2 - 10.0) < 0.1))
    checks.append(("quality factor from the half-power width is within 5 percent of 10", abs(L.q_from_curve(Om, sim) - 10.0) < 0.5))
    checks.append(("peak sits at w0 sqrt(1 - 2 zeta^2) = 0.9975 w0 (within the grid step)",
                   abs(Om[int(np.argmax(sim))] / w0 - np.sqrt(1 - 2 * zeta ** 2)) < 0.011))
    best, table = L.tune_spring(0.17, 0.03, 2.0, [10, 15, 20, 25, 30, 40, 60], b=0.2)
    checks.append(("mini-project: the best stock spring for 2.0 Hz is 30 N/m (2.053 Hz)", best == 30 and abs(dict(table)[30] - 2.053) < 1e-3))
    ball = L.ballast_for_target(30, 0.17, 0.03, 2.0, b=0.2)
    mm = 0.17 + 0.03 / 3 + ball
    ts, xs, vs = L.simulate_spring_mass(mm, 30.0, 0.2)
    checks.append(("mini-project: 9.6 g of ballast gives 2.000 Hz in the simulation (within 0.2 percent)",
                   abs(ball - 0.00964) < 1e-4 and abs(1 / L.measure_period(ts, xs) - 2.0) < 4e-3))
    try:
        L.ballast_for_target(1.0, 0.17, 0.03, 2.0, b=10.0)
        ok = False
    except ValueError:
        ok = True
    checks.append(("edge: an impossible spring and damping combination is rejected", ok))
    try:
        L.exact_period(180.0)
        ok = False
    except ValueError:
        ok = True
    checks.append(("edge: an amplitude of 180 degrees (balanced upright) is rejected", ok))
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
