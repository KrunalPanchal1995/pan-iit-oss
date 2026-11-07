"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    wood = L.average_density(4.8, 0.008)
    checks.append((f"worked example: wood block average density is 600 kg/m^3 (got {wood:.1f})", abs(wood - 600.0) < 1e-9))
    checks.append(("worked example: the wood block floats in fresh water", L.floats(wood, L.FRESH)))
    checks.append(("worked example: 60 percent of the wood block is under water",
                   abs(L.submerged_fraction(wood, L.FRESH) - 0.6) < 1e-12))
    d = L.draft_box(4.8, 0.04, L.FRESH)
    checks.append((f"worked example: draft = 4.8 / (1000 * 0.04) = 0.120 m (got {d:.3f})", abs(d - 0.12) < 1e-12))
    checks.append(("the rock (2700 kg/m^3) sinks", not L.floats(L.average_density(21.6, 0.008), L.FRESH)))
    checks.append(("a sunk object has submerged fraction 1", L.submerged_fraction(2700.0, L.FRESH) == 1.0))
    boat = L.average_density(150.0, 0.8)
    checks.append(("the steel boat floats although steel itself sinks", L.floats(boat, L.FRESH) and not L.floats(L.STEEL, L.FRESH)))
    checks.append(("a floating object displaces water of its own mass",
                   abs(L.displaced_mass(wood, 0.008, L.FRESH) - 4.8) < 1e-9 and abs(L.displaced_mass(boat, 0.8, L.SEA) - 150.0) < 1e-9))
    checks.append(("sea water holds the block higher than fresh water", L.draft_box(4.8, 0.04, L.SEA) < L.draft_box(4.8, 0.04, L.FRESH)))
    checks.append(("exactly equal density counts as sinking (neutral), not floating", not L.floats(1000.0, 1000.0)))
    checks.append(("each extra kilogram adds 2.5 cm of draft on a 0.04 m^2 bottom",
                   abs(L.draft_box(5.8, 0.04, L.FRESH) - L.draft_box(4.8, 0.04, L.FRESH) - 0.025) < 1e-12))
    # salt-water experiment (issue: salt-water sheet)
    checks.append(("35 g of salt per litre gives sea-water density 1025 kg/m^3",
                   abs(L.salt_water_density(350.0, 10.0) - L.SEA) < 1e-9))
    rows = L.salt_experiment(**L.SALT_SETUP)
    checks.append(("salt experiment: the 0 g row is the fresh-water draft",
                   abs(rows[0][2] - L.draft_box(L.SALT_SETUP["mass"], L.SALT_SETUP["area"], L.FRESH)) < 1e-12))
    checks.append(("salt experiment: more salt means a smaller draft in every row",
                   all(b[2] < a[2] for a, b in zip(rows, rows[1:]))))
    import pathlib
    here = pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path("sessions/session-01")
    sheet = here / "salt_experiment_sheet.md"
    if sheet.exists():
        table = [ln.split("|")[1:-1] for ln in sheet.read_text(encoding="utf-8").splitlines()
                 if ln.startswith("| ") and ln.split("|")[1].strip().replace(".", "").isdigit()]
        match = len(table) == len(rows) and all(
            abs(float(t[0]) - r[0]) < 1e-9 and abs(float(t[3]) - 1000 * r[2]) < 0.5 and abs(float(t[2]) - r[1]) < 0.5
            for t, r in zip(table, rows))
        checks.append(("the experiment sheet's predicted densities and drafts equal salt_experiment()", match))
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
