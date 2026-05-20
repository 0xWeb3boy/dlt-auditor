# Nibiru C4 M-02: Double fee application breaks supply invariant for fee-on-transfer ERC20s

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `Medium`
- Corpus ID: `nibiru-c4-2024-11-m02-fee-on-transfer-supply-drift`

---

## [[M-02] Double fee application breaks supply invariant for fee-on-transfer ERC20s](https://github.com/code-423n4/2024-11-nibiru-findings/issues/48)
*Submitted by [0x41](https://github.com/code-423n4/2024-11-nibiru-findings/issues/48)*

The EVM module incorrectly handles fee-on-transfer tokens when converting bank coins back to ERC20s, resulting in unbacked bank coins remaining in circulation. This breaks the intended 1:1 supply tracking invariant between ERC20 tokens and their bank coin representations.

When converting from ERC20 to bank coins via `sendToBank`, the code correctly accounts for transfer fees by only minting bank coins equal to the amount actually received. However, when converting these bank coins back to ERC20s via `convertCoinToEvmBornERC20`, the code:

1. Takes in `X` bank coins from the user.
2. Tries to transfer `X` ERC20 tokens.
3. Due to fees, only `Y` tokens are received (`Y < X`).
4. Only burns `Y` bank coins.

This creates a discrepancy since the original conversion already accounted for fees. The transfer fees are effectively applied twice:

1. First fee: `100 ERC20 -> 95 bank coins` (correct).
2. Second fee: `95 bank coins -> ~90.25 ERC20` (and only burn 90.25 bank coins).

This leaves 4.75 unbacked bank coins in circulation (95 - 90.25), as the code only burns what was actually transferred in the second conversion.

The impact is monetary - it creates unbacked bank coins that can be used in the rest of the system but don't have corresponding ERC20 tokens backing them in the EVM module's account. Over time, this could lead to significant supply inflation of the bank coin representation.

### Proof of Concept

The first conversion correctly handles fees in `funtoken.go`:

```go
// First conversion correctly uses actual received amount
gotAmount, transferResp, err := p.evmKeeper.ERC20().Transfer(erc20, caller, transferTo, amount, ctx)
if err != nil {
    return nil, fmt.Errorf("error in ERC20.transfer from caller to EVM account: %w", err)
}
coinToSend := sdk.NewCoin(funtoken.BankDenom, math.NewIntFromBigInt(gotAmount))
```

[`funtoken.go#L162-L170`](https://github.com/code-423n4/2024-11-nibiru/blob/84054a4f00fdfefaa8e5849c53eb66851a762319/x/evm/precompile/funtoken.go#L162-L170)

But when converting back in `msg_server.go`, it incorrectly applies fees again:

```go
actualSentAmount, _, err := k.ERC20().Transfer(
    erc20Addr,
    evm.EVM_MODULE_ADDRESS,
    recipient,
    coin.Amount.BigInt(),
    ctx,
)
if err != nil {
    return nil, errors.Wrap(err, "failed to transfer ERC-20 tokens")
}

// Only burns the amount after fees, even though fees were already accounted for
burnCoin := sdk.NewCoin(coin.Denom, sdk.NewIntFromBigInt(actualSentAmount))
err = k.Bank.BurnCoins(ctx, evm.ModuleName, sdk.NewCoins(burnCoin))
```

[`msg_server.go#L597-L613`](https://github.com/code-423n4/2024-11-nibiru/blob/84054a4f00fdfefaa8e5849c53eb66851a762319/x/evm/keeper/msg_server.go#L597-L613)

The code explicitly aims to maintain a supply invariant:

```go
// to preserve an invariant on the sum of the FunToken's bank and ERC20 supply, 
// we burn the coins here in the BC → ERC20 conversion.
```

[`msg_server.go#L603`](https://github.com/code-423n4/2024-11-nibiru/blob/84054a4f00fdfefaa8e5849c53eb66851a762319/x/evm/keeper/msg_server.go#L603)

### Recommended mitigation steps

When converting bank coins back to ERC20s in `convertCoinToEvmBornERC20`, the code should burn the full input amount of bank coins, not just the amount after fees. This ensures fees are only applied once in the entire conversion cycle.

```go
// In msg_server.go convertCoinToEvmBornERC20:
actualSentAmount, _, err := k.ERC20().Transfer(
    erc20Addr,
    evm.EVM_MODULE_ADDRESS,
    recipient,
    coin.Amount.BigInt(),
    ctx,
)
if err != nil {
    return nil, errors.Wrap(err, "failed to transfer ERC-20 tokens")
}

// Burn the full input amount, not the amount after fees
err = k.Bank.BurnCoins(ctx, evm.ModuleName, sdk.NewCoins(coin))
```

This maintains the supply invariant since:

1. First conversion: `100 ERC20 -> 95 bank coins` (after 5% fee).
2. Second conversion: `95 bank coins -> ~90.25 ERC20` (after another 5% fee), burn full 95 bank coins.

The documentation should also be updated to explicitly describe how fee-on-transfer tokens are handled and that fees will apply on both conversions.

**[k-yang (Nibiru) confirmed and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/48#issuecomment-2573453351):**
 > I don't think it has a monetary impact on the financial ecosystem though because those unburned coins that accumulate at the EVM module address are inaccessible. It's the logical equivalent of being burned, except that it still shows up in total supply calculations. We'll fix it for accounting purposes, but it's not an infinite mint bug where the attacker can actually use the funds.

**Nibiru mitigated:**
> [PR-2139](https://github.com/NibiruChain/nibiru/pull/2139) - Ensure bank coins are properly burned after converting back to ERC20.

**Status:** Mitigation confirmed. 

***
