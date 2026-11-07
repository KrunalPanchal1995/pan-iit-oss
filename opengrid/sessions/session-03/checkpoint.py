"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    t, f, pm, _ = L.simulate_frequency()
    checks.append(("worked example: 5% loss, H = 5 s gives RoCoF -0.250 Hz/s by hand (-f0 dP / 2H)",
                   abs(L.rocof_analytic(0.05, 5.0) + 0.25) < 1e-12))
    slope = (f[5] - f[0]) / t[5]
    checks.append(("the RK4 start slope matches the analytic RoCoF within 1 percent", abs(slope - L.rocof_analytic(0.05, 5.0)) < 0.0025))
    checks.append(("worked example: final frequency with governor is 49.881 Hz (analytic -f0 dP / (1/R + D))",
                   abs(f[-1] - 49.881) < 0.002 and abs(f[-1] - (50.0 + L.steady_deviation(0.05, 0.05))) < 0.002))
    checks.append(("the governor power settles at the loss: Pm = 0.0476 pu (0.05 minus D dw)", abs(pm[-1] - 0.0476) < 0.0005))
    _, f0n, _, _ = L.simulate_frequency(governor=False)
    checks.append(("without governor the final frequency is 47.500 Hz (-f0 dP / D)", abs(f0n[-1] - 47.5) < 0.005))
    k = int(round(10.0 / 0.02))
    exact = 50.0 * (1.0 - 0.05 * (1.0 - np.exp(-1.0 * t[k] / (2 * 5.0))))
    checks.append(("without governor the RK4 curve matches the exact exponential at t = 10 s", abs(f0n[k] - exact) < 1e-6))
    ta, fa, _, _ = L.simulate_frequency(dt=0.01)
    checks.append(("halving the time step changes the nadir by under 0.0001 Hz (RK4 converged)", abs(L.nadir(fa) - L.nadir(f)) < 1e-4))
    checks.append(("the governor lifts the nadir from 47.500 Hz to 49.627 Hz at H = 5 s",
                   abs(L.nadir(f0n) - 47.5) < 0.005 and abs(L.nadir(f) - 49.627) < 0.001))
    hs = [2.0, 3.0, 5.0, 8.0]
    nad = [L.nadir_for(h) for h in hs]
    checks.append(("less inertia gives a deeper nadir: 49.461, 49.541, 49.627, 49.692 Hz for H = 2, 3, 5, 8 s",
                   all(np.diff(nad) > 0) and np.allclose(nad, [49.461, 49.541, 49.627, 49.692], atol=0.001)))
    checks.append(("RoCoF scales as 1/H: H = 2 s is 2.5 times steeper than H = 5 s",
                   abs(L.rocof_analytic(0.05, 2.0) / L.rocof_analytic(0.05, 5.0) - 2.5) < 1e-12))
    dn = [L.nadir_for(5.0, droop=r) for r in (0.03, 0.05, 0.08)]
    checks.append(("droop sensitivity: nadir 49.707, 49.627, 49.535 Hz for R = 3, 5, 8 percent",
                   np.allclose(dn, [49.707, 49.627, 49.535], atol=0.001) and all(np.diff(dn) < 0)))
    checks.append(("final values for R = 3 and 8 percent are 49.927 and 49.815 Hz",
                   abs(50.0 + L.steady_deviation(0.05, 0.03) - 49.927) < 0.001 and abs(50.0 + L.steady_deviation(0.05, 0.08) - 49.815) < 0.001))
    f2 = L.simulate_frequency(h_s=2.0, dp=0.10)[1]
    f5 = L.simulate_frequency(h_s=5.0, dp=0.10)[1]
    checks.append(("failure case: a 10% loss at H = 2 s dips to 48.921 Hz and crosses 49 Hz; at H = 5 s the nadir is 49.253 Hz and it does not",
                   L.trips_under_frequency(f2) and not L.trips_under_frequency(f5)
                   and abs(L.nadir(f2) - 48.921) < 0.001 and abs(L.nadir(f5) - 49.253) < 0.001))
    checks.append(("edge: no loss means the frequency stays at exactly 50 Hz", np.allclose(L.simulate_frequency(dp=0.0)[1], 50.0, atol=1e-12)))
    th, fl, ps = L.dc_power_flow([0.0, 0.5, -1.0])
    checks.append(("three-bus DC flow: angles 0, 0.0045, -0.1091 rad; flows -0.0455, 0.5455, 0.4545 pu",
                   np.allclose(th, [0.0, 0.0045, -0.1091], atol=1e-4) and np.allclose(fl, [-0.0455, 0.5455, 0.4545], atol=1e-4)))
    checks.append(("DC flow power balance: slack supplies 0.5 pu, the slack flows add to it, and bus 3 receives 1.0 pu",
                   abs(ps - 0.5) < 1e-12 and abs(fl[0] + fl[1] - 0.5) < 1e-12 and abs(fl[1] + fl[2] - 1.0) < 1e-12
                   and abs(-fl[0] + fl[2] - 0.5) < 1e-12))
    checks.append(("DC flow hand check: with the slack at 0, B theta = P reproduces the injections",
                   abs((th[1] - th[0]) / 0.10 + (th[1] - th[2]) / 0.25 - 0.5) < 1e-12))
    b0 = L.nadir_for(3.0, dp=0.08)
    best = L.smallest_battery(0.08, 3.0)
    below = L.nadir_for(3.0, dp=0.08, batt_pu=best - 0.005)
    checks.append(("mini-project: 8% loss at H = 3 s gives 49.266 Hz with no battery; smallest battery is 0.035 pu (49.531 Hz); 0.030 pu is not enough",
                   abs(b0 - 49.266) < 0.001 and abs(best - 0.035) < 1e-9 and below < 49.5
                   and abs(L.nadir_for(3.0, dp=0.08, batt_pu=best) - 49.531) < 0.001))
    checks.append(("Section F answers: 8% loss at H = 4 s has RoCoF -0.5 Hz/s; 10% loss has -1.25 Hz/s at H = 2 s and -0.5 Hz/s at H = 5 s",
                   abs(L.rocof_analytic(0.08, 4.0) + 0.5) < 1e-12 and abs(L.rocof_analytic(0.10, 2.0) + 1.25) < 1e-12 and abs(L.rocof_analytic(0.10, 5.0) + 0.5) < 1e-12))
    checks.append(("a 4 percent droop gives a final frequency of 49.904 Hz after a 5% loss", abs(50.0 + L.steady_deviation(0.05, 0.04) - 49.904) < 0.001))
    checks.append(("the swing equation uses 2H = 10 s for H = 5 s: with no damping, governor or battery the first-second fall is 0.25 Hz",
                   abs(L.simulate_frequency(governor=False, damp=0.0, t_end=1.0)[1][-1] - 49.75) < 0.002))
    checks.append(("roadmap baselines: 10% loss at H = 2 s with a 0.05 pu battery gives 49.329 Hz; a 10% loss settles at 49.762 Hz; a 20% loss at H = 2 s dips to 47.84 Hz; headroom 0.06 pu would settle at 48.0 Hz",
                   abs(L.nadir_for(2.0, dp=0.10, batt_pu=0.05) - 49.329) < 0.001 and abs(50.0 + L.steady_deviation(0.10, 0.05) - 49.762) < 0.001
                   and abs(L.nadir_for(2.0, dp=0.20) - 47.84) < 0.005 and abs(50.0 * (1.0 - (0.10 - 0.06) / 1.0) - 48.0) < 1e-9))
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
