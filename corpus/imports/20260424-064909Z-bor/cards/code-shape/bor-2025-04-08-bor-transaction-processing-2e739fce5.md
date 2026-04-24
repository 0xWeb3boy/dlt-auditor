# Code-Shape Card

## Metadata

- ID: `bor-2025-04-08-bor-transaction-processing-2e739fce5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## Code Shape Summary

- The patch adds txpool admission checks for EIP-7702-style delegated or pending-authorization accounts. Based on the supplied commit message and code snippets, it is a security-relevant hardening change aimed at reducing a mempool abuse pattern involving blob transaction spam, eviction pressure, and later cancellation. Root cause: The txpool did not fully enforce cross-subpool exclusivity for delegated senders and SetCode authority addresses. From the supplied evidence, that left room for blob and authorization-related transactions to interact in a way that could be used to create txpool eviction and cancellation pressure.

## Search Motifs

- remote input controls allocation, iteration count, queue length, or cache growth without a cap
- decode or validation path panics or aborts process on malformed peer/RPC data
- request processing lacks timeout, size limit, rate limit, or early reject before expensive work

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Add explicit admission-time resource and exclusivity checks, backed by shared reservation tracking across subpools.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
