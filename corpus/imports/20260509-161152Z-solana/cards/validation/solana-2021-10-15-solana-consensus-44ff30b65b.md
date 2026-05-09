# Validation Card

## Metadata

- ID: `solana-2021-10-15-solana-consensus-44ff30b65b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-repair-retry-hardening`

## What Confirmed The Issue

- `DuplicateAncestorDecision::InvalidSample` is made retryable with a comment referencing bad samples from malicious validators.
- `SampleNotDuplicateConfirmed` is also made retryable, suggesting the prior behavior could prematurely stop repair progress under transient validator detection states.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: integrity_or_funds
- Expected severity band: Medium
- Rationale: The impact primarily affects availability, liveness, or validator resource consumption rather than direct fund theft.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
