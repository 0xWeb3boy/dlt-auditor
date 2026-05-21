# Prompt Family: Fee Vault Protocol Discount And DA Fees

## Use This For

- Protocol-owned gas/fee vaults, base-fee and L1-fee recipients, VOID-mode gas buckets, negative-yield discounts, rounded withdrawals, DA fee accounting, and permissionless vault withdrawals.

## Prompt

```text
Hunt for protocol-owned fee discount and data-availability fee-accounting bugs.

Build an owner/value table for every fee recipient and vault:
- fee source: base fee, priority fee, L1 data fee, sequencer fee, protocol gas, VOID-mode gas, unallocated penalty, or refund remainder
- on-chain owner address and withdrawal recipient
- yield mode or discount exposure
- who can trigger withdrawal
- whether withdrawal goes through the same discounted queue as user funds
- whether the fee is meant to cover a fixed external cost such as L1 calldata

Search patterns:
- permissionless `withdraw` lets anyone force protocol-owned fees through a negative-yield discounted withdrawal at a bad time
- fee vaults or protocol recipients are in VOID/non-yielding mode but still bear negative-yield withdrawal discounts
- L1 data fees are charged on L2 using nominal values while L1 settlement receives discounted or rounded value
- protocol fee recipients are assumed safe because users cannot steal them, but a user can force timing or accounting losses
- discounted bridge/withdrawal paths change the relation between L2 charged DA fee and L1 fee recovery
- base-fee or L1-fee recipient accounting is mixed with claimable developer gas in a way that changes who absorbs discounts

Questions to answer:
1. Which party owns each fee bucket, and what external obligation is it meant to cover?
2. Can an untrusted user trigger withdrawal or finalization timing for protocol-owned funds?
3. Can a negative yield, rounded claim, or discount reduce protocol recovery below nominal fees collected?
4. Does any L1 data-fee formula assume the withdrawal or fee-vault amount is undiscounted?
5. Are protocol-owned and user-owned withdrawal paths reviewed separately?

Severity guidance:
- Medium if users can force meaningful protocol fee loss, under-recover L1 costs, or shift discount burden to protocol-owned vaults.
- Low if only authorized operators can choose timing or the effect is purely accounting display.
- Informational if protocol fees never cross the discounted/rounded withdrawal path.
```
