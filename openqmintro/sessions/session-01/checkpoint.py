"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    p = L.probabilities(L.prepare(60))
    checks.append((f"worked example: a state prepared at 60 degrees has P0 = 0.75 and P1 = 0.25 (got {p[0]:.2f}, {p[1]:.2f})", abs(p[0] - 0.75) < 1e-12 and abs(p[1] - 0.25) < 1e-12))
    q = L.p_out(60)
    checks.append((f"worked example: the interferometer at phi = 60 degrees gives P0 = 0.75 and P1 = 0.25 (got {q[0]:.2f}, {q[1]:.2f})", abs(q[0] - 0.75) < 1e-12 and abs(q[1] - 0.25) < 1e-12))
    s = L.interferometer(60)
    checks.append(("worked example: the final amplitudes are 0.75 + 0.433i and 0.25 - 0.433i", np.allclose(s, [0.75 + 0.4330127j, 0.25 - 0.4330127j])))
    checks.append(("phi = 0 sends the photon to exit 0 with certainty, phi = 180 degrees to exit 1",
                   abs(L.p_out(0)[0] - 1) < 1e-12 and abs(L.p_out(180)[1] - 1) < 1e-12))
    checks.append(("the interference formula P0 = cos^2(phi / 2) holds at many phases",
                   all(abs(L.p_out(x)[0] - np.cos(np.radians(x) / 2) ** 2) < 1e-12 for x in range(0, 361, 15))))
    checks.append(("a classical coin gives 1/2 at every phase, so it differs from the photon at phi = 0 and 180",
                   L.classical_mixture_p0(0) == 0.5 and abs(L.p_out(0)[0] - L.classical_mixture_p0(0)) > 0.4 and abs(L.p_out(180)[0] - L.classical_mixture_p0(180)) > 0.4))
    checks.append(("the beam splitter undoes itself: BS twice gives the state back", np.allclose(L.BS @ L.BS, np.eye(2))))
    checks.append(("probabilities always add up to 1 after any phase", all(abs(sum(L.p_out(x)) - 1) < 1e-12 for x in range(0, 361, 10))))
    pb = L.probabilities((0.6, 0.8))
    checks.append((f"question B: amplitudes 0.6 and 0.8 give probabilities 0.36 and 0.64 (got {pb[0]:.2f}, {pb[1]:.2f})", abs(pb[0] - 0.36) < 1e-12 and abs(pb[1] - 0.64) < 1e-12))
    pa = L.probabilities(L.BS @ np.array([0.6, 0.8], dtype=complex))
    checks.append((f"question B: after one beam splitter the probabilities are 0.98 and 0.02 (got {pa[0]:.2f}, {pa[1]:.2f})", abs(pa[0] - 0.98) < 1e-12 and abs(pa[1] - 0.02) < 1e-12))
    checks.append(("a state prepared at theta meets a phase and a splitter with P0 = (1 + sin(theta) cos(phi)) / 2",
                   all(abs(L.after_phase_and_splitter(L.prepare(t), f)[0] - (1 + np.sin(np.radians(t)) * np.cos(np.radians(f))) / 2) < 1e-12
                       for t in (0, 30, 90, 150, 180) for f in (0, 45, 180, 270))))
    checks.append(("design: P0 of at least 0.9 holds at phi = 36.8 degrees but not at 37 degrees", L.p_out(36.8)[0] >= 0.9 > L.p_out(37)[0]))
    for bad, label in ((lambda: L.probabilities((0.6, 0.6)), "a state that is not normalised"), (lambda: L.probabilities((1, 0, 0)), "three amplitudes")):
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
    spec = importlib.util.spec_from_file_location("lesson1", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
