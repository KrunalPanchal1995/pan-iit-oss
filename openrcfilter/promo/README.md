# What you are building toward

An animated Bode plot sweeps a filter's cutoff from 60 Hz down to 1.5 Hz and back. On one side the gain curve (a second-order filter against a first-order one) slides along the frequency axis with the 50 Hz hum marked on it; on the other side a noisy sensor trace (a slow wave plus hum) is turned into a clean wave by that very filter, and the delay it costs is marked with an arrow and a number in milliseconds. Your goal over the coming sessions: build that cutoff-versus-delay picture yourself, from a notch filter to zero-phase filtering.

![Target: a Bode plot sweeping a cutoff while the filtered sensor signal shows its delay](media/target.gif)

*Target: a Bode plot sweeping a cutoff while the filtered sensor signal shows its delay*

- [Aliasing: a frequency sweep folding back below Nyquist (video)](media/alias_sweep.mp4)

![Math Visual Studio: the aliasing example](media/aliasing_studio.png)

*Math Visual Studio: the aliasing example*

These results come from a private reference build. The code is not published; the roadmap shows the path so you can build your own.

Live links:

- [Math Visual Studio: Laplace transforms and transfer functions (Atlas S17)](https://krunalpanchal1995.github.io/studio/#atlas?ch=S17&ex=1)
- [Math Visual Studio: Fourier analysis (Atlas S19)](https://krunalpanchal1995.github.io/studio/#atlas?ch=S19&ex=1)
