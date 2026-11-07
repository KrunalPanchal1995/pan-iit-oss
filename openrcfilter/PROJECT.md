# Project form (Hello FOSS)

**Project name:** openrcfilter

**Short description:** Learn RC filters, Bode plots and digital low-pass filters, then design a filter for a noisy sensor, in 3 sessions.

**Full description:** openrcfilter is a beginner-friendly learning repo about removing noise from a sensor signal. In three short sessions you go from a slow signal buried in jitter and an RC low-pass that smooths it, to the mathematics of the filter (time constant, cutoff frequency, gain, phase, decibels, a Bode plot, a design problem and the loading effect), to a digital implementation whose frequency response you measure with sine sweeps and an FFT, whose noise reduction you verify against a formula, and whose failure cases (aliasing, a cutoff above Nyquist) you provoke on purpose. Session 3 ends with a real mini-project: a temperature sensor with 50 Hz pickup. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment), and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next, such as notch filters, zero-phase filtering and decimation.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openrcfilter
