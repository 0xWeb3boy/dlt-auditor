# Nibiru C4 MR-H-03: MsgCreateFunToken and MsgConvertCoinToEvm do not always consume EVM gas

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `High`
- Corpus ID: `nibiru-c4-2025-01-mr-h03-funtoken-conversion-unmetered-evm-calls`

---

## `MsgCreateFunToken` and `MsgConvertCoinToEvm` do not always consume EVM gas

### Original Issue
[M-03](https://github.com/code-423n4/2024-11-nibiru-findings/issues/46)

### Severity: High

- Impact: High
- Likelihood: High

### Description

`convertCoinToEvmBornERC20()` called as part of `MsgConvertCoinToEvm` [does not consume the EVM gas](https://github.com/NibiruChain/nibiru/blob/13c71a70c5a730060b7b096b6509b04d64c73edf/x/evm/keeper/msg_server.go#L649-L667). 

Same in `createFunTokenFromERC20()`, which is called as part of `MsgCreateFunToken`, does not consume the EVM gas when retrieving the ERC20 metadata infos -> [here](https://github.com/NibiruChain/nibiru/blob/13c71a70c5a730060b7b096b6509b04d64c73edf/x/evm/keeper/funtoken_from_erc20.go#L141).

### Recommendation
Consume the EVM gas via the Cosmos SDK gas meter.

### Nibiru
> Addressed with [PR-2180](https://github.com/NibiruChain/nibiru/pull/2180).

### Zenith
> Confirmed.

***
