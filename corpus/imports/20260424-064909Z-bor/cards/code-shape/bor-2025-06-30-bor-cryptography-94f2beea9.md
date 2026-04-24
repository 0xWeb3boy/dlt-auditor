# Code-Shape Card

## Metadata

- ID: `bor-2025-06-30-bor-cryptography-94f2beea9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-consensus-validation`

## Code Shape Summary

- The provided evidence supports a consensus-sensitive stateless-sync validation fix, but it does not establish a concrete vulnerability. The diff shows explicit signer-membership and succession checks being added to snapshot application and veBlop snapshot handling being split into a dedicated helper, which is consistent with bug fixing or hardening in consensus code. From the shown hunks alone, it is not proven that invalid headers were previously accepted, that a chain split was possible, or that an attacker-controlled security issue existed. Root cause: The evidence shows missing or delayed validation in the stateless snapshot transition path: recovered signers were not explicitly checked in the shown code for validator-set membership and succession before further snapshot processing. The diff also suggests veBlop-specific snapshot handling was intertwined with the generic path. The provided material does not prove whether this caused only sync correctness issues or a broader security failure.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted signed payload to verifier or signer boundary and reaches signer recovery, authorization, or replay-protection decision before the missing property is enforced.

## Patch Pattern

- Add explicit validation checks at the snapshot state-transition boundary and isolate special-case reconstruction logic in a dedicated helper.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
