"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    q = 1100.0
    c = L.ideal_cycle("otto", 9.0, q)
    checks.append((f"worked example: simulated Otto r = 9 efficiency {c['eta']:.5f} matches the formula 0.58476",
                   abs(c["eta"] - L.analytic_eta("otto", 9.0)) < 1e-4))
    checks.append(("worked example: net work 643 kJ/kg and rejected heat 457 kJ/kg",
                   abs(c["work"] - 643.3) < 0.2 and abs(c["q_out"] - 456.8) < 0.2))
    checks.append(("first law: net work = q_in - q_out within 0.1 kJ/kg", abs(c["residual"]) < 0.1))
    d = L.ideal_cycle("diesel", 18.0, q)
    checks.append(("simulated Diesel matches the formula at its measured cut-off ratio",
                   abs(d["eta"] - L.analytic_eta("diesel", 18.0, d["rho"])) < 1e-3))
    rho_hand = 1.0 + q / (1.0045 * 300.0 * 18.0 ** 0.4)
    checks.append(("hand calculation: Diesel cut-off ratio 1 + q / (cp T2) = 2.149", abs(d["rho"] - rho_hand) < 5e-3))
    checks.append(("Diesel first law within 0.1 kJ/kg", abs(d["residual"]) < 0.1))
    checks.append(("Otto efficiency does not depend on the heat input",
                   abs(L.ideal_cycle("otto", 9.0, 500.0)["eta"] - c["eta"]) < 1e-4))
    checks.append(("Diesel efficiency falls as the heat input (cut-off) grows",
                   L.ideal_cycle("diesel", 18.0, 500.0)["eta"] > L.ideal_cycle("diesel", 18.0, 1700.0)["eta"]))
    checks.append(("a smaller step still gives the same answer (convergence)",
                   abs(L.ideal_cycle("otto", 9.0, q, n=100)["eta"] - L.ideal_cycle("otto", 9.0, q, n=800)["eta"]) < 1e-3))
    checks.append(("lower gamma lowers the efficiency", L.ideal_cycle("otto", 9.0, q, 1.3)["eta"] < c["eta"]))

    # crank-angle model
    checks.append(("volume ratio is 1 at top dead centre and r at bottom dead centre",
                   abs(L.volume_ratio(0.0, 9.0) - 1.0) < 1e-12 and abs(L.volume_ratio(180.0, 9.0) - 9.0) < 1e-12))
    burnt = sum(L.wiebe_rate(a, 0.0, 40.0) for a in np.arange(0.0, 40.0, 0.01)) * 0.01
    checks.append(("Wiebe curve releases all the heat (integral is 1)", abs(burnt - 1.0) < 1e-3))
    inst = L.engine_cycle(9.0, q, start=-0.5, duration=1.0)
    checks.append(("limit: an almost instant burn at top dead centre recovers the Otto formula within 0.002",
                   abs(inst["eta_ind"] - L.analytic_eta("otto", 9.0)) < 2e-3))
    wie = L.engine_cycle(9.0, q)
    checks.append(("a 40 degree burn costs efficiency and lowers the peak pressure",
                   wie["eta_ind"] < inst["eta_ind"] and wie["p_max"] < inst["p_max"]))
    checks.append(("first law holds for the crank-angle model (within 2 kJ/kg)", abs(wie["residual"]) < 2.0 and abs(inst["residual"]) < 2.0))
    loss = L.engine_cycle(9.0, q, loss=0.10)
    checks.append(("10 percent heat loss lowers efficiency by about 10 percent of itself",
                   0.85 < loss["eta_ind"] / wie["eta_ind"] < 0.92))
    fr = L.engine_cycle(9.0, q, loss=0.10, fmep=100.0)
    checks.append(("friction lowers brake efficiency but not indicated efficiency",
                   fr["eta_brake"] < fr["eta_ind"] and abs(fr["eta_ind"] - loss["eta_ind"]) < 1e-12))
    checks.append(("brake efficiency still rises with r", L.engine_cycle(12.0, q, loss=0.1, fmep=100.0)["eta_brake"] >
                   L.engine_cycle(8.0, q, loss=0.1, fmep=100.0)["eta_brake"]))

    # fair comparisons
    eo, ed = L.compare_equal_r(14.0, q)
    checks.append((f"equal r = 14 and equal heat: Otto ({eo:.3f}) beats Diesel ({ed:.3f})", eo > ed))
    ro, eo2, rd, ed2 = L.compare_equal_pmax(6000.0, q)
    checks.append((f"equal peak pressure 6000 kPa: Diesel ({ed2:.3f}) beats Otto ({eo2:.3f})", ed2 > eo2 and rd > ro))
    pm = max(L.ideal_cycle("otto", ro, q)["p_max"], L.ideal_cycle("diesel", rd, q)["p_max"])
    checks.append(("both cycles really peak at 6000 kPa", abs(L.ideal_cycle("otto", ro, q)["p_max"] - 6000.0) < 5.0
                   and abs(L.ideal_cycle("diesel", rd, q)["p_max"] - 6000.0) < 5.0 and pm < 6005.0))

    # knock limit and mini-project
    checks.append(("end-of-compression temperature at r = 9 is 722 K", abs(L.end_compression_temperature(9.0) - 722.5) < 0.5))
    checks.append(("worked example: knock limit 720 K allows r up to 8.5 in steps of 0.5", L.max_r_knock_free(740.0, 20.0) == 8.5))
    checks.append(("boundary: a limit exactly at r = 16 returns 16", L.max_r_knock_free(300.0 * 16.0 ** 0.4) == 16.0))
    checks.append(("a limit below the intake temperature returns None", L.max_r_knock_free(250.0) is None))
    ra, rb = L.max_r_knock_free(740.0, 20.0), L.max_r_knock_free(800.0, 20.0)
    ba = L.engine_cycle(ra, q, loss=0.10, fmep=100.0)["eta_brake"]
    bb = L.engine_cycle(rb, q, loss=0.10, fmep=100.0)["eta_brake"]
    checks.append((f"mini-project: fuel A r = {ra}, brake {ba:.3f} misses 0.45; fuel B r = {rb}, brake {bb:.3f} reaches it", ba < 0.45 <= bb))
    bad = 0
    for call in (lambda: L.ideal_cycle("otto", 1.0, 100.0), lambda: L.engine_cycle(9.0, 100.0, loss=1.0),
                 lambda: L.r_for_peak_pressure("otto", 50.0, 1100.0)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 3))
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
