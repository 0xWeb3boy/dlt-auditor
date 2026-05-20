# Nibiru C4 M-09: The bankBalance function failed to handle errors correctly

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `Medium`
- Corpus ID: `nibiru-c4-2024-11-m09-bank-balance-parse-error-panic`

---

## [[M-09] The `bankBalance` function failed to handle errors correctly](https://github.com/code-423n4/2024-11-nibiru-findings/issues/5)
*Submitted by [shaflow2](https://github.com/code-423n4/2024-11-nibiru-findings/issues/5), also found by [Rhaydden](https://github.com/code-423n4/2024-11-nibiru-findings/issues/87)*

The `bankBalance` function does not handle errors after decoding the call parameters. As a result, `p.evmKeeper.Bank.GetBalance` may throw a panic, and this erroneous panic cannot be recovered by `HandleOutOfGasPanic`, leading to the erroneous panic being propagated further up the program.

### Proof of Concept

https://github.com/code-423n4/2024-11-nibiru/blob/8ed91a036f664b421182e183f19f6cef1a4e28ea/x/evm/precompile/funtoken.go#L378

```go
func (p precompileFunToken) bankBalance(
	start OnRunStartResult,
	contract *vm.Contract,
) (bz []byte, err error) {
	method, args, ctx := start.Method, start.Args, start.CacheCtx
	defer func() {
		if err != nil {
			err = ErrMethodCalled(method, err)
		}
	}()
	if err := assertContractQuery(contract); err != nil {
		return bz, err
	}

@>	addrEth, addrBech32, bankDenom, err := p.parseArgsBankBalance(args)
	bankBal := p.evmKeeper.Bank.GetBalance(ctx, addrBech32, bankDenom).Amount.BigInt()

	return method.Outputs.Pack([]any{
		bankBal,
		struct {
			EthAddr    gethcommon.Address `json:"ethAddr"`
			Bech32Addr string             `json:"bech32Addr"`
		}{
			EthAddr:    addrEth,
			Bech32Addr: addrBech32.String(),
		},
	}...)
}
```

It can be observed that even if `parseArgsBankBalance` returns an error during decoding, the program will still proceed to call `p.evmKeeper.Bank.GetBalance` using incorrect data.

```go
// GetBalance returns the balance of a specific denomination for a given account
// by address.
func (k BaseViewKeeper) GetBalance(ctx sdk.Context, addr sdk.AccAddress, denom string) sdk.Coin {
	accountStore := k.getAccountStore(ctx, addr)
	bz := accountStore.Get([]byte(denom))
	balance, err := UnmarshalBalanceCompat(k.cdc, bz, denom)
	if err != nil {
		panic(err)
	}

	return balance
}
```

This is likely to cause `GetBalance` to throw a panic. This panic is unexpected and, therefore, cannot be caught by `HandleOutOfGasPanic`, resulting in the program further throwing an exception.

```go
func HandleOutOfGasPanic(err *error) func() {
	return func() {
		if r := recover(); r != nil {
			switch r.(type) {
			case sdk.ErrorOutOfGas:
				*err = vm.ErrOutOfGas
			default:
				panic(r)
			}
		}
	}
}
```

### Recommended mitigation steps

```diff
func (p precompileFunToken) bankBalance(
	start OnRunStartResult,
	contract *vm.Contract,
) (bz []byte, err error) {
	method, args, ctx := start.Method, start.Args, start.CacheCtx
	defer func() {
		if err != nil {
			err = ErrMethodCalled(method, err)
		}
	}()
	if err := assertContractQuery(contract); err != nil {
		return bz, err
	}

  	addrEth, addrBech32, bankDenom, err := p.parseArgsBankBalance(args)
+	if err != nil {
+		err = ErrInvalidArgs(err)
+		return
+	}
	bankBal := p.evmKeeper.Bank.GetBalance(ctx, addrBech32, bankDenom).Amount.BigInt()

	return method.Outputs.Pack([]any{
		bankBal,
		struct {
			EthAddr    gethcommon.Address `json:"ethAddr"`
			Bech32Addr string             `json:"bech32Addr"`
		}{
			EthAddr:    addrEth,
			Bech32Addr: addrBech32.String(),
		},
	}...)
}
```

**Unique-Divine (Nibiru) confirmed**

**Nibiru mitigated:**
> [PR-2116](https://github.com/NibiruChain/nibiru/pull/2116) - Fixed bug where the `err != nil` check is missing in the `bankBalance` precompile method.

**Status:** Mitigation confirmed. 

***
