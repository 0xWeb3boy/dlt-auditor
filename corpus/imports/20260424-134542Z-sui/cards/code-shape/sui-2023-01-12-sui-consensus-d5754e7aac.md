# Code-Shape Card

## Metadata

- ID: `sui-2023-01-12-sui-consensus-d5754e7aac`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-commitment`

## Code Shape Summary

- The patch is best treated as checkpoint integrity hardening. It adds user signatures to checkpoint contents because the commit message states checkpoint history otherwise had no record of submitted user signatures after transaction signatures were removed from the TransactionDigest commitment.

## Search Motifs

- signature-verification enforced after parsing but before consensus state mutation
- consensus handler accepts externally supplied protocol data
- alternate signed encodings accepted as equivalent
- missing epoch/domain/payload binding in verifier

## Typical Asymmetry

- The producer can vary signed bytes or context while the verifier accidentally treats distinct security domains as equivalent.

## Patch Pattern

- Persist the missing cryptographic authorization material in the checkpoint data model and populate it from consensus-processed certificate state.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The alternative encoding cannot be produced by an untrusted party or is normalized before verification.
- The value is only advisory and is recomputed from canonical local consensus state before use.
