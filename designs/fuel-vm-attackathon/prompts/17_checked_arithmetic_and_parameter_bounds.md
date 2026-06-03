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

For consensus-visible VM, parser, proof, receipt, panic, or execution-result paths, build a host-width determinism table:
- opcode, helper, parser, or public API name,
- original input type and width,
- narrowed type and width,
- whether conversion uses `usize`, pointer width, target architecture, host allocation size, or platform-specific collection behavior,
- whether conversion rejects, saturates, panics, wraps, or maps into a protocol error,
- the exact modeled 32-bit output and exact modeled 64-bit output, including panic/revert/error class when both outcomes are failures,
- whether semantic checks happen before or after narrowing, padding, allocation, or size comparison,
- whether the resulting error, receipt, gas use, return data, or panic/revert reason is consensus-visible,
- whether 32-bit, 64-bit, wasm, no-std, std, alloc, or feature-gated builds can differ.

Flag any path where the same protocol input can produce different consensus-visible outputs across supported targets, even if both outputs are errors. A different panic/revert reason, receipt, result-code byte, gas charge, state root, or returned error payload can be a consensus issue when it enters block/result hashing or state transition output.

Search specifically for:
- `usize`, `isize`, pointer-width casts, and `try_into::<usize>()` on protocol lengths or offsets,
- length padding helpers that accept platform-width inputs, including helpers named like padded length, aligned length, word length, or serialized length,
- contract/code/module/artifact load and copy paths that convert a VM `Word`, serialized length, offset, or requested byte count before checking max object size,
- allocation or vector-capacity errors mapped into protocol errors,
- feature-gated implementations of the same cryptographic, VM, parser, or arithmetic operation,
- tests that simulate only the host running the audit but not alternate supported targets.

For VM contract/code loading, do not stop at generic memory helpers. Search and model opcode-specific paths with names like:
- `LDC`, `load_contract_code`, contract code load, code copy, and contract copy dispatch;
- `padded_len`, `padded_len_usize`, padded length, aligned length, qword length, word length, and unpadded length helpers;
- `length_unpadded`, `contract_max_size`, max contract size, max code size, `usize`, `try_into`, allocation, and vector length conversion;
- protocol error classes and panic/revert/result mapping around memory overflow, contract/code size, and allocation failure.

For every changelog, release note, regression test, or code comment that says a `usize` conversion was avoided, a 32-bit system returned different errors, or an error class changed near a VM load/copy path, create an opcode-specific host-width determinism table. The table must contain:
- exact opcode/helper name,
- original attacker-controlled length/offset/source size,
- pre-fix conversion or padding order inferred from the patch trail,
- 32-bit modeled result/error class,
- 64-bit modeled result/error class,
- whether the differing result is included in VM receipts, panic/revert output, execution result data, gas use, or state transition output,
- current status: `current-live`, `fixed-by-current-head`, `regression-risk`, or `unclear`.

For contract-code load opcodes, the host-width pass is incomplete unless it separately models the requested length path. In Fuel-like VMs, create a dedicated LDC/load-contract-code row with:
- requested unpadded length operand,
- old narrowing point if local patch evidence suggests the length went through `usize` or another host-width type,
- padding/alignment helper before and after the fix,
- semantic contract/code max-size check before and after the fix,
- narrow-host failure class when the requested length cannot be represented before semantic checks,
- wide-host failure class when the same requested length reaches semantic max-size checks,
- whether that difference is visible in a VM panic/revert/result receipt.

Do not satisfy a changed-error host-width patch with only generic rows for memory addresses, offsets, stack/heap pointers, or `ToAddr`. A code-load length-padding regression must be its own candidate or an explicit rejected idea with the missing proof named.

Do not downgrade an opcode-specific host-width result divergence into a generic "memory allocation is platform dependent" note. If the path is fixed in current `HEAD`, preserve the missing property as a patch-derived regression candidate when local patch evidence is concrete.

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
10. Could two supported host targets reject the same protocol input with different consensus-visible result bytes, receipts, panic reasons, or gas usage?
11. Are all platform-width or feature-gated differences below the consensus boundary, or do they reach state, receipts, result hashes, or serialized execution output?
12. Did the scan enumerate every VM opcode or parser path that narrows protocol-controlled lengths, or only the generic memory helpers? If only generic helpers were checked, the host-width pass is incomplete.
13. For each code-load or code-copy opcode, what exact error class does the same over-large or padded length produce on 32-bit and 64-bit hosts, and does that class cross the consensus boundary?
14. Did any host-width candidate get merged into a generic memory/index dossier despite evidence that the changed error came from a load opcode's length-padding/max-size order? If yes, split it before canonicalization.

Severity guidance:
- Medium by default.
- Raise only if overflow can directly bypass slashing, quorum, authorization, settlement windows, or other protocol-critical invariants.
```
