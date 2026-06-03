# Prompt Family: Native Bookkeeping Overhead Budget

## Use This For

- Broad native yield/gas/refund overhead that does not fit one exact selector, surcharge, or recipient bug.
- Client-side resource accounting for StateDB native fields, share counters, gas-tracker maps, journals, post-transaction loops, and predeploy storage updates.

## Prompt

```text
Hunt for broad under-metering of protocol-specific native bookkeeping overhead.

Create an overhead budget table with one row per attacker-controlled operation:
- operation and entry point
- attacker-controlled scaling dimension
- native reads/writes
- journal entries and rollback data
- share-count/account-flag updates
- gas-tracker map mutations
- predeploy storage reads/writes
- post-transaction loops/finalizers
- standard gas charged
- custom Blast surcharge charged
- refunds/rebates that reduce effective cost
- reason current gas is or is not proportional to the extra work

Search patterns:
- ordinary ETH/native-yield balance changes update extra account fields or share counters without extra gas
- claimable gas/refund bookkeeping writes predeploy state after execution using transaction-level data but without proportional gas
- the first few unique touched contracts avoid custom surcharge while still creating post-transaction allocation work
- refunds/rebates make effective gas too low for the state writes and native accounting triggered
- failed/reverted paths keep gas-tracker work or journals while ordinary EVM state is reverted
- broad overhead is rejected because no single sink is catastrophic, even though the combined attacker-controlled overhead is a protocol resource issue

Questions to answer:
1. What extra work does Blast do beyond ordinary EVM execution for this transaction shape?
2. Which part of that work scales with user-controlled calls, transfers, claim modes, access lists, refunds, or touched contracts?
3. Is that work charged by standard gas, selector `RequiredGas`, high-frame surcharge, intrinsic gas, or not at all?
4. Can refunds/rebates reduce the effective cost below the resource overhead?
5. Is the impact block resource exhaustion, client CPU/storage overhead, fee undercharge, or wrong-recipient accounting?

Candidate selection rule:
- Promote at least one broad native-bookkeeping-overhead candidate if the table shows attacker-controlled native work whose proportional metering is uncertain. It may be Low/Medium or hardening, but do not drop it silently in favor of only exact precompile/surcharge findings.

Severity guidance:
- Medium if attackers can repeatedly trigger meaningful unmetered or under-metered native bookkeeping at block scale.
- Low if the overhead is bounded or mostly compensated but lacks explicit tests/invariants.
- Informational if every row is fully covered by existing gas or custom surcharges.
```
