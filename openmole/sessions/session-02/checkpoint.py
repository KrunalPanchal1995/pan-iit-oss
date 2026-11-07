"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("M(H2O) = 18.015 g/mol (hand: 2 * 1.008 + 15.999)", abs(L.molar_mass("H2O") - 18.015) < 1e-9))
    checks.append(("M(CaCO3) = 100.086 g/mol (hand: 40.078 + 12.011 + 3 * 15.999)", abs(L.molar_mass("CaCO3") - 100.086) < 1e-9))
    checks.append(("M(CH4) = 16.043 and M(CO2) = 44.009", abs(L.molar_mass("CH4") - 16.043) < 1e-9 and abs(L.molar_mass("CO2") - 44.009) < 1e-9))
    checks.append(("18.015 g of water is one mole = 6.022e23 molecules",
                   abs(L.moles(18.015, "H2O") - 1.0) < 1e-12 and abs(L.molecules(1.0) - 6.022e23) < 1e17))
    co2 = L.convert_mass(16.0, "CH4", 1, "CO2", 1)
    checks.append(("worked example: 16 g of CH4 gives 43.9 g of CO2 (43.89 g)", abs(co2 - 43.89) < 0.01))
    h2o = L.convert_mass(16.0, "CH4", 1, "H2O", 2)
    o2 = L.convert_mass(16.0, "CH4", 1, "O2", 2)
    checks.append(("mass is conserved: CH4 + O2 in = CO2 + H2O out", abs(16.0 + o2 - co2 - h2o) < 1e-9))
    meth = [(1, "CH4"), (2, "O2")]
    k, ext = L.limiting_reagent(meth, [40.0, 50.0])
    checks.append(("40 g CH4 with 50 g O2: oxygen limits (index 1), extent 0.7813 mol", k == 1 and abs(ext - 0.7813) < 1e-3))
    k, ext = L.limiting_reagent(meth, [16.0, 200.0])
    checks.append(("16 g CH4 with excess O2: methane limits (index 0)", k == 0))
    k, ext = L.limiting_reagent(meth, [L.grams(1.0, "CH4"), L.grams(2.0, "O2")])
    checks.append(("exact 1 : 2 mole feed is balanced; the extent is 1 mol (edge case)", abs(ext - 1.0) < 1e-12))
    checks.append(("percent yield: 40.0 g actual out of 43.89 g is 91.1 %", abs(L.percent_yield(40.0, co2) - 91.14) < 0.01))
    checks.append(("0.10 M NaCl, 0.5 L needs 2.922 g (hand: 0.05 mol * 58.44)", abs(L.solute_mass(0.10, 0.5, "NaCl") - 2.922) < 1e-3))
    checks.append(("molarity: 0.05 mol in 0.5 L is 0.10 mol/L", abs(L.molarity(0.05, 0.5) - 0.10) < 1e-12))
    checks.append(("limestone for 500 kg acid, pure: 510.3 kg", abs(L.limestone_needed(500.0) - 510.3) < 0.1))
    checks.append(("92 % pure with 10 % excess: 610.1 kg", abs(L.limestone_needed(500.0, 0.92, 0.10) - 610.1) < 0.1))
    checks.append(("limestone scales linearly with acid", abs(L.limestone_needed(1000.0) - 2 * L.limestone_needed(500.0)) < 1e-9))
    acid = 98.072
    checks.append(("one mole of acid (98.072 g) needs one mole of CaCO3 (100.086 g)",
                   abs(L.convert_mass(acid, "H2SO4", 1, "CaCO3", 1) - 100.086) < 1e-6))
    try:
        L.molar_mass("Xx2")
        ok = False
    except KeyError:
        ok = True
    checks.append(("an element missing from the table raises KeyError", ok))
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
