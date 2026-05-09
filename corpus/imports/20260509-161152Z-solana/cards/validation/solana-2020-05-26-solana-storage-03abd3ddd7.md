# Validation Card

## Metadata

- ID: `solana-2020-05-26-solana-storage-03abd3ddd7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-privilege-check`

## What Confirmed The Issue

- Commit subject is "Prevent privilege escalation (#10232)".
- programs/bpf_loader/src/syscalls.rs adds verify_instruction before CPI dispatch.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: integrity_or_funds
- Expected severity band: High
- Rationale: The impact can affect funds, consensus safety, authorization boundaries, or runtime integrity when reachable.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
