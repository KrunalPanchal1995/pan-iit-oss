"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    daniell = L.cell_voltage(L.E_STD["Cu"], L.E_STD["Zn"])
    checks.append((f"hand calculation: Daniell cell is 0.34 - (-0.76) = 1.10 V (got {daniell:.2f})", abs(daniell - 1.10) < 1e-9))
    n = L.cells_needed(4.5, 1.10)
    checks.append((f"worked example: 4.5 V needs ceil(4.5 / 1.10) = 5 Zn-Cu cells giving 5.50 V (got {n})",
                   n == 5 and abs(L.series_voltage(1.10, n) - 5.5) < 1e-9))
    checks.append(("swapping the electrodes flips the sign of the voltage",
                   abs(L.cell_voltage(-0.76, 0.34) + 1.10) < 1e-9))
    checks.append(("the flow direction text follows the sign",
                   L.electron_direction(0.34, -0.76) == "anode to cathode" and "swap" in L.electron_direction(-0.76, 0.34)
                   and "no flow" in L.electron_direction(0.34, 0.34)))
    a, c, v = L.best_pair()
    checks.append(("largest pair in the table is Li with Ag, 3.84 V", (a, c) == ("Li", "Ag") and abs(v - 3.84) < 1e-9))
    checks.append(("edge: an exact multiple does not get an extra cell (11 V from 1.1 V cells = 10)", L.cells_needed(11.0, 1.1) == 10))
    checks.append(("edge: a tiny target still needs one cell", L.cells_needed(0.1, 1.10) == 1))
    try:
        L.cells_needed(5, 0)
        ok = False
    except ValueError:
        ok = True
    checks.append(("a cell with no voltage is rejected", ok))
    fe_ag = L.cell_voltage(L.E_STD["Ag"], L.E_STD["Fe"])
    checks.append(("hand calculation: Fe/Ag is 1.24 V and 5 V needs 5 cells giving 6.20 V",
                   abs(fe_ag - 1.24) < 1e-9 and L.cells_needed(5.0, fe_ag) == 5 and abs(L.series_voltage(fe_ag, 5) - 6.2) < 1e-9))
    fe_cu = L.cell_voltage(L.E_STD["Cu"], L.E_STD["Fe"])
    checks.append(("hand calculation: 3 V needs 3 Zn-Cu cells but 4 Fe-Cu (0.78 V) cells",
                   L.cells_needed(3.0, 1.10) == 3 and abs(fe_cu - 0.78) < 1e-9 and L.cells_needed(3.0, fe_cu) == 4))
    zn_ag = L.cell_voltage(L.E_STD["Ag"], L.E_STD["Zn"])
    checks.append(("hand calculation: 6 V needs 4 Zn-Ag (1.56 V) cells or 6 Zn-Cu cells",
                   abs(zn_ag - 1.56) < 1e-9 and L.cells_needed(6.0, zn_ag) == 4 and L.cells_needed(6.0, 1.10) == 6))
    checks.append(("the hydrogen electrode is the 0 V reference", L.E_STD["H"] == 0.0))
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
