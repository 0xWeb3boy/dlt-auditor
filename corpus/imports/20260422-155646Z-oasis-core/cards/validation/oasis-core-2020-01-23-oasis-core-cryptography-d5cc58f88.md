# Validation Card

## Metadata

- ID: `oasis-core-2020-01-23-oasis-core-cryptography-d5cc58f88`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `insufficient-signature-verification`

## What Confirmed The Issue

- Evidence 1: The fix introduces multisigned descriptor verification in the node registration path. The shown code now requires signatures from the node identity key and consensus key, accumulates the allowed signer set, rejects descriptors with unexpected signers, and authorizes the transaction based on the node or authorized entity instead of the descriptor's generic signer field.
- Evidence 2: The source finding states the invariant explicitly: Node registration must not accept a descriptor unless the authorized registration principal submits it and the descriptor carries signatures from the required keys it embeds. In the provided evidence, that is directly shown for the node identity key and the consensus key, with rejection of unexpected extra signers.

## What Could Have Invalidated It

- Compensating control 1: Not a match if signer membership, runtime binding, and domain separation are enforced before the sink on every path.
- Compensating control 2: Not a match if the patch only changes serialization, logging, or tests without changing the accepted signer set.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if signer membership, runtime binding, and domain separation are enforced before the sink on every path.
- Caution 2: Not a match if the patch only changes serialization, logging, or tests without changing the accepted signer set.
