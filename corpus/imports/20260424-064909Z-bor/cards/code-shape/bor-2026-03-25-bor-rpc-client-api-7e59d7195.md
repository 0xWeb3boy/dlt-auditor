# Code-Shape Card

## Metadata

- ID: `bor-2026-03-25-bor-rpc-client-api-7e59d7195`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-input-nondeterminism`

## Code Shape Summary

- The provided evidence supports a consensus-relevant determinism fix in Bor's state-sync import path. The patch adds a deterministic-state-sync gate and a Heimdall height lookup by cutoff time to avoid different validators deriving different state-sync sets from different Heimdall views. The evidence does not prove exploitation or a historical chain split. Root cause: The consensus path selected imported state-sync data using a time-based Heimdall query without first pinning the read to a canonical Heimdall snapshot boundary. Different validators querying different Heimdall views could therefore derive different state-sync sets for the same Bor block.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses external RPC client to node service boundary and reaches backend state access, privileged API behavior, or response serialization before the missing property is enforced.

## Patch Pattern

- For consensus-critical cross-system inputs, resolve queries to a canonical snapshot identifier before fetching records, instead of relying on open-ended time-based reads against each node's live view.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
