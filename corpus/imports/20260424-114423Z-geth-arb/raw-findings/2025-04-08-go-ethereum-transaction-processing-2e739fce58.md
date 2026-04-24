---
case_id: case_20250408_2e739fce58
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: high
source_quality: high
date: 2025-04-08
source_refs:
  - git:2e739fce584a3cc8d84bf4c4604cd81c07294e2b
  - "core/txpool/legacypool/legacypool.go:648"
  - "core/txpool/txpool.go:119"
  - "core/txpool/blobpool/blobpool.go:1104"
  - "core/txpool/legacypool/legacypool_test.go:168"
bug_class: txpool-resource-exhaustion-hardening
impact_type:
  - availability
  - mempool-resource-control
tags:
  - blockchain-core
  - transaction-processing
  - txpool
  - blobpool
  - eip-7702
  - resource-exhaustion
  - eviction-mitigation
  - security-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is supported as txpool security hardening for EIP-7702/blobpool resource-control abuse. It adds constraints on delegated or pending-delegation senders in the blobpool and rejects SetCode authority conflicts against pending, queued, or reserved addresses. The evidence supports mitigation of mempool spam, eviction, and later invalidation, not consensus invalidity, signature forgery, direct fund theft, malformed decoding, or remote crash behavior.

## Observed Patch Facts

1. In `core/txpool/legacypool/legacypool.go`, the patch adds `// Because there is no exclusive lock held between different subpools`.

2. In `core/txpool/txpool.go`, the patch replaces `// reserver is a method to create an address reservation callback to exclusively` with `// Close terminates the transaction pool and all its subpools.`.

3. In `core/txpool/blobpool/blobpool.go`, the patch replaces `// validateTx checks whether a transaction is valid according to the consensus` with `// checkDelegationLimit determines if the tx sender is delegated or has a`.

4. In `core/txpool/legacypool/legacypool_test.go`, the patch replaces `func makeAddressReserver() txpool.AddressReserver {` with `func setupPool() (*LegacyPool, *ecdsa.PrivateKey) {`.

## Project Context

The changed code sits primarily in `core/txpool/legacypool`, `core/txpool`, `core/txpool/blobpool`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/txpool/errors.go`, `core/txpool/validation.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/txpool/validation.go`, `core/txpool/subpool.go`. The strongest project-level identifiers around this patch are `from`, `transactions`, `transaction`, and `lock`.

## Before/After Behavior

Before the patch, the provided evidence shows BlobPool transaction validation without the new delegated-sender in-flight executable limit, and LegacyPool SetCode authority validation checking pending and queued entries but not the new shared reservation-tracker state. After the patch, BlobPool has checkDelegationLimit to limit delegated or pending-delegation senders to at most one in-flight executable transaction, LegacyPool validateAuth rejects authorities already pending, queued, or reserved, and TxPool initializes subpools with handles from a shared reservation tracker. The patch comments explicitly acknowledge that simultaneous cross-subpool acceptance can still occur because there is no exclusive lock across all subpools during transaction processing.

# Root Cause

The grounded root cause is missing txpool-level coordination between EIP-7702 delegation state, blob transaction admission, and cross-subpool address reservation. This allowed a delegated or pending-delegation sender to stack executable blob transactions and left SetCode authority conflicts insufficiently checked against reservations held by other subpools, creating a resource-control gap in blobpool admission and eviction behavior.

## Walkthrough

1. An attacker uses an account with delegation or pending authorization to submit multiple blob transactions to the pool.

2. Without the new blobpool limit, the account can have more than one in-flight executable blob transaction cached.

3. Those transactions can consume blobpool capacity and evict other transactions, as described by the commit message.

4. The attacker can then invalidate the pending blob transactions by draining the sender funds if delegation is involved.

5. SetCode authority handling also needs coordination with addresses already pending, queued, or reserved by other subpools.

6. The patch adds delegated-sender blobpool limits, SetCode authority reservation checks, and shared reservation-tracker handles, while documenting a remaining simultaneous-acceptance race.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/txpool/blobpool/blobpool.go | 1104 | Adds blobpool checkDelegationLimit to cap delegated or pending-delegation senders at one in-flight executable transaction. |
| core/txpool/legacypool/legacypool.go | 637 | Validates EIP-7702 SetCode authorizations against pending, queued, and reserved authority addresses. |
| core/txpool/txpool.go | 83 | Initializes subpools with handles from a shared reservation tracker instead of a local reservation callback. |
| core/txpool/reserver.go | 11 | Provides the shared address reservation tracker used to prevent cross-subpool ownership conflicts. |
| core/txpool/errors.go | 11 | Defines txpool errors used by validation paths, including authority-reservation rejection behavior. |

## Code Snippets

## Snippet 1

Context: `core/txpool/legacypool/legacypool.go:648` (changes an authorization or privilege gate)

Before
```go
return ErrAuthorityReserved
			}
		}
	}
```
After
```go
return ErrAuthorityReserved
			}
			// Because there is no exclusive lock held between different subpools
			// when processing transactions, the SetCode transaction may be accepted
			// while other transactions with the same sender address are also
			// accepted simultaneously in the other pools.
			//
			// This scenario is considered acceptable, as the rule primarily ensures
```

## Snippet 2

Context: `core/txpool/txpool.go:119` (changes an authorization or privilege gate)

Before
```go
}

// reserver is a method to create an address reservation callback to exclusively
// assign/deassign addresses to/from subpools. This can ensure that at any point
// in time, only a single subpool is able to manage an account, avoiding cross
// subpool eviction issues and nonce conflicts.
func (p *TxPool) reserver(id int, subpool SubPool) AddressReserver {
	return func(addr common.Address, reserve bool) error {
```
After
```go
}

// Close terminates the transaction pool and all its subpools.
func (p *TxPool) Close() error {
```

## Snippet 3

Context: `core/txpool/blobpool/blobpool.go:1104` (changes signature or replay validation logic)

Before
```go
}

// validateTx checks whether a transaction is valid according to the consensus
// rules and adheres to some heuristic limits of the local node (price and size).
```
After
```go
}

// checkDelegationLimit determines if the tx sender is delegated or has a
// pending delegation, and if so, ensures they have at most one in-flight
// **executable** transaction, e.g. disallow stacked and gapped transactions
// from the account.
func (p *BlobPool) checkDelegationLimit(tx *types.Transaction) error {
	from, _ := types.Sender(p.signer, tx) // validated
```

## Snippet 4

Context: `core/txpool/legacypool/legacypool_test.go:168` (changes persisted or aggregate state handling)

Before
```go
}

func makeAddressReserver() txpool.AddressReserver {
	var (
		reserved = make(map[common.Address]struct{})
		lock     sync.Mutex
	)
	return func(addr common.Address, reserve bool) error {
```
After
```go
}

func setupPool() (*LegacyPool, *ecdsa.PrivateKey) {
	return setupPoolWithConfig(params.TestChainConfig)
}

func newReserver() *txpool.Reserver {
	return txpool.NewReservationTracker().NewHandle(42)
```

# Fix Pattern

Add admission-time txpool resource-control checks: cap executable in-flight blob transactions for delegated or pending-delegation senders, and reject EIP-7702 SetCode authorities that conflict with pending, queued, or cross-subpool reserved addresses.

## How It Was Fixed

BlobPool gained checkDelegationLimit for delegated or pending-delegation senders. LegacyPool validateAuth now checks SetCode authorities against pending, queued, and reserved addresses. TxPool initialization now creates a shared NewReservationTracker and passes per-subpool handles to subpools, with tests updated to use the new reservation tracker helper. The reservation tracker is support infrastructure, not the root cause by itself.

# Why It Matters

1. Mitigates blobpool capacity abuse by delegated accounts.

2. Reduces transaction eviction attacks described in the commit message.

3. Improves coordination between blobpool and legacypool authority ownership.

4. Keeps EIP-7702 SetCode authority conflicts out of normal admission paths.

5. Does not claim complete race elimination or consensus-level impact.

# Evidence Notes

The strongest evidence is the commit body, which explicitly describes the spam, eviction, and cancellation attack, plus code excerpts showing BlobPool checkDelegationLimit, LegacyPool validateAuth reservation checks, and TxPool use of a shared reservation tracker. The supplied evidence does not establish remote crashes, malformed decoding, cryptographic replay, consensus-invalid block acceptance, direct theft, or complete elimination of cross-subpool races. The comments themselves state that a simultaneous acceptance window remains. Protocol security invariant: For EIP-7702 delegated accounts or accounts with pending authorization, txpool admission should not allow multiple executable blob transactions to be stacked in a way that consumes blobpool capacity and can later be invalidated, and SetCode authority addresses should not conflict with addresses already pending, queued, or reserved by another subpool. Verification notes: The patch does not prove consensus-invalid transactions can be accepted into blocks. The patch does not prove remote node crash or malformed decoding behavior. The patch does not eliminate all cross-subpool races; the commit explicitly accepts a simultaneous acceptance window. The patch does not prove direct theft of funds or signature forgery. The evidence supports txpool resource-exhaustion/eviction mitigation, not cryptographic replay failure. Confirmed classification should remain security-hardening rather than proven vulnerability fix. Do not carry over the heuristic baseline's panic or malformed-decoding claims; they are unsupported here. The residual cross-subpool race should be documented as a limitation of the mitigation. Helper and test changes support the fix but are not independent vulnerability roots. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `txpool-resource-exhaustion-hardening`
Final impact type: `availability, mempool-resource-control`
Final tags: `blockchain-core, transaction-processing, txpool, blobpool, eip-7702, resource-exhaustion, eviction-mitigation, security-hardening`

The supplied commit metadata and patch context support keeping this as security hardening. The commit explicitly describes an attack involving blob transaction spam, eviction of other transactions, and later cancellation by draining funds under delegation, and the code adds admission constraints for delegated or pending-delegation accounts plus authority reservation checks. The evidence supports txpool resource-control hardening, but not a proven consensus, cryptographic, crash, or direct theft vulnerability.

## Security Evidence

1. Commit body explicitly says the constraints mitigate an attack involving spam, eviction, and cancellation of pending blob transactions.
2. BlobPool adds a delegation-limit check for delegated or pending-delegation senders, limiting in-flight executable transactions.
3. LegacyPool validateAuth rejects SetCode authorities that conflict with pending, queued, or reserved addresses.
4. TxPool reservation tracking coordinates address ownership across subpools to reduce cross-subpool conflicts.

## Missing Evidence

1. No evidence of consensus-invalid block acceptance or chain safety violation.
2. No evidence of signature forgery, replay bypass, malformed decoding, or remote crash.
3. No proof that all cross-subpool races are eliminated; the supplied comments acknowledge a simultaneous acceptance window remains.
4. No direct exploit demonstration beyond the commit-described resource-control attack scenario.

## Claim Boundaries

1. Classify as security-hardening rather than a fully proven security-fix vulnerability.
2. Limit impact to txpool availability, blobpool capacity abuse, and mempool eviction mitigation.
3. Do not carry over the original consensus tag or imply consensus-layer compromise.
4. Do not claim direct fund theft; draining funds is described as a way to invalidate the attacker's own pending transactions.
