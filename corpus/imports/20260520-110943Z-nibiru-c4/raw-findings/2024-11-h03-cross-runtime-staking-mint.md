# Nibiru C4 H-03: Unlimited Nibi could be minted because EVM and bank balance are not synced when staking

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `High`
- Corpus ID: `nibiru-c4-2024-11-h03-cross-runtime-staking-mint`

---

## [[H-03] Unlimited Nibi could be minted because evm and bank balance are not synced when staking](https://github.com/code-423n4/2024-11-nibiru-findings/issues/26)
*Submitted by [0x007](https://github.com/code-423n4/2024-11-nibiru-findings/issues/26)* 

`NibiruBankKeeper.SyncStateDBWithAccount` function in [`bank_extension.go`](https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/keeper/bank_extension.go#L80C1-L91C2) is responsible for synchronizing the EVM state database (`StateDB`) with the corresponding bank account balance whenever the balance is updated. However, this function is not invoked by all operations that modify bank balances.

```go
func (bk *NibiruBankKeeper) SyncStateDBWithAccount(
	ctx sdk.Context, acc sdk.AccAddress,
) {
	// If there's no StateDB set, it means we're not in an EthereumTx.
	if bk.StateDB == nil {
		return
	}
	balanceWei := evm.NativeToWei(
		bk.GetBalance(ctx, acc, evm.EVMBankDenom).Amount.BigInt(),
	)
	bk.StateDB.SetBalanceWei(eth.NibiruAddrToEthAddr(acc), balanceWei)
}
```

The following functions call [`bankKeeper.setBalance`](https://github.com/NibiruChain/cosmos-sdk/blob/v0.47.11-nibiru.2/x/bank/keeper/send.go#L337), but some do not trigger `SyncStateDBWithAccount`:

```
*   bankKeeper.addCoins
    *   bankKeeper.SendCoins (✅ Synced)
        *   bankMsgServer.Send
        *   bankKeeper.SendCoinsFromModuleToAccount (✅ Synced)
        *   bankKeeper.SendCoinsFromModuleToModule (✅ Synced)
        *   bankKeeper.SendCoinsFromAccountToModule (✅ Synced)
    *   bankKeeper.InputOutputCoins (❌ Not Synced)
        *   bankMsgServer.MultiSend
    *   bankKeeper.DelegateCoins (❌ Not Synced)
    *   bankKeeper.UndelegateCoins (❌ Not Synced)
    *   bankKeeper.MintCoins (✅ Synced)
*   bankKeeper.subUnlockedCoins
    *   bankKeeper.SendCoins (✅ Synced)
    *   bankKeeper.InputOutputCoins (❌ Not Synced)
    *   bankKeeper.UndelegateCoins (❌ Not Synced)
    *   bankKeeper.BurnCoins (✅ Synced)
*   bankKeeper.DelegateCoins (❌ Not Synced)
    *   bankKeeper.DelegateCoinsFromAccountToModule
        *   stakingKeeper.Delegate
            *   stakingMsgServer.CreateValidator
            *   stakingMsgServer.Delegate
            *   stakingMsgServer.CancelUnbondingDelegation
            *   stakingKeeper.BeginRedelegation
                *   stakingMsgServer.BeginRedelegate
```

The EVM can mint or burn an arbitrary amount of Nibi tokens when the `obj.Account.BalanceWei` in the StateDB is out of sync. Specifically, the EVM's [`SetAccBalance`](https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/keeper/statedb.go#L72-L98) function allows this discrepancy to occur if balances are updated outside of the `SyncStateDBWithAccount` mechanism.

### Proof of Concept

The `bankKeeper.DelegateCoins` function illustrates this vulnerability. It would reduce the balance of delegator address and increase the balance [`BondedPoolName` or `NotBondedPoolName`](https://github.com/NibiruChain/cosmos-sdk/blob/v0.47.11-nibiru.2/x/staking/keeper/delegation.go#L672-L680) module address. And this could be triggered because

- `stakingMsgServer` can reach it with `Delegate -> stakingKeeper.Delegate -> bankKeeper.DelegateCoinsFromAccountToModule -> bankKeeper.DelegateCoins`.
- `stakingMsgServer` can be triggered by wasm contracts ([here](https://github.com/code-423n4/2024-11-nibiru/blob/main/app/keepers.go#L462-L465) and [here](https://github.com/NibiruChain/wasmd/blob/v0.44.0-nibiru/app/wasm.go#L9)).
- wasm contracts can be triggered by evm contracts ([here](https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/precompile/wasm.go#L118C1-L162C2)).

<https://github.com/code-423n4/2024-11-nibiru/blob/main/app/keepers.go#L462-L465>

```go
supportedFeatures := strings.Join(wasmdapp.AllCapabilities(), ",")

// Create wasm VM outside keeper so it can be reused in client keeper
wasmVM, err := wasmvm.NewVM(filepath.Join(wasmDir, "wasm"), supportedFeatures, wasmVmContractMemoryLimit, wasmConfig.ContractDebugMode, wasmConfig.MemoryCacheSize)
```

<https://github.com/NibiruChain/wasmd/blob/v0.44.0-nibiru/app/wasm.go#L9>

```go
func AllCapabilities() []string {
	return []string{
		"iterator",
		"staking",
		"stargate",
		"cosmwasm_1_1",
		"cosmwasm_1_2",
		"cosmwasm_1_3",
		"cosmwasm_1_4",
	}
}
```

<https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/precompile/wasm.go#L118C1-L162C2>

```go
// execute invokes a Wasm contract's "ExecuteMsg", which corresponds to
// "wasm/types/MsgExecuteContract". This enables arbitrary smart contract
// execution using the Wasm VM from the EVM.
//
// Implements "execute" from evm/embeds/contracts/Wasm.sol:
//
//	```solidity
//	 function execute(
//	   string memory contractAddr,
//	   bytes memory msgArgs,
//	   BankCoin[] memory funds
//	 ) payable external returns (bytes memory response);
//	```
//
// Contract Args:
//   - contractAddr: nibi-prefixed Bech32 address of the wasm contract
//   - msgArgs: JSON encoded wasm execute invocation
//   - funds: Optional funds to supply during the execute call. It's
//     uncommon to use this field, so you'll pass an empty array most of the time.
func (p precompileWasm) execute(
	start OnRunStartResult,
	caller gethcommon.Address,
	readOnly bool,
) (bz []byte, err error) {
	method, args, ctx := start.Method, start.Args, start.CacheCtx
	defer func() {
		if err != nil {
			err = ErrMethodCalled(method, err)
		}
	}()
	if err := assertNotReadonlyTx(readOnly, method); err != nil {
		return nil, err
	}

	wasmContract, msgArgsBz, funds, err := p.parseArgsWasmExecute(args)
	if err != nil {
		err = ErrInvalidArgs(err)
		return
	}
	data, err := p.Wasm.Execute(ctx, wasmContract, eth.EthAddrToNibiruAddr(caller), msgArgsBz, funds)
	if err != nil {
		return
	}
	return method.Outputs.Pack(data)
}
```

### Exploit Steps

- Create a Wasm contract to perform staking-related operations and fund it with `X` Nibi.
- Create an EVM contract to interact with the Wasm contract.
- In the EVM contract:
    - Transfer dust amount to the wasm so that the account is retrieved and added to the `statedb`'s `stateObjects`
    - Instruct the wasm contract to delegate `Y` Nibi
- When delegate reduces the wasm balance from `X` to `X-Y`. EVM would still believe the balance is `X` and `SetAccBalance` would increase the balance from `X-Y` to `X` by minting `Y`.
- The attacker can call the wasm contract to undelegate the delegated `Y` Nibi, or attack several times to take over the chain.

### Recommended mitigation steps

Make sure EVM statedb is synced for every action that changes bank balances, preferably from `setBalance`.

**[k-yang (Nibiru) confirmed and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/26#issuecomment-2550259578):**
 > Agree this is a high risk vulnerability.

**Nibiru mitigated:**
> [PR-2142](https://github.com/NibiruChain/nibiru/pull/2142) - Add additional missing bank keeper method overrides to sync with `StateDB`.

**Status:** Mitigation confirmed. 

***
