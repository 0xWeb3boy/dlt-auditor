# Validation Card

## Metadata

- ID: `oasis-core-2021-02-15-oasis-core-cryptography-a0ac508da`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `insufficient-signature-domain-separation`

## What Confirmed The Issue

- Evidence 1: The fix threads 'runtimeID' into the affected verification paths, derives runtime-qualified signature contexts via 'WithSuffix(runtimeID.String())', updates commitment-generation helpers to sign with an explicit runtime, and adds regression coverage for runtime-mismatched evidence.
- Evidence 2: The source finding states the invariant explicitly: Executor commitments and proposed-batch scheduler signatures must be bound to the specific runtime they belong to. A signature that verifies in one runtime context must not verify in another runtime context.

## What Could Have Invalidated It

- Compensating control 1: Not a match if signer membership, runtime binding, and domain separation are enforced before the sink on every path.
- Compensating control 2: Not a match if the patch only changes serialization, logging, or tests without changing the accepted signer set.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Not a match if signer membership, runtime binding, and domain separation are enforced before the sink on every path.
- Caution 2: Not a match if the patch only changes serialization, logging, or tests without changing the accepted signer set.
