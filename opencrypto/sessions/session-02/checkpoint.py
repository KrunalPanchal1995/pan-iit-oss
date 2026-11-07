"""Checkpoint for Session 2. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # --- key space
    checks.append(("Caesar has 25 useful keys", L.keyspace_caesar() == 25))
    checks.append(("worked example: 26! = 403291461126605635584000000, about 4.03e26",
                   L.keyspace_substitution() == 403291461126605635584000000))
    checks.append(("worked example: 26! is about 88.4 bits", abs(L.key_bits(L.keyspace_substitution()) - 88.38) < 0.01))
    checks.append(("worked example: the IC of LETTER is 2/15 = 0.1333", abs(L.index_of_coincidence("LETTER") - 2 / 15) < 1e-12))
    smallest = next(m for m in range(1, 60) if L.keyspace_vigenere(m) > L.keyspace_substitution())
    checks.append(("a Vigenere key needs 19 letters before 26^m exceeds 26!", smallest == 19))
    checks.append(("26^3 = 17576 Vigenere keys of length 3", L.keyspace_vigenere(3) == 17576))
    checks.append(("the table gives E 12.7 percent", L.ENGLISH_PCT[4] == 12.7))
    r14 = np.random.default_rng(1)
    hits = 0
    for _ in range(10):
        k14 = "".join(r14.choice(list(L.ALPHABET), size=14))
        c14 = L.vigenere_encrypt(L.english_like_text(1200, r14), k14)
        m14 = L.guess_key_length(c14)
        hits += m14 is not None and L.recover_key(c14, m14) == k14
    checks.append(("limit: this lesson's search (lengths up to 12) recovers 0 of 10 keys of length 14", hits == 0))
    checks.append(("26^6 = 308915776 Vigenere keys of length 6", L.keyspace_vigenere(6) == 308915776))
    checks.append(("log10(26!) is 26.6 and log10(25) is 1.40",
                   abs(math.log10(L.keyspace_substitution()) - 26.606) < 0.001 and abs(math.log10(25) - 1.398) < 0.001))

    # --- English statistics
    checks.append(("English table adds up to about 100 percent", abs(L.ENGLISH_PCT.sum() - 100.0) < 0.2))
    checks.append(("E is the most common English letter in the table", L.ALPHABET[int(np.argmax(L.ENGLISH_PCT))] == "E"))
    plain = L.letters_only(L.SAMPLE)
    checks.append(("the sample has 1326 letters", len(plain) == 1326))
    checks.append(("E is also the most common letter of the sample", L.ALPHABET[int(np.argmax(L.letter_counts(plain)))] == "E"))
    ic = L.index_of_coincidence(plain)
    checks.append(("IC of English text is near 0.067 (sample: between 0.060 and 0.075)", 0.060 < ic < 0.075))
    checks.append(("sum of squared English probabilities is 0.0655", abs(float((L.ENGLISH ** 2).sum()) - 0.0655) < 0.0005))
    rnd = L.random_text(20000, np.random.default_rng(3))
    checks.append(("IC of random letters is near 0.038 (1/26 = 0.0385)", abs(L.index_of_coincidence(rnd) - 1 / 26) < 0.002))

    # --- substitution cipher
    key = L.random_substitution_key(7)
    checks.append(("the key is a permutation of the 26 letters", sorted(key) == list(L.ALPHABET)))
    ct = L.substitute(L.SAMPLE, key)
    checks.append(("decrypting with the true key returns the plain text",
                   L.apply_decryption_key(ct, L.true_decryption_key(key)) == plain and L.unsubstitute(ct, key) == plain))
    checks.append(("the cipher keeps the letter counts, only relabelled",
                   sorted(L.letter_counts(ct)) == sorted(L.letter_counts(plain))))
    guess = L.rank_match_key(ct)
    truth = L.true_decryption_key(key)
    dec = L.apply_decryption_key(ct, guess)
    checks.append(("rank matching gets 7 of the 26 key letters right", round(L.key_accuracy(guess, truth) * 26) == 7))
    checks.append(("...which gets 44 percent of the text letters right", abs(L.text_accuracy(dec, plain) - 0.44) < 0.01))
    checks.append(("rank matching beats a blind guess (identity key) by a wide margin",
                   L.text_accuracy(dec, plain) > L.text_accuracy(L.apply_decryption_key(ct, L.ALPHABET), plain) + 0.2))
    checks.append(("rank-match key is also a permutation", sorted(guess) == list(L.ALPHABET)))

    # --- Vigenere
    checks.append(("hand calculation: ATTACKATDAWN with key LEMON is LXFOPVEFRNHR",
                   L.vigenere_encrypt("ATTACKATDAWN", "LEMON") == "LXFOPVEFRNHR"))
    checks.append(("Vigenere decrypt undoes encrypt", L.vigenere_decrypt(L.vigenere_encrypt(L.SAMPLE, "ORCHID"), "ORCHID") == plain))
    checks.append(("a one-letter key is a Caesar shift", L.vigenere_encrypt("HELLO", "D") == "KHOOR"))
    vct = L.vigenere_encrypt(L.SAMPLE, "ORCHID")
    checks.append(("Vigenere flattens the letters: IC of the ciphertext is below 0.045",
                   L.index_of_coincidence(vct) < 0.045))
    checks.append(("columns at the true length 6 have IC above 0.065", L.ic_for_length(vct, 6) > 0.065))
    checks.append(("columns at a wrong length (5) have IC below 0.050", L.ic_for_length(vct, 5) < 0.050))
    checks.append(("key length 6 is guessed from the IC", L.guess_key_length(vct) == 6))
    checks.append(("the key ORCHID is recovered from the ciphertext alone", L.recover_key(vct, 6) == "ORCHID"))
    ics = {m: L.ic_for_length(vct, m) for m in range(1, 19)}
    checks.append(("IC by guessed length: 0.065 or more at 6, 12, 18; between 0.04 and 0.055 elsewhere",
                   all(v >= 0.065 for m, v in ics.items() if m % 6 == 0) and all(0.04 < v < 0.055 for m, v in ics.items() if m % 6)))
    checks.append(("hand calculation: HELLO with key AB is HFLMO", L.vigenere_encrypt("HELLO", "AB") == "HFLMO"))
    rng = np.random.default_rng(2)
    ok = True
    for m in (1, 3, 6):
        v = []
        for _ in range(40):
            k = "".join(rng.choice(list(L.ALPHABET), size=m))
            v.append(L.index_of_coincidence(L.vigenere_encrypt(L.english_like_text(3000, rng), k)))
        model = 1 / 26 + (float((L.ENGLISH ** 2).sum()) - 1 / 26) / m
        ok &= abs(float(np.mean(v)) - model) < 0.003
    checks.append(("whole-text IC follows 1/26 + (0.0655 - 1/26)/m for m = 1, 3, 6", ok))

    # --- design problem
    checks.append(("n = 300, key length 8 (37 letters per column): key recovered in at least 90 percent of runs",
                   L.success_rate(300, 8, trials=200) >= 0.90))
    checks.append(("n = 300, key length 20 (15 letters per column): key recovered in under 15 percent of runs",
                   L.success_rate(300, 20, trials=200) < 0.15))
    checks.append(("a column of 10 letters gives the right shift 65 to 80 percent of the time",
                   0.65 < L.success_rate(10, 1, trials=400, seed=5) < 0.80))
    checks.append(("a column of 25 letters gives the right shift at least 95 percent of the time",
                   L.success_rate(25, 1, trials=400, seed=5) >= 0.95))
    checks.append(("edge: IC of an empty or one-letter text is 0, not an error",
                   L.index_of_coincidence("") == 0.0 and L.index_of_coincidence("A") == 0.0))
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
