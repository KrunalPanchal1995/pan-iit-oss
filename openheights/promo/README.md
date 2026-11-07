# What you are building toward

An observer walks away from a 30 m tower and reads a phone angle at every stop. On the left, the sight lines fan out from each stop to the top. On the right, the height estimate from all readings so far wobbles at first and then settles on the true height, inside a shrinking error band: it ends at 29.95 m with a 2-sigma band of 0.15 m. Stops far from the tower count less, because their error is larger. Your goal over the coming sessions: build that estimator yourself and report a height with an honest uncertainty.

![Target: walking away from a tower, the weighted height estimate converges inside an error band](media/target.gif)

*Target: walking away from a tower, the weighted height estimate converges inside an error band*

![Target, last frame: 29.95 m with a 2-sigma band of 0.15 m](media/target_still.png)

*Target, last frame: 29.95 m with a 2-sigma band of 0.15 m*

![Every stop has its own error; the error is smallest near 45 degrees](media/stop_errors.png)

*Every stop has its own error; the error is smallest near 45 degrees*

These results come from a private reference build. The code is not published; the roadmap shows the path so you can build your own.

Live links:

- [Math Visual Studio: analytic geometry and curves (Atlas S05)](https://krunalpanchal1995.github.io/studio/#atlas?ch=S05&ex=1)
- [Math Visual Studio: open the studio (trigonometry chapter S04 has no live examples yet)](https://krunalpanchal1995.github.io/studio/)
