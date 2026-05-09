---
case_id: case_20191220_3c361eb759
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
impact_type:
  - state-integrity
source_quality: high
date: 2019-12-20
source_refs:
  - git:3c361eb75929593254446deb808e7b50d0b6e5ff
  - "runtime/src/accounts_db.rs:1001"
  - "runtime/src/accounts_db.rs:2226"
  - "sdk/src/hash.rs:30"
  - "sdk/src/hash.rs:75"
bug_class: snapshot-integrity-validation
confidence: medium
tags:
  - infrastructure
  - cryptography
  - snapshot-verification
  - account-hash
  - state-integrity
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch strengthens Solana snapshot/account verification by adding a per-account hash check in `runtime/src/accounts_db.rs::verify_bank_hash`. Before aggregation, the verifier now recomputes each non-sysvar account hash and returns `MismatchedAccountHash` if it differs from the stored `account.hash`. The `sdk/src/hash.rs` changes from literal `32` to `HASH_BYTES` are supporting cleanup and are not independent vulnerability evidence.

## Observed Patch Facts

1. In `runtime/src/accounts_db.rs`, the patch replaces `hash_state.xor(hash);` with `if mismatch_found {`.

2. In `runtime/src/accounts_db.rs`, the patch adds `#[test]`.

3. In `sdk/src/hash.rs`, the patch replaces `Hash(<[u8; 32]>::try_from(self.hasher.result().as_slice()).unwrap())` with `Hash(<[u8; HASH_BYTES]>::try_from(self.hasher.result().as_slice()).unwrap())`.

4. In `sdk/src/hash.rs`, the patch replaces `Hash(<[u8; 32]>::try_from(hash_slice).unwrap())` with `Hash(<[u8; HASH_BYTES]>::try_from(hash_slice).unwrap())`.

## Project Context

The changed code sits primarily in `runtime/src`, `sdk/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `sdk/src/bank_hash.rs`, `runtime/src/blockhash_queue.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sdk/src/bank_hash.rs`, `sdk/src/transaction.rs`. The strongest project-level identifiers around this patch are `Hash`, `unwrap`, `try_from`, and `BankHash::default`.

## Before/After Behavior

Before the patch, the shown verifier path aggregated account hash values into a bank hash and compared the aggregate against `slot_hashes`, without the provided evidence showing a recomputation check that each account's stored hash matched its actual slot, contents, and pubkey. After the patch, `verify_bank_hash` recomputes each non-sysvar account hash, detects any mismatch, returns `Err(MismatchedAccountHash)` before aggregate comparison, and then aggregates only recomputed hashes into `calculated_hash`.

# Root Cause

The snapshot bank-hash verifier trusted stored per-account hash values as inputs to aggregate verification without first validating those values against the underlying account records.

## Walkthrough

1. `verify_bank_hash` scans accounts for a target slot and ancestor set.

2. The pre-patch shown path XORed account hash values into an aggregate and compared that aggregate with the recorded slot hash.

3. The patch adds recomputation with `Self::hash_account(slot, &account, pubkey)` for each non-sysvar account.

4. If the recomputed hash differs from `account.hash`, the scan records `mismatch_found`.

5. After scanning, `verify_bank_hash` returns `Err(MismatchedAccountHash)` if any mismatch was found.

6. Only when per-account hashes match does the function XOR recomputed `BankHash` values into `calculated_hash` and compare it to `slot_hashes`.

7. New tests cover `verify_bank_hash`, including an incorrect account hash case.

8. The `HASH_BYTES` edits in `sdk/src/hash.rs` improve consistency but are not the root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/accounts_db.rs | 976 | verify_bank_hash scans accounts, recomputes each account hash, and flags mismatches before aggregation |
| runtime/src/accounts_db.rs | 1001 | failure handling returns MismatchedAccountHash and compares calculated aggregate BankHash to slot_hashes |
| runtime/src/accounts_db.rs | 2226 | new tests cover verify_bank_hash behavior for matching and incorrect account hash cases |
| sdk/src/hash.rs | 29 | uses HASH_BYTES constant when converting hasher result into Hash |
| sdk/src/hash.rs | 75 | uses HASH_BYTES constant when constructing Hash from a slice |

## Code Snippets

## Snippet 1

Context: `runtime/src/accounts_db.rs:1001` (changes signature or replay validation logic)

Before
```rust
},
        );
        for hash in hashes {
            hash_state.xor(hash);
        }
        let slot_hashes = self.slot_hashes.read().unwrap();
        if let Some(state) = slot_hashes.get(&slot) {
            hash_state == *state
```
After
```rust
},
        );
        if mismatch_found {
            return Err(MismatchedAccountHash);
        }
        let mut calculated_hash = BankHash::default();
        for hash in hashes {
            calculated_hash.xor(hash);
```

## Snippet 2

Context: `runtime/src/accounts_db.rs:2226` (changes signature or replay validation logic)

Before
```rust
);
    }
}
```
After
```rust
);
    }

    #[test]
    fn test_verify_bank_hash() {
        use BankHashVerificatonError::*;
        solana_logger::setup();
        let db = AccountsDB::new(Vec::new());
```

## Snippet 3

Context: `sdk/src/hash.rs:30` (changes signature or replay validation logic)

Before
```rust
// At the time of this writing, the sha2 library is stuck on an old version
        // of generic_array (0.9.0). Decouple ourselves with a clone to our version.
        Hash(<[u8; 32]>::try_from(self.hasher.result().as_slice()).unwrap())
    }
}
```
After
```rust
// At the time of this writing, the sha2 library is stuck on an old version
        // of generic_array (0.9.0). Decouple ourselves with a clone to our version.
        Hash(<[u8; HASH_BYTES]>::try_from(self.hasher.result().as_slice()).unwrap())
    }
}
```

## Snippet 4

Context: `sdk/src/hash.rs:75` (changes signature or replay validation logic)

Before
```rust
impl Hash {
    pub fn new(hash_slice: &[u8]) -> Self {
        Hash(<[u8; 32]>::try_from(hash_slice).unwrap())
    }
}
```
After
```rust
impl Hash {
    pub fn new(hash_slice: &[u8]) -> Self {
        Hash(<[u8; HASH_BYTES]>::try_from(hash_slice).unwrap())
    }
}
```

# Fix Pattern

Validate underlying leaf state before accepting a derived aggregate integrity check.

## How It Was Fixed

The fix adds per-account hash recomputation and mismatch handling in `runtime/src/accounts_db.rs::verify_bank_hash`, introduces an early `MismatchedAccountHash` error path, and changes the aggregate comparison to use recomputed hashes. Tests were added for the verifier behavior. Supporting hash code replaces hard-coded `32` lengths with `HASH_BYTES`.

# Why It Matters

1. Prevents snapshot verification from accepting account records whose contents do not match their stored hash.

2. Makes account-level integrity failure explicit before bank-hash aggregation.

3. Keeps the aggregate bank hash grounded in recomputed account hashes.

4. Evidence does not prove remote exploitability or consensus divergence.

# Evidence Notes

The strongest evidence is the `runtime/src/accounts_db.rs` change around `verify_bank_hash`, where `mismatch_found`, `Self::hash_account`, `MismatchedAccountHash`, and `calculated_hash` are added. The new test block supports the intended behavior. The `sdk/src/hash.rs` literal-to-constant changes are cleanup/supporting consistency only. Claims about attacker-controlled snapshots, remote exploitability, or proven consensus divergence are not established by the provided input. Protocol security invariant: Snapshot bank-hash verification should not rely solely on persisted per-account hash fields. For each non-sysvar account, verification should recompute the account hash from the slot, account data, and pubkey, reject mismatches, and only then aggregate hashes for comparison with the recorded slot bank hash. Verification notes: The patch does not prove remote exploitability or an attacker-controlled snapshot path. The patch does not show consensus divergence by itself, only a missing integrity check in snapshot account verification. The HASH_BYTES replacements are not independently evidence of a vulnerability. No evidence is provided that sysvar account handling is vulnerable; sysvar accounts are explicitly skipped in the shown verifier path. Supported: missing per-account hash validation in the shown verifier path. Supported: fix rejects mismatched account hashes before aggregate bank-hash comparison. Supported: sysvar accounts are skipped by the shown verifier path. Not supported: independent vulnerability in `sdk/src/hash.rs`. Not supported: remote exploitability or demonstrated consensus divergence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `snapshot-integrity-validation`
Final confidence: `medium`
Final tags: `infrastructure, cryptography, snapshot-verification, account-hash, state-integrity`

The supplied patch evidence clearly shows Solana snapshot/account bank-hash verification was strengthened to recompute each non-sysvar account hash, reject mismatches with MismatchedAccountHash, and aggregate recomputed hashes rather than trusting stored per-account hash values. That is security-relevant integrity hardening in a consensus/state verification path. However, the evidence does not prove a concrete exploitable vulnerability, remote attacker path, or demonstrated consensus failure, so security-hardening is more conservative than security-fix.

## Security Evidence

1. verify_bank_hash now recomputes each non-sysvar account hash with Self::hash_account(slot, &account, pubkey).
2. The verifier compares the recomputed hash against account.hash and records mismatch_found on disagreement.
3. The function now returns Err(MismatchedAccountHash) before aggregate bank-hash comparison when a mismatch is found.
4. The aggregate BankHash is calculated from recomputed hashes rather than directly trusting stored hash inputs.
5. New tests explicitly cover verify_bank_hash behavior, including incorrect account hash handling.

## Missing Evidence

1. No proof that malformed or attacker-controlled snapshots are remotely accepted.
2. No demonstrated exploit, consensus divergence, or state corruption scenario is provided.
3. No evidence that the sdk/src/hash.rs HASH_BYTES cleanup independently fixes a security issue.
4. No evidence that sysvar account skipping is itself vulnerable.

## Claim Boundaries

1. Keep claims limited to snapshot/account hash verification hardening.
2. Do not classify as a proven exploitable vulnerability from the supplied evidence alone.
3. Do not claim signature, queue, or blockhash-queue security impact from this patch.
4. Do not treat the HASH_BYTES literal-to-constant edits as independent vulnerability evidence.
