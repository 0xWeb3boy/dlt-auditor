# Code-Shape Card

## Metadata

- ID: `bor-2015-05-15-bor-core-logic-5c1a7b965`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-peer-chain-validation`

## Code Shape Summary

- The evidence supports a downloader validation flaw in which a peer could satisfy a cross-check with a block hash alone, without proving parent continuity to the queued chain. The patch tightens that check and the tests were updated to exercise reordered or made-up chain data. The security relevance is plausible and supported by the live-code change, but the provided excerpts do not prove downstream consensus impact, so confidence should be kept below high. Root cause: Cross-check state was advanced based only on receipt of a block with the expected hash, without verifying that the block's parent matched the queued chain state.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses remote peer to node networking boundary and reaches peer table mutation, sync scheduling, or message acceptance before the missing property is enforced.

## Patch Pattern

- Require structural consistency before advancing verification state, and add adversarial tests that model the required parent-child relationships.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
