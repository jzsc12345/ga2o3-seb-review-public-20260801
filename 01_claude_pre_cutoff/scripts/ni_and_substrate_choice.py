# -*- coding: utf-8 -*-
"""Why "p-type 2e6" is a numerically dangerous way to fake a semi-insulating
beta-Ga2O3 substrate, and what the deep-acceptor route does instead.
"""
import math
k, T = 8.617333e-5, 300.0
kT = k * T

def ni(Eg, Nc, Nv):
    return math.sqrt(Nc * Nv) * math.exp(-Eg / (2 * kT))

mats = {
    "beta-Ga2O3": (4.85, 3.70e18, 6.44e20),
    "4H-SiC":     (3.26, 1.70e19, 2.50e19),
    "GaN":        (3.40, 2.20e18, 4.60e19),
    "Si":         (1.12, 2.80e19, 1.04e19),
}
print(f"{'material':<12}{'Eg[eV]':>8}{'ni(300K) [cm^-3]':>22}")
for m, (Eg, Nc, Nv) in mats.items():
    print(f"{m:<12}{Eg:8.2f}{ni(Eg,Nc,Nv):22.3e}")

Eg, Nc, Nv = mats["beta-Ga2O3"]
n_i = ni(Eg, Nc, Nv)
print(f"\nbeta-Ga2O3 ni = {n_i:.3e} cm^-3  -- intrinsic material is a near-perfect insulator.")

p = 2e6                       # the user's current substrate setting
n = n_i**2 / p
print(f"\nIf the substrate is set p-type {p:.0e} cm^-3:")
print(f"   minority n = ni^2/p = {n:.3e} cm^-3")
print("   -> that is ~300 orders below anything a double-precision Newton solve")
print("      can carry.  ATLAS resolves concentrations down to CLIMIT (default 1e4,")
print("      dimensionless) / CLIM.DD; below that the value is meaningless.")
print("      The manual also offers MATERIAL NI.MIN specifically to stop this underflow:")
print("      'set a minimum value of intrinsic carrier density ... to prevent underflow,")
print("       but may result in an incorrect thermal generation rate.'")

print("\nDeep-acceptor route (what the paper does):")
Nt, Et = 2e18, 0.8            # Fe acceptor, 0.8 eV below Ec
for Nd in (1.15e16, 1.5e15):
    # EF pinned near the deep level once Nt >> Nd
    n_pinned = Nc * math.exp(-Et / kT)
    print(f"   background Nd={Nd:.2e}, Fe acceptor {Nt:.0e} at Ec-{Et} eV")
    print(f"     Nt/Nd = {Nt/Nd:.0f}x  -> EF pinned near the level,")
    print(f"     n ~ Nc*exp(-Et/kT) = {n_pinned:.3e} cm^-3")
print("   -> free-electron density lands in a range the solver CAN represent,")
print("      and the trap occupancy is dynamic, which is what an SEE transient needs.")
