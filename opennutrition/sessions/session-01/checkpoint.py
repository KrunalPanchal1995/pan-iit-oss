"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("1 kcal = 4.184 kJ", abs(L.kcal_to_kj(1.0) - 4.184) < 1e-12))
    checks.append(("2000 kcal = 8368 kJ", abs(L.kcal_to_kj(2000) - 8368.0) < 1e-9))
    checks.append(("kJ to kcal and back restores the number", abs(L.kj_to_kcal(L.kcal_to_kj(1234.5)) - 1234.5) < 1e-9))
    walk = L.energy_out([("walking", 1)], 60.0)
    banana2 = L.energy_in([("banana (1 medium)", 2)])
    checks.append(("worked example: 1 hour of walking at 60 kg is 210 kcal, equal to two bananas (210 kcal)",
                   abs(walk - 210.0) < 1e-9 and abs(banana2 - 210.0) < 1e-9))
    checks.append(("210 kcal is about 879 kJ", abs(L.kcal_to_kj(210.0) - 878.64) < 1e-6))
    checks.append(("hand calculation: 3 eggs and 2 slices of bread are 3*78 + 2*80 = 394 kcal",
                   L.energy_in([("boiled egg (1)", 3), ("slice of bread (1)", 2)]) == 394.0))
    checks.append(("Meera's day lasts 24 hours", abs(sum(h for _, h in L.MEERA_DAY) - 24.0) < 1e-12))
    e_in = L.energy_in(L.MEERA_MEALS)
    e_out = L.energy_out(L.MEERA_DAY, L.MEERA_KG)
    checks.append(("Meera eats 2289 kcal (about 9577 kJ)", e_in == 2289.0 and round(L.kcal_to_kj(e_in)) == 9577))
    checks.append(("Meera uses 2223 kcal and her balance is +66 kcal", abs(e_out - 2223.0) < 1e-9 and abs(L.daily_balance(e_in, e_out) - 66.0) < 1e-9))
    checks.append(("a balance of zero keeps the running total at zero", np.allclose(L.running_balance([0.0] * 14), 0.0)))
    checks.append(("300 kcal short each day gives -4200 kcal after 14 days", L.running_balance([-300.0] * 14)[-1] == -4200.0))
    checks.append(("energy in with no food is 0 (edge case)", L.energy_in([]) == 0.0))
    checks.append(("zero time gives zero energy out (edge case)", L.energy_out([("running", 0)], 60.0) == 0.0))
    checks.append(("food table: banana 105, egg 78, bread 80, rice 205, apple 95, milk 150 kcal per serving",
                   [L.FOODS[k] for k in ("banana (1 medium)", "boiled egg (1)", "slice of bread (1)", "cooked rice (1 cup)", "apple (1 medium)", "milk (1 glass, 250 mL)")] == [105, 78, 80, 205, 95, 150]))
    checks.append(("MET table: sleeping 0.95, sitting 1.3, light chores 2.3, walking 3.5, cycling 6, running 9",
                   [L.MET[k] for k in ("sleeping", "sitting", "light chores", "walking", "cycling", "running")] == [0.95, 1.3, 2.3, 3.5, 6.0, 9.0]))
    checks.append(("8 hours of sleep at 60 kg is 456 kcal", abs(L.energy_out([("sleeping", 8)], 60.0) - 456.0) < 1e-9))
    checks.append(("1500 kcal is 6276 kJ", abs(L.kcal_to_kj(1500) - 6276.0) < 1e-9))
    checks.append(("eating 2000 and using 2300 gives -300 per day, so -2100 after 7 days",
                   L.daily_balance(2000, 2300) == -300 and L.running_balance([-300.0] * 7)[-1] == -2100.0))
    swapped = [("sleeping", 8), ("sitting", 10.5), ("light chores", 3), ("walking", 2.0), ("cycling", 0.5)]
    checks.append(("design: swapping half an hour of sitting for walking raises Meera's use to 2289 kcal (balance 0)",
                   abs(L.energy_out(swapped, 60.0) - 2289.0) < 1e-9 and abs((3.5 - 1.3) * 60.0 - 132.0) < 1e-9))
    checks.append(("the conversion constant is 4.184 kJ per kcal", abs(L.KJ_PER_KCAL - 4.184) < 1e-12))
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
