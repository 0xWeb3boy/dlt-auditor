# Code-Shape Card

## Metadata

- ID: `bor-2019-03-12-bor-transaction-processing-7504dbd6e`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `resource-accounting-overflow`

## Code Shape Summary

- The patch clearly hardens EVM memory/gas arithmetic by moving sizing and gas-related interfaces onto uint64 and adding explicit overflow handling, but the provided evidence does not establish a concrete vulnerability or exploit path in the pre-patch code. The stack-validation and other refactors in the same commit further weaken a strong security-fix claim. Root cause: Arithmetic around memory sizing and gas charging was refactored to an explicit checked uint64 path, suggesting prior correctness risk at that boundary; however, the supplied hunks do not prove that the earlier code was actually vulnerable in a security sense.

## Search Motifs

- remote input controls allocation, iteration count, queue length, or cache growth without a cap
- decode or validation path panics or aborts process on malformed peer/RPC data
- request processing lacks timeout, size limit, rate limit, or early reject before expensive work

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Introduce fixed-width checked arithmetic for resource accounting and fail closed on overflow.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
