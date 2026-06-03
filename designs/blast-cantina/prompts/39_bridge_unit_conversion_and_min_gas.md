# Prompt Family: Bridge Unit Conversion And Min Gas

## Use This For

- Direct bridge deposits, asset-specific bridge branches, decimals conversion, native/token unit mismatches, non-replayable deposits, and minimum gas budgets.
- Cases where one bridge path bypasses messenger helpers and must duplicate replay, gas, value, and unit handling correctly.

## Prompt

```text
Hunt for bridge unit-conversion and minimum-gas bugs.

For each deposit, withdrawal, retry, direct portal call, finalizer, and bridge helper, build a per-path table:
- user requested amount and token decimals
- escrowed/burned amount
- provider principal amount
- portal mint/value amount
- calldata amount to the remote finalizer
- emitted event amount
- received/delivered amount
- requested min gas
- actual gas reaching the user-visible sink after wrapper overhead, EIP-150, reserve gas, finalizer checks, events, and post-call storage writes
- replay/retry behavior if the finalizer reverts or runs out of gas

Search patterns:
- raw token units are used for portal value/principal while the remote finalizer receives an 18-decimal converted value
- direct deposit paths copy messenger gas semantics but omit messenger `baseGas` or equivalent overhead
- `_minGasLimit` is treated as total deposit gas even though users expect that much gas at the final target or recipient
- a finalizer performs checks, emits events, forwards value, or writes accounting before forwarding gas, making the true recipient budget smaller
- non-replayable direct deposits can pass the portal minimum but fail inside the L2 finalizer
- discounts, fees, or rounding occur before conversion on one path and after conversion on an equivalent path

Questions to answer:
1. Which amount is authoritative at each sink, and are all sink amounts in the same unit?
2. Do non-18-decimal assets receive exactly equivalent value and principal on both domains?
3. Is `_minGasLimit` increased by all relay/finalizer overhead before the user sink is called?
4. If finalization fails, is there replay, retry, refund, escrow, or governance-only recovery?
5. Do direct and messenger paths have the same safety margin and failure semantics?

Severity guidance:
- High if user funds can be permanently stuck, under-minted, over-minted, or delivered in wrong units.
- Medium if finalization/retry safety is broken only for specific gas/rounding/unit cases.
- Low if the issue is a conservative overpayment or operator-only recovery nuisance.
```
