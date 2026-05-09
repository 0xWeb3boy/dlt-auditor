---
case_id: case_20241228_1a256f2a
project: nibiru
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2024-12-28
source_refs:
  - git:1a256f2a24cdfe0998787c68c2cf01fb47ce90a1
  - "x/evm/keeper/erc20.go:28"
  - "x/evm/keeper/funtoken_from_erc20_test.go:386"
  - "x/evm/keeper/erc20.go:70"
  - "x/evm/keeper/erc20.go:151"
bug_class: recursive-gas-forwarding
impact_type:
  - resource-exhaustion
tags:
  - infrastructure
  - transaction-processing
  - evm
  - erc20
  - funtoken
  - gas-forwarding
  - recursion
  - resource-exhaustion
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a security-relevant recursion/gas-forwarding issue in the EVM FunToken/ERC20 integration. ERC20 mint and burn calls previously passed the fixed Erc20GasLimitExecute value directly to CallContract. The fix computes forwarded gas from ctx.GasMeter().GasRemaining(), subtracts floor(remaining/64), and caps it by the configured limit. Added test coverage uses a malicious recursive ERC20 contract, supporting the conclusion that the change targets recursive ERC20/precompile call behavior. The evidence does not establish theft, state corruption, privilege escalation, consensus failure, or a complete externally triggerable exploit sequence.

## Observed Patch Facts

1. In `x/evm/keeper/erc20.go`, the patch replaces `// ERC20 returns a mutable reference to the keeper with an ERC20 contract ABI and` with `// getCallGas returns the gas limit for a call to an ERC20 contract following 63/64 r...`.

2. In `x/evm/keeper/funtoken_from_erc20_test.go`, the patch replaces `type FunTokenFromErc20Suite struct {` with `// TestFunTokenInfiniteRecursionERC20 creates a funtoken from a contract`.

3. In `x/evm/keeper/erc20.go`, the patch replaces `return e.CallContract(ctx, e.ABI, from, &contract, true, Erc20GasLimitExecute, "mint"...` with `return e.CallContract(ctx, e.ABI, from, &contract, true, getCallGasWithLimit(ctx, Erc...`.

4. In `x/evm/keeper/erc20.go`, the patch replaces `return e.CallContract(ctx, e.ABI, from, &contract, true, Erc20GasLimitExecute, "burn"...` with `return e.CallContract(ctx, e.ABI, from, &contract, true, getCallGasWithLimit(ctx, Erc...`.

## Project Context

The changed code sits primarily in `x/evm/keeper`, `x/evm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/evm/keeper/funtoken_from_coin_test.go`, `x/evm/keeper/call_contract.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/keeper/msg_server.go`, `x/evm/statedb/journal_test.go`. The strongest project-level identifiers around this patch are `contract`, `from`, `CallContract`, and `Erc20GasLimitExecute`. Nearby tests or test-like files include `x/evm/evmtest/tx.go`, `x/evm/evmtest/smart_contract.go`.

## Before/After Behavior

Before the patch, ERC20 Mint and Burn forwarded the fixed Erc20GasLimitExecute gas limit to CallContract. After the patch, both paths call getCallGasWithLimit(ctx, Erc20GasLimitExecute), which derives the forwarded amount from remaining SDK gas minus floor(remaining/64), capped at the configured limit. A new regression test covers a FunToken-from-ERC20 scenario involving malicious recursive balanceOf() and transfer() behavior.

# Root Cause

The supported root cause is fixed gas forwarding at ERC20 contract-call boundaries. In recursive ERC20 -> precompile -> ERC20 patterns, using a fixed per-call allowance could fail to shrink forwarded gas according to the remaining transaction gas budget. The provided evidence supports a recursion gas-control bug, not an accounting/state-drift bug.

## Walkthrough

1. FunToken-from-ERC20 flows can invoke ERC20 contract methods through keeper CallContract helpers.

2. Before the fix, ERC20 Mint passed Erc20GasLimitExecute directly to CallContract.

3. Before the fix, ERC20 Burn also passed Erc20GasLimitExecute directly to CallContract.

4. The patch adds getCallGasWithLimit, which reads remaining SDK gas and subtracts floor(remaining/64).

5. The helper returns the smaller of the reduced remaining-gas value and the configured gas limit.

6. Mint and Burn now use this helper when calling ERC20 contracts.

7. The added test coverage describes a malicious ERC20 with recursive balanceOf() and transfer() behavior.

8. The code comment explicitly frames the helper as protection against recursive ERC20 -> precompile -> ERC20 calls.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/keeper/erc20.go | 28 | Introduces EIP-150-style gas forwarding helper that reduces available gas for nested ERC20 contract calls. |
| x/evm/keeper/erc20.go | 70 | Applies bounded remaining-gas forwarding to ERC20 mint calls made through CallContract. |
| x/evm/keeper/erc20.go | 151 | Applies bounded remaining-gas forwarding to ERC20 burn calls made through CallContract. |
| x/evm/keeper/funtoken_from_erc20_test.go | 386 | Adds regression coverage using a malicious recursive ERC20 in the FunToken-from-ERC20 flow. |
| x/evm/embeds/contracts/TestInfiniteRecursionERC20.sol | 1 | Provides malicious recursive ERC20 test contract used to exercise the recursion path. |

## Code Snippets

## Snippet 1

Context: `x/evm/keeper/erc20.go:28` (updates aggregate accounting or lifecycle state)

Before
```go
)

// ERC20 returns a mutable reference to the keeper with an ERC20 contract ABI and
// Go functions corresponding to contract calls in the ERC20 standard like "mint"
```
After
```go
)

// getCallGas returns the gas limit for a call to an ERC20 contract following 63/64 rule (EIP-150)
// protection against recursive calls ERC20 -> precompile -> ERC20.
func getCallGasWithLimit(ctx sdk.Context, gasLimit uint64) uint64 {
	availableGas := ctx.GasMeter().GasRemaining()
	callGas := availableGas - uint64(math.Floor(float64(availableGas)/64))
	return min(callGas, gasLimit)
```

## Snippet 2

Context: `x/evm/keeper/funtoken_from_erc20_test.go:386` (updates aggregate accounting or lifecycle state)

Before
```go
}

type FunTokenFromErc20Suite struct {
	suite.Suite
```
After
```go
}

// TestFunTokenInfiniteRecursionERC20 creates a funtoken from a contract
// with a malicious recursive balanceOf() and transfer() functions.
func (s *FunTokenFromErc20Suite) TestFunTokenInfiniteRecursionERC20() {
	deps := evmtest.NewTestDeps()

	s.T().Log("Deploy InfiniteRecursionERC20")
```

## Snippet 3

Context: `x/evm/keeper/erc20.go:70` (updates aggregate accounting or lifecycle state)

Before
```go
ctx sdk.Context,
) (evmResp *evm.MsgEthereumTxResponse, err error) {
	return e.CallContract(ctx, e.ABI, from, &contract, true, Erc20GasLimitExecute, "mint", to, amount)
}
```
After
```go
ctx sdk.Context,
) (evmResp *evm.MsgEthereumTxResponse, err error) {
	return e.CallContract(ctx, e.ABI, from, &contract, true, getCallGasWithLimit(ctx, Erc20GasLimitExecute), "mint", to, amount)
}
```

## Snippet 4

Context: `x/evm/keeper/erc20.go:151` (updates aggregate accounting or lifecycle state)

Before
```go
ctx sdk.Context,
) (evmResp *evm.MsgEthereumTxResponse, err error) {
	return e.CallContract(ctx, e.ABI, from, &contract, true, Erc20GasLimitExecute, "burn", amount)
}
```
After
```go
ctx sdk.Context,
) (evmResp *evm.MsgEthereumTxResponse, err error) {
	return e.CallContract(ctx, e.ABI, from, &contract, true, getCallGasWithLimit(ctx, Erc20GasLimitExecute), "burn", amount)
}
```

# Fix Pattern

Replace fixed gas forwarding at recursive contract-call boundaries with remaining-gas-based forwarding, preserving the configured cap while applying a 63/64-style reduction.

## How It Was Fixed

The patch introduced getCallGasWithLimit(ctx, gasLimit) in x/evm/keeper/erc20.go and changed ERC20 Mint and Burn to pass its result into CallContract instead of Erc20GasLimitExecute directly. It also added a malicious recursive ERC20 test contract/artifact and a FunToken-from-ERC20 regression test.

# Why It Matters

1. Constrains recursive ERC20/precompile call paths to remaining transaction gas.

2. Avoids refreshing the same fixed ERC20 execution gas limit on nested calls.

3. Documents the malicious recursive ERC20 scenario in regression coverage.

4. Impact beyond gas exhaustion or recursion control is not established by the provided evidence.

# Evidence Notes

Primary evidence is commit 1a256f2a dated 2024-12-28. x/evm/keeper/erc20.go adds getCallGasWithLimit with a comment naming EIP-150 and protection against recursive ERC20 -> precompile -> ERC20 calls. The Mint and Burn helpers are changed to use getCallGasWithLimit(ctx, Erc20GasLimitExecute). x/evm/keeper/funtoken_from_erc20_test.go adds TestFunTokenInfiniteRecursionERC20 for a malicious recursive ERC20 with balanceOf() and transfer() behavior. Helper test files and embedded artifacts support the regression scenario but are not themselves the root cause. The exact external transaction path and concrete network-level impact are not fully shown, so confirmed severity claims would be unsupported. Protocol security invariant: Keeper-mediated ERC20 calls used by FunToken flows should not grant a fresh fixed execution gas allowance on recursive ERC20 -> precompile -> ERC20 paths; forwarded call gas should be bounded by the transaction's remaining gas budget using the 63/64-style reduction shown in the patch. Verification notes: The patch does not prove fund theft or balance corruption. The patch does not prove consensus failure or chain halt. The evidence shows recursion gas exhaustion risk, not privilege escalation. Only the shown ERC20/FunToken call paths are supported by the provided evidence. The exact externally triggerable transaction sequence is not fully shown in the patch excerpts. Downgraded confidence from high to medium because the exploit path and impact are only partially shown. Rejected the heuristic baseline's accounting-or-state-drift classification as unsupported. Kept the finding as likely security because code comments, commit message, and malicious-recursion regression test all point to a protective fix. Did not claim fund theft, balance corruption, privilege escalation, consensus failure, or chain halt. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `recursive-gas-forwarding`
Final impact type: `resource-exhaustion`
Final tags: `infrastructure, transaction-processing, evm, erc20, funtoken, gas-forwarding, recursion, resource-exhaustion`

The patch evidence supports retaining this as security hardening, not a confidently proven security fix. The code adds an EIP-150-style 63/64 gas forwarding helper specifically documented as protection against recursive ERC20 -> precompile -> ERC20 calls, applies it to ERC20 mint and burn contract calls, and adds a malicious infinite-recursion ERC20 regression test. However, the evidence does not prove a concrete exploit outcome such as theft, state drift, economic distortion, consensus failure, or externally demonstrated denial of service, so the original accounting/state-drift framing is too strong.

## Security Evidence

1. Commit subject and body explicitly mention fixing infinite recursion in ERC20 funtoken contracts.
2. New helper limits forwarded call gas based on remaining transaction gas and references EIP-150.
3. Inline comment states the helper protects against recursive ERC20 -> precompile -> ERC20 calls.
4. Mint and Burn changed from fixed Erc20GasLimitExecute forwarding to getCallGasWithLimit.
5. Regression test uses a malicious recursive ERC20 with balanceOf and transfer behavior.

## Missing Evidence

1. No complete externally triggerable exploit sequence is shown.
2. No demonstrated fund loss, unauthorized state mutation, or accounting drift is shown.
3. No concrete chain halt, consensus failure, or network-level denial of service impact is proven.
4. No before/after test result excerpt proves the old behavior caused an exploitable security failure.

## Claim Boundaries

1. Supported claim: recursive ERC20/FunToken call paths are hardened by remaining-gas-based forwarding.
2. Supported claim: the previous fixed gas forwarding could preserve too much gas across recursive contract/precompile boundaries.
3. Unsupported claim: this caused state-accounting drift or economic distortion.
4. Unsupported claim: this is a confirmed exploitable vulnerability with a demonstrated attacker impact.
