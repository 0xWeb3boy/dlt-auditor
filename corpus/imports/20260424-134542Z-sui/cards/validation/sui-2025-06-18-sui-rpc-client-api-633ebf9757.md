# Validation Card

## Metadata

- ID: `sui-2025-06-18-sui-rpc-client-api-633ebf9757`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transport-security-hardening`

## What Confirmed The Issue

- Release notes state TLS is now required to connect to the validator gRPC interface.
- The validator client setup in crates/sui-tool/src/lib.rs now calls connect_lazy with tls_config unconditionally.
- TLS client config is built from validator network public key bytes and a validator server name.
- Server-side tests are updated to bind test gRPC servers with rustls server config instead of None.

## What Could Have Invalidated It

- No supplied implementation snippet shows server-side rejection of non-TLS validator gRPC connections outside tests.
- No evidence demonstrates a concrete exploit, downgrade attack, MITM, replay, or request forgery.
- No evidence shows changes to transaction signature validation, nonce handling, or consensus rules.
- No regression test explicitly proving plaintext validator gRPC is refused is shown.

## Severity Guidance

- Expected impact band: plaintext-transport-exposure
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Valid claim: validator gRPC transport configuration was hardened toward TLS-required operation.
- Valid claim: at least one validator client path no longer allows omitting TLS config.
- Unsupported claim: this fixed replay or signature validation logic.
- Unsupported claim: this proves a concrete security vulnerability was exploitable before the change.
