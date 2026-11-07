# Project form (Hello FOSS)

**Project name:** openalias

**Short description:** Learn why a filmed wheel runs backwards, and recover the true speed: aliasing, Nyquist and FFT, in 5 sessions.

**Full description:** openalias is a beginner-friendly learning repo about aliasing: what happens when something that changes quickly is only looked at at fixed instants, as a camera does at 24 or 30 frames per second. In five short sessions you go from a spinning wheel that appears slow, frozen or backwards, to the alias formula and the Nyquist limit with a frame-rate design problem, to simulated signals and rendered marker clips whose FFT peak you check against the exact formula, and from which you recover the true frequency by combining two frame rates. Session 4 then recovers the true speed from noisy apparent speeds by choosing the best pair of ladder rungs, with an uncertainty, checked over 2000 trials against the theoretical limit. Session 5 adds a third clip: the range becomes the least common multiple of all the frame rates, a third rate that divides the lcm of the other two adds nothing, and the extra clip lowers the noise by sqrt(2/3). Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment), and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next, such as multi-blade fans and speeds that change over time.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openalias
