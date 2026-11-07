"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    j = L.turbojet(288, 10, 1400)
    checks.append((f"worked example: T2 = 603.3 K (got {j['t2']:.1f})", abs(j["t2"] - 603.3) < 0.1))
    checks.append((f"worked example: T4 = 1084.7 K (got {j['t4']:.1f})", abs(j["t4"] - 1084.7) < 0.1))
    checks.append((f"worked example: nozzle pressure ratio 3.65 (got {j['p_ratio_nozzle']:.2f})", abs(j["p_ratio_nozzle"] - 3.65) < 0.01))
    checks.append((f"worked example: exit speed 800 m/s (got {j['v_e']:.0f})", abs(j["v_e"] - 800) < 1))
    checks.append((f"worked example: TSFC 23.7 g/(kN s) (got {j['tsfc']:.1f})", abs(j["tsfc"] - 23.7) < 0.1))
    checks.append((f"worked example: 20 kg/s gives 16.0 kN (got {L.thrust_kn(20, t1=288, r=10, t3=1400):.1f})",
                   abs(L.thrust_kn(20, t1=288, r=10, t3=1400) - 16.0) < 0.05))
    # validation 1: no losses -> jet kinetic energy equals the ideal net work of Session 2
    ok1 = True
    for r, t3 in ((5, 1200), (10, 1400), (20, 1600)):
        i = L.turbojet(288, r, t3, eta_c=1, eta_t=1, eta_n=1)
        ok1 &= abs(i["v_e"] ** 2 / 2 - L.ideal_net_work(288, r, t3)) < 1e-6 * L.ideal_net_work(288, r, t3)
    checks.append(("validation: with no losses, v_e^2 / 2 equals the ideal net work of Session 2", ok1))
    # validation 2: energy balance of the whole engine
    ok2 = True
    for r, t3, ec, et, en in ((10, 1400, 0.85, 0.9, 0.95), (16, 1600, 0.8, 0.85, 0.9), (6, 1200, 0.9, 0.9, 1.0)):
        g = L.turbojet(288, r, t3, ec, et, en)
        ok2 &= abs(g["q_in"] - (L.CP * (g["t5"] - 288) + g["v_e"] ** 2 / 2)) < 1e-6 * g["q_in"]
    checks.append(("validation: heat added = enthalpy gain of the exhaust + jet kinetic energy", ok2))
    checks.append(("losses reduce the thrust", L.turbojet(288, 10, 1400, 0.8, 0.85, 0.9)["v_e"] < j["v_e"] < L.turbojet(288, 10, 1400, 1, 1, 1)["v_e"]))
    checks.append(("a hotter turbine inlet gives more specific thrust", L.turbojet(288, 10, 1600)["v_e"] > j["v_e"] > L.turbojet(288, 10, 1200)["v_e"]))
    checks.append(("design: r = 16, T3 = 1600 K reaches 900 N s/kg and 24 g/(kN s)",
                   L.turbojet(288, 16, 1600)["v_e"] >= 900 and L.turbojet(288, 16, 1600)["tsfc"] <= 24))
    checks.append(("edge case: r = 1 gives zero thrust", abs(L.turbojet(288, 1, 1400)["v_e"]) < 1e-9))
    for bad, label in ((lambda: L.turbojet(288, 0.5, 1400), "r below 1"),
                       (lambda: L.turbojet(288, 10, 1400, eta_c=0.0), "compressor efficiency 0"),
                       (lambda: L.turbojet(288, 30, 800), "T3 too low for the compressor"),
                       (lambda: L.turbojet(288, 30, 1000, 0.7, 0.7, 1.0), "no pressure left for a jet")):
        try:
            bad()
            raised = False
        except ValueError:
            raised = True
        checks.append((f"edge case: {label} gives an error", raised))
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
