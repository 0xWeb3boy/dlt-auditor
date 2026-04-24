# Code-Shape Card

## Metadata

- ID: `bor-2017-05-12-bor-transaction-processing-a5f6a1cb7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `chain-config-validation`

## Code Shape Summary

- The provided evidence supports a correctness fix in chain-configuration compatibility checking: params/config.go adds a previously missing MetropolisBlock incompatibility check and an IsMetropolis helper. That is consensus-relevant code, but the supplied material does not establish a concrete vulnerability, exploit path, or real security impact, so this should be treated as unclear rather than a confirmed security fix. Root cause: ChainConfig.checkCompatible enforced historical compatibility for several fork parameters but omitted MetropolisBlock, leaving that fork point out of the existing compatibility gate.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Add the missing fork-parameter validation to the central chain-config compatibility gate.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
