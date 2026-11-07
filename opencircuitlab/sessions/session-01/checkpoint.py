"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    s = L.series_chain(6.0, 3)
    checks.append(("worked example: 6 V, 3 bulbs in series -> 0.2 A, 2 V and 0.4 W each",
                   np.isclose(s["i"], 0.2) and np.isclose(s["v_each"], 2.0) and np.isclose(s["p_each"], 0.4)))
    p = L.parallel_bank(6.0, 3)
    checks.append(("worked example: 6 V, 3 bulbs in parallel -> 1.8 A total, 6 V and 3.6 W each",
                   np.isclose(p["i"], 1.8) and np.isclose(p["v_each"], 6.0) and np.isclose(p["p_each"], 3.6)))
    checks.append(("series: the voltages across the bulbs add up to the battery voltage",
                   np.isclose(3 * s["v_each"], 6.0)))
    checks.append(("energy: total bulb power equals battery voltage times battery current",
                   np.isclose(s["p_total"], 6.0 * s["i"]) and np.isclose(p["p_total"], 6.0 * p["i"])))
    checks.append(("one bulb gives the same answer in series and in parallel",
                   np.isclose(L.series_chain(9.0, 1)["p_each"], L.parallel_bank(9.0, 1)["p_each"])))
    checks.append(("open switch: no current in either wiring",
                   L.series_chain(6, 2, switch_closed=False)["i"] == 0.0 and L.parallel_bank(6, 2, switch_closed=False)["i"] == 0.0))
    ratio = L.series_chain(8.0, 4)["p_each"] / L.parallel_bank(8.0, 4)["p_each"]
    checks.append(("N bulbs in series are N squared times dimmer than in parallel (N = 4 -> 1/16)", np.isclose(ratio, 1 / 16)))
    try:
        L.series_chain(6, 0)
        ok = False
    except ValueError:
        ok = True
    checks.append(("zero bulbs is rejected", ok))
    # optional hot-bulb model (issue: real-bulb model)
    h6 = L.hot_bulb_current(6.0)
    checks.append((f"hot bulb at 6 V: warm current is 0.6 A like the 10 ohm model (got {h6['i_warm']:.3f})", abs(h6["i_warm"] - 0.6) < 1e-9))
    checks.append((f"hot bulb at 6 V: switch-on current is 7 times the warm current (got {h6['i_on'] / h6['i_warm']:.2f})",
                   abs(h6["i_on"] / h6["i_warm"] - 7.0) < 1e-9))
    checks.append(("hot bulb: warm state satisfies P = v * i and R = r_cold * (1 + a * P)",
                   abs(h6["p_warm"] - 6.0 * h6["i_warm"]) < 1e-9 and abs(h6["r_warm"] - L.R_COLD * (1 + L.A_HOT * h6["p_warm"])) < 1e-9))
    h0 = L.hot_bulb_current(0.0)
    checks.append(("hot bulb: no battery means no current", h0["i_on"] == 0.0 and h0["i_warm"] == 0.0))
    hl = L.hot_bulb_current(0.05)
    checks.append(("hot bulb at a tiny voltage barely warms: warm current is within 1 percent of the cold current",
                   abs(hl["i_warm"] - hl["i_on"]) / hl["i_on"] < 0.01))
    checks.append(("hot bulb: with no heating coefficient the warm current equals the cold current",
                   abs(L.hot_bulb_current(6.0, a_hot=0.0)["i_warm"] - 6.0 / L.R_COLD) < 1e-9))
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
