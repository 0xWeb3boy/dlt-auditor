# Validation Card

## Metadata

- ID: `oasis-core-2018-05-26-oasis-core-cryptography-19cd4a286`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signed-message-validation-consistency`

## What Confirmed The Issue

- Evidence 1: The fix restructures signed-message handling so the signed wrapper stores serialized payload bytes, the dispatcher uses the verified call object for both method lookup and execution, and one registry identity check now treats payload extraction as fallible.
- Evidence 2: The source finding states the invariant explicitly: Signed requests should be verified once and then routed and executed using that same verified representation, and failures while extracting signed contents should abort processing.

## What Could Have Invalidated It

- Compensating control 1: Not a match if signer membership, runtime binding, and domain separation are enforced before the sink on every path.
- Compensating control 2: Not a match if the patch only changes serialization, logging, or tests without changing the accepted signer set.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if signer membership, runtime binding, and domain separation are enforced before the sink on every path.
- Caution 2: Not a match if the patch only changes serialization, logging, or tests without changing the accepted signer set.
