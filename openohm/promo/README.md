# What you are building toward

A circuit solver view sweeps a design space. On the left, a 12 V supply drives a series-parallel resistor network and each part glows red as it nears its 0.25 W rating. In the middle, a heat map of current against supply voltage and total resistance shows the safe region, with the operating point moving through it. On the right, Newton's method walks down an LED load line to the operating point, step by step. Your goal over the coming sessions: build the solver behind it, then extend it to any network and any limit.

![Target: a circuit solver sweeping the design space (network, safe-region heat map, Newton on an LED)](media/target.gif)

*Target: a circuit solver sweeping the design space (network, safe-region heat map, Newton on an LED)*

![The design space: current and power limits carve out a safe region](media/design_space.png)

*The design space: current and power limits carve out a safe region*

![Newton's method walking down to an LED operating point](media/led_newton.png)

*Newton's method walking down to an LED operating point*

These results come from a private reference build. The code is not published; the roadmap shows the path so you can build your own.

Live links:

- [Math Visual Studio (open the Studio and explore curves and functions)](https://krunalpanchal1995.github.io/studio/)
- [Math Visual Studio: functions and their transformations (Atlas S03)](https://krunalpanchal1995.github.io/studio/#atlas?ch=S03&ex=1)
