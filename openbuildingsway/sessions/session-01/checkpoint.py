"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    m, k = 2.0e5, 2.0e7
    w, T = L.sway_frequency(k, m), L.sway_period(k, m)
    checks.append((f"worked example: m = 200000 kg, k = 20000000 N/m gives w = 10 rad/s and T = 0.6283 s (got {w:.3f}, {T:.4f})",
                   abs(w - 10.0) < 1e-9 and abs(T - 0.6283) < 5e-5))
    checks.append(("a period is 2 pi / w (T w = 2 pi)", abs(T * w - 2 * np.pi) < 1e-12))
    checks.append(("twice the mass: T grows by sqrt(2), 0.8886 s", abs(L.sway_period(k, 2 * m) - 0.8886) < 5e-5
                   and abs(L.sway_period(k, 2 * m) / T - np.sqrt(2)) < 1e-12))
    checks.append(("four times the stiffness halves the period, 0.3142 s", abs(L.sway_period(4 * k, m) - 0.3142) < 5e-5
                   and abs(L.sway_period(4 * k, m) / T - 0.5) < 1e-12))
    # free sway: starts at x0, comes back after exactly one period, is at -x0 after half a period
    x0 = 0.05
    checks.append(("free sway starts at x0 and returns after one period",
                   abs(L.free_sway(0.0, x0, k, m) - x0) < 1e-12 and abs(L.free_sway(T, x0, k, m) - x0) < 1e-12))
    checks.append(("free sway is -x0 after half a period", abs(L.free_sway(T / 2, x0, k, m) + x0) < 1e-12))
    # rule of thumb
    checks.append(("rule of thumb: 3 storeys 0.3 s, 10 storeys 1.0 s, 20 storeys 2.0 s",
                   abs(L.rule_of_thumb_period(3) - 0.3) < 1e-12 and abs(L.rule_of_thumb_period(10) - 1.0) < 1e-12
                   and abs(L.rule_of_thumb_period(20) - 2.0) < 1e-12))
    # resonance gain
    checks.append(("gain at matching periods with 5% damping is 10.00 (= 1 / (2 zeta))", abs(L.gain(1.0, 1.0) - 10.0) < 1e-9))
    checks.append(("very slow shaking: gain close to 1 (1.04 at r = 0.2)", abs(L.gain(0.2, 1.0) - 1.0414) < 5e-4))
    checks.append(("very fast shaking: gain well below 1 (0.33 at r = 2)", abs(L.gain(2.0, 1.0) - 0.3326) < 5e-4))
    checks.append(("gain is about 2 at r = 0.707 (1.98)", abs(L.gain(0.7071, 1.0) - 1.98) < 5e-3))
    # edge: more damping, smaller peak
    checks.append(("more damping lowers the resonance gain (zeta 0.1 gives 5.00)", abs(L.gain(1.0, 1.0, 0.1) - 5.0) < 1e-9))
    # edge: array input works
    g = L.gain(1.0, np.array([0.5, 1.0, 2.0]))
    checks.append(("gain accepts arrays, largest at matching period", g.shape == (3,) and int(np.argmax(g)) == 1))
    # assessment answers quoted in Section F
    checks.append(("B: m = 500000 kg, k = 20000000 N/m gives w = 6.325 rad/s and T = 0.9935 s",
                   abs(L.sway_frequency(2e7, 5e5) - 6.325) < 5e-4 and abs(L.sway_period(2e7, 5e5) - 0.9935) < 5e-5))
    k_half = 2e5 * (2 * np.pi / 0.5) ** 2
    k_long = 2e5 * (2 * np.pi / 1.5) ** 2
    checks.append(("D: T = 0.5 s needs k = 3.158e7 N/m (gain 1.33); T = 1.5 s needs k = 3.509e6 N/m (gain 0.79) for m = 200000 kg",
                   abs(k_half - 3.158e7) < 2e4 and abs(L.sway_period(k_half, 2e5) - 0.5) < 1e-12 and abs(L.gain(0.5, 1.0) - 1.33) < 5e-3
                   and abs(k_long - 3.509e6) < 2e3 and abs(L.sway_period(k_long, 2e5) - 1.5) < 1e-12 and abs(L.gain(1.5, 1.0) - 0.794) < 5e-4))
    checks.append(("C: a 1 s building shaken with a 2 s period has gain 1.33; with a 0.5 s period 0.33",
                   abs(L.gain(1.0, 2.0) - 1.33) < 5e-3 and abs(L.gain(1.0, 0.5) - 0.33) < 5e-3))
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
