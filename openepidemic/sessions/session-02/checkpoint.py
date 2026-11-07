"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("R0 = beta / gamma = 2 for 0.4 and 0.2", abs(L.r0(0.4, 0.2) - 2.0) < 1e-12))
    checks.append(("worked example: herd immunity threshold for R0 = 3 is 66.7 percent",
                   abs(L.herd_immunity_threshold(3.0) - 2 / 3) < 1e-12))
    z = L.final_size(2.0)
    checks.append((f"worked example: final size for R0 = 2 is 79.7 percent (got {100 * z:.2f})", abs(100 * z - 79.68) < 0.01))
    checks.append(("the final size really solves z = 1 - exp(-R0 z)", abs(z - (1 - np.exp(-2.0 * z))) < 1e-12))
    checks.append(("final size for R0 = 3 is 94.0 percent", abs(100 * L.final_size(3.0) - 94.05) < 0.01))
    checks.append(("edge: R0 <= 1 gives final size 0 and threshold 0",
                   L.final_size(1.0) == 0.0 and L.final_size(0.5) == 0.0 and L.herd_immunity_threshold(0.8) == 0.0))
    checks.append(("peak fraction formula for R0 = 2 is 15.3 percent", abs(100 * L.peak_fraction(2.0) - 15.34) < 0.01))

    S, I, R = L.simulate(0.4, 0.2)
    N = 10000
    checks.append(("S + I + R = N on every day", float(np.abs(S + I + R - N).max()) < 1e-6))
    checks.append(("simulated peak is within 1 percent of N of the formula (15.4 vs 15.3 percent)",
                   abs(I.max() / N - L.peak_fraction(2.0)) < 0.01 and abs(100 * I.max() / N - 15.4) < 0.05))
    checks.append(("simulated final size matches the equation within 0.2 percent of N (79.8 vs 79.7)",
                   abs(R[-1] / N - z) < 0.002 and abs(100 * R[-1] / N - 79.8) < 0.05))

    # growth rule: grows when R0 * S / N > 1
    checks.append(("I grows at the start when R0 S/N > 1 and falls when R0 S/N < 1",
                   (np.diff(I)[0] > 0) and L.r_effective(2.0, 0.6) > 1 and L.r_effective(2.0, 0.4) < 1))
    S2, I2, R2 = L.simulate(0.4, 0.2, R_init=0.6 * N)
    checks.append(("with 60 percent protected (R_eff = 0.8) the outbreak shrinks from day 0", bool(I2.max() == I2[0])))

    # design problem
    checks.append(("coverage needed for R0 = 3 and efficacy 0.9 is 74.1 percent", abs(100 * L.coverage_needed(3.0, 0.9) - 74.07) < 0.01))
    checks.append(("efficacy 0.6 and R0 = 3 needs more than 100 percent coverage: impossible", L.coverage_needed(3.0, 0.6) > 1.0))
    c = L.coverage_needed(3.0, 0.9)
    checks.append(("at that coverage R_eff is exactly 1", abs(L.r_effective(3.0, 1 - L.protected_share(c, 0.9)) - 1.0) < 1e-12))
    p30 = simulate_peak(L, 0.3)
    p50 = simulate_peak(L, 0.5)
    checks.append((f"R0 = 2 peaks: none 1542.9, 30 percent covered 415.2, 50 percent covered 32.6 people (got {p30:.1f}, {p50:.1f})",
                   abs(L.simulate(0.4, 0.2)[1].max() - 1542.9) < 0.1 and abs(p30 - 415.2) < 0.1 and abs(p50 - 32.6) < 0.1))
    checks.append(("worked example: z = 0.797 satisfies z = 1 - exp(-2 z) to 0.001 (1 - exp(-1.594) = 0.797)", abs(1 - np.exp(-2 * 0.797) - 0.797) < 1e-3))
    checks.append(("R_eff at the start is 2, 1.46 and 1.10 for 0, 30, 50 percent coverage (efficacy 0.9)",
                   [round(L.r_effective(2.0, 1 - L.protected_share(c, 0.9)), 2) for c in (0.0, 0.3, 0.5)] == [2.0, 1.46, 1.1]))
    checks.append(("R0 = 4: threshold 75 percent; efficacy 0.8 needs 93.75 percent", abs(L.herd_immunity_threshold(4.0) - 0.75) < 1e-12 and abs(L.coverage_needed(4.0, 0.8) - 0.9375) < 1e-12))
    checks.append(("R0 = 3, efficacy 0.6: full coverage leaves R_eff = 1.2; with R0 = 2.5 full coverage just reaches the threshold",
                   abs(L.r_effective(3.0, 1 - L.protected_share(1.0, 0.6)) - 1.2) < 1e-12 and abs(L.coverage_needed(2.5, 0.6) - 1.0) < 1e-12))
    checks.append(("coverage 0.741 at efficacy 0.9 protects 66.7 percent", abs(L.protected_share(0.741, 0.9) - 0.667) < 1e-3))
    return checks


def simulate_peak(L, coverage, efficacy=0.9):
    return float(L.simulate(0.4, 0.2, R_init=L.protected_share(coverage, efficacy) * 10000)[1].max())


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson2", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
