---
case_id: case_20250506_4523d3d13
project: sei-chain
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: rpc-client-api
source_quality: high
date: 2025-05-06
source_refs:
  - git:4523d3d13ffcaf06743b3701e8310d8d7701e9bc
  - "x/oracle/keeper/keeper.go:580"
  - "x/oracle/ante.go:100"
  - "x/oracle/keeper/keeper_test.go:818"
  - "x/oracle/keeper/keeper.go:601"
bug_class: check-then-set-race
impact_type:
  - spam-prevention-bypass
  - validator-invariant-hardening
confidence: medium
tags:
  - blockchain-core
  - oracle
  - ante-handler
  - spam-prevention
  - validator
  - concurrency
  - race-condition
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens oracle transaction spam prevention by replacing a split read-then-write counter check in the ante decorator with a keeper-level `CheckAndSetSpamPreventionCounter` method that locks per validator address, checks the current block height, and updates the counter while holding the lock.

## Observed Patch Facts

1. In `x/oracle/keeper/keeper.go`, the patch replaces `func (k Keeper) GetSpamPreventionCounter(ctx sdk.Context, validatorAddr sdk.ValAddres...` with `func (k Keeper) CheckAndSetSpamPreventionCounter(ctx sdk.Context, validatorAddr sdk.V...`.

2. In `x/oracle/ante.go`, the patch replaces `spamPreventionCounterHeight := spd.oracleKeeper.GetSpamPreventionCounter(ctx, valAddr)` with `if err := spd.oracleKeeper.CheckAndSetSpamPreventionCounter(ctx, valAddr); err != nil {`.

3. In `x/oracle/keeper/keeper_test.go`, the patch replaces `// verify value == -1 when not set` with `require.NoError(t, input.OracleKeeper.CheckAndSetSpamPreventionCounter(input.Ctx, sdk...`.

4. In `x/oracle/keeper/keeper.go`, the patch replaces `func (k Keeper) SetSpamPreventionCounter(ctx sdk.Context, validatorAddr sdk.ValAddres...` with `func (k Keeper) setSpamPreventionCounter(ctx sdk.Context, validatorAddr sdk.ValAddres...`.

## Project Context

The changed code sits primarily in `x/oracle/keeper`, `x/oracle`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `x/oracle/keeper/querier_test.go`, `x/oracle/keeper/migrations_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/oracle/keeper/querier_test.go`, `x/oracle/keeper/migrations_test.go`. The strongest project-level identifiers around this patch are `input`, `ValAddress`, `validatorAddr`, and `OracleKeeper`. Nearby tests or test-like files include `x/oracle/spec/05_events.md`, `x/oracle/spec/04_messages.md`.

## Before/After Behavior

Before the patch, `x/oracle/ante.go` read the validator spam-prevention counter, compared it to the current height, and then separately called `SetSpamPreventionCounter`. After the patch, the ante decorator calls `CheckAndSetSpamPreventionCounter`, which performs the check and set under a per-validator mutex. Tests now exercise first-call success, duplicate same-height failure, later-height success, and different-validator success through the combined method.

# Root Cause

The supported root cause is a split check/update sequence for the oracle spam-prevention counter. If the same validator's oracle vote path can be evaluated concurrently, two executions could both observe that the counter was not yet set for the current height before either writes it. The provided evidence does not prove that such concurrency occurs in production, so this is best classified as hardening rather than a confirmed exploited vulnerability.

## Walkthrough

1. A `MsgAggregateExchangeRateVote` reaches `SpammingPreventionDecorator.CheckOracleSpamming`.

2. The decorator parses feeder and validator addresses and validates the feeder for the validator.

3. Before the patch, the decorator called `GetSpamPreventionCounter`, compared the result to the current block height, and then separately called `SetSpamPreventionCounter`.

4. The patch introduces `CheckAndSetSpamPreventionCounter` in the keeper.

5. That method loads or creates a mutex keyed by `validatorAddr.String()`, locks it, checks the stored counter against `ctx.BlockHeight()`, and sets the counter before unlocking.

6. The ante decorator now uses the combined method instead of separate get/set calls.

7. The raw setter is renamed to internal `setSpamPreventionCounter`, reducing direct external use of the unchecked mutation path.

8. The updated test verifies the intended duplicate-prevention behavior for same validator, later height, and different validators.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/oracle/ante.go | 100 | Oracle ante decorator call site now invokes atomic CheckAndSetSpamPreventionCounter after feeder validation for MsgAggregateExchangeRateVote. |
| x/oracle/keeper/keeper.go | 580 | Introduces per-validator mutex and combines counter check with counter update under the same lock. |
| x/oracle/keeper/keeper.go | 601 | Makes the raw counter setter internal so callers use the checked atomic path. |
| x/oracle/keeper/keeper_test.go | 817 | Updates tests to assert first submission succeeds, repeated same-height submission fails, and later height or different validator succeeds. |

## Code Snippets

## Snippet 1

Context: `x/oracle/keeper/keeper.go:580` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (k Keeper) GetSpamPreventionCounter(ctx sdk.Context, validatorAddr sdk.ValAddress) int64 {
	store := ctx.KVStore(k.memKey)
	bz := store.Get(types.GetSpamPreventionCounterKey(validatorAddr))
```
After
```go
}

func (k Keeper) CheckAndSetSpamPreventionCounter(ctx sdk.Context, validatorAddr sdk.ValAddress) error {
	mtx, _ := k.spamPreventionCounterMtxMap.LoadOrStore(validatorAddr.String(), &sync.Mutex{})
	mtx.Lock()
	defer mtx.Unlock()
	if k.getSpamPreventionCounter(ctx, validatorAddr) == ctx.BlockHeight() {
		return sdkerrors.Wrap(sdkerrors.ErrAlreadyExists, fmt.Sprintf("the validator has already submitted a vote at the current height=%d", ctx.BlockHeight()))
```

## Snippet 2

Context: `x/oracle/ante.go:100` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

			spamPreventionCounterHeight := spd.oracleKeeper.GetSpamPreventionCounter(ctx, valAddr)
			if spamPreventionCounterHeight == curHeight {
				return sdkerrors.Wrap(sdkerrors.ErrAlreadyExists, fmt.Sprintf("the validator has already submitted a vote at the current height=%d", curHeight))
			}
			spd.oracleKeeper.SetSpamPreventionCounter(ctx, valAddr)
			continue
```
After
```go
}

			if err := spd.oracleKeeper.CheckAndSetSpamPreventionCounter(ctx, valAddr); err != nil {
				return err
			}
			continue
		default:
```

## Snippet 3

Context: `x/oracle/keeper/keeper_test.go:818` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
input := CreateTestInput(t)

	// verify value == -1 when not set
	require.Equal(t, int64(-1), input.OracleKeeper.GetSpamPreventionCounter(input.Ctx, sdk.ValAddress(Addrs[0])))

	input.Ctx = input.Ctx.WithBlockHeight(3)

	input.OracleKeeper.SetSpamPreventionCounter(input.Ctx, sdk.ValAddress(Addrs[0]))
```
After
```go
input := CreateTestInput(t)

	require.NoError(t, input.OracleKeeper.CheckAndSetSpamPreventionCounter(input.Ctx, sdk.ValAddress(Addrs[0])))
	require.Error(t, input.OracleKeeper.CheckAndSetSpamPreventionCounter(input.Ctx, sdk.ValAddress(Addrs[0])))

	input.Ctx = input.Ctx.WithBlockHeight(3)

	require.NoError(t, input.OracleKeeper.CheckAndSetSpamPreventionCounter(input.Ctx, sdk.ValAddress(Addrs[0])))
```

## Snippet 4

Context: `x/oracle/keeper/keeper.go:601` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (k Keeper) SetSpamPreventionCounter(ctx sdk.Context, validatorAddr sdk.ValAddress) {
	store := ctx.KVStore(k.memKey)
```
After
```go
}

func (k Keeper) setSpamPreventionCounter(ctx sdk.Context, validatorAddr sdk.ValAddress) {
	store := ctx.KVStore(k.memKey)
```

# Fix Pattern

Combine split check-then-update enforcement into one keeper method and guard it with a per-validator lock.

## How It Was Fixed

`x/oracle/keeper/keeper.go` adds `CheckAndSetSpamPreventionCounter`, which locks a mutex for the validator address, rejects if the stored counter equals the current block height, and otherwise writes the current height. `x/oracle/ante.go` calls this method after feeder validation. The direct setter is made internal, and tests are updated to use the combined API.

# Why It Matters

1. Protects the one-vote-per-validator-per-height spam-prevention invariant in this code path.

2. Removes a split read/write sequence that could be race-prone if ante handling is concurrent.

3. Keeps the change scoped to duplicate oracle vote spam prevention.

4. Does not establish price manipulation, consensus failure, or feeder authorization bypass.

# Evidence Notes

The strongest evidence is the replacement of separate `GetSpamPreventionCounter` and `SetSpamPreventionCounter` calls in `x/oracle/ante.go` with `CheckAndSetSpamPreventionCounter`, and the new keeper implementation using `spamPreventionCounterMtxMap.LoadOrStore`, `Lock`, `getSpamPreventionCounter`, and `setSpamPreventionCounter`. The heuristic baseline's RPC/client serialization claim is unsupported by the supplied diff and should be discarded. Practical exploitability is not proven because the supplied evidence does not show production concurrent ante execution. Protocol security invariant: For oracle aggregate exchange-rate votes handled by the ante spam-prevention path, a validator should not be able to submit more than once at the same block height. The counter check and counter update need to occur as one per-validator operation for that invariant to hold under concurrent evaluation. Verification notes: The patch does not prove that transaction ante processing is actually concurrent in production. The patch does not prove oracle price manipulation or consensus failure. The patch does not show an authentication or feeder-authorization bypass. The patch only supports duplicate same-height vote spam prevention for the same validator address. No evidence is shown for persistence issues beyond the in-memory spam-prevention counter. Grounded in changed lines from `x/oracle/ante.go`, `x/oracle/keeper/keeper.go`, and `x/oracle/keeper/keeper_test.go`. Confidence downgraded from high to medium because production concurrency and exploit impact are not established. Classified as security hardening, not a confirmed vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `check-then-set-race`
Final impact type: `spam-prevention-bypass, validator-invariant-hardening`
Final confidence: `medium`
Final tags: `blockchain-core, oracle, ante-handler, spam-prevention, validator, concurrency, race-condition`

The patch evidence supports retaining this as security hardening, not as the original RPC/client serialization finding. The change moves oracle vote spam-prevention enforcement from a separate read-then-write sequence into a keeper method that locks per validator, checks whether the validator already submitted at the current height, and sets the counter while holding the lock. That clearly tightens a validator-facing anti-spam invariant, but the supplied evidence does not prove production concurrent ante execution or a concrete exploit impact, so security-fix would be too strong.

## Security Evidence

1. Commit subject explicitly says "Harden oracle tx spam prevention".
2. The ante decorator replaces separate GetSpamPreventionCounter and SetSpamPreventionCounter calls with CheckAndSetSpamPreventionCounter.
3. The new keeper method uses a per-validator mutex before checking and setting the spam-prevention counter.
4. The duplicate same-height vote condition returns ErrAlreadyExists for the same validator.
5. The raw setter is made internal as setSpamPreventionCounter, reducing unchecked external mutation of the counter.
6. Tests now exercise first submission success, duplicate same-height failure, later-height success, and different-validator success.

## Missing Evidence

1. No evidence shows ante handling actually runs concurrently in production.
2. No evidence demonstrates an exploitable duplicate oracle vote attack.
3. No evidence proves oracle price manipulation, consensus failure, or validator authorization bypass.
4. No evidence supports the original rpc-client-api or serialization/state-representation classification.

## Claim Boundaries

1. This should be described as oracle transaction spam-prevention hardening.
2. The supported issue is a possible check-then-set race or atomicity weakness around a per-validator counter.
3. Do not claim confirmed exploitation or a concrete vulnerability without more evidence.
4. Do not claim RPC/client divergence, serialization bugs, price manipulation, or consensus failure from this patch alone.
