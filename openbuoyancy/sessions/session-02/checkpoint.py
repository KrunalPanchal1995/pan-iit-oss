"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    d = L.draft_barge(160000.0, 20.0, 6.0, L.FRESH)
    checks.append((f"worked example: draft = 160000 / (1000 * 20 * 6) = 1.333 m (got {d:.3f})", abs(d - 4.0 / 3.0) < 1e-12))
    cap = L.max_cargo(20.0, 6.0, 2.5, 60000.0, L.FRESH)
    checks.append((f"worked example: capacity with the deck awash is 240 t (got {cap/1000:.1f})", abs(cap - 240000.0) < 1e-6))
    cap3 = L.max_cargo(20.0, 6.0, 2.5, 60000.0, L.FRESH, 0.3)
    checks.append((f"worked example: capacity with 0.3 m freeboard is 204 t (got {cap3/1000:.1f})", abs(cap3 - 204000.0) < 1e-6))
    checks.append(("freeboard is zero at the awash load", abs(L.freeboard(300000.0, 20.0, 6.0, 2.5, L.FRESH)) < 1e-12))
    checks.append(("freeboard is negative when overloaded", L.freeboard(310000.0, 20.0, 6.0, 2.5, L.FRESH) < 0))
    checks.append(("sea water carries more than fresh water",
                   L.max_cargo(20.0, 6.0, 2.5, 60000.0, L.SEA) > L.max_cargo(20.0, 6.0, 2.5, 60000.0, L.FRESH)))
    checks.append(("buoyant force on 1 m^3 of fresh water is 9810 N", abs(L.buoyant_force(L.FRESH, 1.0) - 9810.0) < 1e-9))
    checks.append(("a floating-density object has zero net force when fully submerged",
                   abs(L.net_force_up(1000.0, 1.0, L.FRESH)) < 1e-9))
    checks.append(("floats() agrees with the density rule", L.floats(500.0, 1.0, L.FRESH) and not L.floats(1500.0, 1.0, L.FRESH)))
    # balloons
    he = L.lift_per_m3(L.gas_density(L.M_AIR, 15.0), L.gas_density(L.M_HELIUM, 15.0))
    checks.append((f"worked example: helium lifts 1.06 kg per m^3 at 15 C (got {he:.3f})", abs(he - 1.056) < 0.005))
    hot = L.lift_per_m3(L.gas_density(L.M_AIR, 20.0), L.gas_density(L.M_AIR, 100.0))
    checks.append((f"hot air at 100 C lifts about 0.26 kg per m^3 (got {hot:.3f})", abs(hot - 0.258) < 0.005))
    checks.append(("air at 15 C has density about 1.225 kg/m^3", abs(L.gas_density(L.M_AIR, 15.0) - 1.225) < 0.005))
    # design problem
    checks.append(("raft: 12 people in fresh water, 13 in sea water (65 kg each)",
                   L.people_on_raft(3.0, 2.0, 0.25, 60.0, 65.0, L.FRESH, 0.10) == 12
                   and L.people_on_raft(3.0, 2.0, 0.25, 60.0, 65.0, L.SEA, 0.10) == 13))
    checks.append(("edge: capacity exactly 12 persons of 70 kg counts 12 (round-off safe)",
                   L.people_on_raft(3.0, 2.0, 0.25, 60.0, 70.0, L.FRESH, 0.10) == 12))
    checks.append(("edge: a raft that cannot carry its own weight carries 0 people",
                   L.people_on_raft(1.0, 1.0, 0.25, 500.0, 65.0, L.FRESH, 0.10) == 0))
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
