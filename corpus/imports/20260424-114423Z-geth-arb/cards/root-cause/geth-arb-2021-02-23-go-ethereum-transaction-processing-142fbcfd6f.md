# Root-Cause Card

## Metadata

- ID: `geth-arb-2021-02-23-go-ethereum-transaction-processing-142fbcfd6f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-replay-protection-enforcement`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `chain-id-replay-protection`

## Violated Invariant

- Invariant: Public transaction submission should reject unprotected transactions unless the operator has explicitly opted into accepting replayable legacy signatures.

## Trust Boundary

- Boundary: external RPC transaction submission -> mempool and network broadcast

## Attack Surface

- Entrypoint type: RPC SendRawTransaction or SendTx path
- Sensitive sink: transaction pool admission and peer propagation

## Impact Pattern

- Primary impact: replay-protection
- Secondary impact: transaction-integrity
- Severity guide: medium

## Short Reusable Lesson

- The RPC submission path forwarded non-EIP-155 transactions unless configured otherwise, allowing replayable transactions to enter normal propagation. Add a fail-closed replay-protection check before SendTx and require an explicit override for legacy acceptance.
