---
case_id: case_20250408_2e739fce5
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2025-04-08
source_refs:
  - git:2e739fce584a3cc8d84bf4c4604cd81c07294e2b
  - "core/txpool/legacypool/legacypool.go:648"
  - "core/txpool/txpool.go:119"
  - "core/txpool/blobpool/blobpool.go:1104"
  - "core/txpool/legacypool/legacypool_test.go:168"
bug_class: mempool-resource-exhaustion
impact_type:
  - availability
  - resource-exhaustion
  - transaction-eviction
confidence: high
tags:
  - blockchain-core
  - transaction-processing
  - txpool
  - blobpool
  - eip-7702
  - resource-control
  - availability
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is txpool resource-control hardening for EIP-7702 interactions, not malformed-input panic handling or consensus compromise. The patch adds blobpool limits for delegated or pending-delegation senders, rejects SetCode authorities already reserved by another pool, and centralizes reservation tracking through shared reservation handles.

## Observed Patch Facts

1. In `core/txpool/legacypool/legacypool.go`, the patch adds `// Because there is no exclusive lock held between different subpools`.

2. In `core/txpool/txpool.go`, the patch replaces `// reserver is a method to create an address reservation callback to exclusively` with `// Close terminates the transaction pool and all its subpools.`.

3. In `core/txpool/blobpool/blobpool.go`, the patch replaces `// validateTx checks whether a transaction is valid according to the consensus` with `// checkDelegationLimit determines if the tx sender is delegated or has a`.

4. In `core/txpool/legacypool/legacypool_test.go`, the patch replaces `func makeAddressReserver() txpool.AddressReserver {` with `func setupPool() (*LegacyPool, *ecdsa.PrivateKey) {`.

## Project Context

The changed code sits primarily in `core/txpool/legacypool`, `core/txpool`, `core/txpool/blobpool`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/txpool/errors.go`, `core/txpool/validation.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/txpool/validation.go`, `core/txpool/subpool.go`. The strongest project-level identifiers around this patch are `from`, `transactions`, `transaction`, and `lock`.

## Before/After Behavior

Before the patch, the supplied snippets show no blobpool `checkDelegationLimit` helper and `LegacyPool.validateAuth` only checking SetCode authorities against pending and queued legacy transactions. After the patch, blobpool enforces at most one in-flight executable transaction for delegated or pending-delegation senders, legacy validation also rejects authorities reported by `pool.reserver.Has(auth)`, and txpool initialization gives subpools handles from `NewReservationTracker()`. Comments explicitly acknowledge a residual cross-subpool race because processing is not protected by one exclusive global lock.

# Root Cause

The issue was missing EIP-7702-aware txpool admission and reservation policy across blobpool and legacy-pool paths. That gap allowed the spam, eviction, and later cancellation pattern described in the commit message when delegated accounts or pending authorities interacted with blob transactions and SetCode transactions.

## Walkthrough

1. An attacker uses a sender with an existing delegation or pending EIP-7702 authorization.

2. Before the new policy, the blobpool could cache more than one in-flight executable blob transaction for that delegated or pending-delegation sender.

3. The same txpool system also processes SetCode transactions through the legacy pool, where authorities were checked against pending and queued legacy transactions but not clearly against shared reservations.

4. This allowed cross-subpool reservation conflicts that could support the commit-described pattern of spamming blob transactions, evicting others, and later cancelling the attacker's pending blob transactions by draining funds.

5. The patch adds conservative admission checks so delegated or pending-delegation senders cannot stack executable blobpool transactions and SetCode authorities already reserved by another pool are rejected.

6. The fix mitigates the documented pattern but does not claim to remove every simultaneous-acceptance race between subpools.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/txpool/blobpool/blobpool.go | 1104 | adds delegation-aware blobpool admission limit for delegated or pending-delegation senders |
| core/txpool/legacypool/legacypool.go | 637 | validates SetCode authorities against pending, queued, and reserved addresses |
| core/txpool/txpool.go | 83 | initializes shared reservation tracker handles for subpools |
| core/txpool/reserver.go | 11 | shared address reservation tracking used to prevent cross-subpool conflicts |
| core/txpool/errors.go | 11 | defines txpool rejection errors used by validation paths |

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

Add conservative mempool admission checks around EIP-7702 delegation state and shared address reservations: limit delegated senders to one executable blobpool transaction and reject SetCode authorities already reserved elsewhere.

## How It Was Fixed

`core/txpool/blobpool/blobpool.go` adds `checkDelegationLimit` for delegated or pending-delegation senders. `core/txpool/legacypool/legacypool.go` extends SetCode authority validation with `pool.reserver.Has(auth)` and returns `ErrAuthorityReserved` on conflict. `core/txpool/txpool.go` initializes a shared reservation tracker and passes per-subpool handles during initialization.

# Why It Matters

1. Reduces a txpool spam and eviction vector involving blob transactions and EIP-7702 delegation.

2. Prevents delegated or pending-delegation senders from occupying multiple executable blobpool slots under the new policy.

3. Reduces cross-subpool conflicts involving SetCode authorities already reserved by blobpool or another subpool.

4. Does not establish consensus compromise, transaction forgery, signature bypass, or guaranteed node crash.

# Evidence Notes

The strongest evidence is the commit message describing the spam, eviction, and cancellation attack, plus code snippets adding `checkDelegationLimit`, `pool.reserver.Has(auth)`, and `NewReservationTracker()` handles. The earlier heuristic claim about malformed decoded values reaching panic-prone conversions is unsupported and should be discarded. The provided evidence supports mempool resource-control hardening with a documented residual race, not a complete vulnerability proof. Protocol security invariant: Txpool admission should not let EIP-7702 delegated senders or pending SetCode authorities use blobpool and legacy-pool interactions to reserve many executable slots, evict other transactions, and then cheaply invalidate the reserved transactions. Verification notes: The patch does not prove remote consensus compromise or chain-state corruption. The patch does not show arbitrary transaction forgery or signature bypass. The commit itself notes residual race windows between subpools due to lack of an exclusive global lock. Exploitability is described as mitigation of a spam/eviction pattern, not proven as a guaranteed node crash or full denial of service. The change appears to harden mempool policy, not alter consensus transaction validity. Commit text explicitly frames the change as mitigation of a blobpool spam and eviction attack. Code comments describe delegated or pending-delegation senders being limited to one in-flight executable transaction. Legacy SetCode authorization validation now checks shared reservation state before accepting an authority. Residual race windows are acknowledged in comments, so the verdict should remain likely hardening rather than confirmed complete fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `mempool-resource-exhaustion`
Final impact type: `availability, resource-exhaustion, transaction-eviction`
Final confidence: `high`
Final tags: `blockchain-core, transaction-processing, txpool, blobpool, eip-7702, resource-control, availability`

The supplied commit message explicitly describes a blobpool spam, eviction, and cancellation attack, and the patch evidence shows admission-policy tightening for delegated or pending-delegation senders plus shared reservation checks for SetCode authorities. This supports retaining the case as security hardening for txpool resource-control and availability, not as a proven consensus or cryptographic security fix.

## Security Evidence

1. Commit body states the constraints mitigate an attack involving blob transaction spam, eviction of other transactions, and later cancellation by draining funds.
2. BlobPool adds checkDelegationLimit to allow at most one in-flight executable transaction for delegated or pending-delegation senders.
3. LegacyPool validateAuth rejects SetCode authorities already reserved through pool.reserver.Has(auth).
4. TxPool now initializes subpools with handles from a shared NewReservationTracker, supporting cross-subpool reservation policy.

## Missing Evidence

1. No supplied evidence proves consensus compromise, transaction forgery, signature bypass, or chain-state corruption.
2. No exploit trace or test output demonstrates a guaranteed remote denial of service.
3. The commit itself notes a residual simultaneous-acceptance race between subpools.

## Claim Boundaries

1. Classify as txpool resource-control hardening for EIP-7702/blobpool interactions.
2. Do not claim a complete fix for all cross-subpool races.
3. Do not tag as consensus failure or cryptographic/replay validation bypass.
4. Impact should be limited to availability, resource exhaustion, and transaction-pool eviction risk.
