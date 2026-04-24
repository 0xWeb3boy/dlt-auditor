---
case_id: case_20250408_2e739fce5
project: bor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2025-04-08
source_refs:
  - git:2e739fce584a3cc8d84bf4c4604cd81c07294e2b
  - "core/txpool/legacypool/legacypool.go:648"
  - "core/txpool/txpool.go:119"
  - "core/txpool/blobpool/blobpool.go:1104"
  - "core/txpool/legacypool/legacypool_test.go:168"
bug_class: resource-exhaustion
impact_type:
  - availability
tags:
  - blockchain-core
  - transaction-processing
  - txpool
  - mempool
  - resource-control
  - delegation
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds txpool admission checks for EIP-7702-style delegated or pending-authorization accounts. Based on the supplied commit message and code snippets, it is a security-relevant hardening change aimed at reducing a mempool abuse pattern involving blob transaction spam, eviction pressure, and later cancellation.

## Observed Patch Facts

1. In `core/txpool/legacypool/legacypool.go`, the patch adds `// Because there is no exclusive lock held between different subpools`.

2. In `core/txpool/txpool.go`, the patch replaces `// reserver is a method to create an address reservation callback to exclusively` with `// Close terminates the transaction pool and all its subpools.`.

3. In `core/txpool/blobpool/blobpool.go`, the patch replaces `// validateTx checks whether a transaction is valid according to the consensus` with `// checkDelegationLimit determines if the tx sender is delegated or has a`.

4. In `core/txpool/legacypool/legacypool_test.go`, the patch replaces `func makeAddressReserver() txpool.AddressReserver {` with `func setupPool() (*LegacyPool, *ecdsa.PrivateKey) {`.

## Project Context

The changed code sits primarily in `core/txpool/legacypool`, `core/txpool`, `core/txpool/blobpool`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/txpool/errors.go`, `core/txpool/validation.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/txpool/validation.go`, `core/txpool/subpool.go`. The strongest project-level identifiers around this patch are `from`, `transactions`, `transaction`, and `lock`.

## Before/After Behavior

Before the patch, the provided snippets only show local `pending`/`queue` authority-conflict checks in `LegacyPool.validateAuth`, and no delegation-specific executable-transaction limit is visible near the shown `blobpool` validation path. After the patch, `blobpool` adds `checkDelegationLimit` for delegated or pending-delegation senders, `legacypool` rejects authorities already reserved via `pool.reserver.Has(auth)`, and `TxPool.New` initializes a shared `ReservationTracker` for subpool coordination. The added comments also state that a narrow cross-subpool race still exists because processing is not covered by an exclusive cross-pool lock.

# Root Cause

The txpool did not fully enforce cross-subpool exclusivity for delegated senders and `SetCode` authority addresses. From the supplied evidence, that left room for blob and authorization-related transactions to interact in a way that could be used to create txpool eviction and cancellation pressure.

## Walkthrough

1. A sender with delegation or pending authorization reaches txpool admission paths in `blobpool` and `legacypool`.

2. The patch introduces `BlobPool.checkDelegationLimit`, documented to allow at most one in-flight executable transaction for such senders.

3. `LegacyPool.validateAuth` is extended to reject authorities already reserved, not just authorities already present in that pool's `pending` or `queue`.

4. `TxPool.New` now creates a shared `ReservationTracker` and passes handles to subpools so those checks can coordinate across pools.

5. The comments explicitly note the mitigation is not absolute because conflicting admissions can still race across subpools.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/txpool/blobpool/blobpool.go | 1104 | enforces delegation-aware blobpool admission limit so delegated or pending-delegation senders cannot queue multiple executable blob transactions |
| core/txpool/legacypool/legacypool.go | 637 | validates SetCode authorization lists and rejects authority addresses already reserved or otherwise conflicting with pending/queued ownership |
| core/txpool/txpool.go | 83 | initializes the shared reservation tracker used to assign account ownership across subpools and avoid cross-pool conflicts |
| core/txpool/reserver.go | 14 | provides the reservation-handle mechanism that underpins exclusive address ownership between subpools |

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

Add explicit admission-time resource and exclusivity checks, backed by shared reservation tracking across subpools.

## How It Was Fixed

The fix adds two guards described in the commit body and reflected in the snippets: delegated or pending-delegation senders are limited to one executable in-flight blob transaction, and `SetCode` transactions are rejected when an authority is already reserved. A shared reservation tracker is initialized in `TxPool.New` so subpools can enforce those checks against shared address ownership rather than only local queue state.

# Why It Matters

1. Reduces a stated mempool abuse pattern involving spam, eviction, and later cancellation.

2. Strengthens txpool isolation across subpools instead of relying only on local pool checks.

3. Limits the ability of delegated accounts to stack executable blob transactions.

4. The comments show the remaining race, so this is mitigation rather than a complete elimination of the issue.

# Evidence Notes

The changes are centered on txpool admission and reservation logic, not serialization or refactoring. `BlobPool.checkDelegationLimit` limits delegated or pending-delegation senders to one executable in-flight blob transaction, and `LegacyPool.validateAuth` rejects SetCode authorities already reserved by another pool handle. Combined with the shared reservation tracker, this maps to a mempool availability/liveness hardening against cross-subpool eviction and cancellation abuse. The patch and commit text support a security-relevant resource-control issue, but they do not fully prove broad exploitability, especially because the code comments acknowledge a remaining race between subpools. Protocol security invariant: Delegated or pending-authorization accounts should not be able to occupy multiple executable blobpool slots or reuse an authority already reserved by another subpool in a way that lets one actor manipulate txpool eviction and later cancellation of pending transactions. Verification notes: The patch does not show a consensus or chain-state corruption bug; the scope shown is txpool admission and availability. The evidence does not prove remote node crash or code-execution impact. The comments explicitly note a remaining cross-subpool race, so exclusivity is best-effort rather than absolute. The patch does not prove chain-wide exploitability or attacker profitability beyond mempool eviction/cancellation pressure. Assessment is based only on the provided commit text and extracted snippets. The evidence supports txpool availability and resource-control hardening, not consensus corruption or code execution. Exploitability is plausible from the commit description but not independently demonstrated in the supplied material. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-exhaustion`
Final impact type: `availability`
Final tags: `blockchain-core, transaction-processing, txpool, mempool, resource-control, delegation`

The supplied evidence supports keeping this as a security-relevant hardening change. The commit message explicitly describes a txpool abuse scenario involving blob-transaction spam, eviction pressure, and later cancellation, and the patch adds concrete admission and reservation checks to reduce that behavior across subpools. At the same time, the diff and comments do not prove a fully exploitable vulnerability or complete elimination of the race, so the most conservative fit is security-hardening rather than a confirmed security-fix.

## Security Evidence

1. Commit body explicitly frames the change as mitigation for an attacker-driven blobpool spam and eviction pattern.
2. `BlobPool.checkDelegationLimit` limits delegated or pending-delegation senders to one executable in-flight transaction.
3. `LegacyPool.validateAuth` now rejects authorities already reserved, extending checks beyond local pending or queued state.
4. `TxPool.New` initializes a shared `ReservationTracker`, showing deliberate cross-subpool resource coordination.

## Missing Evidence

1. No exploit reproduction or failing test is provided to show real-world impact against peers or the network.
2. The comments acknowledge a remaining cross-subpool race, so the protection is not absolute.
3. The provided patch does not show consensus breakage, fund loss, or another higher-severity outcome beyond txpool abuse and availability pressure.

## Claim Boundaries

1. This supports txpool or mempool availability hardening, not consensus or state-integrity repair.
2. The evidence does not show code execution, privilege escalation, or direct theft.
3. The most defensible corpus label is security hardening against resource-abuse or eviction abuse in transaction admission.
