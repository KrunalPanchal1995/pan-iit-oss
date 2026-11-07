"""Session 2 (Level 2): the buoyant force, barge draft, load capacity and balloon lift.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: F_b = rho * g * V
# **A. Real-world problem.** How much cargo can a barge carry before its deck goes under?
# How many people can a raft carry? Why does a helium balloon lift a child's toy but not
# the child? One equation answers all three: the buoyant force equals the weight of the
# fluid pushed aside, F_b = rho_fluid * g * V_displaced.
# *Educational model only: real vessels need safety margins, waves and rules this lesson ignores.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81            # m/s^2
FRESH = 1000.0      # kg/m^3
SEA = 1025.0        # kg/m^3 (about)
R_GAS = 8.314       # J/(mol K), universal gas constant
P_ATM = 101325.0    # Pa


# %% [markdown]
# ## Step 1: the buoyant force and the floating condition
# Weight of the object = m g. Buoyant force when fully submerged = rho_fluid g V. It floats
# when the object's average density is below the fluid's.

# %%
def buoyant_force(rho_fluid, volume, g=G):
    """Newtons: weight of the displaced fluid."""
    return rho_fluid * g * volume


def net_force_up(mass, volume, rho_fluid, g=G):
    """Net upward force (N) on a fully submerged object (positive: it rises)."""
    return buoyant_force(rho_fluid, volume, g) - mass * g


def floats(mass, volume, rho_fluid):
    """True if the average density mass/volume is below the fluid density."""
    return bool(mass / volume < rho_fluid)


# %% [markdown]
# ## Step 2: a rectangular barge
# A barge of length `L`, beam (width) `B` and hull depth `H`, with total mass `m`, floats at
# draft d = m / (rho L B). The deck goes under when d reaches `H`. Subtracting the empty
# (lightship) mass from the heaviest total mass gives the load capacity. We also keep a
# minimum freeboard (height of deck above the water) as a safety margin.

# %%
def draft_barge(mass, L, B, rho_fluid):
    """Depth (m) of the hull below the water line."""
    return mass / (rho_fluid * L * B)


def freeboard(mass, L, B, H, rho_fluid):
    """Height (m) of the deck above the water; negative means the deck is under water."""
    return H - draft_barge(mass, L, B, rho_fluid)


def max_cargo(L, B, H, lightship, rho_fluid, min_freeboard=0.0):
    """Largest cargo mass (kg) so that freeboard stays at least `min_freeboard` (m)."""
    return rho_fluid * L * B * (H - min_freeboard) - lightship


# %% [markdown]
# ## Step 3: lift of a balloon
# A balloon is the same law in air: lift = (rho_air - rho_gas) g V. Density of an ideal gas
# is rho = P M / (R T) with M the molar mass (kg/mol) and T the temperature in kelvin.

# %%
def gas_density(molar_mass, temp_c, pressure=P_ATM):
    """Ideal-gas density (kg/m^3)."""
    return pressure * molar_mass / (R_GAS * (temp_c + 273.15))


M_AIR, M_HELIUM = 0.02897, 0.0040026   # kg/mol


def lift_per_m3(rho_outside, rho_inside):
    """Lifting mass per cubic metre (kg/m^3): the density difference."""
    return rho_outside - rho_inside


# %% [markdown]
# ## Step 4: a design problem, how many people on a raft?
# Number of people = largest whole number n with n * m_person <= max_cargo(...).
# A tiny tolerance protects against round-off when the answer is exactly a whole number.

# %%
def people_on_raft(L, B, H, raft_mass, person_mass, rho_fluid, min_freeboard):
    cap = max_cargo(L, B, H, raft_mass, rho_fluid, min_freeboard)
    if cap <= 0:
        return 0
    return int(np.floor(cap / person_mass + 1e-9))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    L_, B_, H_, M0 = 20.0, 6.0, 2.5, 60000.0
    print("barge 20 x 6 x 2.5 m, lightship 60 t")
    for rho, name in ((FRESH, "fresh"), (SEA, "sea")):
        print(f"{name:5s}: empty draft {draft_barge(M0, L_, B_, rho):.3f} m, capacity (deck awash) {max_cargo(L_, B_, H_, M0, rho)/1000:.1f} t,"
              f" capacity with 0.3 m freeboard {max_cargo(L_, B_, H_, M0, rho, 0.3)/1000:.1f} t")
    print("worked example: 100 t cargo in fresh water -> draft", round(draft_barge(M0 + 100000.0, L_, B_, FRESH), 3), "m")
    rho_he = gas_density(M_HELIUM, 15.0)
    rho_air = gas_density(M_AIR, 15.0)
    print(f"air {rho_air:.3f}, helium {rho_he:.3f} kg/m^3 at 15 C: lift {lift_per_m3(rho_air, rho_he):.3f} kg per m^3")
    rho_hot = gas_density(M_AIR, 100.0)
    rho_cold = gas_density(M_AIR, 20.0)
    print(f"hot air at 100 C {rho_hot:.3f} vs air at 20 C {rho_cold:.3f}: lift {lift_per_m3(rho_cold, rho_hot):.3f} kg per m^3")
    print("raft 3 x 2 x 0.25 m, 60 kg, 65 kg people, 0.10 m freeboard: fresh",
          people_on_raft(3.0, 2.0, 0.25, 60.0, 65.0, FRESH, 0.10), "sea", people_on_raft(3.0, 2.0, 0.25, 60.0, 65.0, SEA, 0.10))

    # figure 1: draft versus cargo
    cargo = np.linspace(0, 260000, 261)
    fig, ax = plt.subplots(figsize=(6, 4))
    for rho, name in ((FRESH, "fresh water"), (SEA, "sea water")):
        ax.plot(cargo / 1000, draft_barge(M0 + cargo, L_, B_, rho), label=name)
    ax.axhline(H_, color="red", ls="--", label="deck level (hull depth 2.5 m)")
    ax.set_xlabel("cargo mass (tonnes)")
    ax.set_ylabel("draft (m)")
    ax.set_title("Barge draft grows linearly with load")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    ax.set_ylim(0, 2.8)
    fig.tight_layout()
    fig.savefig(OUT / "barge_draft.png", dpi=120)

    # figure 2: balloon lift
    T = np.linspace(20, 120, 101)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(T, lift_per_m3(gas_density(M_AIR, 20.0), gas_density(M_AIR, T)), label="hot-air balloon (outside air 20 C)")
    ax2.axhline(lift_per_m3(gas_density(M_AIR, 15.0), gas_density(M_HELIUM, 15.0)), color="tab:green", ls="--", label="helium at 15 C (air 15 C)")
    ax2.set_xlabel("temperature of the air inside the envelope (C)")
    ax2.set_ylabel("lift per cubic metre (kg/m^3)")
    ax2.set_title("Lift is the density difference")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "balloon_lift.png", dpi=120)
    n = 100.0 / lift_per_m3(gas_density(M_AIR, 20.0), gas_density(M_AIR, 100.0))
    print(f"envelope volume to lift 100 kg of payload with 100 C air: {n:.0f} m^3")
    print(f"envelope volume to lift 100 kg with helium: {100.0/lift_per_m3(rho_air, rho_he):.0f} m^3")

    # figure 3: raft capacity map
    Ls = np.linspace(1.0, 5.0, 41)
    Bs = np.linspace(1.0, 3.0, 41)
    N = np.array([[people_on_raft(l, b, 0.25, 60.0 * l * b / 6.0, 65.0, FRESH, 0.10) for l in Ls] for b in Bs])
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    im = ax3.pcolormesh(Ls, Bs, N, shading="auto")
    fig3.colorbar(im, label="people carried")
    ax3.set_xlabel("raft length (m)")
    ax3.set_ylabel("raft width (m)")
    ax3.set_title("Raft capacity (0.25 m deep, 10 kg per m^2, fresh water)")
    fig3.tight_layout()
    fig3.savefig(OUT / "raft_capacity.png", dpi=120)
