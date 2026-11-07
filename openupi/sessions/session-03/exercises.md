# Coding tasks: Session 3

1. **Easy.** Run `python start.py run session-03/lesson.py` and then change `p_rep` in `run_workload` to 0.4. How many ids are double-charged without a key, and does the idempotent switch stay clean?
2. **Stretch.** Add a fourth fraud rule to `FraudScreen` (for example, flag any payment above Rs 3000) and use `evaluate` to see how FPR and FNR change on the seeded data.
3. **Explain in your own words.** Explain why a double charge does not break the 'money conserved' invariant, and which invariant catches it.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
