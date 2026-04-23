# Code-Shape Card

## Metadata

- ID: `reth-2025-09-25-reth-rpc-client-api-aa192c255`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-auth-header-parsing`

## Code Shape Summary

- The patch tightens Bearer token parsing in `crates/rpc/rpc-layer/src/jwt_validator.rs`. Before, the helper accepted any Authorization header containing the substring `"Bearer "` anywhere; after, it requires the header to start with that prefix. The evidence shows a malformed header was previously treated as a Bearer token source, but it does not establish a concrete authentication bypass or broader exploit from that behavior alone.

## Search Motifs

- Motif 1: TODO
- Motif 2: TODO
- Motif 3: TODO

## Typical Asymmetry

- TODO

## Patch Pattern

- TODO

## False Match Warnings

- TODO
