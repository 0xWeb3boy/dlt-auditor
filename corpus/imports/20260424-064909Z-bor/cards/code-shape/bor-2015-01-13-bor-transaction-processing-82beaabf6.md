# Code-Shape Card

## Metadata

- ID: `bor-2015-01-13-bor-transaction-processing-82beaabf6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-rule-mismatch`

## Code Shape Summary

- The supplied evidence supports a likely consensus-fix classification, but not a fully proven exploit narrative. The patch corrects two consensus-sensitive logic points: CREATE code-deposit gas handling in state transition code and the ancestor-depth constant used in uncle/reward processing. Root cause: Consensus-sensitive logic was encoded with brittle local control flow and an incorrect rule constant: the CREATE code-deposit check reused an enclosing error variable, and uncle processing used a different ancestor depth than the fixed code.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Localize sub-operation error handling and correct consensus-rule constants in validation/execution paths.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
