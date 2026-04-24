---
case_id: case_20221115_d9d950ab7
project: sei-chain
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: access-control
bug_class: access-control
impact_type:
  - privilege-misuse
source_quality: medium
date: 2022-11-15
source_refs:
  - git:d9d950ab7ad8792b8d0cbc2c26f9a79f133d85f8
  - "x/dex/keeper/msgserver/msg_server_register_contract.go:22"
  - "x/dex/keeper/msgserver/msg_server_contract_deposit_rent_test.go:96"
  - "x/dex/keeper/msgserver/msg_server_update_tick_size_test.go:191"
  - "x/dex/keeper/msgserver/msg_server_register_pairs_test.go:203"
confidence: medium
tags:
  - blockchain-core
  - access-control
  - authorization-check
  - contract-registration
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a direct authorization gate to RegisterContract. The code now fetches wasm contract metadata for msg.Contract.ContractAddr and rejects the request with sdkerrors.ErrUnauthorized when contractInfo.Creator does not match msg.Creator. This supports a grounded missing-authorization finding for the DEX contract registration path.

## Observed Patch Facts

1. In `x/dex/keeper/msgserver/msg_server_register_contract.go`, the patch replaces `if err := k.ValidateUniqueDependencies(msg); err != nil {` with `// Validation such that only the user who instantiated the contract can register cont...`.

2. In `x/dex/keeper/msgserver/msg_server_contract_deposit_rent_test.go`, the patch replaces `_, err = keeper.GetContract(ctx, TestContractA)` with `_, err = dexkeeper.GetContract(ctx, TestContractA)`.

3. In `x/dex/keeper/msgserver/msg_server_update_tick_size_test.go`, the patch replaces `keeper, ctx := keepertest.DexKeeper(t)` with `// Instantiate and get contract address`.

4. In `x/dex/keeper/msgserver/msg_server_register_pairs_test.go`, the patch replaces `keeper, ctx := keepertest.DexKeeper(t)` with `testApp := keepertest.TestApp()`.

## Project Context

The changed code sits primarily in `x/dex/keeper/msgserver`, `x/dex/keeper`, which anchors the finding in the `access-control` area of the project. Historical context from `x/dex/keeper/msgserver/msg_server_register_contract_test.go`, `x/dex/keeper/msgserver/msg_server_unregister_contract_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/dex/keeper/msgserver/msg_server_register_contract_test.go`, `x/dex/keeper/msgserver/msg_server_unregister_contract_test.go`. The strongest project-level identifiers around this patch are `testApp`, `keeper`, `contract`, and `require`. Nearby tests or test-like files include `x/dex/keeper/msgserver/msg_server_place_orders_fuzz_test.go`.

## Before/After Behavior

Before the patch, the shown RegisterContract flow ran ValidateBasics and then proceeded toward registration-specific validation without any supplied evidence of a check tying msg.Creator to the wasm contract metadata for msg.Contract.ContractAddr. After the patch, RegisterContract parses the contract address, calls WasmKeeper.GetContractInfo, and returns sdkerrors.ErrUnauthorized if contractInfo.Creator != msg.Creator. Related tests were updated to use full app and wasm instantiation fixtures so creator metadata exists for the checked path.

# Root Cause

RegisterContract trusted the registration request without verifying, in the observed code path, that the caller was the wasm-recorded creator of the contract being registered.

## Walkthrough

1. RegisterContract unwraps the SDK context and validates basic message structure.

2. The pre-patch evidence shows the function moving from basic validation into dependency validation, with no supplied creator authorization check in between.

3. The patch inserts a check immediately after ValidateBasics.

4. The new code converts msg.Contract.ContractAddr to an SDK account address and loads contractInfo from WasmKeeper.

5. If contractInfo.Creator differs from msg.Creator, the function returns sdkerrors.ErrUnauthorized.

6. Test fixture changes instantiate wasm contracts through the test app so the creator relationship used by the new check is represented.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/dex/keeper/msgserver/msg_server_register_contract.go | 22 | Adds the creator-vs-contractInfo.Creator authorization gate before contract registration proceeds. |
| x/dex/keeper/msgserver/msg_server_contract_deposit_rent_test.go | 47 | Updates registration/rent test setup to instantiate a wasm contract under the registering account. |
| x/dex/keeper/msgserver/msg_server_register_pairs_test.go | 197 | Updates creator-sensitive register-pairs test setup to use the full app/wasm path. |
| x/dex/keeper/msgserver/msg_server_update_tick_size_test.go | 185 | Updates creator-sensitive tick-size test setup to use the full app/wasm path. |

## Code Snippets

## Snippet 1

Context: `x/dex/keeper/msgserver/msg_server_register_contract.go:22` (changes a sensitive control or state-update path)

Before
```go
return &types.MsgRegisterContractResponse{}, err
	}
	if err := k.ValidateUniqueDependencies(msg); err != nil {
		ctx.Logger().Error(fmt.Sprintf("dependencies of contract %s are not unique", msg.Contract.ContractAddr))
```
After
```go
return &types.MsgRegisterContractResponse{}, err
	}

	// Validation such that only the user who instantiated the contract can register contract
	contractAddr, _ := sdk.AccAddressFromBech32(msg.Contract.ContractAddr)
	contractInfo := k.Keeper.WasmKeeper.GetContractInfo(ctx, contractAddr)

	// TODO: Add wasm fixture to write unit tests to verify this behavior
```

## Snippet 2

Context: `x/dex/keeper/msgserver/msg_server_contract_deposit_rent_test.go:96` (changes persisted or aggregate state handling)

Before
```go
})
	require.NoError(t, err)
	_, err = keeper.GetContract(ctx, TestContractA)
	require.NoError(t, err)
	balance = keeper.BankKeeper.GetBalance(ctx, testAccount, "usei")
	require.Equal(t, int64(8000000), balance.Amount.Int64())
}
```
After
```go
})
	require.NoError(t, err)
	_, err = dexkeeper.GetContract(ctx, TestContractA)
	require.NoError(t, err)
	balance = dexkeeper.BankKeeper.GetBalance(ctx, testAccount, "usei")
	require.Equal(t, int64(7900000), balance.Amount.Int64())
}
```

## Snippet 3

Context: `x/dex/keeper/msgserver/msg_server_update_tick_size_test.go:191` (changes a sensitive control or state-update path)

Before
```go
// Test only contract creator can update tick size for contract
func TestInvalidUpdateTickSizeCreator(t *testing.T) {
	keeper, ctx := keepertest.DexKeeper(t)
	wctx := sdk.WrapSDKContext(ctx)
	server := msgserver.NewMsgServerImpl(*keeper)
	err := RegisterContractUtil(server, wctx, TestContractA, nil)
	require.NoError(t, err)
```
After
```go
// Test only contract creator can update tick size for contract
func TestInvalidUpdateTickSizeCreator(t *testing.T) {
	// Instantiate and get contract address
	testApp := keepertest.TestApp()
	ctx := testApp.BaseApp.NewContext(false, tmproto.Header{Time: time.Now()})
	ctx = ctx.WithContext(context.WithValue(ctx.Context(), dexutils.DexMemStateContextKey, dexcache.NewMemState(testApp.GetKey(types.StoreKey))))
	wctx := sdk.WrapSDKContext(ctx)
	keeper := testApp.DexKeeper
```

## Snippet 4

Context: `x/dex/keeper/msgserver/msg_server_register_pairs_test.go:203` (changes a sensitive control or state-update path)

Before
```go
// Test only contract creator can update registered pairs for contract
func TestInvalidRegisterPairCreator(t *testing.T) {
	keeper, ctx := keepertest.DexKeeper(t)
	wctx := sdk.WrapSDKContext(ctx)
	server := msgserver.NewMsgServerImpl(*keeper)
	err := RegisterContractUtil(server, wctx, TestContractA, nil)
	require.NoError(t, err)
```
After
```go
// Test only contract creator can update registered pairs for contract
func TestInvalidRegisterPairCreator(t *testing.T) {
	testApp := keepertest.TestApp()
	ctx := testApp.BaseApp.NewContext(false, tmproto.Header{Time: time.Now()})
	ctx = ctx.WithContext(context.WithValue(ctx.Context(), dexutils.DexMemStateContextKey, dexcache.NewMemState(testApp.GetKey(types.StoreKey))))
	wctx := sdk.WrapSDKContext(ctx)
	keeper := testApp.DexKeeper
```

# Fix Pattern

Authorize state-changing registration against canonical ownership metadata from the wasm subsystem before accepting DEX registration state.

## How It Was Fixed

The implementation now derives the authorized creator from WasmKeeper.GetContractInfo(ctx, contractAddr).Creator and compares it to msg.Creator in RegisterContract. Mismatches are rejected before the rest of registration proceeds. Tests were adjusted to create real wasm contract metadata for paths affected by the new validation.

# Why It Matters

1. Prevents a non-creator from registering a wasm contract into the DEX through this message path.

2. Bases authorization on wasm module state rather than caller-supplied registration data.

3. Keeps the finding limited to unauthorized registration; the supplied evidence does not prove theft, fund loss, or order manipulation.

# Evidence Notes

The strongest evidence is the added ErrUnauthorized branch in x/dex/keeper/msgserver/msg_server_register_contract.go. Test changes support the new creator-metadata dependency but are mostly fixture updates. The evidence establishes the authorization invariant for RegisterContract only; it does not establish broader compromise or coverage of all contract-management entry points. Protocol security invariant: A DEX contract registration request must be authorized by the account recorded in the wasm module metadata as the Creator for msg.Contract.ContractAddr before DEX registration state is accepted. Verification notes: The patch does not prove theft, fund loss, or order manipulation by itself. The evidence does not show whether unregistered arbitrary contracts could execute privileged DEX behavior before registration. The patch only demonstrates the RegisterContract authorization invariant, not all contract-management entry points. The tests are mostly fixture updates and do not independently prove exploitability. Direct code evidence shows a new creator check in RegisterContract. Commit message and tests are consistent with an authorization fix. No supplied evidence demonstrates concrete exploitation beyond unauthorized registration being possible before the added check. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final confidence: `medium`
Final tags: `blockchain-core, access-control, authorization-check, contract-registration`

The supplied patch clearly adds an authorization gate to the DEX contract registration path by comparing the wasm contract's recorded Creator against msg.Creator and returning ErrUnauthorized on mismatch. That is security-relevant and suitable for a security corpus, but the evidence is stronger as hardening than as a fully proven exploitable security fix because the provided before-context does not show the entire pre-existing validation path or demonstrate a concrete exploit impact beyond unauthorized registration being newly rejected.

## Security Evidence

1. RegisterContract now fetches wasm contract metadata with WasmKeeper.GetContractInfo for msg.Contract.ContractAddr.
2. The new code rejects registration when contractInfo.Creator != msg.Creator using sdkerrors.ErrUnauthorized.
3. The inserted comment states the intended invariant: only the user who instantiated the contract can register it.
4. Tests were updated to use wasm instantiation fixtures so creator metadata exists for registration-related paths.

## Missing Evidence

1. No full pre-patch RegisterContract implementation is supplied to rule out equivalent authorization elsewhere in the function.
2. No test evidence is shown where a non-creator registration previously succeeded and now fails.
3. No concrete downstream exploit, fund loss, order manipulation, or privilege escalation beyond unauthorized registration is demonstrated.
4. The impact of registering another creator's contract into the DEX is not fully established from the provided evidence.

## Claim Boundaries

1. Supports an authorization hardening finding for RegisterContract only.
2. Does not prove broader compromise of all DEX contract-management entry points.
3. Does not support claims of theft, direct fund loss, or market manipulation.
4. Confidence should be medium rather than high because exploitability and prior absence of all equivalent checks are not fully proven.
