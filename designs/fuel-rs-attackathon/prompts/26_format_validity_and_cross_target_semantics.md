# Prompt Family: Format Validity And Cross Target Semantics

## Use This For

- Target-independent encoded formats decoded by SDKs, clients, indexers, relayers, wallets, bridges, or generated bindings.
- Serialized length, count, offset, index, discriminant, proof-size, transaction-size, or cursor fields whose width is defined by the format rather than the host.
- Cases where 32-bit, 64-bit, WASM, no-std, embedded, or native targets may return different typed values or different errors for the same bytes.

## Prompt

```text
Hunt for bugs where the encoded format has one meaning but the implementation's host target changes validity, decoded output, or error behavior.

Start from public decode/parse surfaces and generated binding boundaries:
- ABI decoders and encoders.
- Receipt, log, event, return-data, transaction, proof, storage, and RPC response decoders.
- Debug-string or raw-token paths that applications may consume before typed conversion.
- Generated client bindings that turn external bytes into application decisions.

Search patterns:
- `from_be_bytes`, `from_le_bytes`, `from_ne_bytes`
- `try_into::<usize>`, `usize::try_from`, `as usize`, `as isize`
- `len`, `length`, `count`, `offset`, `cursor`, `bytes_read`, `skip`, `peek`, `take`
- `max_tokens`, `limit`, `capacity`, `reserve`, `with_capacity`
- `cfg(target_pointer_width)`, `wasm32`, `target_arch`, `target_endian`

For each hit, build a target-outcome table:
- Encoded field and its format-defined width.
- First point where the value becomes host-sized.
- Checks before host narrowing.
- Checks after host narrowing.
- Outcome on 64-bit.
- Outcome on 32-bit/WASM.
- Whether the same encoded bytes produce success vs error, different decoded values, different cursor movement, or different allocation behavior.

Do not kill a candidate merely because:
- One target returns a clean error.
- The value is large.
- A practical full allocation would be expensive.
- A token limit exists but is not an architecture-independent byte/value bound before host narrowing.
- The narrowing uses `try_into`, `try_from`, or another checked conversion. Checked conversion can still be the root cause when the format field is wider than a supported target's host integer.
- The finding is error-vs-success or early-error-vs-late-error instead of silent truncation. Target-dependent validity is a format semantic difference.

Kill a candidate only when:
- The external format itself bounds the value below the minimum supported target width before host conversion.
- The value is purely local/developer-generated and never crosses an SDK/client/protocol boundary.
- The differing behavior is unreachable behind an equivalent earlier check on every supported target.

Candidate quality bar:
- Prefer exact functions and call paths over generic "uses usize" claims.
- Keep separate candidates for length prefixes, element counts, offsets, discriminants, and cursor accounting when the code paths differ.
- Explain the smallest encoded value class that demonstrates target-dependent behavior; a full memory-heavy PoC is optional when the type-width reasoning is deterministic.
- For dynamic length/count fields, explicitly distinguish the encoded length's representability from token limits, byte availability, allocation limits, and later payload reads.
- Scope impact to SDK/client/application behavior unless there is evidence of node consensus or proof verification divergence.

Severity guidance:
- Medium when valid target-independent encoded data can decode, fail, or reach different validation stages across supported targets at an application-facing boundary.
- Medium can be justified for fallible `u64 -> usize` length/count conversion when a 64-bit target can represent the encoded value but a 32-bit/WASM target rejects it before the format's own architecture-independent bounds.
- Low when the behavior is a developer-only ergonomics issue or already bounded by the format before host conversion.
```
