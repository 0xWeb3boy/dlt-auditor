---
case_id: case_20220803_8c6e9717
project: nibiru
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
source_quality: medium
date: 2022-08-03
source_refs:
  - git:8c6e971709ddcab2dabddffe4a36cc07ceea6d12
  - "x/perp/keeper/liquidate_test.go:70"
  - "x/perp/keeper/clearing_house.go:142"
  - "x/perp/keeper/liquidate_test.go:116"
  - "x/perp/keeper/msg_server_test.go:289"
bug_class: insufficient-margin-validation
impact_type:
  - economic-integrity
  - bad-debt-risk
confidence: medium
tags:
  - blockchain-core
  - perp
  - margin-validation
  - leverage-control
  - bad-debt
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is likely a security fix in the perpetuals margin path. The grounded evidence supports that the open/update flow was changed around post-position margin validation and that a prior test treating an extreme-leverage bad-debt scenario as a happy path was removed. The evidence does not fully show the before-state implementation of the missing check, so confirmed exploitability should not be claimed.

## Observed Patch Facts

1. In `x/perp/keeper/liquidate_test.go`, the patch removes `expectedBadDebt: sdk.MustNewDecFromStr("0"),`.

2. In `x/perp/keeper/clearing_house.go`, the patch replaces `return err` with `return types.ErrMarginRatioTooLow`.

3. In `x/perp/keeper/liquidate_test.go`, the patch adds `t.Log("increment block height and time for TWAP calculation")`.

4. In `x/perp/keeper/msg_server_test.go`, the patch adds `t.Log("increment block height and time for TWAP calculation")`.

## Project Context

The changed code sits primarily in `x/perp/keeper`, `x/perp`, which anchors the finding in the `storage` area of the project. Historical context from `x/perp/keeper/perp_test.go`, `x/perp/keeper/margin_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/perp/keeper/perp_test.go`, `x/perp/keeper/margin_test.go`. The strongest project-level identifiers around this patch are `time`, `types`, `position`, and `maintenanceMarginRatio`. Nearby tests or test-like files include `x/perp/keeper/clearing_house_integration_test.go`, `x/perp/spec/04_events.md`.

## Before/After Behavior

Before the patch, tests included a happy-path liquidation scenario where a trader used 10000x leverage with only 50 NUSD margin and expected bad debt. After the patch, that fixture is removed, tests advance block height/time before TWAP-dependent open-position paths, and `afterPositionUpdate` returns `types.ErrMarginRatioTooLow` when the margin-ratio requirement fails. The provided after-context shows nonzero bad debt being rejected and post-update margin ratio being checked against maintenance margin ratio.

# Root Cause

The supported root cause is insufficient enforcement of post-trade margin health on the perp position open/update path. The removed test case indicates that an extreme undercollateralized position leading to bad debt had previously been represented as valid behavior, but the snippets do not prove every missing pre-patch branch or caller behavior.

## Walkthrough

1. A trader opens or updates a perpetuals position, producing a `positionResp` handled by `afterPositionUpdate`.

2. The position update path persists nonzero positions and performs accounting-related checks before settlement continues.

3. The removed liquidation fixture modeled a 10000x long position with only 50 NUSD margin as a happy path that could lead to bad debt.

4. The after-context rejects nonzero `positionResp.BadDebt`.

5. The after-context computes the resulting margin ratio using `MarginCalculationPriceOption_MAX_PNL`.

6. The computed margin ratio is compared with the pool maintenance margin ratio through `requireMoreMarginRatio`.

7. If the check fails, the path returns `types.ErrMarginRatioTooLow`.

8. Test setup changes advance block height/time before open-position calls, apparently to support TWAP-dependent margin behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/perp/keeper/clearing_house.go | 115 | post-position-update path computes margin ratio, checks it against maintenance margin, and rejects too-low margin positions |
| x/perp/keeper/clearing_house.go | 142 | maps failed margin requirement to the explicit margin-ratio-too-low error returned by the open/update path |
| x/perp/keeper/liquidate_test.go | 25 | liquidation coverage no longer includes the removed extreme-leverage bad-debt scenario as a valid happy path |
| x/perp/keeper/liquidate_test.go | 110 | test setup advances block height/time before opening a position for TWAP-based margin calculations |
| x/perp/keeper/msg_server_test.go | 246 | message-server open-position test path advances block height/time before exercising position opening |

## Code Snippets

## Snippet 1

Context: `x/perp/keeper/liquidate_test.go:70` (changes a sensitive control or state-update path)

Before
```go
// perpEFBalance = startingBalance + openPositionDelta + liquidateDelta
			expectedPerpEFBalance: sdk.NewInt64Coin("NUSD", 1_046_972),
			expectedBadDebt:       sdk.MustNewDecFromStr("0"),
		},
		"happy path - bad debt, long": {
			/* We open a position for 500k, with a liquidation fee of 50k.
			This means 25k for the liquidator, and 25k for the perp fund.
			Because the user only have margin for 50, we create 24950 of bad
```
After
```go
// perpEFBalance = startingBalance + openPositionDelta + liquidateDelta
			expectedPerpEFBalance: sdk.NewInt64Coin("NUSD", 1_046_972),
		},
	}
```

## Snippet 2

Context: `x/perp/keeper/clearing_house.go:142` (changes a sensitive control or state-update path)

Before
```go
maintenanceMarginRatio := k.VpoolKeeper.GetMaintenanceMarginRatio(ctx, pair)
		if err = requireMoreMarginRatio(marginRatio, maintenanceMarginRatio, true); err != nil {
			return err
		}
	}
```
After
```go
maintenanceMarginRatio := k.VpoolKeeper.GetMaintenanceMarginRatio(ctx, pair)
		if err = requireMoreMarginRatio(marginRatio, maintenanceMarginRatio, true); err != nil {
			return types.ErrMarginRatioTooLow
		}
	}
```

## Snippet 3

Context: `x/perp/keeper/liquidate_test.go:116` (changes a sensitive control or state-update path)

Before
```go
require.NoError(t, err)

			t.Log("Open position")
			positionResp, err := nibiruApp.PerpKeeper.OpenPosition(
```
After
```go
require.NoError(t, err)

			t.Log("increment block height and time for TWAP calculation")
			ctx = ctx.WithBlockHeight(ctx.BlockHeight() + 1).
				WithBlockTime(time.Now().Add(time.Minute))

			t.Log("Open position")
			positionResp, err := nibiruApp.PerpKeeper.OpenPosition(
```

## Snippet 4

Context: `x/perp/keeper/msg_server_test.go:289` (changes a sensitive control or state-update path)

Before
```go
}

			resp, err := msgServer.OpenPosition(sdk.WrapSDKContext(ctx), &types.MsgOpenPosition{
				Sender:               tc.sender,
```
After
```go
}

			t.Log("increment block height and time for TWAP calculation")
			ctx = ctx.WithBlockHeight(ctx.BlockHeight() + 1).
				WithBlockTime(time.Now().Add(time.Minute))

			resp, err := msgServer.OpenPosition(sdk.WrapSDKContext(ctx), &types.MsgOpenPosition{
				Sender:               tc.sender,
```

# Fix Pattern

Add or enforce post-position-update margin-health validation in the business path, and remove tests that encoded undercollateralized bad-debt opens as valid behavior.

## How It Was Fixed

The patch removes the extreme-leverage bad-debt happy-path liquidation case, adjusts tests to set block height/time before TWAP-dependent open-position calculations, and maps failed margin-ratio validation to `types.ErrMarginRatioTooLow`. The provided after-context shows `afterPositionUpdate` checking bad debt and requiring the post-update margin ratio to exceed the maintenance margin ratio.

# Why It Matters

1. Prevents under-margined perp positions from being accepted as normal state.

2. Reduces risk of bad debt caused by effectively unbounded leverage.

3. Keeps the open/update path aligned with maintenance margin requirements.

4. The evidence does not prove historical loss of funds or a full external exploit path.

# Evidence Notes

Strongest evidence is the commit subject/body naming infinite leverage and margin-ratio checks, the removal of the 10000x bad-debt happy-path test in `x/perp/keeper/liquidate_test.go`, and the after-context in `x/perp/keeper/clearing_house.go` showing bad-debt rejection and maintenance-margin validation. The provided changed line in `clearing_house.go` only shows error normalization from `return err` to `return types.ErrMarginRatioTooLow`, so claims about the exact pre-patch missing code path should remain bounded. Protocol security invariant: A perpetuals position open or update must not leave the trader below the required maintenance margin ratio or allow position opening that creates bad debt/effectively unbounded leverage. Verification notes: The patch evidence supports rejection of under-margined or effectively infinite-leverage opens, but does not prove a complete external exploit path. The evidence does not prove loss of funds occurred before the patch. The provided snippets do not show every caller of `afterPositionUpdate` or the full transaction rollback semantics. The test-only TWAP timing changes are supporting evidence, not independently security-relevant. Do not claim confirmed loss of funds from the provided evidence. Do not classify this as storage state-corruption; the supported subsystem is perp margin/accounting. Treat TWAP timing test changes as supporting test setup, not the root cause. Confidence is medium because the full before/after implementation diff for the added margin-ratio check is not shown. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-margin-validation`
Final impact type: `economic-integrity, bad-debt-risk`
Final confidence: `medium`
Final tags: `blockchain-core, perp, margin-validation, leverage-control, bad-debt`

The evidence supports retaining this as security hardening rather than a confirmed security fix. The commit explicitly targets blocking infinite leverage positions, the code context shows post-position checks for bad debt and maintenance margin ratio, and a prior test case treating an extreme-leverage bad-debt scenario as valid was removed. However, the supplied diff snippets do not fully show the pre-patch missing validation or a complete exploitable path, so the original storage/state-corruption framing is too broad and the security-fix classification is stronger than the evidence proves.

## Security Evidence

1. Commit subject says users are blocked from opening infinite leverage positions.
2. Commit body says a margin-ratio check was added when opening a new position.
3. Perp keeper code rejects nonzero bad debt with an attacker-focused error message in the provided after-context.
4. Post-position update path compares margin ratio against maintenance margin and returns ErrMarginRatioTooLow on failure.
5. A removed liquidation test case modeled a 10000x leverage position with only 50 NUSD margin creating bad debt as a happy path.

## Missing Evidence

1. The supplied changed lines do not show the full before/after addition of the margin-ratio check.
2. No complete external exploit transaction or loss scenario is demonstrated.
3. No caller or rollback semantics are shown to prove exactly how bad state could persist before the patch.
4. TWAP timing test changes are not independently security evidence.

## Claim Boundaries

1. Do not classify this as storage state corruption; the supported area is perp margin/accounting.
2. Do not claim confirmed exploitation or realized loss of funds.
3. Treat this as preventing or tightening an exposed risky economic condition, not as proof of a concrete exploited vulnerability.
4. The supported issue is insufficient margin/leverage validation that could allow bad debt or effectively infinite leverage.
