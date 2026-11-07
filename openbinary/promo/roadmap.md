# Roadmap: the path to the openbinary Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 6: A saturating adder

**You will learn:** Clamping instead of wrapping, as used in audio and image processing.

**You will build:** An 8-bit adder-subtractor that returns the nearest extreme on overflow.

**Checkpoint (not met by the shipped code):** 100 + 100 gives 127 and -100 + -100 gives -128 for 8-bit inputs (the shipped adder wraps 100 + 100 to -56), and all 65536 pairs match a clamped Python sum.

**Difficulty:** intermediate

## Session 7: A counter that remembers

**You will learn:** Memory from gates: a latch built from two cross-coupled NAND gates, and a clocked counter.

**You will build:** A 4-bit counter driven by clock ticks.

**Checkpoint (not met by the shipped code):** After 20 clock ticks from zero the counter shows 4, and it wraps from 15 to 0 (the shipped circuits have no memory).

**Difficulty:** advanced

## Session 8: An ALU with flags and a decoder

**You will learn:** Zero, negative, carry and overflow flags, and a seven-segment display driver built from gates.

**You will build:** An 8-bit ALU with four operations and flags, and a decoder lighting the right segments for each digit.

**Checkpoint (not met by the shipped code):** All 65536 input pairs match Python for every operation, and the decoder lights the segments of all ten digits correctly from gates alone (the shipped decoder is a lookup table).

**Difficulty:** advanced

## The final step

Combine the milestones: an 8-bit processor core that adds, subtracts, multiplies and counts, with a fast carry. If your result behaves like the Target animation, open a pull request and tell us how you did it.
