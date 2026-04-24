# Code-Shape Card

## Metadata

- ID: `bor-2015-05-21-bor-core-logic-52db6d8be`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `verification-bypass`

## Code Shape Summary

- The patch tightens eth/downloader cross-checking so a sampled block must match the exact expected parent, not just any parent already present in the download queue. The evidence supports a sync-path integrity bypass in downloader verification, with a regression test for the forged-parent case. Root cause: The cross-check state was too weak: it remembered only expiration and later accepted any queued parent for a sampled block hash. That allowed the deferred verification step to test local membership rather than exact ancestry for the sampled block.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses remote peer to node networking boundary and reaches peer table mutation, sync scheduling, or message acceptance before the missing property is enforced.

## Patch Pattern

- Record the exact relationship to be verified later, then compare against that recorded value instead of using a broader local-state predicate.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
