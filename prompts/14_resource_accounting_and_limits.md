# Prompt Family: Resource Accounting And Limits

## Use This For

- Missing gas charging.
- Simulation paths that skip metering.
- Weight or queue limits enforced on the wrong representation.
- Mempool, scheduler, or batching resource-limit mismatches.
- Consensus safety floors not enforced during election or admission.

## Prompt

```text
Hunt for resource-accounting bugs in a blockchain or DLT codebase.

Focus on code that performs expensive work before charging gas or fees, before applying quotas or weight limits, or before queue admission can fail cleanly.

Prioritize:
- mempool, txpool, scheduler, or block-builder code
- admission and execution handlers
- simulation or estimation flows
- bridge or batch processing handlers
- quota, rate-limit, and spam-protection code

Search patterns:
- handlers that start with state reads, runtime lookups, proof parsing, or validation before UseGas or an equivalent charge
- simulation checks placed before charging
- admission checks done on raw transaction size instead of checked transaction weight, byte cost, proof cost, or resource units
- queue insertion that can fail after validation but without mapping failure back to the originating tx
- minimum or threshold parameters validated in one place but not enforced where the decision is made

Questions to answer:
1. What resource is the protocol trying to meter: gas, fees, bytes, weight, queue slots, proving budget, bridge capacity, committee size, or sender concurrency?
2. When is it charged or enforced?
3. Is there a path that performs meaningful work before that point?
4. Does simulation use the same accounting path as live execution?
5. Are errors propagated back to the correct transaction and caller?

Severity guidance:
- Medium by default for DoS, fee bypass, and resource exhaustion.
- Raise only if the missing limit can destabilize consensus, settlement, bridge processing, or systematically underprice privileged operations.
```
