---
case_id: case_20250126_3f5be387
project: nibiru
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: staking
confidence: medium
source_quality: high
date: 2025-01-26
source_refs:
  - git:3f5be387ce3a659233be6190dd2b09b743ceb691
  - "x/evm/keeper/bank_extension.go:90"
  - "x/evm/precompile/wasm_test.go:671"
  - "x/evm/embeds/embeds.go:185"
  - "x/evm/precompile/wasm_test.go:7"
bug_class: cross-runtime-state-sync
impact_type:
  - state-accounting
tags:
  - infrastructure
  - evm
  - wasm
  - staking
  - precompile
  - state-sync
  - state-accounting
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Likely security fix for stale EVM-visible balances during an EVM-to-wasm staking flow. The implementation adds a `DelegateCoinsFromAccountToModule` wrapper that runs the base bank delegation and then syncs the EVM StateDB for the sender and recipient module account when the transferred coins include the EVM bank denom. The regression is named `TestDirtyStateAttack5` and documents an EVM contract calling the wasm precompile into a wasm contract that stakes 5 NIBI.

## Observed Patch Facts

1. In `x/evm/keeper/bank_extension.go`, the patch replaces `func (bk NibiruBankKeeper) MintCoins(` with `func (bk NibiruBankKeeper) DelegateCoinsFromAccountToModule(ctx sdk.Context, senderAd...`.

2. In `x/evm/precompile/wasm_test.go`, the patch adds `// TestDirtyStateAttack5`.

3. In `x/evm/embeds/embeds.go`, the patch adds `// SmartContract_TestDirtyStateAttack5 is a test contract that calls a wasm contract...`.

4. In `x/evm/precompile/wasm_test.go`, the patch adds `sdk "github.com/cosmos/cosmos-sdk/types"`.

## Project Context

The changed code sits primarily in `x/evm/keeper`, `x/evm`, `x/evm/precompile`, which anchors the finding in the `staking` area of the project. Historical context from `x/evm/precompile/wasm.go`, `x/evm/precompile/wasm_parse.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/precompile/wasm.go`, `x/evm/precompile/precompile.go`. The strongest project-level identifiers around this patch are `wasm`, `contract`, `cosmos`, and `that`. Nearby tests or test-like files include `x/evm/precompile/test/export.go`, `x/evm/evmtest/smart_contract.go`.

## Before/After Behavior

Before the patch, the provided implementation evidence does not show `DelegateCoinsFromAccountToModule` refreshing EVM StateDB after a Cosmos SDK delegation-to-module bank movement. After the patch, that path is wrapped in `ForceGasInvariant`, delegates through `bk.BaseKeeper.DelegateCoinsFromAccountToModule`, checks `findEtherBalanceChangeFromCoins(amt)`, and syncs both `senderAddr` and `auth.NewModuleAddress(recipientModule)`. The patch also adds regression support for `TestDirtyStateAttack5`, including an embedded Solidity test contract and a wasm precompile test scenario involving staking 5 NIBI.

# Root Cause

The supported root cause is a missing EVM StateDB synchronization hook on the Cosmos SDK delegation-to-module bank path. In the nested EVM-to-wasm staking scenario shown by the test comments, a NIBI balance movement could update Cosmos bank state without refreshing the EVM-visible balances for both affected accounts. The evidence supports stale cross-runtime balance/state risk, but does not establish theft, inflation, permanent fund loss, access-control bypass, or a broad consensus failure.

## Walkthrough

1. An EVM contract calls the wasm precompile, according to the documented `TestDirtyStateAttack5` scenario.

2. The wasm-side contract stakes 5 NIBI, which uses Cosmos SDK bank/staking delegation behavior.

3. That delegation moves EVM-denom funds from the sender account to a module account through `DelegateCoinsFromAccountToModule`.

4. Before the shown change, the supplied evidence does not show this path syncing the EVM StateDB after the Cosmos bank movement.

5. The patch adds a `NibiruBankKeeper.DelegateCoinsFromAccountToModule` wrapper around the base keeper call.

6. After the base delegation succeeds, the wrapper checks whether the moved coins include the EVM bank denom.

7. If the EVM denom changed, it syncs the EVM StateDB for the sender and the derived module account.

8. The new embedded contract and wasm precompile test exercise this nested staking path as a dirty-state regression.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/keeper/bank_extension.go | 90 | fixes bank delegation-to-module path by syncing EVM StateDB for sender and staking/module account after NIBI balance changes |
| x/evm/precompile/wasm_test.go | 671 | adds regression coverage for EVM contract calling wasm precompile into wasm staking flow |
| x/evm/embeds/embeds.go | 185 | registers TestDirtyStateAttack5 EVM test contract used by the regression |
| x/evm/embeds/contracts/TestDirtyStateAttack5.sol | 1 | test contract artifact source for exercising nested EVM-to-wasm staking behavior |

## Code Snippets

## Snippet 1

Context: `x/evm/keeper/bank_extension.go:90` (updates aggregate accounting or lifecycle state)

Before
```go
}

func (bk NibiruBankKeeper) MintCoins(
	ctx sdk.Context,
```
After
```go
}

func (bk NibiruBankKeeper) DelegateCoinsFromAccountToModule(ctx sdk.Context, senderAddr sdk.AccAddress, recipientModule string, amt sdk.Coins) error {
	return bk.ForceGasInvariant(
		ctx,
		func(ctx sdk.Context) error {
			return bk.BaseKeeper.DelegateCoinsFromAccountToModule(ctx, senderAddr, recipientModule, amt)
		},
```

## Snippet 2

Context: `x/evm/precompile/wasm_test.go:671` (updates aggregate accounting or lifecycle state)

Before
```go
})
}
```
After
```go
})
}

// TestDirtyStateAttack5
//  1. Deploy a simple wasm contract that stakes NIBI
//  2. Calls the test contract
//     a. call the wasm precompile which calls the wasm contract that stakes 5 NIBI
//
```

## Snippet 3

Context: `x/evm/embeds/embeds.go:185` (updates aggregate accounting or lifecycle state)

Before
```go
EmbedJSON: testDirtyStateAttack4,
	}
)
```
After
```go
EmbedJSON: testDirtyStateAttack4,
	}
	// SmartContract_TestDirtyStateAttack5 is a test contract that calls a wasm contract with 5 NIBI
	SmartContract_TestDirtyStateAttack5 = CompiledEvmContract{
		Name:      "TestDirtyStateAttack5.sol",
		EmbedJSON: testDirtyStateAttack5,
	}
)
```

## Snippet 4

Context: `x/evm/precompile/wasm_test.go:7` (updates aggregate accounting or lifecycle state)

Before
```go
"testing"

	wasm "github.com/CosmWasm/wasmd/x/wasm/types"

	"github.com/NibiruChain/nibiru/v2/eth"
```
After
```go
"testing"

	"cosmossdk.io/math"
	wasm "github.com/CosmWasm/wasmd/x/wasm/types"
	sdk "github.com/cosmos/cosmos-sdk/types"
	stakingkeeper "github.com/cosmos/cosmos-sdk/x/staking/keeper"
	stakingtypes "github.com/cosmos/cosmos-sdk/x/staking/types"
	"github.com/stretchr/testify/suite"
```

# Fix Pattern

Add a post-operation state synchronization hook to the bank delegation-to-module path, scoped to EVM-denom balance changes, and refresh all accounts whose EVM-visible balances may have changed.

## How It Was Fixed

`x/evm/keeper/bank_extension.go` adds `NibiruBankKeeper.DelegateCoinsFromAccountToModule`. The wrapper calls `bk.BaseKeeper.DelegateCoinsFromAccountToModule` inside `ForceGasInvariant`, then calls `SyncStateDBWithAccount` for the sender and recipient module account when `findEtherBalanceChangeFromCoins(amt)` is true. Test support was added through `TestDirtyStateAttack5` in the wasm precompile tests and a corresponding embedded Solidity contract registration.

# Why It Matters

1. Nested EVM-to-wasm execution crosses runtime state boundaries.

2. EVM-denom balances must remain coherent between Cosmos bank state and EVM StateDB.

3. Delegation-to-module movements affect both the sender and module account.

4. The patch addresses dirty or stale EVM-visible balance risk in this path.

5. The provided evidence does not prove a concrete loss or minting exploit.

# Evidence Notes

Strongest evidence is the implementation change in `x/evm/keeper/bank_extension.go` adding the delegation-to-module wrapper and conditional StateDB sync. Regression evidence is `x/evm/precompile/wasm_test.go`, where comments describe `TestDirtyStateAttack5` as an EVM contract calling the wasm precompile into a wasm contract that stakes 5 NIBI. `x/evm/embeds/embeds.go` registers the test contract. The wasm precompile implementation itself is only contextual in the supplied evidence and is not directly changed. Protocol security invariant: When EVM execution reaches Cosmos SDK bank or staking flows through the wasm precompile, EVM-denom balance changes must keep Cosmos bank state and the EVM StateDB coherent for every affected account, including module accounts. Verification notes: The patch does not by itself prove theft, inflation, or permanent fund loss. The patch does not show an access-control bypass despite touching a sensitive keeper path. The exact exploit preconditions, transaction ordering, and revert behavior are not fully shown in the supplied evidence. The evidence supports stale cross-runtime balance/state risk, not a broad validator-consensus failure claim. The wasm precompile implementation is contextual only; no direct change there is shown. Do not classify this as an access-control fix; the supplied code does not show privilege checks changing. Do not claim theft, inflation, permanent fund loss, or consensus failure from the provided evidence. Helper files, embedded artifacts, and wasm test files are regression/support code, not the root cause. The security classification rests on dirty cross-runtime balance state in an EVM-denom bank/staking path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `cross-runtime-state-sync`
Final impact type: `state-accounting`
Final tags: `infrastructure, evm, wasm, staking, precompile, state-sync, state-accounting`

The supplied patch evidence supports retaining this as security hardening rather than a fully proven security fix. The implementation adds a missing synchronization wrapper for DelegateCoinsFromAccountToModule so EVM StateDB is refreshed for both sender and module accounts when EVM-denom balances move, and the regression is explicitly framed as a DirtyStateAttack involving EVM-to-wasm staking. However, the evidence does not prove a concrete exploit outcome such as theft, inflation, consensus failure, or permanent fund loss.

## Security Evidence

1. Adds NibiruBankKeeper.DelegateCoinsFromAccountToModule wrapper around the base bank keeper path.
2. Conditionally syncs EVM StateDB after delegation-to-module when transferred coins include the EVM bank denom.
3. Syncs both the sender account and recipient module account, matching the affected balance movement.
4. Adds regression coverage named TestDirtyStateAttack5 for an EVM contract calling the wasm precompile into a staking wasm contract.
5. Registers an embedded TestDirtyStateAttack5 contract used by the dirty-state regression.

## Missing Evidence

1. No explicit exploit trace showing theft, inflation, fund loss, or unauthorized staking.
2. No before/after assertion output proving stale EVM-visible balances were exploitable.
3. No advisory, CVE, issue reference, or commit message identifying this as a security fix.
4. No direct evidence of access-control or validator-consensus failure despite sensitive subsystem context.

## Claim Boundaries

1. Classify as cross-runtime state synchronization hardening, not an access-control fix.
2. Do not claim proven theft, inflation, permanent fund loss, or consensus failure from the supplied evidence.
3. The strongest supported impact is stale or inconsistent EVM-visible state accounting during EVM-to-wasm staking.
4. Regression/support files corroborate the risky scenario but are not themselves the root cause.
