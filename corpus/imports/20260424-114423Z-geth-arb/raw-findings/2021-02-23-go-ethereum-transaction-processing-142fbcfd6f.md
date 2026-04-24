---
case_id: case_20210223_142fbcfd6f
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: high
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
  - transaction-replay-risk
tags:
  - blockchain-core
  - transaction-processing
  - rpc
  - replay
  - eip-155
  - security-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens go-ethereum's RPC transaction submission path by rejecting non-EIP-155, non-replay-protected transactions before they are forwarded to SendTx, unless an explicit operator override is enabled.

## Observed Patch Facts

1. In `internal/ethapi/api.go`, the patch adds `if !b.UnprotectedAllowed() && !tx.Protected() {`.

2. In `cmd/utils/flags.go`, the patch adds `AllowUnprotectedTxs = cli.BoolFlag{`.

3. In `cmd/utils/flags.go`, the patch adds `if ctx.GlobalIsSet(AllowUnprotectedTxs.Name) {`.

4. In `internal/ethapi/backend.go`, the patch replaces `RPCGasCap() uint64 // global gas cap for eth_call over rpc: DoS protection` with `RPCGasCap() uint64 // global gas cap for eth_call over rpc: DoS protection`.

## Project Context

The changed code sits primarily in `internal/ethapi`, `cmd/utils`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `cmd/utils/customflags.go`, `cmd/utils/cmd.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `cmd/utils/customflags.go`, `cmd/utils/cmd.go`. The strongest project-level identifiers around this patch are `transactions`, `AllowUnprotectedTxs`, `Name`, and `global`.

## Before/After Behavior

Before the change, the provided SubmitTransaction evidence shows fee-cap validation followed by b.SendTx(ctx, tx), with no visible check that the transaction was EIP-155 protected. After the change, SubmitTransaction rejects transactions when !b.UnprotectedAllowed() && !tx.Protected(), returning an error before SendTx. Supporting changes add a Backend.UnprotectedAllowed() policy hook and a --rpc.allow-unprotected-txs override flag wired into node configuration.

# Root Cause

The RPC transaction intake path did not enforce the configured replay-protection policy before forwarding user-submitted transactions to downstream transaction handling. The evidence supports a missing RPC-boundary policy check, not a consensus validation flaw or state-corruption bug.

## Walkthrough

1. A client submits a transaction through the RPC path handled by internal/ethapi.SubmitTransaction.

2. The pre-fix visible path checks transaction fee limits and then forwards the transaction with b.SendTx(ctx, tx).

3. No supplied pre-fix evidence shows SubmitTransaction checking tx.Protected() before forwarding the transaction.

4. The patch adds a guard that rejects unprotected transactions when the backend policy does not allow them.

5. The patch adds Backend.UnprotectedAllowed() so the RPC API can query the configured policy.

6. The patch adds and wires the rpc.allow-unprotected-txs CLI flag as an explicit compatibility override.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| internal/ethapi/api.go | 1556 | enforces rejection of non-EIP-155 transactions before RPC-submitted txs enter SendTx |
| internal/ethapi/backend.go | 46 | adds backend policy hook exposing whether unprotected transactions are allowed |
| cmd/utils/flags.go | 594 | defines operator override flag for accepting unprotected RPC transactions |
| cmd/utils/flags.go | 971 | maps the override flag into node configuration |

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

Enforce a replay-protection policy at the RPC API boundary before dispatching the transaction to lower-level submission logic, with legacy behavior available only through explicit configuration.

## How It Was Fixed

internal/ethapi/api.go now checks !b.UnprotectedAllowed() && !tx.Protected() inside SubmitTransaction and returns an error instead of calling SendTx. internal/ethapi/backend.go adds the UnprotectedAllowed() interface method, and cmd/utils/flags.go defines and maps the rpc.allow-unprotected-txs flag into node configuration.

# Why It Matters

1. RPC transaction submission is a sensitive entry point for user-provided transactions.

2. EIP-155 is explicitly replay-protection-related in the supplied evidence.

3. The patch prevents default acceptance of non-replay-protected RPC-submitted transactions.

4. The evidence does not support broader claims such as authentication bypass, privilege escalation, transaction theft, or consensus validation changes.

# Evidence Notes

Primary evidence is internal/ethapi/api.go:1556, where the new guard rejects transactions that are not tx.Protected() unless UnprotectedAllowed() is true. Supporting evidence is internal/ethapi/backend.go:46 for the backend policy hook, cmd/utils/flags.go:594 for the rpc.allow-unprotected-txs flag, and cmd/utils/flags.go:971 for configuration wiring. The commit message directly states that the PR prevents users from submitting transactions without EIP-155 enabled unless overridden. No supplied evidence demonstrates exploit success in a specific deployment. Protocol security invariant: Transactions submitted through the Ethereum RPC transaction path should be EIP-155 replay-protected by default unless the node operator explicitly opts into accepting unprotected transactions. Verification notes: The patch does not prove remote authentication bypass or privilege escalation. The patch does not prove transaction theft or successful replay in a specific deployment. The patch evidence is limited to RPC transaction submission, not consensus validation generally. The operator override means unprotected transactions can still be accepted when explicitly configured. Verified from provided snippets only; no commands or external context used. Downgraded the heuristic state-corruption framing as unsupported. Kept the finding security-relevant because the patch directly enforces replay-protection policy on RPC-submitted transactions. Scoped the claim to RPC transaction submission, not consensus validation. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-replay-protection-enforcement`
Final impact type: `transaction-replay-risk`
Final tags: `blockchain-core, transaction-processing, rpc, replay, eip-155, security-hardening`

The supplied patch evidence directly shows a new RPC-boundary guard rejecting non-EIP-155, non-replay-protected transactions before SendTx unless an explicit operator override is enabled. This is security-relevant hardening of replay-sensitive transaction submission behavior, but the evidence does not prove an exploited vulnerability, state corruption, consensus failure, or concrete transaction theft. The original state-corruption framing is too broad and should be narrowed.

## Security Evidence

1. SubmitTransaction now checks !b.UnprotectedAllowed() && !tx.Protected() before calling SendTx.
2. Rejected transactions return an error stating only replay-protected EIP-155 transactions are allowed over RPC.
3. A new rpc.allow-unprotected-txs flag makes legacy acceptance an explicit opt-in rather than default behavior.
4. Backend gains an UnprotectedAllowed policy hook used by the RPC transaction submission path.
5. Commit message explicitly says users are prevented from submitting transactions without EIP-155 enabled unless overridden.

## Missing Evidence

1. No evidence of a concrete exploit or successful replay attack is supplied.
2. No evidence shows consensus validation or on-chain state corruption was affected.
3. No evidence supports authentication bypass, privilege escalation, or transaction theft claims.
4. No tests or deployment scenario demonstrate impact beyond accepting unprotected RPC-submitted transactions.

## Claim Boundaries

1. Keep as security-hardening, not a proven security-fix.
2. Scope is RPC transaction submission, not general consensus transaction validation.
3. Impact should be framed as replay-risk reduction, not state corruption.
4. Unprotected transactions remain possible when the operator explicitly enables the override flag.
