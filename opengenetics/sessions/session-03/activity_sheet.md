# Activity sheet: opengenetics, Session 3: Wright-Fisher simulation: drift, selection and mutation

Name: ____________________   Date: ____________

**Objectives**

- Simulate allele frequencies in a finite population with a seeded generator.
- Show that small populations drift faster, that fixation probability equals the start frequency, and that heterozygosity decays by (1 - 1/(2N)) per generation.
- Add selection and mutation using stated update formulas, and validate against closed forms.
- Explain the failure case: a beneficial allele lost by chance in a tiny population.
- Size a conservation population from the heterozygosity formula and check it by simulation.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
(a) With s = 0.10 haploid-like selection and p = 0.10, find p' after one generation. (b) For N = 20 and p_0 = 0.5, find the expected heterozygosity after 20 generations of drift, and check it with the simulation.

1. ______________________________  (hint: (a) p' = p (1 + s) / (1 + s p) = 0.10 x 1.10 / (1 + 0.01) = 0.11 / 1.0...)
2. ______________________________  (hint: (b) H_0 = 2 x 0.5 x 0.5 = 0.5. The factor per generation is 1 - 1/40 =...)
3. ______________________________  (hint: After 20 generations: 0.5 x 0.975^20 = 0.5 x 0.6027 = 0.3013....)
4. ______________________________  (hint: Simulation: average 2pq over 20000 seeded populations after 20 generat...)
5. ______________________________  (hint: The two agree to three decimal places, as expected for a large number ...)

Final answer: ____________________

## Questions
**A. Conceptual.** A helpful allele is lost in a very small population even though selection favours it. Does this mean selection did not work? Explain.

Answer: ______________________________________________


**B. Numerical.** A population has N = 50 and a neutral allele. What fraction of heterozygosity is expected after 10 generations? Check the units and sanity.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the N = 10 and N = 5000 panels of the selection figure, what do the grey paths and the dashed curve tell you? What is the spread of p after 20 generations at N = 10 and N = 1000?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: what is the smallest N (diploid individuals) that keeps at least 90 percent of the heterozygosity for 50 generations, and how could you check it? Name two reasons the real number would be larger.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
