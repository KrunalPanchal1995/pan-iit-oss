"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("protein 4, carbohydrate 4, fat 9 kcal per gram", L.KCAL_PER_G == {"protein": 4.0, "carbohydrate": 4.0, "fat": 9.0}))
    calc, diff, pct = L.label_check(450, 5, 60, 20)
    checks.append(("hand calculation: 5 g protein, 60 g carbohydrate, 20 g fat = 20 + 240 + 180 = 440 kcal",
                   calc == 440.0 and L.label_kcal(5, 60, 20) == 440.0))
    checks.append(("printed 450 kcal is 10 kcal (2.2 percent) above the computed 440", diff == 10.0 and round(pct, 1) == 2.2))
    checks.append(("a label with only fat, 10 g, is 90 kcal", L.label_kcal(0, 0, 10) == 90.0))
    ravi = L.RAVI
    bmr = L.mifflin(ravi["sex"], ravi["mass_kg"], ravi["height_cm"], ravi["age"])
    checks.append(("Mifflin-St Jeor for Ravi (male, 70 kg, 175 cm, 19 y) is 1703.75 kcal/day", abs(bmr - 1703.75) < 1e-9))
    checks.append(("Mifflin-St Jeor for a made-up woman (60 kg, 165 cm, 20 y) is 1370.25 kcal/day",
                   abs(L.mifflin("female", 60, 165, 20) - 1370.25) < 1e-9))
    checks.append(("same body, male minus female is 166 kcal/day", abs(L.mifflin("male", 60, 165, 20) - L.mifflin("female", 60, 165, 20) - 166.0) < 1e-9))
    E = L.tdee(bmr, L.PAL[ravi["pal"]])
    checks.append(("Ravi's TDEE with factor 1.55 is 2640.8 kcal/day", round(E, 1) == 2640.8))
    checks.append(("sedentary factor 1.2 gives 2044.5 kcal/day for Ravi", abs(L.tdee(bmr, L.PAL["sedentary"]) - 2044.5) < 1e-9))
    checks.append(("worked example: eating 2900 kcal/day for 30 days adds about 1.01 kg by the 7700 rule",
                   round(L.mass_change_rule(2900, E, 30), 2) == 1.01))
    series = L.mass_series(70.0, 2900.0, E, 30)
    checks.append(("difference equation agrees with the closed form", abs(series[-1] - (70.0 + L.mass_change_rule(2900, E, 30))) < 1e-9))
    checks.append(("a surplus of exactly 7700 kcal adds 1 kg", abs(L.mass_change_rule(7700.0, 0.0, 1) - 1.0) < 1e-12))
    checks.append(("a deficit of 500 kcal/day for 28 days is -1.82 kg by the rule", round(L.mass_change_rule(0.0, 500.0, 28), 2) == -1.82))
    checks.append(("zero days gives the starting mass (edge case)", L.mass_series(70.0, 3000.0, 2000.0, 0).tolist() == [70.0]))
    raised = False
    try:
        L.mifflin("other", 60, 165, 20)
    except ValueError:
        raised = True
    checks.append(("an unknown sex value is rejected (edge case)", raised))
    checks.append(("Ravi's example menu plan has 2618 kcal, 22.8 kcal below his TDEE, and meets the rules",
                   L.menu_kcal(L.RAVI_PLAN) == 2618.0 and round(E - 2618.0, 1) == 22.8 and L.plan_ok(L.RAVI_PLAN, E)))
    checks.append(("a plan using only 3 items fails the rules even if the energy matches",
                   not L.plan_ok({"rice (1 cup)": 4, "dal (1 bowl)": 4, "chapati (1)": 4}, L.menu_kcal({"rice (1 cup)": 4, "dal (1 bowl)": 4, "chapati (1)": 4}))))
    checks.append(("surplus for Ravi at 2900 kcal/day is 259.2 kcal/day", round(2900.0 - E, 1) == 259.2))
    checks.append(("Mifflin terms: 6.25 x 175 = 1093.75 and 10 x 70 = 700", 6.25 * 175 == 1093.75 and 10 * 70 == 700))
    checks.append(("activity factors 1.2, 1.375, 1.55, 1.725", [L.PAL[k] for k in ("sedentary", "light", "moderate", "active")] == [1.2, 1.375, 1.55, 1.725]))
    calc2, diff2, pct2 = L.label_check(270, 8, 30, 12)
    checks.append(("exercise label: 8 g protein, 30 g carbohydrate, 12 g fat = 260 kcal against printed 270 (3.7 percent)",
                   calc2 == 260.0 and diff2 == 10.0 and round(pct2, 1) == 3.7))
    checks.append(("a surplus of 500 kcal/day for 30 days is +1.95 kg by the rule", round(L.mass_change_rule(E + 500.0, E, 30), 2) == 1.95))
    checks.append(("energy of the menu items: rice 205, dal 204, chapati 111, paneer 134, milk 152, banana 112, peanuts 178, egg 73 kcal",
                   [L.label_kcal(*L.MENU[k]) for k in ("rice (1 cup)", "dal (1 bowl)", "chapati (1)", "paneer (50 g)", "milk (1 glass)", "banana (1)", "peanuts (30 g)", "egg (1)")] == [205.0, 204.0, 111.0, 134.0, 152.0, 112.0, 178.0, 73.0]))
    checks.append(("Ravi's plan uses 7 different items", sum(1 for n in L.RAVI_PLAN.values() if n > 0) == 7))
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
