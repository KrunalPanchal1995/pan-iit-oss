# opencircuitlab

[![Checks](https://github.com/KrunalPanchal1995/pan-iit-oss/actions/workflows/tests.yml/badge.svg)](https://github.com/KrunalPanchal1995/pan-iit-oss/actions/workflows/tests.yml) ![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square) ![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square) [![Open in Colab](https://img.shields.io/badge/Colab-session%201-F9AB00?style=flat-square&logo=googlecolab&logoColor=white)](https://colab.research.google.com/github/KrunalPanchal1995/pan-iit-oss/blob/main/opencircuitlab/sessions/session-01/lesson.ipynb) [![Live apps](https://img.shields.io/badge/live-apps-1f6feb?style=flat-square)](https://krunalpanchal1995.github.io/pan-iit-oss/opencircuitlab/)

**Build series and parallel circuits and solve them with Kirchhoff's laws.**

opencircuitlab teaches circuit analysis from a battery and two bulbs to a matrix solver that handles any resistor network, using only Python and a browser.

- **Start from a battery and a bulb.** Session 1 needs only Ohm's law; every symbol is explained from scratch.
- **See it move.** Every session ships a slider app that runs in the browser, with labelled graphs and a challenge.
- **Know you got it right.** Each session ends with a checkpoint that prints PASS or FAIL against hand calculations and conservation of energy.
- **Build the missing half.** The repo stops at Session 5 on purpose; the roadmap shows the path to the Target.

[Target](#the-target) · [Who is this for](#who-is-this-for) · [Quick start](#quick-start) · [Sessions](#sessions) · [Roadmap](#roadmap) · [Contribute](#contribute) · [Explainer PDF](docs/explainer.pdf)

> **This repo is incomplete on purpose.** Sessions 1 to 5 are here and fully working. The finished Target below is a preview of what the community can build next. We show you the path, not the code. Sessions 6 and up are yours.

## The Target

An animated bridge circuit: one resistor is swept from 500 to 1500 ohm while every node voltage and every branch current is recomputed and drawn on the schematic. Beside it the Thevenin equivalent of the bridge output is drawn as a load line, with the operating point sliding along it, and a graph shows the output crossing zero at the balance point. Your goal over the coming sessions: after the solver of Session 3, the netlist reader of Session 4 and the diode loop of Session 5, animate any component sweep.

![Target: sweeping one bridge resistor while node voltages, branch currents and the Thevenin load line update](promo/media/target.gif)

*Target: sweeping one bridge resistor while node voltages, branch currents and the Thevenin load line update*

![Target, one frame: R3 = 1155 ohm, the bridge is out of balance](promo/media/target_still.png)

*Target, one frame: R3 = 1155 ohm, the bridge is out of balance*

![Target, R3 = 500 ohm: the output voltage is negative](promo/media/target_low.png)

*Target, R3 = 500 ohm: the output voltage is negative*

![Target, R3 = 1500 ohm: the output voltage is positive](promo/media/target_high.png)

*Target, R3 = 1500 ohm: the output voltage is positive*

Try it live:

- [Math Visual Studio (open playground)](https://krunalpanchal1995.github.io/studio/)

How the Target was made is shown only as a path in [promo/roadmap.md](promo/roadmap.md).

## Who is this for
**secondary school to diploma / undergraduate (levels 3-5).** Topic area: Electricity, Magnetism and Electronics.

Prerequisites:

- Ohm's law, V = I R, and the idea of a battery and a resistor (school physics).
- Python 3.10 or newer; if `python --version` works, you are ready. PRIMER.md explains the rest.
- Session 3 uses a little matrix algebra (solving two or three equations together); it is explained when needed.

New to Python? Read [PRIMER.md](PRIMER.md) first (10 minutes).

## Quick start

No installation knowledge needed. You need [Git](https://git-scm.com/downloads) and [Python 3.10+](https://www.python.org/downloads/) (Windows: tick "Add Python to PATH"). On Mac and Linux type `python3` wherever this page says `python`.

```bash
git clone https://github.com/KrunalPanchal1995/pan-iit-oss.git
cd pan-iit-oss/opencircuitlab
python start.py 1
```

`start.py` creates a private environment, installs what is needed and runs Session 1 with its checkpoint. Next: `python start.py 2`, `python start.py 3`, or `python start.py test` to check everything. Only a checkpoint: `python start.py check 1`.

<!-- friendly-help -->
<details>
<summary><b>Not working? Common fixes (no Git, "python not found", no internet)</b></summary>

- **No Git?** You do not need it. On the main page of this collection click the green **Code** button, then **Download ZIP**, unzip it, open a terminal inside the folder `pan-iit-oss-main/opencircuitlab` and run `python start.py 1`. The ZIP holds every project, so it is large; the live apps need no download at all.
- **"python is not recognized" or "command not found".** On Windows try `py start.py 1`. On Mac and Linux try `python3 start.py 1`. If neither works, install Python from [python.org](https://www.python.org/downloads/) and tick "Add Python to PATH".
- **Needs internet once.** The first run downloads NumPy and Matplotlib into a private folder (`.venv`); after that it works offline.
- **Rather not install anything?** Open the [live apps](https://krunalpanchal1995.github.io/pan-iit-oss/opencircuitlab/) in your browser, or use the Colab badge at the top of this page.
- **Still stuck?** [Open an issue](https://github.com/KrunalPanchal1995/pan-iit-oss/issues/new?title=%5Bopencircuitlab%5D%20) with your operating system and the message you see. Questions from beginners are welcome.

</details>

Four lines solve a whole circuit with one matrix equation (they work as they are): Save it as `try.py` and run it with `python start.py run try.py` (this uses the private environment, where NumPy is installed):

```python
import numpy as np
G = np.array([[1/1000 + 1/2000 + 1/1000]])   # one node: R1 = 1 kohm from 12 V, R2 = 2 kohm and a 1 kohm load to ground
i = np.array([12 / 1000])                      # current pushed into the node through R1
print(np.linalg.solve(G, i).round(3))          # -> [4.8]  the node voltage in volts
```

Every session also opens in your browser with sliders (no install): [live apps](https://krunalpanchal1995.github.io/pan-iit-oss/opencircuitlab/). Or use the Colab badge above for the notebook.

## Sessions

| # | Session | Model level | Time | Live app |
|---|---|---|---|---|
| 1 | [A battery, a switch and bulbs: series and parallel](sessions/session-01/README.md) | Level 1: conceptual interactive model | 60 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/opencircuitlab/session-01/) |
| 2 | [Kirchhoff's laws, dividers and the loading effect](sessions/session-02/README.md) | Level 2: mathematical engineering model | 80 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/opencircuitlab/session-02/) |
| 3 | [Nodal analysis by matrix, Thevenin and the sensor bridge](sessions/session-03/README.md) | Level 3: simulation and validation | 90 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/opencircuitlab/session-03/) |
| 4 | [Read a netlist: text in, voltages out](sessions/session-04/README.md) | Level 3: simulation and validation | 90 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/opencircuitlab/session-04/) |
| 5 | [A nonlinear part: the diode and Newton's method](sessions/session-05/README.md) | Level 3: simulation and validation | 90 min | [open](https://krunalpanchal1995.github.io/pan-iit-oss/opencircuitlab/session-05/) |

Each session follows the same six steps: A real-world problem, B concept and theory, C visual explanation, D interactive simulation, E worked example and experiment, F assessment and design challenge. Each ends with `checkpoint.py`, which prints `PASS` or `FAIL` against reference numbers. Session 3 contains the real-world mini-project **Design a Pt1000 temperature-sensor bridge**; Session 4 adds **Debug the technician's bridge file**, and Session 5 **Choose the resistor of a diode indicator**.

## Architecture

```mermaid
flowchart LR
  S1[Session 1<br/>A battery, a switch and bulbs: series and parallel]
  S2[Session 2<br/>Kirchhoff's laws, dividers and the loading effect]
  S3[Session 3<br/>Nodal analysis by matrix, Thevenin and the sensor bridge]
  S4[Session 4<br/>Read a netlist: text in, voltages out]
  S5[Session 5<br/>A nonlinear part: the diode and Newton's method]
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
| Session 6: An amplifier from a controlled source | A controlled-source stamp and an inverting amplifier built with it. | intermediate |
| Session 7: Sensitivity without Monte Carlo | A function returning dVout/dR for every resistor of any network. | advanced |
| Session 8: Time enters: the RC circuit | A transient solver for a resistor and a capacitor on a step input. | advanced |

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
