"""Checkpoint for Session 3. Prints PASS or FAIL."""
import hashlib
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # --- one-time pad
    m1, m2 = b"MEET AT NOON AT THE GATE", b"BRING THE MAP AND A LAMP"
    key = L.otp_key(len(m1))
    c1, c2 = L.otp_encrypt(m1, key), L.otp_encrypt(m2, key)
    checks.append(("one-time pad: decrypt(encrypt(m)) = m", L.otp_decrypt(c1, key) == m1))
    checks.append(("the key has the same length as the message", len(key) == len(m1)))
    cands = [b"ATTACK AT DAWN AT THE GATE"[:24], b"ALL IS WELL, STAY AT HOME."[:24], b"X" * 24]
    ok = all(L.xor_bytes(c1, L.key_that_explains(c1, p)) == p for p in cands)
    checks.append(("perfect secrecy: every same-length text has a key that explains the ciphertext", ok))
    checks.append(("failure case: reusing the pad gives c1 XOR c2 = m1 XOR m2 (the key cancels)",
                   L.reuse_leak(c1, c2) == L.xor_bytes(m1, m2)))
    checks.append(("failure case: guessing MEET at position 0 reveals BRIN of the other message",
                   L.crib_reveal(c1, c2, b"MEET", 0) == b"BRIN"))
    try:
        L.xor_bytes(b"ab", b"abc")
        raised = False
    except ValueError:
        raised = True
    checks.append(("edge: XOR of unequal lengths is refused", raised))

    # --- stream cipher
    seed = 40503
    sct = L.stream_encrypt(b"HDR: the plan is ready", seed)
    checks.append(("stream cipher round trip", L.stream_decrypt(sct, seed) == b"HDR: the plan is ready"))
    found, tries = L.brute_force_seed(sct, b"HDR:")
    checks.append(("a 16-bit seed is found by trying all 65536 values", found == [seed] and tries == 65536))
    import time
    t0 = time.perf_counter()
    L.brute_force_seed(sct, b"HDR:")
    checks.append(("...in well under 5 seconds", time.perf_counter() - t0 < 5.0))
    checks.append(("worked example: 2^40 = 1099511627776 keys", 2 ** 40 == 1099511627776))
    checks.append(("worked example: 2^40 tries at 10^6 per second take about 12.7 days",
                   abs(L.seconds_to_exhaust(40, 1e6) / 86400 - 12.73) < 0.01))

    # --- hashing
    checks.append(("SHA-256 of abc matches the standard test vector (starts ba7816bf)",
                   hashlib.sha256(b"abc").hexdigest().startswith("ba7816bf")))
    checks.append(("SHA-256 output has 256 bits", len(hashlib.sha256(b"abc").digest()) * 8 == 256))
    d = L.avalanche_samples(2000, 32, 0)
    checks.append(("avalanche: the mean number of changed bits is between 127 and 129 of 256", 127 < d.mean() < 129))
    checks.append(("avalanche: the mean for the lesson run is 128.2", abs(d.mean() - 128.2) < 0.05))
    checks.append(("avalanche: the spread (std) is near sqrt(256 x 0.25) = 8", 7.0 < d.std() < 9.0))
    checks.append(("avalanche: no sample changed fewer than 90 bits", d.min() > 90))
    checks.append(("bit_difference counts bits: 0b1010 vs 0b0110 differ in 2", L.bit_difference(0b1010, 0b0110) == 2))

    # --- passwords
    table = L.precomputed_table(L.DICTIONARY)
    un = L.store_unsalted(L.USERS)
    checks.append(("unsalted: one table cracks all 5 users", len(L.crack_with_table(un, table)) == 5))
    checks.append(("unsalted: equal passwords give equal hashes (alice and carol)", un["alice"] == un["carol"]))
    recs = L.store_salted(L.USERS)
    hashes = {u: h for u, (s, h) in recs.items()}
    checks.append(("salted: the same table cracks 0 users", len(L.crack_with_table(hashes, table)) == 0))
    checks.append(("salted: alice and carol (same password) get different hashes", hashes["alice"] != hashes["carol"]))
    cracked, work = L.crack_salted_by_search(recs, L.DICTIONARY)
    checks.append(("salted: the attacker must now hash 5 users x 8 words = 40 times (a table needed 8)",
                   work == 40 and len(table) == 8 and len(cracked) == 5))
    checks.append(("PBKDF2-HMAC-SHA256 matches a standard test vector",
                   hashlib.pbkdf2_hmac("sha256", b"password", b"salt", 1, 32).hex().startswith("120fb6cffcf8b32c")))
    checks.append(("a wrong password does not match", L.salted_hash("wrong", recs["alice"][0]) != recs["alice"][1]))

    # --- HMAC
    k = b"Jefe"
    tag = L.make_tag(k, b"what do ya want for nothing?")
    checks.append(("HMAC-SHA256 matches the RFC 4231 test vector (starts 5bdcc146)", tag.hex().startswith("5bdcc146bf60754e")))
    checks.append(("a correct tag verifies", L.check_tag(k, b"what do ya want for nothing?", tag)))
    checks.append(("a changed message fails", not L.check_tag(k, b"what do ya want for nothing!", tag)))
    checks.append(("a wrong key fails", not L.check_tag(b"Jeff", b"what do ya want for nothing?", tag)))

    # --- key size table
    rows = {b: (n, s) for b, n, s in L.key_size_table()}
    checks.append(("40 bits at 10^12 per second: 1.0995e12 keys, about 1.1 seconds",
                   abs(rows[40][0] - 1.0995e12) < 1e9 and abs(rows[40][1] - 1.0995) < 0.001))
    checks.append(("56 bits: 72058 seconds, about 20.0 hours", abs(rows[56][1] - 72057.6) < 0.1 and abs(rows[56][1] / 3600 - 20.0) < 0.05))
    checks.append(("80 bits: about 1.2089e12 seconds, about 38300 years",
                   abs(rows[80][1] / 1.2089e12 - 1) < 1e-3 and abs(L.years(rows[80][1]) - 38305) < 5))
    checks.append(("128 bits: about 3.40e26 seconds, about 1.08e19 years",
                   abs(rows[128][1] / 3.4028e26 - 1) < 1e-3 and abs(L.years(rows[128][1]) / 1.078e19 - 1) < 1e-3))
    checks.append(("41 bits at 10^6 per second take about 25.5 days", abs(L.seconds_to_exhaust(41, 1e6) / 86400 - 25.46) < 0.01))
    checks.append(("10^6 seconds is about 11.6 days; 2^40 / 10^6 is 1099512 seconds",
                   abs(1e6 / 86400 - 11.57) < 0.01 and round(L.seconds_to_exhaust(40, 1e6)) == 1099512))
    checks.append(("100 years is 3.156e9 seconds and needs log2(3.156e21) = 71.4 bits",
                   abs(100 * L.SECONDS_PER_YEAR - 3.156e9) < 1e6 and abs(math.log2(100 * L.SECONDS_PER_YEAR * 1e12) - 71.42) < 0.01))
    checks.append(("roadmap: 12 random lowercase letters carry 56.4 bits", abs(12 * math.log2(26) - 56.4) < 0.01))
    checks.append(("roadmap: toy RSA n = 3233, e = 17, d = 2753 maps 65 to 2790 and back",
                   pow(65, 17, 3233) == 2790 and pow(2790, 2753, 3233) == 65))
    checks.append(("each extra bit doubles the time", abs(L.seconds_to_exhaust(61, 1e12) / L.seconds_to_exhaust(60, 1e12) - 2) < 1e-12))
    checks.append(("design: at least 100 years at 10^12 per second needs 72 bits",
                   L.bits_needed(100 * L.SECONDS_PER_YEAR, 1e12) == 72 and
                   L.years(L.seconds_to_exhaust(72, 1e12)) >= 100 > L.years(L.seconds_to_exhaust(71, 1e12))))

    # --- mini-project
    ct = L.mini_ciphertext()
    checks.append(("mini-project: the challenge has 999 letters", len(ct) == 999))
    m, kk, plain = L.break_vigenere(ct)
    checks.append(("mini-project: key length 6 is found from the ciphertext", m == 6))
    checks.append(("mini-project: the key BEACON is recovered", kk == "BEACON"))
    checks.append(("mini-project: the plain text is recovered exactly",
                   plain == "".join(c for c in L.MINI_TEXT.upper() if c in L.ALPHABET)))
    ic_plain = L.ic(np.array(L.clean(L.MINI_TEXT)))
    ic_cipher = L.ic(np.array(L.clean(ct)))
    checks.append(("mini-project: IC drops from about 0.07 (plain) to under 0.05 (cipher)", 0.06 < ic_plain < 0.08 and ic_cipher < 0.05))
    checks.append(("edge: ic of fewer than two letters is 0", L.ic(np.array([3])) == 0.0))
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
