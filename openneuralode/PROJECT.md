# Project form (Hello FOSS)

**Project name:** openneuralode

**Short description:** Learn dynamics from data with neural ODEs: rules for change, solvers and training through the solver, from scratch in 3 sessions.

**Full description:** openneuralode is a beginner-friendly learning repo about learning the laws of motion from data. In three short sessions you go from the idea that a system changes according to a rule dx/dt = f(x), to solving that rule with Euler and RK4 and fitting it with least squares and a small neural network written in plain numpy, to a true Neural ODE trained through the solver with hand-coded backpropagation. Along the way you measure the order of the solvers, compare one-step training with rollout training, check the learned flow against a system with known eigenvalues, and meet three failure cases: stiffness, extrapolation and overfitting. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment), and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next, such as the adjoint method, limit cycles, stiff systems and partial observations.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openneuralode
