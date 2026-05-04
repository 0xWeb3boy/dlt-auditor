# Code-Shape Card

## Metadata

- ID: `avalanchego-2022-11-29-avalanchego-transaction-processing-3511ceac26`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-replay-policy-hardening`

## Code Shape Summary

- A coarse global unprotected-transaction flag was replaced with a transaction-aware allowlist. The reusable shape is replay-policy code where legacy compatibility should be keyed to exact transaction identity, not a process-wide bypass.

## Search Motifs

- UnprotectedAllowed changes from no-arg boolean to tx-aware predicate
- allowUnprotectedTxHashes or known legacy transaction hash maps
- tests around EIP-155 or legacy replay-protection exceptions

## Typical Asymmetry

- The sensitive sink is protected in some paths or under some fork/configuration states, while a neighboring path, boundary case, or compatibility exception omits the same property.
- The vulnerable-looking code often appears as a small predicate, arithmetic expression, allowlist exception, or proof/header check near a much larger protocol feature.

## Patch Pattern

- Replace global allow-all replay exceptions with an exact transaction hash allowlist while preserving an explicit operator override.
- Add focused regression tests for the boundary case, not only broad happy-path coverage.

## False Match Warnings

- A global flag used only in private dev networks may be intentional
- Allowlisting a fixed historical transaction is not itself a bypass
- Do not claim replay theft without a default unsafe acceptance path
