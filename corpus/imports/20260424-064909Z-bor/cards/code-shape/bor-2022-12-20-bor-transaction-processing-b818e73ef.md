# Code-Shape Card

## Metadata

- ID: `bor-2022-12-20-bor-transaction-processing-b818e73ef`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-input-validation`

## Code Shape Summary

- The supported finding is a security-hardening change in the beacon consensus batch-header validation path. The evidence shows Beacon.VerifyHeaders was changed to split merge-boundary batches locally, return per-header errors when the split is invalid, and derive the PoW seal slice from preHeaders instead of relying on caller-prepared state. That supports an insufficient-validation thesis, but not stronger claims about demonstrated invalid-chain acceptance or consensus splits. Root cause: Beacon.VerifyHeaders relied too much on caller-side sanitization and caller-prepared auxiliary state when validating mixed pre-/post-merge header batches.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Internalize validation at the consensus boundary: compute the pre/post split locally, reject invalid splits immediately, and derive downstream verifier inputs from the validated split instead of trusting caller-supplied subsets.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
