# Validation Card

## Metadata

- ID: `agave-2026-04-30-agave-cryptography-26af74dd48`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-protocol-validation`

## What Confirmed The Issue

- Blockstore recovery handling now passes a ShredRecoveryContext.
- A regression test activates discard_unexpected_data_complete_shreds and verifies recovered shreds with unexpected data-complete flags are discarded.

## What Could Have Invalidated It

- Direct and recovered shred paths already shared the same validation before the patch.
- The feature-gated rule does not apply to recovered shreds by protocol design.

## Severity Guidance

- Expected impact band: `consensus data validation hardening`
- Expected severity band: `medium`
- Rationale: Recovered shreds are consensus-sensitive ledger data; inconsistent validation can matter, but no exploit, signature bypass, or state-corruption scenario was proven.

## False-Positive Cautions

- Do not treat all recovery refactors as security; the key signal is inconsistent validation across ingress paths.
- Do not claim signature bypass unless the recovered data can evade cryptographic shred checks.
