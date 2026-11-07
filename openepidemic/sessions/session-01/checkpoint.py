"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # hand calculation of one step of one day (beta 0.5, gamma 0.25, N 1000, S 999, I 1)
    S, I, R = L.one_step(999.0, 1.0, 0.0, 0.5, 0.25, 1000, 1.0)
    checks.append(("worked example: one day moves 0.4995 people S->I and 0.25 people I->R",
                   abs(S - 998.5005) < 1e-9 and abs(I - 1.2495) < 1e-9 and abs(R - 0.25) < 1e-9))
    checks.append(("one step keeps the total of people", abs(S + I + R - 1000) < 1e-9))

    S, I, R = L.run_outbreak(0.5, 0.25)
    checks.append(("S + I + R stays 1000 on every day", float(np.abs(S + I + R - 1000).max()) < 1e-6))
    checks.append(("nobody is negative", bool(min(S.min(), I.min(), R.min()) > -1e-9)))
    checks.append(("day 10 (R0 = 2): S, I, R are about 978.0, 11.4, 10.6",
                   abs(S[10] - 978.0) < 0.1 and abs(I[10] - 11.4) < 0.1 and abs(R[10] - 10.6) < 0.1))
    day, top = L.peak_of(I)
    checks.append((f"R0 = 2 peak is on day 27 with about 155 infected (got day {day}, {top:.1f})", day == 27 and abs(top - 154.7) < 0.5))
    checks.append(("S falls and R rises every day", bool(np.all(np.diff(S) <= 0) and np.all(np.diff(R) >= 0))))
    checks.append(("about 798.5 people end up in R after 120 days", abs(R[-1] - 798.5) < 0.5))

    checks.append(("R0 = beta / gamma = 2 for beta 0.5, gamma 0.25", abs(L.r0(0.5, 0.25) - 2.0) < 1e-12))
    checks.append(("generations for R0 = 2 are 1, 2, 4, 8, 16, 32", L.generations(2.0) == [1.0, 2.0, 4.0, 8.0, 16.0, 32.0]))
    checks.append(("generations for R0 = 0.5 shrink", L.generations(0.5)[-1] < L.generations(0.5)[0] / 30))

    # R0 above and below 1
    _, I_low, _ = L.run_outbreak(0.125, 0.25)
    checks.append(("R0 = 0.5: infected people fall from day 0", bool(np.all(np.diff(I_low) < 0)) and L.peak_of(I_low)[0] == 0))
    _, I_one, _ = L.run_outbreak(0.25, 0.25)
    checks.append(("R0 = 1: still no growth, peak on day 0", L.peak_of(I_one)[0] == 0))
    # edge case: nobody infected, nothing happens
    S0, I0, R0_ = L.run_outbreak(0.5, 0.25, I0=0)
    checks.append(("with nobody infected nothing changes", bool(np.all(I0 == 0) and np.all(S0 == 1000))))
    # step size check: halving dt changes the peak very little
    _, I_fine, _ = L.run_outbreak(0.5, 0.25, dt=0.05)
    checks.append(("halving the step changes the peak by under 2 people", abs(L.peak_of(I_fine)[1] - top) < 2))
    # assessment answers
    checks.append(("beta 0.3, gamma 0.1 gives R0 = 3 and 27 cases in generation 3", abs(L.r0(0.3, 0.1) - 3) < 1e-12 and L.generations(3.0)[3] == 27.0))
    checks.append(("beta 0.25 makes R0 = 1 and beta 0.2 makes R0 = 0.8 at gamma 0.25",
                   abs(L.r0(0.25, 0.25) - 1) < 1e-12 and abs(L.r0(0.2, 0.25) - 0.8) < 1e-12 and L.peak_of(L.run_outbreak(0.2, 0.25)[1])[0] == 0))
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
