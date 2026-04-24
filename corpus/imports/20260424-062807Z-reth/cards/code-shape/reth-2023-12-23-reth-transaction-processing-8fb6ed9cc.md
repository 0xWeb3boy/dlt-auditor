# Code-Shape Card

## Metadata

- ID: `reth-2023-12-23-reth-transaction-processing-8fb6ed9cc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-fork-gating`

## Code Shape Summary

- A validator branch for `Transaction::Eip1559` referenced the wrong hardfork constant, using `Hardfork::Berlin` instead of `Hardfork::London` when deciding whether the transaction type was enabled.

## Search Motifs

- authenticated trie/proof path drops empty-root, revealed-node, or rollback state needed for valid output
- fork-specific consensus rule selected from incomplete boundary inputs or generic validator
- search for `Transaction::Eip1559` call sites that derive, cache, or validate security-sensitive state
- search for `Berlin` call sites that derive, cache, or validate security-sensitive state
- search for `London` call sites that derive, cache, or validate security-sensitive state

## Typical Asymmetry

- Untrusted or fork-dependent input crosses block or transaction input -> execution-layer validator, but fork-state-consistency is incomplete before the code updates or relies on transaction acceptance or consensus rule application.

## Patch Pattern

- Replace an incorrect protocol-version gate with the hardfork condition that matches the transaction type being validated.

## False Match Warnings

- No proof that this function is the sole enforcement point for EIP-1559 enablement
- No evidence of an observed exploit, chain split, or invalid block acceptance
- No test or runtime evidence showing the exact impact on mainnet or production deployments
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
