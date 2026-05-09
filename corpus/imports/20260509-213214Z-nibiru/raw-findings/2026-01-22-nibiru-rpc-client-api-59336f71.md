---
case_id: case_20260122_59336f71
project: nibiru
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: rpc-client-api
confidence: high
source_quality: high
date: 2026-01-22
source_refs:
  - git:59336f71d530d1463c590f786c2572231265e57a
  - "x/oracle/types/ballot.go:215"
  - "x/oracle/keeper/update_exchange_rates.go:55"
  - "x/oracle/keeper/update_exchange_rates.go:29"
  - "x/oracle/keeper/reward.go:42"
bug_class: consensus-nondeterminism
impact_type:
  - state-divergence
  - consensus-failure
tags:
  - blockchain-core
  - oracle
  - validator
  - consensus
  - determinism
  - go-map-iteration
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes nondeterministic iteration over ValidatorPerformances in oracle keeper paths. It adds a helper that sorts validator address keys and uses that order when updating miss counters, distributing oracle rewards, and emitting validator performance events.

## Observed Patch Facts

1. In `x/oracle/types/ballot.go`, the patch replaces `func (vp ValidatorPerformance) String() string {` with `// SortedAddrs returns validator addresses in sorted order for deterministic iteration.`.

2. In `x/oracle/keeper/update_exchange_rates.go`, the patch replaces `for _, validatorPerformance := range validatorPerformances {` with `// Sort validator addresses for deterministic iteration order.`.

3. In `x/oracle/keeper/update_exchange_rates.go`, the patch replaces `for _, validatorPerformance := range validatorPerformances {` with `// Sort validator addresses for deterministic event emission order.`.

4. In `x/oracle/keeper/reward.go`, the patch replaces `for _, validatorPerformance := range validatorPerformances {` with `// Sort validator addresses for deterministic iteration order.`.

## Project Context

The changed code sits primarily in `x/oracle/types`, `x/oracle`, `x/oracle/keeper`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `x/oracle/keeper/ballot.go`, `x/oracle/types/oracle.pb.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/oracle/keeper/ballot.go`, `x/oracle/types/oracle.pb.go`. The strongest project-level identifiers around this patch are `validatorPerformances`, `order`, `deterministic`, and `different`.

## Before/After Behavior

Before the patch, oracle keeper functions directly ranged over validatorPerformances, a Go map, in incrementMissCounters, rewardWinners, and UpdateExchangeRates event emission. After the patch, ValidatorPerformances.SortedAddrs() collects and lexicographically sorts validator address keys, and the keeper functions iterate over that sorted address list before looking up each ValidatorPerformance.

# Root Cause

Consensus-sensitive oracle logic depended on Go map traversal order. Because Go does not guarantee a stable order when ranging over maps, different nodes could process the same validator performance map in different orders in paths that write state or emit ordered results.

## Walkthrough

1. UpdateExchangeRates builds validatorPerformances and passes it through oracle update logic.

2. Before the fix, incrementMissCounters ranged directly over validatorPerformances before inserting miss-counter state for validators with nonzero MissCount.

3. Before the fix, rewardWinners ranged directly over validatorPerformances while processing oracle reward distribution.

4. Before the fix, UpdateExchangeRates ranged directly over validatorPerformances while emitting EventValidatorPerformance events.

5. ValidatorPerformances is keyed by validator address string, so direct range traversal is not deterministic across Go processes.

6. The patch adds SortedAddrs to extract validator addresses, sort them, and return a canonical order.

7. The patched keeper paths iterate over sorted addresses and then retrieve validatorPerformances[valAddr], preserving existing logic while making traversal deterministic.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/oracle/types/ballot.go | 215 | adds SortedAddrs helper to produce canonical validator address ordering for ValidatorPerformances map traversal |
| x/oracle/keeper/update_exchange_rates.go | 55 | uses sorted validator addresses before updating oracle miss counters |
| x/oracle/keeper/update_exchange_rates.go | 29 | uses sorted validator addresses before emitting validator performance events during UpdateExchangeRates |
| x/oracle/keeper/reward.go | 42 | uses sorted validator addresses before distributing oracle rewards to winning validators |

## Code Snippets

## Snippet 1

Context: `x/oracle/types/ballot.go:215` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (vp ValidatorPerformance) String() string {
	jsonBz, _ := json.MarshalIndent(vp, "", "  ")
```
After
```go
}

// SortedAddrs returns validator addresses in sorted order for deterministic iteration.
// Go map iteration is non-deterministic, which can cause consensus failures
// if state is written in different order on different nodes.
func (vp ValidatorPerformances) SortedAddrs() []string {
	addrs := make([]string, 0, len(vp))
	for addr := range vp {
```

## Snippet 2

Context: `x/oracle/keeper/update_exchange_rates.go:55` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
validatorPerformances types.ValidatorPerformances,
) {
	for _, validatorPerformance := range validatorPerformances {
		if int(validatorPerformance.MissCount) > 0 {
			k.MissCounters.Insert(
```
After
```go
validatorPerformances types.ValidatorPerformances,
) {
	// Sort validator addresses for deterministic iteration order.
	// Go map iteration is non-deterministic, which can cause consensus
	// failures if state is written in different order on different nodes.
	sortedAddrs := validatorPerformances.SortedAddrs()

	for _, valAddr := range sortedAddrs {
```

## Snippet 3

Context: `x/oracle/keeper/update_exchange_rates.go:29` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
k.refreshWhitelist(ctx, params.Whitelist, whitelistedPairs)

	for _, validatorPerformance := range validatorPerformances {
		_ = ctx.EventManager().EmitTypedEvent(&types.EventValidatorPerformance{
			Validator:    validatorPerformance.ValAddress.String(),
```
After
```go
k.refreshWhitelist(ctx, params.Whitelist, whitelistedPairs)

	// Sort validator addresses for deterministic event emission order.
	// Go map iteration is non-deterministic, which can cause consensus
	// failures if events are emitted in different order on different nodes.
	sortedAddrs := validatorPerformances.SortedAddrs()
	for _, valAddr := range sortedAddrs {
		validatorPerformance := validatorPerformances[valAddr]
```

## Snippet 4

Context: `x/oracle/keeper/reward.go:42` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
totalRewards = totalRewards.Add(sdk.NewDecCoinsFromCoins(rewards...)...)

	var distributedRewards sdk.Coins
	for _, validatorPerformance := range validatorPerformances {
		validator := k.StakingKeeper.Validator(ctx, validatorPerformance.ValAddress)
		if validator == nil {
```
After
```go
totalRewards = totalRewards.Add(sdk.NewDecCoinsFromCoins(rewards...)...)

	// Sort validator addresses for deterministic iteration order.
	// Go map iteration is non-deterministic, which can cause consensus
	// failures if state is written in different order on different nodes.
	sortedAddrs := validatorPerformances.SortedAddrs()

	var distributedRewards sdk.Coins
```

# Fix Pattern

In consensus-critical paths, do not range directly over Go maps when state writes or ordered outputs may depend on traversal order. Extract map keys, sort them canonically, and iterate through the sorted keys.

## How It Was Fixed

x/oracle/types/ballot.go adds ValidatorPerformances.SortedAddrs(). x/oracle/keeper/update_exchange_rates.go uses it before miss-counter updates and validator performance event emission. x/oracle/keeper/reward.go uses it before reward processing. The EVM state-db change mentioned in the commit body was reverted and is not part of the final patch evidence.

# Why It Matters

1. Identical oracle inputs must produce identical state roots and block results.

2. Go map iteration order can differ across nodes.

3. The changed paths include state updates and event emission in the oracle update flow.

4. The evidence supports AppHash mismatch and consensus failure risk.

5. The evidence does not support direct theft, oracle price manipulation, or cryptographic failure.

# Evidence Notes

Primary evidence is the added SortedAddrs helper in x/oracle/types/ballot.go and replacement of direct validatorPerformances map ranges in x/oracle/keeper/update_exchange_rates.go and x/oracle/keeper/reward.go. Inline comments and the commit message explicitly identify nondeterministic Go map iteration as capable of causing consensus failures, and the commit message reports intermittent AppHash mismatches on long-running mainnet nodes. Claims about RPC/client serialization, price manipulation, direct reward theft, or cryptographic failure are unsupported by the provided diff. Protocol security invariant: Validators executing the oracle exchange-rate update path must process consensus-visible state changes and block-result outputs in a deterministic order for identical inputs. Directly ranging over a Go map violates that invariant because map iteration order is not stable across processes. Verification notes: The patch does not prove funds theft or direct reward theft. The patch does not prove oracle price manipulation. The patch does not show an externally triggerable exploit strategy. The EVM state-db change mentioned in the commit body was reverted and is not part of the final affected files. The evidence supports consensus nondeterminism, not a cryptographic failure. No external exploit path is demonstrated in the provided evidence. The final changed file set is limited to oracle keeper/types paths. The helper is support code for deterministic traversal, not an independent root cause. Security classification rests on consensus nondeterminism and reported AppHash mismatch risk. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `consensus-nondeterminism`
Final impact type: `state-divergence, consensus-failure`
Final tags: `blockchain-core, oracle, validator, consensus, determinism, go-map-iteration`

The supplied patch evidence supports a security-relevant consensus fix. The code changed oracle keeper paths that update state, distribute rewards, and emit ordered events from direct Go map iteration to sorted validator-address iteration, with comments and commit text explicitly tying the bug to nondeterministic execution, AppHash mismatches, and consensus failures. The original RPC/client framing is misleading; this is an oracle consensus determinism issue, not an RPC-client API issue.

## Security Evidence

1. Adds ValidatorPerformances.SortedAddrs() to canonicalize map key order.
2. Replaces direct iteration over validatorPerformances in miss-counter state updates.
3. Replaces direct iteration over validatorPerformances in oracle reward distribution.
4. Replaces direct iteration over validatorPerformances for validator performance event emission.
5. Commit body reports intermittent AppHash mismatches on long-running mainnet nodes.

## Missing Evidence

1. No exploit strategy or attacker trigger path is shown.
2. No proof of direct theft, price manipulation, or privilege bypass is shown.
3. No tests or incident logs are included beyond the commit message statement.

## Claim Boundaries

1. Validated as consensus nondeterminism in oracle keeper logic.
2. Do not classify as RPC/client API, cryptographic failure, or direct fund loss.
3. Impact should be limited to state divergence, AppHash mismatch, and consensus failure risk.
4. The reverted EVM state-db change is not part of the validated finding.
