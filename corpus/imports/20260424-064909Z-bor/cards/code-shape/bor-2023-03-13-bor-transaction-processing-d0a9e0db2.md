# Code-Shape Card

## Metadata

- ID: `bor-2023-03-13-bor-transaction-processing-d0a9e0db2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validator-verification`

## Code Shape Summary

- The supplied diff supports a consensus-side fix in Bor validator-set verification: the validator check was moved to the end-of-sprint boundary, made to compare against the local contract view, and the validator lookup path was changed to return errors instead of panicking. The evidence supports a security-relevant consensus-validation fix, but not a stronger claim about exact pre-patch exploit impact. Root cause: The validator-set verification logic was tied to the wrong sprint-boundary condition, so the intended check was not performed at the end-of-sprint transition point indicated by the commit. In the same path, validator retrieval/parsing errors were handled with panic(err) rather than normal error propagation, making the verification path brittle.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Retarget a consensus check to the correct state-transition boundary, make it derive comparison data from the local authoritative source using a usable ancestor state, and replace panic-based failure handling with explicit error returns.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
