---
case_id: case_20200815_8b5ad567b
project: snarkos
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2020-08-15
source_refs:
  - git:8b5ad567b671ec7816e97a716a37ec8086636266
  - "rpc/src/rpc_impl_protected.rs:117"
  - "rpc/src/rpc_impl.rs:297"
  - "rpc/src/rpc_types.rs:111"
  - "rpc/src/rpc_types.rs:206"
bug_class: missing-authentication
impact_type:
  - unauthorized-rpc-access
  - potential-information-disclosure
confidence: medium
tags:
  - rpc
  - access-control
  - authentication
  - record-endpoints
  - hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a likely security fix for missing authentication on snarkOS record RPC endpoints. The strongest grounded change is the addition of a protected decode_record wrapper that calls validate_auth(meta) before processing parameters, together with evidence that record handling such as decrypt_record was removed from the public RpcFunctions implementation area. The full endpoint list and exploitability details are not proven by the supplied hunks.

## Observed Patch Facts

1. In `rpc/src/rpc_impl_protected.rs`, the patch replaces `/// Wrap authentication around 'create_account'` with `/// Wrap authentication around 'decode_record'`.

2. In `rpc/src/rpc_impl.rs`, the patch removes `// Record handling`.

3. In `rpc/src/rpc_types.rs`, the patch replaces `/// Additional metadata included with a transaction response` with `/// Record payload data`.

4. In `rpc/src/rpc_types.rs`, the patch replaces `/// Record payload data` with `/// Input for the 'createrawtransaction' rpc call`.

## Project Context

The changed code sits primarily in `rpc/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `rpc/src/rpc_trait.rs`, `rpc/src/rpc_server.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `rpc/src/rpc_trait.rs`. The strongest project-level identifiers around this patch are `payload`, `Record`, `derive`, and `Clone`.

## Before/After Behavior

Before the patch, the supplied evidence shows record handling, including decrypt_record, inside impl RpcFunctions for RpcImpl, which the traced context identifies as the public RPC implementation surface. After the patch, that record handling section is absent from the shown rpc_impl.rs after-context, and decode_record_protected is added in rpc_impl_protected.rs with validate_auth(meta) executed before request parsing.

# Root Cause

Record RPC logic was present on the public RPC implementation path instead of being consistently routed through protected wrappers that enforce validate_auth(meta).

## Walkthrough

1. rpc/src/rpc_trait.rs identifies RpcFunctions as the public RPC endpoint surface.

2. The before evidence for rpc/src/rpc_impl.rs shows a record handling section under impl RpcFunctions for RpcImpl, including decrypt_record.

3. The patch evidence shows that record handling section removed from the displayed public implementation area.

4. rpc/src/rpc_impl_protected.rs adds decode_record_protected.

5. decode_record_protected calls self.validate_auth(meta)? before matching Params, checking argument count, deserializing input, or dispatching.

6. Documentation files for public and private decoderecord/decryptrecord were touched, which supports an endpoint-surface change but does not independently prove the complete moved endpoint list.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| rpc/src/rpc_impl_protected.rs | 117 | adds protected decode_record RPC wrapper and enforces validate_auth(meta) before processing params |
| rpc/src/rpc_impl.rs | 297 | record handling implementation path removed from the public RpcFunctions area according to the before/after evidence |
| rpc/src/rpc_trait.rs | 1 | defines public and private RPC endpoint surfaces that determine whether record methods are exposed unauthenticated or protected |
| rpc/src/rpc_types.rs | 111 | record payload/record response types touched as part of the record RPC endpoint move |

## Code Snippets

## Snippet 1

Context: `rpc/src/rpc_impl_protected.rs:117` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

    /// Wrap authentication around `create_account`
    pub fn create_account_protected(&self, params: Params, meta: Meta) -> Result<Value, JsonRPCError> {
```
After
```rust
}

    /// Wrap authentication around `decode_record`
    pub fn decode_record_protected(&self, params: Params, meta: Meta) -> Result<Value, JsonRPCError> {
        self.validate_auth(meta)?;

        let value = match params {
            Params::Array(arr) => arr,
```

## Snippet 2

Context: `rpc/src/rpc_impl.rs:297` (changes an authorization or privilege gate)

Before
```rust
})
    }

    // Record handling

    /// Decrypts the record ciphertext and returns the hex encoded bytes of the record.
    fn decrypt_record(&self, decryption_input: DecryptRecordInput) -> Result<String, RpcError> {
        // Read the encrypted_record
```
After
```rust
})
    }
}
```

## Snippet 3

Context: `rpc/src/rpc_types.rs:111` (changes an authorization or privilege gate)

Before
```rust
}

/// Additional metadata included with a transaction response
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct TransactionMetadata {
    /// The block number associated with this transaction
    pub block_number: Option<u32>,
}
```
After
```rust
}

/// Record payload data
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct RPCRecordPayload {
    /// Record payload
    pub payload: String,
}
```

## Snippet 4

Context: `rpc/src/rpc_types.rs:206` (changes an authorization or privilege gate)

Before
```rust
}

/// Record payload data
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub struct RPCRecordPayload {
    /// Record payload
    pub payload: String,
}
```
After
```rust
}

/// Input for the `createrawtransaction` rpc call
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
```

# Fix Pattern

Move record RPC entrypoints from the public implementation surface into protected wrappers and authenticate before parameter parsing or downstream record handling.

## How It Was Fixed

The patch added protected record endpoint handling, with direct evidence for decode_record_protected calling validate_auth(meta) first. It also removed the shown record handling block from the public RpcFunctions implementation area. Type and documentation changes appear supportive rather than root-cause fixes.

# Why It Matters

1. Changes an RPC access-control boundary.

2. Prevents unauthenticated access to the shown protected decode_record path.

3. Record decode/decrypt APIs may expose sensitive record data.

4. Remote exploitability and default exposure are not established by the provided evidence.

# Evidence Notes

Supported: decode_record_protected calls validate_auth(meta) before parameter handling; decrypt_record appeared under the public RpcFunctions implementation before the patch; the public/private RPC surface context is shown in rpc_trait.rs. Not supported: private key disclosure, default unauthenticated network exposure, exact complete list of moved endpoints, or a broader transaction-processing/input-validation bug class. Protocol security invariant: Record-related RPC methods that expose record decoding, decryption, or raw record access should be reachable only through the protected RPC surface and should enforce validate_auth(meta) before parameter parsing or dispatch. Verification notes: The patch does not prove remote exploitability by itself. The patch does not show whether default RPC credentials were enabled or configured. The patch does not prove private key disclosure; it only shows record RPC access control being tightened. The exact full list of record endpoints moved is inferred from the commit subject and touched docs, not fully enumerated in the provided hunks. No external verification was performed per instruction. Assessment is limited to the supplied mapper, draft, and evidence snippets. Confidence is medium because the complete diff and full trait declarations are not provided. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-authentication`
Final impact type: `unauthorized-rpc-access, potential-information-disclosure`
Final confidence: `medium`
Final tags: `rpc, access-control, authentication, record-endpoints, hardening`

The supplied evidence supports retaining this as security hardening: record-related RPC methods are moved or wrapped into protected handlers, and the shown protected decode_record path now calls validate_auth(meta) before parameter handling. The patch evidence is strong for an RPC access-control tightening, but not strong enough to prove a concrete exploit or the complete endpoint set, so security-hardening is more conservative than security-fix.

## Security Evidence

1. decode_record_protected is added and calls self.validate_auth(meta)? before processing params.
2. Project context shows get_raw_record_protected also validates auth before dispatching record access.
3. Before evidence shows decrypt_record under impl RpcFunctions, identified as the public RPC endpoint surface.
4. After evidence shows the record handling block removed from the shown public RpcFunctions implementation area.
5. Commit subject says all record RPC endpoints were made protected.

## Missing Evidence

1. Full diff does not enumerate every record endpoint moved to protected RPC.
2. No exploit scenario, default exposure, or credential configuration is proven.
3. No direct evidence of private key disclosure or concrete data leakage is supplied.
4. Documentation changes support an endpoint-surface change but do not independently prove behavior.

## Claim Boundaries

1. Validate only as RPC authentication/access-control hardening.
2. Do not classify as input validation or consensus behavior.
3. Do not claim confirmed remote exploitability from the supplied evidence.
4. Do not claim the exact complete list of protected endpoints beyond the shown record paths and commit subject.
