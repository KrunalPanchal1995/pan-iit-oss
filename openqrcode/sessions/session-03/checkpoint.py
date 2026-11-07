"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: P(block ok) at q = 0.05 is 0.6983 + 0.2573 = 0.9556, and 0.9556^10 = 0.635",
                   abs(0.95 ** 7 - 0.6983) < 1e-4 and abs(7 * 0.05 * 0.95 ** 6 - 0.2573) < 1e-4
                   and abs(L.block_ok_prob(0.05) - 0.9556) < 1e-4 and abs(L.hamming_theory(0.05) - 0.635) < 1e-3))
    mc = L.hamming_mc(0.05, 6000, 11)
    checks.append(("worked example: simulation at q = 0.05 agrees with 0.635 (within 0.03)", abs(mc - 0.635) < 0.03))
    g, _ = L.grid_success(0.05, 1500, 12)
    checks.append(("the full grid pipeline (build, damage, read) agrees with theory at q = 0.05 (within 0.04)", abs(g - 0.635) < 0.04))
    clean = L.make_grid("OPEN", 10)
    res = L.read_grid(clean, 10)
    checks.append(("a clean code reads back OPEN with the check byte correct", res["text"] == "OPEN" and res["check_ok"] and res["fixed"] == 0))
    checks.append(("grid has 12 x 12 squares and 96 data squares", clean.shape == (12, 12) and len(L.DATA_POS) == 96))
    words = L.encode_blocks(L.message_bits("OPEN"))
    checks.append(("interleaving and de-interleaving are inverse operations",
                   all(np.array_equal(L.deinterleave(L.interleave(words, g), g, 10), words) for g in (1, 2, 5, 10))))
    res = L.read_grid(L.burst_noise(clean, 20, 9), 10)
    checks.append(("a burst of 9 squares is repaired with interleave group 10", res["text"] == "OPEN" and res["check_ok"] and res["fixed"] == 9))
    checks.append(("without interleaving a burst of 2 squares can already fail", L.burst_survival(1, 2) < 1.0))
    checks.append(("guaranteed burst length equals the interleave group (1, 2, 5, 10)",
                   [L.guaranteed_burst(g) for g in (1, 2, 5, 10)] == [1, 2, 5, 10]))
    checks.append(("edge: no damage (q = 0) always succeeds, total damage (q = 1) never does",
                   L.hamming_theory(0.0) == 1.0 and L.hamming_theory(1.0) == 0.0 and L.grid_success(0.0, 20, 1)[0] == 1.0))
    bad = clean.copy()
    bad[0:3, 0:3] ^= 1
    checks.append(("edge: a destroyed finder pattern means the reader gives up", L.read_grid(bad, 10)["finder_ok"] is False))
    q = 0.03
    checks.append(("repetition code: 5 copies beat 3 copies, 3 beat none (theory)",
                   L.repetition_theory(q, 5) > L.repetition_theory(q, 3) > L.uncoded_theory(q)))
    checks.append(("repetition code corrects up to (n-1)/2 = 2 flips of 5, simulation matches theory",
                   abs(L.repetition_mc(0.05, 5, 4000, 3) - L.repetition_theory(0.05, 5)) < 0.03))
    checks.append(("failure case: at q = 0.15 fewer than 10 percent of codes are read", L.hamming_theory(0.15) < 0.10 and L.grid_success(0.15, 300, 2)[0] < 0.10))
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
