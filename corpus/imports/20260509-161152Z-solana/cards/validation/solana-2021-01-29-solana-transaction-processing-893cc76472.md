# Validation Card

## Metadata

- ID: `solana-2021-01-29-solana-transaction-processing-893cc76472`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-invariant-bypass`

## What Confirmed The Issue

- Deploy/upgrade buffer verification changed from ignoring authority_address to comparing it against the supplied upgrade authority.
- Mismatch now returns InstructionError::IncorrectAuthority.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: defense_in_depth_or_input_hardening
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
