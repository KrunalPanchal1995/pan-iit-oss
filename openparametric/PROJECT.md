# Project form (Hello FOSS)

**Project name:** openparametric

**Short description:** Learn how rules and equations generate engineered parts: a shaft size from torque, strength against stiffness, and a rule engine that draws a flange, in 3 sessions.

**Full description:** openparametric is a beginner-friendly learning repo about generating engineered parts from rules and equations. In three short sessions you go from one rule that turns a torque into the smallest safe shaft and then into a standard R10 size, to two competing rules, strength and stiffness, that decide the thickness of a cantilever bracket, with the governing rule switching at a critical length and the lightest material chosen by running the rules for each, to a small rule engine that stores the rules as text, finds the order in which they can be evaluated, refuses circular and unsafe rules, and generates a bolted flange as a drawing that is validated by measuring its area against the formula. The rules are textbook rules of thumb, so the numbers are illustrative, not a design code. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment) and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next, such as units, tables of standard sizes, conditional rules, an explanation of why a result came out as it did, and automatic search for the lightest design.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openparametric
