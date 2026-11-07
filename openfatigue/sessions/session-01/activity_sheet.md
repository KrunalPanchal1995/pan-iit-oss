# Activity sheet: openfatigue, Session 1: Repeated loads break what one load cannot

Name: ____________________   Date: ____________

**Objectives**

- Explain why a part can fail under a repeated stress that is below its one-pull strength.
- Read a cyclic stress wave: amplitude, range, mean and cycle.
- Use the S-N relation S_a = A N^b to turn a stress amplitude into a number of cycles and a running time.
- Say what the endurance limit means for a steel part.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A steel bar (S_u = 600 MPa, S_e = 300 MPa, so A = 972 MPa and b = -0.085) is loaded with a fully reversed amplitude of 400 MPa at 10 Hz. How many cycles does it survive and for how long does it run?

1. ______________________________  (hint: Check the model applies: 400 MPa is above S_e = 300 MPa, so the life i...)
2. ______________________________  (hint: N = (S_a / A)^(1/b) = (400 / 972)^(1 / -0.0851). Here 400 / 972 = 0.41...)
3. ______________________________  (hint: log10 N = -0.3856 x -11.75 = 4.53, so N = 10^4.53 = 34,000 cycles (34,...)
4. ______________________________  (hint: Running time = N / f = 34,017 / 10 = 3,402 s = 56.7 minutes....)
5. ______________________________  (hint: Sanity check: 400 MPa lies between the 540 MPa at 1000 cycles and the ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can a part break under a repeated stress that is smaller than the stress needed to break it in one pull? What does the part 'remember' from one cycle to the next?

Answer: ______________________________________________


**B. Numerical.** The same steel is loaded at an amplitude of 350 MPa and 20 Hz. Find the number of cycles to failure and the running time in hours. Check that the answer is sensible.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the S-N graph, the amplitude is raised from 400 MPa to 500 MPa, a rise of 25 percent. By what factor does the life fall? What does the steep curve tell a designer?

Answer: ______________________________________________


**D. Design and optimisation challenge.** A rotating bar sees an amplitude of 450 MPa. It must run 8 hours a day at 10 Hz for 30 days. (a) How many cycles is that? (b) How long does it last at 450 MPa? (c) In bending, stress goes as 1/d^3 (d = diameter). By what factor must the diameter grow to bring the stress down to the endurance limit?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
