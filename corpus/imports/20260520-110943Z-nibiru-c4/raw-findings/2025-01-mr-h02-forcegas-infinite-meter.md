# Nibiru C4 MR-H-02: Infinite gas meter in ForceGasInvariant

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `High`
- Corpus ID: `nibiru-c4-2025-01-mr-h02-forcegas-infinite-meter`

---

## Infinite gas meter in `ForceGasInvariant()`

### Original Issue
[H-03](https://github.com/code-423n4/2024-11-nibiru-findings/issues/26)

### Severity: High

- Impact: High
- Likelihood: Medium/Low

### Description

Using an infinite gas meter in [`ForceGasInvariant()`](https://github.com/NibiruChain/nibiru/blob/13c71a70c5a730060b7b096b6509b04d64c73edf/x/evm/keeper/bank_extension.go#L173) seems dangerous. Even though it will error once the original gas meter is used and the gas consumed, it could potentially run indefinitely before using unlimited gas (e.g., when somehow a large number of coins is provided).

### Recommendation
Use the same amount of available gas from the current gas meter.

### Nibiru
> Addressed in [PR-2183](https://github.com/NibiruChain/nibiru/pull/2183)

### Zenith
> Confirmed.

***
