# Project form (Hello FOSS)

**Project name:** opennowcast

**Short description:** Learn rain nowcasting from scratch: advect radar fields, estimate motion, score the forecast. 3 short sessions.

**Full description:** opennowcast is a beginner-friendly learning repo about nowcasting, the art of forecasting rain for the next hour or two from radar pictures. Session 1 starts with one rain cell that drifts with the wind and asks when it reaches your town. Session 2 treats the radar picture as a 100 x 100 grid, shifts it by whole and fractional pixels, estimates the motion between two frames, and scores a persistence forecast against an advection forecast with RMSE, CSI and the fractions skill score. Session 3 adds local motion vectors (two regions moving differently), growing and fading cells, the blur caused by repeated interpolation, an ensemble that turns uncertainty into probabilities, and the cases where advection fails, ending in a mini-project. Every session has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. All data are synthetic. This is a teaching model, not a weather warning system: always follow official forecasts. The repo is intentionally incomplete: a Target animation and a roadmap show how the community can take it further.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/opennowcast
