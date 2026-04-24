# Validation Card

## Metadata

- ID: `sui-2024-05-21-sui-storage-d0ebedf217`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-threshold-api-hardening`

## What Confirmed The Issue

- Committee signature certification depends on the approval threshold associated with a bridge action.
- Call sites changed from `request_committee_signatures(action, threshold)` to `request_committee_signatures(action)`.
- The traced aggregator implementation now derives the threshold via `action.approval_threshold()` internally.
- The changed path is used by bridge action execution and governance CLI signing flows.

## What Could Have Invalidated It

- No shown pre-patch caller supplied an incorrect, stale, lower, or attacker-influenced threshold.
- No exploit path, bypass, replay, or request forgery is demonstrated by the patch evidence.
- No test evidence shows a previously accepted invalid certificate or quorum mismatch.
- The gas price retry and bridge committee helper changes are operational or cleanup-oriented, not independently security-relevant.

## Severity Guidance

- Expected impact band: signature-quorum-integrity
- Expected severity band: medium
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Treat this as hardening of a security-sensitive signing API, not as a proven vulnerability fix.
- Do not classify the issue as replay, request forgery, or storage corruption from the provided evidence.
- Do not claim external attacker control over the threshold parameter without additional evidence.
- The corpus entry should focus on centralized quorum-threshold derivation for bridge committee signatures.
