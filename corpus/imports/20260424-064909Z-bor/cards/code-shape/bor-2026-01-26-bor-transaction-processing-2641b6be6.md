# Code-Shape Card

## Metadata

- ID: `bor-2026-01-26-bor-transaction-processing-2641b6be6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-consensus-validation`

## Code Shape Summary

- The patch fixes a consensus-validation flaw in Bor state-sync handling. Before the change, the finalization path shown in the evidence relied on the last transaction's type and did not explicitly reject receipt/transaction count divergence after state-sync handling. The patch adds canonical state-sync transaction reconstruction plus hash comparison, and the state processors now fail when finalization leaves receipts out of sync with the block body. Root cause: State-sync finalization under-enforced the block validity invariant: the code path shown did not prove that the block body's trailing state-sync transaction matched the locally derived state-sync payload, and downstream processing did not immediately fail on the resulting receipt/transaction mismatch.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Reconstruct the canonical consensus artifact from trusted internal inputs, compare it against block contents, and enforce a structural postcondition so partial or inconsistent processing becomes a hard error.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
