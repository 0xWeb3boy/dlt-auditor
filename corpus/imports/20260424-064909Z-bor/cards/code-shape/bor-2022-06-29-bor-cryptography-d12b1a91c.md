# Code-Shape Card

## Metadata

- ID: `bor-2022-06-29-bor-cryptography-d12b1a91c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-transition-validation`

## Code Shape Summary

- The patch adds an explicit terminal-total-difficulty check to the beacon mixed pre/post-merge header-validation path and preserves that failure during async result collection. The supplied evidence supports a consensus-validity bug around terminal PoW block selection, but not a stronger claim about real-world exploitation. Root cause: The transition-validation path did not visibly enforce the terminal-total-difficulty invariant on the pre-merge PoW segment before asynchronous result aggregation, and the collector could overwrite an earlier TTD-based rejection. That left the terminal-block validity rule under-enforced in the mixed merge-transition path.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Add an explicit consensus-invariant check at the PoW-to-PoS boundary and make asynchronous aggregation preserve that invariant failure instead of overwriting it.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
