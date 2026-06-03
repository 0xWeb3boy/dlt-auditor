# Prompt Family: Host Representation And Codec Portability

## Use This For

- ABI, transaction, proof, storage, or wire formats that should behave the same on every supported target.
- Length, count, cursor, offset, index, and limit fields decoded into host-width types.
- Differences between 32-bit, 64-bit, WASM, embedded, big-endian/little-endian, or feature-gated builds.
- SDKs or clients whose decoded output can change smart-contract calls, wallet behavior, proof verification, or off-chain decision making.

## Prompt

```text
Hunt for target-architecture and host-representation bugs in DLT code. The core question is whether externally defined data has architecture-independent semantics, while the implementation validates, decodes, or re-encodes it through host-dependent types or layouts.

Focus on:
- ABI and wire length prefixes.
- Vector, tuple, struct, map, receipt, log, proof, and storage decoding.
- Cursor advancement and bytes-read accounting after variable-length fields.
- Offsets, indexes, limits, gas/resource counts, witness sizes, and serialized counts.
- `usize`, `isize`, pointer-width integers, native endian conversions, native struct layout, target-specific `cfg`, and WASM-specific branches.
- Conversions from fixed-width serialized values into host-width values.
- Tests that only run on the current developer architecture.
- Large but format-valid values that are above the minimum supported target's host range.

Search patterns:
- `usize`, `isize`, `as usize`, `as isize`, `usize::try_from`, `isize::try_from`, `.try_into()`, `.try_from()`
- `u64::from_be_bytes`, `u32::from_be_bytes`, `from_le_bytes`, `to_ne_bytes`, `from_ne_bytes`
- `len`, `length`, `count`, `offset`, `index`, `cursor`, `bytes_read`, `skip`, `take`, `peek`, `decode`, `encode`
- target gates such as `cfg(target_pointer_width)`, `cfg(target_arch)`, `cfg(target_endian)`, `wasm32`
- tests or docs that mention only the native platform

Questions to answer before killing a candidate:
1. Is the value defined by an external format, protocol, ABI, wire message, proof, transaction, storage object, or node response?
2. Does the implementation narrow it into `usize` or `isize` before checking the format's own maximum range?
3. Would a 32-bit target reject, wrap, truncate, allocate differently, or parse differently from a 64-bit target?
4. Would a WASM or embedded target exercise a different representation or build path?
5. Does the decoder return a clean error on one target but success on another for the same valid encoded bytes?
6. Is target-dependent rejection itself a security issue because clients, wallets, contracts, indexers, or relayers should agree on decoded behavior?
7. Are cursor and `bytes_read` values measured in encoded bytes, decoded payload bytes, elements, words, or host units, and is that consistent across composite decodes?
8. Are tests only proving native-platform behavior with small values?
9. Is the candidate being killed because the value is large, even though the format uses a fixed-width field that can represent it?
10. Are token-count, byte-length, allocation-size, and pointer-width representability being treated as the same property when they are actually different checks?

Validation guidance:
- Prefer a minimal encoded byte sequence or mocked decode path over a full node PoC.
- If direct 32-bit execution is unavailable, reason from Rust type widths and document the target-width precondition.
- Do not downgrade solely because the conversion returns `Result`; ask whether the error creates architecture-dependent validity.
- Do not downgrade solely because the success-side value is very large; scope impact carefully, but preserve the portability finding when one supported target can represent/decode the value and another rejects it due to host width.
- Do not require silent truncation. A checked `u64 -> usize` conversion can be a portability bug when it makes the accepted value range depend on the host target.
- Kill candidates where `usize` is used only after an architecture-independent bound has already been enforced below the minimum supported target width.
- Keep length prefixes, element counts, byte offsets, cursor increments, and discriminants as separate candidates when they use different fields or functions, even if they share a host-width root theme.
- When a resource limit kills exploitability, identify the exact architecture-independent bound that applies before host narrowing. If the only killer is "it would be hard to allocate on one target", keep the candidate scoped instead of killing it.
- Keep impact scoped: SDK/client divergence, unintended decoded values, failed cross-platform transaction construction, or off-chain disagreement can be Medium even without memory corruption.

Severity guidance:
- Medium when architecture-dependent decoding can change SDK/client behavior for valid protocol or ABI data.
- Lower when the value is purely local, developer-controlled, or already bounded by an architecture-independent check.
- Raise only with evidence of consensus divergence, signature/proof acceptance difference, fund loss, or smart-contract behavior change.
```
