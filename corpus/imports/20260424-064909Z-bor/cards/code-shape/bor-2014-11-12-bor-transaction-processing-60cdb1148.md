# Code-Shape Card

## Metadata

- ID: `bor-2014-11-12-bor-transaction-processing-60cdb1148`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `integrity-check-omission`

## Code Shape Summary

- The evidence shows a consensus-relevant validation check was re-enabled and empty-trie root handling was normalized, but the provided material does not establish whether this was an exploitable security vulnerability versus a correctness fix. Root cause: The code had an omitted transaction-root validation step in block processing and non-canonical handling of empty trie roots in GetRoot(), which could lead to inconsistent commitment checking behavior.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Re-enable a disabled integrity check and normalize internal root encoding to a canonical value, then add regression coverage.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
