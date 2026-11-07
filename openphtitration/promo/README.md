# What you are building toward

An animated burette drips 0.1 mol/L base into a flask of diluted vinegar. The flask turns pink as the pH passes the phenolphthalein range, the measured pH points (with realistic noise) appear one by one, and below them the slope of the curve spikes at the equivalence point. The final frame reads the peak and prints the vinegar concentration, about 0.83 mol/L or 5 g per 100 mL. Your goal over the coming sessions: build the numerical engine and the analysis behind that animation.

![Target: a burette titration of vinegar with a live pH curve and a derivative peak at the equivalence point](media/target.gif)

*Target: a burette titration of vinegar with a live pH curve and a derivative peak at the equivalence point*

![Target, final frame: the derivative peak gives the equivalence volume and the vinegar concentration](media/target_still.png)

*Target, final frame: the derivative peak gives the equivalence volume and the vinegar concentration*

![Target analysis: more dilute acids give a smaller jump; 200 noisy runs show how well the peak is located](media/target_summary.png)

*Target analysis: more dilute acids give a smaller jump; 200 noisy runs show how well the peak is located*

These results come from a private reference build. The code is not published; the roadmap shows the path so you can build your own.

Live links:

- [Math Visual Studio: root finding (Atlas S29)](https://krunalpanchal1995.github.io/studio/#atlas?ch=S29&ex=1)
- [Math Visual Studio: numerical differentiation (Atlas S30)](https://krunalpanchal1995.github.io/studio/#atlas?ch=S30&ex=1)
