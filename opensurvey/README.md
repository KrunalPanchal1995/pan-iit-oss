# opensurvey

[![Checks](https://github.com/KrunalPanchal1995/pan-iit-oss/actions/workflows/tests.yml/badge.svg)](https://github.com/KrunalPanchal1995/pan-iit-oss/actions/workflows/tests.yml) ![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square) ![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square) [![Open in Colab](https://img.shields.io/badge/Colab-session%201-F9AB00?style=flat-square&logo=googlecolab&logoColor=white)](https://colab.research.google.com/github/KrunalPanchal1995/pan-iit-oss/blob/main/opensurvey/sessions/session-01/lesson.ipynb) [![Live apps](https://img.shields.io/badge/live-apps-1f6feb?style=flat-square)](https://krunalpanchal1995.github.io/pan-iit-oss/opensurvey/)

**Level a site and measure it with a total station model, in three sessions.**

opensurvey teaches the mathematics of the surveyor, from one level reading to an adjusted closed traverse, using only Python and a browser.

- **Start from zero.** Session 1 needs only subtraction and a picture of a staff; trigonometry arrives in Session 2.
- **See it move.** Every session ships a slider app that runs in the browser, with labelled graphs.
- **Know you got it right.** Each session ends with a checkpoint that prints PASS or FAIL against hand calculations and exact answers.
- **Build the missing half.** The repo stops at Session 3 on purpose; the roadmap shows the path to the Target.

[Target](#the-target) · [Who is this for](#who-is-this-for) · [Quick start](#quick-start) · [Sessions](#sessions) · [Roadmap](#roadmap) · [Contribute](#contribute) · [Explainer PDF](docs/explainer.pdf)

> **This repo is incomplete on purpose.** Sessions 1 to 3 are here and fully working. The finished Target below is a preview of what the community can build next. We show you the path, not the code. Sessions 4 and up are yours.

## The Target

A surveyor walks a five-corner plot leg by leg over a contour map. At the end the walk misses its start: a red misclosure arrow appears (errors are exaggerated so you can see it). Then the Bowditch correction slides every corner back along the walk until the figure closes, while a levelling profile below shows the staff readings for the same ground. Your goal over the coming sessions: build that adjustment and the contour and level profile yourself, then extend them.

![Target: a traverse walked leg by leg, the misclosure arrow, and the Bowditch correction closing it](promo/media/target.gif)

*Target: a traverse walked leg by leg, the misclosure arrow, and the Bowditch correction closing it*

![Target still: the unadjusted walk (red) and the adjusted corners (green) over a contour map, with a level profile](promo/media/target_still.png)

*Target still: the unadjusted walk (red) and the adjusted corners (green) over a contour map, with a level profile*

![Where 2000 simulated surveys end: the scatter of misclosure vectors with typical instrument errors](promo/media/error_scatter.png)

*Where 2000 simulated surveys end: the scatter of misclosure vectors with typical instrument errors*

Try it live:

- [Math Visual Studio: coordinates and analytic geometry (Atlas S05)](https://krunalpanchal1995.github.io/studio/#atlas?ch=S05&ex=1)

How the Target was made is shown only as a path in [promo/roadmap.md](promo/roadmap.md).

## Who is this for
**diploma / undergraduate to advanced undergraduate (levels 5-6).** Topic area: Civil Engineering and Construction.

Prerequisites:

- Adding and subtracting decimals; sine and cosine of an angle (school trigonometry) from Session 2 on.
- Python 3.10 or newer; if `python --version` works, you are ready. PRIMER.md explains the rest.
- No prior GitHub, surveying or statistics experience is needed.

New to Python? Read [PRIMER.md](PRIMER.md) first (10 minutes).

## Quick start

No installation knowledge needed. You need [Git](https://git-scm.com/downloads) and [Python 3.10+](https://www.python.org/downloads/) (Windows: tick "Add Python to PATH"). On Mac and Linux type `python3` wherever this page says `python`.

```bash
git clone https://github.com/KrunalPanchal1995/pan-iit-oss.git
cd pan-iit-oss/opensurvey
python start.py 1
```

`start.py` creates a private environment, installs what is needed and runs Session 1 with its checkpoint. Next: `python start.py 2`, `python start.py 3`, or `python start.py test` to check everything. Only a checkpoint: `python start.py check 1`.

<!-- friendly-help -->
<details>
<summary><b>Not working? Common fixes (no Git, "python not found", no internet)</b></summary>

- **No Git?** You do not need it. On the main page of this collection click the green **Code** button, then **Download ZIP**, unzip it, open a terminal inside the folder `pan-iit-oss-main/opensurvey` and run `python start.py 1`. The ZIP holds every project, so it is large; the live apps need no download at all.
- **"python is not recognized" or "command not found".** On Windows try `py start.py 1`. On Mac and Linux try `python3 start.py 1`. If neither works, install Python from [python.org](https://www.python.org/downloads/) and tick "Add Python to PATH".
- **Needs internet once.** The first run downloads NumPy and Matplotlib into a private folder (`.venv`); after that it works offline.
- **Rather not install anything?** Open the [live apps](https://krunalpanchal1995.github.io/pan-iit-oss/opensurvey/) in your browser, or use the Colab badge at the top of this page.
- **Still stuck?** [Open an issue](https://github.com/KrunalPanchal1995/pan-iit-oss/issues/new?title=%5Bopensurvey%5D%20) with your operating system and the message you see. Questions from beginners are welcome.

</details>

Four lines turn the idea of Session 1 into a result (they work as they are): Save it as `try.py` and run it with `python start.py run try.py` (this uses the private environment, where NumPy is installed):

```python
bs, fs = 1.525, 2.310                      # staff readings in metres: backsight, foresight
rl_a = 100.000                             # reduced level (height) of the first point
rl_b = rl_a + (bs - fs)                    # B is lower because the foresight is bigger
print(round(rl_b, 3))                      # -> 99.215
```

Every session also opens in your browser with sliders (no install): [live apps](https://krunalpanchal1995.github.io/pan-iit-oss/opensurvey/). Or use the Colab badge above for the notebook.

## Sessions

| # | Session | Model level | Time | Live app |
|---|---|---|---|---|
| 1 | [Height difference with a level and a staff](sessions/session-01/README.md) | Level 1: conceptual interactive model | 60 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/opensurvey/session-01/) |
| 2 | [Levelling books, slope distances and total-station coordinates](sessions/session-02/README.md) | Level 2: mathematical engineering model | 75 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/opensurvey/session-02/) |
| 3 | [Close, adjust and test a traverse](sessions/session-03/README.md) | Level 3: simulation and validation | 90 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/opensurvey/session-03/) |

Each session follows the same six steps: A real-world problem, B concept and theory, C visual explanation, D interactive simulation, E worked example and experiment, F assessment and design challenge. Each ends with `checkpoint.py`, which prints `PASS` or `FAIL` against reference numbers. Session 3 also contains the real-world mini-project: **Adjust a field traverse and report coordinates and area**.

## Architecture

```mermaid
flowchart LR
  S1[Session 1<br/>Height difference with a level and a staff]
  S2[Session 2<br/>Levelling books, slope distances and total-station coordinates]
  S3[Session 3<br/>Close, adjust and test a traverse]
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
| Session 4: Least-squares adjustment | A second adjustment function that estimates the corner coordinates by weighted least squares and reports the residuals. | intermediate |
| Session 5: Find distance blunders too | A locator for the leg with a distance blunder, using the direction of the misclosure vector. | intermediate |
| Session 6: A levelling network | A loop of four levelling lines with known benchmark levels, adjusted so that every loop closes. | intermediate |
| Session 7: Resection: where am I? | A function that solves the coordinates of an unknown station from the angles measured to three known points, with a picture of the geometry. | advanced |
| Session 8: Contours and earthwork | A grid of levels, contour lines, and the volume to cut and fill to make a level platform. | advanced |

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
