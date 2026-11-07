"""Session 2 (Level 2): molar mass, moles, limiting reagent, yield and concentration.

Run:  python start.py 2
Educational model with textbook atomic masses; real plants must use certified data and safety review.
"""
# %% [markdown]
# # Session 2: from a balanced equation to grams
# **A. Real-world problem.** A balanced equation counts molecules, but a shop sells kilograms.
# To neutralise a spill of sulphuric acid with limestone you need to know how many kilograms
# of limestone, not how many molecules. The bridge between molecules and grams is the mole.
#
# **Plan.** (1) molar mass from a table of atomic masses, (2) n = m / M and Avogadro's number,
# (3) a general recipe calculator, (4) limiting reagent, theoretical and percent yield,
# (5) molarity, (6) the limestone design problem.

# %%
import pathlib
import re

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# standard atomic masses in g/mol (rounded textbook values)
ATOMIC_MASS = {"H": 1.008, "C": 12.011, "N": 14.007, "O": 15.999, "Na": 22.990,
               "Cl": 35.45, "S": 32.06, "Ca": 40.078, "Fe": 55.845, "Al": 26.982}
AVOGADRO = 6.022e23          # entities per mole (6.02214076e23 exactly; 6.022e23 is plenty here)


# %% [markdown]
# ## Step 1: molar mass
# The molar mass M of a substance is the mass of one mole of it, in g/mol. Add the atomic
# masses of all atoms in the formula: M(H2O) = 2 * 1.008 + 15.999 = 18.015 g/mol.

# %%
def parse_formula(formula):
    """{element: count} for formulas such as 'CaCO3' or 'Ca(OH)2'."""
    tokens = re.findall(r"[A-Z][a-z]?|\d+|\(|\)", formula)
    if not formula or "".join(tokens) != formula:
        raise ValueError(f"cannot read formula {formula!r}")
    stack, i = [{}], 0
    while i < len(tokens):
        t = tokens[i]
        if t == "(":
            stack.append({})
        elif t == ")":
            if len(stack) == 1:
                raise ValueError(f"unbalanced bracket in {formula!r}")
            group = stack.pop()
            mult = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                mult, i = int(tokens[i + 1]), i + 1
            for el, n in group.items():
                stack[-1][el] = stack[-1].get(el, 0) + n * mult
        elif t.isdigit():
            raise ValueError(f"misplaced number in {formula!r}")
        else:
            n = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                n, i = int(tokens[i + 1]), i + 1
            stack[-1][t] = stack[-1].get(t, 0) + n
        i += 1
    if len(stack) != 1:
        raise ValueError(f"unbalanced bracket in {formula!r}")
    return stack[0]


def molar_mass(formula, table=ATOMIC_MASS):
    """Molar mass in g/mol."""
    return sum(table[el] * n for el, n in parse_formula(formula).items())


# %% [markdown]
# ## Step 2: moles, grams and molecules
# n = m / M (moles = grams divided by g/mol), and the number of molecules is N = n * N_A,
# where N_A = 6.022e23 per mole is Avogadro's number.

# %%
def moles(mass_g, formula):
    return mass_g / molar_mass(formula)


def grams(n_mol, formula):
    return n_mol * molar_mass(formula)


def molecules(n_mol):
    return n_mol * AVOGADRO


# %% [markdown]
# ## Step 3: the recipe calculator
# In a balanced equation the coefficients are mole ratios. If a reaction makes `c_out` moles
# of one species for every `c_in` moles of another, then n_out = n_in * c_out / c_in.

# %%
def convert_mass(mass_g, formula_in, coef_in, formula_out, coef_out):
    """Mass (g) of species `out` that matches `mass_g` of species `in` in the balanced equation."""
    n_in = moles(mass_g, formula_in)
    return grams(n_in * coef_out / coef_in, formula_out)


# %% [markdown]
# ## Step 4: limiting reagent and yield
# Reagents run out at different times. For each reactant divide its moles by its coefficient;
# the smallest value is the reaction extent (how many "recipes" can be made) and that
# reactant is the limiting reagent. Theoretical yield = extent * coefficient * M of the
# product. Percent yield = 100 * actual / theoretical.

# %%
def limiting_reagent(reactants, masses_g):
    """reactants = [(coef, formula), ...], masses in g.  Returns (index of limiting reagent, extent in mol)."""
    ratios = [moles(m, f) / c for (c, f), m in zip(reactants, masses_g)]
    k = int(np.argmin(ratios))
    return k, float(ratios[k])


def theoretical_yield(product, extent_mol):
    """product = (coef, formula); returns grams made if the reaction runs to completion."""
    coef, formula = product
    return grams(extent_mol * coef, formula)


def percent_yield(actual_g, theoretical_g):
    return 100.0 * actual_g / theoretical_g


# %% [markdown]
# ## Step 5: concentration of a solution
# Molarity c = n / V in mol/L (written M, not to be confused with molar mass). To make V litres
# of a solution of concentration c you weigh m = c * V * M grams of solute.

# %%
def molarity(n_mol, volume_l):
    return n_mol / volume_l


def solute_mass(conc_mol_per_l, volume_l, formula):
    return conc_mol_per_l * volume_l * molar_mass(formula)


# %% [markdown]
# ## Step 6: design problem, limestone for an acid spill
# CaCO3 + H2SO4 -> CaSO4 + H2O + CO2 (balanced as written: 1 : 1). Limestone is not pure
# and we add a safety excess so that the spill is surely neutralised.

# %%
def limestone_needed(acid_kg, purity=1.0, excess=0.0):
    """kg of limestone (purity = mass fraction CaCO3, excess = extra fraction) to neutralise acid_kg of H2SO4."""
    pure = convert_mass(acid_kg * 1000.0, "H2SO4", 1, "CaCO3", 1) / 1000.0
    return pure * (1.0 + excess) / purity


def co2_released(limestone_kg, purity=1.0):
    """kg of CO2 released if all the CaCO3 reacts."""
    return convert_mass(limestone_kg * purity * 1000.0, "CaCO3", 1, "CO2", 1) / 1000.0


# %% [markdown]
# ## Step 7: see it
# Left: CO2 from 16 g of CH4 as the oxygen supply grows (a kink where oxygen stops being the
# limit). Right: kilograms of limestone against acid mass for three purities.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    meth = [(1, "CH4"), (2, "O2")]
    print("M(CH4) = %.3f g/mol, M(O2) = %.3f, M(CO2) = %.3f, M(H2O) = %.3f" % tuple(
        molar_mass(f) for f in ("CH4", "O2", "CO2", "H2O")))
    n = moles(16.0, "CH4")
    print("16 g CH4 = %.4f mol = %.3e molecules" % (n, molecules(n)))
    co2 = convert_mass(16.0, "CH4", 1, "CO2", 1)
    print("CO2 from 16 g CH4: %.2f g (O2 needed: %.2f g)" % (co2, convert_mass(16.0, "CH4", 1, "O2", 2)))

    o2 = np.linspace(0, 100, 201)
    y = [theoretical_yield((1, "CO2"), limiting_reagent(meth, [16.0, m])[1]) if m > 0 else 0.0 for m in o2]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(o2, y)
    need = convert_mass(16.0, "CH4", 1, "O2", 2)
    ax.axvline(need, color="gray", ls=":")
    ax.annotate("oxygen no longer limits\n(%.1f g O2)" % need, (need, co2 * 0.55), fontsize=8, ha="right")
    ax.set_xlabel("oxygen supplied (g)")
    ax.set_ylabel("CO2 formed from 16 g CH4 (g)")
    ax.set_title("Yield rises until the other reagent becomes limiting")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "yield_vs_oxygen.png", dpi=120)

    acid = np.linspace(0, 1000, 101)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for pur in (1.0, 0.92, 0.80):
        ax2.plot(acid, [limestone_needed(a, pur, 0.10) for a in acid], label="purity %d %%, 10 %% excess" % round(pur * 100))
    ax2.set_xlabel("sulphuric acid to neutralise (kg)")
    ax2.set_ylabel("limestone to order (kg)")
    ax2.set_title("Design: limestone for an acid spill")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "limestone_design.png", dpi=120)
    print("500 kg H2SO4: pure CaCO3 %.1f kg; 92%% pure + 10%% excess: %.1f kg; CO2 %.1f kg" % (
        limestone_needed(500), limestone_needed(500, 0.92, 0.10), co2_released(limestone_needed(500))))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
