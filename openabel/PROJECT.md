# Project form (Hello FOSS)

**Project name:** openabel

**Short description:** Learn how one side-view photo reveals the inside of a flame: line integrals, the Abel transform, inversion and noise, in 5 sessions.

**Full description:** openabel is a beginner-friendly learning repo about a clever trick used in combustion labs and plasma physics: if a glowing object is round about an axis, one photo from the side is enough to recover its 3D glow. In five short sessions you go from adding up light along a line of sight (a glowing ball), to the forward Abel transform of a radial profile with a design question about how many pixels you need, to the inverse by onion peeling and by a smoothed (regularised) method, tested against the exact pair Gaussian to Gaussian, with a measured look at noise amplification and the bias you pay for smoothing. Session 4 then chooses the smoothing from the photo alone, with three truth-free rules (the discrepancy principle, unbiased predictive risk and generalised cross-validation) checked over 20 noise draws. Session 5 finds the flame's symmetry axis from the photo with two finders (the centroid and mirror matching) and inverts with both halves. Mini-projects recover the inside of a candle-like flame from a synthetic photo, choose its smoothing without peeking, and find its axis. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment) and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next, such as using neighbouring rows, keeping the hollow base hollow, and rendering the result in 3D.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openabel
