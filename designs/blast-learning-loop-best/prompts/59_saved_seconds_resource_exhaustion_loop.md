# Prompt Family: Saved Seconds Resource Exhaustion Loop

## Use This For

- Gas-maturity, gas-seconds, saved-time, claim-rate, or fee-credit mechanisms where old maturity may be reused with new gas.
- Distinguishing ordinary claim-rate policy from a repeatable capital-light resource or extraction loop.

## Prompt

```text
Hunt specifically for saved gas seconds, maturity counters, or time-weighted fee credits that can survive a balance reduction and later attach to newly accrued gas.

Do not stop at "the claim curve allows low-rate claims" or "the caller is authorized." Build the economic/resource loop:
- initial gas balance
- initial saved seconds
- claim amount
- seconds consumed
- penalty or fee-vault transfer
- remaining saved seconds
- later gas accrual required to become immediately high-rate claimable
- capital left clawbackable or at risk
- effective work per paid gas/recovered gas
- whether another user, sponsor, router, relayer, or victim can pay for the later gas

Check these paths separately:
- `claimAll`
- `claimMax`
- explicit `claim`
- min-rate helpers
- admin clawback / VOID transitions
- zero-balance or near-zero-balance carry-forward
- redeposit or new transaction gas after a low-rate claim

For every candidate, answer:
1. Can old seconds make new gas immediately mature?
2. Can the claimant reduce the balance that remains exposed to admin clawback while preserving most maturity?
3. Does the strategy create more recoverable value, lower capital at risk, or cheaper node/resource pressure than an honest one-shot claim?
4. Who pays the later gas, who can claim it, and who receives penalties?
5. Which code comment or test claims this is intentional, and why that does or does not kill the security/resource impact?

Reporting discipline:
- If the exact carry-forward mechanism exists, preserve it as a candidate even if validation later caps severity.
- If validation kills impact, include the full numeric/economic killer evidence, not only "intentional behavior."
- Do not merge this with `claimAll` split-optimum findings; saved-seconds carry-forward is a lifecycle/capital-reuse class.
```
