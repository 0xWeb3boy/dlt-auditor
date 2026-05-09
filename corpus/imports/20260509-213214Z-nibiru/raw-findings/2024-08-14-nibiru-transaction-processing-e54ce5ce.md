---
case_id: case_20240814_e54ce5ce
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
source_quality: high
date: 2024-08-14
source_refs:
  - git:e54ce5ce92c07ad7e2443acc534b2041d22d6b88
  - "x/evm/precompile/funtoken.go:151"
  - "x/evm/precompile/funtoken.go:178"
  - "x/evm/keeper/funtoken_from_coin_test.go:268"
  - "x/evm/keeper/erc20_test.go:5"
confidence: medium
tags:
  - transaction-processing
  - bridge-accounting
  - supply-accounting
  - funtoken
  - evm-precompile
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Likely security-relevant accounting fix in the EVM FunToken bridge. The ERC20-to-bank conversion path for bank-origin FunTokens no longer mints bank coins unconditionally; it burns the returned ERC20 representation before sending bank coins from the EVM module account.

## Observed Patch Facts

1. In `x/evm/precompile/funtoken.go`, the patch replaces `err = p.BankKeeper.MintCoins(ctx, evm.ModuleName, coins)` with `if funtoken.IsMadeFromCoin {`.

2. In `x/evm/precompile/funtoken.go`, the patch replaces `// If the FunToken mapping was created from a bank coin, then the EVM account` with `// TODO: UD-DEBUG: feat: Emit EVM events`.

3. In `x/evm/keeper/funtoken_from_coin_test.go`, the patch replaces `type FunTokenFromCoinSuite struct {` with `// TestConvertCoinToEvmAndBack executes sending fun tokens from bank coin to erc20 an...`.

4. In `x/evm/keeper/erc20_test.go`, the patch replaces `sdk "github.com/cosmos/cosmos-sdk/types"` with `func (s *Suite) TestERC20Calls() {`.

## Project Context

The changed code sits primarily in `x/evm/precompile`, `x/evm`, `x/evm/keeper`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/evm/keeper/funtoken_from_coin.go`, `x/evm/precompile/funtoken_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/precompile/funtoken_test.go`, `x/evm/keeper/statedb_test.go`. The strongest project-level identifiers around this patch are `bank`, `cosmos`, `tokens`, and `coin`. Nearby tests or test-like files include `x/evm/evmtest/evmante.go`, `x/evm/evmtest/erc20.go`.

## Before/After Behavior

Before the patch, `precompileFunToken.bankSend` transferred ERC20 tokens from the caller to the EVM module address, converted the amount to `sdk.Coins`, minted `funtoken.BankDenom` into the EVM module account, then sent bank coins from the module account to the recipient. The made-from-coin ERC20 burn occurred later. After the patch, the made-from-coin path burns the ERC20 held by `evm.EVM_MODULE_ADDRESS` before the bank transfer, and the unconditional bank mint is removed. The added regression test covers converting a bank coin to ERC20 and back, checking sender balance, ERC20 balance, and EVM module account balance.

# Root Cause

The reverse conversion path treated ERC20-to-bank conversion as a bank-coin mint even when the FunToken mapping was originally backed by a bank coin. For made-from-coin mappings, the evidence indicates bank-side value should come from existing module-held backing while the ERC20 representation is burned; minting bank coins in that path could make supply or module-account accounting diverge from the expected backing model.

## Walkthrough

1. A FunToken mapping exists for an ERC20 address and may be marked `IsMadeFromCoin`.

2. A caller invokes `bankSend` to convert ERC20 representation back to a Cosmos bank coin recipient.

3. The function transfers the caller's ERC20 amount to `evm.EVM_MODULE_ADDRESS`.

4. Before the patch, the function minted `funtoken.BankDenom` coins into the EVM module account for the conversion amount.

5. The function then sent bank coins from the EVM module account to the recipient.

6. For made-from-coin mappings, that meant reverse conversion minted bank coins instead of only releasing existing bank-side backing and retiring the ERC20 representation.

7. After the patch, the made-from-coin branch burns the ERC20 held by the EVM module address before sending bank coins from the module account.

8. The new test exercises bank coin to ERC20 and back and checks sender, ERC20, and EVM module account balances.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/precompile/funtoken.go | 151 | ERC20-to-bank FunToken conversion path; removed unconditional bank coin minting and added made-from-coin burn handling |
| x/evm/precompile/funtoken.go | 172 | bank coin transfer from EVM module account to recipient after conversion |
| x/evm/keeper/funtoken_from_coin_test.go | 268 | regression test for bank coin to ERC20 and back balance/accounting invariants |
| x/evm/keeper/erc20_test.go | 1 | test setup cleanup around bank-denom metadata for ERC20/FunToken tests |

## Code Snippets

## Snippet 1

Context: `x/evm/precompile/funtoken.go:151` (updates aggregate accounting or lifecycle state)

Before
```go
amt := math.NewIntFromBigInt(amount)
	coins := sdk.NewCoins(sdk.NewCoin(funtoken.BankDenom, amt))
	err = p.BankKeeper.MintCoins(ctx, evm.ModuleName, coins)
	if err != nil {
		return nil, fmt.Errorf("mint failed for module \"%s\" (%s): contract caller %s: %w",
			evm.ModuleName, evm.EVM_MODULE_ADDRESS.Hex(), caller.Hex(), err,
		)
	}
```
After
```go
amt := math.NewIntFromBigInt(amount)
	coins := sdk.NewCoins(sdk.NewCoin(funtoken.BankDenom, amt))
	if funtoken.IsMadeFromCoin {
		// If the FunToken mapping was created from a bank coin, then the EVM account
		// owns the ERC20 contract and was the original minter of the ERC20 tokens.
		// Since we're sending them away and want accurate total supply tracking, the
		// tokens need to be burned.
		_, err = p.EvmKeeper.ERC20().Burn(erc20, evm.EVM_MODULE_ADDRESS, amount, ctx)
```

## Snippet 2

Context: `x/evm/precompile/funtoken.go:178` (updates aggregate accounting or lifecycle state)

Before
```go
}

	// If the FunToken mapping was created from a bank coin, then the EVM account
	// owns the ERC20 contract and was the original minter of the ERC20 tokens.
	// Since we're sending them away and want accurate total supply tracking, the
	// tokens need to be burned.
	if funtoken.IsMadeFromCoin {
		_, err = p.EvmKeeper.ERC20().Burn(erc20, evm.EVM_MODULE_ADDRESS, amount, ctx)
```
After
```go
}

	// TODO: UD-DEBUG: feat: Emit EVM events
	// TODO: UD-DEBUG: feat: Emit ABCI events
```

## Snippet 3

Context: `x/evm/keeper/funtoken_from_coin_test.go:268` (updates aggregate accounting or lifecycle state)

Before
```go
}

type FunTokenFromCoinSuite struct {
	suite.Suite
```
After
```go
}

// TestConvertCoinToEvmAndBack executes sending fun tokens from bank coin to erc20 and then back to bank coin and checks the results:
// - sender balance
// - erc-20 balance
// - evm module account balance
func (s *FunTokenFromCoinSuite) TestConvertCoinToEvmAndBack() {
	for _, tc := range []struct {
```

## Snippet 4

Context: `x/evm/keeper/erc20_test.go:5` (updates aggregate accounting or lifecycle state)

Before
```go
"math/big"

	sdk "github.com/cosmos/cosmos-sdk/types"
	bankkeeper "github.com/cosmos/cosmos-sdk/x/bank/keeper"
	bank "github.com/cosmos/cosmos-sdk/x/bank/types"

	"github.com/NibiruChain/nibiru/v2/x/evm"
	"github.com/NibiruChain/nibiru/v2/x/evm/evmtest"
```
After
```go
"math/big"

	"github.com/NibiruChain/nibiru/v2/x/evm"
	"github.com/NibiruChain/nibiru/v2/x/evm/evmtest"
)

func (s *Suite) TestERC20Calls() {
	deps := evmtest.NewTestDeps()
```

# Fix Pattern

Branch conversion accounting by token origin: for bank-origin FunTokens, burn returned ERC20 representation and send existing module-held bank coins instead of minting bank coins during reverse conversion.

## How It Was Fixed

In `x/evm/precompile/funtoken.go`, the unconditional `BankKeeper.MintCoins` call was removed from `bankSend`. For `funtoken.IsMadeFromCoin`, the function now calls `p.EvmKeeper.ERC20().Burn(erc20, evm.EVM_MODULE_ADDRESS, amount, ctx)` before `SendCoinsFromModuleToAccount` and returns an `ERC20.Burn` error if burning fails. Tests in `x/evm/keeper/funtoken_from_coin_test.go` add a coin-to-EVM-and-back scenario that checks balances and module-account accounting.

# Why It Matters

1. The changed path moves value between ERC20 representation and Cosmos bank coins.

2. For bank-origin FunTokens, reverse conversion should conserve bank supply rather than mint new bank coins.

3. Module-account balances need to remain aligned with bridge backing assumptions.

4. The evidence supports accounting and supply-conservation risk, not authorization bypass, arbitrary theft, consensus failure, or chain halt.

# Evidence Notes

Primary evidence is the runtime change in `x/evm/precompile/funtoken.go`: removal of `BankKeeper.MintCoins`, addition of made-from-coin ERC20 burn handling before `SendCoinsFromModuleToAccount`, and removal of the later burn block. Supporting evidence is the added `TestConvertCoinToEvmAndBack`, described as checking sender balance, ERC20 balance, and EVM module account balance. Confidence is medium rather than high because the provided evidence establishes an accounting invariant violation but does not prove direct attacker profit or external withdrawability of any accumulated module-held bank coins. Protocol security invariant: For FunTokens created from a bank coin, converting between bank coins and ERC20 representation should conserve the underlying bank coin supply and keep the EVM module account aligned with the backing model. Returning ERC20 representation to bank form should retire the ERC20 and release existing module-held bank coins, not mint additional bank coins for the same value. Verification notes: The patch does not prove theft from arbitrary users. The patch does not show bypass of authorization or caller identity checks. The patch does not prove the inflated module-held bank coins were directly withdrawable outside the conversion path. The patch does not establish consensus failure or chain halt. The evidence supports accounting/supply conservation risk, not a generic EVM execution vulnerability. No evidence supports arbitrary-user theft. No evidence supports caller authorization bypass. No evidence establishes consensus failure or chain halt. Helper/test setup changes should be treated as support code, not root cause. The runtime precompile change is sufficient to classify this as likely security-relevant accounting work rather than mere cleanup. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final confidence: `medium`
Final tags: `transaction-processing, bridge-accounting, supply-accounting, funtoken, evm-precompile`

The patch clearly changes value-conversion accounting in a sensitive EVM/bank-token bridge path: bank-origin FunTokens no longer mint bank coins during ERC20-to-bank conversion, and instead burn the returned ERC20 representation before sending existing module-held bank coins. This supports retaining the case as security-relevant hardening around supply/accounting invariants. However, the supplied evidence does not prove direct attacker profit, unauthorized withdrawal, or a concrete exploit path, so security-fix is too strong.

## Security Evidence

1. Runtime code removes an unconditional BankKeeper.MintCoins call from the ERC20-to-bank conversion path.
2. The new branch applies only when funtoken.IsMadeFromCoin, indicating token-origin-specific supply handling.
3. The replacement behavior burns ERC20 held by the EVM module address before bank coins are sent out.
4. Added regression coverage checks coin-to-EVM-and-back balances, ERC20 balance, and EVM module account balance.

## Missing Evidence

1. No evidence that inflated module-held bank coins were directly withdrawable by an attacker.
2. No exploit scenario showing a user gaining spendable funds beyond their original balance.
3. No advisory, commit body, or explicit security label identifying this as a vulnerability fix.
4. No evidence of authorization bypass, arbitrary theft, consensus failure, or chain halt.

## Claim Boundaries

1. This supports a bridge/supply-accounting invariant issue, not a generic EVM vulnerability.
2. The strongest supported impact is economic or state-accounting distortion.
3. Treat helper and test changes as supporting evidence only; the runtime precompile change is the root evidence.
4. Classify as security-hardening rather than confirmed security-fix because exploitability is not proven from the patch alone.
