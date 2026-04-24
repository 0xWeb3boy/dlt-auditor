# Code-Shape Card

## Metadata

- ID: `sei-chain-2024-04-15-sei-chain-rpc-client-api-a2aa14179`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-address-association-check`

## Code Shape Summary

- The patch replaces defaulting address-conversion helpers with explicit EVM address lookups plus `found` checks in several `x/evm/client/wasm/query.go` ERC20/ERC721 helper paths. Unassociated Bech32 addresses now cause an error before ABI payload/query data is packed.

## Search Motifs

- Motif 1: explicit address lookup returns found but code ignores it
- Motif 2: default address helper used for participant parameter
- Motif 3: payload builder lacks fail-closed association error

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Require explicit association lookup success before constructing EVM/precompile payloads.

## False Match Warnings

- The generated payload is never used for privileged execution.
- Every downstream precompile revalidates the address association.
