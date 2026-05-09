---
case_id: case_20200521_ee1f218e76
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2020-05-21
source_refs:
  - git:ee1f218e764e725cdc8b4e4d244d7c9a3067343f
  - "core/src/rpc.rs:1609"
  - "core/src/rpc.rs:2687"
  - "core/src/rpc.rs:685"
  - "core/src/rpc.rs:1626"
bug_class: rpc-input-validation-panic-hardening
impact_type:
  - availability-hardening
confidence: medium
tags:
  - rpc
  - input-validation
  - error-handling
  - panic-avoidance
  - transaction-deserialization
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes RPC parameter error handling in `core/src/rpc.rs`. The strongest grounded change is replacing an unchecked `bs58::decode(...).into_vec().unwrap()` in `deserialize_bs58_transaction` with fallible error propagation returning `InvalidParams`. Other changes reclassify oversized transactions, transaction deserialization failures, pubkey parse failures, and signature parse failures from `InvalidRequest` to `InvalidParams`. The evidence supports input-validation hardening and error-shape cleanup, but does not establish an exploitable vulnerability or prove service-wide availability impact.

## Observed Patch Facts

1. In `core/src/rpc.rs`, the patch replaces `let wire_transaction = bs58::decode(bs58_transaction).into_vec().unwrap();` with `let wire_transaction = bs58::decode(bs58_transaction)`.

2. In `core/src/rpc.rs`, the patch replaces `let res = io.handle_request_sync(req, meta.clone());` with `let res = io.handle_request_sync(req, meta);`.

3. In `core/src/rpc.rs`, the patch replaces `input.parse().map_err(|_e| Error::invalid_request())` with `input`.

4. In `core/src/rpc.rs`, the patch replaces `Error::invalid_request()` with `Error::invalid_params(&err.to_string())`.

## Project Context

The changed code sits primarily in `core/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/src/rpc_error.rs`, `core/src/crds_gossip_error.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/rpc_pubsub.rs`, `core/src/blockstream_service.rs`. The strongest project-level identifiers around this patch are `Error::invalid_params`, `Error::invalid_request`, `serde_json::from_str`, and `Error`.

## Before/After Behavior

Before the patch, malformed base58 transaction input could reach an unchecked `unwrap()` in `deserialize_bs58_transaction`; after the patch, base58 decode errors are converted to `Error::invalid_params`. Before the patch, oversized transactions, bincode transaction deserialization failures, pubkey parse failures, and signature parse failures returned generic `InvalidRequest`; after the patch, they return targeted `InvalidParams` errors. The regression test was updated to expect `InvalidParams` for a bad `sendTransaction` request.

# Root Cause

RPC parameter validation used an unchecked unwrap for base58 transaction decoding and mapped several malformed client-parameter cases to generic request errors. The provided evidence does not prove state corruption, consensus impact, authentication bypass, ledger mutation, validator shutdown, or a confirmed remote denial of service.

## Walkthrough

1. A client-supplied `sendTransaction` parameter reaches `deserialize_bs58_transaction` as a base58 string.

2. The old code decoded it with `bs58::decode(bs58_transaction).into_vec().unwrap()`.

3. The patched code maps base58 decode failures to `Error::invalid_params(...)` and returns early.

4. The same function now reports oversized decoded wire data as `InvalidParams` instead of `InvalidRequest`.

5. Bincode transaction deserialization failures are also mapped to `InvalidParams`.

6. RPC pubkey and signature parsing helpers now return parse-specific `InvalidParams` errors.

7. The updated test checks that bad `sendTransaction` input returns the JSON-RPC `InvalidParams` code.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/rpc.rs | 1609 | Decodes client-supplied bs58 sendTransaction payload and now returns InvalidParams instead of panicking on decode failure. |
| core/src/rpc.rs | 1616 | Rejects transactions at or above PACKET_DATA_SIZE with a targeted InvalidParams error. |
| core/src/rpc.rs | 1626 | Maps bincode transaction deserialization failures to InvalidParams instead of InvalidRequest. |
| core/src/rpc.rs | 685 | Validates RPC pubkey and signature string parameters, returning parse-specific InvalidParams errors. |
| core/src/rpc.rs | 2658 | Regression test for bad sendTransaction input expecting InvalidParams. |

## Code Snippets

## Snippet 1

Context: `core/src/rpc.rs:1609` (changes persisted or aggregate state handling)

Before
```rust
fn deserialize_bs58_transaction(bs58_transaction: String) -> Result<(Vec<u8>, Transaction)> {
    let wire_transaction = bs58::decode(bs58_transaction).into_vec().unwrap();
    if wire_transaction.len() >= PACKET_DATA_SIZE {
        info!(
            "transaction too large: {} bytes (max: {} bytes)",
            wire_transaction.len(),
            PACKET_DATA_SIZE
```
After
```rust
fn deserialize_bs58_transaction(bs58_transaction: String) -> Result<(Vec<u8>, Transaction)> {
    let wire_transaction = bs58::decode(bs58_transaction)
        .into_vec()
        .map_err(|e| Error::invalid_params(format!("{:?}", e)))?;
    if wire_transaction.len() >= PACKET_DATA_SIZE {
        let err = format!(
            "transaction too large: {} bytes (max: {} bytes)",
```

## Snippet 2

Context: `core/src/rpc.rs:2687` (changes the branch that decides whether execution stops or continues)

Before
```rust
let req = r#"{"jsonrpc":"2.0","id":1,"method":"sendTransaction","params":["37u9WtQpcm6ULa3Vmu7ySnANv"]}"#;
        let res = io.handle_request_sync(req, meta.clone());
        let expected =
            r#"{"jsonrpc":"2.0","error":{"code":-32600,"message":"Invalid request"},"id":1}"#;
        let expected: Response =
            serde_json::from_str(expected).expect("expected response deserialization");
        let result: Response = serde_json::from_str(&res.expect("actual response"))
```
After
```rust
let req = r#"{"jsonrpc":"2.0","id":1,"method":"sendTransaction","params":["37u9WtQpcm6ULa3Vmu7ySnANv"]}"#;
        let res = io.handle_request_sync(req, meta);
        let json: Value = serde_json::from_str(&res.unwrap()).unwrap();
        let error = &json["error"];
        assert_eq!(error["code"], ErrorCode::InvalidParams.code());
    }
```

## Snippet 3

Context: `core/src/rpc.rs:685` (changes a sensitive control or state-update path)

Before
```rust
fn verify_pubkey(input: String) -> Result<Pubkey> {
    input.parse().map_err(|_e| Error::invalid_request())
}

fn verify_signature(input: &str) -> Result<Signature> {
    input.parse().map_err(|_e| Error::invalid_request())
}
```
After
```rust
fn verify_pubkey(input: String) -> Result<Pubkey> {
    input
        .parse()
        .map_err(|e| Error::invalid_params(format!("{:?}", e)))
}

fn verify_signature(input: &str) -> Result<Signature> {
```

## Snippet 4

Context: `core/src/rpc.rs:1626` (changes a sensitive control or state-update path)

Before
```rust
.map_err(|err| {
            info!("transaction deserialize error: {:?}", err);
            Error::invalid_request()
        })
        .map(|transaction| (wire_transaction, transaction))
```
After
```rust
.map_err(|err| {
            info!("transaction deserialize error: {:?}", err);
            Error::invalid_params(&err.to_string())
        })
        .map(|transaction| (wire_transaction, transaction))
```

# Fix Pattern

Replace unchecked decoding and generic request errors at the RPC boundary with fallible parameter validation that returns structured `InvalidParams` responses.

## How It Was Fixed

The patch removed the unchecked base58 decode `unwrap()` and used `.map_err(...)?` to propagate decode errors as `InvalidParams`. It also changed related validation and deserialization failures to return `InvalidParams` and updated the regression test expectation.

# Why It Matters

1. Malformed RPC input is handled through structured error paths.

2. The removed unwrap is security-relevant hardening, but exploitability is not shown.

3. Most surrounding changes are error-code reclassification.

4. No evidence supports state corruption or consensus impact.

# Evidence Notes

Primary evidence is limited to `core/src/rpc.rs`: `deserialize_bs58_transaction` replaced `into_vec().unwrap()` with `map_err(...)?`; size and bincode deserialization failures now return `InvalidParams`; `verify_pubkey` and `verify_signature` now return parse-specific `InvalidParams`; the test now checks `ErrorCode::InvalidParams`. The evidence does not show that the prior panic escaped the RPC framework, crashed the process, affected consensus, or mutated state. Protocol security invariant: Client-supplied JSON-RPC parameters should be decoded and validated through fallible paths that return structured RPC errors rather than panicking or misclassifying malformed input. Verification notes: The patch does not prove a remote process crash or validator shutdown from the prior unwrap. The patch does not show malformed transactions reaching ledger state, consensus, or storage mutation. The patch does not establish state corruption despite the heuristic baseline suggesting it. The error-code reclassification alone is API behavior cleanup unless tied to the removed unwrap. No authentication, authorization, or signature-verification bypass is shown. No proof of validator shutdown or process-wide crash is provided. No malformed-base58-specific regression test is shown; the shown test only checks a bad transaction response code. No storage, ledger, consensus, authorization, or signature-verification impact is evidenced. Classify as unclear security hardening rather than a confirmed vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `rpc-input-validation-panic-hardening`
Final impact type: `availability-hardening`
Final confidence: `medium`
Final tags: `rpc, input-validation, error-handling, panic-avoidance, transaction-deserialization`

The strongest evidence is the removal of an unchecked unwrap while decoding client-supplied base58 transaction input at the RPC boundary, replacing it with structured InvalidParams error handling. That is enough to retain this as security hardening because it removes an exposed risky panic condition, but the patch does not prove a concrete exploitable vulnerability, process-wide denial of service, state corruption, or consensus impact. The original state-corruption framing is too strong and should be narrowed to RPC input-validation panic hardening.

## Security Evidence

1. Client-controlled sendTransaction input reaches deserialize_bs58_transaction.
2. The old code used bs58::decode(...).into_vec().unwrap() on that input.
3. The patch converts base58 decode errors into Error::invalid_params instead of panicking.
4. A regression test exercises a bad sendTransaction request and expects InvalidParams.

## Missing Evidence

1. No proof that the prior unwrap crashed the validator process or caused service-wide denial of service.
2. No evidence of ledger mutation, state corruption, consensus failure, or signature-verification bypass.
3. No malformed-base58-specific exploit demonstration is shown.
4. Most surrounding changes are error-code reclassification from InvalidRequest to InvalidParams.

## Claim Boundaries

1. Treat as security hardening, not a confirmed vulnerability fix.
2. Do not claim state corruption or consensus impact.
3. Do not claim confirmed remote denial of service from the patch alone.
4. The supported claim is limited to safer RPC parameter decoding and panic avoidance for malformed input.
