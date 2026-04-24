---
case_id: case_20240820_dab9bad618
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
source_quality: high
date: 2024-08-20
source_refs:
  - git:dab9bad6187e0ba342aa6fca4586e6f276583db9
  - "consensus/core/src/block_verifier.rs:143"
  - "consensus/core/src/block_verifier.rs:481"
  - "crates/sui-protocol-config/src/lib.rs:2666"
  - "consensus/core/src/error.rs:25"
bug_class: consensus-resource-limit-hardening
impact_type:
  - resource-exhaustion
  - denial-of-service
confidence: medium
tags:
  - consensus
  - block-verification
  - resource-limits
  - protocol-config
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is security-relevant consensus resource-control work, but the provided evidence does not establish a concrete vulnerability or exploit path. The visible verifier change directly adds a protocol-configured per-transaction size check in `BlockVerifier`; the commit text and added config/error variants indicate intended count and aggregate byte limit enforcement, but the supplied hunks do not fully show those checks.

## Observed Patch Facts

1. In `consensus/core/src/block_verifier.rs`, the patch replaces `// TODO: check transaction size, total size and count.` with `let max_transaction_size_limit =`.

2. In `consensus/core/src/block_verifier.rs`, the patch adds `// Block with transaction too large.`.

3. In `crates/sui-protocol-config/src/lib.rs`, the patch replaces `// Use this template when making changes:` with `// Assume 1KB per transaction and 500 transactions per block.`.

4. In `consensus/core/src/error.rs`, the patch replaces `#[error("Unexpected block authority {0} from peer {1}")]` with `#[error("Block contains a transaction that is too large: {size} > {limit}")]`.

## Project Context

The changed code sits primarily in `consensus/core/src`, `consensus/core`, `crates/sui-protocol-config/src`, which anchors the finding in the `consensus` area of the project. Historical context from `consensus/core/src/transaction.rs`, `consensus/core/src/core.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `consensus/core/src/transaction.rs`, `consensus/core/src/core.rs`. The strongest project-level identifiers around this patch are `limit`, `size`, `usize`, and `block`. Nearby tests or test-like files include `consensus/core/src/tests/universal_committer_tests.rs`, `consensus/core/src/tests/pipelined_committer_tests.rs`.

## Before/After Behavior

Before the change, the shown `SignedBlockVerifier` path collected transaction data and passed it to `transaction_verifier.verify_batch`, with a TODO stating that transaction size, total size, and count still needed checking. After the change, the verifier reads `consensus_max_transaction_size_bytes()` from protocol config and rejects any transaction whose data length exceeds the configured limit when enabled. The patch also adds protocol config values for block transaction byte and count limits and error variants for too-large transactions, too many transactions, and too many transaction bytes.

# Root Cause

The visible root cause was missing block-level resource-bound enforcement in the signed block verification path. The evidence shows an explicit TODO for transaction size, total size, and count checks before the patch, but it does not prove that this omission was exploitable as a security vulnerability.

## Walkthrough

1. `consensus/core/src/block_verifier.rs` previously contained a TODO to check transaction size, total transaction size, and transaction count.

2. The same verifier path built a transaction batch from `block.transactions()` and passed it to transaction batch verification.

3. The patch adds a protocol-configured per-transaction size limit check using `consensus_max_transaction_size_bytes()`.

4. If a transaction exceeds the enabled limit, verification returns `ConsensusError::TransactionTooLarge`.

5. `consensus/core/src/error.rs` adds explicit errors for oversized transactions, excessive transaction count, and excessive aggregate transaction bytes.

6. `crates/sui-protocol-config/src/lib.rs` adds version 55 values for consensus transaction byte and count limits.

7. A unit test covers rejection of a signed block containing a transaction larger than the configured per-transaction size limit.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| consensus/core/src/block_verifier.rs | 143 | enforces protocol-configured transaction size and block transaction limits during signed block verification |
| crates/sui-protocol-config/src/lib.rs | 2666 | defines consensus transaction byte and count limits in protocol configuration |
| consensus/core/src/error.rs | 25 | adds rejection errors for oversized transactions, too many transactions, and excessive transaction bytes |
| consensus/core/src/block_verifier.rs | 481 | adds regression coverage for rejecting a block containing an oversized transaction |

## Code Snippets

## Snippet 1

Context: `consensus/core/src/block_verifier.rs:143` (changes bounds, limits, or capacity handling)

Before
```rust
}

        // TODO: check transaction size, total size and count.
        let batch: Vec<_> = block.transactions().iter().map(|t| t.data()).collect();
        self.transaction_verifier
            .verify_batch(&self.context.protocol_config, &batch)
```
After
```rust
}

        let batch: Vec<_> = block.transactions().iter().map(|t| t.data()).collect();

        let max_transaction_size_limit =
            self.context
                .protocol_config
                .consensus_max_transaction_size_bytes() as usize;
```

## Snippet 2

Context: `consensus/core/src/block_verifier.rs:481` (changes signature or replay validation logic)

Before
```rust
));
        }
    }
```
After
```rust
));
        }

        // Block with transaction too large.
        {
            let block = test_block
                .clone()
                .set_transactions(vec![Transaction::new(vec![4; 257 * 1024])])
```

## Snippet 3

Context: `crates/sui-protocol-config/src/lib.rs:2666` (changes a consensus- or validator-sensitive branch)

Before
```rust
// Turn on enums mainnet
                    cfg.move_binary_format_version = Some(7);
                }
                // Use this template when making changes:
```
After
```rust
// Turn on enums mainnet
                    cfg.move_binary_format_version = Some(7);

                    // Assume 1KB per transaction and 500 transactions per block.
                    cfg.consensus_max_transactions_in_block_bytes = Some(512 * 1024);
                    // Assume 20_000 TPS * 5% max stake per validator / (minimum) 4 blocks per round = 250 transactions per block maximum
                    // Using a higher limit that is 512, to account for bursty traffic and system transactions.
                    cfg.consensus_max_num_transactions_in_block = Some(512);
```

## Snippet 4

Context: `consensus/core/src/error.rs:25` (changes bounds, limits, or capacity handling)

Before
```rust
SerializationFailure(bcs::Error),

    #[error("Unexpected block authority {0} from peer {1}")]
    UnexpectedAuthority(AuthorityIndex, AuthorityIndex),
```
After
```rust
SerializationFailure(bcs::Error),

    #[error("Block contains a transaction that is too large: {size} > {limit}")]
    TransactionTooLarge { size: usize, limit: usize },

    #[error("Block contains too many transactions: {count} > {limit}")]
    TooManyTransactions { count: usize, limit: usize },
```

# Fix Pattern

Enforce protocol-configured resource limits at the signed block verification boundary and return explicit verifier errors for limit violations.

## How It Was Fixed

The patch moves relevant consensus transaction limits into protocol configuration and updates `BlockVerifier` to consult those limits. The visible implementation rejects oversized individual transaction data, adds dedicated error variants for resource-limit failures, and adds regression coverage for the oversized transaction case.

# Why It Matters

1. Bounds validator work during block verification.

2. Aligns block acceptance with protocol-configured limits.

3. Makes at least one missing resource check explicit and test-covered.

4. Does not prove a remote exploit, consensus divergence, or cryptographic failure.

# Evidence Notes

Downgraded from likely security hardening to unclear because the evidence supports resource-limit enforcement but not a demonstrated vulnerability. The per-transaction size check is directly visible. Count and aggregate byte enforcement are supported by commit text, config additions, and error variants, but their exact verifier logic is not shown in the supplied snippets. No exploit path, denial-of-service scenario, consensus safety break, replay issue, or signature bypass is established. Protocol security invariant: Consensus block verification should apply protocol-configured resource bounds to proposed block contents before accepting a signed block, including limits on transaction size and, as described by the commit, block transaction count and aggregate transaction bytes. Verification notes: No remote exploit path is demonstrated by the patch evidence. No consensus divergence or safety break is proven. No cryptographic, signature, or replay invariant is shown to be fixed. The evidence supports resource-bound enforcement, not arbitrary transaction validity changes. The exact pre-patch behavior of total byte and count enforcement is inferred from the TODO and commit description, not fully shown in the hunks. Visible test verifies rejection of a 257 KiB transaction with `TransactionTooLarge`. No provided evidence shows a pre-patch exploit or externally triggerable attack path. No provided evidence fully shows the new total byte or transaction count checks in `BlockVerifier`. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-resource-limit-hardening`
Final impact type: `resource-exhaustion, denial-of-service`
Final confidence: `medium`
Final tags: `consensus, block-verification, resource-limits, protocol-config, hardening`

The supplied evidence supports retaining this as security hardening, not as a proven security fix. The patch adds protocol-configured transaction size and block transaction limit enforcement in the consensus block verification path, replacing an explicit TODO for missing size/count checks and adding rejection errors plus tests. That clearly tightens resource-control behavior at a security-sensitive validator/consensus boundary, but the evidence does not prove an exploitable vulnerability, consensus safety break, or concrete attack path.

## Security Evidence

1. SignedBlockVerifier previously contained a TODO to check transaction size, total size, and count before accepting block transactions.
2. The patch adds a protocol-configured per-transaction size limit check and returns TransactionTooLarge on violation.
3. Protocol config adds consensus transaction byte and transaction count limits for blocks.
4. ConsensusError gains explicit errors for too-large transactions, too many transactions, and too many transaction bytes.
5. A regression test verifies rejection of a signed block containing an oversized transaction.

## Missing Evidence

1. No exploit scenario or externally triggerable denial-of-service path is demonstrated.
2. The provided hunks do not fully show implementation of aggregate byte and transaction count checks.
3. No evidence shows a pre-patch consensus divergence, signature bypass, replay issue, or safety failure.
4. No operational incident, advisory, or security-labeled commit metadata is provided.

## Claim Boundaries

1. Classify as consensus resource-limit hardening, not a confirmed vulnerability fix.
2. Do not claim consensus safety compromise from the supplied evidence.
3. Do not claim cryptographic, replay, or authentication impact.
4. Do not claim all block limit checks are visible in the supplied patch snippets, only that the commit and errors/config indicate them.
