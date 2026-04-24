# Code-Shape Card

## Metadata

- ID: `sui-2025-06-18-sui-rpc-client-api-633ebf9757`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transport-security-hardening`

## Code Shape Summary

- The supported evidence shows a transport-security hardening change for validator gRPC: the release notes state TLS is now required, and the shown sui-tool validator client path now passes a rustls TLS config directly to `connect_lazy` instead of gating it on `use_tls`.

## Search Motifs

- input-validation enforced after parsing but before rpc-client-api state mutation
- rpc-client-api handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- The rpc-client-api sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- Require TLS configuration at validator gRPC connection setup instead of allowing conditional or absent TLS config at the observed call sites.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
