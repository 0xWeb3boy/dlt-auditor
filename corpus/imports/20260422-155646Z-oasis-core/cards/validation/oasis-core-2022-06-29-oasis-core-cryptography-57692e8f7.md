# Validation Card

## Metadata

- ID: `oasis-core-2022-06-29-oasis-core-cryptography-57692e8f7`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-query-verification`

## What Confirmed The Issue

- Evidence 1: The fix adds 'verify_for_query' to the verifier trait, implements it in the Tendermint verifier, routes query-mode requests through that path, and adds an explicit runtime-ID/namespace check before query-time consensus state is returned or treated as verified.
- Evidence 2: The source finding states the invariant explicitly: Historical query state access should only use consensus state derived from a runtime header that has been checked against the expected runtime identity and associated consensus block.

## What Could Have Invalidated It

- Compensating control 1: Not a match if signer membership, runtime binding, and domain separation are enforced before the sink on every path.
- Compensating control 2: Not a match if the patch only changes serialization, logging, or tests without changing the accepted signer set.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if signer membership, runtime binding, and domain separation are enforced before the sink on every path.
- Caution 2: Not a match if the patch only changes serialization, logging, or tests without changing the accepted signer set.
