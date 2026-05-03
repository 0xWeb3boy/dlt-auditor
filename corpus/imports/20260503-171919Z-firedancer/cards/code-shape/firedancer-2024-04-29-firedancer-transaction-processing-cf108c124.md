# Code-Shape Card

## Metadata

- ID: `firedancer-2024-04-29-firedancer-transaction-processing-cf108c124`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## Code Shape Summary

- The authorization gate inferred signer status from indirect metadata rather than asking whether the specific authority account index was actually a signer.

## Search Motifs

- Motif 1: signature count comparison replaced with exact signer-index check
- Motif 2: authority index validated with direct signer helper
- Motif 3: deploy gate inferred signer status from coarse transaction metadata

## Typical Asymmetry

- The attacker shapes transaction metadata broadly, but the sink should trust only the exact authority account attached to the state change.

## Patch Pattern

- Replace indirect or count-based authorization logic with an exact signer check on the privileged account index.

## False Match Warnings

- No full exploit scenario is provided showing unauthorized deployment in practice.
- Test contents are not provided, only test file metadata.
