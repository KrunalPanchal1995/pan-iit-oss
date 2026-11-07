# Roadmap: the path to the openfloat Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Other number formats

**You will learn:** How 16-bit and 32-bit floats and fixed-point numbers divide their bits, and what that does to range and precision.

**You will build:** A decoder that works for any width of sign, exponent and fraction fields.

**Checkpoint (not met by the shipped code):** Your decoder reproduces NumPy's value for all 65,536 half-precision bit patterns (the shipped `decode` handles only 64-bit numbers).

**Difficulty:** intermediate

## Session 5: Neumaier summation and bad orderings

**You will learn:** Why Kahan summation can fail when a term is larger than the running sum, and how a small change repairs it.

**You will build:** A compensated sum that is robust to term order.

**Checkpoint (not met by the shipped code):** sum of [1, 1e100, 1, -1e100] returns 2.0 (the shipped Kahan sum returns 0.0).

**Difficulty:** intermediate

## Session 6: Interval arithmetic

**You will learn:** Computing a guaranteed range for a result by rounding every operation outwards.

**You will build:** A small interval class for + - * / and sqrt with outward rounding.

**Checkpoint (not met by the shipped code):** For the textbook small root of x^2 - 1e6 x + 1 your interval contains the true value 1.000000000001e-6 and its relative width exceeds 1e-6, while the stable formula's interval has relative width below 1e-14 (the shipped code only measures error, it gives no guarantee).

**Difficulty:** advanced

## Session 7: Conditioning of a linear system

**You will learn:** Why some problems are sensitive to tiny input changes even with a perfect algorithm, measured by the condition number.

**You will build:** A study of Hilbert matrix systems of growing size.

**Checkpoint (not met by the shipped code):** Predicted digits lost, from the condition number times 2^-53, within 2 digits of the measured loss for sizes 4 to 10 (the shipped code has no linear solver).

**Difficulty:** advanced

## Session 8: Count ticks as integers

**You will learn:** How an integer tick counter removes the accumulation that the chopped-0.1 clock suffers.

**You will build:** A clock model that stores whole ticks and converts to seconds only on reading.

**Checkpoint (not met by the shipped code):** Clock error below 1e-8 s after 1000 hours (the shipped chopped-register model gives 3.43 s).

**Difficulty:** intermediate

## The final step

Combine the milestones: a small numerics toolkit that decodes any float format, sums robustly, reports guaranteed error intervals and shows the three Target panels live. If your result looks like the Target animation, open a pull request and tell us how you did it.
