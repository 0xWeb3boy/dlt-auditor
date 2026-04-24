# Validation Card

## Metadata

- ID: `optimism-2026-02-12-optimism-transaction-processing-bcec0992d2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-derivation-completeness-check`

## What Confirmed The Issue

- The changed Rust logic sits in interop fault-proof transition handling, not in ancillary product code.
- The patch adds an explicit check that safe_head.block_info.number must reach disputed_l2_block_number before proceeding on the normal success path.
- When derivation falls short, the code now requires INVALID_TRANSITION_HASH and otherwise returns FaultProofProgramError::InvalidClaim.
- The change removes reliance on advance_to_target(...) success alone and tightens validation of proof-related state transitions.

## What Could Have Invalidated It

- No direct evidence shows the old code could be exploited by an attacker or malicious claimant.
- No patch evidence proves transition_and_check(...) would previously accept an incorrect post-state.
- No demonstrated consensus failure, asset loss, or dispute-game bypass is shown.
- No evidence establishes how reachable incomplete derivation was under adversarial conditions versus benign missing-input conditions.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No direct evidence shows the old code could be exploited by an attacker or malicious claimant.
- No patch evidence proves transition_and_check(...) would previously accept an incorrect post-state.
- No demonstrated consensus failure, asset loss, or dispute-game bypass is shown.
