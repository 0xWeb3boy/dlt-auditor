# Prompt Family: Signed Arithmetic And Control Loop Panic

## Use This For

- Gas-price algorithms, fee-market controllers, PID-style feedback loops, difficulty/target updates, moving averages, and dynamic resource pricing.
- Signed arithmetic, absolute values, negation, min/max clamps, percent caps, and persisted parameter validation.
- Panics or silent fallback from invalid control-loop state.

## Prompt

```text
Hunt for signed arithmetic bugs in control loops and dynamic protocol parameters.

Focus on:
- proportional/derivative/integral components
- gas-price, fee-price, congestion, block-utilization, DA-cost, difficulty, reward, and moving-average algorithms
- persisted metadata loaded from storage
- operator, governance, genesis, or migration parameters
- calculations that produce signed deltas and then clamp or convert to unsigned values

Search patterns:
- `abs`, unary minus, negation, or absolute-difference logic on signed integers
- adding two signed terms before `abs`, percent cap, clamp, or unsigned conversion
- the signed minimum value, where negation or absolute value can overflow or panic
- `checked_add` without `checked_abs`, or checked multiplication followed by unchecked negation
- division by zero that falls back to zero/old value instead of rejecting invalid state
- saturating arithmetic that turns impossible values into plausible prices, limits, or progress
- constructors that accept invalid windows, factors, capacities, or averages and rely on later arithmetic to cope
- persisted metadata or snapshots that bypass the validated constructor used at startup
- test/fuzz-only algorithms that may become production-wired later without parameter validation
- public library/crate algorithms that are in the audited product scope even if the primary node service currently uses a different implementation
- control loops where negative factors or costs are meaningful in type but nonsensical in protocol

Questions to answer:
1. Which parameters are signed, and can they be negative through config, storage, governance, migration, or corruption?
2. Can independently valid signed terms sum to the minimum signed value?
3. Does the code call `abs`, negate, or narrow after that sum?
4. Is the panic caught and converted to an error, or can it halt a service/node?
5. Are invalid persisted parameters rejected before arithmetic, or silently handled with saturation/fallback?
6. Is the algorithm wired into production, gated, dormant, or test-only? What would make it active?
7. Do tests include signed minimum, maximum, zero divisor, negative factors, and large-cost cases?
8. Is the algorithm exposed as a public crate, library API, feature-gated component, migration path, or documented extension point?
9. If the exact panic is found but current service wiring is dormant, should the final report keep it as a library/dormant finding with lower severity rather than rejecting it?

Candidate retention rules:
- Keep exact signed-minimum, unchecked-negation, or zero-divisor panics when the audited scope includes the library or feature, even if current default service wiring is dormant. Label reachability precisely as production-wired, feature-gated, library-exposed, migration-only, operator-only, or test-only.
- Reject only when the code is outside audited scope or the signed extrema cannot be reached under any constructor, parser, storage, or API path.
- Do not inflate dormant/library bugs into production node compromise; preserve them as Insight/Low unless activation or attacker control is demonstrated.

Severity guidance:
- Insight or Low when the code is dormant or operator-only.
- Medium when a reachable service panic can halt processing, fee updates, block production, or transaction admission.
```
