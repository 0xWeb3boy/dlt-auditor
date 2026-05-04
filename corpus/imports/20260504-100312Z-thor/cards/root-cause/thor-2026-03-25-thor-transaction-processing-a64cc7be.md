# Root-Cause Card

## Metadata

- ID: `thor-2026-03-25-thor-transaction-processing-a64cc7be`
- Bug family: `resource_accounting_and_limits`
- Bug class: `unbounded-rlp-list-decoding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `decode-cardinality-bound`

## Violated Invariant

- Invariant: Transaction decoders must bound list-shaped fields before fully decoding or allocating per-item objects from untrusted bytes.

## Trust Boundary

- Boundary: `untrusted-transaction-bytes->transaction-decoder`

## Attack Surface

- Entrypoint type: `transaction-rlp-decoder`
- Sensitive sink: reserved-field and clause-list decoding before mempool or consensus validation
- Attacker capability: Submit or relay encoded transactions with oversized RLP lists.
- Preconditions: The decoder processes attacker-supplied transaction bytes before other admission limits reject them.

## Impact Pattern

- Primary impact: transaction decode resource exhaustion
- Secondary impact: mempool admission amplification
- Blast radius: `node-local`

## Short Reusable Lesson

- Decoders for consensus or mempool objects should enforce cardinality limits while the data is still raw, before allocating or recursively decoding attacker-controlled list elements.
