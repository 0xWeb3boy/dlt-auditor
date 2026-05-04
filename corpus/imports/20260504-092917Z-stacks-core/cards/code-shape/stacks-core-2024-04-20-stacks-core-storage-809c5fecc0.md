# Code-Shape Card

## Metadata

- ID: `stacks-core-2024-04-20-stacks-core-storage-809c5fecc0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `vm-error-propagation-transaction-validity`

## Code Shape Summary

- The patch likely fixes a consensus-relevant STX transfer rollback bug in the Clarity VM. The grounded change is a one-character error-propagation fix in `Environment::stx_transfer`: `value.clone().expect_result()` became `value.clone().expect_result()?`. Given the surrounding code, this means the commit/rollback decision now matches the inner Clarity response result, committing only for inner `Ok(_)`.

## Search Motifs

- Motif 1: manual construction bypasses constructor checks
- Motif 2: noncanonical preimage or type accepted at signing or validation boundary
- Motif 3: VM or transaction error interpreted inconsistently

## Typical Asymmetry

- The producer, peer, signer, or caller can choose fields that the consumer later treats as authoritative unless the missing property is checked at the boundary.

## Patch Pattern

- Centralize canonical construction or validation and reject ambiguous representations before using them in sensitive logic.

## False Match Warnings

- The constructor may be used only with trusted constants.
- The changed path may improve diagnostics without changing acceptance behavior.
