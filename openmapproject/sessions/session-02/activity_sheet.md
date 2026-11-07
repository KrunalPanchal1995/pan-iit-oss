# Activity sheet: openmapproject, Session 2: The Mercator projection and area exaggeration

Name: ____________________   Date: ____________

**Objectives**

- Write the sphere as X, Y, Z equations of latitude and longitude.
- Compute the Mercator coordinates of a point and invert them.
- Explain why Mercator keeps small shapes but inflates areas by 1 / cos^2(latitude).
- Compute true and apparent areas of two regions and find the latitude limit for a given exaggeration.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Find the Mercator position (x, y) of the point at latitude 60 degrees north and longitude 30 degrees east, its area exaggeration, and the apparent size ratio of the two boxes in Section C.

1. ______________________________  (hint: x = R lambda = 6371 x (30 x pi/180) = 6371 x 0.5236 = 3335.8 km....)
2. ______________________________  (hint: y = R ln tan(45 + 30 degrees) = 6371 x ln tan 75 = 6371 x ln 3.7321 = ...)
3. ______________________________  (hint: Area exaggeration = 1 / cos^2 60 = 1 / 0.25 = 4.0, and the length scal...)
4. ______________________________  (hint: Boxes: true areas are 5.47 million km2 (Greenland box) and 56.62 milli...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does Mercator keep the shape of small objects but not their area?

Answer: ______________________________________________


**B. Numerical.** Compute the Mercator coordinates (x, y) in km of the point at latitude 50 degrees north, longitude 10 degrees east, and the area exaggeration there.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the exaggeration curve, at about what latitude does Mercator inflate area by a factor 4, and what is the factor at 80 degrees?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: (1) What latitude limit keeps Mercator's area exaggeration at most 3? (2) Which map property do you need for a world map of population density per square kilometre, for a sea chart, and for a map of the Arctic? Justify each in one line.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
