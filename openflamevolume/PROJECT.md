# Project form (Hello FOSS)

**Project name:** openflamevolume

**Short description:** Learn how photos from several cameras rebuild a 3D flame: stereo depth, image correlation and volume with an error bar, from scratch in 3 sessions.

**Full description:** openflamevolume is a beginner-friendly learning repo about reconstructing a three-dimensional flame from two-dimensional photos. In three short sessions you go from the pinhole camera and the idea that two cameras give a disparity that is a depth, to matching image windows by zero-mean normalised cross-correlation with a sub-pixel peak and a Monte Carlo study of bias and spread, to a multi-view reconstruction of a synthetic flame that you slice, add up to a volume and validate against the exact shape. You also see why too few views give a biased volume, and choose how many stereo pairs a lab burner needs. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment), and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The repo is intentionally incomplete: a Target figure and a roadmap show where the community can take it next (calibration, toed-in cameras, flicker, an error budget and tomography of a translucent flame). All models are simplified teaching models, not measurement procedures.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openflamevolume
