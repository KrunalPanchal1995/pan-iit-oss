"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    H = L.heskestad_height(50.0, 0.30)
    checks.append((f"worked example: Q = 50 kW, D = 0.30 m gives H = 0.818 m (got {H:.3f})", abs(H - 0.818) < 0.001))
    f = L.flicker_frequency(0.30)
    checks.append((f"worked example: D = 0.30 m puffs at 1.5 / sqrt(0.30) = 2.74 Hz (got {f:.3f})", abs(f - 2.739) < 0.001))
    # hand calculation of the correlation: 50^0.4 = 4.7818
    checks.append(("hand calculation: 0.235 * 4.7818 - 1.02 * 0.30 = 1.1237 - 0.3060 = 0.8177 m",
                   abs(0.235 * 4.7818 - 1.02 * 0.30 - L.heskestad_height(50.0, 0.30)) < 0.001))
    q = L.heat_release_for_height(1.0, 0.30)
    checks.append((f"design: a 1.0 m flame on a 0.30 m burner needs Q = 72.8 kW (got {q:.1f})", abs(q - 72.81) < 0.05))
    checks.append(("the inverse undoes the correlation", abs(L.heskestad_height(q, 0.30) - 1.0) < 1e-9))
    checks.append(("edge: a tiny Q on a wide burner gives no flame (0), not a negative height", L.heskestad_height(5.0, 1.0) == 0.0))

    fs = 30.0
    t, h = L.height_signal(10.0, fs, 0.8, 0.04, 2.74)
    checks.append(("10 s at 30 fps is 300 samples", len(h) == 300 and abs(t[1] - 1 / 30) < 1e-12))
    checks.append(("cycle counting recovers 2.74 Hz within 0.01 Hz", abs(L.count_frequency(h, fs) - 2.74) < 0.01))
    checks.append(("FFT recovers 2.74 Hz within 0.01 Hz", abs(L.fft_frequency(h, fs) - 2.74) < 0.01))
    # amplitude scale: a flicker exactly on an FFT bin has peak height equal to its amplitude
    t2, h2 = L.height_signal(10.0, fs, 0.8, 0.04, 3.0)
    fr, am = L.spectrum(h2, fs, 1)
    checks.append(("on a bin (3.0 Hz) the spectrum peak equals the amplitude 0.04", abs(am.max() - 0.04) < 1e-4 and abs(fr[np.argmax(am)] - 3.0) < 1e-9))
    checks.append(("resolution of a 10 s clip is 0.1 Hz and Nyquist at 30 fps is 15 Hz", abs(L.resolution(10.0) - 0.1) < 1e-12 and L.nyquist(30.0) == 15.0))
    checks.append(("a constant signal has no cycles (count gives 0)", L.count_frequency(np.ones(50), fs) == 0.0))

    # aliasing
    checks.append(("below Nyquist the frequency is seen correctly (4.74 Hz at 15 fps)", abs(L.alias_frequency(4.74, 15.0) - 4.74) < 1e-12))
    a = L.alias_frequency(10.61, 15.0)
    checks.append((f"10.61 Hz filmed at 15 fps appears at 4.39 Hz (got {a:.2f})", abs(a - 4.39) < 0.01))
    checks.append(("edge: exactly at Nyquist (15 Hz at 30 fps) appears at 15 Hz", abs(L.alias_frequency(15.0, 30.0) - 15.0) < 1e-12))
    checks.append(("edge: a flicker equal to the frame rate looks frozen (0 Hz)", abs(L.alias_frequency(30.0, 30.0)) < 1e-12))
    t3, h3 = L.height_signal(10.0, 15.0, 0.8, 0.04, 10.61)
    checks.append(("the FFT of the 15 fps recording shows the aliased 4.39 Hz, not 10.61 Hz", abs(L.fft_frequency(h3, 15.0) - 4.39) < 0.02))
    return checks


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
