# Code-Shape Card

## Metadata

- ID: `sui-2025-03-26-sui-cryptography-aba86cd0d7`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-consensus-object-ownership-authentication`

## Code Shape Summary

- The evidence supports a likely security fix in Sui transaction input validation for ConsensusV2 objects. The commit message says object ownership is now verified at signing time, and the diff adds access to ConsensusV2 authenticator metadata while separating ConsensusV2 handling from ordinary shared-object version checks.

## Search Motifs

- authorization enforced after parsing but before cryptography state mutation
- cryptography handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Expose owner authenticator metadata and use a ConsensusV2-specific transaction input validation path instead of relying only on shared-object start-version checks.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The value is only advisory and is recomputed from canonical local consensus state before use.
- A later mandatory ownership or capability check rejects the request before any state change.
