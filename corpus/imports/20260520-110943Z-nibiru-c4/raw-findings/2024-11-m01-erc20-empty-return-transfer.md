# Nibiru C4 M-01: ERC20 transfer fails with non-compliant tokens missing return values

- Source bundle: `report.md`
- Contest: `2024-11-nibiru`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Original severity: `Medium`
- Corpus ID: `nibiru-c4-2024-11-m01-erc20-empty-return-transfer`

---

## [[M-01] ERC20 transfer fails with non-compliant tokens missing return values](https://github.com/code-423n4/2024-11-nibiru-findings/issues/54)
*Submitted by [0x41](https://github.com/code-423n4/2024-11-nibiru-findings/issues/54), also found by [ifex445](https://github.com/code-423n4/2024-11-nibiru-findings/issues/68), [0x007](https://github.com/code-423n4/2024-11-nibiru-findings/issues/64), [Bauchibred](https://github.com/code-423n4/2024-11-nibiru-findings/issues/62), and [0xaltego](https://github.com/code-423n4/2024-11-nibiru-findings/issues/61)*

The `erc20.go` file assumes all ERC20 tokens return a boolean value from transfer operations, but some popular tokens like USDT, BNB, and OMG do not (<https://github.com/d-xo/weird-erc20>). These tokens are valid ERC20s but do not conform to the current standard of returning a boolean.

When attempting to transfer such tokens, `UnpackIntoInterface` will call `Unpack` which fails when there is no return data but a return value is expected in the ABI. This causes the transfer to fail with an error, preventing users from transferring otherwise valid tokens through the system.

As noted in the audit scope, handling of "Missing return values" is explicitly in scope for this audit.

### Proof of Concept

The issue occurs in [`erc20.go:91-95`](https://github.com/code-423n4/2024-11-nibiru/blob/84054a4f00fdfefaa8e5849c53eb66851a762319/x/evm/keeper/erc20.go#L91):

```go
var erc20Bool ERC20Bool
err = e.ABI.UnpackIntoInterface(&erc20Bool, "transfer", resp.Ret)
if err != nil {
    return balanceIncrease, nil, err
}
```

The underlying `Unpack` function in the Ethereum ABI encoding will error when attempting to unpack empty return data if the ABI specifies a return value (`go-ethereum/accounts/abi/argument.go`):

```go
func (arguments Arguments) Unpack(data []byte) ([]interface{}, error) {
    if len(data) == 0 {
        if len(arguments.NonIndexed()) != 0 {
            return nil, errors.New("abi: attempting to unmarshall an empty string while arguments are expected")
        }
        return make([]interface{}, 0), nil
    }
    return arguments.UnpackValues(data)
}
```

This prevents transfers of tokens like USDT that don't return a value, even when the transfer itself succeeds.

### Recommended mitigation steps

Modify the transfer function to consider a transfer successful if:
1. The token returns true, OR
2. The token returns no value and the transfer didn't revert.

```go
func (e erc20Calls) Transfer(
    contract, from, to gethcommon.Address, amount *big.Int,
    ctx sdk.Context,
) (balanceIncrease *big.Int, resp *evm.MsgEthereumTxResponse, err error) {
    recipientBalanceBefore, err := e.BalanceOf(contract, to, ctx)
    if err != nil {
        return balanceIncrease, nil, errors.Wrap(err, "failed to retrieve recipient balance")
    }

    resp, err = e.CallContract(ctx, e.ABI, from, &contract, true, Erc20GasLimitExecute, "transfer", to, amount)
    if err != nil {
        return balanceIncrease, nil, err
    }

    // If there's return data, try to unpack it
    if len(resp.Ret) > 0 {
        var erc20Bool ERC20Bool
        if err := e.ABI.UnpackIntoInterface(&erc20Bool, "transfer", resp.Ret); err != nil {
            return balanceIncrease, nil, err
        }
        if !erc20Bool.Value {
            return balanceIncrease, nil, fmt.Errorf("transfer executed but returned success=false")
        }
    }
    // No return data = transfer didn't revert, consider it successful

    recipientBalanceAfter, err := e.BalanceOf(contract, to, ctx)
    if err != nil {
        return balanceIncrease, nil, errors.Wrap(err, "failed to retrieve recipient balance")
    }

    balanceIncrease = new(big.Int).Sub(recipientBalanceAfter, recipientBalanceBefore)
    if balanceIncrease.Sign() <= 0 {
        return balanceIncrease, nil, fmt.Errorf(
            "amount of ERC20 tokens received MUST be positive: the balance of recipient %s would've changed by %v for token %s",
            to.Hex(), balanceIncrease.String(), contract.Hex(),
        )
    }

    return balanceIncrease, resp, nil
}
```

This makes the system compatible with both standard ERC20 tokens that return a boolean and non-standard tokens that don't return a value. The approach is similar to that used by established DeFi protocols that need to handle both types of tokens.

**[berndartmueller (judge) decreased severity to Low and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/54#issuecomment-2556574950):**
 > As seen in the [ERC-20 standard](https://eips.ethereum.org/EIPS/eip-20), the `transfer` function is expected to return a `bool`. Thus, a token like `USDT` is, strictly speaking, not an ERC-20 token.
> 
> Moreover, USDT in the same form as on ETH Mainnet will likely not exist on Nibiru. The token contract will have to be deployed there and is likely to be deployed with an ERC-20 compliant version that returns a `bool` from `transfer()`. [For example, USDT on Base does not have this flaw, it has a return value.](https://basescan.org/token/0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2#code#F1#L444)
> 
> Therefore, I'm downgrading this to QA (Low).

**[Lambda (warden) commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/54#issuecomment-2580992429):**
 > > The `transfer` function is expected to return a `bool`. Thus, a token like `USDT` is, strictly speaking, not an ERC-20 token.
> 
> @berndartmueller - while this is true, there are unfortunately many tokens that do not completely adhere to the standard. While some may change their code for a deployment on Nibiru, others may not in order to have a consistent behaviour across chains and to not introduce any code changes (if they used something like [`xdeployer`](https://github.com/pcaversaccio/xdeployer) or another `CREATE2` based factory for consistent addresses across chains, they could not even without changing the address). Of course, it is ultimately up to a project to decide if these tokens should be supported or not, which is why C4 started to ask the sponsors if they want to.
>
> On the [audit page](https://code4rena.com/audits/2024-11-nibiru), "missing return values" were explicitly marked as in scope, which was my motivation to mark it as Medium. [Issue 14](https://github.com/code-423n4/2024-11-nibiru-findings/issues/14) was also the reason this was kept as Medium; although, the total value of all rebasing tokens across all chains is probably much lower than the one of tokens with missing return values.

**[berndartmueller (judge) increased severity to Medium and commented](https://github.com/code-423n4/2024-11-nibiru-findings/issues/54#issuecomment-2585273395):**
 > For consistency across severities, especially with regards to [Issue 14](https://github.com/code-423n4/2024-11-nibiru-findings/issues/14), I'm upgrading this issue to Medium severity.

**k-yang (Nibiru) acknowledged and commented outside of Github with C4 staff:**
> Will address it on an as needed basis (i.e., when `dApps` tell us they need support for non-ERC20 compliant tokens).

***
