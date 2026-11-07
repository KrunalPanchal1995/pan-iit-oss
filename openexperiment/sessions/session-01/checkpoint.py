"""Checkpoint for Session 1. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("unfair test (lid and cup size both change) says -4.0 degrees C",
                   abs(L.unfair_effect() - (-4.0)) < 1e-12))
    checks.append(("fair test (only the lid changes) says -1.0 degrees C",
                   abs(L.fair_effect() - (-1.0)) < 1e-12))
    checks.append(("the unfair test is wrong by the cup effect, -3.0 degrees C",
                   abs((L.unfair_effect() - L.fair_effect()) - L.BIG_EFFECT) < 1e-12))
    checks.append(("worked example: one run per setting gives the wrong sign with chance 0.319",
                   abs(L.p_wrong_sign(1) - 0.319) < 0.0005))
    checks.append(("hand calculation: n = 1 -> z = 1 / (1.5 * sqrt(2)) = 0.4714, tail 0.319",
                   abs(L.normal_tail(1.0 / (1.5 * math.sqrt(2.0))) - 0.319) < 0.0005))
    checks.append(("simulation agrees with the formula for n = 1 (within 0.01)",
                   abs(L.simulate_wrong_sign(1, 20000, 1) - L.p_wrong_sign(1)) < 0.01))
    checks.append(("9 runs per setting: wrong-sign chance 0.079 (simulated within 0.01)",
                   abs(L.p_wrong_sign(9) - 0.079) < 0.0005 and abs(L.simulate_wrong_sign(9, 20000, 1) - 0.079) < 0.01))
    checks.append(("25 runs per setting: wrong-sign chance below 0.01",
                   L.p_wrong_sign(25) < 0.01))
    checks.append(("wrong-sign chance never rises as n grows (n = 1..30)",
                   all(L.p_wrong_sign(k + 1) <= L.p_wrong_sign(k) for k in range(1, 30))))
    checks.append(("normal_tail(0) = 0.5 (edge case)", abs(L.normal_tail(0.0) - 0.5) < 1e-12))
    # accurate vs precise: 2000 readings, mean error close to bias, sd close to sd
    ok = True
    for name, (b, s) in L.INSTRUMENTS.items():
        me, sd = L.describe(L.thermometer(b, s, 2000, 7))
        ok &= abs(me - b) < 4 * s / math.sqrt(2000) and abs(sd - s) < 0.1 * s
    checks.append(("each thermometer's mean error is about its bias and its scatter about its sd", ok))
    me, sd = L.describe(L.thermometer(2.0, 0.1, 2000, 7))
    checks.append(("precise-but-not-accurate: mean error 2.0 +- 0.01, scatter about 0.1",
                   abs(me - 2.0) < 0.01 and abs(sd - 0.1) < 0.01))
    r = L.thermometer(0.0, 1.0, 100000, 11)
    checks.append(("averaging many readings of an unbiased jumpy thermometer approaches the truth",
                   abs(r.mean() - 50.0) < 0.02))
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
