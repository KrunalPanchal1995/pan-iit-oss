# openascent

[![Checks](https://github.com/KrunalPanchal1995/pan-iit-oss/actions/workflows/tests.yml/badge.svg)](https://github.com/KrunalPanchal1995/pan-iit-oss/actions/workflows/tests.yml) ![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square) ![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square) [![Open in Colab](https://img.shields.io/badge/Colab-session%201-F9AB00?style=flat-square&logo=googlecolab&logoColor=white)](https://colab.research.google.com/github/KrunalPanchal1995/pan-iit-oss/blob/main/openascent/sessions/session-01/lesson.ipynb) [![Live apps](https://img.shields.io/badge/live-apps-1f6feb?style=flat-square)](https://krunalpanchal1995.github.io/pan-iit-oss/openascent/)

**Fly a rocket launch trajectory to orbit with staging, in three sessions.**

openascent teaches how a rocket reaches orbit, from the rocket equation and staging, to the gravity and drag losses of a vertical climb, to a two-stage gravity-turn ascent into a 200 km orbit, using only Python and a browser.

- **Start from zero.** Session 1 needs only school arithmetic and the ln button on a calculator: mass ratio in, delta-v out.
- **See the flight.** Every session ships a slider app that runs in the browser, with labelled trajectories, speed curves and delta-v budgets.
- **Know you got it right.** Each session ends with a checkpoint that prints PASS or FAIL against hand calculations, exact formulas, energy conservation and a closed delta-v budget.
- **Build the missing half.** The repo stops at Session 3 on purpose; the roadmap shows the path to the Target.

[Target](#the-target) · [Who is this for](#who-is-this-for) · [Quick start](#quick-start) · [Sessions](#sessions) · [Roadmap](#roadmap) · [Contribute](#contribute) · [Explainer PDF](docs/explainer.pdf)

> **This repo is incomplete on purpose.** Sessions 1 to 3 are here and fully working. The finished Target below is a preview of what the community can build next. We show you the path, not the code. Sessions 4 and up are yours.

## The Target

A two-stage launcher lifts off from a rotating Earth, throttles through max Q, pitches over on a planned gravity turn, drops its first stage and flies an optimised upper-stage steering law into a 200 km orbit, all animated: the rocket and its trail drawn over a curved Earth, the first stage falling away after separation, and live panels of altitude, speed, dynamic pressure and the delta-v budget filling up as it flies. Your goal over the coming sessions: build that animated flight yourself, add Earth's rotation, altitude-dependent thrust and an optimised pitch program, and find how much more payload they buy. The figure below is the Session 3 flight you start from.

![Target starting point: the Session 3 two-stage ascent to a 200 km orbit, side view and whole-Earth view](promo/media/target.png)

*Target starting point: the Session 3 two-stage ascent to a 200 km orbit, side view and whole-Earth view*

Try it live:

- [Session 3 app: fly to orbit with staging](https://krunalpanchal1995.github.io/pan-iit-oss/openascent/session-03/)
- [Math Visual Studio](https://krunalpanchal1995.github.io/studio/)

How the Target was made is shown only as a path in [promo/roadmap.md](promo/roadmap.md).

## Who is this for
**higher secondary to advanced undergraduate (levels 4-6).** Topic area: Aerospace, Automotive and Transportation.

Prerequisites:

- School physics: Newton's laws, momentum, and the natural logarithm ln; vectors in two dimensions for Session 3.
- Python 3.10 or newer; if `python --version` works, you are ready. PRIMER.md explains the rest.
- No prior GitHub, orbital mechanics or calculus experience is needed; Sessions 2 and 3 explain the numerical steps they use.

New to Python? Read [PRIMER.md](PRIMER.md) first (10 minutes).

## Quick start

No installation knowledge needed. You need [Git](https://git-scm.com/downloads) and [Python 3.10+](https://www.python.org/downloads/) (Windows: tick "Add Python to PATH"). On Mac and Linux type `python3` wherever this page says `python`.

```bash
git clone https://github.com/KrunalPanchal1995/pan-iit-oss.git
cd pan-iit-oss/openascent
python start.py 1
```

`start.py` creates a private environment, installs what is needed and runs Session 1 with its checkpoint. Next: `python start.py 2`, `python start.py 3`, or `python start.py test` to check everything. Only a checkpoint: `python start.py check 1`.

<!-- friendly-help -->
<details>
<summary><b>Not working? Common fixes (no Git, "python not found", no internet)</b></summary>

- **No Git?** You do not need it. On the main page of this collection click the green **Code** button, then **Download ZIP**, unzip it, open a terminal inside the folder `pan-iit-oss-main/openascent` and run `python start.py 1`. The ZIP holds every project, so it is large; the live apps need no download at all.
- **"python is not recognized" or "command not found".** On Windows try `py start.py 1`. On Mac and Linux try `python3 start.py 1`. If neither works, install Python from [python.org](https://www.python.org/downloads/) and tick "Add Python to PATH".
- **Needs internet once.** The first run downloads NumPy and Matplotlib into a private folder (`.venv`); after that it works offline.
- **Rather not install anything?** Open the [live apps](https://krunalpanchal1995.github.io/pan-iit-oss/openascent/) in your browser, or use the Colab badge at the top of this page.
- **Still stuck?** [Open an issue](https://github.com/KrunalPanchal1995/pan-iit-oss/issues/new?title=%5Bopenascent%5D%20) with your operating system and the message you see. Questions from beginners are welcome.

</details>

Four lines turn the idea of Session 1 into a result (they work as they are): Save it as `try.py` and run it with `python start.py run try.py` (this uses the private environment, where NumPy is installed):

```python
import numpy as np
ve = 340 * 9.80665                             # exhaust speed of an Isp 340 s engine, m/s
print(np.round(ve * np.log(17.5 / 2.5)))       # -> 6488.0  stage-2 delta-v, 17.5 t full, 2.5 t empty
print(np.round(np.sqrt(3.986e14 / 6.571e6)))   # -> 7788.0  orbital speed at 200 km, m/s
```

Every session also opens in your browser with sliders (no install): [live apps](https://krunalpanchal1995.github.io/pan-iit-oss/openascent/). Or use the Colab badge above for the notebook.

## Sessions

| # | Session | Model level | Time | Live app |
|---|---|---|---|---|
| 1 | [The rocket equation and staging](sessions/session-01/README.md) | Level 1: conceptual interactive model | 60 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/openascent/session-01/) |
| 2 | [Straight up: gravity and drag losses](sessions/session-02/README.md) | Level 2: mathematical engineering model | 75 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/openascent/session-02/) |
| 3 | [Fly to orbit with a gravity turn and staging](sessions/session-03/README.md) | Level 3: simulation and validation | 90 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/openascent/session-03/) |

Each session follows the same six steps: A real-world problem, B concept and theory, C visual explanation, D interactive simulation, E worked example and experiment, F assessment and design challenge. Each ends with `checkpoint.py`, which prints `PASS` or `FAIL` against reference numbers. Session 3 also contains the real-world mini-project: **How much payload can the teaching launcher put in orbit?**

## Architecture

```mermaid
flowchart LR
  S1[Session 1<br/>The rocket equation and staging]
  S2[Session 2<br/>Straight up: gravity and drag losses]
  S3[Session 3<br/>Fly to orbit with a gravity turn and staging]
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
| Session 4: Launch from a rotating Earth | Give the rocket Earth's eastward surface speed and launch from a chosen latitude. | intermediate |
| Session 5: Thrust that changes with altitude | Engines with sea-level and vacuum thrust and Isp that blend with outside pressure. | intermediate |
| Session 6: Max Q and throttling | Throttle stage 1 to keep dynamic pressure under a limit and measure the cost. | intermediate |
| Session 7: An optimised upper-stage steering law | Replace the altitude hold with a linear-tangent pitch law tuned by a search. | advanced |
| Session 8: The animated Target flight | Animate the flight over a curved Earth with live panels and a falling first stage. | advanced |

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
