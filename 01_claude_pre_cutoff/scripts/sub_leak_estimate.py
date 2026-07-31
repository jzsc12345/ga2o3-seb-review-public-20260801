# -*- coding: utf-8 -*-
"""Is the n-type substrate a parallel conduction path? Order-of-magnitude check.

Current deck (SEB_Ga2O3_VDOE.sdb / SEB.in):
    substrate  y -0.10 .. +0.40  = 0.5 um thick, n-type 1.5e15 cm-3, mun 300
It sits directly under the whole device, source to drain, with nothing to
deplete it -- no deep acceptors, no semi-insulating compensation.
"""
q   = 1.602e-19
Nd  = 1.5e15      # cm-3   substrate doping in the current deck
mun = 300.0       # cm2/Vs (material statement)
t   = 0.5e-4      # cm     substrate thickness (0.5 um)
L   = 25e-4       # cm     source-to-drain span ~25 um
W   = 1e-4        # cm     per 1 um of device width

sigma  = q * Nd * mun                 # S/cm
G      = sigma * t * W / L            # S  for a 1 um-wide slab
print(f"sigma            = {sigma:.3e} S/cm")
print(f"sheet conductance= {sigma*t:.3e} S/square")
print(f"G (per um width) = {G:.3e} S")
for V in (300, 755, 1600):
    print(f"  V={V:5d} V  ->  I = {G*V:.3e} A/um   ({G*V*1e6:.3e} mA/mm)")

print()
print("Paper Fig.2(c)/Fig.10(c) off-state leakage is ~1e-8..1e-6 mA/mm,")
print("i.e. ~1e-14..1e-12 A/um.  Compare with the observed ~1e-6 A/um.")
print()
# what the substrate would need to be to get down to paper-level leakage
target = 1e-12   # A/um at 300 V
Nd_max = target / (300 * q * mun * t * W / L)
print(f"To reach ~1e-12 A/um at 300 V the substrate free-electron density")
print(f"would have to be <= {Nd_max:.2e} cm-3  -- i.e. essentially fully")
print(f"compensated.  That is exactly what the paper's Fe deep acceptor")
print(f"(2e18 cm-3 at Ec-0.8 eV) does: it pins EF near midgap and leaves")
print(f"a free-carrier density many orders below the doping.")
