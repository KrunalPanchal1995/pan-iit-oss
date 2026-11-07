"""Checkpoint for Session 3. Prints PASS or FAIL."""
import math


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: tau_e = 2.5 ms and tau_m = J R / (k^2 + b R) = 153.8 ms",
                   abs(L.tau_e() - 0.0025) < 1e-12 and abs(L.tau_m() - 0.15385) < 1e-4))
    w_ss, i_ss = L.steady_state(12.0)
    sim = L.simulate(1.0, 1e-4, V=12.0)
    t63 = L.time_to_fraction(sim, 1 - math.exp(-1), w_final=w_ss)
    checks.append(("worked example: simulated time to 63.2 percent speed is 154 ms, within 2 percent of tau_m",
                   abs(w_ss - 230.77) < 0.01 and abs(t63 - L.tau_m()) / L.tau_m() < 0.02))
    checks.append(("worked example: switch-on current peaks near 5.7 A, below the stall limit V/R = 6 A",
                   5.6 < max(sim["i"]) < 6.0))
    checks.append(("energy accounting: electrical in = heat + friction + load + stored (residual < 1e-6 J)",
                   abs(L.energy_residual(sim)) < 1e-6 and sim["E_in"][-1] > 10.0))
    loaded = L.simulate(1.0, 2e-4, V=12.0, T_load=lambda t: 0.1 if t > 0.3 else 0.0)
    checks.append(("energy accounting also holds with a load switched on mid-run", abs(L.energy_residual(loaded)) < 1e-6))
    ref = L.simulate(0.3, 5e-5, V=12.0)["w"][-1]
    e1 = abs(L.simulate(0.3, 2e-3, V=12.0)["w"][-1] - ref)
    e2 = abs(L.simulate(0.3, 1e-3, V=12.0)["w"][-1] - ref)
    checks.append(("RK4 error falls by about 16 when the step is halved (fourth order)", 12.0 < e1 / e2 < 20.0))
    ok = True
    for tl in (0.0, 0.1, 0.2):
        s = L.simulate(1.5, 2e-4, V=12.0, T_load=tl)
        ok &= abs(s["w"][-1] - L.steady_state(12.0, tl)[0]) < 0.05
    checks.append(("simulated steady speed matches the Session 2 torque-speed line for three loads", ok))
    lim = L.simulate(0.6, 1e-4, V=12.0, par={"I_lim": 3.0})
    checks.append(("a 3 A current limit caps the start-up current at 3 A", max(lim["i"]) <= 3.0 + 1e-6 and max(lim["i"]) > 2.9))
    r = L.pwm_run(0.5)
    hand = 0.5 * 0.5 * 12.0 / (5e-3 * 1000.0)
    checks.append(("PWM D = 0.5: mean speed is the speed at 6 V (115.4 rad/s)", abs(r["w_mean"] - 115.38) < 0.2))
    checks.append(("PWM D = 0.5: current ripple matches the hand estimate D(1-D)V/(L f) = 0.6 A within 2 percent",
                   abs(r["i_ripple"] - hand) / hand < 0.02))
    checks.append(("PWM speed ripple is tiny (under 0.1 rad/s) because tau_m is much longer than the period", r["w_ripple"] < 0.1))
    r1 = L.pwm_run(1.0)
    checks.append(("edge case: D = 1 is steady DC with no ripple", r1["i_ripple"] < 1e-9 and abs(r1["w_mean"] - 230.77) < 0.05))
    checks.append(("edge case: D = 0 gives no speed", L.pwm_run(0.0)["w_mean"] < 1e-9))
    lk = L.simulate(0.03, 1e-5, par={"J": 1e6})
    checks.append(("failure case: a locked rotor draws V/R = 6 A and heats at 72 W",
                   abs(lk["i"][-1] - 6.0) < 0.01 and abs(L.stall_heat() - 72.0) < 1e-9 and abs(L.stall_heat(6.0) - 18.0) < 1e-9))
    checks.append(("failure case: +100 K takes 20.8 s with no cooling (assumed 15 J/K)", abs(L.time_to_heat(100.0, 72.0) - 20.833) < 0.01))
    F = 8.0 * 9.81 * (math.sin(math.radians(20)) + 0.03 * math.cos(math.radians(20)))
    d = L.wheel_drive(16, 20)
    checks.append(("worked example: robot at 20 degrees needs 29.05 N; N = 16 climbs at 0.600 m/s with 1.20 A",
                   abs(F - 29.05) < 0.01 and abs(d["F"] - F) < 1e-9 and abs(d["v"] - 0.600) < 0.001 and abs(d["current"] - 1.201) < 0.002))
    w20, best20 = L.window(20)
    checks.append(("sizing sweep: at 20 degrees the ratios 13 to 19 qualify and 16 is the most efficient",
                   w20 == list(range(13, 20)) and best20 == 16))
    checks.append(("sizing sweep: at 30 degrees only N = 18 qualifies, at 35 degrees none", L.window(30)[0] == [18] and L.window(35)[0] == []))
    checks.append(("the steepest slope this motor can climb at 0.5 m/s within 1.5 A is 31 degrees", L.steepest_slope() == 31))
    v_end, t90 = L.climb_sim(16, 20)
    checks.append(("time-domain climb settles at the steady-state speed", abs(v_end - d["v"]) / d["v"] < 0.005 and t90 < 0.3))
    checks.append(("a ratio that is too low cannot start the climb (margin below 1)", L.wheel_drive(1, 30)["start"] < 1.0))
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
