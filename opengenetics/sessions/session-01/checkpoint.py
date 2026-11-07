"""Checkpoint for Session 1. Prints PASS or FAIL."""


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    gc = L.genotype_counts("Aa", "Aa")
    pc = L.phenotype_counts("Aa", "Aa")
    checks.append(("worked example: Aa x Aa gives genotypes AA:Aa:aa = 1:2:1", (gc["AA"], gc["Aa"], gc["aa"]) == (1, 2, 1)))
    checks.append(("worked example: Aa x Aa gives appearance 3 dominant : 1 recessive", (pc["dominant"], pc["recessive"]) == (3, 1)))
    gc2 = L.genotype_counts("AA", "aa")
    checks.append(("AA x aa: all four boxes are Aa", gc2 == {"AA": 0, "Aa": 4, "aa": 0}))
    pc3 = L.phenotype_counts("Aa", "aa")
    checks.append(("Aa x aa gives appearance 2 : 2 (a 1 : 1 ratio)", (pc3["dominant"], pc3["recessive"]) == (2, 2)))
    checks.append(("aa x aa: all four boxes are aa", L.genotype_counts("aa", "aa") == {"AA": 0, "Aa": 0, "aa": 4}))
    checks.append(("the four boxes always add up to 4", all(sum(L.genotype_counts(a, b).values()) == 4 for a in ("AA", "Aa", "aa") for b in ("AA", "Aa", "aa"))))
    checks.append(("order of letters does not matter: child_genotype('a','A') is 'Aa'", L.child_genotype("a", "A") == "Aa"))
    r = L.simulate_children("Aa", "Aa", 10000)
    checks.append((f"simulation of 10000 Aa x Aa children: recessive fraction near 0.25 (got {r['recessive'] / 10000:.3f})", abs(r["recessive"] / 10000 - 0.25) < 0.02))
    r0 = L.simulate_children("AA", "Aa", 2000)
    checks.append(("AA x Aa gives genotypes AA:Aa:aa = 2:2:0", L.genotype_counts("AA", "Aa") == {"AA": 2, "Aa": 2, "aa": 0}))
    checks.append(("AA x Aa never gives a recessive child", r0["recessive"] == 0))
    checks.append(("a seeded simulation repeats exactly", L.simulate_children("Aa", "Aa", 500, seed=3) == L.simulate_children("Aa", "Aa", 500, seed=3)))
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
