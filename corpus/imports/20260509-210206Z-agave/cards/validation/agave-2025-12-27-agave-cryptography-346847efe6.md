# Validation Card

## Metadata

- ID: `agave-2025-12-27-agave-cryptography-346847efe6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `nonce-state-validation-timing`

## What Confirmed The Issue

- Bank-side checking no longer performs final authority signer checks or full nonce execution-state construction.
- SVM processing reloads the nonce account and comments cover used, closed, reopened, spoofed, or authority-changed accounts.

## What Could Have Invalidated It

- The old state could not change between early check and execution.
- A later mandatory execution check already rejected stale nonce state.

## Severity Guidance

- Expected impact band: `replay-sensitive state hardening`
- Expected severity band: `medium`
- Rationale: Fresh nonce validation protects replay-sensitive transaction state, but the evidence did not prove unauthorized acceptance, fund loss, or a concrete exploit.

## False-Positive Cautions

- Moving validation later is not enough for a finding unless mutable state can become stale.
- Do not infer cryptographic primitive failure from nonce-state authorization timing.
