# Nibiru C4 M-05: Inconsistent fee denomination handling in transaction validation and building

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `Medium`
- Corpus ID: `nibiru-c4-2024-11-m05-wei-native-fee-units`

---

## [[M-05] Inconsistent fee denomination handling in transaction validation and building](https://github.com/code-423n4/2024-11-nibiru-findings/issues/44)
*Submitted by [0x41](https://github.com/code-423n4/2024-11-nibiru-findings/issues/44)*

The Nibiru EVM module incorrectly handles fee denominations during transaction validation and building, failing to convert wei amounts to the native unibi denomination. This can lead to significant discrepancies in fee calculations and potentially allow users to pay far fewer fees than intended.

The issue occurs in two locations:

1. Transaction validation in `evmante_validate_basic.go`.
2. Transaction building in `msg.go`.

In both cases, fees that are calculated in wei (1e18 units) are directly used with `evm.EVMBankDenom` (unibi), without converting from wei to unibi (1e6 units). This causes an undervaluation of fees by a factor of `10^12`, as the system expects fees in unibi but receives them in wei.

### Proof of Concept

1. In `evmante_validate_basic.go`, the fee validation directly uses the wei amount:

```go
txFee = txFee.Add(
    sdk.Coin{
        Denom:  evm.EVMBankDenom,
        Amount: sdkmath.NewIntFromBigInt(txData.Fee()), // Fee() returns wei amount
    },
)
```

[`evmante_validate_basic.go#L128`](https://github.com/code-423n4/2024-11-nibiru/blob/84054a4f00fdfefaa8e5849c53eb66851a762319/app/evmante/evmante_validate_basic.go#L128)

2. Similarly in `msg.go`, when building a transaction:

```go
feeAmt := sdkmath.NewIntFromBigInt(txData.Fee())
if feeAmt.Sign() > 0 {
    fees = append(fees, sdk.NewCoin(evmDenom, feeAmt)) // Fee() returns wei amount
}
```

[`msg.go#L367`](https://github.com/code-423n4/2024-11-nibiru/blob/84054a4f00fdfefaa8e5849c53eb66851a762319/x/evm/msg.go#L367)

The `Fee()` function in `tx_data_legacy.go` calculates fees in wei:

```go
func (tx LegacyTx) Fee() *big.Int {
    return priceTimesGas(tx.GetGasPrice(), tx.GetGas())
}
```

To demonstrate the impact:

1. A transaction with a gas price of 1 wei and gas limit of 21000 would result in a fee of 21000 wei.
2. This should be converted to 0.000021 unibi (`21000 / 10^12`).
3. However, the current code would set it as 21000 unibi, which is incorrect by a factor of `10^12`.

### Recommended mitigation steps

1. In `evmante_validate_basic.go`, modify the fee validation to convert from wei to unibi:

```go
txFee = txFee.Add(
    sdk.Coin{
        Denom:  evm.EVMBankDenom,
        Amount: sdkmath.NewIntFromBigInt(evm.WeiToNative(txData.Fee())),
    },
)
```

2. In `msg.go`, update the fee conversion in `BuildTx`:

```go
feeAmt := sdkmath.NewIntFromBigInt(evm.WeiToNative(txData.Fee()))
if feeAmt.Sign() > 0 {
    fees = append(fees, sdk.NewCoin(evmDenom, feeAmt))
}
```

**[k-yang (Nibiru) confirmed](https://github.com/code-423n4/2024-11-nibiru-findings/issues/44#event-15816019229)** 

**[Unique-Divine (Nibiru) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/44#issuecomment-2582030643):**
 > Note that a gas price of 1 wei isn't possible. The smallest unit of funds that can be transferred is `10^{12}` wei, or 1 unibi, meaning the `21000unibi` value for fees paid what's wanted here. 
> 
> Digging into this now to see which parts are correct or incorrect between `msg.go` and `evmante_validate_basic.go`.

**Nibiru mitigated:**
> [PR-2157](https://github.com/NibiruChain/nibiru/pull/2157) - Fixed unit inconsistency related to `AuthInfo.Fee` and `txData.Fee`.

**Status:** Mitigation confirmed. 

***
