# Session 3: How sure are we about k where we did not measure?

*Level 3 (simulation and validation) · about 90 minutes · openarrhenius*

> This is a simplified educational model. It is not a validated design tool and must not be used for real structures, electrical installations, vehicles, industrial processes or medical decisions.

**Prerequisites**

- Session 1: the Arrhenius plot.
- Session 2: least squares, Sxx and SE(Ea).
- A covariance matrix is explained in Section B.

**Learning objectives.** After this session you can:

- Compute the covariance of (ln A, Ea) from the regression and explain why they are strongly correlated.
- Draw a confidence band for ln k(T) and explain why it flares outside the data.
- Predict k at an unmeasured temperature with Monte Carlo and check it against the formula.
- Validate the whole method on synthetic data with a coverage test, and recognise two failure cases (narrow range, curved plot).

## A. Real-world problem
A lab measured k between 600 and 1000 K, but an engine model needs k at 2000 K, where nobody could measure. A single line gives one number. A useful answer is a number plus a range that holds the truth 95 times in 100. How wide must that range be, how do we know our method is honest, and what warning signs tell us the straight line should not be trusted at all?

## B. Concept and theory
Fit y = b0 + b1 x with x = 1000/T and y = ln k. The estimate of the error of ln k is s = sqrt(RSS/(n-2)), where RSS is the sum of squared residuals and n-2 are the degrees of freedom. The covariance of (b0, b1) is s^2 (X^T X)^-1, with X a matrix with a column of ones and a column of x. Since ln A = b0 and Ea = -R b1, the covariance of (ln A, Ea) follows by a sign change and a scale. Because all x values are on one side of zero, ln A and Ea are strongly correlated (r close to +1): a line that is steeper must also start higher. At a temperature T the fitted ln k has variance s^2 [1/n + (x - xbar)^2 / Sxx], smallest at the mean x and growing with distance from it, so the 95 percent band, ln k plus or minus t times the standard error, is narrowest in the middle of the data and flares outside. Here t is the Student t factor for n-2 degrees of freedom (3.182 for 3, 2.365 for 7). On the k axis the band is a multiplicative factor. Monte Carlo propagation draws many (ln A, Ea) pairs from the fitted covariance, computes k at the target for each and reads off percentiles. To validate, repeat the whole experiment many times with known A and Ea and count how often the interval contains the true k (coverage). If the noise is not equal for all points, use weights 1/sigma_i^2. The straight line assumes one Arrhenius process: the band counts only noise, not a wrong model.

| Symbol | Meaning | Unit |
|---|---|---|
| b0, b1 | intercept and slope of ln k against 1000/T | no unit |
| s | estimated error of ln k | no unit |
| cov | covariance matrix of the fitted parameters | same units as the squares of the parameters |
| t | Student t factor for a 95 percent interval | no unit |
| r | correlation between ln A and Ea | no unit |
| coverage | fraction of repeated experiments whose interval contains the truth | no unit |

**Assumptions**

- Errors of ln k are independent, unbiased and normally distributed.
- The straight-line (single-channel Arrhenius) model is correct; the band does not include model error.
- Temperatures are exact.
- Synthetic data are used so the truth is known; real data need extra care.
- This is a simplified teaching model, not a validated tool for design decisions.

$$ \mathrm{Cov}(b_0,b_1)=s^2\,(X^{\mathsf T}X)^{-1},\qquad s^2=\frac{\mathrm{RSS}}{n-2} $$

$$ \mathrm{Cov}(\ln A,E_a)=M\,\mathrm{Cov}(b_0,b_1)\,M^{\mathsf T},\qquad M=\begin{pmatrix}1&0\\0&-R\end{pmatrix} $$

$$ \mathrm{Var}[\ln k(T)]=s^2\left[\frac1n+\frac{(x-\bar x)^2}{S_{xx}}\right],\qquad x=\frac{1000}{T} $$

$$ k\in\left[\hat k\,e^{-t\,\mathrm{se}},\ \hat k\,e^{+t\,\mathrm{se}}\right]\quad(95\%) $$

## C. Visual explanation
The figure has three panels. Left: nine data points from 600 to 1000 K, the fitted line, the 95 percent band out to 2000 K and the true law (dotted). The band is thinnest at 1000/T = 1.28 (778.7 K, the middle of the data) and widens towards both ends, much more on the extrapolated side. Middle: the one-sigma ellipse of (Ea, ln A) is a thin tilted sliver, which shows the strong positive correlation: only certain combinations of Ea and ln A are consistent with the data. Right: for a reaction with two channels the plot is curved; a straight line fitted over 800 to 1600 K misses the truth at 2000 K by a large factor, and the band does not warn about it.

![Left: the 95 percent band flares outside the data. Middle: the one-sigma ellipse of (Ea, ln A), thin and tilted (r = 0.986 is for the worked example, the figure uses seed 4). Right: failure on curved data from two channels; the straight line misses the truth at 2000 K.](../../docs/figures/s03_band_ellipse_failure.png)

*Left: the 95 percent band flares outside the data. Middle: the one-sigma ellipse of (Ea, ln A), thin and tilted (r = 0.986 is for the worked example, the figure uses seed 4). Right: failure on curved data from two channels; the straight line misses the truth at 2000 K.*

**A resampling alternative: the bootstrap.** `bootstrap_predict(T, k, T_target, method="residual" or "pairs")` builds the interval without a formula. It reuses the data you already have: the residual version adds randomly drawn residuals (corrected for leverage) back onto the fitted line, the pairs version draws whole (T, k) points with replacement, and each of 4000 resamples is refitted and evaluated at the target. It is pure numpy and takes a few milliseconds (the limit is 20 seconds). The table uses the mini-project data (7 points, 700 to 1100 K, 6 percent error, true k(2000 K) = 2.2e8 per s) and then asks how often each method's interval holds the true k when the whole experiment is repeated 1000 times (`interval_coverage` in `lesson.py`):

| Method | Lower (1/s) | Upper (1/s) | Upper / lower | Coverage, 7 points | Coverage, 40 points |
|---|---|---|---|---|---|
| t formula (`band`) | 1.5e+08 | 2.67e+08 | 1.78 | 94.3% | 95.1% |
| normal Monte Carlo (`mc_predict`) | 1.61e+08 | 2.5e+08 | 1.55 | 87.7% | 94.0% |
| residual bootstrap | 1.63e+08 | 2.47e+08 | 1.52 | 88.1% | 94.2% |
| pairs bootstrap | 1.72e+08 | 2.47e+08 | 1.43 | 88.4% | 93.8% |

All four hold the true k in the single example, but the repeated experiments tell them apart. The t formula is honest at 94 to 95 percent. Monte Carlo and both bootstraps are about 6 points short at 7 points, because they treat the scatter of 7 numbers as if it were the true scatter and the t factor (2.57 against 1.96) is what pays for that mistake; with 40 points the four methods agree. The lesson: a bootstrap is a good choice when no formula exists, but with fewer than about 20 points it needs care, and a narrower interval is not a better one unless its coverage is checked.

## D. Interactive simulation
Run the lesson (`python start.py 3`), then open the live app: [Session 3: how sure is k at 2000 K?](https://krunalpanchal1995.github.io/pan-iit-oss/openarrhenius/session-03/) (or `app.html` in this folder). Change the noise, the number of points and the cold end of the data window. In the band view watch the flare at 2000 K, in the ellipse view see the sliver shrink or stretch, and in the ruler view compare the length of the data window with the distance to the target.

**Challenge.** Make the 95 percent factor on k(2000 K) at most 1.15 with an error of 5 percent or more.

## E. Worked example and experiment
**Problem.** Nine temperatures from 600 to 1000 K in steps of 50 K, synthetic data with 5 percent error, true A = 1e13 per s and Ea = 150 kJ/mol (seed 4). Fit, give Ea and ln A with errors and their correlation, and predict k at 2000 K with a 95 percent interval. Does it contain the truth?

1. x = 1000/T has mean 1.2841 (T = 778.7 K) and Sxx = 0.4113.
2. The regression gives s = 0.0535 on 7 degrees of freedom; Ea = 149.43 +- 0.69 kJ/mol, ln A = 29.833 +- 0.109, and correlation 0.986 between them.
3. At 2000 K, x = 0.5: se = s sqrt(1/9 + (0.5 - 1.2841)^2 / 0.4113) = 0.0678.
4. t for 7 degrees of freedom = 2.365, so the factor is exp(2.365 x 0.0678) and the 95 percent interval is 9.6e8 to 1.33e9 per s around the fitted 1.13e9 per s.
5. The true k(2000 K) = 1.209e9 per s lies inside the interval. Check inside the data: the band is narrowest at x = 1.2841 where se = s/3 = 0.0178, and it is wider by a factor 1.09 at 800 K, 1.29 at 1500 K and 1.38 at 2000 K (upper divided by lower).

**Answer.** Ea = 149.43 +- 0.69 kJ/mol; k(2000 K) = 1.13e9 per s with 95 percent interval 9.6e8 to 1.33e9, which contains the true 1.209e9. Monte Carlo agrees with the formula.

**Experiment.** Measure k at 600 to 1000 K, then try a single measurement at the highest temperature you can reach safely (say 1400 K) and compare it with the extrapolated band. Within the model's assumptions the band should hold the new point about 95 times in 100. In reality the new point often falls outside because a second reaction path or a change of mechanism sets in at high temperature: the model has no way to know, which is why extrapolation far outside the data is dangerous.

## Real-world application and mini-project: Fit Ea and A and predict k at 2000 K with a band
A lab reports seven rate constants for one reaction at 700, 766.7, 833.3, 900, 966.7, 1033.3 and 1100 K. In this exercise the data are synthetic so you can check your answer: build them with `synthetic(np.linspace(700, 1100, 7), 0.06, 21, 3e11, 120.0)` from Session 3 (6 percent multiplicative error, true A = 3e11 per s, true Ea = 120 kJ/mol). Fit the line, report Ea and ln A with their errors and correlation, and predict k at 2000 K with a 95 percent interval from `band` and from Monte Carlo. Then repeat with the window 900 to 1100 K and see what the interval does.

**Deliverable:** A script that prints Ea +- se, ln A +- se and the correlation, then k(2000 K) with its 95 percent interval (formula and Monte Carlo), repeats the calculation for 900 to 1100 K, and saves a figure with the data, fitted line, band out to 2000 K and the true law.

**Success looks like:** For 700 to 1100 K: Ea = 118.75 +- 1.42 kJ/mol, k(2000 K) = 2.0e8 per s with interval 1.5e8 to 2.67e8, which contains the true 2.2e8 and has an upper-to-lower factor of 1.78 (below 2). For 900 to 1100 K the factor grows to 3.12, which fails the limit of 2.

## F. Assessment and design challenge
**Question type A: Conceptual.** Why does the confidence band get wider outside the data, and why is it widest on the side of the extrapolation?

<details>
<summary>Hint</summary>

Look at the term (x - xbar)^2 / Sxx in the variance of the fitted ln k.

</details>

<details>
<summary>Step-by-step solution</summary>

The fitted value at x is the line's height at x. Errors in the slope matter more the farther x is from the centre of the data (a lever effect), so the variance grows like (x - xbar)^2. At 2000 K the value x = 0.5 is 0.78 away from the mean, while the data span only from 1.0 to 1.67, so the band is wide there. Also, the band is a multiplicative factor on k: a constant width in ln k means a wider range in k itself.

</details>
**Question type B: Numerical.** With s = 0.0535, n = 9, xbar = 1.2841 and Sxx = 0.4113 find the standard error of ln k at 800 K (x = 1.25) by hand and the 95 percent factor with t = 2.365.

<details>
<summary>Hint</summary>

se = s sqrt(1/n + (x - xbar)^2 / Sxx).

</details>

<details>
<summary>Step-by-step solution</summary>

(x - xbar)^2 = 0.0341^2 = 0.00116, divided by 0.4113 is 0.0028; 1/9 = 0.1111; the sum is 0.1139, its square root 0.3375, so se = 0.0535 x 0.3375 = 0.0181 (the lesson gives 0.01806). The factor on each side is exp(2.365 x 0.0181) = 1.044; the upper divided by the lower is 1.09.

</details>
**Question type C: Graph and simulation interpretation.** In the right panel of the figure, the straight-line fit has a band that does not contain the truth at 2000 K. What number from the fit warns you that the straight line is wrong?

<details>
<summary>Hint</summary>

Compare the fitted error s with the noise you expect from the lab (3 percent).

</details>

<details>
<summary>Step-by-step solution</summary>

The residual error s is 0.86 (a typical misfit of a factor 2.4 in k), where a true single channel with 3 percent noise gives s of about 0.037. A fit error far above the known measurement error means the straight line does not describe the data. The truth at 2000 K is 5.98e8 per s and the line predicts 6.5e7, a factor 9.2 too low.

</details>
**Question type D: Design and optimisation challenge.** Design: you can add measurements to the 600 to 1000 K data to get k(2000 K) with a factor of at most 1.15. What do you change first, the number of points or the range, and why? Test the cases in the app.

<details>
<summary>Hint</summary>

Try the app: 5 percent error, change n and the cold end Tlow separately.

</details>

<details>
<summary>Step-by-step solution</summary>

In the app, with 5 percent error and a hot end of 1000 K, six points from 800 K give a factor 1.52; twelve points from 500 K give 1.11, which meets the limit. Widening the range mostly helps because it increases Sxx and moves xbar towards the target; adding points helps through 1/n and through the t factor. A cheaper option is to extend the range towards high temperature, but the furnace limit and the risk of a second reaction channel are the trade-offs.

</details>

Score yourself with [RUBRIC.md](../../RUBRIC.md). Print the [activity sheet](activity_sheet.md) to work on paper.

## Common misconceptions
| Common misconception | What is actually true |
|---|---|
| A 95 percent band means 95 percent of the data points lie inside it. | The band is for the fitted curve (the mean ln k), not for individual measurements. It is much narrower than the scatter of the data. |
| The band is the same width everywhere. | It is narrowest at the mean of 1000/T and flares outside the data, especially on the extrapolated side. |
| A narrow band means the model is right. | The band counts only random error. A curved Arrhenius plot gives a straight-line fit with a tight band around a wrong answer; check that s is close to the known measurement error. |
| Ea and ln A can be judged separately. | They are strongly correlated (r = 0.986 in the worked example): the error in k at one temperature is much smaller than the individual errors suggest. |
| A narrow data range gives a wrong coverage. | The interval is wide but honest: with 900 to 1000 K data the coverage is still about 94 percent; it is the usefulness that suffers. |

## Glossary
- **covariance matrix**: a table of how much each fitted number varies and how the numbers vary together
- **correlation**: covariance divided by the product of the standard errors; between -1 and 1
- **confidence band**: a range around the fitted curve that holds the true curve 95 times in 100
- **extrapolation**: predicting outside the range of the data
- **Monte Carlo**: estimating a result by repeating a calculation with many random draws
- **coverage**: the fraction of repeated experiments whose interval contains the truth; a correct 95 percent interval has coverage near 0.95
- **residual**: measured value minus fitted value

## Finish
1. Do the three coding tasks in [exercises.md](exercises.md).
2. Run `python start.py 3` again after your changes. It ends with the checkpoint; when it prints `PASS`, you are done. (Checkpoint only: `python start.py check 3`.)

Next: [Session 4: Fit a curved Arrhenius plot](../session-04/README.md).
