# Prompt Family: VM Instruction Semantics And Observer Consistency

## Use This For

- VM opcode or bytecode instruction semantics.
- System-register, flag, overflow, error, program-counter, receipt, panic, or return-data side effects.
- Interpreter vs spec mismatches.
- Cross-platform deterministic execution for VM paths.
- Gas, profiler, trace, debug, or simulation observer mismatches around instruction execution.

## Prompt

```text
Hunt for VM instruction semantics, observer, and deterministic-execution bugs in a blockchain or DLT codebase.

Focus on VM/interpreter/precompile/host-function code where small semantic differences become protocol behavior:
- opcode dispatch tables,
- ALU and wide-integer helpers,
- memory copy, clear, load, grow, and ownership helpers,
- code, contract, module, proof, or artifact loading instructions,
- gas charge helpers,
- system registers, flags, error registers, overflow registers, program-counter changes,
- receipts, logs, panic/revert reasons, return bytes, and execution result data,
- profiler, trace, debug, coverage, simulation, and estimate paths.

Start with an instruction side-effect matrix. For each relevant instruction family, record:
- source operands and whether they are direct or indirect,
- destination register or memory writes,
- system registers written or cleared,
- flags, error, overflow, or status registers written or cleared,
- spec or test evidence for expected status-register behavior, including sibling-opcode behavior when external specs are unavailable,
- program-counter behavior,
- memory/state/storage side effects,
- receipt/log/panic/revert/result outputs,
- gas charged before execution and dependent gas charged during execution,
- observer/profiler/trace events,
- existing tests and spec references if present.
- changelog, release-note, or regression-test entries that mention changed instruction behavior, gas charging, profiling, host-width conversion, or panic/error behavior.

Required VM sub-matrices:
- For every wide integer compare opcode, create one row per opcode. In Fuel-like VMs this means rows for names such as `WDCM` and `WQCM`, separate from wide integer arithmetic rows. The row must name the dispatch arm, the helper called, the helper arguments, and whether that exact helper takes and writes the error and overflow/status registers.
- For every contract/code load or copy opcode, create one row per opcode. In Fuel-like VMs this means rows for names such as `LDC`, `CCP`, and related code-copy/load helpers, separate from generic memory helpers.
- For each row, state whether the issue is `current-live`, `fixed-by-current-head`, `regression-risk`, or `unclear`.

Search patterns:
- related opcodes that should share flag/error/overflow clearing but one helper only updates the destination or PC;
- compare, arithmetic, conversion, copy, clear, load, and hash operations that leave stale status registers observable by later instructions;
- instruction helpers that call a common ALU function but bypass the cleanup performed by other operations in the same family;
- panic/revert/error reasons derived from host-specific conversion, allocation, or platform width;
- code paths where both outcomes are failures but the specific failure value is consensus-visible;
- `usize`, pointer-width, target-architecture, wasm/no-std/std, alloc, serde, debug, profile, or backend-feature differences inside instruction execution;
- gas/profiler helpers where fixed-cost and dependent-cost paths record cost at different times relative to deduction;
- profiling or tracing that caps against remaining gas after gas has been deducted;
- profiler/observer paths where successful dependent charges and failing dependent charges observe different pre-state/post-state values than fixed charges;
- simulation/debug/trace execution that reuses instruction helpers but suppresses, moves, or duplicates side effects differently than live execution;
- copy/load/clear instructions where the bytes charged differ from bytes fetched, bytes copied, bytes written, or bytes zero/default-filled;
- storage-backed code or artifact loading where a full object is fetched before charging based on size metadata.
- wide compare helpers whose arithmetic siblings clear or write status registers, while the compare helper only writes the destination or returns a comparison value.
- spec tests, Rust tests, doc comments, or sibling-opcode tests that mention compare opcodes, `$err`, `$of`, overflow, error, status, or flag behavior.
- contract/code load paths where a VM word or requested byte length is padded, narrowed through `usize`, allocated, or compared to max object size in different orders across host widths.

For copy, clear, load, and fill instructions, build a size/effect matrix:
- object bytes fetched from storage or backend,
- source bytes read after offset handling,
- destination bytes written,
- bytes zero-filled or default-filled,
- bytes used for memory ownership/range checks,
- bytes used for dependent gas or fee charging,
- behavior when source offset is beyond source length,
- current status if a changelog or patch note says the charge basis changed.
- charge basis before and after the patch if local changelog, release notes, regression tests, or current fix shape indicate that the charge basis changed.
- whether the billed size must be the source length, requested length, fetched object length, destination write length, zero-fill length, or a maximum across several of those dimensions.

For wide integer compare/status instructions, build a per-opcode status matrix:
- opcode mnemonic and dispatch location,
- helper function and helper arguments,
- destination value written,
- exact `$err`, `$of`, flag, or status-register writes performed by that helper,
- sibling opcode behavior in the same instruction family,
- local spec/test/comment evidence for expected clearing or preservation,
- whether a later instruction or contract code can read stale status,
- reason a candidate was promoted or killed.

Do not conclude "ALU helpers manage status registers" at family level unless the analysis shows the exact helper for every opcode being claimed takes and writes those status registers. Wide arithmetic helpers and wide compare helpers must be checked separately.

For host-width contract/code load determinism, build an opcode-specific table:
- opcode and helper path, especially contract/code load paths,
- input length, offset, and source object size,
- padding or alignment helper used,
- conversion to `usize`, allocation size, or target pointer width,
- semantic max-size or contract-size check and whether it happens before or after narrowing,
- modeled 32-bit output/error class,
- modeled 64-bit output/error class,
- consensus-visible result, receipt, panic/revert reason, gas use, or return data affected.

If changelog wording mentions avoiding `usize` conversion, different errors on 32-bit targets, changed panic/error behavior, or max-size checking for code load/copy, create a patch-derived candidate with the exact opcode, conversion, and result-class effect. Do not collapse it into a broad "memory host-width" note.

For load-code length host-width fixes, model requested length separately from offset and destination address. A valid row names the old length narrowing/padding order, the current length padding/max-size order, and the two failure classes a narrow and wide host would have produced before the fix. If the exact source diff is unavailable, infer from changelog wording plus current fix shape, and label the uncertainty rather than dropping the candidate.

For profiler, trace, coverage, metrics, and simulation observers, build both a success ledger and a failure ledger:
- cost requested,
- pre-charge context/global budget,
- post-charge context/global budget,
- value observed by the profiler/trace,
- cap applied by the observer,
- whether fixed and dependent charge helpers observe the same state.

For profiler patch archaeology, also record:
- changelog or test evidence that the profiler observation point changed,
- old inferred observer position relative to gas deduction,
- current observer position relative to gas deduction,
- whether the issue is diagnostic-only, pricing/governance/operator-safety relevant, or consensus-visible,
- final current status: `fixed-by-current-head` or `regression-risk`.

Questions to answer:
1. What exact side effects does the protocol/spec require for this instruction family?
2. Which helper actually writes each destination, system register, flag, error, overflow state, PC, receipt, memory region, and storage slot?
3. Do sibling opcodes or modes disagree about clearing or preserving status registers?
4. Are status registers read by later instructions, contracts, receipts, or host APIs?
5. Can the same invalid input produce different consensus-visible errors across host targets or feature sets?
6. Does the code charge before every expensive piece of work, including full object loads and zero/default-filled writes?
7. Does observer/profiler/trace output match the authoritative charged amount and execution state?
8. Is the issue live in normal execution, only simulation/debug/profile builds, or only unsupported targets?
9. What existing tests assert the relevant side effects, and what side-effect row is untested?

Validation guidance:
- Do not report a spec mismatch unless the expected side effect is supported by a local spec, tests, naming, sibling-opcode behavior, or protocol invariant.
- If local tests, sibling helpers, or protocol invariants support the expected side effect, do not reject solely because an external spec is unavailable in blind scope. Report it as conditional and state the missing spec check.
- Do not reject a reachable VM status-register mismatch solely because no deployed contract or compiler pattern was found. User-observable smart-contract behavior is a valid impact class when the opcode effect is consensus-visible.
- Do not reject a status-register mismatch by citing sibling arithmetic behavior unless the exact compare/load/copy opcode helper was checked. If sibling tests or local specs imply clearing and the current opcode leaves stale values, promote at least a conditional VM semantics finding.
- Do not report host-width differences unless the differing value can reach consensus-visible state, receipts, gas, result data, or block/result hashes.
- Do not reject host-width divergence just because both platforms fail. If the failure class, panic/revert reason, result bytes, gas, receipt, or serialized execution output differs, model it as consensus-visible unless the code proves the value is hidden below the protocol boundary.
- Do not report profiler/trace issues as high impact unless the observer feeds pricing, governance, operator safety, user fees, or consensus-visible behavior.
- Do not reject concrete profiler/trace patch-derived fixes solely because they are not high impact. Keep them as Insight/Informational fixed mechanisms when the missing observer timing property and current fix shape are concrete.
- Do not kill profiler issues by checking only out-of-gas behavior; successful high-cost dependent charges must also be compared against fixed charge profiling.
- Record killed ideas with enough detail to avoid repeating the same opcode walk.

Severity guidance:
- Medium by default for user-observable VM semantic mismatches, consensus-visible error divergence, or meaningful fee/accounting observer bugs.
- Raise only when the mismatch can split consensus, bypass authorization, undercharge significant execution, corrupt finalized state, or create a strong chain-wide DoS.
- Low or informational for debug-only, unsupported-target, or purely diagnostic observer issues.
```
