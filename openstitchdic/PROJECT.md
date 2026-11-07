# Project form (Hello FOSS)

**Project name:** openstitchdic

**Short description:** Merge two cameras with different angles, frame rates and aspect ratios into one uniform data set (homography, resampling, Makima), in 3 sessions.

**Full description:** openstitchdic is a beginner-friendly learning repo for a problem every stereo digital image correlation (DIC) set-up has: what if you do not adjust anything? The two cameras look from different angles, run at different frame rates (say 30 and 24 pictures per second) and have different picture shapes and sizes. In three short sessions you see why the cameras disagree, bring both pictures onto one pixel grid with a homography and bilinear resampling, bring both clocks onto one 120 fps timeline with Makima interpolation (modified Akima, derived and coded from scratch, compared with linear and cubic spline), and finally run a small subset-correlation pipeline on synthetic speckle pictures whose true motion is known, so you can measure what skipping each step costs. Drop your own pictures here: make a folder named data next to start.py and put view_a.png and view_b.png in it (optional points.txt: four lines xa ya xb yb); Session 3 then aligns your pair, and without them it draws its own speckle pictures. Only numpy and matplotlib are used. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment) and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openstitchdic
