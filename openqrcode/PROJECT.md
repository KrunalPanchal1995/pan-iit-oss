# Project form (Hello FOSS)

**Project name:** openqrcode

**Short description:** Learn how a damaged QR code can still be read: check digits, Hamming codes and interleaving, in 3 sessions.

**Full description:** openqrcode is a beginner-friendly learning repo about error-correcting codes, the idea that lets a scuffed barcode or QR code still scan. In three short sessions you go from data as black and white squares and the EAN-13 check digit, to parity bits and the Hamming(7,4) code that finds and fixes any single flipped bit, to a toy 2D matrix code that you build yourself, damage with random noise and scratches, and decode, measuring the success rate against a probability formula. Real QR codes use Reed-Solomon codes over GF(256) with four error-correction levels (L, M, Q, H) that restore roughly 7, 15, 25 and 30 percent of the codewords; the toy code here is NOT that, but it shows the same ideas: redundancy, a trade-off with capacity, finder patterns and interleaving. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment), and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openqrcode
