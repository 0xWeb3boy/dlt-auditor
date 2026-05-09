# Code-Shape Card

## Metadata

- ID: `agave-2026-04-27-agave-validator-ops-7b7ffdd747`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `cli-validator-info-signer-check`

## Code Shape Summary

- A CLI parser extracts validator metadata but drops whether the validator pubkey actually signed, then selection/display logic treats unsigned or malformed records like trusted entries.

## Search Motifs

- parse validator info returns pubkey without signer flag
- publish path matches existing metadata without requiring signer true
- validator info account scan unwraps malformed data
- CLI display trusts unsigned metadata record

## Typical Asymmetry

- The vulnerable shape trusts an earlier, broader, or non-consuming check while a later security-sensitive sink assumes the data, identity, quota, or state was fully validated.
- The fixed shape moves the check to the boundary that owns the sink, consumes/accounting resources at admission, or carries authenticity/state metadata forward explicitly.

## Patch Pattern

- Return signer/authenticity metadata from parsing, require it in publish/get selection logic, and convert malformed account parsing to graceful rejection.

## False Match Warnings

- The signer bit is checked before any metadata is displayed, selected, or reused.
- The data is explicitly labeled unauthenticated and used only for diagnostics.
- On-chain transaction authorization, not CLI parsing, is the only security boundary in question.
