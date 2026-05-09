# Validation Card

## Metadata

- ID: `solana-2021-01-23-solana-cryptography-480a35d678`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-privilege-propagation`

## What Confirmed The Issue

- Runtime verification now computes an optional writable flag when writable-deescalation tracking is enabled.
- BPF CPI syscall code derives caller_privileges by mapping callee account keys back to caller KeyedAccount writability.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: state_integrity_or_policy_bypass
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
