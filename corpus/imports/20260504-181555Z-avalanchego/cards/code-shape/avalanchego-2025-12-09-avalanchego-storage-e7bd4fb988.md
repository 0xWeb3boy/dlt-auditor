# Code-Shape Card

## Metadata

- ID: `avalanchego-2025-12-09-avalanchego-storage-e7bd4fb988`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `range-proof-boundary-hardening`

## Code Shape Summary

- Range proof boundaries were changed to bind requested start/end keys instead of only yielded keys. The reusable shape is proof generation where absence at range edges must be proven explicitly, especially when no exact boundary key exists.

## Search Motifs

- start_proof computed from requested start_key rather than first yielded key
- comments about proving a gap between requested bound and returned key
- range iterator filtering coupled with Merkle proof construction

## Typical Asymmetry

- The sensitive sink is protected in some paths or under some fork/configuration states, while a neighboring path, boundary case, or compatibility exception omits the same property.
- The vulnerable-looking code often appears as a small predicate, arithmetic expression, allowlist exception, or proof/header check near a much larger protocol feature.

## Patch Pattern

- Generate boundary proofs for requested bounds and filter iteration to the requested range so both inclusion and edge absence are represented.
- Add focused regression tests for the boundary case, not only broad happy-path coverage.

## False Match Warnings

- If clients never verify absence/completeness, impact may be correctness-only
- Exact-key proof fixes are not necessarily range-boundary fixes
- Do not claim forged state unless verifier behavior is shown
