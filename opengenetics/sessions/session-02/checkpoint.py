"""Checkpoint for Session 2. Prints PASS or FAIL."""


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    c = L.child_probabilities(0.5, 0.5)
    checks.append(("multiplication rule: Aa x Aa gives P(aa) = 1/4", abs(c["aa"] - 0.25) < 1e-12))
    checks.append(("addition rule: Aa x Aa gives P(carrier Aa) = 1/4 + 1/4 = 1/2", abs(c["Aa"] - 0.5) < 1e-12))
    checks.append(("child probabilities add to 1", abs(sum(L.child_probabilities(0.3, 0.8).values()) - 1) < 1e-12))
    checks.append(("a parent AA passes A with probability 1, Aa with 1/2, aa with 0", (L.passes_A("AA"), L.passes_A("Aa"), L.passes_A("aa")) == (1.0, 0.5, 0.0)))

    q = L.q_from_recessive_rate(1e-4)
    hw = L.hardy_weinberg(q)
    checks.append((f"worked example: 1 in 10000 gives q = 0.01 (got {q:.4f})", abs(q - 0.01) < 1e-12))
    checks.append((f"worked example: carrier proportion 2pq = 0.0198 (got {hw['Aa']:.4f})", abs(hw["Aa"] - 0.0198) < 1e-12))
    checks.append(("Hardy-Weinberg proportions add to 1 for q = 0.37", abs(sum(L.hardy_weinberg(0.37).values()) - 1) < 1e-12))
    checks.append(("hand check: q = 0.5 gives 1/4 : 1/2 : 1/4", all(abs(a - b) < 1e-12 for a, b in zip(L.hardy_weinberg(0.5).values(), (0.25, 0.5, 0.25)))))
    checks.append(("edge: q = 0 gives no carriers and no aa", L.hardy_weinberg(0.0) == {"AA": 1.0, "Aa": 0.0, "aa": 0.0}))

    q_est = L.allele_freq_from_counts(640, 320, 40)
    checks.append((f"design: counts 640/320/40 give q = 0.2 (got {q_est:.3f})", abs(q_est - 0.2) < 1e-12))
    checks.append(("counts 640/320/40 match Hardy-Weinberg for q = 0.2 (0.64, 0.32, 0.04)",
                   all(abs(a - b) < 1e-12 for a, b in zip(L.hardy_weinberg(q_est).values(), (0.64, 0.32, 0.04)))))

    x2 = L.chi_square_3_to_1(740, 260)
    checks.append((f"chi-square for 740:260 is 100/750 + 100/250 = 0.533 (got {x2:.3f})", abs(x2 - (100 / 750 + 100 / 250)) < 1e-9))
    checks.append(("740:260 is below 3.84, so 3:1 is not rejected", L.consistent_with_3_to_1(740, 260)))
    x2b = L.chi_square_3_to_1(800, 200)
    checks.append((f"chi-square for 800:200 is 13.33 (got {x2b:.2f}), above 3.84, so 3:1 is rejected",
                   abs(x2b - 40 / 3) < 1e-9 and not L.consistent_with_3_to_1(800, 200)))
    checks.append(("a perfect 3:1 sample (750:250) gives chi-square 0", L.chi_square_3_to_1(750, 250) == 0))
    ok = L.acceptable_recessive_counts(100)
    checks.append((f"design: of 100 children, 3:1 is kept for 17 to 33 recessive (got {ok[0]} to {ok[-1]})", (ok[0], ok[-1]) == (17, 33) and len(ok) == 17))

    q2 = L.q_from_recessive_rate(1 / 2500)
    hw2 = L.hardy_weinberg(q2)
    checks.append((f"1 in 2500 gives q = 0.02 and carriers 2pq = 0.0392 (got {q2:.3f}, {hw2['Aa']:.4f})", abs(q2 - 0.02) < 1e-12 and abs(hw2["Aa"] - 0.0392) < 1e-12))
    ok1000 = L.acceptable_recessive_counts(1000)
    checks.append((f"design: of 1000 children, 3:1 is kept for 224 to 276 recessive (got {ok1000[0]} to {ok1000[-1]})", (ok1000[0], ok1000[-1]) == (224, 276)))
    checks.append(("chi-square for 70:30 is 1.33, so 3:1 is kept", abs(L.chi_square_3_to_1(70, 30) - 4 / 3) < 1e-9 and L.consistent_with_3_to_1(70, 30)))

    d = L.dihybrid_counts()
    checks.append(("dihybrid AaBb x AaBb gives 9:3:3:1", (d["A_B_"], d["A_bb"], d["aaB_"], d["aabb"]) == (9, 3, 3, 1)))
    checks.append(("dihybrid: 3/4 x 3/4 = 9/16 by the multiplication rule", abs(0.75 * 0.75 - 9 / 16) < 1e-12))
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
