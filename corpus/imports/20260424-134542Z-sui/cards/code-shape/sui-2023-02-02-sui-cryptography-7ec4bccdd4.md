# Code-Shape Card

## Metadata

- ID: `sui-2023-02-02-sui-cryptography-7ec4bccdd4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-quorum-hardening`

## Code Shape Summary

- The patch hardens Sui checkpoint certification by replacing `AuthorityWeakQuorumSignInfo` with `AuthorityStrongQuorumSignInfo` for `CertifiedCheckpointSummary` and related aggregation paths. The evidence supports consensus/checkpoint quorum hardening, not signature forgery, replay, nonce misuse, or a fully demonstrated exploit.

## Search Motifs

- state-transition-invariant enforced after parsing but before cryptography state mutation
- cryptography handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Encode the stronger quorum requirement in the checkpoint certificate type and aggregation path by replacing weak quorum signature information with strong quorum signature information.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The value is only advisory and is recomputed from canonical local consensus state before use.
