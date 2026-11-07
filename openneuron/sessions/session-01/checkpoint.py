"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("the smallest drive that can fire is 1.5 mV per ms (hand: 0.1 x 15)", abs(L.smallest_drive() - 1.5) < 1e-12))
    tr, sp = L.toy_neuron(1.0)
    checks.append(("weak input (1.0 mV per ms) never fires and stays below threshold", len(sp) == 0 and tr.max() < L.V_THRESH))
    checks.append(("final level for drive 1.0 is -60 mV", abs(L.final_level(1.0) - (-60.0)) < 1e-12))
    tr15, sp15 = L.toy_neuron(1.5)
    checks.append(("edge case: drive exactly 1.5 only approaches the threshold and never fires", len(sp15) == 0))
    tr2, sp2 = L.toy_neuron(2.0)
    checks.append((f"worked example: drive 2.0 first fires at step 14 (hand: ceil(ln 0.25 / ln 0.9) = 14), got {sp2[0] if sp2 else None}",
                   L.steps_to_first_spike(2.0) == 14 and sp2 and sp2[0] == 14))
    checks.append(("worked example: drive 2.0 gives 6 spikes in 100 ms", len(sp2) == 6))
    tr3, sp3 = L.toy_neuron(3.0)
    tr4, sp4 = L.toy_neuron(4.0)
    checks.append(("worked example: drive 3.0 gives 11 spikes and drive 4.0 gives 14 spikes", len(sp3) == 11 and len(sp4) == 14))
    checks.append(("all or nothing: every spike has the same height whatever the drive", tr2.max() == tr3.max() == tr4.max() == L.V_SPIKE))
    checks.append(("a stronger drive fires more often", len(sp4) > len(sp3) > len(sp2) > 0))
    gaps = np.diff(sp2)
    checks.append(("refractory period: spikes are at least 3 ms apart even for a huge drive", bool(np.all(np.diff(L.toy_neuron(50.0)[1]) >= 3))))
    checks.append(("drive 2.0: spikes are regularly spaced (gaps all 16 or 17 ms)", bool(np.all((gaps >= 16) & (gaps <= 17)))))
    checks.append(("without any input the neuron sits at rest", np.allclose(L.toy_neuron(0.0)[0], L.V_REST)))
    pulse = np.zeros(100)
    pulse[10] = 20.0
    checks.append(("one big pulse of 20 mV (above 15 mV) fires at once", L.toy_neuron(pulse)[1] == [11]))
    checks.append(("one small pulse of 10 mV does not fire", L.toy_neuron(np.where(np.arange(100) == 10, 10.0, 0.0))[1] == []))
    checks.append(("axon delay: 0.5 m at 50 m/s takes 10 ms", abs(L.travel_time_ms(0.5, 50.0) - 10.0) < 1e-12))
    checks.append(("axon delay: 1 m at 100 m/s takes 10 ms and 1 m at 1 m/s takes 1000 ms", abs(L.travel_time_ms(1.0, 100.0) - 10.0) < 1e-12 and abs(L.travel_time_ms(1.0, 1.0) - 1000.0) < 1e-9))
    checks.append(("worked example: hand calculation ln 0.25 / ln 0.9 = 13.16, so 13 steps are not enough (V = -55.08 mV) and 14 are (V = -54.58 mV)",
                   abs(np.log(0.25) / np.log(0.9) - 13.158) < 0.005 and abs(-70 + 20 * (1 - 0.9 ** 13) + 55.08) < 0.005 and abs(-70 + 20 * (1 - 0.9 ** 14) + 54.58) < 0.005))
    checks.append(("question B: drive 3.0 settles at -40 mV and first fires at step 7 (hand: ln 0.5 / ln 0.9 = 6.58)",
                   abs(L.final_level(3.0) + 40.0) < 1e-12 and L.steps_to_first_spike(3.0) == 7 == sp3[0] and abs(np.log(0.5) / np.log(0.9) - 6.579) < 0.005))
    checks.append(("question D: drive 2.5 gives 9 spikes and drive 3.5 gives 12 spikes in 100 ms", len(L.toy_neuron(2.5)[1]) == 9 and len(L.toy_neuron(3.5)[1]) == 12))
    checks.append(("question D: a 0.5 m axon needs more than 100 m/s to deliver in under 5 ms (exactly 5 ms at 100 m/s)", abs(L.travel_time_ms(0.5, 100.0) - 5.0) < 1e-12))
    checks.append(("misconception: with an enormous drive the neuron fires every 3 ms (34 spikes in 100 ms), never faster", bool(np.all(np.diff(L.toy_neuron(50.0)[1]) == 3)) and len(L.toy_neuron(50.0)[1]) == 34))
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
