# Code-Shape Card

## Metadata

- ID: `avalanchego-2024-04-29-avalanchego-cryptography-5e7c692547`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-header-validation`

## Code Shape Summary

- Fork-aware header validation was expanded to cover a previously incomplete field check. The reusable shape is block syntactic validation where each fork-dependent field needs explicit nil/value handling on both sides of activation.

## Search Motifs

- ParentBeaconRoot or blob gas checks guarded by Cancun activation
- pre-fork forbidden field and post-fork required field tests
- header validation split between dummy consensus and production block verifier

## Typical Asymmetry

- The sensitive sink is protected in some paths or under some fork/configuration states, while a neighboring path, boundary case, or compatibility exception omits the same property.
- The vulnerable-looking code often appears as a small predicate, arithmetic expression, allowlist exception, or proof/header check near a much larger protocol feature.

## Patch Pattern

- Add explicit fork-aware required/forbidden checks at block syntactic validation boundaries and mirror them in consensus-engine test paths.
- Add focused regression tests for the boundary case, not only broad happy-path coverage.

## False Match Warnings

- Dummy consensus changes alone may be test infrastructure
- Do not claim cryptographic failure from ordinary header field validation
- If a downstream verifier always rejects the field, an upstream missing check may be defense-in-depth only
