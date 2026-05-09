---
case_id: case_20260427_224de766
project: nibiru
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: access-control
impact_type:
  - privilege-misuse
confidence: medium
source_quality: high
tags:
  - infrastructure
  - transaction-processing
  - access-control
  - privilege-misuse
date: 2026-04-27
source_refs:
  - git:224de766186e4e51dc0bc4b1d9cf109d64a278ac
  - "x/evm/evmstate/msg_server.go:580"
  - "x/evm/evmstate/funtoken_from_erc20_test.go:217"
  - "x/evm/evmstate/funtoken_from_coin_test.go:266"
  - "x/evm/evmstate/funtoken_from_erc20_test.go:10"
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a mainnet-only authorization gate to `Keeper.CreateFunToken`. On mainnet, the sender must either pass `SudoKeeper.CheckPermissions` or match the configured keeper authority before FunToken registration can continue. The evidence supports an access-control hardening/fix, but does not establish a concrete exploit impact beyond unauthorized mapping creation.

## Observed Patch Facts

1. In `x/evm/evmstate/msg_server.go`, the patch replaces `// Deduct fee upon registration.` with `if k.EthChainID(ctx).Cmp(big.NewInt(appconst.ETH_CHAIN_ID_MAINNET)) == 0 {`.

2. In `x/evm/evmstate/funtoken_from_erc20_test.go`, the patch replaces `func (s *SuiteFunToken) TestSendFromEvmToBank_MadeFromErc20() {` with `func (s *SuiteFunToken) TestCreateFunTokenPermissions_ERC20() {`.

3. In `x/evm/evmstate/funtoken_from_coin_test.go`, the patch replaces `// TestERC20TransferThenPrecompileSend` with `func (s *SuiteFunToken) TestCreateFunTokenPermissions_MainnetCoin() {`.

4. In `x/evm/evmstate/funtoken_from_erc20_test.go`, the patch adds `govtypes "github.com/cosmos/cosmos-sdk/x/gov/types"`.

## Project Context

The changed code sits primarily in `x/evm/evmstate`, `x/evm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/evm/evmstate/msg_ethereum_tx_test.go`, `x/evm/evmstate/bank_extension_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/evmstate/sdb_journal_test.go`, `x/evm/evmstate/sdb_ext_keeper_test.go`. The strongest project-level identifiers around this patch are `cosmos`, `bank`, `ethereum`, and `Sender`. Nearby tests or test-like files include `x/evm/precompile/test/bank_transfer.wasm`, `x/evm/precompile/test/export.go`.

## Before/After Behavior

Before the patch, the shown `CreateFunToken` flow validated the message, unwrapped the SDK context, and proceeded toward fee deduction and registration without the now-added mainnet authority or sudo permission check. After the patch, mainnet execution rejects senders that are neither sudo-authorized nor the configured authority. Tests were added for ERC20-backed and bank-denom-backed FunToken creation permissions.

# Root Cause

The provided evidence shows that `CreateFunToken` lacked an explicit mainnet-specific authorization gate before registration continued. It does not prove the full downstream impact of that missing gate.

## Walkthrough

1. `CreateFunToken` validates the incoming message.

2. The patched code unwraps the SDK context and checks whether the EVM chain ID is mainnet.

3. For mainnet, it parses `msg.Sender` as a Cosmos address.

4. It checks sudo permissions for that sender and separately allows the configured authority account.

5. If neither condition holds, it returns an `invalid signing authority` error before registration continues.

6. New tests cover permission behavior for ERC20-backed and bank-denom-backed FunToken creation.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/evmstate/msg_server.go | 580 | adds mainnet-only authority or sudo permission check in CreateFunToken before registration continues |
| x/evm/evmstate/funtoken_from_erc20_test.go | 217 | adds regression coverage for ERC20 FunToken creation permissions |
| x/evm/evmstate/funtoken_from_coin_test.go | 266 | adds regression coverage for bank-denom FunToken creation permissions |
| x/evm/evmstate/funtoken_from_erc20_test.go | 10 | adds governance types import used by permission tests |

## Code Snippets

## Snippet 1

Context: `x/evm/evmstate/msg_server.go:580` (changes a sensitive control or state-update path)

Before
```go
}

	// Deduct fee upon registration.
	ctx := sdk.UnwrapSDKContext(goCtx)
	err = k.deductCreateFunTokenFee(ctx, msg)
	if err != nil {
```
After
```go
}

	ctx := sdk.UnwrapSDKContext(goCtx)
	if k.EthChainID(ctx).Cmp(big.NewInt(appconst.ETH_CHAIN_ID_MAINNET)) == 0 {
		sender := sdk.MustAccAddressFromBech32(msg.Sender)
		sudoPermsErr := k.SudoKeeper.CheckPermissions(sender, ctx)
		havePerms := (sudoPermsErr == nil) || (k.authority.String() == msg.Sender)
		if !havePerms {
```

## Snippet 2

Context: `x/evm/evmstate/funtoken_from_erc20_test.go:217` (changes an authorization or privilege gate)

Before
```go
}

func (s *SuiteFunToken) TestSendFromEvmToBank_MadeFromErc20() {
	deps := evmtest.NewTestDeps()
```
After
```go
}

func (s *SuiteFunToken) TestCreateFunTokenPermissions_ERC20() {
	meta := evm.ERC20Metadata{
		Name:     "erc20permissioned",
		Symbol:   "TOKEN",
		Decimals: 18,
	}
```

## Snippet 3

Context: `x/evm/evmstate/funtoken_from_coin_test.go:266` (changes the branch that decides whether execution stops or continues)

Before
```go
}

// TestERC20TransferThenPrecompileSend
// 1. Creates a funtoken from coin.
```
After
```go
}

func (s *SuiteFunToken) TestCreateFunTokenPermissions_MainnetCoin() {
	validBankMetadata := func(bankDenom string) bank.Metadata {
		return bank.Metadata{
			DenomUnits: []*bank.DenomUnit{
				{
					Denom:    bankDenom,
```

## Snippet 4

Context: `x/evm/evmstate/funtoken_from_erc20_test.go:10` (changes a sensitive control or state-update path)

Before
```go
auth "github.com/cosmos/cosmos-sdk/x/auth/types"
	bank "github.com/cosmos/cosmos-sdk/x/bank/types"
	gethcommon "github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/crypto"
```
After
```go
auth "github.com/cosmos/cosmos-sdk/x/auth/types"
	bank "github.com/cosmos/cosmos-sdk/x/bank/types"
	govtypes "github.com/cosmos/cosmos-sdk/x/gov/types"
	gethcommon "github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/crypto"
```

# Fix Pattern

Add an authorization guard before a privileged state transition and cover the relevant creation variants with regression tests.

## How It Was Fixed

The fix inserted a mainnet-only check in `x/evm/evmstate/msg_server.go` inside `CreateFunToken`. The check allows the call only for sudo-authorized senders or the configured authority. Permission-focused tests were added in the ERC20 and coin FunToken test files.

# Why It Matters

1. Reduces who can create FunToken mappings on mainnet.

2. Makes the privileged-account requirement explicit in the message-server path.

3. Prevents non-authorized mainnet callers from reaching the registration flow.

4. Evidence does not show arbitrary fund theft or direct balance compromise.

# Evidence Notes

Primary evidence is the `CreateFunToken` hunk adding the mainnet chain-ID check, sudo permission check, authority fallback, and rejection error. Supporting evidence is the addition of `TestCreateFunTokenPermissions_ERC20` and `TestCreateFunTokenPermissions_MainnetCoin`. The evidence is limited to this creation path and does not establish broader FunToken mutation behavior or concrete exploit consequences. Protocol security invariant: On mainnet, FunToken mapping creation through `CreateFunToken` should be limited to the configured authority account or accounts authorized by the sudo module. Verification notes: The patch does not prove arbitrary fund theft or direct token balance compromise. The evidence only shows the CreateFunToken path, not all possible FunToken mutation paths. The restriction is explicitly mainnet-gated; non-mainnet behavior is not shown as vulnerable. The exact impact of unauthorized FunToken mapping creation is not fully demonstrated by the provided patch. The tests are evidence of intended authorization behavior, not proof of an externally exploitable attack path. Implementation evidence supports an authorization change in `CreateFunToken`. Tests support intended permission enforcement for both creation variants. Downgraded from confirmed security-fix to likely security-hardening because exploit impact is not demonstrated by the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`

The supplied patch evidence supports retaining this as security hardening: `CreateFunToken` now rejects mainnet callers unless they are sudo-authorized or match the configured authority, and new tests exercise permission behavior for ERC20-backed and coin-backed FunToken creation. The evidence does not prove a concrete exploit or downstream asset compromise, so it should not be upgraded to a confirmed security-fix case.

## Security Evidence

1. Adds a mainnet-only authorization gate in `Keeper.CreateFunToken` before registration continues.
2. Allows only senders passing `SudoKeeper.CheckPermissions` or matching `k.authority`.
3. Unauthorized mainnet senders now receive an `invalid signing authority` error.
4. Permission-focused tests were added for ERC20 and bank-denom FunToken creation paths.

## Missing Evidence

1. No proof that unauthorized FunToken creation was externally exploitable before the patch.
2. No demonstrated fund theft, balance corruption, or privilege escalation beyond unauthorized mapping creation.
3. No full before/after test output or exploit scenario showing concrete impact.
4. Commit body contains unrelated changes, so the specific security intent must be inferred from this hunk.

## Claim Boundaries

1. Validated only for the `CreateFunToken` authorization behavior shown in the supplied evidence.
2. Security classification should remain hardening rather than confirmed exploit fix.
3. Impact should be limited to unauthorized mainnet FunToken mapping creation or privilege misuse.
4. Non-mainnet behavior is intentionally unchanged by the shown patch.
