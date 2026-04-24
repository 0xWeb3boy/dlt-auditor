# Validation Card

## Metadata

- ID: `zksync-2019-09-03-zksync-cryptography-136c8d4e5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-message-binding`

## What Confirmed The Issue

- The patch adds signature-message construction verification in circuit code.
- The check targets transfer-to-new serialized transaction bits.
- The storage hunk was not used as evidence.

## What Could Have Invalidated It

- The circuit already reconstructed and constrained the same signed message elsewhere.
- The changed helper is only used in tests or non-verifying tooling.

## Severity Guidance

- Expected impact band: `authorization_integrity`
- Expected severity band: `high_or_medium`
- Rationale: Signature-message binding bugs can authorize the wrong operation, but this one is likely rather than confirmed because a concrete accepted exploit was not shown.

## False-Positive Cautions

- Storage formatting or unrelated cleanup hunks should not support this case.
- If signed bytes are already constrained by a shared helper on all paths, the patch may only deduplicate checks.
