# Nibiru C4 M-08: Nibiru's bank coin to EVM balance tracking logic is broken for rebasing tokens

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `Medium`
- Corpus ID: `nibiru-c4-2024-11-m08-rebasing-token-escrow-drift`

---

## [[M-08] Nibiru's bank coin to EVM balance tracking logic is completely broken for rebasing tokens and would lead to leakage/loss of funds when converting](https://github.com/code-423n4/2024-11-nibiru-findings/issues/14)
*Submitted by [Bauchibred](https://github.com/code-423n4/2024-11-nibiru-findings/issues/14), also found by [Sentryx](https://github.com/code-423n4/2024-11-nibiru-findings/issues/65) and [0x007](https://github.com/code-423n4/2024-11-nibiru-findings/issues/63)*

The Nibiru EVM module's token conversion mechanism contains a critical vulnerability when handling rebasing tokens. The issue stems from an incorrect assumption about the 1:1 relationship between escrowed ERC20 tokens and their bank coin representations, which can be violated when token balances change outside of transfers (e.g., through rebasing) and these type of tokens are supported by Nibiru.

### Context

The Nibiru EVM module supports converting ERC20 tokens to bank coins and vice versa. When converting from ERC20 to bank coins, the tokens are escrowed in the EVM module, and when converting back, these escrowed tokens are used to fulfill the conversion.

This logic can be seen in the `ConvertCoinToEvm`, `convertCoinToEvmBornERC20` and `convertEvmToCoin` functions in the `msg_server.go` file, see [`x/evm/keeper/msg_server.go#L486-L561`](https://github.com/code-423n4/2024-11-nibiru/blob/8ed91a036f664b421182e183f19f6cef1a4e28ea/x/evm/keeper/msg_server.go#L486-L624).

### Problem

The conversion mechanism assumes a static 1:1 relationship between escrowed ERC20 tokens and bank coins, as evidenced in the `convertCoinToEvmBornERC20` function that is used when [converting the bank coins back to its ERC20 representation](https://github.com/code-423n4/2024-11-nibiru/blob/8ed91a036f664b421182e183f19f6cef1a4e28ea/x/evm/keeper/msg_server.go#L510-L513):

See [here](https://github.com/code-423n4/2024-11-nibiru/blob/8ed91a036f664b421182e183f19f6cef1a4e28ea/x/evm/keeper/msg_server.go#L567-L624>):

```go
func (k Keeper) convertCoinToEvmBornERC20(
	ctx sdk.Context,
	sender sdk.AccAddress,
	recipient gethcommon.Address,
	coin sdk.Coin,
	funTokenMapping evm.FunToken,
) (*evm.MsgConvertCoinToEvmResponse, error) {
	erc20Addr := funTokenMapping.Erc20Addr.Address
	// 1 | Caller transfers Bank Coins to be converted to ERC20 tokens.
	if err := k.Bank.SendCoinsFromAccountToModule(
		ctx,
		sender,
		evm.ModuleName,
		sdk.NewCoins(coin),
	); err != nil {
		return nil, errors.Wrap(err, "error sending Bank Coins to the EVM")
	}

	// 2 | EVM sends ERC20 tokens to the "to" account.
	// This should never fail due to the EVM account lacking ERc20 fund because
	// the an account must have sent the EVM module ERC20 tokens in the mapping
	// in order to create the coins originally.
	//
	// Said another way, if an asset is created as an ERC20 and some amount is
	// converted to its Bank Coin representation, a balance of the ERC20 is left
	// inside the EVM module account in order to convert the coins back to
	// ERC20s.
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

	// 3 | In the FunToken ERC20 → BC conversion process that preceded this
	// TxMsg, the Bank Coins were minted. Consequently, to preserve an invariant
	// on the sum of the FunToken's bank and ERC20 supply, we burn the coins here
	// in the BC → ERC20 conversion.
	burnCoin := sdk.NewCoin(coin.Denom, sdk.NewIntFromBigInt(actualSentAmount))
	err = k.Bank.BurnCoins(ctx, evm.ModuleName, sdk.NewCoins(burnCoin))
	if err != nil {
		return nil, errors.Wrap(err, "failed to burn coins")
	}

	// Emit event with the actual amount received
	_ = ctx.EventManager().EmitTypedEvent(&evm.EventConvertCoinToEvm{
		Sender:               sender.String(),
		Erc20ContractAddress: funTokenMapping.Erc20Addr.String(),
		ToEthAddr:            recipient.String(),
		BankCoin:             burnCoin,
	})

	return &evm.MsgConvertCoinToEvmResponse{}, nil
}
```

Evidently, Nibiru makes a critical assumption (invariant) about token availability as shown in the snippet above.

```markdown
    // This should never fail due to the EVM account lacking ERc20 fund because
    // the an account must have sent the EVM module ERC20 tokens in the mapping
    // in order to create the coins originally.
    //
    // Said another way, if an asset is created as an ERC20 and some amount is
    // converted to its Bank Coin representation, a balance of the ERC20 is left
    // inside the EVM module account in order to convert the coins back to
    // ERC20s.
```

However, this assumption would be incorrect for some supported tokens like rebasing tokens, which have been hinted to be used by Nibiru as shown in the README:

[README.md#L129-L137](https://github.com/code-423n4/2024-11-nibiru/blob/8ed91a036f664b421182e183f19f6cef1a4e28ea/README.md#L129-L137)

This is because for tokens that have their balance changes not necessarily through transfers, and are rebasing in nature there would be multiple rebases while the tokens are escrowed after the initial conversion from ERC20 to Bank Coin; which would then mean that by the time there is an attempt to convert the tokens back to ERC20, the balance of the tokens in the escrow would have changed (positively/negatively) completely sidestepping the invariant of 1:1 relationship between escrowed ERC20 tokens and their bank coin representations.

### Impact

This bug case completely breaks the subtle invariant of 1:1 relationship between escrowed ERC20 tokens and their bank coin representations. In our case, the issue manifests itself in the following two scenarios:

1. If cumulatively, the rebases that occur since the initial conversion from ERC20 to Bank Coin are positive, then the difference between the amount of escrowed tokens and that of bank coins would be stuck in the escrow.

2. Alternatively, if cumulatively, the rebases that occur since the initial conversion from ERC20 to Bank Coin are negative, then the escrow balance would be insufficient to fulfill the conversion, causing the transaction to revert with insufficient balance errors.

### Tools Used

- Similar issue from the Q2 Thorchain Contest on Code4rena [here](https://code4rena.com/reports/2024-06-thorchain#h-01-a-malicious-user-can-steal-money-out-of-the-vault-and-other-users) and [here](https://github.com/code-423n4/2024-06-thorchain-findings/issues?q=is%3Aissue+Protocol+could+be+tricked+on+some+to-be+integrated+tokens+is%3Aclosed).
- [Nibiru's documentation on intended to-be integrated tokens](https://github.com/code-423n4/2024-11-nibiru/blob/8ed91a036f664b421182e183f19f6cef1a4e28ea/README.md#erc20-token-behaviors-in-scope)
- [Weird ERC20 tokens documentation](https://github.com/d-xo/weird-erc20#balance-modifications-outside-of-transfers-rebasingairdrops)

### Recommended Mitigation Steps

Consider not supporting these type of tokens at all or instead provide a mechanism to handle balance changes in the escrow/EVM module.

**[berndartmueller (judge) decreased severity to Medium](https://github.com/code-423n4/2024-11-nibiru-findings/issues/14#issuecomment-2556580499):**

**[Unique-Divine (Nibiru) disputed and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/14#issuecomment-2565969516):**
 > This function uses the actually transferred amount by querying the ERC20 balance before and after the transfer (`actualSentAmount`). There is not a 1 to 1 assumption like the issue says. 
> 
> We already addressed this potential issue in the Zenith audit.

**[berndartmueller (judge) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/14#issuecomment-2572601665):**
 > > ```
> > Balance changes outside of transfers
> > ```
> 
> The "Balance changes outside of transfers" behavior is explicitly marked as in-scope in the audit readme. Therefore, I consider this to be a valid issue.

**[Bauchibred (warden) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/14#issuecomment-2585307984):**
 > Wouldn't this be categorised as `3` rating since there is a direct impact on assets? 

**[berndartmueller (judge) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/14#issuecomment-2585353852):**
 > @Bauchibred - no, I don't see how high severity would be justified when this is a compatibility issue with rebasing tokens. "Assets" at risk in this case would be only the rebasing token itself, so the risk is contained. 

***
