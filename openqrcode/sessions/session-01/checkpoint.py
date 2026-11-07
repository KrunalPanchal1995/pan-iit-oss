"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    bits = L.text_to_bits("A")
    checks.append(("'A' (65) is 01000001", "".join(map(str, bits)) == "01000001"))
    grid = L.bits_to_grid(L.text_to_bits("QR"), 8)
    checks.append(("two letters fill a 2 x 8 grid of squares", grid.shape == (2, 8) and int(grid.sum()) == 6))
    checks.append(("worked example: check digit of 400638133393 is 1 (weighted sum 89 + 1 = 90)",
                   L.weighted_sum("400638133393") == 89 and L.ean13_check_digit("400638133393") == 1))
    checks.append(("hand calculation: 590123412345 needs check digit 7", L.ean13_check_digit("590123412345") == 7))
    checks.append(("all three real-format examples are valid", all(L.ean13_is_valid(c) for c in L.EXAMPLES)))
    checks.append(("a wrong check digit is rejected", not L.ean13_is_valid("4006381333932")))
    checks.append(("edge: a check digit of 0 works (sum already ends in 0)",
                   L.ean13_check_digit("000000000000") == 0 and L.ean13_is_valid("0000000000000")))
    checks.append(("edge: wrong length or letters are rejected", not L.ean13_is_valid("40063813339") and not L.ean13_is_valid("40063813339x1")))
    checks.append(("every one-digit error is caught", all(L.single_error_detection(c) == 1.0 for c in L.EXAMPLES)))
    frac, missed = L.swap_detection_all_pairs()
    checks.append(("neighbour swaps: 80 of 90 pairs caught, the 10 missed differ by 5",
                   abs(frac - 80 / 90) < 1e-12 and all(abs(a - b) == 5 for a, b in missed)))
    undetected = "4006381333931".replace("40", "04")   # swap 4 and 0: differ by 4, caught
    checks.append(("swapping 4 and 0 is caught", not L.ean13_is_valid(undetected)))
    checks.append(("design: weights 7..2 modulo 11 catch every neighbour swap", L.mod11_swap_detection() == 1.0))
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
