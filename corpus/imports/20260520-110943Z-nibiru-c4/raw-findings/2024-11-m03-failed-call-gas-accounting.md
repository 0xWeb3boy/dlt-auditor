# Nibiru C4 M-03: Gas used mismatch in failed contract calls can lead to wrong gas deductions

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `Medium`
- Corpus ID: `nibiru-c4-2024-11-m03-failed-call-gas-accounting`

---

## [[M-03] Gas used mismatch in failed contract calls can lead to wrong gas deductions](https://github.com/code-423n4/2024-11-nibiru-findings/issues/46)
*Submitted by [0x41](https://github.com/code-423n4/2024-11-nibiru-findings/issues/46)*

In `call_contract.go`, when a contract call fails, the code only consumes gas for the failed transaction but does not account for previously accumulated block gas usage. This creates a mismatch between the actual gas used in the block and what gets consumed in the gas meter.

The issue occurs in the error handling path of `CallContractWithInput` where after a failed call, only the gas of the failed transaction is consumed:

```go
if evmResp.Failed() {
    k.ResetGasMeterAndConsumeGas(ctx, evmResp.GasUsed) // Only consumes gas for this tx
    // ... error handling
}
```

However, in the success path, the code correctly adds the gas used to the block total:

```go
blockGasUsed, err := k.AddToBlockGasUsed(ctx, evmResp.GasUsed)
// ...
k.ResetGasMeterAndConsumeGas(ctx, blockGasUsed)
```

This inconsistency means that failed transactions do not properly contribute to the block's gas tracking. This is especially bad when the failed transaction is the last one in a block, as it will decrease the gas counter heavily (only the last transaction vs. the sum of all).

### Proof of Concept

The issue can be found in [`call_contract.go#L118`](https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/keeper/call_contract.go#L118):

```go
if evmResp.Failed() {
    k.ResetGasMeterAndConsumeGas(ctx, evmResp.GasUsed) // Only consumes failed tx gas
    if strings.Contains(evmResp.VmError, vm.ErrOutOfGas.Error()) {
        err = fmt.Errorf("gas required exceeds allowance (%d)", gasLimit)
        return
    }
    if evmResp.VmError == vm.ErrExecutionReverted.Error() {
        err = fmt.Errorf("VMError: %w", evm.NewRevertError(evmResp.Ret))
        return
    }
    err = fmt.Errorf("VMError: %s", evmResp.VmError)
    return
}
```

Compared to the success path at [`call_contract.go#L133`](https://github.com/code-423n4/2024-11-nibiru/blob/main/x/evm/keeper/call_contract.go#L133):

```go
blockGasUsed, err := k.AddToBlockGasUsed(ctx, evmResp.GasUsed)
if err != nil {
    k.ResetGasMeterAndConsumeGas(ctx, ctx.GasMeter().Limit())
    return nil, nil, errors.Wrap(err, "error adding transient gas used to block")
}
k.ResetGasMeterAndConsumeGas(ctx, blockGasUsed)
```

### Recommended mitigation steps

To fix this issue, the gas accounting should be consistent between success and failure paths. Add the block gas tracking before handling the failure case:

```go
// Add to block gas used regardless of success/failure
blockGasUsed, err := k.AddToBlockGasUsed(ctx, evmResp.GasUsed)
if err != nil {
    k.ResetGasMeterAndConsumeGas(ctx, ctx.GasMeter().Limit())
    return nil, nil, errors.Wrap(err, "error adding transient gas used to block")
}
k.ResetGasMeterAndConsumeGas(ctx, blockGasUsed)

if evmResp.Failed() {
    if strings.Contains(evmResp.VmError, vm.ErrOutOfGas.Error()) {
        err = fmt.Errorf("gas required exceeds allowance (%d)", gasLimit)
        return
    }
    // ... rest of error handling
}
```

This ensures that all gas used, whether from successful or failed transactions, is properly accounted for in the block total.

**[berndartmueller (judge) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/46#issuecomment-2556604380):**
 > Valid issue! For comparison, Ethermint consumes the cumulative gas for all EVM messages contained in the Cosmos tx (transient gas) -> [here](https://github.com/evmos/ethermint/blob/fd8c2d25cf80e7d2d2a142e7b374f979f8f51981/x/evm/keeper/state_transition.go#L260-L261).

**[k-yang (Nibiru) confirmed and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/46#issuecomment-2564154771):**
 > It's a valid issue but inaccurate. `k.ResetGasMeterAndConsumeGas()` sets the gas on the current transaction's gas meter, so setting it to `blockGasUsed` is incorrect and might lead to out of gas panics in later txs in a block. 
> 
> Specifically, the mistake is that we're not adding to the block gas meter on evm tx failure, and `k.ResetGasMeterAndConsumeGas(ctx, N)` should only be called with the evm tx gas used. 

**[Lambda (warden) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/46#issuecomment-2580994433):**
 > For audit severity consistency, I'd like to ask for a reconsideration of the severity here. The impact is the same as [Issue 25](https://github.com/code-423n4/2024-11-nibiru-findings/issues/25), so I think they should have the same severity.

**[berndartmueller (judge) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/46#issuecomment-2585250708):**
 > I had a closer look again. `CallContractWithInput()` is relevant for precompile calls. Those precompile calls have their own gas meter with a specific gas limit and are executed from within the EVM, which meters the gas and returns the gas used. This `evmResp.GasUsed` is then [added to the transient gas](https://github.com/code-423n4/2024-11-nibiru/blob/8ed91a036f664b421182e183f19f6cef1a4e28ea/x/evm/keeper/msg_server.go#L78) (block gas used, keeping track of the cumulative gas used across all EVM tx's bundled within a single Cosmos tx). 
> 
> I conclude from this that contract calls from within precompile calls are always added to the block gas used. Rendering this issue **invalid** as it does not explain the real issue. 
> 
> I even think that in the success case, the used gas should **not** be added to the block gas (in [`call_contract.go`](https://github.com/code-423n4/2024-11-nibiru/blob/8ed91a036f664b421182e183f19f6cef1a4e28ea/x/evm/keeper/call_contract.go#L133-L138)) and `k.ResetGasMeterAndConsumeGas(..)` should be called by providing `evmResp.GasUsed`. Otherwise, in my opinion, it would consider the gas used twice, the second time in `EthereumTx()`. This matches the sponsor's comment [above](https://github.com/code-423n4/2024-11-nibiru-findings/issues/46#issuecomment-2564154771).
> 
> Inviting @Lambda for comment.

**[Lambda (warden) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/46#issuecomment-2585295724):**
 > I first want to note that `CallContractWithInput` is not only used within `EthereumTx`, but also within `CallContract` or `deployERC20ForBankCoin`. Therefore, we would have to do the gas consumption in all consumers (which was not done) based on the `evmResp` and then we could drop it completely within `CallContractWithInput`.
> In the fix, the sponsor now actually did this. In other callers, the return value is now also added to the block gas meter and consumed as well, see example [here](https://github.com/NibiruChain/nibiru/pull/2132/files#diff-9fb1a48127c29e02a63ffd715100a99e5f8ab5a39cf64cebf3c718612e351e1bR88). However, this was previously not done and it was the responsibility of this function to add to the block gas meter in both cases.
> 
> But yes, after looking at it again, I agree that the success path was previously also wrong (depending on the caller), which would have been an issue on its own. This lead to a wrong recommended mitigation from me because I assumed this path was correct. Nevertheless, the issue that was pointed out in the finding description ("This inconsistency means that failed transactions do not properly contribute to the block's gas tracking") was actually present and would have lead to wrong gas tracking (for instance, for `deployERC20ForBankCoin` with failed calls, where the `evmResp.gasUsed` was not read and added to the block gas).

**[berndartmueller (judge) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/46#issuecomment-2585693189):**
 > @Lambda - let's clarify what "block gas" i.e., `AddToBlockGasUsed()` is used for. It is **not** used to track/meter cumulative gas used for the Cosmos block. Instead, it accumulates the gas that is used by EVM messages that are bundled within a single Cosmos SDK tx. The meter is [reset](https://github.com/code-423n4/2024-11-nibiru/blob/8ed91a036f664b421182e183f19f6cef1a4e28ea/app/evmante/evmante_setup_ctx.go#L46) in the ante handler for each Cosmos tx. "Block gas" is a rather lousy name for this. "Transient gas" meter would be more appropriate. Overall, this meter is used to make sure that the total gas used by a Cosmos tx that includes one or multiple EVM transactions is correctly accounted and [added to the actual block gas meter](https://github.com/cosmos/cosmos-sdk/blob/a1a4c9a962fe4ed4f4ade225ec9095dbce87b662/baseapp/baseapp.go#L867-L869). Also important to know that to ensure EVM gas equivalence, an [infinite gas meter is used for the overall Cosmos tx](https://github.com/code-423n4/2024-11-nibiru/blob/8ed91a036f664b421182e183f19f6cef1a4e28ea/app/evmante/evmante_setup_ctx.go#L40-L42). The gas limit is then enforced per EVM tx.
> 
> We have to consider this potential issue within two different contexts:
> 
> 1. Within a precompile called from within an EVM tx (potentially multiple EVM transactions bundled in a Cosmos tx).
> 2. Within a regular Cosmos tx.
> 
> For 1, the precompile call has its own gas meter. Gas usage is bubbled up and [handled appropriately](https://github.com/code-423n4/2024-11-nibiru/blob/8ed91a036f664b421182e183f19f6cef1a4e28ea/x/evm/keeper/msg_server.go#L65-L95) in `EthereumTx()`. Therefore, it's not necessary that within the precompile, i.e., within `CallContractWithInput()`, gas is added to the transient gas meter by calling `AddToBlockGasUsed()`. 
> 
> Can we agree on that?
> 
> For 2, the transient gas meter is not relevant. A regular Cosmos tx has a gas meter with the limit set to the limit provided by the tx sender. This gas meter is used for all messages contained in that tx. ~~Basically, this acts as a "transient" gas meter. Therefore, it's also not an issue~~. It even seems as if the EVM's transient gas meter is counterproductive and even problematic. It's not reset for each Cosmos SDK tx in the ante handler, it accumulates across them, causing issues at some point. @k-yang, did you consider this?
> 
> That's why I think the reported issue is not an actual issue. Please let me know what you think, happy to hear your thoughts!

**[Lambda (warden) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/46#issuecomment-2585857386):**
 > Regarding 1, agree, this was apparently another issue that the gas was added twice in this codepath.
> 
> Regarding 2, for regular Cosmos TX that contains some EVM calls (such as `deployERC20ForBankCoin`), we still need to add the gas used by the EVM execution to the Cosmos gas meter, right? Here, you have two approaches: Either you bubble it up and add it there (this is the approach that the sponsor seems to take in the new PR for all consumers of `CallContractWithInput`) or you do it directly in `CallContractWithInput` (this was done in the in-scope code).
>
> Moreover, when multiple messages are contained in a TX, you could add up the gas for the EVM calls and add it in the end or add it directly. In the in-scope code, both were done*, depending on if the call was successful or not. This still seems wrong to me, I do not see any reason why the gas accounting logic should be handled differently in the success or failure path (which `EthereumTx` does not as well), i.e., the underlying issue of this report.
> 
> **Note:* It seems like it was indeed done incorrectly after looking at it in more detail, as the transient gas meter is not reset in the ante handler for Cosmos SDK txs. But I think this is a different problem with a different underlying issue (the underlying issue being that it was not reset) and it seems natural to assume that the code was written with the intended functioning that it should add to the transient gas meter there; otherwise, this code would not have been in the success path.

**[berndartmueller (judge) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/46#issuecomment-2589496886):**
 > I now agree that within regular Cosmos TXs, it must track the cumulative EVM gas used across all batched Cosmos messages (which invoke an EVM call) and use it with `ResetGasMeterAndConsumeGas(..)`. 
> 
> Otherwise, as it is currently the case, `ResetGasMeterAndConsumeGas(..)` will incorrectly reset the Cosmos TX's gas meter to the currently failed msg's consumed gas (`evmResp.Failed()`) or gas limit (`err != nil`), ignoring the gas consumed by the preceding messages (in the same TX). As a result, the block gas meter will be inaccurate and increased by less gas than actually consumed.

**[k-yang (Nibiru) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/46#issuecomment-2619844763):**
 > Sorry for the late reply, but our code doesn't allow for mixing EVM msgs and Cosmos msgs in the same Cosmos tx, see:
> - https://github.com/code-423n4/2024-11-nibiru/blob/main/app/ante.go#L32-L47
> - https://github.com/code-423n4/2024-11-nibiru/blob/main/app/evmante/evmante_validate_basic.go#L95-L101
> 
> If a user wants to submit an EVM tx, it will contain the `/eth.evm.v1.ExtensionOptionsEthereumTx` extension option and `EthValidateBasicDecorator` will ensure that every bundled msg in the Tx is of type `evm.MsgEthereumTx`. So that eliminates the case where there are Cosmos and EVM msgs bundled in the same Cosmos Tx.
> 
> I agree that `BlockGasUsed` is a lousy name for the field. It should be `CumulativeGasUsedInTransaction` or something along those lines.
> 
> I see the warden's point for how, in a bundle of EVM msgs in a tx, if the last EVM msg fails, then we reset the _entire_ tx's gas meter and only consume the gas used of the last EVM msg. Now, we have removed the `BlockGasUsed` gas meter and switched to a model where each and every EVM msg adds to the gas meter (think vector addition), instead of always resetting and adding the cumulative gas used to the gas meter (which seemed redundant and more complicated than it needs to be).
>
> See [this fix](https://github.com/NibiruChain/nibiru/pull/2167) for the removal of the `BlockGasUsed` gas meter.

**Nibiru mitigated:**
> [PR-2132](https://github.com/NibiruChain/nibiru/pull/2132) - Proper tx gas refund outside of `CallContract`.

**Status:** Mitigation confirmed. 

***
