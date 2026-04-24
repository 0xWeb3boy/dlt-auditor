# Code-Shape Card

## Metadata

- ID: `bor-2019-01-24-bor-transaction-processing-c7664b063`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-rule-hardening`

## Code Shape Summary

- The supplied evidence shows implementation of the Petersburg/ConstantinopleFix fork across gas metering, config compatibility, and chain-spec generation. That is security-relevant protocol hardening, but the provided material does not establish a standalone exploitable vulnerability in this client. Root cause: The shown code lacked first-class handling for the Petersburg/ConstantinopleFix fork. The evidence supports missing protocol-update support across consensus-critical paths, not a clearly demonstrated local implementation flaw with a proven exploit path.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Implement a new fork boundary consistently across execution rules, compatibility checks, and chain-spec tooling.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
