"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    rng = np.random.default_rng(5)
    checks.append(("edge: a lost allele (p = 0) stays lost and a fixed one (p = 1) stays fixed",
                   L.drift_step(0.0, 10, rng) == 0.0 and L.drift_step(1.0, 10, rng) == 1.0))
    a = L.simulate_paths(50, 0.4, 30, 5, seed=7)
    b = L.simulate_paths(50, 0.4, 30, 5, seed=7)
    checks.append(("a seeded simulation repeats exactly", bool(np.array_equal(a, b))))
    checks.append(("frequencies stay between 0 and 1", bool(a.min() >= 0 and a.max() <= 1)))

    # selection
    checks.append(("s = 0 leaves p unchanged", abs(L.selection_step(0.3, 0.0, 0.5) - 0.3) < 1e-12))
    p1 = L.haploid_selection_step(0.10, 0.10)
    checks.append((f"worked example: p = 0.10, s = 0.10 gives p' = 0.11 / 1.01 = 0.1089 (got {p1:.4f})", abs(p1 - 0.11 / 1.01) < 1e-12 and round(p1, 4) == 0.1089))
    p = 0.05
    for _ in range(100):
        p = L.haploid_selection_step(p, 0.05)
    checks.append(("haploid update agrees with the logit closed form after 100 generations", abs(p - L.haploid_closed_form(0.05, 0.05, 100)) < 1e-9))
    gain = [L.selection_step(0.05, 0.1, h) - 0.05 for h in (0.0, 0.5, 1.0)]
    checks.append(("at low p, a dominant advantage spreads faster than additive, and additive faster than recessive", gain[0] < gain[1] < gain[2]))
    checks.append(("hand check: diploid additive update p = 0.5, s = 0.2 gives wbar = 1.1 and p' = 0.575 / 1.1 = 0.5227",
                   abs(L.selection_step(0.5, 0.2, 0.5) - 0.5 * 1.15 / 1.1) < 1e-12))

    # mutation
    p = 0.3
    for _ in range(20000):
        p = L.mutation_step(p, 1e-3, 2e-4)
    checks.append((f"mutation alone settles at nu / (mu + nu) = 0.1667 (got {p:.4f})", abs(p - 2e-4 / 1.2e-3) < 1e-6))

    # Hardy-Weinberg with huge N and no selection
    g = L.random_mating_genotypes(10 ** 6, 0.3, np.random.default_rng(1))
    checks.append((f"huge N: genotype fractions match p^2, 2pq, q^2 = 0.09, 0.42, 0.49 (got {np.round(g, 3).tolist()})",
                   bool(np.allclose(g, [0.09, 0.42, 0.49], atol=0.003))))
    big = L.simulate_paths(10 ** 6, 0.3, 50, 20, seed=2)
    checks.append(("huge N, no selection: allele frequency barely moves in 50 generations", bool(np.abs(big[-1] - 0.3).max() < 0.01)))

    # heterozygosity decay
    paths = L.simulate_paths(20, 0.5, 20, 20000, seed=1)
    h_sim = float(L.heterozygosity(paths[-1]).mean())
    h_th = L.expected_heterozygosity(0.5, 20, 20)
    checks.append((f"worked example: heterozygosity decay (1 - 1/(2N))^t, N = 20, t = 20 gives 0.301 (formula {h_th:.4f}, simulated {h_sim:.4f})",
                   abs(h_th - 0.3013) < 5e-4 and abs(h_sim - h_th) < 0.005))
    checks.append(("hand check: N = 50, 10 generations keeps 0.99^10 = 0.9044 of H",
                   abs(L.expected_heterozygosity(1.0, 50, 10) - 0.99 ** 10) < 1e-12 and round(0.99 ** 10, 4) == 0.9044))

    # fixation probability equals starting frequency
    fix, lost = L.fixation_fraction(10, 0.3, 4000, 400)
    checks.append((f"neutral allele: fixation fraction is near the start frequency 0.3 (got {fix:.3f})", abs(fix - 0.3) < 0.03 and abs(fix + lost - 1) < 1e-9))

    # sensitivity to N
    s10 = L.simulate_paths(10, 0.5, 20, 500)[-1].std()
    s1000 = L.simulate_paths(1000, 0.5, 20, 500)[-1].std()
    checks.append((f"smaller populations drift more: spread {s10:.3f} (N=10) > {s1000:.3f} (N=1000)", s10 > 3 * s1000))
    # sensitivity to s
    fx = [L.fixation_fraction(100, 0.05, 1000, 1500, s=s)[0] for s in (0.0, 0.05, 0.2)]
    checks.append(("fixation chances at N = 100 are about 5, 37 and 86 percent for s = 0, 0.05, 0.2",
                   abs(fx[0] - 0.05) < 0.03 and abs(fx[1] - 0.37) < 0.06 and abs(fx[2] - 0.86) < 0.05))
    checks.append(("spread of p after 20 generations is about 0.4 at N = 10 and 0.05 at N = 1000", abs(s10 - 0.40) < 0.05 and abs(s1000 - 0.05) < 0.02))
    checks.append((f"a larger s raises the fixation chance at N = 100 (got {fx[0]:.2f}, {fx[1]:.2f}, {fx[2]:.2f})", fx[0] < fx[1] < fx[2]))

    # failure case
    f_small, l_small = L.fixation_fraction(10, 0.05, 1000, 600, s=0.05)
    f_big, l_big = L.fixation_fraction(5000, 0.05, 200, 600, s=0.05)
    checks.append((f"failure case: beneficial allele (s = 0.05) is lost in {l_small:.0%} of runs at N = 10", l_small > 0.8))
    checks.append((f"large N (5000): the same allele is never lost and almost always fixes (fixed {f_big:.0%})", l_big == 0 and f_big > 0.95))

    # mini-project
    n = L.min_population_for_heterozygosity(0.9, 50)
    checks.append((f"mini-project: smallest N keeping 90% heterozygosity for 50 generations is 238 (got {n})", n == 238))
    checks.append(("N = 238 passes (0.9002) and N = 237 fails (0.8998)",
                   L.expected_heterozygosity(1, 238, 50) >= 0.9 > L.expected_heterozygosity(1, 237, 50)))
    pa = L.simulate_paths(238, 0.5, 50, 5000, seed=2)
    ratio = float(L.heterozygosity(pa[-1]).mean() / 0.5)
    checks.append((f"simulation at N = 238 keeps about 90% of H (got {ratio:.3f})", abs(ratio - 0.9) < 0.02))
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
