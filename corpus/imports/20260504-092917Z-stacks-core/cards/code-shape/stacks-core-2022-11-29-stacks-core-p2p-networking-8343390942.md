# Code-Shape Card

## Metadata

- ID: `stacks-core-2022-11-29-stacks-core-p2p-networking-8343390942`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unhandled-protocol-error-panic`

## Code Shape Summary

- The patch fixes an unhandled PoX already-locked error in Clarity special contract-call handling. Before the change, `ChainstateError::PoxAlreadyLocked` from PoX v1 or PoX v2 lock application had no dedicated match arm and could fall through to the generic `panic!` branch. After the change, both handlers translate the condition into `Error::Runtime(RuntimeErrorType::PoxAlreadyLocked, None)`, and a regression test covers stacking in both PoX versions.

## Search Motifs

- Motif 1: request body decoded before max-size enforcement
- Motif 2: panic or unwrap reachable from peer-controlled protocol data
- Motif 3: execution cost or resource budget charged inconsistently across error cases

## Typical Asymmetry

- The producer, peer, signer, or caller can choose fields that the consumer later treats as authoritative unless the missing property is checked at the boundary.

## Patch Pattern

- Move size, cost, and error checks to the boundary and convert panic or ambiguous errors into explicit validation failures.

## False Match Warnings

- The input may already be bounded by transport framing.
- A panic in test-only or unreachable internal code is not an externally reachable denial of service.
