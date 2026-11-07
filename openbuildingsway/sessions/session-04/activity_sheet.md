# Activity sheet: openbuildingsway, Session 4: The response-spectrum shortcut

Name: ____________________   Date: ____________

**Objectives**

- Read a response spectrum and turn it into the base shear of one mode, V = M* S_a.
- Combine the modes with SRSS and compare with the plain sum and the full time history.
- See that the shortcut is exact for one mode, close for a well-separated frame and less reliable for very soft frames.
- Judge from a table of errors when the shortcut can be used for screening.

## Before you start: predict
In your own words, if you stiffen a building (shorter period), do you expect the base shear from an earthquake to go down or up? Why?

______________________________________________________________

## Worked example (fill in as you go)
The two-storey building of Session 3 (m = 200 000 kg, k = 3.5e8 N/m) has T1 = 0.2430 s and T2 = 0.0928 s and effective mass shares 94.72 and 5.28 percent of the total mass 400 000 kg. A made-up spectrum gives S_a = 2.0 m/s^2 at T1 and 1.0 m/s^2 at T2. Find the modal base shears, the SRSS and the plain sum.

1. ______________________________  (hint: M* = share x total mass)
2. ______________________________  (hint: V = M* S_a, in newtons)
3. ______________________________  (hint: SRSS = sqrt(V1^2 + V2^2))
4. ______________________________  (hint: plain sum = V1 + V2)
5. ______________________________  (hint: how much bigger is the sum than the SRSS, in percent?)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the shortcut combine the modes with the square root of the sum of squares rather than adding the modal peaks, and when could SRSS be too small?

Answer: ______________________________________________


**B. Numerical.** A building of total mass 2.0e6 kg has a first mode that carries 75 percent of the mass and a second that carries 20 percent. The spectrum gives S_a = 2.5 m/s^2 at the first period and 3.5 m/s^2 at the second. Find the modal base shears, the SRSS and the plain sum.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the spectrum figure the first mode (T = 1.00 s) sits at S_a / PGA = 2.64, in a dip, while the peak of 4.4 is at 0.72 s. A retrofit moves the first period to 0.71 s. What does the spectrum predict for the first-mode base shear, and what does that say about stiffening?

Answer: ______________________________________________


**D. Design and optimisation challenge.** The error of the 3-mode SRSS shortcut is +22.1, +6.1, +2.5, +0.5, -1.6, -3.4, -4.0, -2.8, -2.1, -3.2, -4.8, -4.7, -4.6, -4.1 and -5.4 percent for storey stiffnesses of 100, 200, ..., 1500 MN/m. The screening limit is 5 percent. For which options can the shortcut be used, and which failures are on the unsafe side?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
