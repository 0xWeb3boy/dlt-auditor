# Root-Cause Card

## Metadata

- ID: `snarkos-2021-07-11-snarkos-cryptography-9dfc4e2da`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-network-id-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `network-id-binding`

## Violated Invariant

- Invariant: Block construction must reject transactions whose network identifier does not match the active consensus parameters.

## Trust Boundary

- Boundary: `transaction/mempool->miner-consensus-construction`

## Attack Surface

- Entrypoint type: `block-construction-path`
- Sensitive sink: coinbase/block transaction inclusion
- Attacker capability: provide transaction data with a mismatched network id; influence miner transaction selection.
- Preconditions: miner constructs blocks from externally sourced transactions; network id separates consensus domains.

## Impact Pattern

- Primary impact: cross-network transaction inclusion risk.
- Secondary impact: consensus construction ambiguity.
- Severity guide: `medium` for `consensus-domain-separation` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- Block construction must reject transactions whose network identifier does not match the active consensus parameters. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: The patch updates consensus and mining code. The clearest security-relevant change is an added check in miner coinbase construction that rejects transactions whose network id differs from the active consensus parameters. Other changes switch to canonical noop program ids, Testnet1DPC-based execution generation with CryptoRng, and explicit little-endian memory pool decoding. The evidence supports possible consensus hardening, but not a confirmed vulnerability fix. 1. In `consensus/src/parameters.rs`, the patch replaces `pub fn generate_program_proofs<R: Rng, S: Storage>(` with `pub fn generate_program_proofs<R: Rng + CryptoRng, S: Storage>(`. 2. In `consensus/src/memory_pool.rs`, the patch re
