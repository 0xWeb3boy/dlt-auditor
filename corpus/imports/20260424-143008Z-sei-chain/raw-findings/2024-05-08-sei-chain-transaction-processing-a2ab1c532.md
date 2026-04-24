---
case_id: case_20240508_a2ab1c532
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2024-05-08
source_refs:
  - git:a2ab1c5324a34a8055ef4a4416bf48e34cc20427
  - "x/evm/ante/fee.go:88"
  - "x/evm/module.go:238"
  - "x/evm/module.go:144"
  - "x/evm/state/statedb.go:114"
bug_class: monetary-accounting-invariant
impact_type:
  - supply-integrity
  - accounting-integrity
confidence: medium
tags:
  - blockchain
  - evm
  - transaction-processing
  - fee-accounting
  - total-supply
  - monetary-invariant
  - migration
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a security-relevant EVM surplus accounting bug. The strongest supported finding is that ante surplus was mishandled across ante processing, EndBlock aggregation, and total supply repair. The evidence supports a supply-accounting mismatch, not a crash, theft, replay, cryptographic validation, or proven attacker-controlled minting issue.

## Observed Patch Facts

1. In `x/evm/ante/fee.go`, the patch replaces `msg.Derived.AnteSurplus = surplus` with `if err := fc.evmKeeper.AddAnteSurplus(ctx, etx.Hash(), surplus); err != nil {`.

2. In `x/evm/module.go`, the patch adds `if surplus.IsPositive() {`.

3. In `x/evm/module.go`, the patch adds `_ = cfg.RegisterMigration(types.ModuleName, 5, func(ctx sdk.Context) error {`.

4. In `x/evm/state/statedb.go`, the patch removes `if surplus.IsNegative() {`.

## Project Context

The changed code sits primarily in `x/evm/ante`, `x/evm`, `x/evm/state`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/evm/state/expected_keepers.go`, `x/evm/state/balance_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/state/balance_test.go`, `x/evm/state/balance.go`. The strongest project-level identifiers around this patch are `surplus`, `surplusUsei`, `keeper`, and `types`. Nearby tests or test-like files include `x/evm/blocktest/config.go`.

## Before/After Behavior

Before the patch, ante processing assigned finalized surplus to msg.Derived.AnteSurplus, EndBlock split and added aggregate surplus without the shown positive-net guard, and stateDB.Finalize rejected negative surplus. After the patch, ante surplus is written through AddAnteSurplus keyed by transaction hash, EndBlock starts from GetAnteSurplusSum and only performs add operations when the net surplus is positive, and Finalize returns negative surplus so it can be netted. A version 5 migration was also registered to fix total supply mismatch caused by mishandled ante surplus.

# Root Cause

Surplus accounting was handled inconsistently across EVM ante finalization, deferred transaction accounting, and EndBlock balance updates. Negative surplus could be rejected before netting, and ante surplus was not recorded through the keeper path now used for EndBlock aggregation.

## Walkthrough

1. AnteHandle runs EVM fee checks, buys gas, finalizes stateDB, and receives a surplus value.

2. The old code stored that value in msg.Derived.AnteSurplus; the fixed code calls fc.evmKeeper.AddAnteSurplus(ctx, etx.Hash(), surplus) and returns write errors.

3. EndBlock now reads am.keeper.GetAnteSurplusSum(ctx) and adds deferredInfo.Surplus values from deferred EVM transaction info.

4. EndBlock only splits and adds surplus coins/wei when the aggregate surplus is positive.

5. stateDB.Finalize no longer errors on negative surplus, allowing negative values to offset positive values later.

6. RegisterServices adds migration version 5, and the migration excerpt describes fixing total supply mismatch caused by mishandled ante surplus.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/ante/fee.go | 88 | records finalized ante surplus through keeper state instead of mutating derived transaction metadata |
| x/evm/module.go | 238 | aggregates ante and deferred EVM surplus at EndBlock and only adds module coins/wei for positive net surplus |
| x/evm/module.go | 144 | registers migration that repairs total supply after the surplus accounting bug |
| x/evm/state/statedb.go | 114 | allows finalized surplus to be negative so EndBlock can net surplus values instead of rejecting them early |
| x/evm/migrations/fix_total_supply.go | 1 | migration path for correcting total supply mismatch caused by mishandled ante surplus |

## Code Snippets

## Snippet 1

Context: `x/evm/ante/fee.go:88` (changes signature or replay validation logic)

Before
```go
return ctx, err
		}
		msg.Derived.AnteSurplus = surplus
	}
```
After
```go
return ctx, err
		}
		if err := fc.evmKeeper.AddAnteSurplus(ctx, etx.Hash(), surplus); err != nil {
			return ctx, err
		}
	}
```

## Snippet 2

Context: `x/evm/module.go:238` (changes persisted or aggregate state handling)

Before
```go
surplus = surplus.Add(deferredInfo.Surplus)
	}
	surplusUsei, surplusWei := state.SplitUseiWeiAmount(surplus.BigInt())
	if surplusUsei.GT(sdk.ZeroInt()) {
		if err := am.keeper.BankKeeper().AddCoins(ctx, am.keeper.AccountKeeper().GetModuleAddress(types.ModuleName), sdk.NewCoins(sdk.NewCoin(am.keeper.GetBaseDenom(ctx), surplusUsei)), true); err != nil {
			ctx.Logger().Error("failed to send usei surplus of %s to EVM module account", surplusUsei)
		}
	}
```
After
```go
surplus = surplus.Add(deferredInfo.Surplus)
	}
	if surplus.IsPositive() {
		surplusUsei, surplusWei := state.SplitUseiWeiAmount(surplus.BigInt())
		if surplusUsei.GT(sdk.ZeroInt()) {
			if err := am.keeper.BankKeeper().AddCoins(ctx, am.keeper.AccountKeeper().GetModuleAddress(types.ModuleName), sdk.NewCoins(sdk.NewCoin(am.keeper.GetBaseDenom(ctx), surplusUsei)), true); err != nil {
				ctx.Logger().Error("failed to send usei surplus of %s to EVM module account", surplusUsei)
			}
```

## Snippet 3

Context: `x/evm/module.go:144` (changes a sensitive control or state-update path)

Before
```go
return migrations.StoreCWPointerCode(ctx, am.keeper)
	})
}
```
After
```go
return migrations.StoreCWPointerCode(ctx, am.keeper)
	})

	_ = cfg.RegisterMigration(types.ModuleName, 5, func(ctx sdk.Context) error {
		return migrations.FixTotalSupply(ctx, am.keeper)
	})
}
```

## Snippet 4

Context: `x/evm/state/statedb.go:114` (changes a sensitive control or state-update path)

Before
```go
surplus = surplus.Add(ts.surplus)
	}
	if surplus.IsNegative() {
		err = fmt.Errorf("negative surplus value: %s", surplus.String())
	}
	return
}
```
After
```go
surplus = surplus.Add(ts.surplus)
	}
	return
}
```

# Fix Pattern

Move accounting deltas into keeper-managed state, aggregate related surplus values at EndBlock, net positive and negative values before adding balances, and repair historical total supply drift with a targeted migration.

## How It Was Fixed

The patch replaces derived-message surplus assignment with AddAnteSurplus, updates EndBlock to combine ante and deferred surplus before performing positive-only add operations, permits negative surplus to flow out of Finalize for netting, and registers FixTotalSupply as a module migration.

# Why It Matters

1. Protects the chain's monetary accounting invariant.

2. Prevents surplus values from being added before proper netting.

3. Includes a migration for historical total supply mismatch.

4. Does not prove theft, attacker-controlled minting, node crash, or consensus divergence.

# Evidence Notes

Grounded evidence comes from x/evm/ante/fee.go, x/evm/module.go, x/evm/state/statedb.go, and x/evm/migrations/fix_total_supply.go. The migration comment explicitly ties the change to total supply mismatch from mishandled ante surplus. The provided snippets do not establish exploitability, magnitude, attacker control, or a cryptographic/replay issue. Protocol security invariant: EVM ante and EndBlock surplus handling must preserve monetary accounting: surplus values produced during EVM transaction processing should be recorded consistently and netted before module balances or total supply are adjusted. Verification notes: No evidence proves remote transaction input can directly trigger a node crash. No evidence proves an attacker can steal funds or mint spendable funds on demand. No evidence proves consensus divergence between honest nodes. The patch does not show cryptographic, signature, or replay-validation logic being fixed. The exact magnitude and trigger conditions of the total supply mismatch are not proven by the provided snippets. No evidence supports the heuristic panic or malformed-input denial-of-service theory. No evidence supports fund theft or attacker-controlled spendable minting. No evidence supports consensus divergence between honest nodes. Security classification rests on the monetary supply-accounting invariant and the explicit total supply mismatch migration. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `monetary-accounting-invariant`
Final impact type: `supply-integrity, accounting-integrity`
Final confidence: `medium`
Final tags: `blockchain, evm, transaction-processing, fee-accounting, total-supply, monetary-invariant, migration`

The supplied evidence supports a security-hardening classification rather than a proven security-fix. The patch changes EVM ante surplus recording, EndBlock surplus aggregation, negative-surplus netting, and registers a migration explicitly described as fixing a total supply mismatch caused by mishandled ante surplus. That is security-relevant in a blockchain because it tightens monetary accounting invariants, but the evidence does not prove exploitability, attacker control, liveness failure, replay impact, theft, or consensus divergence.

## Security Evidence

1. Ante surplus is moved from derived transaction metadata to keeper-managed state keyed by transaction hash.
2. EndBlock now aggregates ante surplus with deferred EVM surplus and only adds balances when the net surplus is positive.
3. Finalize no longer rejects negative surplus, allowing negative and positive surplus values to be netted before supply-affecting operations.
4. A module migration is registered, and the migration context states it fixes a total supply mismatch caused by mishandled ante surplus.

## Missing Evidence

1. No proof that an attacker could trigger or control the mismatch.
2. No demonstrated theft, spendable minting, or direct fund loss.
3. No evidence of consensus divergence or validator liveness failure.
4. No evidence that replay, cryptographic validation, or signature logic was affected.
5. No magnitude, trigger conditions, or exploit path for the total supply mismatch is provided.

## Claim Boundaries

1. Retain as a monetary accounting hardening case, not as a confirmed exploitable vulnerability.
2. Do not classify as liveness-failure based on the supplied patch evidence.
3. Do not claim replay or cryptographic impact.
4. Do not claim attacker-controlled minting, theft, or consensus failure.
5. The strongest supported impact is preservation or repair of total supply/accounting integrity.
