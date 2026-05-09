# Validation Card

## Metadata

- ID: `solana-2022-05-07-solana-cryptography-10f6845071`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-transaction-sanitization`

## What Confirmed The Issue

- Commit subject states that transaction sanitization should fail when an instruction program id uses a lookup table.
- VersionedTransaction gains sanitize(require_static_program_ids) and forwards the policy into message sanitization.

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
