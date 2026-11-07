"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("hand calculation: Zn/Cu is 1.10 V", abs(L.cell_voltage("Cu", "Zn") - 1.10) < 1e-9))
    checks.append(("hand calculation: 1 Ah is 3600 C = 0.03731 mol of electrons",
                   abs(L.charge_coulombs(1.0) - 3600.0) < 1e-9 and abs(3600.0 / L.FARADAY - 0.03731) < 1e-5))
    checks.append((f"hand calculation: 1 Ah dissolves 1.2197 g of zinc (got {L.metal_mass_g(3600.0, 'Zn'):.4f})",
                   abs(L.metal_mass_g(3600.0, "Zn") - 1.2197) < 5e-4))
    d = L.design_pack(12.0, 2.0, 1.10, 1.0)
    checks.append((f"worked example: 12 V and 2 Ah from 1.10 V, 1 Ah cells = 11 in series x 2 strings, 12.1 V, 24.2 Wh, 26.8 g zinc (got {d['ns']}x{d['npar']}, {d['volts']:.1f} V, {d['watt_hours']:.1f} Wh, {d['metal_g']:.1f} g)",
                   d["ns"] == 11 and d["npar"] == 2 and d["cells"] == 22 and abs(d["volts"] - 12.1) < 1e-9
                   and abs(d["watt_hours"] - 24.2) < 1e-9 and abs(d["metal_g"] - 26.83) < 0.01))
    checks.append(("energy equals the sum over cells of V x Ah",
                   abs(d["watt_hours"] - d["cells"] * 1.10 * 1.0) < 1e-9))
    checks.append(("zinc needed = cells x grams per Ah (linear in charge)",
                   abs(L.metal_mass_g(7200.0, "Zn") - 2 * L.metal_mass_g(3600.0, "Zn")) < 1e-12))
    checks.append(("zero charge consumes zero metal", L.metal_mass_g(0.0, "Zn") == 0.0))
    checks.append(("edge: exactly 11 V from 1.1 V cells needs 10, not 11", L.design_pack(11.0, 1.0, 1.1, 1.0)["ns"] == 10))
    checks.append(("edge: exactly 2 Ah from 1 Ah cells needs 2 strings", L.design_pack(1.0, 2.0, 1.1, 1.0)["npar"] == 2))
    checks.append(("lithium stores about 3861 mAh per gram, zinc about 820",
                   abs(L.specific_capacity_mah_per_g("Li") - 3861) < 2 and abs(L.specific_capacity_mah_per_g("Zn") - 820) < 1))
    checks.append(("a series string keeps the capacity, parallel keeps the voltage",
                   L.pack(5, 1, 1.1, 2.0)["amp_hours"] == 2.0 and L.pack(1, 5, 1.1, 2.0)["volts"] == 1.1))
    bad = 0
    for args in ((0, 1), (1, 0), (1.5, 1)):
        try:
            L.pack(args[0], args[1], 1.1, 1.0)
        except ValueError:
            bad += 1
    checks.append(("invalid cell counts are rejected", bad == 3))
    z = L.metal_mass_g(0.5 * 4 * 3600.0, "Zn")
    checks.append((f"hand calculation: 0.5 A for 4 h dissolves 2.439 g of zinc (got {z:.3f})", abs(z - 2.439) < 5e-4))
    d2 = L.design_pack(6.0, 3.0, 1.10, 0.8)
    checks.append((f"design example: 6 V and 3 Ah from 1.10 V, 0.8 Ah cells = 6 x 4 = 24 cells, 21.1 Wh, 23.4 g zinc (got {d2['ns']}x{d2['npar']}, {d2['watt_hours']:.1f} Wh, {d2['metal_g']:.1f} g)",
                   d2["ns"] == 6 and d2["npar"] == 4 and abs(d2["watt_hours"] - 21.12) < 0.01 and abs(d2["metal_g"] - 23.42) < 0.01))
    checks.append(("Section F: 11 series cells give 13.4 g of zinc per ampere-hour of pack capacity", abs(11 * L.metal_mass_g(3600.0, "Zn") - 13.42) < 0.01))
    checks.append(("runtime = capacity / current: 2 Ah at 0.5 A lasts 4 h", abs(L.runtime_hours(2.0, 0.5) - 4.0) < 1e-12))
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
