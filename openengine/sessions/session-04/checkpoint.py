"""Checkpoint for Session 4. Prints PASS or FAIL."""
import math


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append((f"air at 300 K: cp = 1.006 kJ/(kg K) and gamma = 1.40 (tables: 1.005, 1.40) (got {L.cp_air(300):.4f})",
                   abs(L.cp_air(300) - 1.005) < 0.005 and abs(L.gamma_air(300) - 1.40) < 0.005))
    checks.append((f"air at 1000 K: cp = 1.146 kJ/(kg K) (tables: 1.141) (got {L.cp_air(1000):.4f})", abs(L.cp_air(1000) - 1.141) < 0.01))
    checks.append(("cp rises and gamma falls from 300 K to 3000 K",
                   all(L.cp_air(a) < L.cp_air(b) and L.gamma_air(a) > L.gamma_air(b) for a, b in ((300, 800), (800, 1500), (1500, 3000)))))
    checks.append(("the two polynomial ranges join smoothly at 1000 K (cp, h and s0)",
                   abs(L.cp_air(1000 - 1e-6) - L.cp_air(1000)) < 1e-4 and abs(L.h_air(1000 - 1e-6) - L.h_air(1000)) < 1e-3
                   and abs(L.s0_air(1000 - 1e-6) - L.s0_air(1000)) < 1e-5))
    checks.append(("dh/dT = cp and d(phi)/dT = cv / T (numerical derivative)",
                   all(abs((L.h_air(t + 1e-3) - L.h_air(t - 1e-3)) / 2e-3 - L.cp_air(t)) < 1e-5
                       and abs((L.phi_air(t + 1e-3) - L.phi_air(t - 1e-3)) / 2e-3 * t - L.cv_air(t)) < 1e-5 for t in (400, 1600))))
    const = L.otto_cycle(9.0, 1100.0, L.ConstantGas())
    checks.append((f"validation: constant gamma reproduces Session 2, 0.5848 and T3 = 2255.6 K (got {const['eta']:.4f}, {const['T'][2]:.1f} K)",
                   abs(const["eta"] - (1 - 9 ** -0.4)) < 1e-9 and abs(const["T"][2] - 2255.6) < 0.1))
    var = L.otto_cycle(9.0, 1100.0)
    t1, t2, t3, t4 = var["T"]
    checks.append((f"worked example: T2 = 700.0 K, T3 = 1927 K, T4 = 964 K (got {t2:.1f}, {t3:.0f}, {t4:.0f})",
                   abs(t2 - 700.0) < 0.5 and abs(t3 - 1927) < 1.5 and abs(t4 - 964) < 1.5))
    checks.append((f"worked example: efficiency 0.530 (got {var['eta']:.4f})", abs(var["eta"] - 0.530) < 5e-4))
    checks.append((f"roadmap checkpoint: Otto at r = 9 and q_in = 1100 kJ/kg is below 0.56 (got {var['eta']:.3f}; constant gamma 0.585)",
                   var["eta"] < 0.56 and const["eta"] > 0.584))
    checks.append(("effective gamma lies between gamma(T3) and gamma(T1)",
                   L.gamma_air(t3) < var["gamma_eff"] < L.gamma_air(t1)))
    v, p = L.otto_path(9.0, 1100.0)
    w = L.loop_work(v, p)
    checks.append((f"first law: P dv loop area {w:.1f} equals q_in - q_out = {1100 - var['q_out']:.1f} kJ/kg within 0.1 percent",
                   abs(w - (1100 - var["q_out"])) / (1100 - var["q_out"]) < 1e-3))
    checks.append(("RK4 isentrope ends at the T2 found from phi", abs(p[len(p) // 2 - 1] * v[len(v) // 2 - 1] / L.R_AIR - t2) < 0.01))
    etas = [L.otto_cycle(9.0, q)["eta"] for q in (300, 700, 1100, 1500, 2000)]
    checks.append(("efficiency falls as more heat is added (hotter gas, lower gamma)", all(a > b for a, b in zip(etas, etas[1:]))))
    checks.append(("with little heat the variable model approaches the cold-air formula",
                   abs(L.otto_cycle(9.0, 5.0)["eta"] - (1 - 9 ** (1 - L.gamma_air(450)))) < 0.01))
    checks.append(("variable cp lowers the Otto efficiency at every r from 4 to 20",
                   all(L.otto_cycle(r, 1100)["eta"] < L.otto_cycle(r, 1100, L.ConstantGas())["eta"] for r in (4, 8, 12, 16, 20))))
    d, dc = L.diesel_cycle(18.0, 1100.0), L.diesel_cycle(18.0, 1100.0, L.ConstantGas())
    checks.append((f"Diesel r = 18: variable cp gives 0.575 below the constant-gamma 0.625 (got {d['eta']:.4f})",
                   abs(d["eta"] - 0.575) < 5e-4 and abs(dc["eta"] - 0.6247) < 5e-4))
    bad = 0
    for call in (lambda: L.otto_cycle(1.0, 1100), lambda: L.otto_cycle(9, -5), lambda: L.cp_air(100), lambda: L.otto_cycle(9, 1e6)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 4))
    checks.append(("no NaN anywhere for r from 2 to 25 and q_in from 50 to 2500 kJ/kg",
                   all(math.isfinite(L.otto_cycle(r, q)["eta"]) for r in (2, 25) for q in (50, 2500))))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson4", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
