# Prompt Family: Memory Contract And Buffer Ownership

## Use This For

- Caller/callee span or buffer-size mismatches.
- Fixed-capacity receive buffers that never reject oversized protocol objects.
- Copy-back or post-execution memcpy paths that trust attacker-shaped lengths.
- Stack-local metadata or borrowed handles that outlive their intended scope.
- Parser, VM, crypto, or networking helpers with stronger documented contracts than their call sites enforce.

## Prompt

```text
Hunt for memory-contract and buffer-ownership bugs in a blockchain or DLT codebase.

Focus on parser, runtime, VM, cryptographic, and networking helpers where safety depends on exact backing-span size, output-buffer size, destination-length equality, or ownership lifetime.

Prioritize:
- packet, frame, stream, and message parsing
- syscall, precompile, VM, and host-function boundaries
- cryptographic decode, transcript, and proof helpers
- copy-in, copy-out, serialization, and persistence boundaries
- async, callback-driven, nested, or deferred execution paths

Search patterns:
- callers that pass a typed object, struct, or small stack local where the callee contract really expects a maximum-sized byte buffer or backing span
- parser APIs that require one extra sentinel, terminator, or trailing byte beyond the logical payload length
- memcpy, memmove, copy-back, or return-data propagation that uses a parsed, computed, or post-execution length without first proving the destination length is exactly compatible
- stack-local metadata, parsed instruction state, borrowed slices, or temporary handles that escape into later nested, async, callback-driven, or replayed execution
- fixed-capacity local buffers that are never compared against peer-declared, parsed, decompressed, or negotiated frame size before the state machine waits for progress
- helper contracts documented in comments, headers, type wrappers, or surrounding checks that are stronger than the checks enforced at call sites
- callers that validate only logical element count while the callee consumes bytes, alignment, sentinel space, transcript capacity, or serialized length
- fixed arrays, bitsets, filters, or caches indexed by attacker-controlled parser fields where the parser's accepted numeric domain is wider than the helper storage. Bounds must be format-specific and enforced before indexing, not inferred from a different transaction, message, or protocol version.
- fallback or error paths that return partially initialized bytes, stale stack content, or environment-shaped diagnostics to a protocol-visible sink

Questions to answer:
1. What exact memory, span, or ownership contract does the callee require?
2. What does the caller actually provide?
3. Can attacker-shaped input, peer input, or replayed state drive execution onto the mismatched path?
4. Is the failure an overwrite, overread, use-after-scope, stale-borrow reuse, or impossible-progress availability failure?
5. Would exact length equality, owned storage, explicit sentinel allocation, or fail-closed capacity checks eliminate the issue?
6. Are there compensating controls at every call site, or only in the happy path?

Severity guidance:
- High for overwrite, copy-back overflow, or lifetime bugs that can corrupt validator memory or privileged execution state.
- Medium for overreads, null dereferences, protocol-state corruption, or deterministic crash paths.
- Low to Medium for impossible-progress or capacity-deadlock bugs that are deployment- or configuration-dependent.
```
