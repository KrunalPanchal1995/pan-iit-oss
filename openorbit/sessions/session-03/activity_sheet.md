# Activity sheet: openorbit, Session 3: Plan a transfer orbit and check it

Name: ____________________   Date: ____________

**Objectives**

- Compute the two burns and the flight time of a Hohmann transfer between circular orbits.
- Verify the transfer by integrating the trajectory numerically from the first burn.
- Compare Hohmann with a bi-elliptic transfer and find where the cheaper choice changes.
- Price a plane change and a phasing manoeuvre, and show where the instant-burn model fails.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Plan the Hohmann transfer from a circular orbit of radius 6778 km (a low orbit) to the geostationary radius 42164 km. Find both burns, the total, and the flight time, and verify them by integration.

1. ______________________________  (hint: a_t = (6778 + 42164) / 2 = 24471 km....)
2. ______________________________  (hint: Speeds: circular at 6778 km is 7.669 km/s, the transfer's perigee spee...)
3. ______________________________  (hint: dv1 = 10.066 - 7.669 = 2.398 km/s. dv2 = 3.075 - 1.618 = 1.457 km/s. T...)
4. ______________________________  (hint: Transfer time = half the period of the ellipse = 5.291 hours....)
5. ______________________________  (hint: Numerical check: start at 6778 km, speed 10.066 km/s, integrate for 5....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why are both Hohmann burns along the velocity (tangential), and why is the flight time half an ellipse period?

Answer: ______________________________________________


**B. Numerical.** Find the Hohmann burns and the transfer time between the circular orbits of radius 6778 km and 7178 km (a small step, for example before docking).

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the bi-elliptic graph, for which radius ratios is Hohmann cheaper, and what does the 11.94 crossing mean for LEO to GEO?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a satellite is launched into a low orbit inclined 28.5 degrees and must be put into the equatorial geostationary orbit. Compare three plans for the plane change: in the low orbit, at the geostationary orbit, and combined with the second burn at the transfer apogee. Which would you choose and what is the trade-off?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
