# Root-Cause Card

## Metadata

- ID: `sui-2024-08-31-sui-transaction-processing-fdc8325abf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Untrusted work must be bounded, attributed, and charged or throttled before it can consume shared validator resources.

## Trust Boundary

- Boundary: submitted transaction or validator response -> execution/effects pipeline

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: consuming validator CPU, memory, network, or execution budget

## Impact Pattern

- Primary impact: potential-remote-dos
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch is best characterized as GraphQL RPC availability hardening for oversized transaction-bearing requests. The commit text states that mutation and dry-run transaction payloads can be much larger than ordinary query payloads and adds a max_tx_payload_size derived from protocol max_tx_bytes with Base64 overhead.
