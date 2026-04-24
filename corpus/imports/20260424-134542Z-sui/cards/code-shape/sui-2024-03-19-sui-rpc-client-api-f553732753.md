# Code-Shape Card

## Metadata

- ID: `sui-2024-03-19-sui-rpc-client-api-f553732753`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-rpc-epoch-filter-hardening`

## Code Shape Summary

- The supported finding is narrow: the patch adds an epoch-based authorization/filter layer to Sui's Anemo consensus RPC router. The evidence shows the pre-patch route had peer authorization via `AllowedPeers` and the patched route additionally applies `AllowedEpoch`, which rejects missing or mismatched `epoch` headers.

## Search Motifs

- state-transition-invariant enforced after parsing but before rpc-client-api state mutation
- rpc-client-api handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Add a request authorization/filter layer at the network routing boundary to validate protocol-context metadata before RPC dispatch.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The value is only advisory and is recomputed from canonical local consensus state before use.
