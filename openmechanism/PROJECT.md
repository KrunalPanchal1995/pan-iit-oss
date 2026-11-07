# Project form (Hello FOSS)

**Project name:** openmechanism

**Short description:** Learn how kinetic mechanisms are fitted to experiments: rate laws, Arrhenius, sensitivity, least squares and uncertainty, in 3 sessions.

**Full description:** openmechanism is a beginner-friendly learning repo about the central task of chemical kinetics modelling: choosing the rate constants of a reaction mechanism so that its simulations agree with experiments, and saying how well the data pinned them down. In three short sessions you go from a two-step reaction network written as equations, to the Arrhenius temperature dependence, the 1000/T plot and sensitivity coefficients (which rate does an experiment feel?), to a full calibration of a four-reaction toy mechanism against noisy synthetic ignition-delay data, with an implicit stiff-ODE solver you write, a least-squares fit, parameter uncertainty from the Jacobian, and a check that the fit recovers a known truth. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment) and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. All numbers are invented toys for teaching; nothing here is a validated combustion mechanism. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next, such as optimal experiment design, fitting activation energies and propagating uncertainty into predictions.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openmechanism
