# Project form (Hello FOSS)

**Project name:** openpinn

**Short description:** Learn physics-informed neural networks: a hand-coded numpy network that solves u' = -u and the 1D heat equation, in 3 sessions.

**Full description:** openpinn is a beginner-friendly learning repo about physics-informed neural networks (PINNs): networks trained to satisfy a differential equation as well as data. In three short sessions you go from a flexible curve that can also be asked to obey a law, to a tiny tanh network with hand-coded backpropagation trained on the equation u' = -u, to a network u(x, t) that solves the 1D heat equation, with the second derivative computed by hand and checked against finite differences. You validate against the exact solution and against a classical finite-difference solver, measure what happens with too few collocation points or a badly weighted loss, see where a small network fails, and finally use the same machinery backwards to recover the diffusivity from noisy readings. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment), and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. Pure numpy: no deep-learning framework is needed. The repo is intentionally incomplete: a Target animation and a roadmap point to Fourier features, exact boundary conditions and 2D problems.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openpinn
