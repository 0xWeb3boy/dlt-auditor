# Validation Card

## Metadata

- ID: `fuel-core-2022-03-02-fuel-core-storage-10a47d0a77`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `block-malleability`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- Patch adds a dedicated transaction-status persistence path after execution.
- Patch changes commitment construction to include canonical transaction serialization with witness data.

## What Could Have Invalidated It

- Independent recomputation of block commitments from finalized block bytes before use.
- Status records treated only as advisory and never used for proofs, client finality, or execution decisions.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: A commitment mismatch can make nodes, indexes, or clients reason over non-canonical block contents. The finding is likely rather than fully proven, so high is appropriate but not critical.

## False-Positive Cautions

- Pure refactors of transaction status storage are not enough without a commitment/status ordering issue.
- If canonical serialization is already the sole commitment input before persistence, the motif is not a bug.
