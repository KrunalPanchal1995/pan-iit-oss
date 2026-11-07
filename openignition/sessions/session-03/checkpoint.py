"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    p = L.make_params()
    T0 = 1000.0
    ref = L.reference_delay(T0, p)
    checks.append(("reference delay by quadrature at 1000 K is 1.1920 ms",
                   abs(ref * 1e3 - 1.1920) < 0.0005))

    lam = -L.rate_k(2500.0, p)
    ev = np.linalg.eigvals(L.jacobian(np.array([2500.0, 1e-12]), p)).real.min()
    dt_lim = 2.785 / abs(lam)
    checks.append(("worked example: the fast decay rate after ignition is 1.84e6 per second and the RK4 step limit 2.785/rate = 1.52 microseconds",
                   abs(ev / lam - 1) < 1e-6 and abs(lam / -1.835e6 - 1) < 0.002 and abs(dt_lim * 1e6 - 1.517) < 0.01))
    tau1, y1, n1, ok1 = L.rk4_fixed(T0, p, 1.45e-6, 3e-3)
    tau2, y2, n2, ok2 = L.rk4_fixed(T0, p, 1.6e-6, 3e-3)
    tau3, y3, n3, ok3 = L.rk4_fixed(T0, p, 5e-6, 3e-3)
    checks.append(("worked example: just under the limit (1.45 us) RK4 ends correctly at 2500 K with the fuel gone",
                   ok1 and abs(y1[0] - 2500.0) < 0.5 and y1[1] < 1e-10))
    checks.append(("just over the limit (1.6 us) RK4 stays finite but ends wrong: 59 thousandths of the fuel is left",
                   ok2 and y2[1] > 0.05 and y2[0] < 2450.0))
    checks.append(("at 5 us RK4 blows up after ignition, yet the delay it reported before was right to 0.01 percent",
                   (not ok3) and abs(tau3 / ref - 1) < 1e-4))
    checks.append(("at 1 ms (a step as long as the delay) RK4 finds no ignition at all",
                   L.rk4_fixed(T0, p, 1e-3, 3e-3)[0] is None))

    a = L.rk4_adaptive(T0, p, 30e-3, 1e-4)
    b = L.trapezoid_adaptive(T0, p, 30e-3, 1e-4)
    checks.append(("both adaptive solvers find the delay within 0.01 percent of the reference",
                   abs(a["tau"] / ref - 1) < 1e-4 and abs(b["tau"] / ref - 1) < 1e-4))
    checks.append(("covering 30 ms: explicit RK4 needs over 9000 steps, implicit trapezoid under 200",
                   a["steps"] > 9000 and b["steps"] < 200 and a["steps"] / b["steps"] > 50))
    checks.append(("RK4's mean step (3.1 us) stays near its stability limit, not near the accuracy need",
                   1.5e-6 < 30e-3 / a["steps"] < 6e-6))
    b3 = L.trapezoid_adaptive(T0, p, 3e-3, 1e-4)
    a3 = L.rk4_adaptive(T0, p, 3e-3, 1e-4)
    checks.append(("stiffness: 10 times longer horizon costs RK4 about 15 times more steps but the trapezoid only a few percent more",
                   a["steps"] / a3["steps"] > 10 and b["steps"] < 1.1 * b3["steps"]))

    errs, steps = [], []
    for rtol in (1e-2, 1e-3, 1e-5):
        r = L.trapezoid_adaptive(T0, p, 5e-3, rtol)
        errs.append(abs(r["tau"] / ref - 1))
        steps.append(r["steps"])
    checks.append(("convergence: tolerance 1e-2 gives error below 0.1 percent, 1e-5 below 0.001 percent, steps grow",
                   errs[0] < 1e-3 and errs[2] < 1e-5 and steps[0] < steps[1] < steps[2]))

    be1 = L.backward_euler_fixed(T0, p, 1e-5, 3e-3)
    be2 = L.backward_euler_fixed(T0, p, 1e-4, 3e-3)
    be3 = L.backward_euler_fixed(T0, p, 1e-3, 3e-3)
    e1, e2, e3 = (x[0] / ref - 1 for x in (be1, be2, be3))
    checks.append(("backward Euler never blows up (ends at 2500 K at 1 ms) but a long step smears the delay: -77.6 percent",
                   abs(be3[1][0] - 2500.0) < 1.0 and abs(e3 + 0.776) < 0.005))
    checks.append(("backward Euler is first order: a 10 times smaller step gives about 10 times smaller error",
                   8 < e2 / e1 < 12 and abs(e1 + 0.0233) < 0.002))

    Ea_s = L.log_sensitivity(lambda x: L.delay_for(T0, Ea=x), 150e3)
    checks.append(("sensitivity to Ea is +16.9 (a 1 percent larger Ea lengthens the delay by 17 percent), near Ea/(R T0) = 18.0",
                   abs(Ea_s - 16.90) < 0.05 and Ea_s < 150e3 / (L.R_GAS * T0)))
    f_s = L.log_sensitivity(lambda x: L.delay_for(T0, dT=x), 1500.0)
    checks.append(("richer mixture (larger heat release) shortens the delay: sensitivity -1.05, close to the textbook -1",
                   abs(f_s + 1.053) < 0.01))
    checks.append(("pressure with exponent 1: 10 atm gives exactly a tenth of the 1 atm delay (0.1192 ms)",
                   abs(L.delay_at_pressure(T0, 10.0) * 10.0 / ref - 1) < 1e-9 and abs(L.delay_at_pressure(T0, 10.0) * 1e3 - 0.1192) < 0.0005))

    ca = L.critical_Ta_analytic(500.0)
    cf = L.critical_Ta_numeric(500.0, frozen=True)
    cb = L.critical_Ta_numeric(500.0, frozen=False)
    checks.append(("Semenov at h = 500 per second: analytic 905.7 K, simulated with fixed fuel within 5 K above it",
                   abs(ca - 905.7) < 0.2 and 0 < cf - ca < 5.0))
    checks.append(("fuel burn-up raises the simulated critical temperature by about 16 K (924.7 K), so the analytic criterion is a lower bound",
                   abs(cb - 924.7) < 1.0 and cb - cf > 10))
    checks.append(("Semenov edge: psi equals 1/e at the analytic critical temperature",
                   abs(L.semenov_psi(ca, 500.0) - np.exp(-1.0)) < 1e-6))

    T0B = np.arange(800.0, 1301.0, 50.0)
    tB = L.delay_table(T0B, **L.FUEL_B)
    refB = np.array([L.reference_delay(T, L.make_params(**L.FUEL_B)) for T in T0B])
    bB, aB, r2B = L.fit_line(T0B, tB)
    checks.append(("mini-project: toy fuel B table matches the quadrature reference to 0.1 percent at all 11 temperatures",
                   bool(np.all(np.abs(tB / refB - 1) < 1e-3))))
    checks.append(("mini-project: fit slope 11.19, R^2 above 0.9999, delay 1 ms at 1153 K",
                   abs(bB - 11.19) < 0.02 and r2B > 0.9999 and abs(L.temperature_for_delay(T0B, tB, 1e-3) - 1153.4) < 1.0))
    checks.append(("edge: if burning everything cannot add 400 K the solver reports no event",
                   L.trapezoid_adaptive(T0, L.make_params(dT=300.0), 2e-3, 1e-4, stop_at_event=True)["tau"] is None))
    lam9 = L.rate_k(2400.0, p)
    checks.append(("hand calculation: starting at 900 K the final temperature is 2400 K, the decay rate 1.36e6 per second, the RK4 limit 2.05 us",
                   abs(lam9 / 1.36e6 - 1) < 0.005 and abs(2.785 / lam9 * 1e6 - 2.05) < 0.02))
    a_lo = L.rk4_adaptive(T0, p, 30e-3, 1e-2)
    a_hi = L.rk4_adaptive(T0, p, 30e-3, 1e-6)
    b_lo = L.trapezoid_adaptive(T0, p, 30e-3, 1e-2)
    b_hi = L.trapezoid_adaptive(T0, p, 30e-3, 1e-6)
    checks.append(("graph reading: RK4 steps hardly change with tolerance (within 6 percent from 1e-2 to 1e-6) while the trapezoid needs 7 times more",
                   max(a_lo["steps"], a_hi["steps"]) / min(a_lo["steps"], a_hi["steps"]) < 1.06 and b_hi["steps"] / b_lo["steps"] > 7))
    a_mid = L.rk4_adaptive(T0, p, 30e-3, 1e-3)
    b_mid = L.trapezoid_adaptive(T0, p, 30e-3, 1e-3)
    checks.append(("design: at tolerance 1e-3 the trapezoid is within 0.1 percent using 1540 RHS calls, RK4 needs over 100 times more",
                   abs(b_mid["tau"] / ref - 1) < 1e-3 and b_mid["rhs_calls"] < 2000 and a_mid["rhs_calls"] > 100 * b_mid["rhs_calls"]))
    T0_s = L.log_sensitivity(lambda T: L.delay_for(T), 1000.0)
    checks.append(("sensitivity to the start temperature is -15.9: one percent hotter (10 K) shortens the delay by about 16 percent",
                   abs(T0_s + 15.90) < 0.05))
    checks.append(("roadmap facts: at 0.1 atm the shipped model still ignites (11.9 ms) and the trapezoid needs 457 steps for 1e-6",
                   abs(L.delay_at_pressure(T0, 0.1) * 1e3 - 11.92) < 0.01 and b_hi["steps"] == 457 and abs(b_hi["tau"] / ref - 1) < 1e-6))
    t100, y100, n100, ok100 = L.rk4_fixed(T0, p, 1e-4, 3e-3)
    checks.append(("at 100 us RK4's delay is 0.27 percent late, 13 steps are taken, and the state still blows up",
                   abs(t100 / ref - 1 - 0.0027) < 0.0003 and n100 == 13 and not ok100))
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
