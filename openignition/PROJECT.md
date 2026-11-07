# Project form (Hello FOSS)

**Project name:** openignition

**Short description:** Learn why mixtures ignite after a delay and how stiff solvers predict it: Arrhenius runaway, ln(delay) laws and implicit integrators, from scratch in 3 sessions.

**Full description:** openignition is a beginner-friendly learning repo about ignition delay, the waiting time before a fuel mixture suddenly burns. In three short sessions you go from a closed insulated box where heat release feeds back on the reaction rate (thermal runaway), to a one-step Arrhenius model whose delay follows a straight line of ln(delay) against 1000/T0 that you can invert for design, to a stiffness study in which you write your own explicit RK4 and implicit trapezoid solvers with Newton iteration, validate them against an exact quadrature and the Semenov criterion, and measure sensitivities, a pressure law and a failure case. Everything is a one-step toy, not hydrogen chemistry: real hydrogen-oxygen ignition is a chain-branching network with explosion limits, and the repo says so in every session. Each session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment), and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next, such as chain branching, variable heat capacity and hot-spot ignition.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openignition
