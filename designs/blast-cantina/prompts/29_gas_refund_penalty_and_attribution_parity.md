# Prompt Family: Gas Refund Penalty And Attribution Parity

## Use This For

- Refunds, rebates, discounts, penalties, access lists, intrinsic costs, and claimable gas attribution.
- Custom gas trackers or sidecar fee systems that decide which contract, user, relayer, sequencer, or protocol account earns value.
- Differences between success, revert, nested call, precompile, system call, no-code target, delegate-style call, and simulation paths.

## Prompt

```text
Hunt for gas refund, penalty, and attribution parity bugs in a blockchain or DLT codebase.

Build an attribution matrix before proposing candidates. For each relevant gas or fee path, identify:
- who pays the gas or fee
- which contract/account is charged or warmed
- which contract/account earns a refund, rebate, claimable balance, or penalty
- where residual value goes when attribution fails
- whether the path is success, top-level revert, nested revert, precompile, system call, no-code target, delegate-style call, call-code-like call, access-list-warmed call, repeated call, deposit/system transaction, simulation, trace, or replay

Search patterns:
- refund caps or net-gas scaling applied globally when the refund economically belongs to the contract that performed the refundable work
- access-list or intrinsic prepayment that warms one account/storage slot but is attributed to a protocol/global account instead of the warmed actor
- custom cold-call or frame penalties charged when the target has no code, no storage side effect, or no per-target accounting state to initialize
- delegate-style calls where execution happens in the caller's context but the penalty, refund, or claimable allocation is charged as if a normal callee-owned context were used
- precompile or system-contract calls that reuse a global fee recipient or protocol address for per-contract gas accounting
- first-call storage overhead charged again on repeated precompile/system calls because the accounting address is global or wrong
- reverted transactions or failed subcalls that still allocate claimable gas, rebates, or developer fees as if the state-changing work succeeded
- simulation, estimation, or trace paths that skip fee purchase but still mutate sidecar gas-attribution state or exercise different refund logic
- fallback behavior that silently sends all value to a base/protocol recipient when tracker accounting diverges, hiding per-contract underpayment

Questions to answer:
1. Which exact actor owns each gas dimension: base fee, priority fee, refund, rebate, custom penalty, warmed-state cost, storage-initialization cost, and claimable allocation?
2. Does a refund reduce everyone proportionally or only the actor whose refundable operation created it? Which invariant proves that choice?
3. Does access-list prepayment affect both warm/cold charging and the recipient of any custom gas allocation?
4. Are no-code targets and precompiles charged only for work that actually occurs for that target?
5. Are delegate-style calls charged in the caller context, callee context, both, or neither, and does that match the state that changes?
6. Do reverted top-level transactions and reverted inner frames allocate the same sidecar gas value as successful frames?
7. If accounting fails closed to a protocol recipient, can a user intentionally trigger that fallback to steal or deny another actor's claim?

Severity guidance:
- High if the issue enables systematic fee theft, profitable spam, unbounded underpayment, or consensus-visible gas/accounting divergence.
- Medium if it enables repeated undercharging, wrong-recipient gas claims, access-list incompatibility, or meaningful griefing.
- Low if it is only conservative overcharging or a deployment/operator policy without attacker-controlled value flow.
```
