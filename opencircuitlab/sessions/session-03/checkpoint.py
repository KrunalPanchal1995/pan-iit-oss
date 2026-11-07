"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    v, j = L.solve_network(**L.TWO_LOOP)
    checks.append(("worked example: nodal solver reproduces the hand-solved two-loop circuit (V_A = 6.545 V, I1 = 34.55 mA, I2 = -12.73 mA)",
                   abs(v[1] - 6.54545) < 1e-4 and abs(j[0] - 0.034545) < 1e-6 and abs(j[1] + 0.012727) < 1e-6))
    res = L.TWO_LOOP["resistors"]
    cur = L.branch_currents(v, res)
    checks.append(("KCL: the branch currents at node A sum to zero", abs(cur[0] + cur[1] - cur[2]) < 1e-12))
    s, d = L.power_balance(v, j, res, L.TWO_LOOP["vsources"])
    checks.append(("power balance: supplied equals dissipated (294.5 mW)", abs(s - d) < 1e-12 and abs(s - 0.2945455) < 1e-6))
    # a random ladder: power balance and KCL must hold for any network
    rng = np.random.default_rng(3)
    rs = [(a, b, float(rng.uniform(50, 500))) for a, b in [(1, 2), (2, 3), (3, 4), (1, 3), (2, 4), (4, 0), (1, 0), (3, 0)]]
    vs = [(1, 0, 9.0)]
    v2, j2 = L.solve_network(4, rs, vs, [(0, 3, 0.01)])
    s2, d2 = L.power_balance(v2, j2, rs, vs, [(0, 3, 0.01)])
    checks.append(("power balance on a random 4-node network with a current source", abs(s2 - d2) < 1e-9))
    vth, rth = L.thevenin(**L.DIVIDER_12V, port=(2, 0))
    checks.append(("hand calculation: Thevenin of the 12 V divider is 8 V and 666.7 ohm",
                   abs(vth - 8.0) < 1e-9 and abs(rth - 2000.0 / 3.0) < 1e-6))
    pmax = vth ** 2 / (4 * rth)
    checks.append(("maximum power is 24 mW at R_L = R_th (formula)", abs(pmax - 0.024) < 1e-9 and abs(L.load_power(vth, rth, rth) - pmax) < 1e-12))
    rl = np.linspace(100, 3000, 2901)
    pn = np.array([L.load_power_by_nodal(x) for x in rl])
    checks.append(("numerical sweep with the real nodal solver peaks within 1 ohm of R_th", abs(rl[np.argmax(pn)] - rth) <= 1.0))
    checks.append(("worked example: a 1 kohm load gets 23.04 mW, and the Thevenin and nodal powers agree", abs(L.load_power(vth, rth, 1000.0) - 0.02304) < 1e-9 and abs(L.load_power_by_nodal(1000.0) - 0.02304) < 1e-9))
    checks.append(("bridge balances when R1 R4 = R2 R3 (any supply voltage)",
                   abs(L.bridge_out(5, 1000, 2000, 1500, 3000)) < 1e-12 and abs(L.bridge_out(1, 1000, 2000, 1500, 3000)) < 1e-12))
    checks.append(("bridge formula agrees with the general nodal solver", abs(L.bridge_out(5, 900, 1100, 1300, 700) - L.bridge_by_nodal(5, 900, 1100, 1300, 700)) < 1e-12))
    small = L.bridge_out(5.0, 1000, 1000, 1010, 1000)
    checks.append(("small change: 1 percent in one arm gives about Vs/4 * 1 percent = 12.5 mV", abs(small - 0.0125) < 1e-4))
    mc = L.monte_carlo_bridge()
    checks.append(("Monte Carlo spread with 5 percent resistors matches the prediction (72 mV) within 3 percent",
                   abs(mc.std() / L.predicted_offset_std() - 1) < 0.03))
    checks.append(("1 percent resistors give a 5 times smaller spread", abs(L.monte_carlo_bridge(tol=0.01).std() / mc.std() - 0.2) < 0.01))
    try:
        L.solve_network(3, [(1, 0, 10.0), (2, 3, 5.0)], [(1, 0, 5.0)])
        ok = False
    except ValueError:
        ok = True
    checks.append(("failure: a floating node (2-3 not connected to ground) gives a singular matrix error", ok))
    try:
        L.solve_network(1, [(1, 0, 10.0)], [(1, 0, 5.0), (1, 0, 6.0)])
        ok = False
    except ValueError:
        ok = True
    checks.append(("failure: two different ideal sources across the same nodes are rejected", ok))
    try:
        L.solve_network(1, [(1, 0, 0.0)], [(1, 0, 5.0)])
        ok = False
    except ValueError:
        ok = True
    checks.append(("failure: a 0 ohm resistor is rejected", ok))
    i_sc, heat = L.short_circuit(9.0, 1.0, 0.01)
    checks.append(("short circuit of a 9 V pack with 1 ohm internal resistance: 8.9 A and 79 W", abs(i_sc - 8.91) < 0.01 and abs(heat - 79.4) < 0.1))
    ok_vs = [k / 10 for k in range(10, 51)
             if float(L.sensor_bridge_out(k / 10, 100)) >= 0.1 and float(L.sensor_power(k / 10, 100)) <= 1e-3]
    checks.append(("mini-project: supply voltages 1.3 V to 2.0 V meet 100 mV output and 1 mW sensor heat; 5 V fails",
                   ok_vs[0] == 1.3 and ok_vs[-1] == 2.0 and float(L.sensor_power(5.0, 100)) > 1e-3))
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
