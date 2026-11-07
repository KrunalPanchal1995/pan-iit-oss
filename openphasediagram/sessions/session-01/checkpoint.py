"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def _time_at(t, T, T_target):
    """Time at which a falling temperature curve first reaches T_target."""
    i = int(np.argmax(T <= T_target))
    return float(t[i])


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("pure Cu and pure Ni melt at 1085 C and 1455 C",
                   abs(float(L.liquidus(0)) - 1085) < 1e-9 and abs(float(L.liquidus(100)) - 1455) < 1e-9))
    checks.append(("a pure metal has zero melting range (liquidus = solidus)",
                   L.melting_range(0) == 0.0 and L.melting_range(100) == 0.0))
    checks.append(("worked example: 50 wt% Ni melts between 1240 C and 1320 C, a range of 80 K",
                   float(L.solidus(50)) == 1240.0 and float(L.liquidus(50)) == 1320.0 and abs(L.melting_range(50) - 80.0) < 1e-9))
    checks.append(("50 wt% Ni is liquid at 1400 C, liquid + solid at 1280 C, solid at 1200 C",
                   (L.region(50, 1400), L.region(50, 1280), L.region(50, 1200)) == ("liquid", "liquid + solid", "solid")))
    checks.append(("boundary: exactly on the liquidus counts as liquid + solid, exactly on the solidus too",
                   L.region(50, 1320) == "liquid + solid" and L.region(50, 1240) == "liquid + solid"))
    checks.append(("every alloy has liquidus >= solidus",
                   bool(np.all(L.liquidus(np.linspace(0, 100, 101)) >= L.solidus(np.linspace(0, 100, 101))))))

    # hand calculation: the arrest of a pure metal lasts L / Q = 200 / 2 = 100 s
    arrest_hand = L.L_HEAT / L.Q_OUT
    checks.append((f"pure Cu: flat arrest lasts L/Q = {arrest_hand:.0f} s (got {L.arrest_time(0.0):.1f} s)",
                   abs(L.arrest_time(0.0) - arrest_hand) < 0.2))
    checks.append(("alloy 50 wt% Ni has no flat arrest", L.arrest_time(50.0) < 0.05))

    # cooling rates: liquid cools at Q/c = 4 K/s, inside the range of the alloy much slower
    t, T = L.cooling_curve(50.0)
    rate_liquid = L.Q_OUT / L.C_HEAT
    i = np.searchsorted(-T, -1400.0)
    j = i + 50
    rate_meas = -(T[j] - T[i]) / (t[j] - t[i])
    checks.append((f"liquid cools at Q/c = {rate_liquid:.1f} K/s (measured {rate_meas:.2f})", abs(rate_meas - rate_liquid) < 0.05))
    tL = _time_at(t, T, 1320.0)
    tS = _time_at(t, T, 1240.0)
    mean_rate = 80.0 / (tS - tL)
    hand = 80.0 / ((L.C_HEAT * 80.0 + L.L_HEAT) / L.Q_OUT)
    checks.append((f"alloy: mean cooling rate across the range is 80 K / 120 s = 0.67 K/s (measured {mean_rate:.2f}, hand {hand:.2f})",
                   abs(mean_rate - hand) < 0.02 and abs(hand - 2.0 / 3.0) < 1e-9))
    checks.append(("cooling curve never rises", bool(np.all(np.diff(T) <= 1e-9))))
    frac = L.frozen_fraction([1330.0, 1280.0, 1230.0], 50.0)
    checks.append(("frozen fraction is 0 above the liquidus, 0.5 midway, 1 below the solidus", np.allclose(frac, [0.0, 0.5, 1.0])))
    # design: which alloys are fully liquid at 1350 C and fully solid at 1200 C?
    ok = [c for c in range(0, 101) if float(L.liquidus(c)) <= 1350.0 and float(L.solidus(c)) >= 1200.0]
    checks.append((f"design: liquid at 1350 C and solid at 1200 C needs {ok[0]} to {ok[-1]} wt% Ni (37 and 62 fail)",
                   (ok[0], ok[-1]) == (38, 61) and 37 not in ok and 62 not in ok and 0 not in ok and 100 not in ok))
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
