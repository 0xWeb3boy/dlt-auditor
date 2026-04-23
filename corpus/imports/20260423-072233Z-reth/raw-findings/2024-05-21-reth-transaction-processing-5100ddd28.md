---
case_id: case_20240521_5100ddd28
project: reth
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2024-05-21
source_refs:
  - git:5100ddd28e3ae0396aa97633d6f700d77aefb50f
  - "crates/primitives/src/transaction/mod.rs:1463"
  - "crates/rpc/rpc/src/eth/api/transactions.rs:980"
  - "crates/rpc/rpc-types-compat/src/transaction/mod.rs:43"
  - "crates/primitives/src/transaction/eip4844.rs:47"
bug_class: input-validation
impact_type:
  - invalid-transaction-processing
confidence: medium
tags:
  - security-hardening
  - transaction-processing
  - transaction-validation
  - protocol-invariant
  - eip-4844
  - rpc
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a cross-layer correctness fix that tightens how EIP-4844 transactions are represented and built: the EIP-4844 type no longer stores a generic `TxKind`, and the RPC construction path no longer defaults a missing `to` field into `Create`. What is not established by the provided snippets is a concrete security failure mode such as successful acceptance into consensus, a remotely triggerable denial of service, or state corruption.

## Observed Patch Facts

1. In `crates/primitives/src/transaction/mod.rs`, the patch replaces `TransactionSigned { hash: Default::default(), signature: sig, transaction };` with `if let Transaction::Eip4844(ref mut tx_eip_4844) = transaction {`.

2. In `crates/rpc/rpc/src/eth/api/transactions.rs`, the patch replaces `kind: to.unwrap_or(RpcTransactionKind::Create),` with `#[allow(clippy::manual_unwrap_or_default)] // clippy is suggesting here unwrap_or_def...`.

3. In `crates/rpc/rpc-types-compat/src/transaction/mod.rs`, the patch replaces `let to = match signed_tx.kind() {` with `let to: Option<Address> = match signed_tx.kind() {`.

4. In `crates/primitives/src/transaction/eip4844.rs`, the patch replaces `/// The 160-bit address of the message call’s recipient or, for a contract creation` with `/// TODO(debt): this should be removed if we break the DB.`.

## Project Context

The changed code sits primarily in `crates/primitives/src/transaction`, `crates/primitives/src`, `crates/rpc/rpc/src/eth/api`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/rpc/rpc/src/eth/api/call.rs`, `crates/primitives/src/transaction/optimism.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/rpc/rpc/src/eth/api/call.rs`, `crates/primitives/src/revm/env.rs`. The strongest project-level identifiers around this patch are `Address::default`, `TxKind::Call`, `Some`, and `unwrap_or_default`.

## Before/After Behavior

Before the change, `TxEip4844.to` was a `TxKind`, so the EIP-4844 model could represent either call or create semantics, and the RPC path used `to.unwrap_or(RpcTransactionKind::Create)`, which would manufacture CREATE semantics when `to` was absent. After the change, `TxEip4844.to` is an `Address`, the RPC path only extracts an address from `Some(RpcTransactionKind::Call(to))` and otherwise writes `Address::default()`, and compatibility/construction code was updated to match that address-based representation. The added `placeholder` field is documented as compact/DB layout support, not as the primary fix.

# Root Cause

EIP-4844-specific rules were not encoded directly in the relevant representation and conversion layers. A generic destination type (`TxKind`) and a generic RPC default (`Create`) were reused in a context that appears to require an address-only recipient model.

## Walkthrough

1. `crates/primitives/src/transaction/eip4844.rs` changes `TxEip4844.to` from `TxKind` to `Address`, which removes CREATE as a directly representable state in that struct.

2. `crates/rpc/rpc/src/eth/api/transactions.rs` stops using `to.unwrap_or(RpcTransactionKind::Create)` and instead only accepts `Some(RpcTransactionKind::Call(to))` when deriving the address for this transaction shape.

3. `crates/rpc/rpc-types-compat/src/transaction/mod.rs` explicitly materializes `Option<Address>` from a signed transaction kind, keeping the outward view aligned with the narrowed representation.

4. `crates/primitives/src/transaction/mod.rs` updates EIP-4844 arbitrary construction so the new `placeholder` field tracks whether `to` is the default address, which matches the revised encoding/layout expectations.

5. These snippets show invariant tightening across model and conversion code, but they do not by themselves show exploitability or prior acceptance of an invalid transaction through consensus-critical paths.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/primitives/src/transaction/eip4844.rs | 47 | Core EIP-4844 transaction model; removes CREATE-capable destination encoding and stores only an address recipient. |
| crates/rpc/rpc/src/eth/api/transactions.rs | 980 | RPC request to internal transaction conversion; prevents missing `to` from being interpreted as CREATE for EIP-4844 transactions. |
| crates/rpc/rpc-types-compat/src/transaction/mod.rs | 43 | Compatibility/export path that preserves call-vs-create semantics when materializing RPC transaction views. |
| crates/primitives/src/transaction/mod.rs | 1463 | Construction/test path updated to keep the new EIP-4844 encoding invariant consistent with recipient presence. |

## Code Snippets

## Snippet 1

Context: `crates/primitives/src/transaction/mod.rs:1463` (changes a sensitive control or state-update path)

Before
```rust
.unwrap_or(sig);

                let mut tx =
                    TransactionSigned { hash: Default::default(), signature: sig, transaction };
```
After
```rust
.unwrap_or(sig);

                if let Transaction::Eip4844(ref mut tx_eip_4844) = transaction {
                    tx_eip_4844.placeholder =
                        if tx_eip_4844.to != Address::default() { Some(()) } else { None };
                }

                let mut tx =
```

## Snippet 2

Context: `crates/rpc/rpc/src/eth/api/transactions.rs:980` (changes a sensitive control or state-update path)

Before
```rust
value: value.unwrap_or_default(),
                    input: data.into_input().unwrap_or_default(),
                    kind: to.unwrap_or(RpcTransactionKind::Create),
                    access_list: access_list.unwrap_or_default(),
```
After
```rust
value: value.unwrap_or_default(),
                    input: data.into_input().unwrap_or_default(),
                    #[allow(clippy::manual_unwrap_or_default)] // clippy is suggesting here unwrap_or_default
                    to: match to {
                        Some(RpcTransactionKind::Call(to)) => to,
                        _ => Address::default(),
                    },
                    access_list: access_list.unwrap_or_default(),
```

## Snippet 3

Context: `crates/rpc/rpc-types-compat/src/transaction/mod.rs:43` (changes a sensitive control or state-update path)

Before
```rust
let signed_tx = tx.into_signed();

    let to = match signed_tx.kind() {
        TxKind::Create => None,
        TxKind::Call(to) => Some(*to),
    };
```
After
```rust
let signed_tx = tx.into_signed();

    let to: Option<Address> = match signed_tx.kind() {
        TxKind::Create => None,
        TxKind::Call(to) => Some(Address(*to)),
    };
```

## Snippet 4

Context: `crates/primitives/src/transaction/eip4844.rs:47` (changes a sensitive control or state-update path)

Before
```rust
/// This is also known as `GasTipCap`
    pub max_priority_fee_per_gas: u128,
    /// The 160-bit address of the message call’s recipient or, for a contract creation
    /// transaction, ∅, used here to denote the only member of B0 ; formally Tt.
    pub to: TxKind,
    /// A scalar value equal to the number of Wei to
    /// be transferred to the message call’s recipient or,
```
After
```rust
/// This is also known as `GasTipCap`
    pub max_priority_fee_per_gas: u128,
    /// TODO(debt): this should be removed if we break the DB.
    /// Makes sure that the Compact bitflag struct has one bit after the above field:
    /// <https://github.com/paradigmxyz/reth/pull/8291#issuecomment-2117545016>
    pub placeholder: Option<CompactPlaceholder>,
    /// The 160-bit address of the message call’s recipient.
    pub to: Address,
```

# Fix Pattern

Encode the protocol-specific shape in the data model and remove generic conversion defaults that can synthesize invalid variants for that protocol.

## How It Was Fixed

The patch narrows the EIP-4844 transaction representation to store an `Address` recipient instead of a generic `TxKind`, updates the RPC transaction-building path so it no longer defaults missing `to` into CREATE semantics for this type, and adjusts compatibility/support code to preserve the new address-only shape. The `placeholder` addition appears to be a serialization/layout compatibility aid for the new struct layout.

# Why It Matters

1. It reduces the chance that EIP-4844 transactions are represented in an invalid create-style form inside the codebase.

2. It makes the intended transaction shape explicit in the type definition instead of relying on downstream interpretation.

3. It aligns RPC construction and compatibility layers with the narrowed model, reducing cross-layer inconsistency.

4. The provided evidence does not show a proven security exploit, so the impact should not be overstated.

# Evidence Notes

The strongest grounded evidence is the change from `TxKind` to `Address` in `TxEip4844`, plus the RPC conversion change that removes `unwrap_or(...Create)` and only extracts `Call(to)` into an address. The compatibility-layer adjustment to `Option<Address>` is consistent with that model change. The `placeholder` field is explicitly documented as a DB/compact bitflag compatibility measure. The provided snippets do not include the actual diffs for the touched consensus or transaction-pool validation files, so claims about consensus acceptance, remote reachability, or rejection behavior beyond these shown conversions are not established here. Protocol security invariant: EIP-4844 transactions should use a concrete recipient address in this codepath, not a generic call-or-create destination that can express CREATE semantics. Verification notes: The provided patch evidence does not prove a remotely triggerable denial-of-service or consensus split in deployed nodes. The evidence does not show whether invalid EIP-4844 CREATE transactions could previously pass all the way through block import, only that the representation and validation paths were tightened. The patch does not show signature forgery, authorization bypass, or value-transfer corruption. The added placeholder field appears to preserve codec/layout compatibility and is not itself evidence of a separate security issue. The supplied evidence is sufficient to support a representation/conversion invariant fix. The supplied evidence is not sufficient to prove a vulnerability with demonstrated exploitability or runtime impact. No test evidence or rejection-path evidence is provided here. Security relevance is plausible but not established strongly enough to keep this as a confirmed or likely security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `input-validation`
Final impact type: `invalid-transaction-processing`
Final confidence: `medium`
Final tags: `security-hardening, transaction-processing, transaction-validation, protocol-invariant, eip-4844, rpc`

The patch evidence supports a security-relevant hardening change, not a proven exploitable vulnerability. The code removes CREATE as a representable form for EIP-4844 transactions by changing the core field from `TxKind` to `Address`, and it stops the RPC construction path from defaulting a missing destination into CREATE semantics. That is a meaningful tightening of transaction-validation behavior in a security-sensitive path, but the provided snippets do not prove that invalid transactions were previously accepted through consensus or that a concrete attack impact occurred.

## Security Evidence

1. The commit explicitly targets preventing CREATE transactions for EIP-4844 types.
2. `TxEip4844.to` changes from `TxKind` to `Address`, removing CREATE as an expressible state in the type.
3. The RPC conversion path no longer defaults missing `to` to `Create`; it only extracts a destination from `Call(to)`.
4. Supporting conversion and construction code is updated to preserve the narrowed invariant across layers.

## Missing Evidence

1. No provided diff from the consensus or transaction-pool validation files shows the exact rejection path.
2. No test or runtime evidence shows invalid EIP-4844 CREATE transactions were previously accepted end-to-end.
3. No evidence demonstrates exploitability, remote triggerability, denial of service, consensus impact, or fund impact.

## Claim Boundaries

1. Supported: the patch hardens protocol-specific transaction representation and RPC conversion against invalid EIP-4844 CREATE semantics.
2. Not supported: a confirmed exploitable security bug in deployed nodes.
3. Not supported: consensus split, remote DoS, signature bypass, authorization bypass, or fund-loss claims.
4. The added `placeholder` field is evidenced as codec/layout compatibility support, not as a separate security issue.
