# Nibiru C4 MR-H-01: Bank's StateDB pointer is not set to nil

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `High`
- Corpus ID: `nibiru-c4-2025-01-mr-h01-statedb-pointer-not-cleared`

---

## Bank's `StateDB` pointer is not set to `nil`

### Original Issue
[H-02](https://github.com/code-423n4/2024-11-nibiru-findings/issues/57)

### Lines of Code

[`funtoken.go#L62`](https://github.com/NibiruChain/nibiru/blob/13c71a70c5a730060b7b096b6509b04d64c73edf/x/evm/precompile/funtoken.go#L62)

### Severity: High

- Impact: High
- Likelihood: High

### Description

Line 62 sets and keeps the bank's `StateDB` set, even if `EthCall` is used. Same in `wasm.go`. Which then causes the same issue as the one that is reported in [H-02](https://github.com/code-423n4/2024-11-nibiru-findings/issues/57), due to the check [here](https://github.com/NibiruChain/nibiru/blob/13c71a70c5a730060b7b096b6509b04d64c73edf/x/evm/keeper/bank_extension.go#L208-L211).

### Nibiru
> Fixed with [PR-2173](https://github.com/NibiruChain/nibiru/pull/2173).

### Zenith
> Confirmed.

***
