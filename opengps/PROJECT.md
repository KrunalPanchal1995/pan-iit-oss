# Project form (Hello FOSS)

**Project name:** opengps

**Short description:** Learn how GPS works: trilateration, pseudoranges, clock bias, DOP and the relativity correction, in 3 sessions.

**Full description:** opengps is a beginner-friendly learning repo about how GPS navigation works. In three short sessions you go from the idea that two circles meet at two points and a third circle picks one, to pseudoranges (distance = speed of light x travel time) solved with linear algebra and the size of timing errors (1 microsecond is about 300 m), to a Gauss-Newton solver that finds position and the receiver clock error together from noisy ranges. You measure dilution of precision, check the solver against a known true position, and compute the special and general relativity offsets of a satellite clock from their formulas. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment), and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. All satellites are toy positions for teaching, not real orbits. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next, such as real orbits, atmosphere delays, fault detection and weighted solutions.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/opengps
