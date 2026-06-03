# Prompt Family: Custom Bookkeeping Overhead Metering

## Use This For

- Native yield, gas refund, claimable gas, predeploy updates, journal entries, end-of-transaction accounting, system calls, and any protocol-specific state writes not represented by ordinary EVM gas.

## Prompt

```text
Hunt for broad under-metering where custom protocol bookkeeping consumes resources or writes state without proportional gas.

Build a table of custom bookkeeping operations:
- operation name and trigger
- state reads/writes, journal entries, logs, system calls, and map mutations
- whether the work happens inside ordinary EVM gas, native code, transaction finalization, or replay/bridge wrapper code
- whether the transaction sender pays gas proportional to the work
- whether refunds, rebates, or claimable gas can offset the cost
- whether failed/reverted paths still perform the work

Search patterns:
- native yield or gas-accounting state updates add storage writes after EVM execution without enough charged gas
- per-contract gas/rebate allocation loops scale with touched contracts, access-list entries, frames, precompile calls, or refund entries but are charged as a constant
- StateDB journals, rollback data, gas trackers, or predeploy writes grow with attacker-controlled call graphs
- post-transaction allocation or claimable-gas updates are not represented in intrinsic gas, dynamic gas, or custom surcharge formulas
- a refunded or rebated transaction can cause more client work than the final net paid gas should permit
- system-contract or precompile paths perform native bookkeeping outside the metered interpreter path

Questions to answer:
1. Which custom work is performed after or outside the ordinary gas meter?
2. What attacker-controlled dimension makes that work scale?
3. Does the custom surcharge or intrinsic gas include all added reads, writes, journals, and finalization loops?
4. Can refunds/rebates make the net cost too low for the resources consumed?
5. Is the impact wrong-recipient accounting, fee undercharge, block resource exhaustion, or only implementation inefficiency?

Severity guidance:
- Medium if attacker-controlled transactions can repeatedly consume meaningful unmetered state/client resources or underpay protocol bookkeeping.
- Low if the overhead is bounded, operator-only, or already conservatively overcharged.
- Informational if the work is fully included in standard gas or cannot be attacker-amplified.
```
