# Code-Shape Card

## Metadata

- ID: `snarkvm-2025-09-04-snarkvm-transaction-processing-fa65b01b8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cryptographic-input-validation-hardening`

## Code Shape Summary

- ECDSA instruction validation returned a boolean output type while incomplete comments left operand shape checks underspecified, and syntax gating for V11 was commented out.

## Search Motifs

- ecdsa_verify output_types returns bool without checking signature array length
- verifying_key_from_bytes calls parser before length check
- contains_v11_syntax guard is commented out or version condition is inactive

## Typical Asymmetry

- The code accepted or derived security-sensitive state before proving the boundary property named in the record: `cryptographic-input-shape-validation`.

## Patch Pattern

- Add explicit ECDSA signature and verifying-key length checks and activate consensus-version syntax gating before execution or deployment proceeds.

## False Match Warnings

- The runtime verifier rejects every malformed operand before any security decision.
- The parser enforces the same length and emits deterministic errors everywhere.
- The syntax gate is intentionally inactive because all peers are already on the activating version.
