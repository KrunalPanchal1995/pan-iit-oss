# Project form (Hello FOSS)

**Project name:** openkymo

**Short description:** Learn to measure speed from video with kymographs: stripes, slopes, units and aliasing, in 3 sessions.

**Full description:** openkymo is a beginner-friendly learning repo about one of the most useful tricks in video measurement: take the same line of pixels from every frame and stack the lines into a new image. A moving object becomes a slanted stripe, and the slope of the stripe is its speed. In three short sessions you go from building a kymograph by hand and reading the slope of a single stripe, to converting pixels per frame into metres per second with image gradients (the structure tensor) and to choosing a frame rate that avoids aliasing, and finally to testing two estimators on synthetic kymographs with a known speed, measuring how noise and large shifts per frame break them. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment), and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next, such as separating moving from static stripes, stripes in both directions and unwrapping aliased speeds.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openkymo
