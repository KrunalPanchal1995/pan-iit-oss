# Roadmap: the path to the openupi Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Reconcile three ledgers at the end of the day

**You will learn:** Why real systems keep separate ledgers at the banks and the switch, and how an end-of-day comparison finds payments that one side saw and the other did not.

**You will build:** A version of the switch with three separate ledgers (payer bank, switch, payee bank), bank timeouts injected, and a reconciliation step that repairs mismatches.

**Checkpoint (not met by the shipped code):** With 5 percent of bank replies lost over 10000 seeded payments, reconciliation leaves zero unmatched payments and all invariants hold (the shipped switch has a single ledger and cannot even show a mismatch).

**Difficulty:** advanced

## Session 5: Catch the slow attack

**You will learn:** Per-customer baselines (rolling median and spread) and combining weak signals, instead of one fixed limit per rule.

**You will build:** A better scoring function than the three fixed rules, judged on the same seeded synthetic data.

**Checkpoint (not met by the shipped code):** At least 16 of the 20 slow attacks flagged at least once while the false positive rate stays at or below 5 percent (the shipped rules catch 1 of 20 at 2.8 percent; lowering the new-payee amount to 300 catches 12 of 20 but raises FPR to 12.6 percent).

**Difficulty:** advanced

## Session 6: Lockout that recovers

**You will learn:** Time-based lockout and rate limiting, and the trade-off between security and a locked-out owner.

**You will build:** A lockout that expires after 30 simulated minutes and a counter that is kept per account and per day.

**Checkpoint (not met by the shipped code):** The owner can pay again after 30 minutes, and an attacker guessing PINs at random gets at most 3 x 48 = 144 guesses a day, so at most a 1.44 percent chance of guessing a 4-digit PIN (the shipped lockout never expires, so an owner is locked out for good).

**Difficulty:** intermediate

## Session 7: Survive a crash: a write-ahead log

**You will learn:** Writing intent to a durable log before changing the ledger, and replaying the log after a restart.

**You will build:** A switch that appends each payment to a log file first and rebuilds all balances and its id memory by replaying it.

**Checkpoint (not met by the shipped code):** After a simulated crash injected at each of 1000 random points in a run of payments, the rebuilt balances equal the balances of an uncrashed run every time and no id is charged twice (the shipped in-memory switch forgets everything on a restart).

**Difficulty:** advanced

## Session 8: Two payments at once

**You will learn:** Race conditions: two requests from the same account at the same moment, and how a lock or a version number prevents an overdraft.

**You will build:** A threaded test harness and per-account locking in the switch.

**Checkpoint (not met by the shipped code):** 100 interleaved payments from one account with Rs 1000 and amounts of Rs 30 never overdraw it: the balance stays at or above 0 and exactly 33 payments succeed (the shipped switch was written for one request at a time and has no locking).

**Difficulty:** advanced

## The final step

Combine the milestones: a switch with three ledgers and reconciliation, crash recovery from a log, safe concurrent payments, and fraud scoring that catches slow attacks with few false alarms, shown as a message-flow animation like the Target. If your result looks like the Target animation, open a pull request and tell us how you did it.
