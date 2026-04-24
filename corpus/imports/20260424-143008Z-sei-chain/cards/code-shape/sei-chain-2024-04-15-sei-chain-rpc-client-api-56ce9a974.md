# Code-Shape Card

## Metadata

- ID: `sei-chain-2024-04-15-sei-chain-rpc-client-api-56ce9a974`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `identity-binding-hardening`

## Code Shape Summary

- The patch changes several wasm EVM query payload builders to reject unassociated Bech32 accounts before ABI packing. This is security-relevant identity-binding hardening, but the provided evidence only shows query/payload-construction paths and does not establish a concrete vulnerability or exploit impact.

## Search Motifs

- Motif 1: GetEVMAddressOrDefault used before ABI pack
- Motif 2: missing found check from address association lookup
- Motif 3: unassociated Bech32 accepted in ERC20/ERC721 helper

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Replace default-derived address conversion with explicit lookup and reject absent associations before payload construction.

## False Match Warnings

- The payload is informational and cannot be submitted to a state-changing path.
- Downstream execution independently rejects unassociated addresses.
