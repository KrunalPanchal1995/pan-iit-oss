# opencentripetal

[![Checks](https://github.com/KrunalPanchal1995/pan-iit-oss/actions/workflows/tests.yml/badge.svg)](https://github.com/KrunalPanchal1995/pan-iit-oss/actions/workflows/tests.yml) ![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square) ![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square) [![Open in Colab](https://img.shields.io/badge/Colab-session%201-F9AB00?style=flat-square&logo=googlecolab&logoColor=white)](https://colab.research.google.com/github/KrunalPanchal1995/pan-iit-oss/blob/main/opencentripetal/sessions/session-01/lesson.ipynb) [![Live apps](https://img.shields.io/badge/live-apps-1f6feb?style=flat-square)](https://krunalpanchal1995.github.io/pan-iit-oss/opencentripetal/)

**Design a banked curve that grips at speed, in four sessions.**

opencentripetal teaches circular motion and centripetal force through cars on curves: friction, banking and a friction-circle simulation, using only Python and a browser.

- **Start from zero.** Session 1 needs only school arithmetic: one formula, a = v^2 / r.
- **See it move.** Every session ships a slider app that runs in the browser, with labelled graphs.
- **Know you got it right.** The simulation is validated against the analytic limits, and each session ends with a checkpoint that prints PASS or FAIL.
- **Build the missing half.** The repo stops at Session 4 on purpose; the roadmap shows the path to the Target.

[Target](#the-target) · [Who is this for](#who-is-this-for) · [Quick start](#quick-start) · [Sessions](#sessions) · [Roadmap](#roadmap) · [Contribute](#contribute) · [Explainer PDF](docs/explainer.pdf)

> **This repo is incomplete on purpose.** Sessions 1 to 4 are here and fully working. The finished Target below is a preview of what the community can build next. We show you the path, not the code. Sessions 5 and up are yours.

## The Target

A top-down animation of a curve with a straight, a smooth transition and a banked arc. A green car enters at 85 percent of the grip limit and holds the lane; a red car enters at 120 percent and slides wide, with the friction circle showing its demand leaving the circle at the same moment. A map on the right shows the safe speed for every combination of bank angle and road friction. Your goal over the coming sessions: build this yourself, then add transition spirals, weight transfer and rollover.

![Target: a safe car and a car entering too fast, with the friction circle and the safe-speed map](promo/media/target.gif)

*Target: a safe car and a car entering too fast, with the friction circle and the safe-speed map*

![Target, one frame: the red car has run wide and its demand is outside the friction circle](promo/media/target_still.png)

*Target, one frame: the red car has run wide and its demand is outside the friction circle*

![Safe speed over bank angle and road friction for a curve of radius 60 m](promo/media/speed_map.png)

*Safe speed over bank angle and road friction for a curve of radius 60 m*

Try it live:

- [Math Visual Studio: Newton's laws of motion (Atlas S36)](https://krunalpanchal1995.github.io/studio/#atlas?ch=S36&ex=1)
- [Math Visual Studio: free-body diagrams (Atlas S37)](https://krunalpanchal1995.github.io/studio/#atlas?ch=S37&ex=1)

How the Target was made is shown only as a path in [promo/roadmap.md](promo/roadmap.md).

## Who is this for
**secondary school to diploma / undergraduate (levels 3-5).** Topic area: Physics and the Science of Motion.

Prerequisites:

- Multiplication, division and square roots; the idea of speed in m/s.
- Sine, cosine and tangent of an angle for Session 2 (explained where used).
- Python 3.10 or newer; if `python --version` works, you are ready. PRIMER.md explains the rest.
- No prior GitHub or physics-simulation experience is needed.

New to Python? Read [PRIMER.md](PRIMER.md) first (10 minutes).

## Quick start

No installation knowledge needed. You need [Git](https://git-scm.com/downloads) and [Python 3.10+](https://www.python.org/downloads/) (Windows: tick "Add Python to PATH"). On Mac and Linux type `python3` wherever this page says `python`.

```bash
git clone https://github.com/KrunalPanchal1995/pan-iit-oss.git
cd pan-iit-oss/opencentripetal
python start.py 1
```

`start.py` creates a private environment, installs what is needed and runs Session 1 with its checkpoint. Next: `python start.py 2`, `python start.py 3`, or `python start.py test` to check everything. Only a checkpoint: `python start.py check 1`.

<!-- friendly-help -->
<details>
<summary><b>Not working? Common fixes (no Git, "python not found", no internet)</b></summary>

- **No Git?** You do not need it. On the main page of this collection click the green **Code** button, then **Download ZIP**, unzip it, open a terminal inside the folder `pan-iit-oss-main/opencentripetal` and run `python start.py 1`. The ZIP holds every project, so it is large; the live apps need no download at all.
- **"python is not recognized" or "command not found".** On Windows try `py start.py 1`. On Mac and Linux try `python3 start.py 1`. If neither works, install Python from [python.org](https://www.python.org/downloads/) and tick "Add Python to PATH".
- **Needs internet once.** The first run downloads NumPy and Matplotlib into a private folder (`.venv`); after that it works offline.
- **Rather not install anything?** Open the [live apps](https://krunalpanchal1995.github.io/pan-iit-oss/opencentripetal/) in your browser, or use the Colab badge at the top of this page.
- **Still stuck?** [Open an issue](https://github.com/KrunalPanchal1995/pan-iit-oss/issues/new?title=%5Bopencentripetal%5D%20) with your operating system and the message you see. Questions from beginners are welcome.

</details>

Five lines turn the idea of Session 2 into a result (they work as they are): Save it as `try.py` and run it with `python start.py run try.py` (this uses the private environment, where NumPy is installed):

```python
import numpy as np
g, r = 9.81, 100.0                      # gravity (m/s^2), curve radius (m)
v = 80 / 3.6                             # 80 km/h in m/s
print(round(np.degrees(np.arctan(v**2 / (g * r))), 1))   # -> 26.7  ideal bank angle (degrees)
print(round(3.6 * np.sqrt(0.4 * g * r), 1))              # -> 71.3  wet flat-road limit (km/h)
```

Every session also opens in your browser with sliders (no install): [live apps](https://krunalpanchal1995.github.io/pan-iit-oss/opencentripetal/). Or use the Colab badge above for the notebook.

## Sessions

| # | Session | Model level | Time | Live app |
|---|---|---|---|---|
| 1 | [Going round a bend needs an inward push](sessions/session-01/README.md) | Level 1: conceptual interactive model | 60 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/opencentripetal/session-01/) |
| 2 | [Friction and banking supply the inward force](sessions/session-02/README.md) | Level 2: mathematical engineering model | 75 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/opencentripetal/session-02/) |
| 3 | [A simulated car on a curve, checked against the formulas](sessions/session-03/README.md) | Level 3: simulation and validation | 90 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/opencentripetal/session-03/) |
| 4 | [A transition spiral into the curve](sessions/session-04/README.md) | Level 3: simulation and validation | 90 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/opencentripetal/session-04/) |

Each session follows the same six steps: A real-world problem, B concept and theory, C visual explanation, D interactive simulation, E worked example and experiment, F assessment and design challenge. Each ends with `checkpoint.py`, which prints `PASS` or `FAIL` against reference numbers. Session 3 also contains the real-world mini-project: **Set the speed limit sign for a curve**.

## Architecture

```mermaid
flowchart LR
  S1[Session 1<br/>Going round a bend needs an inward push]
  S2[Session 2<br/>Friction and banking supply the inward force]
  S3[Session 3<br/>A simulated car on a curve, checked against the formulas]
  S4[Session 4<br/>A transition spiral into the curve]
  R[Roadmap S5+<br/>YOU build this]
  T((Target))
  S1 --> S2 --> S3 --> S4 --> R --> T
```

| Folder or file | What is inside |
|---|---|
| `sessions/` | four sessions: README (A-F), `lesson.py`, notebook, live app, exercises, activity sheet, checkpoint |
| `promo/` | the Target: media, live links, and the roadmap (path only) |
| `docs/` | `explainer.tex` and the built `explainer.pdf` |
| `tests/` | runs every lesson and checkpoint headless |
| `start.py` | one command to set up and run anything |
| `QUALITY.md`, `RUBRIC.md` | the quality checklist and the scoring rubric |
| `.github/` | CI, PDF build, Pages deploy, issue and PR templates |

## Roadmap

| Milestone | What you will build | Difficulty |
|---|---|---|
| Session 5: Weight transfer between left and right wheels | A car with centre of gravity height, track width and four tyre loads. | intermediate |
| Session 6: Rollover before sliding | A rollover check added to the friction-circle limit. | advanced |
| Session 7: Plan the speed round a whole circuit | A speed planner for a stadium circuit of two 100 m straights and two half circles of radius 30 m. | advanced |
| Session 8: Measure mu and compare with a turntable | A short lab report with a measured mu, a predicted slip speed and a measured slip speed. | intermediate |

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
