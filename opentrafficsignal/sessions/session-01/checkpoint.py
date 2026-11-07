"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    q, g = 0.15, 27.0
    checks.append(("cycle time for g = 27 s and amber 3 s is 60 s", abs(L.cycle_time(g) - 60.0) < 1e-12))
    checks.append(("red time is C - g = 33 s", abs(L.red_time(g) - 33.0) < 1e-12))
    checks.append(("worked example: peak queue q r = 0.15 x 33 = 4.95 cars",
                   abs(L.peak_queue_theory(q, g) - 4.95) < 1e-9))
    checks.append(("worked example: queue clears in 4.95 / 0.35 = 14.14 s",
                   abs(L.clear_time_theory(q, g) - 14.142857) < 1e-4))
    t, qu = L.queue_history(q, g, T=5 * L.cycle_time(g))
    C = L.cycle_time(g)
    steady = qu[int(2 * C / 0.1): int(3 * C / 0.1)]
    checks.append(("simulated peak queue matches q r within 0.1 car", abs(steady.max() - 4.95) < 0.1))
    checks.append(("queue is empty again before green ends", abs(qu[int((2 * C + g) / 0.1)]) < 1e-6))
    checks.append(("signal order is green, amber, red",
                   [L.signal_state(x, g) for x in (0.0, 28.0, 40.0)] == ["green", "amber", "red"]))
    checks.append(("road B runs half a cycle behind road A",
                   L.signal_state(0.0, g, offset=C / 2) == "red" and L.signal_state(33.0, g, offset=C / 2) == "green"))
    cap = L.capacity(g)
    checks.append(("capacity s g / C = 0.5 x 27 / 60 = 0.225 cars/s", abs(cap - 0.225) < 1e-12))
    checks.append(("arrival exactly at capacity needs the whole green (edge case)",
                   abs(L.clear_time_theory(cap, g) - g) < 1e-6))
    checks.append(("above capacity there is no clearing time", L.clear_time_theory(cap + 0.01, g) is None))
    checks.append(("no arrivals means no queue", L.peak_queue_theory(0.0, g) == 0.0 and L.queue_history(0.0, g, T=60.0)[1].max() == 0.0))
    _, over = L.queue_history(0.25, g, T=20 * C)
    checks.append(("above capacity the queue grows from cycle to cycle", over[-int(C / 0.1):].max() > over[int(4 * C / 0.1): int(5 * C / 0.1)].max() + 1.0))
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
