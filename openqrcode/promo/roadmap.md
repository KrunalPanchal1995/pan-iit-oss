# Roadmap: the path to the openqrcode Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Survive a coffee-stain blob

**You will learn:** Why a 2D blob is harder than a scratch along reading order, and how to spread codewords over the plane.

**You will build:** A 2D interleaving layout for the toy code and a test harness for square blobs.

**Checkpoint (not met by the shipped code):** Every placement of a 4 by 4 blob on the data squares is repaired (the shipped layout repairs only 19 of the 81 placements).

**Difficulty:** intermediate

## Session 5: Know when it failed

**You will learn:** Extended Hamming codes that detect two flips, and checksums such as CRC.

**You will build:** A decoder that marks unreliable blocks instead of guessing, plus a stronger checksum.

**Checkpoint (not met by the shipped code):** Wrong text accepted in fewer than 1 attempt in 10,000 at 5 percent random damage (the shipped code accepts about 1 in 800).

**Difficulty:** intermediate

## Session 6: Find the code in any orientation

**You will learn:** How finder patterns give position and orientation.

**You will build:** A reader that finds the three finder patterns and rotates the grid to upright before decoding.

**Checkpoint (not met by the shipped code):** Correct text for all four 90 degree rotations (the shipped reader handles only the upright one).

**Difficulty:** intermediate

## Session 7: Symbols instead of bits: Reed-Solomon

**You will learn:** Finite fields, polynomials over them, and why whole symbols are repaired at once.

**You will build:** A small Reed-Solomon encoder and decoder over GF(16) or GF(256).

**Checkpoint (not met by the shipped code):** Any 4 completely wrong bytes in a 16-byte block (8 data + 8 parity) are repaired; the shipped code is guaranteed to repair at most one flipped bit per 7.

**Difficulty:** advanced

## Session 8: Read a photograph

**You will learn:** Thresholding, perspective correction and sampling the grid from an image.

**You will build:** A reader that takes a tilted greyscale picture of a code and recovers the message.

**Checkpoint (not met by the shipped code):** Message recovered from pictures with 15 degrees of tilt and added Gaussian noise.

**Difficulty:** advanced

## The final step

Combine the milestones: a reader that finds the code in any orientation, survives a stain over a fifth of its squares and tells you honestly when it cannot read it. If your result looks like the Target animation, open a pull request and tell us how you did it.
