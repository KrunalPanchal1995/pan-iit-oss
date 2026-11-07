# Activity sheet: openvfx, Session 1: One matrix moves a whole arm

Name: ____________________   Date: ____________

**Objectives**

- Explain what a rotation matrix does to a point.
- Use R @ p to compute where a point lands, by hand and in Python.
- Show that a rotation never changes length or area.
- Read a graph of hand x and y against angle.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Where does the hand end up after the arm (length 1, pointing along x) is turned by 30 degrees? Check that the length is still 1.

1. ______________________________  (hint: The hand starts at (1, 0). For 30 degrees, cos = 0.866 and sin = 0.500...)
2. ______________________________  (hint: New x = 0.866 * 1 - 0.500 * 0 = 0.866....)
3. ______________________________  (hint: New y = 0.500 * 1 + 0.866 * 0 = 0.500....)
4. ______________________________  (hint: Length = sqrt(0.866^2 + 0.500^2) = sqrt(0.750 + 0.250) = sqrt(1.000) =...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can a rotation never stretch the arm? What would a matrix that stretched the arm have to look like?

Answer: ______________________________________________


**B. Numerical.** Rotate the point (2, 0) by 90 degrees counter-clockwise. Where does it land? Check its distance from the origin.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the graph of hand x and y against angle, at which angle do the two curves cross, and where is the hand then?

Answer: ______________________________________________


**D. Design and optimisation challenge.** An animation needs the hand to swing from pointing right to pointing straight up in exactly 3 equal steps (frames). Choose the angle for each frame and list the hand position in each.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
