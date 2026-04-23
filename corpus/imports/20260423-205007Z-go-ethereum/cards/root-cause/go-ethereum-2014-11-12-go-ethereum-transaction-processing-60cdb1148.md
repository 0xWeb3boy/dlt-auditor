# Root-Cause Card

## Metadata

- ID: `go-ethereum-2014-11-12-go-ethereum-transaction-processing-60cdb1148`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-consensus-commitment-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-validation`

## Violated Invariant

- Invariant: During block processing, the transaction trie hash derived from the block's transaction list must match the block header's TxSha commitment before the block is accepted by that validation path.

## Trust Boundary

- Boundary: Untrusted transaction data crossing into local execution and admission checks.

## Attack Surface

- Entrypoint type: `transaction validation path`
- Sensitive sink: `canonical-chain selection or persistent chain-state update`

## Impact Pattern

- Primary impact: `consensus-integrity`
- Secondary impact: `validation-bypass`

## Short Reusable Lesson

- The supported security finding is a consensus validation fix: `BlockManager.ProcessWithParent` re-enables validation that `DeriveSha(block.transactions)` matches `block.TxSha` and returns an error on mismatch.
