# Validation Card

## Metadata

- ID: `optimism-2025-08-12-optimism-storage-1b6f57f0cd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reorg-state-validation`

## What Confirmed The Issue

- find_common_ancestor() now derives a lower bound from the finalized safety head before rewinding.
- find_rewind_target() walks backward only above that ancestor bound and stops on a canonical source block.
- The changed logic sits in reorg/canonicality handling, which is security-sensitive for blockchain state integrity.
- New tests target finalized and future-activation reorg edge cases, showing intentional hardening of finalization-bound behavior.

## What Could Have Invalidated It

- No end-to-end pre-patch failure is shown causing an actual invalid state transition or consensus break.
- No evidence shows an external attacker could reliably trigger or exploit the condition.
- No proof of forged block acceptance, funds impact, or cross-node divergence is included in the supplied patch evidence.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No end-to-end pre-patch failure is shown causing an actual invalid state transition or consensus break.
- No evidence shows an external attacker could reliably trigger or exploit the condition.
- No proof of forged block acceptance, funds impact, or cross-node divergence is included in the supplied patch evidence.
