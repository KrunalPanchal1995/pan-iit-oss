# Roadmap: the path to the openqmintro Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: From the infinite box to the finite well

**You will learn:** Why a real trap has walls of finite height, why the wave function leaks into the wall, and why the number of bound levels is finite.

**You will build:** Solve for the bound-state energies of a square well of finite depth by finding the roots of the matching conditions (or by a numerical eigenvalue solver).

**Checkpoint (not met by the shipped code):** As the well depth goes to infinity the energies approach the box energies of Session 2, and for any finite depth every level lies below its box value.

**Difficulty:** intermediate

## Session 5: A wave packet in time

**You will learn:** How a bump made of many energies moves and spreads, and how the time-dependent Schrodinger equation can be stepped forward numerically.

**You will build:** A split-step or Crank-Nicolson solver that sends a Gaussian wave packet at a barrier and records the reflected and transmitted probabilities.

**Checkpoint (not met by the shipped code):** The total probability stays 1 to within 1e-6 over the whole run, and for a wide packet the transmitted fraction agrees with the Session 3 formula at the mean energy.

**Difficulty:** advanced

## Session 6: The harmonic oscillator and molecular vibrations

**You will learn:** Why the energy levels of a mass on a spring are equally spaced, and how this explains the infrared spectra of molecules.

**You will build:** Numerical energy levels for the potential V = 1/2 k x^2 and the wavelength of the photon emitted in a jump between neighbouring levels for a diatomic molecule.

**Checkpoint (not met by the shipped code):** The lowest levels agree with E_n = (n + 1/2) hbar omega to within 1 percent, and the spacing is the same between all neighbouring levels.

**Difficulty:** intermediate

## Session 7: The hydrogen atom

**You will learn:** How an electron bound by the pull of a nucleus has the energies -13.6 eV / n^2, and why that gives the spectral lines of hydrogen.

**You will build:** A numerical solution of the radial equation and the wavelengths of the Balmer lines.

**Checkpoint (not met by the shipped code):** The first three levels are within 1 percent of -13.6, -3.40 and -1.51 eV, and the first Balmer line is near 656 nm.

**Difficulty:** advanced

## Session 8: Spin measurements in different directions

**You will learn:** How a measurement along one direction changes the state so that a later measurement along another direction becomes random.

**You will build:** Extend the two-state model of Session 1 to sequences of spin measurements along chosen angles, with the probabilities of each outcome.

**Checkpoint (not met by the shipped code):** For a measurement along an axis at angle theta after one along the first axis, the probability of the same outcome is cos^2(theta / 2), and three measurements at 0, 90 and 0 degrees give the outcome 'up' a quarter of the time.

**Difficulty:** intermediate
