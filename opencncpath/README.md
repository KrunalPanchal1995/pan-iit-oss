# opencncpath

[![Checks](https://github.com/KrunalPanchal1995/pan-iit-oss/actions/workflows/tests.yml/badge.svg)](https://github.com/KrunalPanchal1995/pan-iit-oss/actions/workflows/tests.yml) ![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square) ![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square) [![Open in Colab](https://img.shields.io/badge/Colab-session%201-F9AB00?style=flat-square&logo=googlecolab&logoColor=white)](https://colab.research.google.com/github/KrunalPanchal1995/pan-iit-oss/blob/main/opencncpath/sessions/session-01/lesson.ipynb) [![Live apps](https://img.shields.io/badge/live-apps-1f6feb?style=flat-square)](https://krunalpanchal1995.github.io/pan-iit-oss/opencncpath/)

**Turn a drawing into a CNC toolpath, in five sessions.**

opencncpath teaches how a cutter path is built from an outline: offsets, G-code, arcs, stepover and a height-map check, using only Python and a browser.

- **Start from zero.** Session 1 needs only a ruler's worth of geometry: a path, a radius and a speed.
- **See it cut.** Every session ships a slider app that runs in the browser, with labelled graphs.
- **Know you got it right.** Each session ends with a checkpoint that prints PASS or FAIL against hand calculations and a simulation.
- **Build the missing half.** The repo stops at Session 5 on purpose; the roadmap shows the path to the Target.

[Target](#the-target) · [Who is this for](#who-is-this-for) · [Quick start](#quick-start) · [Sessions](#sessions) · [Roadmap](#roadmap) · [Contribute](#contribute) · [Explainer PDF](docs/explainer.pdf)

> **This repo is incomplete on purpose.** Sessions 1 to 5 are here and fully working. The finished Target below is a preview of what the community can build next. We show you the path, not the code. Sessions 6 and up are yours.

## The Target

A flat cutter clears a rectangular pocket that has two round bosses. Its tool-path rings bend round the bosses, the cutter carves a simulated height-map, and counters show the chips (removed volume), the machine clock and the percentage of floor left uncut. Beside it a trade-off curve shows how a bigger stepover saves time but leaves more material. Your goal over the coming sessions: build that planner and simulator yourself.

![Target: a cutter carves a pocket with two bosses while chips, time and the stepover trade-off are counted](promo/media/target.gif)

*Target: a cutter carves a pocket with two bosses while chips, time and the stepover trade-off are counted*

![Target, last frame: carved height-map, counters and the time versus uncut curves](promo/media/target_still.png)

*Target, last frame: carved height-map, counters and the time versus uncut curves*

![The same pocket with a small and a large stepover: more rings and time against more uncut floor](promo/media/stepover_rings.png)

*The same pocket with a small and a large stepover: more rings and time against more uncut floor*

Try it live:

- [Math Visual Studio: open the Studio](https://krunalpanchal1995.github.io/studio/)

How the Target was made is shown only as a path in [promo/roadmap.md](promo/roadmap.md).

## Who is this for
**diploma / undergraduate to advanced undergraduate (levels 5-6).** Topic area: Mechanical Engineering.

Prerequisites:

- Distance between two points and the area and perimeter of a rectangle and a circle (school geometry).
- Python 3.10 or newer; if `python --version` works, you are ready. PRIMER.md explains the rest.
- No prior GitHub, CAD or machining experience is needed. This repo teaches toolpath geometry only, not how to operate a machine.

New to Python? Read [PRIMER.md](PRIMER.md) first (10 minutes).

## Quick start

No installation knowledge needed. You need [Git](https://git-scm.com/downloads) and [Python 3.10+](https://www.python.org/downloads/) (Windows: tick "Add Python to PATH"). On Mac and Linux type `python3` wherever this page says `python`.

```bash
git clone https://github.com/KrunalPanchal1995/pan-iit-oss.git
cd pan-iit-oss/opencncpath
python start.py 1
```

`start.py` creates a private environment, installs what is needed and runs Session 1 with its checkpoint. Next: `python start.py 2`, `python start.py 3`, or `python start.py test` to check everything. Only a checkpoint: `python start.py check 1`.

<!-- friendly-help -->
<details>
<summary><b>Not working? Common fixes (no Git, "python not found", no internet)</b></summary>

- **No Git?** You do not need it. On the main page of this collection click the green **Code** button, then **Download ZIP**, unzip it, open a terminal inside the folder `pan-iit-oss-main/opencncpath` and run `python start.py 1`. The ZIP holds every project, so it is large; the live apps need no download at all.
- **"python is not recognized" or "command not found".** On Windows try `py start.py 1`. On Mac and Linux try `python3 start.py 1`. If neither works, install Python from [python.org](https://www.python.org/downloads/) and tick "Add Python to PATH".
- **Needs internet once.** The first run downloads NumPy and Matplotlib into a private folder (`.venv`); after that it works offline.
- **Rather not install anything?** Open the [live apps](https://krunalpanchal1995.github.io/pan-iit-oss/opencncpath/) in your browser, or use the Colab badge at the top of this page.
- **Still stuck?** [Open an issue](https://github.com/KrunalPanchal1995/pan-iit-oss/issues/new?title=%5Bopencncpath%5D%20) with your operating system and the message you see. Questions from beginners are welcome.

</details>

Five lines turn the idea of Session 2 into a result (they work as they are): Save it as `try.py` and run it with `python start.py run try.py` (this uses the private environment, where NumPy is installed):

```python
import numpy as np
w, h, d, F = 40.0, 30.0, 6.0, 300.0           # pocket 40 x 30 mm, 6 mm cutter, feed 300 mm/min
n = int(np.ceil((h - d) / 4.0)) + 1             # zigzag lines at most 4 mm apart
length = n * (w - d) + (h - d)                  # cutter-centre path per layer, mm
print(n, length, round(length / F * 60, 1))     # -> 7 262.0 52.4 (seconds per layer)
```

Every session also opens in your browser with sliders (no install): [live apps](https://krunalpanchal1995.github.io/pan-iit-oss/opencncpath/). Or use the Colab badge above for the notebook.

## Sessions

| # | Session | Model level | Time | Live app |
|---|---|---|---|---|
| 1 | [A cutter follows a path](sessions/session-01/README.md) | Level 1: conceptual interactive model | 60 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/opencncpath/session-01/) |
| 2 | [G-code, offsets and arcs](sessions/session-02/README.md) | Level 2: mathematical engineering model | 75 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/opencncpath/session-02/) |
| 3 | [Pocketing strategies and a simulation that checks them](sessions/session-03/README.md) | Level 3: simulation and validation | 90 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/opencncpath/session-03/) |
| 4 | [Offset any convex polygon](sessions/session-04/README.md) | Level 3: simulation and validation | 90 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/opencncpath/session-04/) |
| 5 | [A pocket with a boss, cut without lifting](sessions/session-05/README.md) | Level 3: simulation and validation | 90 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/opencncpath/session-05/) |

Each session follows the same six steps: A real-world problem, B concept and theory, C visual explanation, D interactive simulation, E worked example and experiment, F assessment and design challenge. Each ends with `checkpoint.py`, which prints `PASS` or `FAIL` against reference numbers. Session 3 also contains the real-world mini-project: **Generate G-code for a pocket with a boss and check it**; Session 4 adds **Offset any convex polygon and cut a hexagonal pocket**; Session 5 adds **Contour-parallel pocket with a boss**.

## Architecture

```mermaid
flowchart LR
  S1[Session 1<br/>A cutter follows a path]
  S2[Session 2<br/>G-code, offsets and arcs]
  S3[Session 3<br/>Pocketing strategies and a simulation that checks them]
  S4[Session 4<br/>Offset any convex polygon]
  S5[Session 5<br/>A pocket with a boss, cut without lifting]
  R[Roadmap S6+<br/>YOU build this]
  T((Target))
  S1 --> S2 --> S3 --> S4 --> S5 --> R --> T
```

| Folder or file | What is inside |
|---|---|
| `sessions/` | five sessions: README (A-F), `lesson.py`, notebook, live app, exercises, activity sheet, checkpoint |
| `promo/` | the Target: media, live links, and the roadmap (path only) |
| `docs/` | `explainer.tex` and the built `explainer.pdf` |
| `tests/` | runs every lesson and checkpoint headless |
| `start.py` | one command to set up and run anything |
| `QUALITY.md`, `RUBRIC.md` | the quality checklist and the scoring rubric |
| `.github/` | CI, PDF build, Pages deploy, issue and PR templates |

## Roadmap

| Milestone | What you will build | Difficulty |
|---|---|---|
| Session 6: Rest machining of the corners | A second pass with a 2 mm cutter that follows the corner leftover left by the 6 mm cutter. | advanced |
| Session 7: 3D ball-end finishing | Parallel finishing passes over a hemisphere of radius 15 mm with a ball cutter of radius 3 mm, simulated on a 3D height-map. | advanced |
| Session 8: Post-processor dialects | A writer that outputs arcs with I, J and with the R word, and a parser that reads both. | advanced |

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
