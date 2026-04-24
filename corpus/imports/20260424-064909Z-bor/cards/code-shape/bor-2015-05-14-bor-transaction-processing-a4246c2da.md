# Code-Shape Card

## Metadata

- ID: `bor-2015-05-14-bor-transaction-processing-a4246c2da`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-validation`

## Code Shape Summary

- The patch changes the downloader so an unknown-parent head is reported as an error instead of being silently treated as "no blocks available." That is clear validation hardening in the sync pipeline, but the provided evidence does not establish a concrete exploit or security impact beyond handling an invalid state more explicitly. Root cause: The downloader boundary conflated two different states: an empty queue and a queued block batch whose head did not connect to known local chain state. That hid invalid input/state from the caller instead of surfacing it explicitly.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses remote peer to node networking boundary and reaches peer table mutation, sync scheduling, or message acceptance before the missing property is enforced.

## Patch Pattern

- Distinguish benign empty state from invalid state at the handoff boundary and propagate an explicit error instead of silently collapsing both cases into the same result.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
