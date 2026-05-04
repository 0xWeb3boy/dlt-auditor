# Validation Card

## Metadata

- ID: `snarkvm-2025-09-04-snarkvm-transaction-processing-fa65b01b8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cryptographic-input-validation-hardening`

## What Confirmed The Issue

- `ecdsa_verify::output_types` now enforces a 65-byte u8 signature array.
- Verifying-key parsing now checks byte length, and V11 syntax is rejected before `ConsensusVersion::V11`.

## What Could Have Invalidated It

- A prior type checker enforces exactly the same ECDSA operand shapes.
- The V11 syntax gate is not consensus-sensitive in the affected release.

## Severity Guidance

- Expected impact band: validation_and_consensus_hardening
- Expected severity band: medium_or_low

## False-Positive Cautions

- The runtime verifier rejects every malformed operand before any security decision.
- The parser enforces the same length and emits deterministic errors everywhere.
