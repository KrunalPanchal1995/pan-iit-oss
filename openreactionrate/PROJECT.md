# Project form (Hello FOSS)

**Project name:** openreactionrate

**Short description:** Learn reaction rates, rate laws, catalysts and reaction networks as ODEs, from scratch in 3 sessions.

**Full description:** openreactionrate is a beginner-friendly learning repo about how fast chemical reactions go. In three short sessions you go from the concentration-versus-time curve of A -> B, through rate laws, half-life, the Arrhenius form and the way a catalyst lowers the activation energy, to whole reaction networks written as dc/dt = S r(c) with a stoichiometry matrix. You write your own RK4 solver, validate it against exact first-order solutions and mass conservation, compare the Michaelis-Menten (quasi-steady-state) approximation with the full enzyme-like cycle, find the rate-determining step in a chain, and meet stiffness, where an explicit solver with too large a step blows up. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment), and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next, such as temperature-dependent networks, heat release and oscillating reactions. The models are simplified teaching models, not tools for designing real chemical processes.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openreactionrate
