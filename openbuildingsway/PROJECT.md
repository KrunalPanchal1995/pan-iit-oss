# Project form (Hello FOSS)

**Project name:** openbuildingsway

**Short description:** Learn why buildings sway, resonate and fail: spring-mass models, mode shapes and drift, from scratch in 4 sessions.

**Full description:** openbuildingsway is a beginner-friendly learning repo about how a building moves when the ground shakes. In four short sessions you go from a building as one mass on a spring (period, stiffness and the idea of resonance), to a single storey shaken at its base (the amplification factor, damping and a stiffness design problem), to an N-storey shear building with a mass matrix and a stiffness matrix. There you solve the eigenproblem for periods and mode shapes, check it against an exact formula, shake the frame with a synthetic ground record by two independent methods (modal superposition and Newmark-beta integration), check energy, read off drift and base shear, and see how one weak storey ruins everything. Session 4 skips the time history: it builds the response spectrum of the record and estimates the base shear from the modes (square root of the sum of squares), then measures when that shortcut can be trusted. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment), and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The models are simplified and educational: they are never a substitute for seismic design by qualified engineers. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openbuildingsway
