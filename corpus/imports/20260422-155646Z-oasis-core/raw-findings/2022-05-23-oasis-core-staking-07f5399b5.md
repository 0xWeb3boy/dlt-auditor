---
case_id: case_20220523_07f5399b5
project: oasis-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: not-security
phase3_validated_as: not-security
phase3_keep_candidate: false
subsystem: staking
source_quality: high
date: 2022-05-23
source_refs:
  - git:07f5399b5bafb0eb44c380e02eb633dd09ebfc5c
  - "go/staking/api/sanity_check.go:342"
  - "go/consensus/tendermint/apps/staking/transactions.go:46"
  - "go/consensus/tendermint/apps/staking/transactions.go:184"
  - "go/consensus/tendermint/apps/staking/transactions.go:41"
bug_class: reserved-address-invariant-enforcement
impact_type:
  - state-integrity
confidence: medium
tags:
  - blockchain-core
  - staking
  - consensus
  - reserved-address
  - burn-address
  - state-invariant
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided evidence supports a staking semantics fix, not a demonstrated vulnerability fix. The patch makes transfers to `staking.BurnAddress` execute burn logic and adds a sanity check that rejects ledger/genesis state where the burn address has a non-zero balance or nonce.

## Observed Patch Facts

1. In `go/staking/api/sanity_check.go`, the patch replaces `// Check the above two invariants for each account as well.` with `// The burn address is actually "unused" for reasonable definitions of "unused".`.

2. In `go/consensus/tendermint/apps/staking/transactions.go`, the patch replaces `from, err := state.Account(ctx, fromAddr)` with `if xfer.To.Equal(staking.BurnAddress) {`.

3. In `go/consensus/tendermint/apps/staking/transactions.go`, the patch replaces `from, err := state.Account(ctx, fromAddr)` with `return app.burnImpl(ctx, state, params, fromAddr, &burn.Amount)`.

4. In `go/consensus/tendermint/apps/staking/transactions.go`, the patch replaces `// Check if sender provided at least a minimum amount.` with `if fromAddr.IsReserved() || !isTransferPermitted(params, fromAddr) {`.

## Project Context

The changed code sits primarily in `go/staking/api`, `go/staking`, `go/consensus/tendermint/apps/staking`, which anchors the finding in the `staking` area of the project. Historical context from `go/consensus/tendermint/apps/staking/staking.go`, `go/staking/api/api.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/staking/api/api.go`, `go/consensus/tendermint/apps/staking/transactions_test.go`. The strongest project-level identifiers around this patch are `fromAddr`, `state`, `params`, and `staking`. Nearby tests or test-like files include `go/staking/tests/tester.go`, `go/staking/tests/state.go`.

## Before/After Behavior

Before the patch, the transfer path did not special-case `xfer.To == staking.BurnAddress` in the shown code and burn-address state was not explicitly rejected by `SanityCheck`. After the patch, transfers to `staking.BurnAddress` are routed to `app.burnImpl(...)`, the explicit burn path also uses `app.burnImpl(...)`, and `SanityCheck` returns an error if `g.Ledger[BurnAddress]` has a non-zero balance or nonce.

# Root Cause

`staking.BurnAddress` was not handled consistently as a dedicated burn sink. The transfer path could treat it like a normal destination, and sanity checking did not enforce that the burn address remain unused in ledger/genesis state.

## Walkthrough

1. `transactions.go` now checks `if xfer.To.Equal(staking.BurnAddress)` and calls `app.burnImpl(...)` instead of always following normal transfer handling.

2. The explicit `burn(...)` handler was changed to return `app.burnImpl(...)`, showing that burn behavior is now centralized in one implementation.

3. `sanity_check.go` now inspects `g.Ledger[BurnAddress]` and returns an error if its balance is non-zero.

4. The same sanity-check block also returns an error if the burn address nonce is non-zero.

5. These changes establish corrected burn-address semantics and a state invariant, but the supplied evidence does not establish theft, permission bypass, denial of service, or consensus failure.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/consensus/tendermint/apps/staking/transactions.go | 24 | transfer path now special-cases `BurnAddress` and dispatches to burn semantics |
| go/consensus/tendermint/apps/staking/transactions.go | 162 | burn transaction path refactored to share `burnImpl` with transfer-to-burn handling |
| go/staking/api/sanity_check.go | 336 | genesis/state validation now enforces that the burn address remains unused (zero balance, zero nonce) |

## Code Snippets

## Snippet 1

Context: `go/staking/api/sanity_check.go:342` (changes signature or replay validation logic)

Before
```go
}

	// Check the above two invariants for each account as well.
	for addr, acct := range g.Ledger {
```
After
```go
}

	// The burn address is actually "unused" for reasonable definitions of "unused".
	if ba := g.Ledger[BurnAddress]; ba != nil {
		if !ba.General.Balance.IsZero() {
			return fmt.Errorf(
				"staking: sanity check failed: burn address has non-zero balance: %v", ba.General.Balance,
			)
```

## Snippet 2

Context: `go/consensus/tendermint/apps/staking/transactions.go:46` (changes a consensus- or validator-sensitive branch)

Before
```go
}

	from, err := state.Account(ctx, fromAddr)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch account: %w", err)
	}
```
After
```go
}

	if xfer.To.Equal(staking.BurnAddress) {
		err = app.burnImpl(ctx, state, params, fromAddr, &xfer.Amount)
	} else {
		err = app.transferImpl(ctx, state, params, fromAddr, xfer)
	}
	if err != nil {
```

## Snippet 3

Context: `go/consensus/tendermint/apps/staking/transactions.go:184` (changes a consensus- or validator-sensitive branch)

Before
```go
}

	from, err := state.Account(ctx, fromAddr)
	if err != nil {
```
After
```go
}

	return app.burnImpl(ctx, state, params, fromAddr, &burn.Amount)
}

func (app *stakingApplication) burnImpl(
	ctx *api.Context,
	state *stakingState.MutableState,
```

## Snippet 4

Context: `go/consensus/tendermint/apps/staking/transactions.go:41` (changes a sensitive control or state-update path)

Before
```go
}

	// Check if sender provided at least a minimum amount.
	if xfer.Amount.Cmp(&params.MinTransferAmount) < 0 {
		return nil, staking.ErrUnderMinTransferAmount
	}

	fromAddr := ctx.CallerAddress()
```
After
```go
}

	fromAddr := ctx.CallerAddress()
	if fromAddr.IsReserved() || !isTransferPermitted(params, fromAddr) {
```

# Fix Pattern

Special-case a reserved protocol address in transaction handling and enforce an explicit ledger/genesis invariant for that address.

## How It Was Fixed

The patch rerouted transfer-to-burn-address operations into shared burn logic via `burnImpl(...)` and added sanity-check validation that rejects any burn-address ledger entry with non-zero balance or nonce.

# Why It Matters

1. It makes burn-address handling explicit instead of relying on generic transfer behavior.

2. It prevents ledger/genesis state from treating the burn address like a normal account.

3. It clarifies a protocol invariant for a reserved address.

4. The supplied evidence still does not prove an exploitable security issue.

# Evidence Notes

Direct evidence is limited to the new `if xfer.To.Equal(staking.BurnAddress)` branch in `go/consensus/tendermint/apps/staking/transactions.go`, the refactoring of the explicit burn path to `burnImpl(...)`, and the new `go/staking/api/sanity_check.go` checks for non-zero burn-address balance and nonce. The commit metadata mentions tests, but no test diff is provided here, so no stronger behavioral or exploit claim is supported. Protocol security invariant: `staking.BurnAddress` must be treated as a burn sink, not as a normal transfer recipient, and ledger/genesis validation must reject non-zero balance or nonce for that address. Verification notes: The patch does not prove an exploitable vulnerability beyond incorrect burn-address semantics. It is not shown that an attacker could gain funds, bypass permissions, or forge state transitions. It is not proven that pre-patch behavior caused a consensus failure rather than merely undesirable ledger state. The evidence does not show a denial-of-service, panic, or memory-corruption condition. The touched tests are not included here, so exact regression scenarios are inferred only from the implementation changes. Observed code changes clearly support a business-logic/state-invariant fix. No provided evidence shows fund theft, auth bypass, crash behavior, or consensus divergence. Security relevance is possible in a broad sense, but the vulnerability thesis is not established by the supplied patch evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `reserved-address-invariant-enforcement`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, staking, consensus, reserved-address, burn-address, state-invariant`

The patch evidence supports retaining this as a security-hardening case, not a proven security-fix. In a consensus staking subsystem, the burn address is a reserved protocol sink, and the change explicitly prevents it from being handled like a normal transfer recipient while adding state/genesis checks that enforce zero balance and zero nonce for that address. That clearly tightens a security-sensitive invariant around protocol state integrity. However, the patch alone does not prove an exploitable vulnerability, theft path, or consensus break in pre-patch behavior.

## Security Evidence

1. `transfer` now special-cases `xfer.To == staking.BurnAddress` and routes to `burnImpl(...)` instead of normal transfer handling.
2. The explicit `burn(...)` path was refactored to use the same `burnImpl(...)`, reducing inconsistent handling of burn semantics.
3. `SanityCheck` now rejects ledger/genesis state where `BurnAddress` has a non-zero balance.
4. `SanityCheck` now rejects ledger/genesis state where `BurnAddress` has a non-zero nonce.
5. The modified code sits in staking consensus transaction processing and state validation, which are security-sensitive integrity boundaries.

## Missing Evidence

1. No proof that pre-patch behavior allowed an attacker to steal, recover, or redirect funds.
2. No evidence of a real-world exploit, incident, or consensus divergence caused by the old behavior.
3. No test diff is provided here to show the exact regression scenario being prevented.
4. The patch does not show whether `transferImpl` previously created a materially dangerous state beyond violating protocol semantics.

## Claim Boundaries

1. The evidence supports hardening of reserved burn-address handling and protocol-state invariants.
2. The evidence does not support claims of fund theft, authentication bypass, remote code execution, or memory corruption.
3. The evidence does not prove a concrete exploitable vulnerability; it shows tighter enforcement in a security-sensitive path.
4. This should be cataloged as security-hardening rather than a confirmed security-fix.
