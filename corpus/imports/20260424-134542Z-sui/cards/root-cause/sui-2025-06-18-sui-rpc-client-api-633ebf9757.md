# Root-Cause Card

## Metadata

- ID: `sui-2025-06-18-sui-rpc-client-api-633ebf9757`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transport-security-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: The input-validation property must be enforced before untrusted protocol data reaches a security-sensitive sink.

## Trust Boundary

- Boundary: remote client/proxy request or response -> node API trust decision

## Attack Surface

- Entrypoint type: rpc-handler
- Sensitive sink: committing security-sensitive protocol state

## Impact Pattern

- Primary impact: plaintext-transport-exposure
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The supported evidence shows a transport-security hardening change for validator gRPC: the release notes state TLS is now required, and the shown sui-tool validator client path now passes a rustls TLS config directly to `connect_lazy` instead of gating it on `use_tls`.
