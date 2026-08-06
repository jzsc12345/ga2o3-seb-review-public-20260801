# PARENT_DEFAULT_LEAKAGE_AUDIT_SCOPE

> Status: SCOPE ONLY / NOT EXECUTED / VALUES NOT ASSERTED
>
> This index does not authorize or apply any material override, physical model, solver step, bias, or transient.

## Semiconductor identity and band slots

- material class and parent identity
- band gap: `Eg` and temperature dependence
- electron affinity
- relative permittivity
- effective density of states: `Nc`, `Nv`

## Transport slots

- low-field electron mobility `mun`
- low-field hole mobility `mup`
- saturation velocity `vsat`
- field-dependent mobility
- temperature-dependent mobility

## Recombination and carrier-statistics slots

- SRH electron lifetime
- SRH hole lifetime
- lifetime temperature dependence
- Auger coefficients
- band-gap narrowing
- incomplete ionization

## Thermal slots

- thermal conductivity
- thermal-conductivity temperature dependence
- heat capacity and any temperature dependence activated by the later model set

## Avalanche slots

- impact-ionization model family
- electron coefficients
- hole coefficients
- field exponents and temperature dependence

## Activation closure

- every material-default slot reachable from the later approved `MODELS` statement
- every region-specific `MATERIAL`, `MOBILITY`, `IMPACT`, and thermal card required to prevent unintended GaN/ZnO parent defaults

All values remain **UNVERIFIED** until a later, separately authorized evidence and parser/runtime audit.
