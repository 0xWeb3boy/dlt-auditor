---
case_id: case_20200422_d477a90f7
project: oasis-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: staking
source_quality: high
date: 2020-04-22
source_refs:
  - git:d477a90f71d459d3333707473d9e73dbe212d2eb
  - "go/consensus/tendermint/apps/scheduler/scheduler.go:615"
  - "go/scheduler/api/api.go:249"
  - "go/scheduler/api/api.go:149"
  - "go/consensus/tendermint/apps/scheduler/scheduler.go:593"
bug_class: incorrect-validator-voting-power
impact_type:
  - consensus-integrity
confidence: medium
tags:
  - blockchain-core
  - consensus
  - staking
  - validator
  - voting-power
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes validator-set construction so elected validators carry explicit voting power derived from stake, and it adds a shared token-to-power conversion helper. That supports a stake-weight correctness fix in consensus-facing code, but the provided evidence does not establish a concrete security vulnerability or exploit.

## Observed Patch Facts

1. In `go/consensus/tendermint/apps/scheduler/scheduler.go`, the patch replaces `newValidators = append(newValidators, n.Consensus.ID)` with `var power int64`.

2. In `go/scheduler/api/api.go`, the patch adds `func init() {`.

3. In `go/scheduler/api/api.go`, the patch replaces `// Validator is a consensus validator.` with `// TokensPerVotingPower is the ratio of base units staked to validator power.`.

4. In `go/consensus/tendermint/apps/scheduler/scheduler.go`, the patch replaces `var newValidators []signature.PublicKey` with `newValidators := make(map[signature.PublicKey]int64)`.

## Project Context

The changed code sits primarily in `go/consensus/tendermint/apps/scheduler`, `go/consensus/tendermint/apps`, `go/scheduler/api`, which anchors the finding in the `staking` area of the project. Historical context from `go/consensus/tendermint/apps/scheduler/query.go`, `go/consensus/tendermint/apps/scheduler/genesis.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/consensus/tendermint/apps/staking/slashing.go`, `go/consensus/tendermint/apps/scheduler/query.go`. The strongest project-level identifiers around this patch are `power`, `newValidators`, `TokensPerVotingPower`, and `stake`. Nearby tests or test-like files include `go/scheduler/tests/tester.go`.

## Before/After Behavior

Before the patch, the shown election path built `newValidators` as a `[]signature.PublicKey` and appended validator identities without any visible stake-to-power computation in that snippet. After the patch, `newValidators` becomes a `map[signature.PublicKey]int64`, the code computes `power` for each elected validator, uses `power = 1` only when `stakeAcc == nil`, and otherwise fetches escrow balance and converts it with `scheduler.VotingPowerFromTokens(stake)`. The API layer also adds `TokensPerVotingPower`, `VotingPowerFromTokens`, and default initialization for that ratio.

# Root Cause

The scheduler election path previously did not assign explicit stake-derived voting power in the shown validator-set construction path; the patch adds that missing mapping.

## Walkthrough

1. `electValidators` changes `newValidators` from a slice of public keys to a map from public key to `int64` power.

2. Inside the election loop, the patch introduces a local `power` variable before recording the elected validator.

3. If `stakeAcc == nil`, the code explicitly assigns flat power `1`, with a comment limiting that behavior to simplified no-stake deployments.

4. If staking is enabled, the code fetches the elected entity's escrow balance with `stakeAcc.GetEscrowBalance(v)` and returns an error on failure.

5. The path then converts stake to voting power with `scheduler.VotingPowerFromTokens(stake)`.

6. `go/scheduler/api/api.go` adds `TokensPerVotingPower` and the `VotingPowerFromTokens` helper, including checked division and `int64` conversion.

7. The same file initializes the default conversion ratio in `init()`.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/consensus/tendermint/apps/scheduler/scheduler.go | 593 | validator election path now builds the next validator set with explicit voting power entries instead of only validator identities |
| go/consensus/tendermint/apps/scheduler/scheduler.go | 615 | computes each elected validator's voting power from escrowed stake, with flat power reserved for no-stake deployments |
| go/scheduler/api/api.go | 149 | defines the canonical token-to-voting-power conversion helper used by scheduler consensus logic |
| go/scheduler/api/api.go | 249 | initializes the default TokensPerVotingPower ratio that sets the stake-to-power baseline |

## Code Snippets

## Snippet 1

Context: `go/consensus/tendermint/apps/scheduler/scheduler.go:615` (changes a consensus- or validator-sensitive branch)

Before
```go
}

			newValidators = append(newValidators, n.Consensus.ID)
			if len(newValidators) >= params.MaxValidators {
				break electLoop
```
After
```go
}

			var power int64
			if stakeAcc == nil {
				// In simplified no-stake deployments, make validators have flat voting power.
				power = 1
			} else {
				var stake *quantity.Quantity
```

## Snippet 2

Context: `go/scheduler/api/api.go:249` (changes a sensitive control or state-update path)

Before
```go
return nil
}
```
After
```go
return nil
}

func init() {
	// 2 allows for up to 1.8e19 base units to be staked.
	if err := TokensPerVotingPower.FromUint64(2); err != nil {
		panic(err)
	}
```

## Snippet 3

Context: `go/scheduler/api/api.go:149` (changes a sensitive control or state-update path)

Before
```go
}

// Validator is a consensus validator.
type Validator struct {
```
After
```go
}

// TokensPerVotingPower is the ratio of base units staked to validator power.
var TokensPerVotingPower quantity.Quantity

func VotingPowerFromTokens(t *quantity.Quantity) (int64, error) {
	powerQ := t.Clone()
	if err := powerQ.Quo(&TokensPerVotingPower); err != nil {
```

## Snippet 4

Context: `go/consensus/tendermint/apps/scheduler/scheduler.go:593` (changes signature or replay validation logic)

Before
```go
// Go down the list of entities running nodes by stake, picking one node
	// to act as a validator till the maximum is reached.
	var newValidators []signature.PublicKey
electLoop:
	for _, v := range sortedEntities {
```
After
```go
// Go down the list of entities running nodes by stake, picking one node
	// to act as a validator till the maximum is reached.
	newValidators := make(map[signature.PublicKey]int64)
electLoop:
	for _, v := range sortedEntities {
```

# Fix Pattern

Replace identity-only validator-set assembly with explicit power-bearing entries and centralize token-to-power conversion in a checked helper.

## How It Was Fixed

The fix updates validator election to compute and store per-validator voting power instead of only collecting validator identities. It also introduces a shared scheduler API helper for converting escrowed stake into voting power and initializes the default conversion ratio used by that helper.

# Why It Matters

1. It makes validator-set construction reflect stake-weighted consensus semantics in the shown path.

2. It limits equal-power behavior to an explicit no-stake branch instead of leaving it implicit.

3. It centralizes token-to-power conversion and its bounds checking in one helper.

# Evidence Notes

The evidence supports that validator power assignment was added to a consensus-facing scheduler path. It does not by itself prove that the old behavior caused a live consensus break, was exploitable by an attacker, or even that downstream handling previously treated all validators as equal power in all cases; that part is inferred from the changed types and new logic, not directly demonstrated. The added checked conversion helper is real, but the supplied diff does not establish that panic-avoidance or input-validation was the primary bug being fixed. Protocol security invariant: In stake-based deployments, the validator set constructed by the scheduler should carry voting power derived from escrowed stake through a deterministic conversion. Flat voting power is only consistent with an explicit no-stake mode. Verification notes: The patch does not prove that the prior equal-power behavior was exploitable on a live network. The diff does not show a remotely triggerable crash, memory-safety issue, or input-validation bug. The evidence does not establish that validator eligibility or ordering was wrong; it shows power assignment changed after election. The patch alone does not prove consensus safety failure or fund loss, only that stake-weighted voting power was not being enforced in this path. No provided commit text or test excerpt identifies this as a security fix. The pre-patch downstream behavior of the `[]signature.PublicKey` form is not shown, so security impact is not proven from the supplied evidence alone. The safest reading is consensus/stake-weight correctness work with possible security relevance, not a confirmed vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `incorrect-validator-voting-power`
Final impact type: `consensus-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, staking, validator, voting-power`

The patch changes a consensus-critical validator-election path from collecting validator identities to assigning explicit voting power derived from stake, and it confines flat power to an explicit no-stake mode. In a stake-based blockchain, validator voting power is security-sensitive because it defines consensus influence, so this is better treated as security hardening rather than a mere reliability change. However, the provided evidence does not prove a concrete exploitable vulnerability, live-network incident, or specific safety/liveness failure before the patch, so a conservative classification is security-hardening rather than security-fix.

## Security Evidence

1. Validator election changes `newValidators` from a list of public keys to a `map[signature.PublicKey]int64` carrying power.
2. In staking mode, the code fetches escrow balance and derives voting power with `VotingPowerFromTokens(stake)`.
3. Equal voting power is explicitly restricted to `stakeAcc == nil`, i.e. simplified no-stake deployments.
4. A shared token-to-power helper with checked division and `int64` bounds checking is introduced.
5. The commit subject explicitly states validator power is now set based on stake.

## Missing Evidence

1. No commit message, test excerpt, or comment identifies a concrete vulnerability or attack scenario.
2. The supplied diff does not show how the pre-patch `[]signature.PublicKey` form was consumed downstream.
3. No evidence demonstrates consensus breakage, slashing bypass, fund loss, or exploitability on a live network.
4. The patch alone does not prove the prior behavior was attacker-triggerable rather than protocol-correctness debt.

## Claim Boundaries

1. Supported: the patch hardens stake-weighted validator power handling in consensus-facing code.
2. Supported: pre-patch logic in this path did not visibly assign stake-derived voting power.
3. Not proven: a concrete exploitable security bug existed before the change.
4. Not proven: the specific impact was liveness failure rather than broader consensus-weight correctness risk.
