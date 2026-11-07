# Activity sheet: openseismo, Session 2: Three circles pin down the epicentre

Name: ____________________   Date: ____________

**Objectives**

- Explain where vp/vs = sqrt(3) comes from for a Poisson's ratio of 0.25.
- Compute distance from the S-P time, d = (ts - tp) vp vs / (vp - vs).
- Find an epicentre from three stations by solving a linear system.
- Explain why two stations are not enough and why three stations on one line fail.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Stations A (0, 0), B (100, 0), C (40, 90) km record a quake at (60, 35) km. Compute the distances and S-P gaps, then recover the epicentre from the gaps.

1. ______________________________  (hint: Distances: rA = sqrt(60^2 + 35^2) = 69.46 km, rB = sqrt(40^2 + 35^2) =...)
2. ______________________________  (hint: Gaps: rA / 8.4 = 8.27 s, rB / 8.4 = 6.33 s, rC / 8.4 = 6.97 s. Going b...)
3. ______________________________  (hint: Line from A and B: 200 x = rA^2 - rB^2 + 100^2 = 12000, so x = 60 km....)
4. ______________________________  (hint: Line from A and C: 80 x + 180 y = rA^2 - rC^2 + 40^2 + 90^2 = 11100. W...)
5. ______________________________  (hint: The epicentre is (60, 35) km. Check: the mirror point (60, -35) is 126...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why do two stations leave two possible epicentres, and why does a third station fix this? Why do three stations on one straight line still fail?

Answer: ______________________________________________


**B. Numerical.** Compute the ratio vp/vs for Poisson's ratio 0.25 and compare it with 6.0 / 3.5. Which Poisson's ratio gives exactly 6.0 / 3.5?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the app, set the quake to (60, 35) km and add a clock error of +1.0 s at station A. Describe how the black dot moves relative to the red cross. Is the error the same everywhere on the map?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you can place a third station at (50, 0), (100, 90) or (40, 90) next to A (0, 0) and B (100, 0). Which choices let you find an epicentre at (60, 35) km, and which fail? What is the minimum number of stations for an epicentre from S-P times, and why?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
