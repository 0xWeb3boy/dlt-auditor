# Prompt Family: Fallible Host Width Narrowing

## Use This For

- Fixed-width encoded length, count, offset, or size fields converted with `try_into::<usize>`, `usize::try_from`, or similar checked narrowing.
- Decoder behavior that differs by pointer width even though the conversion fails cleanly on the narrower target.
- SDK/client APIs that parse target-independent ABI, wire, proof, storage, transaction, receipt, log, or RPC data.

## Prompt

```text
Hunt specifically for fallible host-width narrowing bugs. The question is not only "does the code truncate"; the question is whether a target-independent encoded field becomes valid or invalid based on the host pointer width.

Search patterns:
- `try_into::<usize>`, `usize::try_from`, `.try_into()`, `.try_from()`
- `u64::from_be_bytes`, `u64::from_le_bytes`, `from_be_bytes`, `from_le_bytes`
- `length`, `len`, `count`, `offset`, `index`, `size`, `capacity`
- `decode`, `parse`, `peek`, `take`, `skip`, `bytes_read`, `max_tokens`, `max_depth`

For each candidate, answer:
1. Is the field width defined by an external format rather than the host?
2. Is the value narrowed before an architecture-independent maximum is checked?
3. Can a 64-bit target represent a value that a 32-bit/WASM target rejects at conversion?
4. If the 64-bit target later fails, is that failure due to byte availability, allocation, token count, or another check that is distinct from pointer-width representability?
5. Is there any dynamic type or configuration where a matching payload could be processed on 64-bit while 32-bit fails at conversion?
6. Would applications, generated bindings, logs, indexers, relayers, wallets, or tests observe different success/error behavior for the same encoded bytes?

Do not downgrade solely because:
- The conversion is checked and returns `Result`.
- The smaller target fails closed.
- The success-side payload is large.
- A default token limit bounds one subtype but not the general length/count conversion property.
- The candidate is an error-behavior divergence rather than wrong decoded data.

Kill only with concrete evidence:
- A format-level maximum below the minimum supported target width is checked before narrowing.
- The API explicitly does not support the narrower target for this decoder.
- The input is purely local and cannot cross an SDK/client/application boundary.
- Every larger value is rejected by the same architecture-independent check before host conversion on every supported target.

Severity guidance:
- Medium when externally supplied target-independent data can be accepted, rejected, or fail at a different semantic layer depending on host pointer width.
- Low when the difference is unreachable by public APIs or already covered by an explicit pre-narrowing format bound.
```
