# Nibiru C4 M-04: Gas refunds use block gas instead of transaction gas, leading to incorrect refund amounts

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `Medium`
- Corpus ID: `nibiru-c4-2024-11-m04-cumulative-gas-refund`

---

## [[M-04] Gas refunds use block gas instead of transaction gas, leading to incorrect refund amounts](https://github.com/code-423n4/2024-11-nibiru-findings/issues/45)
*Submitted by [0x41](https://github.com/code-423n4/2024-11-nibiru-findings/issues/45), also found by [ABAIKUNANBAEV](https://github.com/code-423n4/2024-11-nibiru-findings/issues/83) and [Sentryx](https://github.com/code-423n4/2024-11-nibiru-findings/issues/66)*

There is a mismatch between how gas fees are deducted and refunded in the EVM implementation:

1. In `evmante_gas_consume.go`, gas fees are deducted upfront based on each transaction's individual gas limit.
2. However, the refund calculation in `msg_server.go` uses the cumulative block gas usage to determine refunds for individual transactions.

This mismatch means users will receive incorrect (lower) refunds than they should. The gas refund should be based on the difference between a transaction's gas limit (what was charged) and its actual gas usage (what was consumed), not the block's total gas usage.

The impact is that users will lose funds as they receive smaller refunds than they should. This becomes especially problematic when multiple transactions are included in a block, as the cumulative block gas increases with each transaction, reducing refunds for subsequent transactions.

### Proof of Concept

The issue stems from two pieces of code:

1. Gas fees are deducted in `evmante_gas_consume.go` based on transaction gas limit:

```go
// https://github.com/code-423n4/2024-11-nibiru/blob/84054a4f00fdfefaa8e5849c53eb66851a762319/app/evmante/evmante_gas_consume.go#L100-L105
		fees, err := keeper.VerifyFee(
			txData,
			evm.EVMBankDenom,
			baseFeeMicronibiPerGas,
			ctx.IsCheckTx(),
		)
```

Where `VerifyFee` returns the fee based on the transaction gas limit:

```go
// https://github.com/code-423n4/2024-11-nibiru/blob/84054a4f00fdfefaa8e5849c53eb66851a762319/x/evm/keeper/gas_fees.go#L194-L200
	feeAmtMicronibi := evm.WeiToNative(txData.EffectiveFeeWei(baseFeeWei))
	if feeAmtMicronibi.Sign() == 0 {
		// zero fee, no need to deduct
		return sdk.Coins{{Denom: denom, Amount: sdkmath.ZeroInt()}}, nil
	}

	return sdk.Coins{{Denom: denom, Amount: sdkmath.NewIntFromBigInt(feeAmtMicronibi)}}, nil
```

2. But refunds in `msg_server.go` are calculated using block gas:

```go
// https://github.com/code-423n4/2024-11-nibiru/blob/84054a4f00fdfefaa8e5849c53eb66851a762319/x/evm/keeper/msg_server.go#L87-L93
blockGasUsed, err := k.AddToBlockGasUsed(ctx, evmResp.GasUsed)
if err != nil {
    return nil, errors.Wrap(err, "EthereumTx: error adding transient gas used to block")
}

refundGas := uint64(0)
if evmMsg.Gas() > blockGasUsed {
    refundGas = evmMsg.Gas() - blockGasUsed
}
```

To demonstrate the impact, consider this scenario:

1. Transaction A has gas limit 100,000 and uses 50,000 gas.
2. Transaction B has gas limit 100,000 and uses 40,000 gas.
3. When calculating the refund for transaction B:
    - It should receive: 100,000 - 40,000 = 60,000 gas refund.
    - But actually receives: 100,000 - (50,000 + 40,000) = 10,000 gas refund.
    - The user loses refund for 50,000 gas.

### Recommended mitigation steps

The refund calculation should be based on each transaction's individual gas usage rather than the block gas. Modify the refund logic in `msg_server.go`:

```go
// Before
blockGasUsed, err := k.AddToBlockGasUsed(ctx, evmResp.GasUsed)
refundGas := uint64(0)
if evmMsg.Gas() > blockGasUsed {
    refundGas = evmMsg.Gas() - blockGasUsed
}

// After
refundGas := uint64(0)
if evmMsg.Gas() > evmResp.GasUsed {
    refundGas = evmMsg.Gas() - evmResp.GasUsed
}
blockGasUsed, err := k.AddToBlockGasUsed(ctx, evmResp.GasUsed)
```

This ensures that each transaction's refund is calculated based on its own gas limit and usage, independent of other transactions in the block.

**[ABAIKUNANBAEV (warden) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/45#issuecomment-2581685781):**
 > @berndartmueller, I believe this should be of high severity as the issue deals with refunds and therefore, losing of funds. There are several DOS-related issues marked as high but this one with the actual funds losing is not.

**[berndartmueller (judge) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/45#issuecomment-2585255454):**
> @ABAIKUNANBAEV, sticking with Medium as this affects individual users, users who batch multiple EVM tx's within a single Cosmos SDK tx. And batch EVM messages are not that common currently. Thus, I think Medium is justified.

**[k-yang (Nibiru) disputed and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/45#issuecomment-2620147976):**
 > Please see my comment on [Issue 46](https://github.com/code-423n4/2024-11-nibiru-findings/issues/46#issuecomment-2619844763).
> 
> `BlockGasUsed` was actually a terrible name for the gas tracker variable. It's actually the cumulative amount of gas used in the TX when multiple EVM msgs are bundled in it. It gets [reset between TXs by the evm ante handler](https://github.com/code-423n4/2024-11-nibiru/blob/84054a4f00fdfefaa8e5849c53eb66851a762319/app/evmante/evmante_setup_ctx.go#L46).
> 
> Since that's the case, the gas refunded here is correct. The `blockGasUsed` variable is actually the total amount of gas used by the entire TXs, summing up all the individually bundled EVM msgs.

**Nibiru mitigated:**
> [PR-2132](https://github.com/NibiruChain/nibiru/pull/2132) - Proper tx gas refund outside of `CallContract`.

**Status:** Mitigation confirmed. 

***
