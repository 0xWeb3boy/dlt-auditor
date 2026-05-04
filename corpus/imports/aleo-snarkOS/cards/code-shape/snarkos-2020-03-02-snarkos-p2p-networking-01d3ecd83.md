# Code-Shape Card

## Metadata

- ID: `snarkos-2020-03-02-snarkos-p2p-networking-01d3ecd83`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-panic-hardening`

## Code Shape Summary

- Inbound peer paths unwrap or under-handle expected handshake/read failures, letting network-controlled EOF or protocol errors reach panic-prone control flow.

## Search Motifs

- unwrap on handshake/read result in peer handler
- silent_disconnect or EOF path without explicit branch
- network error converted only after panic-prone operation

## Typical Asymmetry

- The code has a validation, authentication, sizing, correlation, or peer-enforcement concept nearby, but the specific inbound path either does not call it, ignores its result, signs too little data, or maps failure to a log/return instead of a state-changing rejection.

## Patch Pattern

- Replace unwrap/silent failure paths with explicit result handling, logging, and normalized disconnect messages.

## False Match Warnings

- Only local test harnesses or non-production crawler code may reduce severity
- A surrounding supervisor that catches panics and isolates all peer state lowers impact
- If the error source is not peer-controlled, this is robustness rather than security
