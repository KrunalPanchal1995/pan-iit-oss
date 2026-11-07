"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: 40 Hz sampled at 50 Hz has alias 10 Hz (k = 1)",
                   L.nearest_multiple(40, 50) == 1 and abs(L.alias_frequency(40, 50) - 10.0) < 1e-9
                   and abs(L.signed_alias(40, 50) + 10.0) < 1e-9))
    s40 = L.sample_sine(40, 50, 50)
    s10 = L.sample_sine(-10, 50, 50)
    checks.append(("worked example: the samples of 40 Hz equal the samples of -10 Hz", np.allclose(s40, s10, atol=1e-9)))
    checks.append(("hand calculation: x[1] = sin(2 pi 0.8) = -0.951", abs(s40[1] + 0.951057) < 1e-5))
    checks.append(("f and f + k fs give identical samples", L.same_samples(7.0, 7.0 + 3 * 50.0, 50.0)))
    checks.append(("f and fs - f differ only by a sign of the samples",
                   np.allclose(L.sample_sine(40, 50, 40), -L.sample_sine(10, 50, 40), atol=1e-9)))
    checks.append(("a signal below Nyquist is not changed (12 Hz at 50 Hz)", abs(L.alias_frequency(12, 50) - 12.0) < 1e-9))
    checks.append(("exactly Nyquist: 25 Hz at 50 Hz gives alias 25 Hz", abs(L.alias_frequency(25, 50) - 25.0) < 1e-9))
    checks.append(("exactly fs gives alias 0 (DC): 50 Hz at 50 Hz", abs(L.alias_frequency(50, 50)) < 1e-9))
    fa = [L.alias_frequency(x, 50) for x in np.linspace(0, 500, 2001)]
    checks.append(("alias frequency always lies between 0 and fs/2", 0 <= min(fa) and max(fa) <= 25 + 1e-9))
    checks.append(("design: the minimum rate for a 48 Hz pattern is 96 Hz", abs(L.min_sampling_rate(48) - 96.0) < 1e-9))
    checks.append(("worked example (design): a 4-blade fan at 12 rev/s filmed at 30 fps looks like -3 rev/s",
                   abs(L.pattern_apparent_rev(12, 4, 30) + 3.0) < 1e-9))
    checks.append(("the same fan filmed at 120 fps is seen correctly (12 rev/s)", abs(L.pattern_apparent_rev(12, 4, 120) - 12.0) < 1e-9))
    checks.append(("one-spoke wheel agrees with Session 1: 28 rev/s at 30 fps is -2 rev/s", abs(L.pattern_apparent_rev(28, 1, 30) + 2.0) < 1e-9))
    checks.append(("hand calculation: 130 Hz sampled at 100 Hz has alias 30 Hz; 70 Hz and 170 Hz alias to 30 Hz too",
                   all(abs(L.alias_frequency(x, 100) - 30.0) < 1e-9 for x in (130, 70, 170))))
    zig = [x for x in np.arange(0, 150, 0.5) if abs(L.alias_frequency(x, 50) - 10.0) < 1e-9]
    checks.append(("graph reading: at fs = 50 the alias is 10 Hz for f = 10, 40, 60, 90, 110, 140", zig == [10.0, 40.0, 60.0, 90.0, 110.0, 140.0]))
    checks.append(("design: the 4-blade 12 rev/s fan looks -3 rev/s at 60 fps but +12 rev/s (correct) at 100 and 120 fps",
                   abs(L.pattern_apparent_rev(12, 4, 60) + 3.0) < 1e-9 and abs(L.pattern_apparent_rev(12, 4, 100) - 12.0) < 1e-9
                   and abs(L.pattern_apparent_rev(12, 4, 120) - 12.0) < 1e-9))
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
