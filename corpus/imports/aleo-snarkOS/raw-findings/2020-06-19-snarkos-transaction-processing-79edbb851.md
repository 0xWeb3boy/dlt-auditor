---
case_id: case_20200619_79edbb851
project: snarkos
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2020-06-19
source_refs:
  - git:79edbb8517a844e047f49c0bb12e07813e15667a
  - "rpc/src/rpc_impl.rs:141"
  - "rpc/src/rpc_impl.rs:290"
  - "rpc/src/rpc_trait.rs:39"
  - "rpc/src/rpc_trait.rs:24"
bug_class: rpc-attack-surface-reduction
impact_type:
  - attack-surface-reduction
  - potential-unauthorized-record-access
confidence: medium
tags:
  - blockchain-core
  - rpc
  - access-control
  - attack-surface-reduction
  - record-access
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch removes several JSON-RPC methods from the exported `RpcFunctions` trait and their shown implementations from `RpcImpl`, including `createrawtransaction` and record-access methods such as `fetchrecordcommitments` and `getrawrecord`. A nearby TODO mentions adding password guarding, so the change may be security-motivated RPC surface reduction. However, the evidence does not establish a concrete vulnerability, exploit path, deployment exposure, or actual secret disclosure. Treat this as unclear security relevance rather than a confirmed or likely security fix.

## Observed Patch Facts

1. In `rpc/src/rpc_impl.rs`, the patch replaces `fn create_raw_transaction(&self, transaction_input: TransactionInputs) -> Result<(Str...` with `/// Returns information about a transaction from serialized transaction bytes.`.

2. In `rpc/src/rpc_impl.rs`, the patch removes `// TODO (raychu86) add password guarding`.

3. In `rpc/src/rpc_trait.rs`, the patch removes `// Record access`.

4. In `rpc/src/rpc_trait.rs`, the patch removes `#[rpc(name = "createrawtransaction")]`.

## Project Context

The changed code sits primarily in `rpc/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `rpc/src/rpc_server.rs`, `rpc/src/rpc_types.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `rpc/src/rpc_server.rs`. The strongest project-level identifiers around this patch are `Result`, `RpcError`, `transaction_input`, and `Components::NUM_OUTPUT_RECORDS`.

## Before/After Behavior

Before the patch, the RPC trait declared `createrawtransaction`, `fetchrecordcommitments`, and `getrawrecord`, and the implementation included transaction construction plus stored-record commitment access. After the patch, those declarations and shown implementations are removed, leaving nearby decode and lookup RPC methods.

# Root Cause

Not established as a vulnerability. The grounded issue is that methods associated with transaction construction and record access were present on the JSON-RPC trait while a nearby comment indicated password guarding was still TODO. The evidence does not prove that this created an exploitable access-control flaw.

## Walkthrough

1. `RpcImpl` is registered with the JSON-RPC handler through `to_delegate()`, so trait-declared RPC methods are part of the served RPC interface.

2. Before the patch, `rpc/src/rpc_trait.rs` declared `createrawtransaction`.

3. Before the patch, `rpc/src/rpc_impl.rs` implemented `create_raw_transaction` and began by asserting counts for records, keys, and recipients before transaction-building logic.

4. Before the patch, the trait also declared record-access RPC methods including `fetchrecordcommitments` and `getrawrecord`.

5. The shown `fetch_record_commtiments` implementation read stored record commitments from storage and returned hex strings.

6. A nearby comment said password guarding should be added, which supports possible security motivation but not a proven vulnerability.

7. After the patch, these RPC declarations and shown implementation bodies are removed from the exported surface.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| rpc/src/rpc_trait.rs | 24 | removed `createrawtransaction` from the exported JSON-RPC trait |
| rpc/src/rpc_trait.rs | 39 | removed record-access RPC methods such as `fetchrecordcommitments` and `getrawrecord` from the exported trait |
| rpc/src/rpc_impl.rs | 141 | removed `create_raw_transaction` implementation from `RpcImpl` RPC surface |
| rpc/src/rpc_impl.rs | 290 | removed unguarded stored-record access implementation marked with password-guarding TODO |
| rpc/src/rpc_server.rs | 16 | context shows `RpcImpl` is exposed through JSON-RPC delegate on the HTTP server |

## Code Snippets

## Snippet 1

Context: `rpc/src/rpc_impl.rs:141` (changes signature or replay validation logic)

Before
```rust
}

    fn create_raw_transaction(&self, transaction_input: TransactionInputs) -> Result<(String, Vec<String>), RpcError> {
        let rng = &mut thread_rng();

        assert!(transaction_input.old_records.len() > 0);
        assert!(transaction_input.old_records.len() <= Components::NUM_OUTPUT_RECORDS);
        assert!(transaction_input.old_account_private_keys.len() > 0);
```
After
```rust
}

    /// Returns information about a transaction from serialized transaction bytes.
    fn decode_raw_transaction(&self, transaction_bytes: String) -> Result<TransactionInfo, RpcError> {
```

## Snippet 2

Context: `rpc/src/rpc_impl.rs:290` (changes persisted or aggregate state handling)

Before
```rust
})
    }

    // TODO (raychu86) add password guarding

    /// Fetch the node's stored record commitments
    fn fetch_record_commtiments(&self) -> Result<Vec<String>, RpcError> {
        let record_commitments = self.storage.get_record_commitments(100)?;
```
After
```rust
})
    }
}
```

## Snippet 3

Context: `rpc/src/rpc_trait.rs:39` (changes a sensitive control or state-update path)

Before
```rust
fn get_block_template(&self) -> Result<BlockTemplate, RpcError>;

    // Record access

    #[rpc(name = "decoderecord")]
    fn decode_record(&self, record_bytes: String) -> Result<RecordInfo, RpcError>;

    #[rpc(name = "fetchrecordcommitments")]
```
After
```rust
fn get_block_template(&self) -> Result<BlockTemplate, RpcError>;

    #[rpc(name = "decoderecord")]
    fn decode_record(&self, record_bytes: String) -> Result<RecordInfo, RpcError>;
}
```

## Snippet 4

Context: `rpc/src/rpc_trait.rs:24` (changes a sensitive control or state-update path)

Before
```rust
fn get_transaction_info(&self, transaction_id: String) -> Result<TransactionInfo, RpcError>;

    #[rpc(name = "createrawtransaction")]
    fn create_raw_transaction(&self, transaction_input: TransactionInputs) -> Result<(String, Vec<String>), RpcError>;

    #[rpc(name = "decoderawtransaction")]
    fn decode_raw_transaction(&self, transaction_bytes: String) -> Result<TransactionInfo, RpcError>;
```
After
```rust
fn get_transaction_info(&self, transaction_id: String) -> Result<TransactionInfo, RpcError>;

    #[rpc(name = "decoderawtransaction")]
    fn decode_raw_transaction(&self, transaction_bytes: String) -> Result<TransactionInfo, RpcError>;
```

# Fix Pattern

Remove RPC methods from the exported JSON-RPC surface instead of adding authentication or changing validation logic.

## How It Was Fixed

The patch deleted `createrawtransaction`, `fetchrecordcommitments`, and `getrawrecord` declarations from `rpc/src/rpc_trait.rs` and removed the shown corresponding implementation code from `rpc/src/rpc_impl.rs`.

# Why It Matters

1. Reduces exposed RPC functionality.

2. Removes record-access code near a password-guarding TODO.

3. Does not prove exploitability or unauthorized access from the provided evidence.

4. Does not change consensus or cryptographic validation logic.

# Evidence Notes

Supported by diffs in `rpc/src/rpc_trait.rs` and `rpc/src/rpc_impl.rs`, plus server context showing RPC delegate registration. Unsupported claims include remote exploitability, public network exposure, private key leakage, consensus impact, cryptographic flaw, or a confirmed access-control bypass. Protocol security invariant: Potentially sensitive record or transaction RPC methods should not be exported through the JSON-RPC delegate without an intended access guard, but the supplied evidence does not establish that these methods were exploitable or exposed to untrusted callers. Verification notes: The patch does not prove remote exploitability by itself. The patch does not show whether deployments exposed the RPC port to untrusted networks. The patch does not prove private keys were stored or leaked by `create_raw_transaction`; it only shows sensitive transaction construction was removed from the RPC API. The patch does not change consensus validation or cryptographic verification logic. The patch does not add authentication; it removes RPC methods from the exported surface. No tests or exploit evidence are provided. No deployment configuration proves untrusted RPC access. No authentication change is shown; the patch removes methods. Security relevance is plausible but not established enough to keep in a vulnerability corpus. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `rpc-attack-surface-reduction`
Final impact type: `attack-surface-reduction, potential-unauthorized-record-access`
Final confidence: `medium`
Final tags: `blockchain-core, rpc, access-control, attack-surface-reduction, record-access`

The patch does not prove a concrete vulnerability, but it does remove JSON-RPC methods from an interface served through the RPC delegate on a server bound to 0.0.0.0. The removed record-access methods sit next to a TODO to add password guarding, which is direct evidence that the exposed functionality was considered guard-worthy. This supports retaining the case as security hardening, not as a confirmed security fix or input-validation issue.

## Security Evidence

1. Removed exported JSON-RPC declarations for createrawtransaction, fetchrecordcommitments, and getrawrecord.
2. Removed corresponding RpcImpl functionality including stored record commitment access.
3. A nearby comment explicitly says password guarding should be added before the record-access methods.
4. Project context shows RpcImpl is registered via to_delegate() and served over HTTP on 0.0.0.0.

## Missing Evidence

1. No exploit, advisory, or vulnerability description is provided.
2. No proof that the RPC endpoint was exposed to untrusted users in real deployments.
3. No authentication or authorization model is shown before or after the patch.
4. No evidence that private keys or raw records were actually leaked or misused.

## Claim Boundaries

1. Validate only as security hardening through RPC surface reduction.
2. Do not claim a confirmed access-control bypass.
3. Do not claim consensus, signature, replay, or cryptographic validation impact.
4. Do not classify as input validation; the meaningful change is removal of exposed RPC methods.
