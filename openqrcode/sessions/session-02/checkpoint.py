"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    c = L.encode([1, 0, 1, 1])
    checks.append(("worked example: data 1011 encodes to 1011010", "".join(map(str, c)) == "1011010"))
    r = c.copy()
    r[2] ^= 1
    checks.append(("worked example: flipping bit 3 gives syndrome 011 (column 3 of H), repaired to 1011",
                   "".join(map(str, L.syndrome(r))) == "011" and L.error_position(r) == 3
                   and "".join(map(str, L.decode(r)[0])) == "1011"))
    checks.append(("hand calculation: p1 = d1+d2+d4 = 0, p2 = d1+d3+d4 = 1, p3 = d2+d3+d4 = 0 for 1011",
                   (1 + 0 + 1) % 2 == c[4] and (1 + 1 + 1) % 2 == c[5] and (0 + 1 + 1) % 2 == c[6]))
    checks.append(("G has shape 4 x 7 and H has shape 3 x 7", L.G.shape == (4, 7) and L.H.shape == (3, 7)))
    checks.append(("H @ G^T = 0 (mod 2): every codeword has syndrome 000", not ((L.H @ L.G.T) % 2).any()))
    checks.append(("edge: a clean codeword needs no correction", L.error_position(c) == 0))
    ok = True
    for k in range(3, 7):          # errors on the parity bits are found too
        r = c.copy()
        r[k] ^= 1
        ok &= L.error_position(r) == k + 1 and np.array_equal(L.decode(r)[0], [1, 0, 1, 1])
    checks.append(("edge: a flipped parity bit is located and the data stay right", bool(ok)))
    checks.append(("all 16 data words x 7 positions = 112 single errors are repaired", L.single_error_success() == (112, 112)))
    checks.append(("the minimum distance is 3 (corrects 1, not 2)", L.min_distance() == 3))
    checks.append(("two flipped bits are never repaired (0 of 336)", L.double_error_success() == (0, 336)))
    checks.append(("design: parity bits needed for 1, 4, 11, 26, 64 data bits are 2, 3, 4, 5, 7",
                   [L.min_parity_bits(k) for k in (1, 4, 11, 26, 64)] == [2, 3, 4, 5, 7]))
    checks.append(("edge: k = 11 needs exactly r = 4 (2^4 = 11 + 4 + 1) and k = 12 needs 5",
                   L.min_parity_bits(11) == 4 and L.min_parity_bits(12) == 5))
    checks.append(("rate of Hamming(7,4) is 4/7 = 0.571", abs(L.code_rate(4, 3) - 4 / 7) < 1e-12))
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
