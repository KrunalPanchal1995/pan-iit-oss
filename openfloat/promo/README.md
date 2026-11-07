# What you are building toward

One animated tour with three linked panels. Top: a window of fixed width 8 on the real 64-bit number line; as the magnitude climbs from 1 to about 1e17 the stored numbers thin out until a single one is left. Bottom left: the error of adding 0.1 up to ten million times, a plain accumulator against a compensated one and the worst-case bound. Bottom right: the Patriot-style clock counter, drifting to about 0.34 s late over 100 hours. Your goal over the coming sessions: build all three panels yourself, then extend them.

![Target: number-line gaps, error growth and Patriot clock drift in one tour](media/target.gif)

*Target: number-line gaps, error growth and Patriot clock drift in one tour*

![A still from the Target: gap of 2 near 1e16, summation error and clock drift](media/target_still.png)

*A still from the Target: gap of 2 near 1e16, summation error and clock drift*

![Error of adding 0.1 up to ten million times: plain versus compensated versus the bound](media/error_growth.png)

*Error of adding 0.1 up to ten million times: plain versus compensated versus the bound*

These results come from a private reference build. The code is not published; the roadmap shows the path so you can build your own.

Live links:

- [Math Visual Studio: floating point, error and conditioning (Atlas S28)](https://krunalpanchal1995.github.io/studio/#atlas?ch=S28&ex=1)
- [Math Visual Studio: the best step size for a difference quotient (Atlas S28, example 2)](https://krunalpanchal1995.github.io/studio/#atlas?ch=S28&ex=2)
