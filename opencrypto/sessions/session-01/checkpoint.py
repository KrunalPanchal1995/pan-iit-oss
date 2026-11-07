"""Checkpoint for Session 1. Prints PASS or FAIL."""


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("hand calculation: HELLO with key 3 is KHOOR", L.caesar_encrypt("HELLO", 3) == "KHOOR"))
    checks.append(("wrap-around: Y shifted by 3 is B", L.caesar_encrypt("Y", 3) == "B"))
    ct = L.caesar_encrypt("SEE YOU AT NOON", 5)
    checks.append(("worked example: SEE YOU AT NOON with key 5 is XJJ DTZ FY STTS", ct == "XJJ DTZ FY STTS"))
    checks.append(("worked example: decrypting it with key 5 returns the note", L.caesar_decrypt(ct, 5) == "SEE YOU AT NOON"))
    ok = all(L.caesar_decrypt(L.caesar_encrypt(L.MESSAGE, k), k) == L.MESSAGE for k in range(-30, 60))
    checks.append(("decrypt undoes encrypt for every key from -30 to 59", ok))
    checks.append(("key 0 and key 26 change nothing (so only 25 useful keys)",
                   L.caesar_encrypt(L.MESSAGE, 0) == L.MESSAGE and L.caesar_encrypt(L.MESSAGE, 26) == L.MESSAGE))
    outs = {L.caesar_encrypt("A", k) for k in range(26)}
    checks.append(("26 keys give 26 different letters, 25 of them change the letter", len(outs) == 26))
    checks.append(("case and punctuation are kept", L.caesar_encrypt("Hello, World!", 3) == "Khoor, Zruog!"))
    checks.append(("all_shifts returns exactly 25 candidates", len(L.all_shifts("KHOOR")) == 25))
    checks.append(("one of the 25 candidates for KHOOR is HELLO", any(t == "HELLO" for _, t in L.all_shifts("KHOOR"))))
    ct3 = L.caesar_encrypt(L.MESSAGE, 3)
    checks.append(("brute force recovers key 3 automatically", L.best_shift(ct3) == 3))
    checks.append(("brute force recovers every key from 1 to 25",
                   all(L.best_shift(L.caesar_encrypt(L.MESSAGE, k)) == k for k in range(1, 26))))
    r = L.readability(L.MESSAGE)
    checks.append(("the note scores about 79 percent common letters", abs(r - 0.7917) < 0.001))
    sc = L.score_by_guess(ct3)
    wrong = max(s for g, s in enumerate(sc) if g != 3)
    checks.append(("right guess 79 percent beats the best wrong guess 67 percent",
                   abs(sc[3] - 0.7917) < 0.001 and abs(wrong - 0.6667) < 0.001))
    checks.append(("a flat alphabet scores 9/26 = 0.346 (35 percent)", abs(L.readability(L.ALPHABET) - 9 / 26) < 1e-12))
    checks.append(("hand calculation: GO with key 20 is AI (G=6, 6+20=26 wraps to 0; O=14, 34-26=8)", L.caesar_encrypt("GO", 20) == "AI"))
    checks.append(("key 13 is its own inverse: HELLO becomes URYYB and back", L.caesar_encrypt("HELLO", 13) == "URYYB" and L.caesar_encrypt("URYYB", 13) == "HELLO"))
    checks.append(("a string with no letters scores 0 (no division by zero)", L.readability("123 !?") == 0.0))
    checks.append(("trying all keys takes well under one second", L.time_to_try_all(ct3) < 1.0))
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
