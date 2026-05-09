---
case_id: case_20250108_20531e7d
project: nibiru
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: accounting-or-state-drift
impact_type:
  - state-accounting
  - economic-distortion
confidence: medium
source_quality: high
date: 2025-01-08
source_refs:
  - git:20531e7dae87a3e3f73500325caec51f75958beb
  - "x/evm/keeper/funtoken_from_erc20_test.go:453"
  - "x/evm/keeper/msg_server.go:626"
  - "x/evm/keeper/msg_server.go:611"
  - "x/evm/const.go:86"
tags:
  - infrastructure
  - transaction-processing
  - accounting-or-state-drift
  - state-accounting
  - economic-distortion
  - evm
  - erc20
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a security-relevant accounting invariant bug in the ERC20-born FunToken conversion path. Before the patch, the bank burn amount was derived from `actualSentAmount` returned by the ERC20 transfer. For a fee-charging ERC20, that value could be lower than the input bank `coin`, causing the conversion path to burn less bank supply than it had accepted. After the patch, `convertCoinToEvmBornERC20` ignores the ERC20 transfer result amount and burns the full input `coin`. The added regression test explicitly covers a malicious ERC20 charging a 10% transfer fee and verifies that all bank coins are burned after conversion.

## Observed Patch Facts

1. In `x/evm/keeper/funtoken_from_erc20_test.go`, the patch replaces `type FunTokenFromErc20Suite struct {` with `// TestSendERC20WithFee creates a funtoken from a malicious contract which charges a...`.

2. In `x/evm/keeper/msg_server.go`, the patch replaces `burnCoin := sdk.NewCoin(coin.Denom, sdk.NewIntFromBigInt(actualSentAmount))` with `err = k.Bank.BurnCoins(ctx, evm.ModuleName, sdk.NewCoins(coin))`.

3. In `x/evm/keeper/msg_server.go`, the patch replaces `actualSentAmount, _, err := k.ERC20().Transfer(` with `_, _, err := k.ERC20().Transfer(`.

4. In `x/evm/const.go`, the patch replaces `EVM_MODULE_ADDRESS = gethcommon.BytesToAddress(authtypes.NewModuleAddress(ModuleName))` with `var EVM_MODULE_ADDRESS_NIBI sdk.AccAddress`.

## Project Context

The changed code sits primarily in `x/evm/keeper`, `x/evm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/evm/keeper/funtoken_from_coin_test.go`, `x/evm/keeper/statedb.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/keeper/statedb.go`, `x/evm/keeper/grpc_query_test.go`. The strongest project-level identifiers around this patch are `coins`, `ModuleName`, `coin`, and `gethcommon`. Nearby tests or test-like files include `x/evm/evmtest/tx_test.go`, `x/evm/evmtest/evmante.go`.

## Before/After Behavior

Before the patch, `convertCoinToEvmBornERC20` moved the full requested bank `coin` into the EVM module account, transferred ERC20 using `coin.Amount.BigInt()`, captured `actualSentAmount`, and burned only `sdk.NewCoin(coin.Denom, sdk.NewIntFromBigInt(actualSentAmount))`. After the patch, the transfer result amount is discarded and the function burns `sdk.NewCoins(coin)`, matching the full bank-coin input.

# Root Cause

The bank-coin burn amount was coupled to the ERC20 transfer's observed received amount instead of the bank-coin amount accepted into the module for conversion. Fee-on-transfer ERC20 behavior can reduce the observed transfer amount, so the old burn calculation could under-burn the bank representation.

## Walkthrough

1. An ERC20-born FunToken can be represented as ERC20 tokens and as bank coins through the conversion path.

2. During bank-coin-to-ERC20 conversion, the function sends the caller's full bank `coin` amount into the EVM module account.

3. The function then requests an ERC20 transfer from the EVM module address to the recipient for `coin.Amount.BigInt()`.

4. Before the fix, it used `actualSentAmount` from that ERC20 transfer to decide how many bank coins to burn.

5. For a fee-charging ERC20, `actualSentAmount` can be lower than the requested amount.

6. That means the old code could burn fewer bank coins than were accepted into the module for conversion.

7. The patch burns the original `coin` amount instead, preserving the intended accounting for the bank side.

8. The new test uses a malicious fee-charging ERC20 contract and checks that all bank coins are burned after round-trip conversion.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/keeper/msg_server.go | 586 | coin-to-ERC20 conversion path for ERC20-born FunTokens |
| x/evm/keeper/msg_server.go | 611 | ERC20 transfer no longer supplies the burn amount via `actualSentAmount` |
| x/evm/keeper/msg_server.go | 626 | burns the full bank coin input from the module account to preserve supply accounting |
| x/evm/keeper/funtoken_from_erc20_test.go | 453 | regression test using a fee-charging ERC20 contract to verify all bank coins are burned |
| x/evm/const.go | 86 | exposes the EVM module account address in SDK address form, likely supporting module balance/accounting checks |

## Code Snippets

## Snippet 1

Context: `x/evm/keeper/funtoken_from_erc20_test.go:453` (updates aggregate accounting or lifecycle state)

Before
```go
}

type FunTokenFromErc20Suite struct {
	suite.Suite
```
After
```go
}

// TestSendERC20WithFee creates a funtoken from a malicious contract which charges a 10% fee on any transfer.
// Test ensures that after sending ERC20 token to coin and back, all bank coins are burned.
func (s *FunTokenFromErc20Suite) TestSendERC20WithFee() {
	deps := evmtest.NewTestDeps()

	s.T().Log("Deploy ERC20")
```

## Snippet 2

Context: `x/evm/keeper/msg_server.go:626` (updates aggregate accounting or lifecycle state)

Before
```go
// on the sum of the FunToken's bank and ERC20 supply, we burn the coins here
	// in the BC → ERC20 conversion.
	burnCoin := sdk.NewCoin(coin.Denom, sdk.NewIntFromBigInt(actualSentAmount))
	err = k.Bank.BurnCoins(ctx, evm.ModuleName, sdk.NewCoins(burnCoin))
	if err != nil {
		return nil, errors.Wrap(err, "failed to burn coins")
```
After
```go
// on the sum of the FunToken's bank and ERC20 supply, we burn the coins here
	// in the BC → ERC20 conversion.
	err = k.Bank.BurnCoins(ctx, evm.ModuleName, sdk.NewCoins(coin))
	if err != nil {
		return nil, errors.Wrap(err, "failed to burn coins")
```

## Snippet 3

Context: `x/evm/keeper/msg_server.go:611` (updates aggregate accounting or lifecycle state)

Before
```go
// inside the EVM module account in order to convert the coins back to
	// ERC20s.
	actualSentAmount, _, err := k.ERC20().Transfer(
		erc20Addr,
		evm.EVM_MODULE_ADDRESS,
```
After
```go
// inside the EVM module account in order to convert the coins back to
	// ERC20s.
	_, _, err := k.ERC20().Transfer(
		erc20Addr,
		evm.EVM_MODULE_ADDRESS,
```

## Snippet 4

Context: `x/evm/const.go:86` (updates aggregate accounting or lifecycle state)

Before
```go
var EVM_MODULE_ADDRESS gethcommon.Address

func init() {
	EVM_MODULE_ADDRESS = gethcommon.BytesToAddress(authtypes.NewModuleAddress(ModuleName))
}
```
After
```go
var EVM_MODULE_ADDRESS gethcommon.Address
var EVM_MODULE_ADDRESS_NIBI sdk.AccAddress

func init() {
	EVM_MODULE_ADDRESS_NIBI = authtypes.NewModuleAddress(ModuleName)
	EVM_MODULE_ADDRESS = gethcommon.BytesToAddress(EVM_MODULE_ADDRESS_NIBI)
}
```

# Fix Pattern

Use the amount accepted at the conversion/accounting boundary for supply reconciliation, not a downstream transfer result that token behavior can reduce.

## How It Was Fixed

In `x/evm/keeper/msg_server.go`, the patch removes the `burnCoin` derived from `actualSentAmount` and replaces the burn call with `k.Bank.BurnCoins(ctx, evm.ModuleName, sdk.NewCoins(coin))`. In tests, it adds a fee-charging ERC20 scenario that verifies the module burns all bank coins after conversion. The added SDK-form module address appears to support balance/accounting checks, but it is support code rather than the root cause.

# Why It Matters

1. Preserves FunToken bank/ERC20 accounting consistency.

2. Prevents fee-on-transfer behavior from reducing the bank burn amount.

3. Avoids unburned bank coins remaining after conversion.

4. Security impact beyond the accounting invariant is not proven by the provided evidence.

# Evidence Notes

The strongest evidence is the runtime diff in `x/evm/keeper/msg_server.go`, where the burn changes from `actualSentAmount`-derived `burnCoin` to the full input `coin`. The test comment in `x/evm/keeper/funtoken_from_erc20_test.go` states that the new test creates a malicious ERC20 charging a 10% transfer fee and ensures all bank coins are burned. The evidence does not prove that leftover module bank coins were withdrawable, does not prove privilege escalation, and does not establish impact for standard non-fee ERC20s. Protocol security invariant: For an ERC20-born FunToken, converting bank coins back into ERC20 must burn the full bank-coin amount accepted into the EVM module for conversion so the bank-coin representation remains reconciled with the ERC20 representation, including when the ERC20 transfer has fee-on-transfer behavior. Verification notes: The patch does not prove an attacker can withdraw the unburned bank coins from the module account. The patch does not prove chain-wide inflation beyond the shown FunToken accounting mismatch. The patch does not show unauthorized access control bypass or privilege escalation. The patch does not establish impact for standard ERC20 tokens without transfer fees. The exact economic exploitability depends on surrounding module-account and token-conversion rules not fully shown in the provided evidence. Runtime fix is directly shown in the conversion function diff. Regression test is directly tied to fee-on-transfer ERC20 behavior. Exploitability and economic impact are bounded to the shown accounting mismatch because surrounding withdrawal rules are not provided. Confidence is medium rather than high because the invariant violation is clear but the attack path is not fully established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final tags: `infrastructure, transaction-processing, accounting-or-state-drift, state-accounting, economic-distortion, evm, erc20`

The supplied patch supports keeping this as security-relevant hardening, but not confidently as a proven security fix. The conversion path previously burned bank coins based on the ERC20 transfer result amount, and the new regression test explicitly models a malicious fee-charging ERC20 where that amount can be reduced. Burning the original input coin clearly tightens a supply/accounting invariant in a transaction-processing path. However, the evidence does not prove a concrete exploit path, withdrawability of leftover module coins, or chain-wide inflation impact, so security-hardening is the conservative classification.

## Security Evidence

1. Runtime code now burns the full input bank coin instead of a transfer-result-derived amount.
2. The removed `actualSentAmount` dependency mattered for fee-on-transfer ERC20 behavior.
3. The added test describes a malicious ERC20 charging a 10% transfer fee.
4. The test objective is to ensure all bank coins are burned after ERC20-to-coin-to-ERC20 conversion.
5. The touched path is a token conversion flow that preserves bank/ERC20 supply accounting.

## Missing Evidence

1. No evidence shows the unburned bank coins were withdrawable by an attacker.
2. No full exploit sequence is provided.
3. No evidence proves chain-wide inflation or direct loss of funds.
4. No evidence establishes impact for standard ERC20s without transfer fees.
5. No access-control or privilege-bypass issue is shown.

## Claim Boundaries

1. Classify as security-hardening rather than confirmed security-fix.
2. Limit impact to FunToken bank/ERC20 accounting invariant protection.
3. Do not claim proven theft, privilege escalation, or full inflation exploit.
4. Do not rely on the unrelated SDK-form module address change as root-cause evidence.
5. The unsupported `rpc` tag should not be retained.
