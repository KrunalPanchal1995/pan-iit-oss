# Project form (Hello FOSS)

**Project name:** openflame

**Short description:** Measure flame height and flicker frequency from video: thresholds, FFT, aliasing and error bars, in 3 sessions.

**Full description:** openflame is a beginner-friendly learning repo about measuring a flickering flame from ordinary video. In three short sessions you go from a flame video as a stack of pictures and a brightness threshold that finds the flame, to the flicker frequency from counting cycles and from the Fourier transform (with the sampling rate, the Nyquist limit and the Heskestad flame-height and puffing-frequency correlations), to a complete test on a synthetic noisy video whose height and flicker are known: automatic sub-pixel height extraction, a frequency with an error bar checked against repeated experiments, aliasing when the frame rate is too low, and sensitivity to the threshold. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment) and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next, such as glare correction, resolving aliasing with two cameras, kymographs and onset detection. It is general education about image measurement; it gives no guidance on starting fires or on fire safety design.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openflame
