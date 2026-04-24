# Root-Cause Card

## Metadata

- ID: `geth-arb-2020-12-08-go-ethereum-transaction-processing-ed0670cb17`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `replay-protection-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `chain-id-replay-protection`

## Violated Invariant

- Invariant: Transaction signing helpers should bind signatures to the intended chain ID by default so generated transactions cannot be replayed across compatible chains.

## Trust Boundary

- Boundary: application transaction builder -> signer and transaction broadcast

## Attack Surface

- Entrypoint type: contract binding or transaction signing helper
- Sensitive sink: signed transaction accepted for broadcast

## Impact Pattern

- Primary impact: replay-protection
- Secondary impact: transaction-integrity
- Severity guide: low-medium

## Short Reusable Lesson

- Contract binding helpers exposed signing paths that did not force chain-ID-aware transaction signing, so applications could accidentally produce replayable transactions. Expose and route through chain-ID-aware transactor helpers that construct EIP-155 protected signatures.
