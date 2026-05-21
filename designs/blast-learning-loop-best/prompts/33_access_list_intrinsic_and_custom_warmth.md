# Prompt Family: Access List Intrinsic And Custom Warmth

## Use This For

- EIP-2930 access lists, intrinsic gas, warm/cold access costs, storage-key prepayment, and custom gas penalties.
- Fee/rebate systems that must decide whether access-list costs belong to the global protocol account or the dapp whose address/storage is warmed.
- Compatibility paths where fixed-gas calls rely on access lists to avoid EIP-2929 cold-cost breakage.

## Prompt

```text
Hunt for access-list accounting and custom-warmth bugs.

Build a table for every transaction type that can include an access list:
- intrinsic gas charged for access-list addresses and storage keys
- warm/cold state prepared before execution
- custom gas penalties that are still charged after the warm state is prepared
- gas-tracker or rebate recipient for intrinsic access-list gas
- execution-time gas/rebate recipient for the same warmed address or storage key

Search patterns:
- access-list intrinsic gas is booked to a global/protocol account even though the warmed address/storage belongs to a dapp
- access-list prepayment warms a target for EIP-2929, but a custom cold-call/frame penalty still charges as if the target were cold or uninitialized
- fixed-gas subcalls, transfers, or compatibility paths that should be rescued by EIP-2930 still fail because custom penalties ignore access-list state
- address-list and storage-key costs have different attribution than equivalent live CALL/SLOAD costs
- simulation, estimation, and tracing disagree with live execution when access lists are present
- repeated calls to an access-list-warmed target still pay a first-use or storage-initialization surcharge

Questions to answer:
1. Where is intrinsic access-list gas computed, and which gas-tracker address receives it?
2. Which code prepares warm addresses and storage keys, and does the custom penalty predicate consult that warm state?
3. Can a user force a dapp to lose claimable fee share by moving cold-access cost into intrinsic gas?
4. Can a contract relying on fixed-gas subcalls break even when the user prepaid access-list warmth?
5. Are access-list address and storage-key costs both assigned to the actor that induced them?

Severity guidance:
- Medium if dapps lose material fee attribution or EIP-2930 compatibility is broken for reachable fixed-gas paths.
- Low if the effect is only conservative overpayment by a self-paid transaction with no compatibility or fee-recipient impact.
```
