# Nibiru C4 MR-M-02: Block transient gas meter got removed causing different gas usage compared to Ethereum

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `Medium`
- Corpus ID: `nibiru-c4-2025-01-mr-m02-transient-gas-meter-removal`

---

## Block (transient) gas meter got removed which results in a slightly different gas usage compared to Ethereum

### Original Issue
[M-03](https://github.com/code-423n4/2024-11-nibiru-findings/issues/46)

### Lines of Code

[`PR-2167`](https://github.com/NibiruChain/nibiru/pull/2167)

### Severity: Medium

- Impact: Medium
- Likelihood: High

### Description

The reported finding [Issue #46](https://github.com/code-423n4/2024-11-nibiru-findings/issues/46) is mitigated via [PR-2132](https://github.com/NibiruChain/nibiru/pull/2132).

However, a more recent PR, [PR-2167](https://github.com/NibiruChain/nibiru/pull/2167), removed the block (transient) gas meter completely. This means that now both the Cosmos SDK gas and EVM gas is mixed together, resulting in potential EVM gas compatibility issues. 

### Recommendation
Either document this discrepancy clearly, or re-add the block (transient) gas meter again.

### Nibiru
> Acknowledged.

***
