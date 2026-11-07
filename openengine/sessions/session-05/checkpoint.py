"""Checkpoint for Session 5. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    r, q = 18.0, 1100.0
    otto, diesel, half = L.dual_cycle(r, q, 1.0), L.dual_cycle(r, q, 0.0), L.dual_cycle(r, q, 0.5)
    checks.append((f"limit: x = 1 is the Otto cycle, 0.685 (got {otto['eta']:.4f})",
                   abs(otto["eta"] - L.otto_eta(r)) < 1e-12 and abs(otto["rho"] - 1) < 1e-12 and abs(otto["eta"] - 0.685) < 5e-4))
    checks.append((f"limit: x = 0 is the Session 2 Diesel cycle, 0.625 (got {diesel['eta']:.4f})",
                   abs(diesel["eta"] - L.diesel_eta(r, diesel["rho"])) < 1e-12 and abs(diesel["alpha"] - 1) < 1e-12
                   and abs(diesel["eta"] - 0.6247) < 5e-4))
    checks.append((f"roadmap checkpoint: half split at r = 18 and 1100 kJ/kg lies strictly between 0.625 and 0.685 (got {half['eta']:.4f})",
                   diesel["eta"] < half["eta"] < otto["eta"]))
    checks.append((f"worked example: alpha = 1.804, rho = 1.318, eta = 0.676 (got {half['alpha']:.3f}, {half['rho']:.3f}, {half['eta']:.4f})",
                   abs(half["alpha"] - 1.804) < 5e-4 and abs(half["rho"] - 1.318) < 5e-4 and abs(half["eta"] - 0.676) < 5e-4))
    checks.append(("closed-form formula agrees with the temperature route for many splits",
                   all(abs(L.dual_eta(rr, c["alpha"], c["rho"]) - c["eta"]) < 1e-12
                       for rr in (6, 12, 18) for qq in (500, 1500) for x in (0.1, 0.4, 0.9) for c in [L.dual_cycle(rr, qq, x)])))
    checks.append(("formula limits: rho = 1 gives Otto, alpha = 1 gives Diesel",
                   abs(L.dual_eta(14, 2.3, 1.0) - L.otto_eta(14)) < 1e-12 and abs(L.dual_eta(14, 1.0, 2.0) - L.diesel_eta(14, 2.0)) < 1e-12))
    xs = np.linspace(0, 1, 21)
    etas = [L.dual_cycle(r, q, x)["eta"] for x in xs]
    peaks = [L.dual_cycle(r, q, x)["P"][2] for x in xs]
    checks.append(("efficiency and peak pressure both rise with the constant-volume share",
                   all(a < b for a, b in zip(etas, etas[1:])) and all(a < b for a, b in zip(peaks, peaks[1:]))))
    t1, t2, t3, t4, t5 = half["T"]
    cv = L.R_AIR / (L.GAMMA - 1)
    checks.append(("heat bookkeeping: cv (T3 - T2) + cp (T4 - T3) = q_in",
                   abs(cv * (t3 - t2) + L.GAMMA * cv * (t4 - t3) - q) < 1e-9))
    v, p = L.dual_path(r, q, 0.5, n=2000)
    w = L.loop_work(v, p)
    checks.append((f"first law: P-V loop area {w:.1f} kJ/kg equals q_in - q_out = {q - half['q_out']:.1f} within 0.1 percent",
                   abs(w - (q - half["q_out"])) / (q - half["q_out"]) < 1e-3))
    checks.append(("Carnot bound with the cycle's own T4 and T1 holds", half["eta"] < 1 - t1 / t4))
    xm = L.max_cv_share(r, q, 9000.0)
    checks.append((f"design: largest share for a 9000 kPa limit is 0.357 and meets the limit exactly (got {xm:.3f})",
                   abs(xm - 0.357) < 5e-4 and abs(L.dual_cycle(r, q, xm)["P"][2] - 9000.0) < 1e-6))
    checks.append(("design: a limit below the end-of-compression pressure is impossible", L.max_cv_share(r, q, 5000.0) is None))
    bad = 0
    for call in (lambda: L.dual_cycle(1.0, q, 0.5), lambda: L.dual_cycle(r, q, 1.5), lambda: L.dual_cycle(r, -1, 0.5),
                 lambda: L.dual_eta(r, 0.9, 1.2)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 4))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson5", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
