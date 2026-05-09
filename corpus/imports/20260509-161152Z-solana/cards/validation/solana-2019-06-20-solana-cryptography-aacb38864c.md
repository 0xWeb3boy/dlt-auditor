# Validation Card

## Metadata

- ID: `solana-2019-06-20-solana-cryptography-aacb38864c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invalid-fork-replay-handling`

## What Confirmed The Issue

- Replay failures from non-committable transaction errors and BlobError::VerificationFailed are explicitly classified as fatal.
- Fatal replay results cause mark_dead_slot(bank.slot(), blocktree, progress) to run.

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
