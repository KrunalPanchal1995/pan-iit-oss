# Activity sheet: opennowcast, Session 2: Translate a field, estimate the motion, score the forecast

Name: ____________________   Date: ____________

**Objectives**

- Shift a 2-D radar field by whole pixels and by fractions of a pixel (bilinear interpolation).
- Show that interpolation conserves total rain but blurs the field, and predict by how much.
- Estimate the shift between two frames by a brute-force search and check it against a known shift.
- Compare persistence and advection forecasts with RMSE, CSI and the fractions skill score.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Two frames show the whole pattern moved (2.4, 1.3) pixels in 5 minutes. What is the wind, how far does the pattern move in 60 minutes, and what is the CSI if a forecast has 80 hits, 10 misses and 10 false alarms?

1. ______________________________  (hint: Wind: u = 2.4 x 12 = 28.8 km/h east and v = 1.3 x 12 = 15.6 km/h north...)
2. ______________________________  (hint: Speed = sqrt(28.8^2 + 15.6^2) = sqrt(829.4 + 243.4) = 32.76 km/h....)
3. ______________________________  (hint: In 60 minutes there are 12 frames, so the pattern moves (2.4 x 12, 1.3...)
4. ______________________________  (hint: CSI = hits / (hits + misses + false alarms) = 80 / (80 + 10 + 10) = 0....)
5. ______________________________  (hint: Check with the code: `estimate_shift` returns about (2.4, 1.3) and the...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does shifting a field by half a pixel make the peak lower, even though no rain is lost?

Answer: ______________________________________________


**B. Numerical.** The estimated shift is (1.5, 0.5) pixels per 5 minutes. Give the wind components and speed in km/h and the displacement after 60 minutes.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the skill-against-lead-time graph for a translating field, which method wins and why does the other curve fall? Quote the 60 minute CSI values.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a cell has a 5 mm/h radius of 9.47 km. You want a CSI of at least 0.5 at 60 minutes. How accurate must the wind be? What if you only need 30 minutes?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
