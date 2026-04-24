---
case_id: case_20250618_633ebf9757
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: rpc-client-api
source_quality: medium
date: 2025-06-18
source_refs:
  - git:633ebf9757c43f0b8461e85b8da77c417510f701
  - "crates/mysten-network/src/server.rs:246"
  - "crates/mysten-network/src/server.rs:323"
  - "crates/mysten-network/src/server.rs:366"
  - "crates/sui-tool/src/lib.rs:110"
bug_class: transport-security-hardening
impact_type:
  - plaintext-transport-exposure
confidence: medium
tags:
  - blockchain-core
  - rpc-client-api
  - grpc
  - tls
  - transport-security
  - validator-network
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported evidence shows a transport-security hardening change for validator gRPC: the release notes state TLS is now required, and the shown sui-tool validator client path now passes a rustls TLS config directly to `connect_lazy` instead of gating it on `use_tls`. The server-side evidence shown is test setup updated to use TLS configs, not direct implementation proof of enforcement.

## Observed Patch Facts

1. In `crates/mysten-network/src/server.rs`, the patch replaces `.bind(&address, None)` with `let keypair = Ed25519KeyPair::generate(&mut rand::thread_rng());`.

2. In `crates/mysten-network/src/server.rs`, the patch replaces `.bind(&address, None)` with `let keypair = Ed25519KeyPair::generate(&mut rand::thread_rng());`.

3. In `crates/mysten-network/src/server.rs`, the patch replaces `let server_handle = config.server_builder().bind(&address, None).await.unwrap();` with `let keypair = Ed25519KeyPair::generate(&mut rand::thread_rng());`.

4. In `crates/sui-tool/src/lib.rs`, the patch replaces `if use_tls {` with `.connect_lazy(&net_addr, tls_config)`.

## Project Context

The changed code sits primarily in `crates/mysten-network/src`, `crates/mysten-network`, `crates/sui-tool/src`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `crates/mysten-network/src/config.rs`, `crates/sui-tool/src/commands.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-tool/src/main.rs`, `crates/sui-tool/src/commands.rs`. The strongest project-level identifiers around this patch are `config`, `Config::new`, `Ed25519KeyPair::generate`, and `rand::thread_rng`.

## Before/After Behavior

Before the patch, the shown sui-tool validator client setup could pass no TLS config via `use_tls.then_some(tls_config)`, and shown mysten-network tests bound gRPC servers with `None` TLS config. After the patch, the sui-tool path always passes the generated TLS client config, and the shown tests bind with `sui_tls::create_rustls_server_config(...)`.

# Root Cause

The prior observed validator gRPC client setup allowed TLS to be omitted at a transport configuration boundary. The provided evidence does not establish a concrete exploit, but it supports that plaintext-capable validator gRPC setup was being removed or reduced.

## Walkthrough

1. The commit release notes explicitly say TLS is now required to connect to the validator gRPC interface.

2. In `crates/sui-tool/src/lib.rs`, the validator client code creates a rustls client config from each validator's network public key bytes.

3. Before the change, that TLS config was passed only when `use_tls` was true.

4. After the change, the TLS config is passed directly to `net_config.connect_lazy`.

5. The shown `crates/mysten-network/src/server.rs` changes are tests updated from `None` TLS config to rustls server config, supporting the new TLS-required baseline but not proving server enforcement by themselves.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-tool/src/lib.rs | 110 | validator gRPC client setup now passes TLS client config unconditionally to connect_lazy |
| crates/mysten-network/src/server.rs | 246 | server test setup now binds with rustls server config instead of None |
| crates/mysten-network/src/server.rs | 323 | server metrics/error-path test updated to use TLS-enabled server/client setup |
| crates/mysten-network/src/server.rs | 366 | multiaddr server test now creates TLS server config before bind |

## Code Snippets

## Snippet 1

Context: `crates/mysten-network/src/server.rs:246` (changes the branch that decides whether execution stops or continues)

Before
```rust
let address: Multiaddr = "/ip4/127.0.0.1/tcp/0/http".parse().unwrap();
        let config = Config::new();

        let server = config
            .server_builder_with_metrics(metrics.clone())
            .bind(&address, None)
            .await
            .unwrap();
```
After
```rust
let address: Multiaddr = "/ip4/127.0.0.1/tcp/0/http".parse().unwrap();
        let config = Config::new();
        let keypair = Ed25519KeyPair::generate(&mut rand::thread_rng());

        let server = config
            .server_builder_with_metrics(metrics.clone())
            .bind(
                &address,
```

## Snippet 2

Context: `crates/mysten-network/src/server.rs:323` (changes the branch that decides whether execution stops or continues)

Before
```rust
let address: Multiaddr = "/ip4/127.0.0.1/tcp/0/http".parse().unwrap();
        let config = Config::new();

        let server = config
            .server_builder_with_metrics(metrics.clone())
            .bind(&address, None)
            .await
            .unwrap();
```
After
```rust
let address: Multiaddr = "/ip4/127.0.0.1/tcp/0/http".parse().unwrap();
        let config = Config::new();
        let keypair = Ed25519KeyPair::generate(&mut rand::thread_rng());

        let server = config
            .server_builder_with_metrics(metrics.clone())
            .bind(
                &address,
```

## Snippet 3

Context: `crates/mysten-network/src/server.rs:366` (changes the branch that decides whether execution stops or continues)

Before
```rust
async fn test_multiaddr(address: Multiaddr) {
        let config = Config::new();
        let server_handle = config.server_builder().bind(&address, None).await.unwrap();
        let address = server_handle.local_addr().to_owned();
        let channel = config.connect(&address, None).await.unwrap();
        let mut client = HealthClient::new(channel);
```
After
```rust
async fn test_multiaddr(address: Multiaddr) {
        let config = Config::new();
        let keypair = Ed25519KeyPair::generate(&mut rand::thread_rng());

        let server_handle = config
            .server_builder()
            .bind(
                &address,
```

## Snippet 4

Context: `crates/sui-tool/src/lib.rs:110` (changes a sensitive control or state-update path)

Before
```rust
None,
        );
        if use_tls {
            net_addr = net_addr.rewrite_http_to_https();
        }
        let channel = net_config
            .connect_lazy(&net_addr, use_tls.then_some(tls_config))
            .map_err(|err| anyhow!(err.to_string()))?;
```
After
```rust
None,
        );
        let channel = net_config
            .connect_lazy(&net_addr, tls_config)
            .map_err(|err| anyhow!(err.to_string()))?;
        let client = NetworkAuthorityClient::new(channel);
```

# Fix Pattern

Require TLS configuration at validator gRPC connection setup instead of allowing conditional or absent TLS config at the observed call sites.

## How It Was Fixed

The sui-tool validator client path now passes the rustls client config unconditionally into `connect_lazy`. Related mysten-network tests now generate an Ed25519 keypair and bind test servers with `sui_tls::create_rustls_server_config(...)` rather than `None`.

# Why It Matters

1. Reduces or removes plaintext validator gRPC connectivity in the observed path.

2. Supports encrypted transport and server authentication for validator network clients.

3. Aligns tests with a TLS-required validator gRPC baseline.

4. Does not support claims about replay, signature validation, nonce handling, or consensus changes.

# Evidence Notes

Strongest evidence is `crates/sui-tool/src/lib.rs` line 110 plus the release-note text. The `server.rs` snippets are test code, so they should be treated as supporting evidence only. No supplied evidence proves a specific MITM exploit, transaction forgery, replay bug, or protocol-level consensus vulnerability. Protocol security invariant: Validator gRPC connections should use TLS configured with validator network identity material so the transport does not permit unauthenticated plaintext gRPC at supported validator connection points. Verification notes: No evidence proves a concrete exploit or successful man-in-the-middle attack. No evidence shows changes to transaction signature validation, nonce handling, or replay protection. No evidence shows protocol-level consensus rules changed. Server.rs evidence shown is test code, so implementation impact is inferred from adjacent changed files and commit metadata. Downgraded from confirmed/high to likely/medium because the implementation evidence is partial and server enforcement is mostly represented by tests in the supplied snippets. Rejected the heuristic replay-or-signature-validation framing as unsupported. Kept as security hardening because TLS requirement for validator gRPC is explicitly stated and reflected in the observed client path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `transport-security-hardening`
Final impact type: `plaintext-transport-exposure`
Final confidence: `medium`
Final tags: `blockchain-core, rpc-client-api, grpc, tls, transport-security, validator-network`

The supplied evidence supports keeping this as security hardening: the commit explicitly says TLS is now required for validator gRPC, and the shown client path now passes a rustls TLS config unconditionally instead of allowing it to be omitted behind a use_tls gate. The evidence does not support the original replay/signature-validation framing or a concrete exploitable vulnerability, so it should be retained only as transport-security hardening.

## Security Evidence

1. Release notes state TLS is now required to connect to the validator gRPC interface.
2. The validator client setup in crates/sui-tool/src/lib.rs now calls connect_lazy with tls_config unconditionally.
3. TLS client config is built from validator network public key bytes and a validator server name.
4. Server-side tests are updated to bind test gRPC servers with rustls server config instead of None.

## Missing Evidence

1. No supplied implementation snippet shows server-side rejection of non-TLS validator gRPC connections outside tests.
2. No evidence demonstrates a concrete exploit, downgrade attack, MITM, replay, or request forgery.
3. No evidence shows changes to transaction signature validation, nonce handling, or consensus rules.
4. No regression test explicitly proving plaintext validator gRPC is refused is shown.

## Claim Boundaries

1. Valid claim: validator gRPC transport configuration was hardened toward TLS-required operation.
2. Valid claim: at least one validator client path no longer allows omitting TLS config.
3. Unsupported claim: this fixed replay or signature validation logic.
4. Unsupported claim: this proves a concrete security vulnerability was exploitable before the change.
