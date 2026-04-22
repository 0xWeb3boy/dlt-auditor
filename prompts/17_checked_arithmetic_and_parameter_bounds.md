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
- "2 * threshold", "epoch + interval", and similar derived values
- constructors that cannot fail even though they build derived protocol parameters
- saturating or wrapping behavior where rejection would be safer
- test code that only exercises small values

Questions to answer:
1. Is the parameter attacker-controlled, governance-controlled, or state-derived?
2. What happens on overflow: wrap, panic, saturate, or reject?
3. Could overflow create a more permissive, permanently frozen, or mis-accounted state?
4. Should this constructor or state update be fallible?
5. Are all call sites prepared to handle invalid parameters?

Severity guidance:
- Medium by default.
- Raise only if overflow can directly bypass slashing, quorum, authorization, settlement windows, or other protocol-critical invariants.
```
