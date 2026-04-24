# Validation Card

## Metadata

- ID: `sui-2023-01-12-sui-consensus-d5754e7aac`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-commitment`

## What Confirmed The Issue

- Commit body states checkpoint history lacked any record of submitted user signatures.
- CheckpointContents gains a user_signatures field documented as pinning signatures to checkpoint contents.
- AuthorityPerEpochStore adds user_signatures_for_checkpoint that waits for certificate consensus processing before returning signatures.
- Tests are updated to seed signatures for checkpointed transaction digests.

## What Could Have Invalidated It

- No evidence that invalid or forged transaction signatures were accepted before the patch.
- No evidence that checkpoint contents could be forged or replayed in practice.
- No evidence of broken validator agreement or consensus safety.
- No evidence of runtime signature verification logic being fixed.

## Severity Guidance

- Expected impact band: checkpoint-auditability_or_historical-integrity
- Expected severity band: medium
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Classify as hardening of checkpoint signature retention, not state corruption.
- Do not claim exploitability or signature bypass from the supplied patch alone.
- Treat test helper changes as supporting coverage, not the production security fix.
- Impact is historical integrity and auditability of checkpointed authorization material.
