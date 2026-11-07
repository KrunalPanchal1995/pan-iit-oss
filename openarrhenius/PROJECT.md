# Project form (Hello FOSS)

**Project name:** openarrhenius

**Short description:** Fit k(T) with the Arrhenius law and report Ea and A with uncertainty bands, from scratch in 4 sessions.

**Full description:** openarrhenius is a beginner-friendly learning repo about one everyday job in chemistry and engineering: turning a handful of measured rate constants into a law k(T) that you can use, and saying how far you can trust it. In four short sessions you go from the idea that reactions speed up steeply with temperature and that the right axes (ln k against 1000/T) make the data a straight line, to a full least-squares fit with units, the modified Arrhenius form and the design of an experiment, to the covariance of the fitted parameters, confidence bands that flare outside the data, Monte Carlo prediction at a temperature nobody measured, validation against synthetic data of known truth, and, in Session 4, a fit of two parallel channels that bend the plot, with a band at 2000 K, a model-comparison check and the finding that the data must reach well past the crossover temperature. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment) and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next, such as optimal experiment design and bootstrap intervals.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openarrhenius
