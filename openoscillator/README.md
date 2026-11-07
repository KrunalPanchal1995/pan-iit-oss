# openoscillator

[![Checks](https://github.com/KrunalPanchal1995/pan-iit-oss/actions/workflows/tests.yml/badge.svg)](https://github.com/KrunalPanchal1995/pan-iit-oss/actions/workflows/tests.yml) ![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square) ![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square) [![Open in Colab](https://img.shields.io/badge/Colab-session%201-F9AB00?style=flat-square&logo=googlecolab&logoColor=white)](https://colab.research.google.com/github/KrunalPanchal1995/pan-iit-oss/blob/main/openoscillator/sessions/session-01/lesson.ipynb) [![Live apps](https://img.shields.io/badge/live-apps-1f6feb?style=flat-square)](https://krunalpanchal1995.github.io/pan-iit-oss/openoscillator/)

**Tune a pendulum or a spring to the exact period you want, in three sessions.**

openoscillator teaches oscillations from a swinging pendulum to resonance, using only Python and a browser, and ends with tuning a spring-mass system to a target frequency.

- **Start from a swing.** Session 1 needs only a square root and a stopwatch idea; the period formulas are explained from scratch.
- **See it move.** Every session ships a slider app that runs in the browser, with labelled graphs, energy bars and a resonance curve.
- **Know you got it right.** Each session ends with a checkpoint that prints PASS or FAIL against hand calculations and exact results.
- **Build the missing half.** The repo stops at Session 3 on purpose; the roadmap shows the path to the Target.

[Target](#the-target) · [Who is this for](#who-is-this-for) · [Quick start](#quick-start) · [Sessions](#sessions) · [Roadmap](#roadmap) · [Contribute](#contribute) · [Explainer PDF](docs/explainer.pdf)

> **This repo is incomplete on purpose.** Sessions 1 to 3 are here and fully working. The finished Target below is a preview of what the community can build next. We show you the path, not the code. Sessions 4 and up are yours.

## The Target

A pendulum released from 100 degrees swings with damping while three panels follow it: its phase portrait spirals inwards, energy bars show potential and kinetic energy trading places while the energy lost to damping grows, and a resonance curve shows how sharply the same oscillator would respond to a periodic push, with its quality factor Q. A faint copy swinging by the small-angle formula drifts out of step with the real pendulum. Your goal over the coming sessions: build these panels yourself and then tune the oscillator to a target period.

![Target: a damped pendulum with phase portrait, energy bars and the resonance curve](promo/media/target.gif)

*Target: a damped pendulum with phase portrait, energy bars and the resonance curve*

![Target still: the pendulum a little way into its decay](promo/media/target_still.png)

*Target still: the pendulum a little way into its decay*

![Resonance curves for four damping values, and how the period grows with amplitude](promo/media/resonance_family.png)

*Resonance curves for four damping values, and how the period grows with amplitude*

Try it live:

- [Math Visual Studio: rigid-body dynamics (Atlas S46)](https://krunalpanchal1995.github.io/studio/#atlas?ch=S46&ex=1)
- [Math Visual Studio: simple harmonic motion (Atlas S47)](https://krunalpanchal1995.github.io/studio/#atlas?ch=S47&ex=1)

How the Target was made is shown only as a path in [promo/roadmap.md](promo/roadmap.md).

## Who is this for
**secondary school to diploma / undergraduate (levels 3-5).** Topic area: Physics and the Science of Motion.

Prerequisites:

- School algebra, square roots, and sine and cosine of an angle.
- Python 3.10 or newer; if `python --version` works, you are ready. PRIMER.md explains the rest.
- No prior GitHub, calculus or physics-simulation experience is needed; Session 3 explains the numerical method it uses.

New to Python? Read [PRIMER.md](PRIMER.md) first (10 minutes).

## Quick start

No installation knowledge needed. You need [Git](https://git-scm.com/downloads) and [Python 3.10+](https://www.python.org/downloads/) (Windows: tick "Add Python to PATH"). On Mac and Linux type `python3` wherever this page says `python`.

```bash
git clone https://github.com/KrunalPanchal1995/pan-iit-oss.git
cd pan-iit-oss/openoscillator
python start.py 1
```

`start.py` creates a private environment, installs what is needed and runs Session 1 with its checkpoint. Next: `python start.py 2`, `python start.py 3`, or `python start.py test` to check everything. Only a checkpoint: `python start.py check 1`.

<!-- friendly-help -->
<details>
<summary><b>Not working? Common fixes (no Git, "python not found", no internet)</b></summary>

- **No Git?** You do not need it. On the main page of this collection click the green **Code** button, then **Download ZIP**, unzip it, open a terminal inside the folder `pan-iit-oss-main/openoscillator` and run `python start.py 1`. The ZIP holds every project, so it is large; the live apps need no download at all.
- **"python is not recognized" or "command not found".** On Windows try `py start.py 1`. On Mac and Linux try `python3 start.py 1`. If neither works, install Python from [python.org](https://www.python.org/downloads/) and tick "Add Python to PATH".
- **Needs internet once.** The first run downloads NumPy and Matplotlib into a private folder (`.venv`); after that it works offline.
- **Rather not install anything?** Open the [live apps](https://krunalpanchal1995.github.io/pan-iit-oss/openoscillator/) in your browser, or use the Colab badge at the top of this page.
- **Still stuck?** [Open an issue](https://github.com/KrunalPanchal1995/pan-iit-oss/issues/new?title=%5Bopenoscillator%5D%20) with your operating system and the message you see. Questions from beginners are welcome.

</details>

Four lines turn the idea of Session 1 into a result (they work as they are): Save it as `try.py` and run it with `python start.py run try.py` (this uses the private environment, where NumPy is installed):

```python
import numpy as np
L = 0.994                                      # pendulum length in metres
T = 2 * np.pi * np.sqrt(L / 9.81)              # period of a small swing
print(f"{T:.3f} s")                            # -> 2.000 s : the 'seconds pendulum'
```

Every session also opens in your browser with sliders (no install): [live apps](https://krunalpanchal1995.github.io/pan-iit-oss/openoscillator/). Or use the Colab badge above for the notebook.

## Sessions

| # | Session | Model level | Time | Live app |
|---|---|---|---|---|
| 1 | [Things that swing: period, amplitude and frequency](sessions/session-01/README.md) | Level 1: conceptual interactive model | 60 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/openoscillator/session-01/) |
| 2 | [Simple harmonic motion, energy and damping](sessions/session-02/README.md) | Level 2: mathematical engineering model | 75 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/openoscillator/session-02/) |
| 3 | [The real pendulum: RK4, validation and resonance](sessions/session-03/README.md) | Level 3: simulation and validation | 90 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/openoscillator/session-03/) |

Each session follows the same six steps: A real-world problem, B concept and theory, C visual explanation, D interactive simulation, E worked example and experiment, F assessment and design challenge. Each ends with `checkpoint.py`, which prints `PASS` or `FAIL` against reference numbers. Session 3 also contains the real-world mini-project: **Tune a spring so a phone sensor bounces at 2 Hz**.

## Architecture

```mermaid
flowchart LR
  S1[Session 1<br/>Things that swing: period, amplitude and frequency]
  S2[Session 2<br/>Simple harmonic motion, energy and damping]
  S3[Session 3<br/>The real pendulum: RK4, validation and resonance]
  R[Roadmap S4+<br/>YOU build this]
  T((Target))
  S1 --> S2 --> S3 --> R --> T
```

| Folder or file | What is inside |
|---|---|
| `sessions/` | three sessions: README (A-F), `lesson.py`, notebook, live app, exercises, activity sheet, checkpoint |
| `promo/` | the Target: media, live links, and the roadmap (path only) |
| `docs/` | `explainer.tex` and the built `explainer.pdf` |
| `tests/` | runs every lesson and checkpoint headless |
| `start.py` | one command to set up and run anything |
| `QUALITY.md`, `RUBRIC.md` | the quality checklist and the scoring rubric |
| `.github/` | CI, PDF build, Pages deploy, issue and PR templates |

## Roadmap

| Milestone | What you will build | Difficulty |
|---|---|---|
| Session 4: Chaos in the driven pendulum | A driven version of the RK4 pendulum with phase portrait and a pair of nearby starting angles. | advanced |
| Session 5: Fit a phone recording | A fitting function for a damped cosine and a synthetic 'accelerometer recording' to test it. | intermediate |
| Session 6: Coupled pendulums and beats | Two identical pendulums joined by a weak spring, simulated with RK4. | intermediate |
| Session 7: Pumping a swing: parametric resonance | A small-angle pendulum whose length is modulated in time. | advanced |
| Session 8: Hardening spring: the resonance curve bends | A driven oscillator with a cubic spring term, swept up and then down in frequency. | advanced |

Full detail with a checkpoint per milestone: [promo/roadmap.md](promo/roadmap.md).

## Contribute
New to GitHub? Read [CONTRIBUTING.md](CONTRIBUTING.md); it starts from zero. Pick an issue labelled `good first issue`. Translations into Hindi, Telugu, Tamil and Malayalam are welcome.

<details>
<summary>Development</summary>

```bash
python start.py test        # runs every lesson and checkpoint
```
Lessons use `# %%` cell markers so they open as notebooks in VS Code. See [QUALITY.md](QUALITY.md) for the standard every session meets.
</details>

## License
MIT. See [LICENSE](LICENSE). Media in `promo/media` is (c) Krunal Panchal, CC BY 4.0.

## Acknowledgments
Part of the [PAN IIT OSS](https://hellofoss.tech-iitb.org/projects) open-source teaching collection, modelled on the structure of [openspline](https://github.com/openspline/openspline). Built on ideas from the Math Visual Studio at https://krunalpanchal1995.github.io/studio/.
