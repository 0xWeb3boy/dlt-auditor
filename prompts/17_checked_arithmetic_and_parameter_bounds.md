# Prompt Family: Checked Arithmetic And Parameter Bounds

## Use This For

- Integer overflow or underflow in security-sensitive derived parameters.
- Arithmetic on epochs, freeze intervals, thresholds, or committee sizes.
- Silent wraparound in protocol-state or economic logic.

## Prompt

```text
Hunt for arithmetic bugs in a blockchain or DLT codebase where protocol parameters are combined to derive security-sensitive values.

Focus on:
- epoch arithmetic
- freeze windows
- thresholds and quorum math
- committee sizes and limits
- bridge limits, validator-set math, signer-set thresholds, and proof window derivation
- conversions between integer widths

Search patterns:
- raw +, -, *, or casts on u8/u16/u32/u64 values that come from config, consensus params, governance params, or protocol state
- raw arithmetic on protocol coordinates received from peers, validators, or RPC callers, such as heights, checkpoints, epochs, rounds, locator intervals, response counts, and range endpoints, even when production values are expected to stay far below numeric limits
- "2 * threshold", "epoch + interval", and similar derived values
- interval membership checks such as `start <= x < start + interval` where `start + interval` can wrap, saturate into an over-broad range, or panic before rejecting impossible boundary values
- constructors that cannot fail even though they build derived protocol parameters
- saturating or wrapping behavior where rejection would be safer
- test code that only exercises small values
- consensus-significant numeric fields parsed as arbitrary precision, RLP integers, decimal strings, or big integers and then narrowed to fixed-width types before checking canonical representability
- block numbers, timestamps, epochs, milestone numbers, fork heights, and confirmation offsets where adding, subtracting, or converting across signed and unsigned widths can turn invalid future, past, or impossible values into plausible local state
- fixed-point, decimal, AMM, lending, vault, interest, yield, reserve, or fee calculations where rounding direction itself is a security invariant. Compare the exact mathematical target, rounded ledger amount, remainder handling, and stored aggregate field
- numeric wrapper types that distinguish validity, canonicality, and representability under the active protocol rules. Valid-but-unrepresentable intermediate values must not reach persisted state fields
- threshold arithmetic for validator quorums, amendment or fork activation, voting windows, signer-set policy, or trust-list policy. Test boundary values just below and above the required fraction, especially with small signer sets
- fallible conversion helpers that return `(value, error)` or equivalent status but are used inline as arguments to staking, reserve, balance, delegation, validator-weight, or accounting mutators. The conversion result should be checked before any state-changing sink observes the narrowed or unit-converted value.
- reconstructed protocol accounting values built from persisted base values plus accrued, deferred, pending, or reward metadata. If the derived value is installed into validator weight, voting power, stake, reserves, supply, fees, or quotas, use checked arithmetic and reject unrepresentable sums before updating state.

Questions to answer:
1. Is the parameter attacker-controlled, governance-controlled, or state-derived?
2. What happens on overflow: wrap, panic, saturate, or reject?
3. Could overflow create a more permissive, permanently frozen, or mis-accounted state?
4. Should this constructor or state update be fallible?
5. Are all call sites prepared to handle invalid parameters?
6. Is the code checking representability and canonical encoding before narrowing or comparing, and do sanity checks enforce the same width as consensus verification?
7. Is rounding direction specified by the protocol, and who receives or loses any remainder?
8. Are threshold calculations achievable, monotonic, and safe at small set sizes and exact boundary fractions?
9. If arithmetic is used only to validate untrusted protocol structure, would checked arithmetic or a subtraction/comparison form fail closed at the numeric boundary?

Severity guidance:
- Medium by default.
- Raise only if overflow can directly bypass slashing, quorum, authorization, settlement windows, or other protocol-critical invariants.
```
