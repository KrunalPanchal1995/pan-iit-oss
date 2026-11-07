"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    prof = L.load_profile()
    checks.append(("profile has 24 hourly values", len(prof) == 24))
    kwh = L.daily_kwh(prof)
    checks.append((f"daily energy = 2.88 + 1.68 + 0.30 + 0.40 + 3.00 = 8.26 kWh (got {kwh:.2f})", abs(kwh - 8.26) < 1e-9))
    # hand calculation of the slab bill for 247.8 kWh
    hand = 50 + 100 * 3.0 + 100 * 5.0 + 47.8 * 7.5
    bill = L.monthly_bill(prof)
    checks.append((f"worked example: 247.8 kWh costs 50+300+500+358.5 = Rs 1208.50 (got {bill:.2f})", abs(bill - hand) < 1e-6))
    checks.append(("slab bill at 0 kWh is the fixed charge", abs(L.slab_bill(0.0) - 50.0) < 1e-12))
    checks.append(("slab bill at exactly 100 kWh is 50 + 300", abs(L.slab_bill(100.0) - 350.0) < 1e-12))
    checks.append(("bill never decreases as usage grows", all(L.slab_bill(a) <= L.slab_bill(a + 1) for a in range(0, 400))))
    try:
        L.slab_bill(-1.0)
        bad = False
    except ValueError:
        bad = True
    checks.append(("negative energy is rejected", bad))
    checks.append(("peak demand is 0.12 + 1.5 = 1.62 kW at 6-7 h", abs(L.peak_kw(prof) - 1.62) < 1e-9 and int(np.argmax(prof)) == 6))
    checks.append(("current at 1.62 kW, pf 0.9, 230 V is 7.83 A", abs(L.current_amps(1.62, 0.9) - 7.826) < 0.01))
    checks.append(("unity power factor: kVA equals kW", abs(L.apparent_kva(1.62, 1.0) - 1.62) < 1e-12))
    checks.append(("a heater from 23:00 for 2 h wraps past midnight", abs(L.overlap(0, 23.0, 2.0) - 1.0) < 1e-12 and abs(L.overlap(23, 23.0, 2.0) - 1.0) < 1e-12))
    checks.append(("moving the heater keeps the energy, changes the peak hour", abs(L.daily_kwh(L.load_profile(19.0)) - kwh) < 1e-9))
    d = L.heater_hours_for_bill(0.8 * bill)
    new = L.monthly_bill(L.load_profile(6.0, d))
    checks.append((f"design: heater {d:.3f} h gives 80% of the bill", abs(new - 0.8 * bill) < 1e-3))
    cut = 1 - L.daily_kwh(L.load_profile(6.0, d)) / kwh
    checks.append((f"a 20% bill cut needs only a {100 * cut:.1f}% energy cut (the top slab is dearer)", 0.12 < cut < 0.14))
    checks.append(("bill target below the fixed charge is impossible", L.heater_hours_for_bill(10.0) is None))
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
