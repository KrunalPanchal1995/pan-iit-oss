# What you are building toward

A genetic search starts from random formulas and tries to explain noisy pendulum measurements. Candidate curves flicker over the data, each generation a little closer. On the right, the Pareto front of complexity against error grows downwards until it reaches the noise floor, and at the end the equation is revealed: the period grows like the square root of the length. Your goal over the coming sessions: build a search that finds such a law, then make it handle many inputs, awkward constants and uneven noise.

![Target: a genetic search rediscovers the pendulum law while the Pareto front grows](media/target.gif)

*Target: a genetic search rediscovers the pendulum law while the Pareto front grows*

![Target, final frame: the discovered formula and its place on the Pareto front](media/target_still.png)

*Target, final frame: the discovered formula and its place on the Pareto front*

![Residuals: the discovered formula leaves only noise, the simpler rival leaves a curve](media/residuals.png)

*Residuals: the discovered formula leaves only noise, the simpler rival leaves a curve*

These results come from a private reference build. The code is not published; the roadmap shows the path so you can build your own.

Live links:

- [Math Visual Studio: regression and fitting (Atlas S26)](https://krunalpanchal1995.github.io/studio/#atlas?ch=S26&ex=1)
- [Math Visual Studio: the Studio home](https://krunalpanchal1995.github.io/studio/)
