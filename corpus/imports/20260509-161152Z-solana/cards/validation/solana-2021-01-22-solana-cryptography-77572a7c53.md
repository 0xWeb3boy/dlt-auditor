# Validation Card

## Metadata

- ID: `solana-2021-01-22-solana-cryptography-77572a7c53`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cpi-writable-privilege-tracking`

## What Confirmed The Issue

- BPF loader syscall builds caller_privileges from keyed_account.is_writable() for CPI message accounts.
- MessageProcessor verification now computes is_writable from caller_privileges when writable deescalation tracking is enabled.

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
