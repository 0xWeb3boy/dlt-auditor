---
case_id: case_20210223_142fbcfd6
project: bor
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
bug_class: missing-replay-protection-check
impact_type:
  - transaction-replay
confidence: high
tags:
  - blockchain-core
  - rpc
  - transaction-submission
  - replay-protection
  - eip155
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens the RPC transaction submission path by rejecting non-EIP-155-signed transactions unless the operator explicitly enables an override. The evidence supports a missing replay-protection check on this RPC boundary before the change, but it does not prove a broader protocol or consensus flaw.

## Observed Patch Facts

1. In `internal/ethapi/api.go`, the patch adds `if !b.UnprotectedAllowed() && !tx.Protected() {`.

2. In `cmd/utils/flags.go`, the patch adds `AllowUnprotectedTxs = cli.BoolFlag{`.

3. In `cmd/utils/flags.go`, the patch adds `if ctx.GlobalIsSet(AllowUnprotectedTxs.Name) {`.

4. In `internal/ethapi/backend.go`, the patch replaces `RPCGasCap() uint64 // global gas cap for eth_call over rpc: DoS protection` with `RPCGasCap() uint64 // global gas cap for eth_call over rpc: DoS protection`.

## Project Context

The changed code sits primarily in `internal/ethapi`, `cmd/utils`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `cmd/utils/customflags.go`, `cmd/utils/cmd.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `cmd/utils/customflags.go`, `cmd/utils/cmd.go`. The strongest project-level identifiers around this patch are `transactions`, `AllowUnprotectedTxs`, `Name`, and `global`.

## Before/After Behavior

Before: the shown `SubmitTransaction` path checked fee limits and then proceeded to `b.SendTx(ctx, tx)` with no visible `tx.Protected()` gate. After: the same path rejects `!tx.Protected()` transactions when `b.UnprotectedAllowed()` is false, and a new `rpc.allow-unprotected-txs` flag allows operators to opt back into the old RPC behavior.

# Root Cause

The RPC submission boundary did not enforce replay protection by default. In the provided pre-patch snippet, unprotected transactions could pass the visible fee-cap checks and reach `SendTx` without a shown EIP-155 protection check.

## Walkthrough

1. `internal/ethapi/api.go` adds a new guard before `SendTx`: reject the transaction when it is not protected and the backend policy does not allow unprotected transactions.

2. The pre-patch excerpt for the same function shows no equivalent replay-protection check between fee validation and `SendTx`.

3. `internal/ethapi/backend.go` adds `UnprotectedAllowed() bool`, which exposes the policy decision needed by the RPC submission path.

4. `cmd/utils/flags.go` adds `rpc.allow-unprotected-txs`, explicitly described as allowing non-EIP155 transactions over RPC.

5. `cmd/utils/flags.go` wires that flag into node configuration via `cfg.AllowUnprotectedTxs`, making the exception an operator-controlled opt-out from the safer default.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| internal/ethapi/api.go | 1552 | Primary RPC transaction submission path; adds the reject-before-send check for non-EIP-155 transactions |
| internal/ethapi/backend.go | 40 | Backend interface gains the policy hook that governs whether unprotected transactions are allowed |
| cmd/utils/flags.go | 588 | Defines the explicit operator override flag for allowing unprotected RPC transactions |
| cmd/utils/flags.go | 922 | Wires the override flag into HTTP/RPC node configuration |

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

Add an explicit security check at the external submission boundary, then plumb a narrowly scoped configuration override for deployments that intentionally need legacy behavior.

## How It Was Fixed

The fix inserts a `tx.Protected()` check in the RPC transaction submission path, adds a backend policy hook to query whether unprotected transactions are allowed, and introduces CLI/config plumbing so acceptance of unprotected RPC transactions requires explicit operator configuration.

# Why It Matters

1. RPC transaction submission is an externally reachable admission path.

2. EIP-155 protection is directly tied to replay-resistance.

3. The new default reduces replay-risk exposure on this path.

4. The override preserves compatibility, but only by explicit operator choice.

5. The evidence supports RPC-boundary hardening, not a consensus-wide rule change.

# Evidence Notes

The strongest evidence is the added rejection in `internal/ethapi/api.go` immediately before `SendTx`. Supporting evidence shows the new backend policy hook and the operator override flag/config wiring. The commit message explicitly frames the change as preventing submission of transactions without EIP-155 enabled, with an override flag. The provided material does not show changes to consensus validation, peer-to-peer handling, exploitability in default deployments, or added tests. Protocol security invariant: Transactions accepted through the external RPC submission path should be replay-protected (EIP-155) by default unless an operator explicitly enables acceptance of unprotected transactions. Verification notes: The patch does not prove an in-the-wild exploit or actual replay incident occurred. The patch does not show a change to consensus validation rules or peer-to-peer acceptance behavior. The evidence does not prove every transaction ingress path, beyond this RPC path, now enforces the same policy. The patch alone does not prove RPC exposure was reachable by attackers in default deployments. The missing check is directly visible in the before/after snippet for `SubmitTransaction`. The security claim should stay scoped to the RPC submission path. Evidence supports classifying this as security hardening rather than a proven exploitable protocol vulnerability. No regression tests were included in the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-replay-protection-check`
Final impact type: `transaction-replay`
Final confidence: `high`
Final tags: `blockchain-core, rpc, transaction-submission, replay-protection, eip155`

The patch clearly hardens a security-sensitive RPC submission path by rejecting non-EIP-155 transactions unless an operator explicitly opts back in. The before/after code shows a missing replay-protection gate immediately before transaction submission, and the new CLI/config flag makes the weaker behavior an explicit override rather than the default. That supports retaining this as a security-hardening case, but not as a proven exploitable security bug or a broader consensus/state-corruption flaw.

## Security Evidence

1. `SubmitTransaction` adds a new `!tx.Protected()` rejection before `SendTx`.
2. The rejection is enabled by default unless `UnprotectedAllowed()` is true.
3. Commit metadata explicitly describes preventing submission of transactions without EIP-155 enabled.
4. A new `rpc.allow-unprotected-txs` flag makes acceptance of unprotected transactions an explicit opt-in.
5. The changed logic is on an externally reachable RPC transaction admission path.

## Missing Evidence

1. No proof of a concrete exploit, incident, or attacker-controlled exposure in default deployments.
2. No evidence that consensus validation or peer-to-peer transaction handling was vulnerable.
3. No tests or additional patch context showing end-to-end replay abuse.
4. No evidence quantifying real-world impact beyond this RPC boundary.

## Claim Boundaries

1. This supports RPC-boundary security hardening, not a confirmed protocol-wide vulnerability.
2. The evidence supports replay-risk reduction, not state corruption.
3. The claim should stay limited to non-EIP-155 transaction submission over RPC.
4. Do not infer that all transaction ingress paths were previously vulnerable or are now covered.
