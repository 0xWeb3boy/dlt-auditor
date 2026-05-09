---
case_id: case_20230601_ffad80c2
project: nibiru
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: rpc-client-api
source_quality: medium
date: 2023-06-01
source_refs:
  - git:ffad80c28523d05f91461d3f691f5d64dacd489f
  - "x/perp/v2/keeper/clearing_house.go:528"
  - "x/perp/v2/keeper/margin.go:160"
  - "x/perp/v2/keeper/clearing_house.go:583"
  - "x/perp/v2/keeper/clearing_house.go:456"
bug_class: missing-margin-ratio-check
impact_type:
  - undercollateralized-position
  - economic-distortion
confidence: medium
tags:
  - blockchain-core
  - perp
  - margin
  - collateral
  - liquidation-threshold
  - accounting-invariant
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Likely security fix in the perp margin keeper. The patch adds a shared `checkMarginRatio` helper and uses it to validate updated positions, most importantly in `RemoveMargin` after applying funding and margin removal but before withdrawing funds from the vault.

## Observed Patch Facts

1. In `x/perp/v2/keeper/clearing_house.go`, the patch replaces `spotNotional, err := PositionNotionalSpot(amm, positionResp.Position)` with `err = k.checkMarginRatio(ctx, market, amm, positionResp.Position)`.

2. In `x/perp/v2/keeper/margin.go`, the patch replaces `if err = k.Withdraw(ctx, market, traderAddr, marginToRemove.Amount); err != nil {` with `position.LatestCumulativePremiumFraction = market.LatestCumulativePremiumFraction`.

3. In `x/perp/v2/keeper/clearing_house.go`, the patch replaces `// transfers the fee to the exchange fee pool` with `// checkMarginRatio checks if the margin ratio of the position is below the liquidati...`.

4. In `x/perp/v2/keeper/clearing_house.go`, the patch adds `err = k.checkMarginRatio(ctx, market, amm, increasePositionResp.Position)`.

## Project Context

The changed code sits primarily in `x/perp/v2/keeper`, `x/perp/v2`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `x/perp/v2/keeper/liquidate.go`, `x/perp/v2/keeper/grpc_query.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/perp/v2/keeper/liquidate.go`, `x/perp/v2/keeper/grpc_query.go`. The strongest project-level identifiers around this patch are `position`, `market`, `Position`, and `positionResp`. Nearby tests or test-like files include `x/perp/v2/integration/action/position.go`, `x/perp/v2/integration/assertion/position.go`.

## Before/After Behavior

Before the patch, the shown `RemoveMargin` path checked whether `remainingMargin` covered the requested removal amount and then called `Withdraw` before the position object was updated with funding payment and removed margin. The provided evidence does not show a post-removal margin-ratio check on that final state. After the patch, `RemoveMargin` updates the in-memory position, calls `checkMarginRatio`, returns on failure, and only then calls `WithdrawFromVault`. `afterPositionUpdate` now uses the same helper instead of inline margin-ratio logic, and `closeAndOpenReversePosition` adds the helper check after increasing the reverse position.

# Root Cause

The margin-removal path validated free collateral but did not clearly enforce the liquidation-threshold margin-ratio invariant on the final position state after funding payment and requested margin removal were applied.

## Walkthrough

1. A trader has an existing perp position for a market pair.

2. `RemoveMargin` fetches the market, AMM, and position and computes remaining margin using spot/TWAP notional, funding payment, and unrealized PnL.

3. In the pre-patch evidence, passing the remaining-margin check led to a withdrawal before the shown position update and without a shown margin-ratio check on the resulting position.

4. The patch applies funding and margin removal to the position object first.

5. The updated position is passed to `checkMarginRatio`; if it fails, the function returns before vault withdrawal.

6. The same helper is used after normal position updates and after increased reverse-position creation, making the shown paths enforce the same margin-ratio rule.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/perp/v2/keeper/margin.go | 113 | RemoveMargin computes remaining margin, applies funding and requested margin removal, then validates the resulting position before vault withdrawal. |
| x/perp/v2/keeper/margin.go | 160 | Changed ordering removes the prior direct Withdraw call and adds checkMarginRatio before WithdrawFromVault. |
| x/perp/v2/keeper/clearing_house.go | 583 | New shared checkMarginRatio helper computes spot and TWAP notionals and enforces the liquidation-threshold margin requirement. |
| x/perp/v2/keeper/clearing_house.go | 512 | afterPositionUpdate now calls the shared margin-ratio check for nonzero updated positions. |
| x/perp/v2/keeper/clearing_house.go | 450 | closeAndOpenReversePosition now validates the increased reverse position margin ratio before continuing. |

## Code Snippets

## Snippet 1

Context: `x/perp/v2/keeper/clearing_house.go:528` (updates aggregate accounting or lifecycle state)

Before
```go
if !positionResp.Position.Size_.IsZero() {
		spotNotional, err := PositionNotionalSpot(amm, positionResp.Position)
		if err != nil {
			return err
		}
		twapNotional, err := k.PositionNotionalTWAP(ctx, positionResp.Position, market.TwapLookbackWindow)
		if err != nil {
```
After
```go
if !positionResp.Position.Size_.IsZero() {
		err = k.checkMarginRatio(ctx, market, amm, positionResp.Position)
		if err != nil {
			return err
		}
	}
```

## Snippet 2

Context: `x/perp/v2/keeper/margin.go:160` (updates aggregate accounting or lifecycle state)

Before
```go
}

	if err = k.Withdraw(ctx, market, traderAddr, marginToRemove.Amount); err != nil {
		return nil, err
	}

	// apply funding payment and remove margin
	position.Margin = position.Margin.Sub(fundingPayment).Sub(sdk.NewDecFromInt(marginToRemove.Amount))
```
After
```go
}

	// apply funding payment and remove margin
	position.Margin = position.Margin.Sub(fundingPayment).Sub(sdk.NewDecFromInt(marginToRemove.Amount))
	position.LatestCumulativePremiumFraction = market.LatestCumulativePremiumFraction
	position.LastUpdatedBlockNumber = ctx.BlockHeight()

	err = k.checkMarginRatio(ctx, market, amm, position)
```

## Snippet 3

Context: `x/perp/v2/keeper/clearing_house.go:583` (updates aggregate accounting or lifecycle state)

Before
```go
}

// transfers the fee to the exchange fee pool
//
```
After
```go
}

// checkMarginRatio checks if the margin ratio of the position is below the liquidation threshold.
func (k Keeper) checkMarginRatio(ctx sdk.Context, market types.Market, amm types.AMM, position types.Position) (err error) {
	spotNotional, err := PositionNotionalSpot(amm, position)
	if err != nil {
		return
	}
```

## Snippet 4

Context: `x/perp/v2/keeper/clearing_house.go:456` (updates aggregate accounting or lifecycle state)

Before
```go
return nil, nil, err
		}

		positionResp = &types.PositionResp{
```
After
```go
return nil, nil, err
		}
		err = k.checkMarginRatio(ctx, market, amm, increasePositionResp.Position)
		if err != nil {
			return
		}

		positionResp = &types.PositionResp{
```

# Fix Pattern

Validate the final post-mutation position state against the margin-ratio invariant before allowing collateral withdrawal or completing position-update flows.

## How It Was Fixed

The patch adds `checkMarginRatio(ctx, market, amm, position)` in `clearing_house.go`. The helper computes spot and TWAP notionals, selects the side-dependent preferred notional, and checks whether the position is below the liquidation threshold. `RemoveMargin` now applies funding and margin removal to the position object, checks that updated position, and only then withdraws from the vault. Existing and newly covered position-update paths call the shared helper.

# Why It Matters

1. Prevents margin removal from relying only on free-collateral arithmetic when the final margin ratio may be too low.

2. Checks the position after funding payment and requested margin removal are reflected.

3. Reduces inconsistent enforcement by centralizing the margin-ratio check.

4. Evidence supports undercollateralized-position prevention, but not theft or a complete exploit trace.

# Evidence Notes

Grounded evidence is limited to `x/perp/v2/keeper/margin.go` and `x/perp/v2/keeper/clearing_house.go`. The heuristic baseline's RPC/query framing is unsupported and removed. The strongest supported claim is a missing or inconsistent liquidation-threshold margin-ratio check in perp margin and position-update flows. The evidence does not prove stolen funds, realized bad debt, or a full exploit path. Protocol security invariant: A perp position should not be allowed to remove margin or complete a position update when the resulting position margin ratio is below the liquidation threshold. Verification notes: The patch does not by itself prove that funds could be stolen. The patch does not show a completed insolvency or bad-debt exploit trace. The exact liquidation threshold formula and error behavior are inferred only from the provided snippets. No claim is made about RPC/query APIs despite heuristic baseline text mentioning them. No claim is made that all margin paths were previously unprotected; only the shown paths are mapped. Commit subject explicitly says the fix ensures margin is high enough when removing it. `RemoveMargin` changed ordering to check the updated position before `WithdrawFromVault`. `checkMarginRatio` is documented as checking whether the position margin ratio is below the liquidation threshold. No direct exploit proof or loss scenario is included in the provided input. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-margin-ratio-check`
Final impact type: `undercollateralized-position, economic-distortion`
Final confidence: `medium`
Final tags: `blockchain-core, perp, margin, collateral, liquidation-threshold, accounting-invariant`

The supplied patch evidence supports a security-relevant hardening case in the perp margin logic: margin removal and position update flows now validate the final position against a liquidation-threshold margin-ratio check before allowing withdrawal or continuing. This protects a financial protocol invariant, but the evidence does not prove a concrete exploit, loss, bad debt event, or externally demonstrated attack, so security-hardening is more conservative than security-fix.

## Security Evidence

1. RemoveMargin now applies funding and margin removal to the position before calling checkMarginRatio.
2. WithdrawFromVault occurs only after the updated position passes checkMarginRatio.
3. checkMarginRatio is documented as checking whether the position margin ratio is below the liquidation threshold.
4. Position update paths in clearing_house.go were changed to use the shared margin-ratio check.
5. The commit subject explicitly says the fix ensures margin is high enough when removing it.

## Missing Evidence

1. No exploit transaction or attacker walkthrough is provided.
2. No evidence shows realized bad debt, insolvency, or stolen funds.
3. The exact pre-patch failure condition is inferred from ordering and snippets, not demonstrated by a failing test in the supplied input.
4. The RPC-client-api framing is not supported by the provided patch evidence.

## Claim Boundaries

1. Validated only as perp margin/accounting invariant hardening.
2. Do not claim theft, fund loss, or full exploitability from this evidence alone.
3. Do not retain the rpc-client-api subsystem claim for corpus metadata.
4. Claims should be limited to margin removal and shown position-update paths.
