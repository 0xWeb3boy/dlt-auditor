# Code-Shape Card

## Metadata

- ID: `bor-2016-11-24-bor-storage-12d654a6f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-inconsistency`

## Code Shape Summary

- The patch fixes a state-revert inconsistency in core/state: touching an empty account through a zero-value balance update was not given its own reversible journal entry, so snapshot rollback could leave a transient touched/dirty account behind. The commit metadata explicitly calls this a consensus issue, which makes the fix likely security-relevant, but the provided evidence does not show the full triggering chain or impact scope. Root cause: Empty-account touch behavior was not modeled as an explicit reversible journaled state transition. As a result, a revert could fail to remove account state introduced only by a touch during execution.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Record touch side effects explicitly in the journal and provide matching undo logic for snapshot reverts.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
