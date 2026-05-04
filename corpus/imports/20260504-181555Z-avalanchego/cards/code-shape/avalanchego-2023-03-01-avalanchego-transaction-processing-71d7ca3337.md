# Code-Shape Card

## Metadata

- ID: `avalanchego-2023-03-01-avalanchego-transaction-processing-71d7ca3337`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-resource-metering`

## Code Shape Summary

- Initcode size and gas metering rules were added across admission, intrinsic gas, state transition, and VM creation paths. The reusable shape is resource accounting that must be duplicated consistently across all ways a payload reaches execution.

## Search Motifs

- MaxInitCodeSize checks added in txpool and state transition
- IntrinsicGas or CREATE gas calculations gain per-word charges
- fork-gated EIP resource rules applied in multiple layers

## Typical Asymmetry

- The sensitive sink is protected in some paths or under some fork/configuration states, while a neighboring path, boundary case, or compatibility exception omits the same property.
- The vulnerable-looking code often appears as a small predicate, arithmetic expression, allowlist exception, or proof/header check near a much larger protocol feature.

## Patch Pattern

- Add fork-gated size validation and gas charging at every admission and execution boundary that can process contract initcode.
- Add focused regression tests for the boundary case, not only broad happy-path coverage.

## False Match Warnings

- A single missing check may be harmless if a stricter earlier layer always dominates
- Do not flag test-only gas helpers without production admission impact
- Performance optimizations are not resource controls unless they enforce a limit
