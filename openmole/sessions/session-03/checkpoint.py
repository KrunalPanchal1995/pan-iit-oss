"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    for r, p, c in L.KNOWN:
        res = L.balance(r, p)
        checks.append((f"validation: {' + '.join(r)} -> {' + '.join(p)} gives {c}", res["coefs"] == c and res["nullity"] == 1))
    # worked example: Fe2O3 + Al -> Al2O3 + Fe, matrix rows Fe, O, Al
    A, els = L.build_matrix(["Fe2O3", "Al"], ["Al2O3", "Fe"])
    checks.append(("worked example: Fe2O3 + Al -> Al2O3 + Fe matrix (rows Al, Fe, O) is [[0,1,-2,0],[2,0,0,-1],[3,0,-3,0]] and (1,2,1,2) is in its null space",
                   els == ["Al", "Fe", "O"] and np.allclose(A, [[0, 1, -2, 0], [2, 0, 0, -1], [3, 0, -3, 0]])
                   and np.allclose(A @ [1, 2, 1, 2], 0)))
    for r, p, c in L.KNOWN:
        cons = L.conservation(r, p, c)
        if not (all(abs(v) < 1e-9 for v in cons["atoms"].values()) and abs(cons["mass_g"]) < 1e-9 and abs(cons["charge"]) < 1e-12):
            checks.append((f"atoms and mass conserved for {p}", False))
            break
    else:
        checks.append(("every validated reaction conserves each element and total mass", True))
    ion_r, ion_p = ["MnO4^-", "Fe^2+", "H^+"], ["Mn^2+", "Fe^3+", "H2O"]
    res = L.balance(ion_r, ion_p)
    checks.append(("ionic: MnO4^- + 5 Fe^2+ + 8 H^+ -> Mn^2+ + 5 Fe^3+ + 4 H2O", res["coefs"] == [1, 5, 8, 1, 5, 4]))
    cons = L.conservation(ion_r, ion_p, res["coefs"])
    checks.append(("ionic charge is conserved (+17 on each side) and mass balances", abs(cons["charge"]) < 1e-12 and abs(cons["mass_g"]) < 1e-9))
    checks.append(("without the charge row the nullity grows from 1 to 2", res["nullity"] == 1 and L.balance(ion_r, ion_p, use_charge=False)["nullity"] == 2))
    cu = L.balance(["Cu", "Ag^+"], ["Cu^2+", "Ag"])
    checks.append(("Cu + 2 Ag^+ -> Cu^2+ + 2 Ag", cu["coefs"] == [1, 2, 1, 2]))
    # failure cases
    none = L.balance(["H2", "O2"], ["NaCl"])
    checks.append(("failure: H2 + O2 -> NaCl has nullity 0 and no coefficients", none["nullity"] == 0 and none["coefs"] is None))
    two = L.balance(["H2", "O2"], ["H2O", "H2O2"])
    checks.append(("failure: H2 + O2 -> H2O + H2O2 has nullity 2 and basis (2,1,2,0), (1,1,0,1)",
                   two["nullity"] == 2 and two["coefs"] is None and sorted(two["basis"]) == [[1, 1, 0, 1], [2, 1, 2, 0]]))
    wrong = L.balance(["H2", "H2O"], ["O2"])
    checks.append(("failure: a species on the wrong side gives a null vector with a negative entry", wrong["nullity"] == 1 and wrong["coefs"] is None))
    # edge cases
    checks.append(("to_integers rationalises (0.5, 0.5, 1.0) to (1, 1, 2)", L.to_integers([0.5, 0.5, 1.0]) == [1, 1, 2]))
    checks.append(("to_integers fixes the sign: (-0.2, -0.4) becomes (1, 2)", L.to_integers([-0.2, -0.4]) == [1, 2]))
    sw = L.balance(["O2", "H2"], ["H2O"])
    checks.append(("species order does not matter: O2 + H2 -> H2O gives 1, 2, 2", sw["coefs"] == [1, 2, 2]))
    big = L.balance(["C6H12O6", "O2"], ["CO2", "H2O"])
    checks.append(("coefficients are the smallest integers (gcd 1)", int(np.gcd.reduce(big["coefs"])) == 1))
    # reactor
    ext, left, prod = L.react((1, 3), [1.0, 3.0], (2,))
    checks.append(("exact 1 : 3 feed leaves nothing over (boundary)", abs(ext - 1.0) < 1e-12 and max(abs(x) for x in left) < 1e-12 and abs(prod[0] - 2.0) < 1e-12))
    tab = L.sweep_feed_ratio(np.linspace(0.0, 6.0, 121))
    checks.append(("yield plateaus at 2 mol NH3 for ratios of 3 and above", np.allclose(tab[tab[:, 0] >= 3, 1], 2.0)))
    checks.append(("NH3 mass over feed mass peaks at ratio 3.0 and equals 1 there (mass conserved)",
                   abs(tab[np.argmax(tab[:, 2]), 0] - 3.0) < 1e-9 and abs(tab[:, 2].max() - 1.0) < 1e-3))
    checks.append(("no ammonia without hydrogen", tab[0, 1] == 0.0))
    # mini-project and sensitivity
    h2 = L.reagent_mass_kg(1000.0, "NH3", 2, "H2", 3)
    n2 = L.reagent_mass_kg(1000.0, "NH3", 2, "N2", 1)
    hand = 1000.0 * 1.5 * 2.016 / 17.031
    checks.append(("mini-project: 1 tonne NH3 needs 177.6 kg of H2 (hand: 1000 * 1.5 * 2.016 / 17.031)", abs(h2 - 177.6) < 0.05 and abs(h2 - hand) < 1e-6))
    checks.append(("mini-project: mass balance H2 + N2 = 1000 kg of NH3", abs(h2 + n2 - 1000.0) < 1e-9))
    checks.append(("a 90 % yield needs 1 / 0.9 times more hydrogen", abs(L.reagent_mass_kg(1000.0, "NH3", 2, "H2", 3, yield_fraction=0.9) - h2 / 0.9) < 1e-9))
    s = L.sensitivity(("H", "N"))
    checks.append(("sensitivity: +1 % on M(H) raises, +1 % on M(N) lowers the hydrogen needed, each by about 0.8 %",
                   0.80 < s["H"] < 0.84 and -0.84 < s["N"] < -0.80))
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
