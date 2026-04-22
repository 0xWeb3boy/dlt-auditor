# Validation Card

## Metadata

- ID: `oasis-core-2023-06-29-oasis-core-rpc-client-api-95923572b`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `state-verification-gap`

## What Confirmed The Issue

- Evidence 1: The patch threads block-metadata retrieval through the runtime host and consensus client, adds transaction-with-proofs support in the backend, and updates proof generation logic so the verifier can use the block metadata transaction for same-block validation.
- Evidence 2: The source finding states the invariant explicitly: Latest-block post-execution state should not be treated as fully verified until the verifier can check block metadata for that same height through the intended consensus proof path.

## What Could Have Invalidated It

- Compensating control 1: Not a match if signer membership, runtime binding, and domain separation are enforced before the sink on every path.
- Compensating control 2: Not a match if the patch only changes serialization, logging, or tests without changing the accepted signer set.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Not a match if signer membership, runtime binding, and domain separation are enforced before the sink on every path.
- Caution 2: Not a match if the patch only changes serialization, logging, or tests without changing the accepted signer set.
