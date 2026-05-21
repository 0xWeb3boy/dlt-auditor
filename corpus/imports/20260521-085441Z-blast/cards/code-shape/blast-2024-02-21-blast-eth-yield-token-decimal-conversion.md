# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-eth-yield-token-decimal-conversion`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cross-domain-unit-conversion-mismatch`

## Code Shape Summary

- One branch converts token amount to 18 decimals for finalizer calldata while another uses raw token units as portal ETH value.

## Search Motifs

- _convertDecimals
- _amount raw
- msg.value == _amount
- remoteToken == address(0)
- token decimals

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Normalize units once at the boundary and use the same normalized amount for custody, portal value, finalizer calldata, and provider accounting.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
