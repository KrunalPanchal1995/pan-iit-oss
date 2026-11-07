"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    Fp, Lc = 200e3, 0.8
    m, v0 = 1000.0, L.kmh_to_ms(56.0)

    # the force curve
    checks.append(("force is zero before impact and half of Fp halfway up the ramp",
                   float(L.crumple_force(-0.1, Fp, Lc)) == 0.0 and abs(float(L.crumple_force(L.XR / 2, Fp, Lc)) - Fp / 2) < 1e-6))
    checks.append(("force is the plateau Fp between the ramp and Lc", abs(float(L.crumple_force(0.4, Fp, Lc)) - Fp) < 1e-9))
    checks.append(("force jumps up beyond Lc (stiff cell)", float(L.crumple_force(Lc + 0.01, Fp, Lc)) > 2 * Fp))
    xs = np.linspace(0.0, 0.85, 200001)
    area = float(np.trapz(L.crumple_force(xs, Fp, Lc), xs)) if hasattr(np, "trapz") else float(np.trapezoid(L.crumple_force(xs, Fp, Lc), xs))
    checks.append(("work_to equals the numerical area under the curve", abs(area - L.work_to(0.85, Fp, Lc)) < 5.0))

    # worked example: 1000 kg, 56 km/h, Fp 200 kN, Lc 0.8 m
    res = L.simulate_crash(m, v0, Fp, Lc)
    d_ref, g_ref, t_ref = L.analytic_plateau(m, v0, Fp)
    checks.append((f"worked example: stop distance {res['stop_distance']:.4f} m vs analytic KE0/Fp + XR/2 = {d_ref:.4f} m",
                   abs(res["stop_distance"] - d_ref) < 1e-4 and abs(d_ref - 0.6299) < 5e-4))
    checks.append((f"worked example: peak deceleration {res['peak_g']:.3f} g = Fp/(m g) = {g_ref:.3f} g",
                   abs(res["peak_g"] - g_ref) < 1e-6 and abs(g_ref - 20.387) < 5e-3))
    checks.append(("stop time agrees with the analytic value (about 79.4 ms)",
                   abs(res["stop_time"] - t_ref) < 1e-4 and abs(t_ref - 0.0794) < 5e-4))
    ke0, total, err = L.energy_balance(res)
    checks.append((f"energy balance: crumple work + damper loss + residual KE = KE0 (error {err:.1e})", err < 1e-9))
    checks.append(("momentum: the impulse of the force equals m v0", abs(res["impulse"] - m * v0) / (m * v0) < 1e-9))
    checks.append(("the car ends at rest (residual kinetic energy is zero)", res["KE_end"] == 0.0))

    # convergence: smaller steps, smaller error
    e_coarse = abs(L.simulate_crash(m, v0, Fp, Lc, dt=1e-3)["stop_distance"] - d_ref)
    e_fine = abs(L.simulate_crash(m, v0, Fp, Lc, dt=1e-4)["stop_distance"] - d_ref)
    checks.append(("a 10 times smaller time step gives a smaller error", e_fine < e_coarse / 10))

    # damper adds loss and a start-of-crash spike
    damped = L.simulate_crash(m, v0, Fp, Lc, c=5000.0)
    ke0d, totald, errd = L.energy_balance(damped)
    checks.append(("with damping, damper loss is positive and the energy balance still closes",
                   damped["W_damper"] > 0 and errd < 1e-9))
    checks.append(("with damping the car stops in a shorter distance", damped["stop_distance"] < res["stop_distance"]))

    # two cars
    eq = L.two_car_collision(1000.0, v0, 1000.0, -v0, Fp, 0.7, 0.7)
    checks.append(("equal cars head on: both stop (common final velocity 0)", abs(eq["v1_final"]) < 1e-6 and abs(eq["v2_final"]) < 1e-6))
    checks.append(("equal cars head on: each crushes as if it hit a rigid wall at its own speed",
                   abs(eq["stop_distance"] / 2 - d_ref) < 0.02 and abs(eq["KE_lost"] / 2 - 0.5 * m * v0 ** 2) < 1e-3))
    un = L.two_car_collision(1500.0, v0, 750.0, -v0, Fp, 0.7, 0.7)
    vf = (1500.0 * v0 - 750.0 * v0) / 2250.0
    checks.append((f"inelastic crash: common velocity (m1 v1 + m2 v2)/(m1 + m2) = {vf:.3f} m/s",
                   abs(un["v1_final"] - vf) < 1e-6 and abs(un["v2_final"] - vf) < 1e-6))
    checks.append(("momentum is conserved in the two-car crash", abs(un["p_before"] - un["p_after"]) < 1e-6))
    checks.append(("the lighter car feels the larger deceleration, in the inverse ratio of the masses",
                   abs(un["peak_g2"] / un["peak_g1"] - 2.0) < 1e-6))
    chase = L.two_car_collision(1000.0, 20.0, 1000.0, 10.0, Fp, 0.7, 0.7)
    checks.append(("hand calculation: 20 m/s hits 10 m/s, equal cars: final 15 m/s, energy lost 25 kJ",
                   abs(chase["v1_final"] - 15.0) < 1e-6 and abs(chase["KE_lost"] - 25000.0) < 1e-6))

    # sensitivity
    rows = L.sweep_plateau(m, v0, 0.9, [150e3, 250e3])
    checks.append(("peak deceleration grows in proportion to Fp", abs(rows[1][1] / rows[0][1] - 250.0 / 150.0) < 1e-6))
    checks.append(("a stiffer plateau stops the car in a shorter distance", rows[1][2] < rows[0][2]))

    # failure case: crumple zone bottoms out
    bad = L.simulate_crash(m, v0, 250e3, 0.35)
    good = L.simulate_crash(m, v0, 250e3, 0.60)
    checks.append(("a 0.35 m zone bottoms out at 250 kN, a 0.60 m zone does not", L.bottomed_out(bad, 0.35) and not L.bottomed_out(good, 0.60)))
    checks.append(("bottoming out makes a second, much larger spike (more than 4 times)", bad["peak_g"] > 4 * good["peak_g"]))
    checks.append(("the spike comes at the end of the crash, not the start", int(np.argmax(bad["a_g"])) >= len(bad["a_g"]) - 3))
    wc, wcell = L.split_work(bad, 250e3, 0.35)
    checks.append(("when bottoming out the passenger cell absorbs part of the energy and the split adds up",
                   wcell > 0 and abs(wc + wcell - bad["KE0"]) / bad["KE0"] < 1e-4))

    # edge case
    still = L.simulate_crash(m, 0.0, Fp, Lc)
    checks.append(("a car that is not moving does not crush", still["stop_distance"] == 0.0 and still["peak_g"] == 0.0))

    # mini-project reference sweep (peak <= 25 g, Lc <= 0.70, stop within 95 percent of Lc)
    best = None
    for f in range(100, 401, 10):
        for lc in np.arange(0.30, 0.701, 0.05):
            r = L.simulate_crash(m, v0, f * 1e3, float(lc))
            if r["peak_g"] <= 25.0 and r["stop_distance"] <= 0.95 * lc:
                if best is None or r["peak_g"] < best[0]:
                    best = (r["peak_g"], f, round(float(lc), 2), r["stop_distance"])
    checks.append((f"mini-project reference: lowest-peak passing design is Fp = 190 kN, Lc = 0.70 m (found {best[1]} kN, {best[2]} m)",
                   best is not None and best[1] == 190 and abs(best[2] - 0.70) < 1e-9))
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
