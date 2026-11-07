# Project form (Hello FOSS)

**Project name:** openupi

**Short description:** Learn how digital payments move between banks, why retries must not double-charge, and where fraud checks sit: 3 sessions, a toy switch you can break.

**Full description:** openupi is a beginner-friendly learning repo about the machinery behind a digital payment. In three short sessions you go from the cast of a payment (payer app, payee app, two banks and a switch) and its message flow, to a double-entry ledger with atomic transactions and idempotent retries, to a small in-memory toy payment switch that you stress with lost replies, check against three invariants (money conserved, no negative balance, no double charge) and defend with simple fraud rules whose false positive and false negative rates you measure on seeded synthetic data. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment), and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. Everything is a teaching toy: there is no real networking, no real bank, no real UPI protocol and no real data, and the fraud material is about defence only. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openupi
