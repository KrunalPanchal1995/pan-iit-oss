"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("S-N line passes through 0.9*S_u at 1000 cycles", abs(L.A * 1000.0 ** L.B - 540.0) < 1e-6))
    checks.append(("S-N line passes through S_e = 300 MPa at 1 million cycles", abs(L.A * 1e6 ** L.B - 300.0) < 1e-6))
    checks.append((f"exponent b is about -0.085 (got {L.B:.4f}), near the typical -0.1", abs(L.B + 0.0851) < 1e-4))
    n400 = L.cycles_to_failure(400)
    hand = 10 ** (np.log10(400 / 972.0) / L.B)       # hand calculation in logs
    checks.append((f"worked example: 400 MPa gives about 34,000 cycles (got {n400:,.0f})", abs(n400 - 34017) < 5 and abs(n400 / hand - 1) < 1e-9))
    minutes = L.time_to_failure_hours(400, 10) * 60
    checks.append((f"worked example: 34,000 cycles at 10 Hz is about 57 minutes (got {minutes:.1f})", abs(minutes - 56.7) < 0.1))
    checks.append(("more stress means fewer cycles", L.cycles_to_failure(500) < L.cycles_to_failure(400) < L.cycles_to_failure(350)))
    checks.append(("500 MPa gives about 2,500 cycles", abs(L.cycles_to_failure(500) - 2471) < 5))
    checks.append(("below the endurance limit no failure is predicted", L.cycles_to_failure(250) == np.inf and L.cycles_to_failure(300) == np.inf))
    checks.append(("edge: just above the limit the life is finite and a little under 1 million cycles", 7e5 < L.cycles_to_failure(300.5) < 1e6))
    checks.append(("edge: at 0.9*S_u the life is 1000 cycles", abs(L.cycles_to_failure(540) - 1000) < 1e-6))
    t = np.linspace(0, 1, 1001)
    w = L.stress_wave(t, 400)
    checks.append(("wave peaks at +400 and -400 MPa, below S_u = 600", abs(w.max() - 400) < 0.1 and abs(w.min() + 400) < 0.1 and w.max() < L.SU))
    checks.append(("stress range is twice the amplitude (800 MPa)", L.stress_range(400) == 800))
    w2 = L.stress_wave(np.linspace(0, 1, 1001), 100, mean=50)
    checks.append(("a mean of 50 MPa shifts the wave to 150 and -50", abs(w2.max() - 150) < 0.1 and abs(w2.min() + 50) < 0.1))
    # extra numbers used in the text
    checks.append(("350 MPa gives 163,392 cycles; at 20 Hz that is 2.27 hours", abs(L.cycles_to_failure(350) - 163392) < 5 and abs(L.time_to_failure_hours(350, 20) - 2.27) < 0.005))
    checks.append(("450 MPa gives 8,522 cycles, which is 14.2 minutes at 10 Hz", abs(L.cycles_to_failure(450) - 8522) < 5 and abs(L.time_to_failure_hours(450, 10) * 60 - 14.2) < 0.05))
    checks.append(("raising the amplitude from 400 to 500 MPa cuts life by a factor of 13.8", abs(L.cycles_to_failure(400) / L.cycles_to_failure(500) - 13.77) < 0.01))
    checks.append(("8 hours a day at 10 Hz for 30 days is 8.64 million cycles", 8 * 3600 * 10 * 30 == 8640000))
    checks.append(("cutting 450 MPa to 300 MPa in bending needs a diameter 1.145 times larger (stress goes as 1/d^3)", abs((450 / 300) ** (1 / 3) - 1.1447) < 1e-4))
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
