"""Session 3 (Level 3): an automatic equation balancer (null space), conservation checks and a reactor sweep.

Run:  python start.py 3
Educational model with textbook atomic masses and ideal complete reactions; not a plant design tool.
"""
# %% [markdown]
# # Session 3: let linear algebra balance the equation
# **A. Real-world problem.** A fertiliser plant turns nitrogen and hydrogen into ammonia. Before
# buying gas the engineer must know the exact ratio of reagents and how much hydrogen one tonne of
# ammonia needs. Balancing by trial does not scale to 20 species. Atom conservation is a set of
# linear equations, and the coefficients are the null space of the element-by-species matrix.
#
# **Plan.** (1) build the matrix A (rows are elements, columns are species), (2) find the null
# space with numpy, (3) turn the numbers into whole numbers with fractions.Fraction,
# (4) validate on known reactions and check mass and charge, (5) sweep feed ratios of a reactor,
# (6) test the sensitivity to the molar-mass table, (7) meet the cases that fail.

# %%
import math
import pathlib
import re
from fractions import Fraction

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

ATOMIC_MASS = {"H": 1.008, "C": 12.011, "N": 14.007, "O": 15.999, "Na": 22.990,
               "Cl": 35.45, "S": 32.06, "Ca": 40.078, "Fe": 55.845, "Al": 26.982,
               "Mn": 54.938, "Cu": 63.546, "Ag": 107.868}


# %% [markdown]
# ## Step 1: species and the matrix A
# A species is written like H2O, Fe^3+ or MnO4^- (the part after ^ is the charge). For every
# element we write one row: atoms in each species (reactants positive, products negative).
# If any species is charged we add a charge row. A column vector c of coefficients conserves
# everything exactly when A c = 0.

# %%
def parse_species(species):
    """Return ({element: count}, charge) for 'H2O', 'Ca(OH)2', 'Fe^3+', 'MnO4^-'."""
    formula, _, chg = species.partition("^")
    charge = 0
    if chg:
        m = re.fullmatch(r"(\d*)([+-])", chg)
        if not m:
            raise ValueError(f"cannot read charge in {species!r}")
        charge = (int(m.group(1)) if m.group(1) else 1) * (1 if m.group(2) == "+" else -1)
    tokens = re.findall(r"[A-Z][a-z]?|\d+|\(|\)", formula)
    if not formula or "".join(tokens) != formula or tokens[0].isdigit():
        raise ValueError(f"cannot read formula {species!r}")
    stack, i = [{}], 0
    while i < len(tokens):
        t = tokens[i]
        if t == "(":
            stack.append({})
        elif t == ")":
            if len(stack) == 1:
                raise ValueError(f"unbalanced bracket in {species!r}")
            group = stack.pop()
            mult = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                mult, i = int(tokens[i + 1]), i + 1
            for el, n in group.items():
                stack[-1][el] = stack[-1].get(el, 0) + n * mult
        elif t.isdigit():
            raise ValueError(f"misplaced number in {species!r}")
        else:
            n = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                n, i = int(tokens[i + 1]), i + 1
            stack[-1][t] = stack[-1].get(t, 0) + n
        i += 1
    if len(stack) != 1:
        raise ValueError(f"unbalanced bracket in {species!r}")
    return stack[0], charge


def build_matrix(reactants, products, use_charge=True):
    """Element-by-species matrix (rows: elements, then charge); products carry a minus sign."""
    species = list(reactants) + list(products)
    parsed = [parse_species(s) for s in species]
    elements = sorted({el for atoms, _ in parsed for el in atoms})
    A = np.zeros((len(elements), len(species)))
    for j, (atoms, _) in enumerate(parsed):
        sign = 1.0 if j < len(reactants) else -1.0
        for el, n in atoms.items():
            A[elements.index(el), j] = sign * n
    if use_charge and any(q != 0 for _, q in parsed):
        row = [(1.0 if j < len(reactants) else -1.0) * q for j, (_, q) in enumerate(parsed)]
        A = np.vstack([A, row])
        elements = elements + ["charge"]
    return A, elements


# %% [markdown]
# ## Step 2: the null space with numpy
# The singular value decomposition A = U S V^T lists, in S, how strongly A acts in each
# direction. Rows of V^T whose singular value is (numerically) zero span the null space.
# The nullity (its dimension) is the number of independent ways to balance.

# %%
def null_space(A, tol=1e-9):
    """Return (basis as columns, nullity). Uses the SVD; tol decides which singular values are zero."""
    _, s, vt = np.linalg.svd(A)
    rank = int((s > tol * max(1.0, s[0] if len(s) else 1.0)).sum())
    return vt[rank:].T, A.shape[1] - rank


# %% [markdown]
# ## Step 3: from decimals to whole numbers
# A unit-length null vector such as (0.26, 0.77, 0.51) is not a recipe. Divide by its smallest
# entry, find the nearest simple fraction with Fraction.limit_denominator, multiply by the
# common denominator, divide by the greatest common divisor, and make the signs positive.
# The result is then verified with exact integer arithmetic.

# %%
def to_integers(vec, max_den=1000):
    v = np.asarray(vec, dtype=float)
    nz = np.abs(v) > 1e-9
    if not nz.any():
        raise ValueError("zero vector")
    v = v / np.min(np.abs(v[nz]))
    fr = [Fraction(float(x)).limit_denominator(max_den) for x in v]
    lcm = 1
    for f in fr:
        lcm = lcm * f.denominator // math.gcd(lcm, f.denominator)
    ints = [int(f * lcm) for f in fr]
    g = 0
    for k in ints:
        g = math.gcd(g, abs(k))
    ints = [k // g for k in ints]
    first = next(k for k in ints if k != 0)
    return [k if first > 0 else -k for k in ints]


def canonical_basis(basis):
    """Rewrite a null-space basis so that the last k species are free (identity block), then make it integer.

    For H2 + O2 -> H2O + H2O2 this returns the two elementary reactions (2, 1, 2, 0) and (1, 1, 0, 1)."""
    n, k = basis.shape
    piv = []
    for row in range(n - 1, -1, -1):
        if np.linalg.matrix_rank(basis[piv + [row], :], tol=1e-9) == len(piv) + 1:
            piv.append(row)
        if len(piv) == k:
            break
    piv.sort()
    return basis @ np.linalg.inv(basis[piv, :])


def balance(reactants, products, use_charge=True):
    """Balance by null space. Returns {'coefs', 'nullity', 'reason', 'basis'}.

    coefs is a list of positive integers (reactants then products) when the solution is unique and
    physical, otherwise None with a reason. basis holds integer null vectors when nullity > 1."""
    A, elements = build_matrix(reactants, products, use_charge)
    basis, k = null_space(A)
    out = {"coefs": None, "nullity": k, "reason": "", "basis": None, "elements": elements}
    if k == 0:
        out["reason"] = "null space is empty: the species cannot conserve every element"
        return out
    if k > 1:
        out["reason"] = f"null space has dimension {k}: the equation is not uniquely balanced"
        canon = canonical_basis(basis)
        out["basis"] = [to_integers(canon[:, j]) for j in range(k)]
        return out
    ints = to_integers(basis[:, 0])
    Ai = np.rint(A).astype(int)
    if np.any(Ai @ np.array(ints) != 0):
        out["reason"] = "rounding failed the exact integer check"
        return out
    if any(c <= 0 for c in ints):
        out["reason"] = "the null vector has zero or negative entries: a species is on the wrong side"
        out["basis"] = [ints]
        return out
    out["coefs"] = ints
    return out


def format_balanced(reactants, products, coefs):
    def one(names, cs):
        return " + ".join((f"{c} " if c != 1 else "") + s for c, s in zip(cs, names))
    n = len(reactants)
    return one(reactants, coefs[:n]) + " -> " + one(products, coefs[n:])


# %% [markdown]
# ## Step 4: validation and conservation checks
# Known answers: water 2, 1, 2; methane 1, 2, 1, 2; Fe2O3 + 2 Al -> Al2O3 + 2 Fe; ammonia 1, 3, 2;
# glucose 1, 6, 6, 6. For any reaction we can also check atoms, charge and mass directly.

# %%
KNOWN = [
    (["H2", "O2"], ["H2O"], [2, 1, 2]),
    (["CH4", "O2"], ["CO2", "H2O"], [1, 2, 1, 2]),
    (["Fe2O3", "Al"], ["Al2O3", "Fe"], [1, 2, 1, 2]),
    (["N2", "H2"], ["NH3"], [1, 3, 2]),
    (["C6H12O6", "O2"], ["CO2", "H2O"], [1, 6, 6, 6]),
]


def conservation(reactants, products, coefs, table=ATOMIC_MASS):
    """Net (left minus right) atoms per element, net charge and net mass in g per mole of reaction."""
    A, elements = build_matrix(reactants, products, use_charge=True)
    c = np.asarray(coefs, dtype=float)
    net = A @ c
    atoms = {el: float(v) for el, v in zip(elements, net) if el != "charge"}
    charge = float(net[elements.index("charge")]) if "charge" in elements else 0.0
    n = len(reactants)
    mass = 0.0
    for j, s in enumerate(list(reactants) + list(products)):
        at, _ = parse_species(s)
        m = sum(table[el] * k for el, k in at.items())
        mass += (1.0 if j < n else -1.0) * coefs[j] * m
    return {"atoms": atoms, "charge": charge, "mass_g": mass}


# %% [markdown]
# ## Step 5: a limiting-reagent reactor and a feed-ratio sweep
# Feed n_N2 = 1 mol and n_H2 = r mol. Extent = min(n_N2 / 1, n_H2 / 3). Below r = 3 hydrogen is
# limiting; above r = 3 nitrogen is limiting and extra hydrogen is wasted. The reaction here is
# complete (100 percent conversion); a real plant recycles unreacted gas.

# %%
def react(coefs_in, feed_mol, coefs_out, conversion=1.0):
    """Ideal reactor. Returns (extent, leftover moles of reactants, moles of products)."""
    extent = conversion * min(n / c for n, c in zip(feed_mol, coefs_in))
    left = [n - c * extent for n, c in zip(feed_mol, coefs_in)]
    return extent, left, [c * extent for c in coefs_out]


def sweep_feed_ratio(ratios, formulas=("N2", "H2", "NH3"), coefs=(1, 3, 2), table=ATOMIC_MASS):
    """For 1 mol N2 and r mol H2 fed: product moles, product mass over feed mass, wasted reagent moles."""
    mm = {f: sum(table[el] * k for el, k in parse_species(f)[0].items()) for f in formulas}
    rows = []
    for r in ratios:
        extent, left, prod = react(coefs[:2], [1.0, r], coefs[2:])
        feed_mass = mm[formulas[0]] + r * mm[formulas[1]]
        rows.append((r, prod[0], prod[0] * mm[formulas[2]] / feed_mass, left[0] + left[1]))
    return np.array(rows)


# %% [markdown]
# ## Step 6: sensitivity to the molar-mass table
# Hydrogen needed per kilogram of ammonia is 1.5 * M(H2) / M(NH3). If an atomic mass in the table
# is wrong by 1 percent, by what percent does the answer change?

# %%
def reagent_mass_kg(product_kg, product, coef_p, reagent, coef_r, table=ATOMIC_MASS, yield_fraction=1.0):
    """kg of reagent needed to make product_kg of product when a fraction `yield_fraction` of the extent is achieved."""
    def mm(f):
        return sum(table[el] * k for el, k in parse_species(f)[0].items())
    n_product = product_kg * 1000.0 / mm(product)
    return n_product * coef_r / coef_p * mm(reagent) / 1000.0 / yield_fraction


def sensitivity(elements=("H", "N"), rel=0.01):
    """Percent change of the hydrogen mass for a rel increase of each atomic mass in `elements`."""
    base = reagent_mass_kg(1000.0, "NH3", 2, "H2", 3)
    out = {}
    for el in elements:
        t = dict(ATOMIC_MASS)
        t[el] = t[el] * (1.0 + rel)
        out[el] = 100.0 * (reagent_mass_kg(1000.0, "NH3", 2, "H2", 3, table=t) / base - 1.0)
    return out


# %% [markdown]
# ## Step 7: see it
# Left: yield and waste against the hydrogen to nitrogen feed ratio. Right: the sensitivity.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    for r, p, c in KNOWN:
        res = balance(r, p)
        print(format_balanced(r, p, res["coefs"]), "| expected", c, "| ok:", res["coefs"] == c)
    print("worked example", conservation(["N2", "H2"], ["NH3"], [1, 3, 2]))
    ion_r, ion_p = ["MnO4^-", "Fe^2+", "H^+"], ["Mn^2+", "Fe^3+", "H2O"]
    print("ionic:", format_balanced(ion_r, ion_p, balance(ion_r, ion_p)["coefs"]),
          "| nullity with charge row", balance(ion_r, ion_p)["nullity"],
          "| without", balance(ion_r, ion_p, use_charge=False)["nullity"])
    print("cannot balance:", balance(["H2", "O2"], ["NaCl"])["reason"])
    two = balance(["H2", "O2"], ["H2O", "H2O2"])
    print("non-unique:", two["reason"], two["basis"])
    print("wrong side:", balance(["H2", "H2O"], ["O2"])["reason"])

    r = np.linspace(0.0, 6.0, 121)
    tab = sweep_feed_ratio(r)
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.8))
    ax[0].plot(tab[:, 0], tab[:, 1], label="NH3 made (mol per mol N2 fed)")
    ax[0].plot(tab[:, 0], tab[:, 3], "--", label="unreacted reagent (mol)")
    ax[0].axvline(3, color="gray", ls=":")
    ax[0].set_xlabel("H2 : N2 feed ratio (mol / mol)")
    ax[0].set_ylabel("moles (mol)")
    ax[0].set_title("Yield stops growing at the 3 : 1 ratio", fontsize=10)
    ax[0].grid(alpha=0.3)
    ax[0].legend(fontsize=8)
    ax[1].plot(tab[:, 0], 100 * tab[:, 2])
    ax[1].axvline(3, color="gray", ls=":")
    ax[1].set_xlabel("H2 : N2 feed ratio (mol / mol)")
    ax[1].set_ylabel("NH3 mass / feed mass (%)")
    ax[1].set_title("Feed is used best at the exact ratio", fontsize=10)
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "feed_ratio_sweep.png", dpi=120)
    best = tab[np.argmax(tab[:, 2])]
    print("best feed ratio %.2f gives %.1f %% of feed mass as NH3" % (best[0], 100 * best[2]))

    sens = sensitivity(("H", "N"))
    rng = np.random.default_rng(0)
    vals = []
    for _ in range(2000):
        t = {k: v * (1 + rng.uniform(-0.01, 0.01)) for k, v in ATOMIC_MASS.items()}
        vals.append(reagent_mass_kg(1000.0, "NH3", 2, "H2", 3, table=t))
    print("H2 for 1 t NH3: %.1f kg; +1%% H mass -> %+.3f %%; +1%% N mass -> %+.3f %%; random +-1%% table: std %.2f kg" % (
        reagent_mass_kg(1000.0, "NH3", 2, "H2", 3), sens["H"], sens["N"], np.std(vals)))
    fig2, ax2 = plt.subplots(figsize=(5, 3.6))
    ax2.bar(list(sens), [sens[k] for k in sens])
    ax2.axhline(0, color="k", lw=0.8)
    ax2.set_xlabel("atomic mass raised by 1 %")
    ax2.set_ylabel("change in hydrogen needed (%)")
    ax2.set_title("Sensitivity of the hydrogen mass", fontsize=10)
    ax2.grid(alpha=0.3, axis="y")
    fig2.tight_layout()
    fig2.savefig(OUT / "mass_table_sensitivity.png", dpi=120)
    h2 = reagent_mass_kg(1000.0, "NH3", 2, "H2", 3)
    n2 = reagent_mass_kg(1000.0, "NH3", 2, "N2", 1)
    print("mini-project: H2 %.1f kg, N2 %.1f kg, sum %.1f kg; at 90 %% yield H2 %.1f kg" % (
        h2, n2, h2 + n2, reagent_mass_kg(1000.0, "NH3", 2, "H2", 3, yield_fraction=0.9)))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
