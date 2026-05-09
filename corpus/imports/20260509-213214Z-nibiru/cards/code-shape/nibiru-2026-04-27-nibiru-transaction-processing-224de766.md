# Code-Shape Card

## Metadata

- ID: `nibiru-2026-04-27-nibiru-transaction-processing-224de766`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## Code Shape Summary

- A public asset-mapping creation path gained a mainnet-only authority/sudo gate before registration can proceed.

## Search Motifs

- CreateFunToken lacks authority check
- mapping registry write before permission check
- tests for permissioned ERC20 and coin mappings
- mainnet chain ID branch added around registration

## Typical Asymmetry

- The trusted protocol side assumes a helper, callback, registry, iterator, or accounting result is already safe; the attacker controls the input, callee, ordering, or transaction shape that reaches that trusted sink.

## Patch Pattern

- Check chain environment, require configured authority or sudo permission before registration, and cover both ERC20-origin and native-coin mapping creation paths with tests.

## False Match Warnings

- Non-mainnet permissionless mapping may be intentional
- Creation fees do not replace authorization for privileged registries
- Need evidence the mapping affects trusted bridge behavior before claiming theft
