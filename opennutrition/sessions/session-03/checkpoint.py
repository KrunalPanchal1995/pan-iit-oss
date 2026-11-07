"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    a = L.ASHA
    A, B = L.exp_params(a["pal"], a["height_cm"], a["age"], a["sex"])
    E0 = A * a["m0"] + B
    checks.append(("Asha: A = 15.5 kcal/day per kg and B = 1193.89 kcal/day", abs(A - 15.5) < 1e-9 and round(B, 2) == 1193.89))
    checks.append(("Asha's starting expenditure is 2123.9 kcal/day", round(E0, 1) == 2123.9))
    checks.append(("time constant RHO / A is about 497 days", round(L.time_constant(A)) == 497))
    I = 2400.0
    t, m = L.simulate(60.0, I, A, B, 84)
    ex = L.exact_mass(60.0, I, A, B, t)
    checks.append(("Euler (dt = 1 day) matches the closed-form exponential within 0.01 kg over 12 weeks", float(np.max(np.abs(m - ex))) < 0.01))
    _, m_half = L.simulate(60.0, I, A, B, 84, dt=0.5)
    e1 = abs(m[-1] - ex[-1])
    e2 = abs(m_half[-1] - ex[-1])
    checks.append(("halving the time step roughly halves the Euler error (first-order method)", 1.7 < e1 / e2 < 2.3))
    checks.append(("worked example: eating 2400 kcal/day gives a steady state of 77.81 kg",
                   round(float(L.steady_state(I, A, B)), 2) == 77.81))
    checks.append(("worked example: after 12 weeks the dynamic model gives 62.77 kg and the naive rule 63.01 kg",
                   round(float(ex[-1]), 2) == 62.77 and round(float(L.naive_mass(60.0, I, A, B, 84)), 2) == 63.01))
    t2, m2 = L.simulate(60.0, I, A, B, 730)
    checks.append(("after 2 years the dynamic model gives 73.72 kg but the naive rule 86.18 kg",
                   round(float(m2[-1]), 2) == 73.72 and round(float(L.naive_mass(60.0, I, A, B, 730)), 2) == 86.18))
    checks.append(("the dynamic curve never passes the steady state (monotone approach)",
                   bool(np.all(np.diff(m2) > 0)) and float(m2[-1]) < float(L.steady_state(I, A, B))))
    checks.append(("intake equal to expenditure keeps mass at 60 kg (edge case)", abs(float(L.exact_mass(60.0, E0, A, B, 500)) - 60.0) < 1e-9))
    checks.append(("naive and dynamic agree at time zero", float(L.naive_mass(60.0, I, A, B, 0)) == 60.0 == float(L.exact_mass(60.0, I, A, B, 0))))
    d = L.monte_carlo(60.0, E0, A, B, 84)
    p5, p50, p95 = np.percentile(d, [5, 50, 95])
    checks.append(("Monte Carlo: the 5th and 95th percentiles of the 12-week change are about -2.87 and +2.88 kg",
                   abs(p5 + 2.87) < 0.1 and abs(p95 - 2.88) < 0.1))
    checks.append(("Monte Carlo: the median is near zero and the standard deviation is about 1.74 kg",
                   abs(p50) < 0.1 and abs(d.std() - 1.74) < 0.1))
    d0 = L.monte_carlo(60.0, E0, A, B, 84, intake_err=0.0, bmr_err=0.0, n=100)
    checks.append(("with no input error the spread is zero (edge case)", float(np.max(np.abs(d0))) < 1e-9))
    checks.append(("rounding 8 labels to the nearest 10 kcal is at most 40 kcal/day off", L.rounding_worst_case(8) == 40.0))
    true_i = L.portion_error(E0, 0.2)
    checks.append(("logging 20 percent too little hides about 531 kcal/day (true intake 2655)", round(true_i) == 2655 and round(true_i - E0) == 531))
    gain = float(L.exact_mass(60.0, true_i, A, B, 84)) - 60.0
    checks.append(("that hidden 531 kcal/day is a gain of about 5.33 kg in 12 weeks, far from the predicted 0", abs(gain - 5.33) < 0.02))
    checks.append(("hand calculation: 1500 kcal meals with no walking leave a balance of -144.3 kcal/day", round(L.plan_balance(1500.0, 0.0), 1) == -144.3))
    checks.append(("a quarter hour of walking adds 37.5 kcal/day, so the balance is -181.8", round(L.plan_balance(1500.0, 0.25), 1) == -181.8))
    checks.append(("plans in the window -225 to -175 kcal/day are (1500, 0.25), (1500, 0.5), (1600, 1.0)",
                   L.find_plans() == [(1500.0, 0.25), (1500.0, 0.5), (1600.0, 1.0)]))
    checks.append(("the 1500 kcal and 15 minute walk plan changes mass by -1.85 kg in 12 weeks", round(L.plan_outcome(1500.0, 0.25), 2) == -1.85))
    lo, hi = L.plan_spread(1500.0, 0.25)
    checks.append(("its 5th to 95th percentile spread is about -4.03 to +0.33 kg, so a 10 percent error can hide the whole effect",
                   abs(lo + 4.03) < 0.1 and abs(hi - 0.33) < 0.1 and hi > 0))
    checks.append(("Asha's surplus at 2400 kcal/day is 276.1 kcal/day", round(2400.0 - E0, 1) == 276.1))
    checks.append(("design: an intake of 2200 kcal/day gives a steady state of 64.91 kg", round(float(L.steady_state(2200.0, A, B)), 2) == 64.91))
    checks.append(("after one time constant the mass has covered 63.2 percent of the way", round(1.0 - float(np.exp(-1.0)), 3) == 0.632
                   and abs((float(L.exact_mass(60.0, I, A, B, L.time_constant(A))) - 60.0) / (float(L.steady_state(I, A, B)) - 60.0) - 0.632) < 1e-3))
    gap2y = float(L.naive_mass(60.0, I, A, B, 730)) - float(L.exact_mass(60.0, I, A, B, 730))
    gap12 = float(L.naive_mass(60.0, I, A, B, 84)) - float(L.exact_mass(60.0, I, A, B, 84))
    checks.append(("the naive and dynamic answers differ by 0.24 kg at 12 weeks but 12.46 kg at 2 years", round(gap12, 2) == 0.24 and round(gap2y, 2) == 12.46))
    checks.append(("snippet numbers: Mifflin for Asha is 1370.25 kcal/day and 5/60/20 g label is 440 kcal",
                   abs(10 * 60 + 6.25 * 165 - 5 * 20 - 161 - 1370.25) < 1e-9 and 4 * 5 + 4 * 60 + 9 * 20 == 440))
    A_hi, B_hi = L.exp_params(a["pal"], a["height_cm"], a["age"], a["sex"], scale=1.1)
    checks.append(("a BMR 10 percent too high raises A and B by 10 percent", abs(A_hi - 1.1 * A) < 1e-9 and abs(B_hi - 1.1 * B) < 1e-9))
    checks.append(("the span between the 5th and 95th percentile at 12 weeks is about 5.8 kg", abs((p95 - p5) - 5.75) < 0.15))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson3", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
