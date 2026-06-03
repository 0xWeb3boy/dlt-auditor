# Prompt Family: High Frame Precompile Surcharge Exact

## Use This For

- Blast custom high-frame call surcharge, `BlastGasParamStorageGas`, precompile/system-call targets, gas tracker attribution, and repeated precompile calls.

## Prompt

```text
Hunt specifically for repeated custom surcharge on precompile targets.

Do not merge this with native-precompile selector RequiredGas or general precompile fee attribution.

Build a call-class table:
- CALL, STATICCALL, DELEGATECALL, and CALLCODE to ordinary code
- CALL, STATICCALL, DELEGATECALL, and CALLCODE to no-code/EOA targets
- CALL, STATICCALL, DELEGATECALL, and CALLCODE to standard EVM precompiles
- CALL, STATICCALL, DELEGATECALL, and CALLCODE to Blast native precompiles
- first call versus repeated call after the high-frame threshold
- cold, warm, and access-list-warmed target states

For each precompile case, compare:
- the address used by the custom surcharge predicate
- the address receiving execution/precompile gas attribution
- whether `GetGasUsedByContract(target)` can remain zero after the first precompile call
- whether `BlastGasParamStorageGas` is charged again on repeated calls
- whether any target gas-parameter storage update is actually performed for a precompile

Search patterns:
- the surcharge checks target allocation, but precompile execution gas is recorded under a global/system address
- repeated precompile calls after `BlastMaxFrameCount` pay the storage surcharge every time because the precompile target never receives gas allocation
- standard precompiles and Blast native precompile share the wrapper but differ in `RequiredGas`, revert, and attribution semantics
- a warm/access-listed precompile still pays a custom storage surcharge unrelated to EIP-2929 warmth

Questions to answer:
1. Does a precompile target ever receive per-target gas allocation that suppresses the high-frame storage surcharge?
2. Is the same target called repeatedly in one transaction charged `BlastGasParamStorageGas` more than once?
3. Is the charged storage work real, or is no target gas-param storage updated for precompiles?
4. Are standard precompiles and Blast native precompile both affected?
5. Is the impact overcharge, gas-limit incompatibility, fee-recipient shift, or all of these?

Severity guidance:
- Medium if repeated precompile calls can pay an unnecessary custom storage surcharge or create gas-limit compatibility failures.
- Low if only first-use surcharge is charged once or precompile targets intentionally receive matching gas-param writes.
- Informational if precompile gas attribution fully suppresses the target-keyed predicate.
```
