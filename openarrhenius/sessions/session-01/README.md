# Session 1: Reaction speed rises steeply with temperature

[Session 1 — हिन्दी](README.hi.md) · [Session 1 — മലയാളം](README.ml.md) · [Session 1 — தமிழ்](README.ta.md) · [Session 1 — తెలుగు](README.te.md)

*Level 1 (conceptual interactive model) · about 60 minutes · openarrhenius*

> This is a simplified educational model. It is not a validated design tool and must not be used for real structures, electrical installations, vehicles, industrial processes or medical decisions.

**Prerequisites**

- School algebra: straight lines, y = m x + c.
- Logarithms: ln and exp are opposites.
- You have read PRIMER.md and run `python start.py 1` once.

**Learning objectives.** After this session you can:

- Evaluate the Arrhenius law k = A exp(-Ea/(R T)) with correct units and kelvin.
- Explain why plotting ln k against 1000/T turns the curve into a straight line.
- Fit a straight line by least squares with the hand formulas and read Ea from its slope.
- Compare how steeply different activation energies make k rise.

## A. Real-world problem
Milk goes off faster on a warm day, and a gas flame needs a spark before it burns. In both cases a chemical reaction goes faster when it is hotter, and by a surprising amount, not a little. A chemist measures the rate constant k (a number that says how fast one reaction goes, here in 1/s) at five temperatures and the values climb so steeply that an ordinary graph hides most of them. How can we draw the same numbers so that a ruler can read the answer, and what does the line tell us about the reaction?

## B. Concept and theory
The Arrhenius law says k = A exp(-Ea/(R T)). T is the absolute temperature in kelvin, Ea is the activation energy, the height of the energy hill that molecules must climb, R = 8.3145 J/(mol K) is the gas constant, and A is a rate scale with the same unit as k. Because R T is the typical thermal energy, the number Ea/(R T) says how many times higher the hill is than the energy a molecule normally has; the bigger it is, the smaller exp(-Ea/(R T)) and the slower the reaction. Taking the natural logarithm gives ln k = ln A - (Ea/R)(1/T), a straight line in 1/T. We plot x = 1000/T (so the numbers are of order 1) against y = ln k; the slope is s = -Ea/(1000 R), so Ea in kJ/mol is -s times 8.3145. The line is chosen by least squares: the one that makes the sum of squared vertical gaps smallest. Its slope is Sxy/Sxx and its intercept is ybar - slope times xbar.

| Symbol | Meaning | Unit |
|---|---|---|
| k | rate constant | 1/s (for a first-order reaction) |
| A | pre-exponential factor | 1/s |
| Ea | activation energy | kJ/mol (converted to J/mol inside the exponent) |
| R | gas constant, 8.3145 | J/(mol K) |
| T | absolute temperature | K |
| x, y | 1000/T and ln k, the straight-line coordinates | x in 1000/K; y has no unit |
| s | slope of ln k against 1000/T | no unit |

**Assumptions**

- One single reaction step controls the rate (a later session shows what happens if not).
- Temperature is in kelvin: add 273.15 to degrees Celsius.
- A and Ea do not depend on T over the range studied.
- Measurement errors are random and proportional to k (each reading is off by a few percent of its own value).
- This is a simplified teaching model, not a validated tool for designing a reactor or a process.

$$ k(T)=A\,\exp\!\left(-\frac{E_a}{R\,T}\right) $$

$$ \ln k=\ln A-\frac{E_a}{R}\cdot\frac{1}{T} $$

$$ s=\frac{S_{xy}}{S_{xx}},\quad S_{xx}=\sum_i (x_i-\bar x)^2,\quad S_{xy}=\sum_i (x_i-\bar x)(y_i-\bar y),\quad b=\bar y-s\,\bar x $$

$$ E_a\,[\mathrm{kJ/mol}]=-s\,R,\qquad s=\text{slope of }\ln k\text{ against }1000/T $$

## C. Visual explanation
The figure has two panels made from the same five measured points. On ordinary axes (left) k against T is a steep curve: the points at 600 and 700 K sit on the floor next to the points at 1000 K, which dominate the picture. On the Arrhenius axes (right) ln k against 1000/T the points fall on a straight line, and the fitted line has slope -18.0, which gives Ea close to 150 kJ/mol. Going left to right on the right-hand plot means going colder, so k falls. The speed-up between two temperatures is not constant: it is 73.4 times from 600 to 700 K but only 25.1 times from 700 to 800 K.

![Same five data points on ordinary axes (steep curve) and on Arrhenius axes (straight line with slope -18.0, Ea about 150 kJ/mol).](../../docs/figures/s01_arrhenius_axes.png)

*Same five data points on ordinary axes (steep curve) and on Arrhenius axes (straight line with slope -18.0, Ea about 150 kJ/mol).*

## D. Interactive simulation
Run the lesson (`python start.py 1`), then open the live app: [Session 1: reaction speed against temperature](https://krunalpanchal1995.github.io/pan-iit-oss/openarrhenius/session-01/) (or `app.html` in this folder). Move the activation energy and temperature sliders. In the bar view compare the energy hill with the thermal energy R T, in the first graph watch k rise along the curve, and in the straight-line view see that changing Ea tilts the line while the point slides along it.

**Challenge.** Find an activation energy and temperature with k of at least 1000 per s while keeping the temperature at 500 K or below.

## E. Worked example and experiment
**Problem.** A reaction has A = 1e13 per s and Ea = 150 kJ/mol. Find k at 800 K, and how many times faster it goes at 700 K than at 600 K.

1. Convert the energy: Ea = 150 kJ/mol = 150000 J/mol.
2. Exponent: Ea/(R T) = 150000 / (8.3145 x 800) = 22.55 (a pure number).
3. k(800 K) = 1e13 x exp(-22.55) = 1608 per s.
4. The factor A cancels in a ratio: k(700)/k(600) = exp[(Ea/R)(1/600 - 1/700)] = 73.4.
5. Sanity check: the reaction is faster when hotter (73.4 is above 1) and the same step of 100 K gives a smaller factor higher up (25.1 from 700 to 800 K), as the figure shows.

**Answer.** k(800 K) = 1608 per s; going from 600 K to 700 K makes the reaction 73.4 times faster.

**Experiment.** Measure with a stopwatch the time an iodine-clock reaction (a clear mixture that suddenly turns dark blue) takes at four water temperatures (take 1/time as a measure of k), plot ln(1/time) against 1000/T with T in kelvin and fit a line. Expect a roughly straight line; the slope gives an apparent Ea. Model versus reality: a stopwatch time is a crude measure of k, the temperature drifts while the mixture reacts, and real reactions often have several steps, so the apparent Ea may differ from the one-step value and the line may bend.

## F. Assessment and design challenge
**Question type A: Conceptual.** Why does plotting ln k against 1000/T give a straight line, and what would you see if you plotted k against 1/T instead?

<details>
<summary>Hint</summary>

Take the logarithm of the Arrhenius law and compare it with y = m x + c.

</details>

<details>
<summary>Step-by-step solution</summary>

ln k = ln A - (Ea/R)(1/T) has the form y = c + m x with y = ln k and x = 1/T (we use 1000/T just to keep the numbers near 1). The slope is -Ea/R and the intercept is ln A. Plotting k itself against 1/T would give an exponential curve, not a line, because k contains the exponential.

</details>

**Question type B: Numerical.** For Ea = 100 kJ/mol, by what factor does k grow from 600 K to 700 K, and what is the slope of the Arrhenius line? Compare with the 73.4 times for Ea = 150 kJ/mol.

<details>
<summary>Hint</summary>

Use k(700)/k(600) = exp[(Ea/R)(1/600 - 1/700)] and slope = -Ea/(1000 R) with R = 8.3145.

</details>

<details>
<summary>Step-by-step solution</summary>

The factor is 17.5 and the slope is -12.03 (units: none). The smaller activation energy gives a smaller factor and a less steep line. Sanity check: the factor is above 1 and lower than 73.4, as it should be for a lower hill.

</details>

**Question type C: Graph and simulation interpretation.** In the right-hand panel of the figure the fitted slope is -18.0. What activation energy does that mean, and what would a line twice as steep mean?

<details>
<summary>Hint</summary>

Ea (kJ/mol) = - slope x 8.3145.

</details>

<details>
<summary>Step-by-step solution</summary>

Ea = 18.0 x 8.3145 = 149.7 kJ/mol (the fitted slope is -18.005). A line twice as steep means twice the activation energy, about 300 kJ/mol: the reaction would be much more sensitive to temperature.

</details>

**Question type D: Design and optimisation challenge.** Design: a furnace can reach at most 600 K and you need k of at least 1000 per s with A = 1e13 per s. What is the largest activation energy that works? And what temperature does a reaction with Ea = 150 kJ/mol need to reach the same k?

<details>
<summary>Hint</summary>

Solve A exp(-Ea/(R T)) = 1000, i.e. Ea/(R T) = ln(1e10).

</details>

<details>
<summary>Step-by-step solution</summary>

Ea/(R T) = ln(1e10) = 23.03, so at 600 K the largest Ea is 23.03 x 8.3145 x 600 / 1000 = 114.9 kJ/mol. For Ea = 150 kJ/mol the temperature is T = 150000 / (8.3145 x 23.03) = 783.5 K, well above the furnace limit. Trade-off: a lower hill allows a cooler (cheaper, safer) process but is not a free choice, since it is fixed by the chemistry.

</details>

Score yourself with [RUBRIC.md](../../RUBRIC.md). Print the [activity sheet](activity_sheet.md) to work on paper.

## Common misconceptions
| Common misconception | What is actually true |
|---|---|
| Reaction rates double for every 10 degrees. | That is only a rule of thumb. With Ea = 150 kJ/mol the factor from 300 K to 310 K is 7.0, and at higher temperature the factor per 10 K is much smaller. The factor depends on Ea and T. |
| Use degrees Celsius in the formula. | T must be in kelvin. A temperature of 0 degrees Celsius is 273.15 K, and 1/T with a Celsius number is meaningless. |
| A higher activation energy means a faster reaction. | A higher hill means a slower reaction at a given T, but one that speeds up faster when heated: the Arrhenius line is steeper. |
| The fitted line must pass through every point. | Real data have scatter; least squares gives the line that is closest overall, and the scatter is information about the error. |

## Glossary
- **rate constant k**: a number that says how fast one reaction goes; its unit depends on the reaction (1/s for first order)
- **activation energy Ea**: the energy hill molecules must climb to react; read from the slope of the Arrhenius plot
- **pre-exponential factor A**: the rate scale in the law; the value k would approach at infinite temperature
- **least squares**: choosing the line that makes the sum of squared vertical gaps smallest
- **Arrhenius plot**: a graph of ln k against 1/T (here 1000/T)
- **kelvin**: absolute temperature scale, T(K) = T(degrees Celsius) + 273.15

## Finish
1. Do the three coding tasks in [exercises.md](exercises.md).
2. Run `python start.py 1` again after your changes. It ends with the checkpoint; when it prints `PASS`, you are done. (Checkpoint only: `python start.py check 1`.)

Next: [Session 2](../session-02/README.md)
