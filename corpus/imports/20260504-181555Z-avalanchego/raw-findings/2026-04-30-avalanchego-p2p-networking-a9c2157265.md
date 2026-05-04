---
case_id: case_20260430_a9c2157265
project: avalanchego
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: p2p-networking
confidence: medium
source_quality: medium
date: 2026-04-30
source_refs:
  - git:a9c21572655eafd208b2e8ad76a823cd81a995b0
  - "vms/saevm/txgossip/txgossip.go:107"
  - "vms/saevm/txgossip/txgossip_test.go:379"
  - "vms/saevm/txgossip/txgossip.go:53"
  - "vms/subnetevm/vm_test.go:377"
bug_class: mempool-allowlist-admission-gap
impact_type:
  - access-control
  - policy-enforcement
tags:
  - transaction-admission
  - mempool
  - allowlist
  - access-control
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely hardens SAE/Subnet EVM transaction admission by adding an Admitter gate before transactions are forwarded into the txpool. The evidence supports an allow-list enforcement improvement at RPC/mempool ingress, but does not establish prior unauthorized block execution, consensus bypass, malformed-input crash, or cryptographic validation failure.

## Observed Patch Facts

1. In `vms/saevm/txgossip/txgossip.go`, the patch adds `// addToPool runs each tx through the configured [Admitter] (if any) and`.

2. In `vms/saevm/txgossip/txgossip_test.go`, the patch replaces `func FuzzEffectiveGasTip(f *testing.F) {` with `// stubAdmitter implements [Admitter] by returning the per-call error`.

3. In `vms/saevm/txgossip/txgossip.go`, the patch replaces `// Set couples a [gossip.BloomSet] with a [txpool.TxPool] that acts as the` with `// An Admitter gates inbound transactions for the mempool.`.

4. In `vms/subnetevm/vm_test.go`, the patch replaces `// (3) Worst-case admission blocks the non-admin sender. We submit two` with `// (3) Mempool ingress (last-executed) rejects the non-admin sender at`.

## Project Context

The changed code sits primarily in `vms/saevm/txgossip`, `vms/saevm`, `vms/subnetevm`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `vms/subnetevm/factory.go`, `vms/saevm/txgossip/pushpull.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `vms/saevm/sae/vm.go`, `vms/subnetevm/factory.go`. The strongest project-level identifiers around this patch are `error`, `Admitter`, `errs`, and `nonAdmin`. Nearby tests or test-like files include `vms/saevm/saetest/wallet.go`, `vms/saevm/saetest/saetest_test.go`.

## Before/After Behavior

Before the patch, txSet.addToPool directly called s.pool.Add for incoming transactions with no visible admission hook. After the patch, addToPool preserves that behavior only when no admitter is configured; otherwise, transactions are checked through an Admitter and only admitted transactions are forwarded to the underlying txpool while preserving index-aligned errors. The Subnet EVM test now asserts that a NoRole sender is rejected at JSON-RPC/mempool ingress rather than only testing later block-level exclusion.

# Root Cause

The tx gossip-backed mempool insertion path did not visibly consult an allow-list-aware admission policy before forwarding transactions to txpool.Add. The provided evidence shows the fix adding that missing admission hook, but does not include enough implementation detail to prove the full prior impact beyond mempool admission behavior.

## Walkthrough

1. txgossip.go introduces an Admitter interface for deciding whether a transaction may enter the mempool.

2. txSet.Add routes transaction insertion through addToPool.

3. Previously, addToPool forwarded all provided transactions directly to s.pool.Add.

4. After the change, addToPool keeps the direct path only when s.admitter is nil.

5. When an admitter is configured, transactions are checked before insertion and rejected transactions are represented in the returned error slice.

6. The txgossip test stub exercises per-transaction Admit results and index-aligned error handling.

7. The Subnet EVM test asserts that a non-admin sender with NoRole is rejected through SendTransaction at RPC/mempool ingress.

8. The evidence supports admission hardening, not a claim of prior accepted-block authorization bypass.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| vms/saevm/txgossip/txgossip.go | 53 | defines the Admitter interface used to gate inbound transactions before mempool insertion |
| vms/saevm/txgossip/txgossip.go | 107 | filters transactions through the configured Admitter before forwarding survivors to txpool.Add |
| vms/subnetevm/vm_test.go | 377 | validates tx allow-list behavior for non-admin sender rejection at RPC/mempool ingress and block admission |
| vms/saevm/txgossip/txgossip_test.go | 379 | adds test stub coverage for per-transaction admission outcomes and index-aligned errors |

## Code Snippets

## Snippet 1

Context: `vms/saevm/txgossip/txgossip.go:107` (changes a sensitive control or state-update path)

Before
```go
}

func (s *txSet) addToPool(local bool, txs ...*types.Transaction) []error {
	return s.pool.Add(txs, local, false /*sync*/)
}
```
After
```go
}

// addToPool runs each tx through the configured [Admitter] (if any) and
// forwards the survivors to the pool. The returned slice is index-aligned
// with `txs`, mirroring [txpool.TxPool.Add].
func (s *txSet) addToPool(local bool, txs ...*types.Transaction) []error {
	if s.admitter == nil {
		return s.pool.Add(txs, local, false /*sync*/)
```

## Snippet 2

Context: `vms/saevm/txgossip/txgossip_test.go:379` (changes signature or replay validation logic)

Before
```go
}

func FuzzEffectiveGasTip(f *testing.F) {
	// The goal of these seeds is to exercise all possible orderings of fee cap,
```
After
```go
}

// stubAdmitter implements [Admitter] by returning the per-call error
// provided at construction; index `i` returns `errs[i]`. A nil entry admits
// the tx. Calls past `len(errs)` panic, which protects against silent
// over-counting.
type stubAdmitter struct {
	errs []error
```

## Snippet 3

Context: `vms/saevm/txgossip/txgossip.go:53` (changes a sensitive control or state-update path)

Before
```go
}

// Set couples a [gossip.BloomSet] with a [txpool.TxPool] that acts as the
// backing for the set.
```
After
```go
}

// An Admitter gates inbound transactions for the mempool.
//
// Implementations MUST make `Admit` cheap when no relevant check is required (i.e no precompile is active)
type Admitter interface {
	// Admit returns nil if `tx` is allowed into the mempool, or an error
	// describing why it was rejected. Safe for concurrent use.
```

## Snippet 4

Context: `vms/subnetevm/vm_test.go:377` (changes an authorization or privilege gate)

Before
```go
require.Equal(t, allowlist.NoRole, sut.fetchTxAllowListRole(t, nonAdmin, rpc.FinalizedBlockNumber))

	// (3) Worst-case admission blocks the non-admin sender. We submit two
	// txs in a single block: one funds `nonAdmin` (so it can pay fees in
	// later steps), the other is from `nonAdmin` and must be dropped.
	fundNonAdmin := sut.sendTransferTx(t, adminIdx, nonAdminIdx, fundValue)
	droppedTx := sut.sendTransferTx(t, nonAdminIdx, adminIdx, common.Big1)
	block := sut.buildAndAcceptBlock(t)
```
After
```go
require.Equal(t, allowlist.NoRole, sut.fetchTxAllowListRole(t, nonAdmin, rpc.FinalizedBlockNumber))

	// (3) Mempool ingress (last-executed) rejects the non-admin sender at
	// RPC; worst-case admission (last-settled) excludes it from blocks.
	// Fund `nonAdmin` so it can pay fees later.
	fundNonAdmin := sut.sendTransferTx(t, adminIdx, nonAdminIdx, fundValue)
	droppedTx := sut.signTransferTx(t, nonAdminIdx, adminIdx, common.Big1)
	// JSON-RPC stringifies the error, so the sentinel chain is lost; match
```

# Fix Pattern

Add a policy hook on the mempool insertion path, apply it before forwarding transactions to the backing txpool, preserve legacy behavior when no policy is configured, and maintain per-transaction error alignment for batched inputs.

## How It Was Fixed

The patch defines txgossip.Admitter and updates txSet.addToPool to use it when configured. Rejected transactions are filtered before txpool.Add, while accepted transactions continue through the existing pool path. Tests cover admission results and allow-list rejection for a non-admin sender at RPC/mempool ingress.

# Why It Matters

1. Enforces allow-list policy earlier in transaction handling.

2. Prevents rejected transactions from being added to the mempool when an admitter is configured.

3. Preserves batch error reporting for mixed accepted and rejected transactions.

4. Does not prove a prior consensus or block execution bypass.

# Evidence Notes

Grounded evidence comes from txgossip.go adding the Admitter interface and changing addToPool, txgossip_test.go adding an admission stub, and vm_test.go asserting NoRole rejection at RPC/mempool ingress. The supplied hunks do not support the heuristic claims about malformed RLP, panic behavior, cryptographic validation, or remote crash risk. The implementation details of sae/admitter.go are not shown, so claims are limited to the visible admission hook and tests. Protocol security invariant: When a transaction allow-list policy is active, transactions from senders without the required role should be rejected at transaction admission boundaries before being accepted into the mempool or propagated for block construction. Verification notes: The patch does not prove that unauthorized transactions could be executed in accepted blocks before the fix. The patch does not prove remote crash, panic, or malformed RLP exploitability. The patch does not show cryptographic signature validation changes despite heuristic flags. The patch evidence supports mempool/RPC admission enforcement, not a broad consensus bypass claim. The exact behavior of sae/admitter.go is inferred from filenames and tests because its implementation hunk is not included. Confirmed as security hardening rather than a fully demonstrated exploitable vulnerability. No evidence of prior unauthorized execution in accepted blocks was provided. No evidence of malformed transaction panic or cryptographic validation changes was provided. Helper test stubs are treated as support code, not root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `mempool-allowlist-admission-gap`
Final impact type: `access-control, policy-enforcement`
Final tags: `transaction-admission, mempool, allowlist, access-control, security-hardening`

The supplied patch evidence supports retaining this as security hardening: it adds an Admitter interface and applies it before transactions enter the txpool, and the test evidence specifically covers rejection of a NoRole sender at RPC/mempool ingress. The evidence does not prove a concrete exploitable vulnerability, prior unauthorized block execution, consensus bypass, cryptographic flaw, or liveness failure, so the original liveness-focused classification should be narrowed.

## Security Evidence

1. New Admitter interface explicitly gates inbound transactions for the mempool.
2. addToPool now filters transactions through the configured admitter before forwarding survivors to txpool.Add.
3. Subnet EVM test asserts a non-admin NoRole sender is rejected at SendTransaction/RPC mempool ingress.
4. The behavior is tied to tx allow-list enforcement, which is security-sensitive access policy handling.

## Missing Evidence

1. No full implementation hunk for sae/admitter.go is provided.
2. No evidence proves unauthorized transactions could previously execute in accepted blocks.
3. No evidence supports malformed input crash, cryptographic validation, replay, or remote DoS claims.
4. No exploit scenario or externally reachable bypass is demonstrated beyond mempool admission behavior.

## Claim Boundaries

1. Validate only as allow-list transaction admission hardening.
2. Do not claim a confirmed consensus or block execution authorization bypass.
3. Do not classify as liveness-failure based on the supplied evidence.
4. Do not infer cryptographic or malformed-RLP security impact from the test stub evidence.
