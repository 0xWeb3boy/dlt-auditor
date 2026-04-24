# Validation Card

## Metadata

- ID: `sui-2022-11-08-sui-storage-d8fef9cd19`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ownership-invariant-enforcement`

## What Confirmed The Issue

- Commit message states shared objects must be newly created and non-new shared transfers should abort.
- `ObjectRuntime::transfer` now returns `TransferResult` instead of only success, classifying new, same-owner, and owner-changed transfers.
- `share_object` now maps `TransferResult::OwnerChanged` to `E_SHARED_NON_NEW_OBJECT` instead of always returning success.
- The changed path controls object ownership transition into shared ownership, a security-sensitive state invariant in Sui.

## What Could Have Invalidated It

- No provided evidence of an end-to-end exploit or attacker-controlled transaction sequence.
- No proof of asset theft, unauthorized access, privilege escalation, or consensus failure.
- No test assertions are included in the supplied evidence despite test files being changed.
- Reachability for ordinary non-test adapters is only partially indicated by comments, not fully proven.

## Severity Guidance

- Expected impact band: state-integrity
- Expected severity band: medium
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Validate only as ownership-invariant hardening for shared-object transfers.
- Do not claim demonstrated state corruption beyond the rejected owner-changing shared transfer condition.
- Do not claim concrete exploitability or financial impact from the provided patch alone.
- Do not rely on issue #5835 contents because they were not supplied.
