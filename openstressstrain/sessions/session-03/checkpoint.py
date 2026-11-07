"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    e, s02, n = 200000.0, 250.0, 10.0
    eps = np.linspace(0.0, 0.02, 801)
    s = L.stress_ro(eps, e, s02, n)
    checks.append(("inverse is exact: strain_ro(stress_ro(eps)) = eps", np.allclose(L.strain_ro(s, e, s02, n), eps, atol=1e-10)))
    checks.append(("validation: numerical 0.2% offset yield equals s02 = 250 MPa", abs(L.offset_yield(eps, s, e) - s02) < 0.2))
    slope = (s[1] - s[0]) / (eps[1] - eps[0])
    checks.append(("validation: initial slope equals E", abs(slope / e - 1) < 0.01))

    # worked example: bilinear metal E = 70 GPa, sy = 200 MPa, H = 7 GPa, pulled to 2 percent strain
    be, bsy, bh = 70000.0, 200.0, 7000.0
    path = L.load_unload_path(0.02)
    bs = L.bilinear_path(path, be, bsy, bh)
    checks.append(("worked example: stress at 2% strain is 200 + 7000 (0.02 - 0.002857) = 320 MPa", abs(bs[199] - 320.0) < 1e-6))
    k = 199 + int(np.argmax(bs[199:] <= 0.0))
    left = path[k - 1] + (path[k] - path[k - 1]) * bs[k - 1] / (bs[k - 1] - bs[k])
    checks.append(("worked example: permanent set 0.02 - 320/70000 = 0.01543", abs(left - (0.02 - 320.0 / 70000.0)) < 1e-6))
    un = (bs[200] - bs[205]) / (path[200] - path[205])
    checks.append(("unloading slope equals E (70 GPa)", abs(un / be - 1) < 1e-6))
    below = L.bilinear_path(np.linspace(0, 0.002, 50), be, bsy, bh)
    checks.append(("below yield the path is purely elastic and fully recoverable",
                   np.allclose(below, be * np.linspace(0, 0.002, 50))))
    checks.append(("zero strain gives zero stress", L.bilinear_path([0.0], be, bsy, bh)[0] == 0.0 and L.stress_ro(0.0, e, s02, n)[0] < 1e-9))
    ps = L.permanent_set_ro(0.008, e, s02, n)
    checks.append(("Ramberg-Osgood permanent set at 0.8% strain is about 0.0066", abs(ps - 0.00659) < 2e-5))

    base, rows = L.sensitivity()
    checks.append(("hand calculation: E -10% raises extension by 1/0.9 - 1 = 11.1%", abs(rows["E -10%"][0] - 11.11) < 0.01))
    checks.append(("hand calculation: yield +10% raises factor of safety by exactly 10%", abs(rows["yield +10%"][1] - 10.0) < 1e-9))
    checks.append(("extension is insensitive to yield and FoS to E", rows["yield +10%"][0] == 0.0 and rows["E +10%"][1] == 0.0))

    sharp = L.stress_ro(0.05, e, s02, 50.0)[0]
    checks.append(("limit: very large n approaches a plateau near s02 (below 1.1 s02 at 5% strain)", sharp < 1.1 * s02))
    checks.append(("limit: the model has no necking, stress never falls", bool(np.all(np.diff(s) >= 0))))

    errs = np.array([L.estimate(k) for k in range(20)])
    checks.append(("mini-project: E within 5% of 205 GPa for 20 noisy tests", bool(np.all(abs(errs[:, 0] / L.TRUE_E - 1) < 0.05))))
    checks.append(("mini-project: yield within 5% of 310 MPa for 20 noisy tests", bool(np.all(abs(errs[:, 1] / L.TRUE_S02 - 1) < 0.05))))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson1", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
