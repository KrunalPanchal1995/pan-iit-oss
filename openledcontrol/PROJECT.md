# Project form (Hello FOSS)

**Project name:** openledcontrol

**Short description:** Learn how a sensor, a transistor and an LED become an automatic light: divider, switch, hysteresis and logic, in 3 sessions.

**Full description:** openledcontrol is a beginner-friendly learning repo about a small, everyday machine: a light that switches itself on when it gets dark. In three short sessions you go from the idea (a light sensor, a decision and a switch) to the numbers (a voltage divider with a light dependent resistor, an LED current-limiting resistor, a transistor base resistor sized for saturation, and a design problem for a night light with a chosen threshold), and then to a simulation of the whole controller over a cloudy synthetic day. There you count the on-off chatter of a single-threshold comparator, cure it with a Schmitt trigger (two thresholds), check the thresholds against hand calculations, study how part tolerances and the supply voltage move the trip point (Monte Carlo), and build a two-condition alarm from a tiny gate simulator and test its truth table on every input. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment) and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. All circuits are low-voltage educational models (5 V, milliamps); they are not designs for mains lighting. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openledcontrol
