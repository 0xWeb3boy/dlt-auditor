# Code-Shape Card

## Metadata

- ID: `avalanchego-2024-08-02-avalanchego-transaction-processing-07b7f15dc1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invalid-header-validation`

## Code Shape Summary

- Header validation now rejects positive BlobGasUsed despite generic Cancun field support. The reusable shape is a chain-specific invariant layered on top of inherited fork-format validation.

## Search Motifs

- BlobGasUsed must be nil before fork and zero after fork
- local no-blobs rule enforced after EIP-4844 field checks
- dummy consensus and production verifier gain the same positive-value rejection

## Typical Asymmetry

- The sensitive sink is protected in some paths or under some fork/configuration states, while a neighboring path, boundary case, or compatibility exception omits the same property.
- The vulnerable-looking code often appears as a small predicate, arithmetic expression, allowlist exception, or proof/header check near a much larger protocol feature.

## Patch Pattern

- After generic fork field validation, add local value checks that reject feature fields forbidden by the chain configuration.
- Add focused regression tests for the boundary case, not only broad happy-path coverage.

## False Match Warnings

- Do not flag chains that actually enable blobs
- A nil/non-nil field-shape check is insufficient evidence for a local value invariant
- If execution payload normalization overwrites positive values before validation, impact may be lower
