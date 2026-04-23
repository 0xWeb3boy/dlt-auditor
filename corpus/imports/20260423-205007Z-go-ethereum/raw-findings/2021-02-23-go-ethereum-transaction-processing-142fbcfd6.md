---
case_id: case_20210223_142fbcfd6
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2021-02-23
source_refs:
  - git:142fbcfd6f4fad825e2ce2684f9d5a487ffb3f84
  - "internal/ethapi/api.go:1556"
  - "cmd/utils/flags.go:594"
  - "cmd/utils/flags.go:971"
  - "internal/ethapi/backend.go:46"
bug_class: missing-replay-protection-enforcement
impact_type:
  - replay-risk
  - transaction-integrity
confidence: high
tags:
  - blockchain-core
  - transaction-processing
  - rpc
  - eip-155
  - replay-protection
  - security-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens go-ethereum RPC transaction submission by rejecting non-EIP-155, non-replay-protected transactions before SendTx unless rpc.allow-unprotected-txs is explicitly enabled.

## Observed Patch Facts

1. In `internal/ethapi/api.go`, the patch adds `if !b.UnprotectedAllowed() && !tx.Protected() {`.

2. In `cmd/utils/flags.go`, the patch adds `AllowUnprotectedTxs = cli.BoolFlag{`.

3. In `cmd/utils/flags.go`, the patch adds `if ctx.GlobalIsSet(AllowUnprotectedTxs.Name) {`.

4. In `internal/ethapi/backend.go`, the patch replaces `RPCGasCap() uint64 // global gas cap for eth_call over rpc: DoS protection` with `RPCGasCap() uint64 // global gas cap for eth_call over rpc: DoS protection`.

## Project Context

The changed code sits primarily in `internal/ethapi`, `cmd/utils`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `cmd/utils/customflags.go`, `cmd/utils/cmd.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `cmd/utils/customflags.go`, `cmd/utils/cmd.go`. The strongest project-level identifiers around this patch are `transactions`, `AllowUnprotectedTxs`, `Name`, and `global`.

## Before/After Behavior

Before the change, the provided SubmitTransaction snippet checked the transaction fee cap and then called b.SendTx(ctx, tx) with no visible tx.Protected() policy check. After the change, SubmitTransaction returns an error when tx.Protected() is false and the backend does not allow unprotected transactions. The patch also adds the rpc.allow-unprotected-txs flag, wires it into node configuration, and exposes UnprotectedAllowed() on the ethapi Backend interface.

# Root Cause

The RPC submission path did not show a default validation gate requiring EIP-155 replay protection before forwarding submitted transactions to SendTx. The provided evidence does not establish whether later code could also reject such transactions.

## Walkthrough

1. SubmitTransaction receives a transaction for RPC submission.

2. The function first applies the existing transaction fee-cap check.

3. In the pre-patch snippet, successful fee-cap validation is followed directly by b.SendTx(ctx, tx).

4. The patch inserts a guard that rejects unprotected transactions when UnprotectedAllowed() is false.

5. The Backend interface gains UnprotectedAllowed() so the RPC API can query this policy.

6. A new rpc.allow-unprotected-txs CLI flag provides an explicit operator override.

7. setHTTP wires the flag into cfg.AllowUnprotectedTxs when set.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| internal/ethapi/api.go | 1556 | enforces default rejection of non-EIP-155 transactions before SendTx |
| cmd/utils/flags.go | 594 | defines explicit RPC opt-out flag for allowing unprotected transactions |
| cmd/utils/flags.go | 971 | wires the opt-out flag into node configuration |
| internal/ethapi/backend.go | 46 | exposes backend policy hook used by RPC transaction submission |

## Code Snippets

## Snippet 1

Context: `internal/ethapi/api.go:1556` (changes signature or replay validation logic)

Before
```go
return common.Hash{}, err
	}
	if err := b.SendTx(ctx, tx); err != nil {
		return common.Hash{}, err
```
After
```go
return common.Hash{}, err
	}
	if !b.UnprotectedAllowed() && !tx.Protected() {
		// Ensure only eip155 signed transactions are submitted if EIP155Required is set.
		return common.Hash{}, errors.New("only replay-protected (EIP-155) transactions allowed over RPC")
	}
	if err := b.SendTx(ctx, tx); err != nil {
		return common.Hash{}, err
```

## Snippet 2

Context: `cmd/utils/flags.go:594` (changes an authorization or privilege gate)

Before
```go
Usage: "Comma separated list of JavaScript files to preload into the console",
	}

	// Network Settings
```
After
```go
Usage: "Comma separated list of JavaScript files to preload into the console",
	}
	AllowUnprotectedTxs = cli.BoolFlag{
		Name:  "rpc.allow-unprotected-txs",
		Usage: "Allow for unprotected (non EIP155 signed) transactions to be submitted via RPC",
	}

	// Network Settings
```

## Snippet 3

Context: `cmd/utils/flags.go:971` (changes a sensitive control or state-update path)

Before
```go
cfg.HTTPPathPrefix = ctx.GlobalString(HTTPPathPrefixFlag.Name)
	}
}
```
After
```go
cfg.HTTPPathPrefix = ctx.GlobalString(HTTPPathPrefixFlag.Name)
	}
	if ctx.GlobalIsSet(AllowUnprotectedTxs.Name) {
		cfg.AllowUnprotectedTxs = ctx.GlobalBool(AllowUnprotectedTxs.Name)
	}
}
```

## Snippet 4

Context: `internal/ethapi/backend.go:46` (changes a sensitive control or state-update path)

Before
```go
AccountManager() *accounts.Manager
	ExtRPCEnabled() bool
	RPCGasCap() uint64    // global gas cap for eth_call over rpc: DoS protection
	RPCTxFeeCap() float64 // global tx fee cap for all transaction related APIs

	// Blockchain API
```
After
```go
AccountManager() *accounts.Manager
	ExtRPCEnabled() bool
	RPCGasCap() uint64        // global gas cap for eth_call over rpc: DoS protection
	RPCTxFeeCap() float64     // global tx fee cap for all transaction related APIs
	UnprotectedAllowed() bool // allows only for EIP155 transactions.

	// Blockchain API
```

# Fix Pattern

Add a default-deny validation gate at the RPC boundary for replay-sensitive legacy transaction inputs, with an explicit configuration override for compatibility.

## How It Was Fixed

The fix checks !b.UnprotectedAllowed() && !tx.Protected() before SendTx and returns a replay-protection error for disallowed unprotected transactions. Supporting changes add the CLI flag, configuration wiring, and backend policy hook needed for enforcement.

# Why It Matters

1. RPC transaction submission is a replay-sensitive path.

2. EIP-155 distinguishes replay-protected transactions from legacy unprotected ones.

3. Rejecting unprotected transactions by default reduces accidental acceptance of replayable transactions.

4. The evidence supports security hardening, not a demonstrated exploit chain.

# Evidence Notes

The strongest evidence is the new guard in internal/ethapi/api.go before SendTx and the commit message stating that users are prevented from submitting transactions without EIP-155 unless the override flag is set. The mapper's state-corruption baseline is unsupported. The evidence does not prove RPC exposure to attackers, successful cross-chain replay, privilege escalation, or a flaw in EIP-155 validation itself. Protocol security invariant: Transactions submitted through RPC should be replay-protected with EIP-155 by default unless an operator explicitly opts into accepting legacy unprotected transactions. Verification notes: The patch does not prove that RPC was exposed to untrusted remote users in any deployment. The patch does not prove that every accepted unprotected transaction would be successfully replayed on another chain. The patch does not indicate a flaw in EIP-155 signature validation itself. The patch preserves an explicit operator override, so it is a default-policy hardening rather than an absolute prohibition. No concrete exploit chain or privilege escalation is shown by the patch alone. No tests are shown in the provided evidence. No concrete exploit path is established by the supplied snippets. Classification is kept as likely security hardening rather than confirmed vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-replay-protection-enforcement`
Final impact type: `replay-risk, transaction-integrity`
Final confidence: `high`
Final tags: `blockchain-core, transaction-processing, rpc, eip-155, replay-protection, security-hardening`

The supplied patch clearly hardens a replay-sensitive RPC transaction submission path by rejecting non-EIP-155 transactions by default before SendTx, while adding an explicit operator override. The evidence supports retaining this as security hardening, but not as a concrete security-fix with proven exploitability. The original state-corruption classification is too strong for the shown evidence.

## Security Evidence

1. SubmitTransaction now rejects transactions where tx.Protected() is false unless UnprotectedAllowed() is enabled.
2. The returned error explicitly says only replay-protected EIP-155 transactions are allowed over RPC.
3. A new rpc.allow-unprotected-txs flag makes acceptance of non-EIP-155 transactions an explicit opt-in.
4. The commit message states the PR prevents users from submitting transactions without EIP-155 enabled.

## Missing Evidence

1. No demonstrated exploit chain or successful replay attack is shown.
2. No evidence proves RPC exposure to untrusted attackers in a vulnerable deployment.
3. No evidence shows later SendTx or consensus paths previously accepted all unprotected transactions without other checks.
4. No tests or vulnerability advisory are included in the supplied evidence.

## Claim Boundaries

1. Classify as default-policy security hardening, not a proven vulnerability fix.
2. Do not claim state corruption is demonstrated by the patch.
3. Do not claim privilege escalation, authentication bypass, or remote exploitation.
4. Do not claim EIP-155 validation itself was broken.
