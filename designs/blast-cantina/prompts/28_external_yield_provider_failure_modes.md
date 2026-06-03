# Prompt Family: External Yield Provider Failure Modes

## Use This For

- Integrations with external yield providers, vaults, staking systems, oracles, insurance funds, and recovery managers.
- Pending deposits/withdrawals, caps, maturity counters, paused providers, emergency shutdown, and ownership recovery.
- Value accounting that depends on third-party state or delayed settlement.

## Prompt

```text
Hunt for external-yield-provider failure modes in a blockchain or DLT codebase.

Focus on code that deposits into, withdraws from, accounts for, caps, insures, pauses, migrates, or recovers funds from external yield, staking, vault, strategy, bridge, oracle, or custodian providers.

Search patterns:
- pending deposits or withdrawals omitted from caps, solvency checks, share price, claimable amount, maturity counters, or recovery calculations
- accrued seconds, maturity counters, reward indices, share rates, or exchange rates reset or restored asymmetrically across revert, claim, withdrawal, pause, or provider-switch paths
- oracle caps, rate limits, provider balances, or insurance coverage checked at request time but not settlement time
- emergency shutdown, pause, migration, or recovery paths that can be entered while pending operations still depend on the old provider's state
- owner, guardian, strategy, vault, provider, or recipient recovery roles that can redirect funds, claim dust, or finalize withdrawals without the same accounting constraints as normal users
- failed external calls, partial fills, asynchronous withdrawals, slashing, negative yield, delayed receipts, or provider insolvency treated as zero-yield success
- accounting that compares internal principal to provider shares or receipts without modeling rounding, exchange-rate movement, fees, queued exits, or paused withdrawals
- insurance or backstop funds released before the provider loss is finalized, before all pending users are accounted for, or before ownership of recovered assets is fixed
- migrations that move current balances but not pending claims, reward indices, durable flags, historical snapshots, or per-user eligibility state
- external provider state read through a local cache, oracle, indexer, or static config without verifying the live provider state at the settlement sink

Questions to answer:
1. Which balances are immediate, pending, accrued, insured, queued, or externally recoverable?
2. Is every user-visible claim computed after pending provider operations and final settlement state are known?
3. Are caps and oracle limits enforced both when a request is opened and when it settles?
4. What happens if the provider pauses, reverts, slashes, delays, returns less than requested, or changes exchange rate between request and settlement?
5. Can emergency shutdown, migration, or recovery change ownership or accounting of pending assets?
6. Are per-user maturity, eligibility, and reward-index fields restored or advanced consistently on success, revert, claim, and rollback?
7. Does the integration distinguish provider operational risk from protocol-accounting risk, and does it fail closed at protocol boundaries?

Severity guidance:
- High if users can claim more than their entitlement, lose protected principal through protocol accounting, or an untrusted actor can seize recovered/provider assets.
- Medium if pending operations can be mis-accounted, withdrawals can be blocked or underfunded, or provider failure can leak value between users.
- Low if the issue is a known third-party insolvency risk with clear protocol accounting and recovery ownership.
```
