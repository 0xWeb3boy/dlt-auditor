# Prompt Family: Lido Oracle Cap Withdrawal Discount

## Use This For

- Lido large slashing, oracle cap/bunker delayed truth, local share price, pending withdrawals, and user withdrawal finalization at stale prices.

## Prompt

```text
Hunt specifically for Lido oracle-cap or delayed-report states that under-discount withdrawals.

Build a withdrawal-discount timeline:
- Lido loss/slashing becomes externally knowable
- Lido oracle cap or bunker mode delays full balance reduction
- Blast provider balance/claimable requests still appear overvalued
- user proves or queues an L2->L1 withdrawal
- YieldManager finalizes local withdrawal at current share price
- later provider report/claim realizes the full loss

Search patterns:
- share price discounts only `accumulatedNegativeYields`, not externally knowable but oracle-capped losses
- provider `totalValue` uses `LIDO.balanceOf`, pending value, or claimable value at par while Lido caps the reported loss
- `finalize` locks withdrawal amounts before all capped/delayed losses are reflected
- admin can finalize user withdrawals between public slashing and full oracle/report catch-up
- claim-batch or pending-exit findings are merged with oracle-cap delayed truth without proving the cap path

Questions to answer:
1. What value does local `sharePrice()` use before the full Lido loss is reported?
2. Can a user withdrawal be finalized during the oracle-cap/delayed-truth window?
3. Does finalization lock a nominal/par amount that should have been discounted by the externally knowable loss?
4. Are pending and claimable Lido exits swept before finalization?
5. What tests or mocks would simulate a large slash capped across multiple reports?

Severity guidance:
- Medium if withdrawals can be finalized at an overvalued share price during a large slashing/oracle-cap window.
- Low if only deposits are affected or if operational sequencing fully prevents withdrawal finalization before report catch-up.
- Informational if Lido cap state cannot make local accounting stale for the withdrawal sink.
```
